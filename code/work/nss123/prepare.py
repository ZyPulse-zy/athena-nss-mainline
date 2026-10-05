from pathlib import Path
import json
r=Path('work/nss123');r.mkdir(exist_ok=True)
names=['controlled-session.mjs','current-audit-diagnostic.mjs','run.mjs','start-dallas.mjs','read-controlled.mjs','close-endpoint.mjs','ssh-client.mjs','bounded-pacer.mjs','server.py','discover-peer.py','probe-peer.py','endpoint-firewall-guardian.py','client-watchdog.ps1','failed-wan-owner.lua','declared-baseline.mjs','service-epoch.mjs','module-stage.mjs','payload.mjs','pack-lua.mjs','pack-guardian.mjs','compact-default-queues.mjs','uplink-tag-plan.mjs','parse-ecm-any-wan.mjs','fast-path.lua','module-stage-guardian.lua','qos-physical.lua','tag-normalizer.lua','upload-ack.mjs','upload-server.py']
for name in names:
 b=(Path('work/nss120')/name).read_bytes();s=b.replace(b'nss120',b'nss123').replace(b'NSS120',b'NSS123');assert s.replace(b'nss123',b'nss120').replace(b'NSS123',b'NSS120')==b
 if name=='current-audit-diagnostic.mjs':s=s.replace(b"from '../nss68/wait-publication-metadata.mjs'",b"from '../nss122/wait-publication-metadata.mjs'")
 (r/name).write_bytes(s)
s=Path('work/nss121/match-target.mjs').read_text(encoding='utf-8').replace('nss120','nss123');(r/'match-controlled.mjs').write_text(s,encoding='utf-8');(r/'natural-target.mjs').write_bytes(Path('work/nss121/natural-target.mjs').read_bytes())
for name in ['qos-native-qualification.json','normalizer-qualification.json','uplink-capacity-private.json']:(r/name).write_bytes((Path('work/nss120')/name).read_bytes())
print(json.dumps({'prepared':True,'uplinkMbps':60,'downlinkMbps':30,'offeredMbps':32,'nssPayloadUnchangedFromQualified120':True,'atomicHintOneDiscardRetry':True,'naturalWanSelectionOnly':5,'productionExecution':False}))
