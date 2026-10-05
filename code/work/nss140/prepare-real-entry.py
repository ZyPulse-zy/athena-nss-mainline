from pathlib import Path
import json
w=Path(__file__).resolve().parents[2];r=w/'work/nss140'
for name in ['real-session.mjs','record-candidates.mjs','read-real-candidates.mjs']:
 s=(w/'work/nss77'/name).read_text(encoding='utf-8').replace('nss77','nss140').replace('NSS77','NSS140')
 if name=='read-real-candidates.mjs':
  anchor="const plan={base:ctx.base,configSha256:ctx.configHash,workerSha256:cfg.files['worker.lua']};"
  assert s.count(anchor)==1
  s=s.replace(anchor,anchor+"\nconst names=new Map(pc.processes.map(p=>[p.pid,p.name]));const allowedTcp=pc.tcp.filter(x=>names.get(x.OwningProcess)==='steam');const allowedUdp=pc.udp.filter(x=>names.get(x.OwningProcess)==='cs2');assert.ok(allowedTcp.length<=128&&allowedUdp.length<=128,'Application socket inventory exceeds bounded reader');const sockets={tcp:allowedTcp,udp:allowedUdp};")
  begin=s.index('local r={deadline=now()+10};');end=s.index('const result=assert(j.stringify',begin)if 'const result=assert(j.stringify'in s else s.index('local result=assert(j.stringify',begin)
  old=s[begin:end]
  new="""local r={deadline=now()+10};local a=A.new(P,fs,j,read,now,run,r);local candidates=a.candidates();local flows={};local sockets=assert(j.parse([====[${JSON.stringify(sockets)}]====]))
for _,f in ipairs(candidates.flows)do local i,d=f.identity,f.decision;local owned=false
if i.original.src=='192.168.237.207'and math.floor(i.mark/8192)%2==0 then
 if i.protocolNumber==6 and d.class=='BULK'then for _,e in ipairs(sockets.tcp)do if e.LocalPort==i.original.sport and e.RemoteAddress==i.original.dst and e.RemotePort==i.original.dport and(e.LocalAddress==i.original.src or e.LocalAddress=='0.0.0.0'or e.LocalAddress=='::')then owned=true end end
 elseif i.protocolNumber==17 and d.class=='RT'and d.budgetAdmitted then for _,e in ipairs(sockets.udp)do if e.LocalPort==i.original.sport and(e.LocalAddress==i.original.src or e.LocalAddress=='0.0.0.0'or e.LocalAddress=='::')then owned=true end end end
end
if owned then flows[#flows+1]=f;assert(#flows<=128,'Candidate count exceeds bounded reader')end end
"""
  s=s[:begin]+new+s[end:]
  target="const {flows,...meta}=native;const out={...meta,game,bulk,";assert s.count(target)==1;s=s.replace(target,"const out={...native,game,bulk,")
 if name=='real-session.mjs':
  s="import{mapClassifiedPair}from'../nss127/class-leaf-map.mjs';\nimport{auditScopedBaseline}from'./declared-baseline.mjs';\nimport{compactDefaultQueues}from'./compact-default-queues.mjs';\n"+s
  s=s.replace("from '../nss50/service-epoch.mjs'","from './service-epoch.mjs'").replace("from '../nss49/parse-ecm-any-wan.mjs'","from './parse-ecm-any-wan.mjs'").replace("from '../nss16/automatic-leaf-plan.mjs'","from './uplink-tag-plan.mjs'")
  target="verifyEpochServices(JSON.parse(fs.readFileSync(dir+'/service-epoch-private.json')).services,before.services);";assert s.count(target)==1;s=s.replace(target,target+"auditScopedBaseline(JSON.parse(fs.readFileSync(dir+'/prewrite-baseline-private.json')),before);")
  target="const pin=JSON.parse(fs.readFileSync('work/nss16/qos-capacity-private.json'));assert.equal(pin.boot.trim(),wan.boot);";assert s.count(target)==1;s=s.replace(target,"const pin=JSON.parse(fs.readFileSync('work/nss16/qos-capacity-private.json'));const up=JSON.parse(fs.readFileSync('work/nss140/uplink-capacity-private.json'));assert.equal(up.boot,wan.boot);assert.equal(up.device,'wan');assert.equal(up.ifindex,6);assert.equal(pin.boot.trim(),wan.boot);")
  target="const template=packetTemplate({decisions:[{slot:'tcp',protocol:6,downTag:2399469568,flow:selected.tcp,validUntilUptime:0},{slot:'udp',protocol:17,downTag:2399535104,flow:selected.udp,validUntilUptime:0}]},owner,unusedPort);";assert s.count(target)==1
  s=s.replace(target,"const classified=mapClassifiedPair(selectionFrame,selected);assert.equal(classified.decisions[0].class,'BULK');assert.equal(classified.decisions[1].class,'RT');save(freeze?'post-checkpoint-class-leaf-map-proof':'initial-class-leaf-map-proof',{passed:true,mappingByActualClass:true,sourceSequence:classified.sourceSequence,sourceAge:classified.sourceAge,producer:classified.producer,nssAdmissionAllowed:false,originalDetachedClassLeaseAndKernelPinStillRequired:true,decisions:classified.decisions.map(({slot,class:category,protocol,upTag,downTag,validUntilUptime})=>({slot,class:category,protocol,upTag,downTag,validUntilUptime}))});const template=packetTemplate(classified,owner,unusedPort);")
  target="qosBaseline:pin.interfaces.lan4.qdiscs,qosBoot:wan.boot}";assert s.count(target)==1;s=s.replace(target,"qosBaseline:compactDefaultQueues(pin.interfaces.lan4.qdiscs),qosBoot:wan.boot,uplinkDevice:'wan',uplinkIfindex:6,uplinkPhysicalAeId:5,uplinkBaseline:compactDefaultQueues(up.defaultQueues)}")
  s=s.replace('for(let i=0;i<26;i++)','for(let i=0;i<60;i++)').replace("'qosModuleUnloaded','wanRestored'","'qosModuleUnloaded','dualPhysicalQueuesRestored','wanRestored'")
  s=s.replace('p.seconds>=5&&p.seconds<=6.5&&p.sampleCount>=8','p.seconds>=20&&p.seconds<=21.5&&p.sampleCount>=40').replace('selectedSubgroupCeilingMbps:20','selectedSubgroupCeilingMbps:30')
  s=s.replace('auditBaseline(before,{...after,native:before.native})','auditScopedBaseline(before,after)')
 (r/name).write_text(s,encoding='utf-8')
print(json.dumps({'preparedRealEntry':True,'defaultInspectionOnly':True,'completeRowsOnlyForActualLocalApplicationOwnedSockets':True,'originalSourceAndOutputReadLimitsKept':True,'actualClassDerivedDualTagsBeforeLearning':True,'productionWrites':False}))
