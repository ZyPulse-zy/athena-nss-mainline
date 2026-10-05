from pathlib import Path
import json
r=Path('work/nss124');r.mkdir(exist_ok=True)
names=['controlled-session.mjs','current-audit-diagnostic.mjs','run.mjs','start-dallas.mjs','read-controlled.mjs','close-endpoint.mjs','ssh-client.mjs','bounded-pacer.mjs','server.py','discover-peer.py','probe-peer.py','endpoint-firewall-guardian.py','client-watchdog.ps1','failed-wan-owner.lua','declared-baseline.mjs','service-epoch.mjs','module-stage.mjs','payload.mjs','pack-lua.mjs','pack-guardian.mjs','compact-default-queues.mjs','uplink-tag-plan.mjs','parse-ecm-any-wan.mjs','fast-path.lua','module-stage-guardian.lua','qos-physical.lua','tag-normalizer.lua','upload-ack.mjs','upload-server.py']
for name in names:
 b=(Path('work/nss123')/name).read_bytes();s=b.replace(b'nss123',b'nss124').replace(b'NSS123',b'NSS124');assert s.replace(b'nss124',b'nss123').replace(b'NSS124',b'NSS123')==b
 if name=='start-dallas.mjs':s=s.replace(b'config.experimentWan=5;',b'')
 if name=='read-controlled.mjs':s=s.replace(b"assert.equal(config.experimentWan,5,'Explicit comparison WAN changed');",b'').replace(b't.identity.wan===config.experimentWan&&',b'')
 if name=='run.mjs':s=s.replace(b' / WAN5',b' / natural healthy WAN')
 (r/name).write_bytes(s)
s=Path('work/nss119/match-controlled.mjs').read_text(encoding='utf-8').replace('nss119','nss124');(r/'match-controlled.mjs').write_text(s,encoding='utf-8')
for name in ['qos-native-qualification.json','normalizer-qualification.json','uplink-capacity-private.json']:(r/name).write_bytes((Path('work/nss123')/name).read_bytes())
print(json.dumps({'prepared':True,'hardwarePayloadUnchangedFrom123':True,'uplinkMbps':60,'downlinkMbps':30,'offeredMbps':32,'udpSocketAndPinnedEndpointPeerFixed':True,'onlyOwnedTcpPortsRotated':True,'productionExecution':False}))
