local Consumer=(function()
local M={}
local function int(v,a,b)return type(v)=='number'and v==math.floor(v)and v>=a and v<=b end
local function equal(a,b)
 if type(a)~=type(b)then return false end;if type(a)~='table'then return a==b end
 for k,v in pairs(a)do if not equal(v,b[k])then return false end end
 for k in pairs(b)do if a[k]==nil then return false end end;return true
end
local function tuple(t)
 assert(type(t)=='table')
 for _,k in ipairs({'src','dst'})do
  assert(type(t[k])=='string'and t[k]:match('^%d+%.%d+%.%d+%.%d+$'))
  local count=0;for x in t[k]:gmatch('%d+')do assert(#x<=3 and tonumber(x)<=255 and(#x==1 or x:sub(1,1)~='0'));count=count+1 end;assert(count==4)
 end
 assert(int(t.sport,1,65535)and int(t.dport,1,65535))
 return{src=t.src,dst=t.dst,sport=t.sport,dport=t.dport}
end
function M.inspect(s,c,now)
 assert(type(now)=='number'and now>=0)
 assert(s.version==23 and s.status=='running'and not s.error and s.nssPermit==false,'Unhealthy classifier')
 assert(s.generation==c.generation and s.boot==c.boot and s.configSha256==c.configSha256,'Classifier provenance changed')
 assert(c.alive==true and c.workerArgv==table.concat({'/usr/bin/lua',c.base..'/worker.lua','watch',c.base,c.configSha256},'\0')..'\0','Classifier process absent or wrong argv')
 assert(s.pid==c.pid and s.start==c.start and s.producer==c.generation..':'..c.boot..':'..c.pid..':'..c.start,'Classifier process instance changed')
 assert(c.stopped==false and c.guardianHealthy==true,'Independent classifier guardian unhealthy')
 assert(s.atUptime<=now and now-s.atUptime<6,'Classifier publication stale')
 local snap=assert(s.snapshot);local p=assert(snap.provenance)
 assert(p.version==1 and p.method=='conntrack-cli'and p.rawStatus==0 and p.exitCode==0 and p.boot==c.boot)
 assert(p.command==c.sourceCommand and p.queryFamily=='ipv4'and p.queryZone==0 and p.authorizedClient=='192.168.237.0/24','Source scope changed')
 assert(int(p.sequence,1,9007199254740991))
 assert(type(p.startedAtUptime)=='number'and type(p.finishedAtUptime)=='number'and p.startedAtUptime<=p.finishedAtUptime and p.finishedAtUptime<=now)
 assert(p.finishedAtUptime-p.startedAtUptime<=2 and now<p.startedAtUptime+6,'Classifier query stale')
 local found,counts,keys={},{},{}
 for _,f in ipairs(snap.flows)do
  assert(type(f.key)=='string'and not keys[f.key],'Duplicate classifier identity');keys[f.key]=true
  local i,d,l=assert(f.identity),assert(f.decision),assert(f.leaf)
  assert(int(i.wan,1,5)and int(i.mark,0,4294967295)and math.floor(i.mark/65536)%256==i.wan)
  assert(i.protocolNumber==6 or i.protocolNumber==17);assert(i.protocol==(i.protocolNumber==6 and'tcp'or'udp'))
  assert(i.instanceTagSafe==true and i.instanceMetadataComplete==true and i.kernelCTObjectPinned==false and i.nssPermit==false)
  assert(tonumber(i.zone)==0 and int(tonumber(i.connectionId),1,4294967295))
  local o,r=tuple(i.original),tuple(i.reply);local u=tuple(i.natUpload)
  assert(o.src:match('^192%.168%.237%.')and o.dst==r.src and o.dport==r.sport)
  assert(equal(u,{src=r.dst,dst=r.src,sport=r.dport,dport=r.sport}),'NAT upload identity drift')
  assert(f.key==table.concat({i.wan,i.mark,i.protocol,o.src,o.sport,r.src,r.dst,r.sport,r.dport,i.zone,i.connectionId},'|'),'Classifier key drift')
  local q=assert(i.queryProvenance)
  assert(q.querySequence==p.sequence and q.startedAtUptime==p.startedAtUptime and q.finishedAtUptime==p.finishedAtUptime and q.idFieldPresent==true and q.fullMarkFieldPresent==true)
  assert(q.zoneSource=='successful-explicit-zone0-query'or q.zoneSource=='explicit-row-zone0')
  assert(f.observationStartedAtUptime==p.startedAtUptime and f.observedAtUptime==p.finishedAtUptime)
  assert(type(f.validUntilUptime)=='number'and f.validUntilUptime<=p.startedAtUptime+6 and now<f.validUntilUptime)
  local rt=d.class=='RT'and d.budgetAdmitted==true
  local bulk=d.class=='BULK'and d.reason=='bulk'
  assert(l.nssPermit==false and l.requiresKernelCTPin==true and l.requiresFreshOwner==true and l.requiresDefaultDenyGate==true and l.changeRequiresExactRetire==true and l.upTag==0 and l.class==d.class)
  assert(l.candidate==(rt or bulk)and l.downTag==(rt and 2399535104 or bulk and 2399469568 or 0),'Leaf mapping drift')
  counts[d.class]=(counts[d.class]or 0)+1
  if rt or bulk then found[#found+1]=f end
 end
 return{candidates=found,classCounts=counts,provenance=p,producer=s.producer,nssAdmissionAllowed=false}
end
function M.pair(s,c,now,selected)
 local checked=M.inspect(s,c,now);local byKey={};for _,f in ipairs(checked.candidates)do byKey[f.key]=f end
 local out={decisions={},producer=checked.producer,sourceSequence=checked.provenance.sequence,epochUntil=checked.provenance.startedAtUptime+6,nssAdmissionAllowed=false,kernelPinsStillRequired=true,tagGetterAndLeafProofStillRequired=true,continuousFreshnessAndScopedRetirementStillRequired=true}
 for _,slot in ipairs({'tcp','udp'})do
  local w=assert(selected[slot]);local f=assert(byKey[w.classifierKey],'Selected class is not admitted');local i,d=f.identity,f.decision
  local proto=slot=='tcp'and 6 or 17;local target=slot=='tcp'and'BULK'or'RT'
  assert(i.protocolNumber==proto and w.protocol==proto and d.class==target)
  assert(w.zone==0 and tonumber(i.connectionId)==w.id and i.mark==w.mark and i.wan==w.wan)
  assert(equal(tuple(i.original),w.original)and equal(tuple(i.reply),w.reply),'Selected CT/NAT tuple drift')
  assert(i.original.src==c.authorizedClient,'Selected client not authorized')
  assert(math.floor(i.mark/8192)%2==0,'Proxy-marked flow refused')
  out.epochUntil=math.min(out.epochUntil,f.validUntilUptime);local untilAt=out.epochUntil
  out.decisions[#out.decisions+1]={slot=slot,class=target,protocol=proto,downTag=f.leaf.downTag,upTag=0,flow=w,validUntilUptime=untilAt,classifierKey=f.key}
 end
 assert(selected.tcp.wan~=selected.udp.wan,'Distinct naturally selected WANs required')
 assert(now<out.epochUntil-3,'Pre-learning time margin insufficient')
 for _,d in ipairs(out.decisions)do assert(now<d.validUntilUptime-3,'Per-flow pre-learning time margin insufficient')end
 return out
end
function M.compareEpoch(epoch,s,c,now,closed)
 local ok,checked=pcall(M.inspect,s,c,now);local affected={}
 if not ok or epoch.producer~=(s and s.producer)or(not closed and now>=epoch.epochUntil)then
  for _,d in ipairs(epoch.decisions)do affected[#affected+1]=d.slot end
 else
  local map={};for _,f in ipairs(checked.candidates)do map[f.key]=f end
  for _,d in ipairs(epoch.decisions)do
   local f=map[d.classifierKey];local i=f and f.identity
   if not f or f.decision.class~=d.class or f.leaf.downTag~=d.downTag or tonumber(i.connectionId)~=d.flow.id or i.mark~=d.flow.mark or i.wan~=d.flow.wan or not equal(tuple(i.original),d.flow.original)or not equal(tuple(i.reply),d.flow.reply)then affected[#affected+1]=d.slot end
  end
 end
 if #affected==0 then return{action='KEEP_IMMUTABLE_EPOCH',extendsExpiry=false,nssAdmissionAllowed=false}end
 return{action='RETIRE_EXACT_SELECTED_SLOTS',affected=affected,nssAdmissionAllowed=false,clearConntrack=false,changeQoSBeforeRetirement=false,
  order={'stop new ECM learning','deny affected gate slot','wait CPU reader barrier and request exact two-direction CI retirement','verify hardware retirement and CI absence','remove old exact tags','obtain fresh classification and CT pins before relearning'},
  reason=not ok and tostring(checked)or now>=epoch.epochUntil and'epoch expired'or'producer, connection identity, or class changed'}
end
return M

end)()
local describeSelection=(function()
local function tupleEqual(a,b)
 if type(a)~='table'or type(b)~='table'then return false end
 for _,k in ipairs({'src','dst','sport','dport'})do if a[k]~=b[k]then return false end end
 return true
end
return function(s,selected,at)
 local snap=type(s)=='table'and s.snapshot;local p=type(snap)=='table'and snap.provenance
 local flows=type(snap)=='table'and type(snap.flows)=='table'and snap.flows or{}
 local projection=type(snap)=='table'and type(snap.admissionProjection)=='table'and snap.admissionProjection.scope=='bulk-and-admitted-rt'
 local out={diagnosticOnly=true,nssAdmissionAllowed=false,sameAdmissionFrame=true,checkedAtUptime=at,slots={},flowCount=#flows,scanLimit=2048,scanTruncated=#flows>2048,admissionProjectionOnly=projection==true}
 if type(p)=='table'then out.sourceSequence=p.sequence;out.startedAtUptime=p.startedAtUptime;out.finishedAtUptime=p.finishedAtUptime end
 for _,slot in ipairs({'tcp','udp'})do
  local w=type(selected)=='table'and selected[slot];local d={expectedClass=slot=='tcp'and'BULK'or'RT',selectedInputPresent=type(w)=='table',present=false,matches=0}
  out.slots[slot]=d
  if type(w)=='table'and type(w.classifierKey)=='string'then
   local found
   for k=1,math.min(#flows,2048)do local f=flows[k];if type(f)=='table'and f.key==w.classifierKey then found=f;d.matches=d.matches+1 end end
   d.present=found~=nil
   if found then
    local i=type(found.identity)=='table'and found.identity or{};local dec=type(found.decision)=='table'and found.decision or{};local leaf=type(found.leaf)=='table'and found.leaf or{}
    d.class=dec.class;d.reason=dec.reason;d.budgetAdmitted=dec.budgetAdmitted;d.pps=dec.pps;d.rateKbps=dec.rateKbps
    d.targetClassMatches=dec.class==d.expectedClass
    d.candidate=(dec.class=='RT'and dec.budgetAdmitted==true)or(dec.class=='BULK'and dec.reason=='bulk')
    d.ctMatches=tonumber(i.connectionId)==w.id;d.zoneMatches=tonumber(i.zone)==w.zone;d.markMatches=i.mark==w.mark;d.wanMatches=i.wan==w.wan
    d.originalMatches=tupleEqual(i.original,w.original);d.replyMatches=tupleEqual(i.reply,w.reply)
    d.downTag=leaf.downTag;d.leafTagMatches=leaf.downTag==(slot=='tcp'and 2399469568 or 2399535104)
    d.validUntilUptime=found.validUntilUptime
    if type(found.validUntilUptime)=='number'and type(at)=='number'then d.validRemainingSeconds=found.validUntilUptime-at end
    if d.matches~=1 then d.reasonCode='DUPLICATE_EXACT_KEY'
    elseif not d.targetClassMatches then d.reasonCode='TARGET_CLASS_MISMATCH'
    elseif slot=='udp'and dec.budgetAdmitted~=true then d.reasonCode='RT_BUDGET_NOT_ADMITTED'
    elseif slot=='tcp'and dec.reason~='bulk'then d.reasonCode='BULK_REASON_NOT_ADMITTED'
    else d.reasonCode='TARGET_CLASS_ADMITTED'end
   else d.reasonCode=out.scanTruncated and'EXACT_KEY_NOT_FOUND_IN_BOUNDED_SCAN'or projection and'NOT_IN_ADMISSION_PROJECTION'or'EXACT_KEY_ABSENT';d.completeInputPresenceKnown=not projection and not out.scanTruncated end
  else d.reasonCode='SELECTED_INPUT_ABSENT'end
 end
 return out
end

end)()
local A={}
local activeInstance
function A.compareCurrentEpoch()return assert(activeInstance,'No owned classified epoch').compare()end
function A.observe()return assert(activeInstance,'No owned classifier').candidates()end
function A.diagnoseObserved()return assert(activeInstance,'No owned classifier').diagnoseObserved()end
function A.compareObserved(closed)return assert(activeInstance).compareObserved(closed)end
function A.resampleClosed()return assert(activeInstance,'No owned classifier').sample()end
function A.preLearningReady()return assert(activeInstance,'No classifier adapter').ready()end
function A.proposeRenewal()return assert(activeInstance).proposeRenewal()end
function A.acceptRenewal(p,ack)return assert(activeInstance).acceptRenewal(p,ack)end
function A.new(P,fs,j,read,now,run,record)
 local O=assert(P.classifierOwner);local base=assert(O.base);local hash=assert(O.configSha256)
 assert(base:match('^/root/router%-project/classifier/nss23%-[%w%-]+$')and hash:match('^[0-9a-f]+$')and #hash==64)
 local generation=base:match('/([^/]+)$');local ram='/tmp/router-project-game-classifier'
 local function stable(path,cap)
  local a=assert(fs.lstat(path));assert(a.type=='reg'and a.uid==0 and a.gid==0 and a.nlink==1)
  local body=read(path,cap);local b=assert(fs.lstat(path))
  assert(a.dev==b.dev and a.ino==b.ino,'Classifier publication changed during read');return body
 end
 assert(read('/root/router-project/game-classifier-generation',512)==base..' '..hash..'\n')
 assert(run('/usr/bin/sha256sum '..base..'/config.json'):match('^(%x+) ')==hash)
 local cfg=assert(j.parse(stable(base..'/config.json',131072)))
 assert(cfg.generation==generation and cfg.files['worker.lua']==O.workerSha256)
 assert(cfg.nssPublication=='classification.json','Early publication channel not qualified')
 record.adapterUsesLongRunningOwner=true;record.adapterPrivateObserverSpawned=false
 local sourceDiagnostic
 local function readContext()
  assert(read('/proc/sys/kernel/random/boot_id',128):gsub('%s+$','')==P.boot)
  assert(stable(ram..'/owner',256)==generation..' '..P.boot..'\n')
  local s=assert(j.parse(stable(ram..'/classification.json',4194304)));local g=assert(j.parse(stable(ram..'/guardian.json',4194304)))
  local p=type(s)=='table'and type(s.snapshot)=='table'and s.snapshot.provenance
  if type(p)=='table'then
   sourceDiagnostic={}
   for _,k in ipairs({'sequence','startedAtUptime','finishedAtUptime'})do
    local v=p[k];if type(v)=='number'and v==v and math.abs(v)<1e16 then sourceDiagnostic[k]=v end
   end
   if type(s.atUptime)=='number'and s.atUptime==s.atUptime and math.abs(s.atUptime)<1e16 then sourceDiagnostic.publishedAtUptime=s.atUptime end
  end
  assert(s.publication=='before-software-baseline','Wrong classifier publication stage')
  local text=read('/proc/'..s.pid..'/stat',8192);local fields={};for v in assert(text:match('^%d+ %b() (.*)$')):gmatch('%S+')do fields[#fields+1]=v end
  local c={base=base,generation=generation,configSha256=hash,boot=P.boot,pid=s.pid,start=fields[20],alive=fields[1]~='Z',workerArgv=read('/proc/'..s.pid..'/cmdline',8192),stopped=fs.lstat(ram..'/stopped')~=nil,guardianHealthy=g.healthy==true and g.generation==generation and g.boot==P.boot and g.configSha256==hash and now()-g.atUptime<6,authorizedClient='192.168.237.207'}
  c.sourceCommand=table.concat({cfg.source.groupRunnerPath,'1',cfg.source.conntrackPath,'-L','-f','ipv4','--zone','0','-s',cfg.source.authorizedClient,'-o','extended,id'},' ')
  return s,c
 end
 local function current()
  local s,c=readContext();Consumer.inspect(s,c,now());return s,c
 end
 local epoch
 local out={}
 function out.candidates()
  local s,c=readContext();local checked=Consumer.inspect(s,c,now())
  out.lastObservedSnapshot=s;out.lastObservedContext=c
  return{flows=checked.candidates,producer=checked.producer,sourceSequence=checked.provenance.sequence,startedAtUptime=checked.provenance.startedAtUptime,finishedAtUptime=checked.provenance.finishedAtUptime,atUptime=now(),nssAdmissionAllowed=false}
 end
 local function completeFacts(x)
  local facts=describeSelection(x,P.selected,now());facts.sameSourceCompleteFrame=true;facts.afterRejectionOnly=true;facts.producer=x.producer;facts.provenance=x.snapshot.provenance;facts.authenticatedSelectedFlows={}
  for _,f in ipairs(x.snapshot.flows)do for _,w in pairs(P.selected)do if f.key==w.classifierKey then facts.authenticatedSelectedFlows[#facts.authenticatedSelectedFlows+1]=f end end end
  assert(#facts.authenticatedSelectedFlows==2,'Complete evidence lacks exact pair');return facts
 end
 local function diagnose(probeSnapshot,probeContext,done,target)
  if probeSnapshot then
   local diagnosed,detail=pcall(describeSelection,probeSnapshot,P.selected,done)
   target.selected=diagnosed and detail or{diagnosticOnly=true,nssAdmissionAllowed=false,diagnosticError=tostring(detail)}
   if diagnosed and detail.admissionProjectionOnly and(not detail.slots.tcp.present or not detail.slots.udp.present)then
    local matched,full=pcall(function()
     local x=assert(j.parse(stable(ram..'/snapshot.json',4194304)))
     for _,k in ipairs({'producer','generation','boot','configSha256','pid','start'})do assert(x[k]==probeSnapshot[k],'Complete diagnostic producer differs')end
     local a=assert(x.snapshot.provenance);local b=assert(probeSnapshot.snapshot.provenance)
     for _,k in ipairs({'sequence','startedAtUptime','finishedAtUptime','method','command','boot','rawStatus','exitCode','queryFamily','queryZone','authorizedClient'})do assert(a[k]==b[k],'Complete diagnostic source differs')end
     assert(not x.snapshot.admissionProjection,'Expected complete diagnostic input')
     Consumer.inspect(x,probeContext,now())
     return completeFacts(x)
    end)
    if matched then target.completeSelected=full
    else target.completeSelectionUnavailable=tostring(full)end
   end
  end
 end
 function out.ready()
  sourceDiagnostic=nil;local began=now()
  local probeSnapshot,probeContext
  local ok,result=pcall(function()local s,c=readContext();probeSnapshot=s;probeContext=c;local e=Consumer.pair(s,c,now(),P.selected);return true end)
  local done=now();record.lastAdmissionProbe={startedAtUptime=began,checkedAtUptime=done,checkSeconds=done-began,diagnosticOnly=true,source=sourceDiagnostic}
  if sourceDiagnostic and sourceDiagnostic.startedAtUptime then record.lastAdmissionProbe.sourceAge=done-sourceDiagnostic.startedAtUptime end
  if not ok then diagnose(probeSnapshot,probeContext,done,record.lastAdmissionProbe)end
  if ok then return result==true,nil,false end
  local reason=tostring(result)
  local retry=reason:match(': Pre%-learning time margin insufficient$')or reason:match(': Per%-flow pre%-learning time margin insufficient$')or reason:match(': Fresh epoch lacks tag setup reserve$')
  return false,reason,retry~=nil
 end
 function out.sample()
  assert(now()<record.deadline-6)
  local s,c=current();local nextEpoch=Consumer.pair(s,c,now(),P.selected);epoch=nextEpoch
  local chosen={};for _,d in ipairs(nextEpoch.decisions)do
   for _,f in ipairs(s.snapshot.flows)do if f.key==d.classifierKey then chosen[#chosen+1]=f end end
  end
  assert(#chosen==2);record.adapterProducer=s.producer;record.adapterSourceSequence=s.snapshot.provenance.sequence
  return{flows=chosen,selection=s.snapshot.selection,provenance=s.snapshot.provenance}
 end

 local pending
 function out.proposeRenewal()
  assert(epoch and not pending,'Renewal already pending or no epoch')
  local s,c=current()
  local comparison=Consumer.compareEpoch(epoch,s,c,now())
  assert(comparison.action=='KEEP_IMMUTABLE_EPOCH','Retire before renewing changed class/identity/owner')
  if s.snapshot.provenance.sequence==epoch.sourceSequence then return nil end
  assert(s.snapshot.provenance.sequence>epoch.sourceSequence,'Source sequence regressed')
  local nextEpoch=Consumer.pair(s,c,now(),P.selected)
  assert(nextEpoch.producer==epoch.producer and nextEpoch.epochUntil>epoch.epochUntil)
  assert(now()<epoch.epochUntil-0.5,'Too late to renew')
  pending={expectedSequence=epoch.sourceSequence,nextSequence=nextEpoch.sourceSequence,untilMs=math.floor(nextEpoch.epochUntil*1000),epoch=nextEpoch,nssAdmissionAllowed=false}
  return pending
 end
 function out.acceptRenewal(proposal,ack)
  assert(pending==proposal and ack.sequence==proposal.nextSequence and ack.classifierUntilMs==proposal.untilMs,'Kernel did not confirm this exact proposal')
  local s,c=current()
  assert(Consumer.compareEpoch(proposal.epoch,s,c,now()).action=='KEEP_IMMUTABLE_EPOCH','Publication changed during kernel update; retire exact pair')
  epoch=proposal.epoch;pending=nil
  record.adapterRenewals=(record.adapterRenewals or 0)+1
  record.adapterSourceSequence=epoch.sourceSequence
  return{sourceSequence=epoch.sourceSequence,epochUntil=epoch.epochUntil,producer=epoch.producer,nssAdmissionAllowed=false}
 end
 function out.diagnoseObserved()
  local facts={diagnosticOnly=true,nssAdmissionAllowed=false};diagnose(out.lastObservedSnapshot,out.lastObservedContext,now(),facts);record.rejectedObservation=facts
 end
 local function completeCurrent(probe,context)
  local began=now();local due=math.min(began+0.65,epoch.epochUntil-0.5);local x;local reads=0
  repeat
   x=assert(j.parse(stable(ram..'/snapshot.json',4194304)));reads=reads+1
   for _,k in ipairs({'producer','generation','boot','configSha256','pid','start'})do assert(x[k]==probe[k],'Complete producer differs')end
   if x.snapshot.provenance.sequence>=probe.snapshot.provenance.sequence then break end
   assert(reads<15 and now()<due,'Complete query lag exceeded original lease window');require('nixio').nanosleep(0,math.floor(math.min(0.05,due-now())*1000000000))
  until false
  assert(not x.snapshot.admissionProjection,'Complete source required');Consumer.inspect(x,context,now())
  local result=Consumer.compareEpoch(epoch,x,context,now(),false);assert(result.action~='KEEP_IMMUTABLE_EPOCH','Full query no longer supports retirement')
  local facts=completeFacts(x);facts.comparisonMadeFromThisCompleteQuery=true;facts.projectionRejectionSequence=probe.snapshot.provenance.sequence;facts.completeReadCount=reads;facts.completeWaitSeconds=now()-began
  result.evidence={diagnosticOnly=true,nssAdmissionAllowed=false,completeSelected=facts};return result
 end
 function out.compareObserved(closed)
  local s,c=assert(out.lastObservedSnapshot),assert(out.lastObservedContext)
  local result=Consumer.compareEpoch(assert(epoch),s,c,now(),closed)
  if result.action~='KEEP_IMMUTABLE_EPOCH'then
   result.evidence={diagnosticOnly=true,nssAdmissionAllowed=false}
   if not closed then local ok,full=pcall(completeCurrent,s,c);if ok then return full end;result.evidence.completeSelectionUnavailable=tostring(full)
   else diagnose(s,c,now(),result.evidence)end
  end
  return result
 end
 function out.compare()
  assert(epoch,'No immutable classified epoch')
  local ok,s,c=pcall(current)
  if not ok then return{action='RETIRE_EXACT_SELECTED_SLOTS',affected={'tcp','udp'},reason=tostring(s),nssAdmissionAllowed=false,clearConntrack=false}end
  return Consumer.compareEpoch(epoch,s,c,now())
 end
 return out
end
return setmetatable(A,{__call=function(_,P,fs,j,read,now,run,record)
 local instance=A.new(P,fs,j,read,now,run,record)
 activeInstance=instance;record.adapterRetirementComparatorAvailable=true
 return instance.sample
end})
