"""Only the offered TCP rate changes; all native NSS and rollback bytes stay fixed."""
from pathlib import Path
import json,hashlib
r=Path('work/nss96');prior=Path('work/nss91');old=json.loads((prior/'entry-qualified.json').read_text())
checks=[]
for name in [Path(x).name for x in old['sourceManifest']]:
 if name=='prepare-load.py':continue
 src=prior/name;dst=r/name;assert not dst.exists(),f'Refuse overwrite {dst}'
 if name in ('fast-path.lua','qos-physical.lua','tag-counter-audit.lua'):
  dst.write_bytes(src.read_bytes());checks.append({'file':name,'nativeBytesUnchanged':True});continue
 s=src.read_text(encoding='utf-8');v=s.replace('nss91','nss96').replace('NSS91','NSS96')
 if name=='ssh-client.mjs':v=v.replace('c.mbps===32','c.mbps===48').replace('32000000','48000000')
 if name=='start-dallas.mjs':v=v.replace('config.mbps=32','config.mbps=48')
 if name=='analyze-controlled.py':v=v.replace("'requestedTcpMbps':32","'requestedTcpMbps':48")
 back=v.replace('nss96','nss91').replace('NSS96','NSS91')
 if name=='ssh-client.mjs':back=back.replace('c.mbps===48','c.mbps===32').replace('48000000','32000000')
 if name=='start-dallas.mjs':back=back.replace('config.mbps=48','config.mbps=32')
 if name=='analyze-controlled.py':back=back.replace("'requestedTcpMbps':48","'requestedTcpMbps':32")
 assert back==s,name;dst.write_text(v,encoding='utf-8');checks.append({'file':name,'namespaceAndExplicitRateOnly':True})
for name in ('qos-native-qualification.json','getter-qualified.json'):r.joinpath(name).write_bytes(prior.joinpath(name).read_bytes())
client=Path('work/nss95/run-existing-entry.mjs').read_text(encoding='utf-8').replace("const root='work/nss95'","const root='work/nss96'").replace('../nss89/session-binding.mjs','./session-binding.mjs').replace('work/nss89/','work/nss96/').replace("entry:'NSS89 unchanged'","entry:'NSS96 rate-only 48Mbps'").replace('offeredMbps:52','offeredMbps:48')
client=client.replace("experiment=JSON.parse(out);", "experiment=JSON.parse(out);")
client=client.replace("const out=await run('work/nss96/controlled-session.mjs',['aba'],110);", "const baseline=JSON.parse(fs.readFileSync(v.dir+'/udp-baseline-qualified.json'));assert.ok(baseline.returned>0,'No actual recent UDP return before staging');const out=await run('work/nss96/controlled-session.mjs',['aba'],110);")
client=client.replace("if(started)try{console.log", "if(started)try{const l=JSON.parse(fs.readFileSync(root+'/load-latest-private.json'));const until=fs.statSync(l.dir+'/launch-receipt.json').mtimeMs+182000;while(Date.now()<until){console.log(JSON.stringify({awaitingIndependentEndpointExpiry:true,secondsRemaining:Math.ceil((until-Date.now())/1000)}));await new Promise(r=>setTimeout(r,Math.min(15000,until-Date.now())))}console.log")
(r/'run.mjs').write_text(client,encoding='utf-8')
m={p.as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in r.iterdir()if p.is_file()and p.suffix in ('.mjs','.py','.ps1','.lua')}
(r/'entry-qualified.json').write_text(json.dumps({'passed':True,'fastAndQosUnchanged':True,'onlyOfferedTcpLoadChanged':True,'qosGroupMbps':60,'tcpOfferedMbps':48,'sameVerifiedNativeLimits':True,'checks':checks,'sourceManifest':m},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'prepared':True,'equivalenceChecks':len(checks),'qosMbps':60,'tcpOfferedMbps':48,'nativeBytesUnchanged':True,'oldInputsUntouched':True}))
