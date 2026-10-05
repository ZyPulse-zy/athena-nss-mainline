from pathlib import Path
import json
r=Path('work/nss128');r.mkdir(exist_ok=True)
names=['controlled-session.mjs','current-audit-diagnostic.mjs','run.mjs','start-dallas.mjs','read-controlled.mjs','close-endpoint.mjs','match-controlled.mjs','ssh-client.mjs','bounded-pacer.mjs','server.py','discover-peer.py','probe-peer.py','endpoint-firewall-guardian.py','client-watchdog.ps1','failed-wan-owner.lua','declared-baseline.mjs','service-epoch.mjs','module-stage.mjs','payload.mjs','pack-lua.mjs','pack-guardian.mjs','compact-default-queues.mjs','uplink-tag-plan.mjs','parse-ecm-any-wan.mjs','fast-path.lua','module-stage-guardian.lua','qos-physical.lua','tag-normalizer.lua','upload-ack.mjs','upload-server.py']
old="  const template=packetTemplate({decisions:[{slot:'tcp',protocol:6,downTag:2399469568,flow:selected.tcp,validUntilUptime:0},{slot:'udp',protocol:17,downTag:2399535104,flow:selected.udp,validUntilUptime:0}]},owner,unusedPort);"
new="  const classified=mapClassifiedPair(selectionFrame,selected);assert.equal(classified.decisions[0].class,'BULK');assert.equal(classified.decisions[1].class,'RT');\n  save(freeze?'post-checkpoint-class-leaf-map-proof':'initial-class-leaf-map-proof',{passed:true,mappingByActualClass:true,sourceSequence:classified.sourceSequence,sourceAge:classified.sourceAge,producer:classified.producer,nssAdmissionAllowed:false,originalDetachedClassLeaseAndKernelPinStillRequired:true,decisions:classified.decisions.map(({slot,class:category,protocol,upTag,downTag,validUntilUptime})=>({slot,class:category,protocol,upTag,downTag,validUntilUptime}))});\n  const template=packetTemplate(classified,owner,unusedPort);"
for name in names:
 b=(Path('work/nss125')/name).read_bytes();s=b.replace(b'nss125',b'nss128').replace(b'NSS125',b'NSS128');assert s.replace(b'nss128',b'nss125').replace(b'NSS128',b'NSS125')==b
 if name=='controlled-session.mjs':assert s.count(old.encode())==1;s=s.replace(old.encode(),new.encode());s=b"import{mapClassifiedPair}from'../nss127/class-leaf-map.mjs';\n"+s
 if name=='run.mjs':s=s.replace(b'NSS128 all-WAN counter observation',b'NSS128 actual-class to dual-leaf mapping')
 (r/name).write_bytes(s)
(r/'uplink-tag-plan.mjs').write_bytes(Path('work/nss127/uplink-tag-plan.mjs').read_bytes())
for name in ['qos-native-qualification.json','normalizer-qualification.json','uplink-capacity-private.json']:(r/name).write_bytes((Path('work/nss125')/name).read_bytes())
print(json.dumps({'prepared':True,'onlyMappingSourceChanged':True,'sameNativePayloadAndScope':True,'productionExecution':False}))
