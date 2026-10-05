"""Only replace elapsed-time backlog pacing with bounded credit."""
from pathlib import Path
import json
r=Path('work/nss119');r.mkdir(exist_ok=True)
names=['controlled-session.mjs','current-audit-diagnostic.mjs','match-controlled.mjs','run.mjs','start-dallas.mjs','read-controlled.mjs','close-endpoint.mjs','ssh-client.mjs','server.py','discover-peer.py','probe-peer.py','endpoint-firewall-guardian.py','client-watchdog.ps1','failed-wan-owner.lua','declared-baseline.mjs','service-epoch.mjs','module-stage.mjs','payload.mjs','pack-lua.mjs','pack-guardian.mjs','compact-default-queues.mjs','uplink-tag-plan.mjs','parse-ecm-any-wan.mjs','fast-path.lua','module-stage-guardian.lua','qos-physical.lua','tag-normalizer.lua','upload-ack.mjs','upload-server.py']
for name in names:
 b=(Path('work/nss118')/name).read_bytes();v=b.replace(b'nss118',b'nss119').replace(b'NSS118',b'NSS119');assert v.replace(b'nss119',b'nss118').replace(b'NSS119',b'NSS118')==b;(r/name).write_bytes(v)
for name in ['qos-native-qualification.json','normalizer-qualification.json','uplink-capacity-private.json']:(r/name).write_bytes((Path('work/nss118')/name).read_bytes())
p=r/'ssh-client.mjs';s=p.read_text(encoding='utf-8');s=s.replace("import{uploadAck}from'./upload-ack.mjs';","import{uploadAck}from'./upload-ack.mjs';import{createPacer}from'./bounded-pacer.mjs';");s=s.replace("tcpMetric:'server-confirmed received bytes'","tcpMetric:'server-confirmed received bytes',pacerDebtCatchupAllowed:false,maximumPacerCreditBytes:65536")
s=s.replace('deliveredBase=stats.tcpBytes,begin=performance.now();','deliveredBase=stats.tcpBytes,begin=performance.now(),pacer=createPacer(begin,32000000/8);')
old="if(current!==client||ended||blocked)return;const target=(performance.now()-begin)/1000*32000000/8;try{for(let i=0;i<4&&submitted<target;i++){"
new="if(current!==client||ended)return;const at=performance.now();try{for(let i=0;i<4&&pacer.next(at,blocked);i++){"
assert s.count(old)==1;s=s.replace(old,new);p.write_text(s,encoding='utf-8')
print(json.dumps({'prepared':True,'onlyUploadPacingChanged':True,'offeredMbps':32,'maximumPacerCreditBytes':65536,'queueRatesChanged':False,'productionExecution':False}))
