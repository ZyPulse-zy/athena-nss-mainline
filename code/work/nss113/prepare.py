from pathlib import Path
import hashlib,json
r=Path('work/nss113');r.mkdir(exist_ok=True)
names=['controlled-session.mjs','current-audit-diagnostic.mjs','match-controlled.mjs','run.mjs','start-dallas.mjs','read-controlled.mjs','close-endpoint.mjs','ssh-client.mjs','server.py','discover-peer.py','probe-peer.py','endpoint-firewall-guardian.py','client-watchdog.ps1','failed-wan-owner.lua','declared-baseline.mjs','service-epoch.mjs','module-stage.mjs','payload.mjs','pack-lua.mjs','uplink-tag-plan.mjs','parse-ecm-any-wan.mjs','fast-path.lua','module-stage-guardian.lua','qos-physical.lua']
for name in names:
 s=(Path('work/nss112')/name).read_bytes();v=s.replace(b'nss112',b'nss113').replace(b'NSS112',b'NSS113')
 assert v.replace(b'nss113',b'nss112').replace(b'NSS113',b'NSS112')==s
 (r/name).write_bytes(v)
(r/'uplink-capacity-private.json').write_bytes(Path('work/nss112/uplink-capacity-private.json').read_bytes())
print(json.dumps({'prepared':True,'copiedSources':len(names),'productionWrites':False}))
