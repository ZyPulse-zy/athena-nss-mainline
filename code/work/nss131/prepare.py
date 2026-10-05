from pathlib import Path
import json
r=Path('work/nss131');r.mkdir(exist_ok=True)
names=['controlled-session.mjs','current-audit-diagnostic.mjs','run.mjs','start-dallas.mjs','read-controlled.mjs','close-endpoint.mjs','match-controlled.mjs','ssh-client.mjs','bounded-pacer.mjs','server.py','discover-peer.py','probe-peer.py','endpoint-firewall-guardian.py','client-watchdog.ps1','failed-wan-owner.lua','declared-baseline.mjs','service-epoch.mjs','module-stage.mjs','payload.mjs','pack-lua.mjs','pack-guardian.mjs','compact-default-queues.mjs','uplink-tag-plan.mjs','parse-ecm-any-wan.mjs','fast-path.lua','module-stage-guardian.lua','qos-physical.lua','tag-normalizer.lua','upload-ack.mjs','upload-server.py','read-final-physical.mjs','classifier.lua','pause-control.mjs','qualify.mjs','measure-payload.mjs']
for name in names:
 b=(Path('work/nss129')/name).read_bytes();s=b.replace(b'nss129',b'nss131').replace(b'NSS129',b'NSS131');assert s.replace(b'nss131',b'nss129').replace(b'NSS131',b'NSS129')==b
 if name=='current-audit-diagnostic.mjs':
  old=b'controlled-matched-aba-';assert s.count(old)==1;s=s.replace(old,b'controlled-class-')
 if name=='qualify.mjs':
  old=b"from'../nss128/session-binding.mjs'";assert s.count(old)==1;s=s.replace(old,b"from'../nss129/session-binding.mjs'")
 (r/name).write_bytes(s)
for name in ['qos-native-qualification.json','normalizer-qualification.json','uplink-capacity-private.json']:(r/name).write_bytes((Path('work/nss129')/name).read_bytes())
b=Path('work/nss130/health.mjs').read_bytes();s=b.replace(b'nss130',b'nss131').replace(b'NSS130',b'NSS131');s=s.replace(b"knownExceptions:['Auth PID-discovery",b"knownExceptions:['Healthy native-audited classifier instance recovered before experiment','Auth PID-discovery");(r/'health.mjs').write_bytes(s)
print(json.dumps({'prepared':True,'earlierFrozenSourcesUntouched':True,'fix':'Explicit class-lifecycle case path in original audit caller','residentClassifierReinstalled':False,'productionWrites':False}))
