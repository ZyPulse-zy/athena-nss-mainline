from pathlib import Path
import json
r=Path('work/nss112');checks=[]
for name in ('controlled-session.mjs','current-audit-diagnostic.mjs','match-controlled.mjs','run.mjs','start-dallas.mjs','read-controlled.mjs','close-endpoint.mjs','ssh-client.mjs','server.py','discover-peer.py','probe-peer.py','endpoint-firewall-guardian.py','client-watchdog.ps1','failed-wan-owner.lua'):
 s=(Path('work/nss111')/name).read_text(encoding='utf-8');v=s.replace('nss111','nss112').replace('NSS111','NSS112')
 assert v.replace('nss112','nss111').replace('NSS112','NSS111')==s
 if name=='controlled-session.mjs':
  v=v.replace("from '../nss49/parse-ecm-any-wan.mjs'","from './parse-ecm-any-wan.mjs'").replace("from '../nss16/automatic-leaf-plan.mjs'","from './uplink-tag-plan.mjs'")
  v=v.replace("const pin=JSON.parse(fs.readFileSync('work/nss16/qos-capacity-private.json'));", "const pin=JSON.parse(fs.readFileSync('work/nss16/qos-capacity-private.json'));const up=JSON.parse(fs.readFileSync('work/nss112/uplink-capacity-private.json'));assert.equal(up.boot,wan.boot);assert.equal(up.device,'wan');assert.equal(up.ifindex,6);")
  v=v.replace('qosBoot:wan.boot}',"qosBoot:wan.boot,uplinkDevice:'wan',uplinkIfindex:6,uplinkPhysicalAeId:5,uplinkBaseline:up.defaultQueues}")
  v=v.replace("'qosModuleUnloaded','wanRestored'", "'qosModuleUnloaded','dualPhysicalQueuesReady','dualPhysicalQueuesRestored','wanRestored'")
 elif name=='current-audit-diagnostic.mjs':
  # Reuse the exact successful four-WAN audit source and scope implementation.
  pass
 (r/name).write_text(v,encoding='utf-8');checks.append({'file':name,'onlyNamespaceChanged':name!='controlled-session.mjs'})
for name in ('declared-baseline.mjs','service-epoch.mjs'):
 (r/name).write_text("export * from '../nss111/"+name+"';\n",encoding='utf-8')
# The guardian and fast-path timing/counter contracts are byte-identical.
for name in ('fast-path.lua','module-stage-guardian.lua'):(r/name).write_bytes((Path('work/nss105')/name).read_bytes())
s=Path('work/nss105/module-stage.mjs').read_text(encoding='utf-8').replace('work/nss105/','work/nss112/')
(r/'module-stage.mjs').write_text(s,encoding='utf-8')
s=Path('work/nss105/payload.mjs').read_text(encoding='utf-8').replace('work/nss105/','work/nss112/')
(r/'payload.mjs').write_text(s,encoding='utf-8')
s=Path('work/nss49/parse-ecm-any-wan.mjs').read_text(encoding='utf-8')
s=s.replace("const f=selected[slot];const direction=", "const f=selected[slot],up=slot==='tcp'?0x8e050000:0x8e060000;const direction=")
s=s.replace('reverse?tag:0','reverse?tag:up').replace('reverse?0:tag','reverse?up:tag').replace('upTag:0,','upTag:up,')
(r/'parse-ecm-any-wan.mjs').write_text(s,encoding='utf-8')
(r/'prepare-receipt.json').write_text(json.dumps({'checks':checks,'hardwarePayloadGateBinaryUnchanged':True,'fastTimingCounterSourceByteIdentical':True,'newUplinkPhysicalDevice':'wan','selectedFlowUplinkTags':['8e05:','8e06:'],'unknownFlowsStillDefaultDenied':True,'sharedModuleCleanupRequired':True,'productionExecution':False},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'prepared':True,'sourceFilesCopied':len(checks),'hardwareExecution':False}))
