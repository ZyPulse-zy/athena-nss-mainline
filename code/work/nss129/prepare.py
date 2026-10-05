from pathlib import Path
import json

r=Path('work/nss129')
r.mkdir(exist_ok=True)
names=['controlled-session.mjs','current-audit-diagnostic.mjs','run.mjs','start-dallas.mjs','read-controlled.mjs','close-endpoint.mjs','match-controlled.mjs','ssh-client.mjs','bounded-pacer.mjs','server.py','discover-peer.py','probe-peer.py','endpoint-firewall-guardian.py','client-watchdog.ps1','failed-wan-owner.lua','declared-baseline.mjs','service-epoch.mjs','module-stage.mjs','payload.mjs','pack-lua.mjs','pack-guardian.mjs','compact-default-queues.mjs','uplink-tag-plan.mjs','parse-ecm-any-wan.mjs','fast-path.lua','module-stage-guardian.lua','qos-physical.lua','tag-normalizer.lua','upload-ack.mjs','upload-server.py','health.mjs','read-final-physical.mjs']
for name in names:
    b=(Path('work/nss128')/name).read_bytes()
    s=b.replace(b'nss128',b'nss129').replace(b'NSS128',b'NSS129')
    assert s.replace(b'nss129',b'nss128').replace(b'NSS129',b'NSS128')==b
    (r/name).write_bytes(s)
for name in ['qos-native-qualification.json','normalizer-qualification.json','uplink-capacity-private.json']:
    (r/name).write_bytes((Path('work/nss128')/name).read_bytes())
(r/'classifier.lua').write_bytes(Path('work/nss73/classifier.lua').read_bytes())
print(json.dumps({'prepared':True,'previousFrozenSourcesUntouched':True,'productionWrites':False}))
