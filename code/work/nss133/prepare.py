from pathlib import Path
import json
r=Path('work/nss133');r.mkdir(exist_ok=True)
names=['controlled-session.mjs','current-audit-diagnostic.mjs','run.mjs','start-dallas.mjs','read-controlled.mjs','close-endpoint.mjs','match-controlled.mjs','ssh-client.mjs','bounded-pacer.mjs','server.py','discover-peer.py','probe-peer.py','endpoint-firewall-guardian.py','client-watchdog.ps1','failed-wan-owner.lua','declared-baseline.mjs','service-epoch.mjs','module-stage.mjs','payload.mjs','pack-lua.mjs','pack-guardian.mjs','compact-default-queues.mjs','uplink-tag-plan.mjs','parse-ecm-any-wan.mjs','fast-path.lua','module-stage-guardian.lua','qos-physical.lua','tag-normalizer.lua','upload-ack.mjs','upload-server.py','health.mjs','read-final-physical.mjs','classifier.lua','pause-control.mjs']
for name in names:
 b=(Path('work/nss132')/name).read_bytes();s=b.replace(b'nss132',b'nss133').replace(b'NSS132',b'NSS133');assert s.replace(b'nss133',b'nss132').replace(b'NSS133',b'NSS132')==b;(r/name).write_bytes(s)
for name in ['qos-native-qualification.json','normalizer-qualification.json','uplink-capacity-private.json']:(r/name).write_bytes((Path('work/nss132')/name).read_bytes())
print(json.dumps({'prepared':True,'unmodifiedEntryRetryInNewNamespace':True,'productionWrites':False}))
