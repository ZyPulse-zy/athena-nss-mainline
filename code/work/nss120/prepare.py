"""Only raise the controlled physical-uplink group 30 -> 60 Mbps."""
from pathlib import Path
import json
r=Path('work/nss120');r.mkdir(exist_ok=True)
names=['controlled-session.mjs','current-audit-diagnostic.mjs','match-controlled.mjs','run.mjs','start-dallas.mjs','read-controlled.mjs','close-endpoint.mjs','ssh-client.mjs','bounded-pacer.mjs','server.py','discover-peer.py','probe-peer.py','endpoint-firewall-guardian.py','client-watchdog.ps1','failed-wan-owner.lua','declared-baseline.mjs','service-epoch.mjs','module-stage.mjs','payload.mjs','pack-lua.mjs','pack-guardian.mjs','compact-default-queues.mjs','uplink-tag-plan.mjs','parse-ecm-any-wan.mjs','fast-path.lua','module-stage-guardian.lua','qos-physical.lua','tag-normalizer.lua','upload-ack.mjs','upload-server.py']
for name in names:
 b=(Path('work/nss119')/name).read_bytes();s=b.replace(b'nss119',b'nss120').replace(b'NSS119',b'NSS120');assert s.replace(b'nss120',b'nss119').replace(b'NSS120',b'NSS119')==b
 if name=='start-dallas.mjs':s=s.replace(b"config.bulkDirection='upload';",b"config.bulkDirection='upload';config.experimentWan=5;")
 if name=='read-controlled.mjs':
  s=s.replace(b'const pairs=[];for(const t of tcp)',b"assert.equal(config.experimentWan,5,'Explicit comparison WAN changed');const pairs=[];for(const t of tcp)")
  s=s.replace(b'if(t.identity.wan===u.identity.wan&&',b'if(t.identity.wan===config.experimentWan&&t.identity.wan===u.identity.wan&&')
 if name=='controlled-session.mjs':s=s.replace(b'unselectedPhysicalFallbackMbps:950',b'selectedUplinkSubgroupCeilingMbps:60,unselectedPhysicalFallbackMbps:950')
 if name=='run.mjs':s=s.replace(b'QoS30 / offered32',b'downQoS30 / upQoS60 / offered32 / WAN5')
 (r/name).write_bytes(s)
for name in ['normalizer-qualification.json','uplink-capacity-private.json']:(r/name).write_bytes((Path('work/nss119')/name).read_bytes())
p=r/'qos-physical.lua';s=p.read_text(encoding='utf-8')
old=' local seenQ,seenC={},{ };local context';new=" local classHeaders=cheaders;if up then classHeaders={};for k,v in pairs(cheaders)do classHeaders[k]=v:gsub('29Mbit','59Mbit'):gsub('30Mbit','60Mbit')end end\n local seenQ,seenC={},{ };local context";assert s.count(old)==1;s=s.replace(old,new)
s=s.replace('assert(cheaders[h]and not seenC[h]', 'assert(classHeaders[h]and not seenC[h]').replace('assert(rest==cheaders[h]', 'assert(rest==classHeaders[h]')
old="if up then c=c:gsub('8f','8e')end;command(tc..' '..c)";new="if up then c=c:gsub('8f','8e'):gsub('29mbit','59mbit'):gsub('30mbit','60mbit')end;command(tc..' '..c)";assert s.count(old)==1;s=s.replace(old,new);p.write_text(s,encoding='utf-8')
print(json.dumps({'prepared':True,'controlledUplinkMbps':60,'downlinkMbps':30,'offeredUploadMbps':32,'comparisonWanSelectedNaturally':5,'routerRoutingWrites':False,'productionExecution':False}))
