"""Only reduce the offered upload 48 -> 32; router bytes remain identical."""
from pathlib import Path
import json
r=Path('work/nss118');r.mkdir(exist_ok=True)
names=['controlled-session.mjs','current-audit-diagnostic.mjs','match-controlled.mjs','run.mjs','start-dallas.mjs','read-controlled.mjs','close-endpoint.mjs','ssh-client.mjs','server.py','discover-peer.py','probe-peer.py','endpoint-firewall-guardian.py','client-watchdog.ps1','failed-wan-owner.lua','declared-baseline.mjs','service-epoch.mjs','module-stage.mjs','payload.mjs','pack-lua.mjs','pack-guardian.mjs','compact-default-queues.mjs','uplink-tag-plan.mjs','parse-ecm-any-wan.mjs','fast-path.lua','module-stage-guardian.lua','qos-physical.lua','tag-normalizer.lua','upload-ack.mjs','upload-server.py']
for name in names:
 b=(Path('work/nss116')/name).read_bytes();s=b.replace(b'nss116',b'nss118').replace(b'NSS116',b'NSS118');assert s.replace(b'nss118',b'nss116').replace(b'NSS118',b'NSS116')==b
 if name=='start-dallas.mjs':assert s.count(b'config.mbps=48;')==1;s=s.replace(b'config.mbps=48;',b'config.mbps=32;')
 if name=='ssh-client.mjs':
  assert s.count(b'c.mbps===48')==1 and s.count(b'*48000000/8')==1;s=s.replace(b'c.mbps===48',b'c.mbps===32').replace(b'*48000000/8',b'*32000000/8')
 if name=='run.mjs':s=s.replace(b'offered48',b'offered32').replace(b'offeredMbps:48',b'offeredMbps:32')
 (r/name).write_bytes(s)
for name in ['qos-native-qualification.json','normalizer-qualification.json','uplink-capacity-private.json']:(r/name).write_bytes((Path('work/nss116')/name).read_bytes())
print(json.dumps({'prepared':True,'onlyOfferedUploadChanged':True,'offeredMbps':32,'qosParentMbps':30,'productionExecution':False}))
