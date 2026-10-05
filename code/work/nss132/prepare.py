from pathlib import Path
import json
r=Path('work/nss132');r.mkdir(exist_ok=True)
names=['controlled-session.mjs','current-audit-diagnostic.mjs','run.mjs','start-dallas.mjs','read-controlled.mjs','close-endpoint.mjs','match-controlled.mjs','ssh-client.mjs','bounded-pacer.mjs','server.py','discover-peer.py','probe-peer.py','endpoint-firewall-guardian.py','client-watchdog.ps1','failed-wan-owner.lua','declared-baseline.mjs','service-epoch.mjs','module-stage.mjs','payload.mjs','pack-lua.mjs','pack-guardian.mjs','compact-default-queues.mjs','uplink-tag-plan.mjs','parse-ecm-any-wan.mjs','fast-path.lua','module-stage-guardian.lua','qos-physical.lua','tag-normalizer.lua','upload-ack.mjs','upload-server.py','health.mjs','read-final-physical.mjs','classifier.lua','pause-control.mjs','qualify.mjs']
for name in names:
 b=(Path('work/nss131')/name).read_bytes();s=b.replace(b'nss131',b'nss132').replace(b'NSS131',b'NSS132');assert s.replace(b'nss132',b'nss131').replace(b'NSS132',b'NSS131')==b
 if name=='pause-control.mjs':
  old=b'pauseAfterOwnedAcceleration(load,context){\n const c=await connectRouter(),due=';assert s.count(old)==1;s=s.replace(old,b'pauseAfterOwnedAcceleration(load,context,c){\n assert.ok(c&&typeof c.run===\'function\');const due=')
 if name=='controlled-session.mjs':
  old=b"const pauseWatcher=mode==='change'?pauseAfterOwnedAcceleration(load,context):Promise.resolve(null);let pauseFailure;";assert s.count(old)==1
  s=s.replace(old,b"const workingDirectory=process.cwd();const pauseConnection=mode==='change'?await connectRouter():null;assert.equal(process.cwd(),workingDirectory,'Connection did not restore working directory');\n  const pauseWatcher=mode==='change'?pauseAfterOwnedAcceleration(load,context,pauseConnection):Promise.resolve(null);let pauseFailure;")
 if name=='qualify.mjs':
  old=b"from'../nss129/session-binding.mjs'";assert s.count(old)==1;s=s.replace(old,b"from'../nss131/session-binding.mjs'")
 (r/name).write_bytes(s)
for name in ['qos-native-qualification.json','normalizer-qualification.json','uplink-capacity-private.json']:(r/name).write_bytes((Path('work/nss131')/name).read_bytes())
print(json.dumps({'prepared':True,'fix':'Sequential credential connection construction; watcher receives existing connection','sameRetirementAndHardwarePolicy':True,'previousFrozenSourcesUntouched':True,'productionWrites':False}))
