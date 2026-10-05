from pathlib import Path
import json
r=Path('work/nss111');checks=[]
for name in ('controlled-session.mjs','match-controlled.mjs','run.mjs','module-stage.mjs','current-audit-diagnostic.mjs','start-dallas.mjs','read-controlled.mjs','close-endpoint.mjs','ssh-client.mjs','server.py','discover-peer.py','probe-peer.py','endpoint-firewall-guardian.py','client-watchdog.ps1'):
 s=(Path('work/nss110')/name).read_text(encoding='utf-8');v=s.replace('nss110','nss111').replace('NSS110','NSS111')
 assert v.replace('nss111','nss110').replace('NSS111','NSS110')==s
 if name=='controlled-session.mjs':
  v=v.replace("from '../nss50/service-epoch.mjs'","from './service-epoch.mjs'")
  v="import {auditScopedBaseline} from './declared-baseline.mjs';\n"+v
  v=v.replace("verifyEpochServices(JSON.parse(fs.readFileSync(dir+'/service-epoch-private.json')).services,before.services);","verifyEpochServices(JSON.parse(fs.readFileSync(dir+'/service-epoch-private.json')).services,before.services);auditScopedBaseline(JSON.parse(fs.readFileSync(dir+'/prewrite-baseline-private.json')),before);")
  v=v.replace("selected=selectionFrame.pairs.find(p=>JSON.stringify(p)===JSON.stringify(preauditSelected));","selected=selectionFrame.pairs.find(p=>JSON.stringify(p)===JSON.stringify(preauditSelected));")
  v=v.replace("assert.ok(selected,'Controlled exact pair changed after original full audit');","assert.ok(selected,'Controlled exact pair changed after original full audit');assert.notEqual(selected.tcp.wan,4,'Failed WAN4 cannot enter controlled NSS');")
  v=v.replace("auditBaseline(before,{...after,native:before.native})","auditScopedBaseline(before,after)")
 elif name=='current-audit-diagnostic.mjs':
  v=v.replace("from '../nss50/service-epoch.mjs'","from './service-epoch.mjs'")
  v=v.replace("{declaredReference,authSha256,manifestSha256}","{declaredReference,verifyFailedWanState,auditScopedBaseline,authSha256,manifestSha256}")
  v=v.replace("let epoch,hint,reference,declaration;", "const status=JSON.parse(await run('ubus call network.interface.wan4 status'));\n const ownerSource=fs.readFileSync('work/nss111/failed-wan-owner.lua','utf8');\n const seal=JSON.parse(await run(\"lua - <<'NSS111_FAILED_WAN_OWNER'\\n\"+ownerSource+\"\\nNSS111_FAILED_WAN_OWNER\\n\"));\n save('failed-wan-owner-private',seal);verifyFailedWanState(after,status,seal);\n let epoch,hint,reference,declaration;")
  v=v.replace("  const status=JSON.parse(await run('ubus call network.interface.wan4 status'));\n",'')
  v=v.replace('declaredReference(historical,after,health,authDigest,status)','declaredReference(historical,after,health,authDigest,status,seal)')
  v=v.replace('version:2,','version:3,').replace('assert.equal(epoch.version,2)','assert.equal(epoch.version,3)')
  v=v.replace('const baseline=auditBaseline(reference,adjusted);','const baseline=auditScopedBaseline(reference,adjusted);')
  v=v.replace('serviceChangesDuringExperimentAllowed:false,','failedUnselectedWan4ProcessEpochMayChange:true,otherServiceChangesDuringExperimentAllowed:false,wan4ProcessOwnershipChecked:true,')
 (r/name).write_text(v,encoding='utf-8');checks.append({'file':name,'namespaceOnly':name not in ('controlled-session.mjs','current-audit-diagnostic.mjs')})
(r/'prepare-receipt.json').write_text(json.dumps({'productionWrites':False,'changedVariable':'explicit failed unselected WAN4 process epoch, routing remains exact','nssHardwarePayloadChanged':False,'checks':checks},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'prepared':True,'files':len(checks),'nssPayloadChanged':False}))
