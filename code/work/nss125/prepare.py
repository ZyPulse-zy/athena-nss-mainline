from pathlib import Path
import json
r=Path('work/nss125');r.mkdir(exist_ok=True)
names=['controlled-session.mjs','current-audit-diagnostic.mjs','run.mjs','start-dallas.mjs','read-controlled.mjs','close-endpoint.mjs','match-controlled.mjs','ssh-client.mjs','bounded-pacer.mjs','server.py','discover-peer.py','probe-peer.py','endpoint-firewall-guardian.py','client-watchdog.ps1','failed-wan-owner.lua','declared-baseline.mjs','service-epoch.mjs','module-stage.mjs','payload.mjs','pack-lua.mjs','pack-guardian.mjs','compact-default-queues.mjs','uplink-tag-plan.mjs','parse-ecm-any-wan.mjs','fast-path.lua','module-stage-guardian.lua','qos-physical.lua','tag-normalizer.lua','upload-ack.mjs','upload-server.py']
old="{'rpwan'..assert(P.selected.tcp.wan),'lan4'}";new="{'rpwan1','rpwan2','rpwan3','rpwan4','rpwan5','wan','lan4'}"
for name in names:
 b=(Path('work/nss124')/name).read_bytes();s=b.replace(b'nss124',b'nss125').replace(b'NSS124',b'NSS125');assert s.replace(b'nss125',b'nss124').replace(b'NSS125',b'NSS124')==b
 if name=='fast-path.lua':assert s.count(old.encode())==1;s=s.replace(old.encode(),new.encode())
 if name=='run.mjs':s=s.replace(b'NSS125 dual physical queue/tag mapping',b'NSS125 all-WAN counter observation')
 (r/name).write_bytes(s)
for name in ['qos-native-qualification.json','normalizer-qualification.json','uplink-capacity-private.json']:(r/name).write_bytes((Path('work/nss124')/name).read_bytes())
print(json.dumps({'prepared':True,'onlyCommonReadOnlyInterfaceListChanged':True,'uplinkMbps':60,'downlinkMbps':30,'offeredMbps':32,'productionExecution':False}))
