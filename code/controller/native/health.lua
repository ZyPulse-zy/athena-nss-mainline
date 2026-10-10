-- Pure, bounded observation reducer. It cannot change admission or queues.
local M={}
local function number(v)return type(v)=='number'and v==v and v>=0 and v<math.huge end
function M.identity(flow,owned,gate)
 if not owned or not gate or owned.key~=flow.key or owned.connectionId~=flow.connectionId or gate.id~=flow.connectionId or
  owned.mark~=flow.mark or owned.protocol~=flow.protocol or owned.class~=flow.class then return false end
 if owned.bindingToken and gate.binding~=owned.bindingToken then return false end
 if owned.generation and gate.generation~=owned.generation or owned.serial and gate.serial~=owned.serial then return false end
 for _,direction in ipairs{'original','reply'}do
  local a,b=flow[direction],owned[direction];if not a or not b then return false end
  for _,key in ipairs{'src','sport','dst','dport'}do if a[key]~=b[key]then return false end end
 end
 return true
end
function M.labels(f,tags,created)
 local o={status='unobserved',basis='CREATE-payload-and-ACK-not-firmware-queue-readback'}
 if not created then o.status='not-created';return o end
 if f.qosObserved~=1 or f.igsObserved~=1 then return o end
 if f.qosDirection~=1 and f.qosDirection~=2 then o.status='direction-unverified';return o end
 local class=f.class=='RT'and f.budgetAdmitted and'RT'or'BE'
 local up=tags and tags.up and tags.up[f.wan];local down=tags and tags.down and tags.down[f.wan]
 if not up or not down or not up[class]or not down[class]then o.status='expected-tags-unavailable';return o end
 local low=class=='RT'and 6 or 0
 o.expected={up=up[class]*65536+low,down=down[class]*65536+low,igsUp=0,igsDown=down[class]}
 if f.qosDirection==1 then o.observed={up=f.flowQos,down=f.returnQos,igsUp=f.igsFlow,igsDown=f.igsReturn}
 else o.observed={up=f.returnQos,down=f.flowQos,igsUp=f.igsReturn,igsDown=f.igsFlow}end
 o.status='verified'
 for key,value in pairs(o.expected)do if o.observed[key]~=value then o.status='mismatch';break end end
 return o
end
function M.hardware(text)
 local o={}
 for _,direction in ipairs{'rx','tx'}do o[direction]=tonumber(text:match('ipv4_'..direction..'_bytes%s*=%s*(%d+)'))end
 return number(o.rx)and number(o.tx)and o or nil
end
function M.flowHardware(f,old,admitted,atMs)
 local out={measured=false,basis='passive-firmware-RX-sync-same-as-conntrack-accounting'}
 if not admitted or f.policyGeneration~=f.generation or f.policyApplied~=1 or not number(f.syncSamples) or f.syncSamples==0 or
  not number(f.hardwareFlowRxBytes) or not number(f.hardwareReturnRxBytes) or (f.qosDirection~=1 and f.qosDirection~=2) then return out end
 out.measured=true;out.up=f.qosDirection==1 and f.hardwareFlowRxBytes or f.hardwareReturnRxBytes
 out.down=f.qosDirection==1 and f.hardwareReturnRxBytes or f.hardwareFlowRxBytes
 out.lastSyncMs=f.lastSyncMs;out.fresh=number(atMs) and number(f.lastSyncMs) and atMs>=f.lastSyncMs and atMs-f.lastSyncMs<6000
 out.samples=f.syncSamples
 if old and old.serial==f.serial and old.generation==f.generation and old.up<=out.up and old.down<=out.down and old.samples<=out.samples then
  out.delta={up=out.up-old.up,down=out.down-old.down}
 end
 return out
end
function M.coverage(v)
 if not v or v.sameCohort~=true or v.sameWindow~=true or v.sameDirection~=true or v.sameByteBasis~=true or
  not number(v.hardwareBytes)or not number(v.totalBytes)or v.totalBytes==0 or v.hardwareBytes>v.totalBytes then
  return{measured=false,reason='Comparable cohort, window, direction and byte basis required'}
 end
 return{measured=true,ratio=v.hardwareBytes/v.totalBytes,hardwareBytes=v.hardwareBytes,totalBytes=v.totalBytes}
end
function M.queues(text,dev)
 local rows={};local handle
 for line in(text..'\n'):gmatch('([^\n]*)\n')do
  if line:match('^qdisc ')then handle=line:match('^qdisc %S+ (%S+)')end
  local drops=tonumber(line:match('Sent %d+ bytes %d+ pkt %(dropped (%d+)'))
  if handle and handle:match('^7[ae][1-5]6:$')and drops then rows[#rows+1]={key=dev..'/'..handle,class='RT',drops=drops}end
 end
 return rows
end
function M.new()
 return{samples=0,events={},eventsOmitted=0,aliases={},nextAlias=0,previous={},
  minNss=nil,maxNss=nil,sourceGaps=0,sourceRestores=0,rtPacketSamples=0,
  rtCreatedSamples=0,rtNotCreatedSamples=0,rtRebindings=0,queueDrops={},counterResets=0,maxReadSeconds=0,
  evidence={},rtAliases={},flowHardware={},attributedIntervals=0,attributedDelta={up=0,down=0},hardwareDelta={rx=0,tx=0},hardwareIntervals=0,hardwareResets=0,labelVerifiedSamples=0,labelMismatchSamples=0}
end
local function event(state,at,kind,flow)
 if #state.events<128 then state.events[#state.events+1]={atUptime=at,kind=kind,flow=flow}
 else state.eventsOmitted=state.eventsOmitted+1 end
end
function M.tick(state,s)
 assert(number(s.atUptime)and type(s.sourceFresh)=='boolean'and type(s.flows)=='table')
 assert(number(s.readSeconds)and #s.flows<=2048)
 if state.lastAt then assert(s.atUptime>=state.lastAt,'Observation time moved backwards')end
 state.firstAt=state.firstAt or s.atUptime;state.lastAt=s.atUptime;state.samples=state.samples+1
 state.maxReadSeconds=math.max(state.maxReadSeconds,s.readSeconds)
 if number(s.actualNss)then
  state.minNss=math.min(state.minNss or s.actualNss,s.actualNss);state.maxNss=math.max(state.maxNss or s.actualNss,s.actualNss)
 end
 if state.lastFresh~=nil and state.lastFresh~=s.sourceFresh then
  local key=s.sourceFresh and'sourceRestores'or'sourceGaps';state[key]=state[key]+1
  event(state,s.atUptime,s.sourceFresh and'source-restored'or'source-unavailable')
 elseif state.lastFresh==nil and not s.sourceFresh then event(state,s.atUptime,'source-unavailable-at-start')end
 state.lastFresh=s.sourceFresh
 state.evidence={};state.evidenceOmitted=0
 if s.hardware and state.lastHardware then
  if s.hardware.rx>=state.lastHardware.rx and s.hardware.tx>=state.lastHardware.tx then
   state.hardwareDelta.rx=state.hardwareDelta.rx+s.hardware.rx-state.lastHardware.rx
   state.hardwareDelta.tx=state.hardwareDelta.tx+s.hardware.tx-state.lastHardware.tx;state.hardwareIntervals=state.hardwareIntervals+1
  else state.hardwareResets=state.hardwareResets+1 end
 end
 state.lastHardware=s.hardware -- Missing reads break the comparison window.
 if s.unconfirmed and s.unconfirmed>0 then event(state,s.atUptime,'firmware-removal-unconfirmed')end
 local nextPrevious,nextHardware,seen={},{},{}
 for _,f in ipairs(s.flows)do
  assert(type(f.key)=='string'and not seen[f.key]);seen[f.key]=true
  if not state.aliases[f.key]and state.nextAlias<256 then state.nextAlias=state.nextAlias+1;state.aliases[f.key]=state.nextAlias end
  local admitted=f.owned==true and f.identityMatches==true and f.state==1 and number(f.untilMs)and number(s.gateNowMs)and f.untilMs>s.gateNowMs
  local receipt=admitted and f.createAck==1 and f.createPending==0 and f.receiptPresent==1 and f.receiptState==0
  local labels=M.labels(f,s.tags,receipt)
  local hardware=M.flowHardware(f,state.flowHardware[f.key],receipt,s.gateNowMs)
  if hardware.measured then
   nextHardware[f.key]={up=hardware.up,down=hardware.down,samples=hardware.samples,serial=f.serial,generation=f.generation}
   if hardware.delta then state.attributedIntervals=state.attributedIntervals+1
    state.attributedDelta.up=state.attributedDelta.up+hardware.delta.up;state.attributedDelta.down=state.attributedDelta.down+hardware.delta.down end
  end
  if labels.status=='verified'then state.labelVerifiedSamples=state.labelVerifiedSamples+1
  elseif labels.status=='mismatch'then state.labelMismatchSamples=state.labelMismatchSamples+1 end
  if #state.evidence<80 then
   state.evidence[#state.evidence+1]={flow=state.aliases[f.key],class=f.class,wan=f.wan,egress=f.egress,
    wireless=f.wireless,sourceFresh=s.sourceFresh,admitted=admitted==true,leaseRemainingMs=admitted and f.untilMs-s.gateNowMs or nil,
    createAcknowledged=receipt==true,labels=labels,hardwareBytesAttributed=hardware.measured,hardware=hardware,
    policyApplied=f.policyApplied==1,incomingQos={flow=f.incomingFlowQos,returnValue=f.incomingReturnQos}}
  else state.evidenceOmitted=state.evidenceOmitted+1 end
  if f.class=='RT'and f.budgetAdmitted==true then
   if state.aliases[f.key]then state.rtAliases[f.key]=true end
   local old=state.previous[f.key];local progressing=old and number(f.replyPackets)and number(old.replyPackets)and f.replyPackets>old.replyPackets
   local created=receipt
   if progressing then
    state.rtPacketSamples=state.rtPacketSamples+1
    if created then state.rtCreatedSamples=state.rtCreatedSamples+1 else
     state.rtNotCreatedSamples=state.rtNotCreatedSamples+1
     event(state,s.atUptime,s.sourceFresh and'active-rt-without-current-create'or'active-rt-during-source-gap',state.aliases[f.key])
    end
    if old.created and created and(old.serial~=f.serial or old.generation~=f.generation)then
     state.rtRebindings=state.rtRebindings+1;event(state,s.atUptime,'active-rt-binding-changed',state.aliases[f.key])
    end
   end
   nextPrevious[f.key]={replyPackets=f.replyPackets,created=created,serial=f.serial,generation=f.generation}
  end
 end
 state.previous=nextPrevious
 state.flowHardware=nextHardware
 for _,q in ipairs(s.queues or{})do
  assert(type(q.key)=='string'and number(q.drops))
  local old=state.queueDrops[q.key]
  if old~=nil then
   if q.drops<old then state.counterResets=state.counterResets+1;event(state,s.atUptime,'queue-counter-reset')
   elseif q.class=='RT'and q.drops>old then
    state.rtQueueDropDelta=(state.rtQueueDropDelta or 0)+q.drops-old;event(state,s.atUptime,'rt-queue-drop')
   end
  end
  state.queueDrops[q.key]=q.drops
 end
end
function M.report(state)
 local rtAliases=0;for _ in pairs(state.rtAliases)do rtAliases=rtAliases+1 end
 return{readOnly=true,generatedTraffic=false,endToEndLossMeasured=false,
  scope='all-budget-admitted-RT-flows-not-game-exclusive',samples=state.samples,
  sampleSeconds=state.firstAt and state.lastAt-state.firstAt or 0,
  sourceGaps=state.sourceGaps,sourceRestores=state.sourceRestores,
  actualNssMin=state.minNss,actualNssMax=state.maxNss,rtFlowAliases=rtAliases,rtFlowAliasLimit=256,flowAliases=state.nextAlias,
  rtProgressingSamples=state.rtPacketSamples,rtCreatedSamples=state.rtCreatedSamples,
  rtNotCreatedSamples=state.rtNotCreatedSamples,rtBindingChanges=state.rtRebindings,
  rtQueueDropDelta=state.rtQueueDropDelta or 0,counterResets=state.counterResets,
  maxReadSeconds=state.maxReadSeconds,events=state.events,eventsOmitted=state.eventsOmitted,
  flowEvidence=state.evidence,flowEvidenceLimit=80,flowEvidenceOmitted=state.evidenceOmitted,
  evidenceScope='candidate-RT-and-BULK-with-passive-per-flow-firmware-byte-progress',
  labelVerifiedSamples=state.labelVerifiedSamples,labelMismatchSamples=state.labelMismatchSamples,
  hardware={measured=state.hardwareIntervals>0,intervals=state.hardwareIntervals,byteDelta=state.hardwareIntervals>0 and state.hardwareDelta or nil,
   counterResets=state.hardwareResets,scope='global-NSS-IPv4-special-counters',perFlowAttribution=false},
  perFlowHardware={measured=state.attributedIntervals>0,intervals=state.attributedIntervals,byteDelta=state.attributedDelta,basis='firmware-RX-sync'},
  byteCoverage={measured=false,reason='Use --coverage for a bracketed downstream byte baseline including BE'},
  interpretation='No local event does not prove zero loss or jitter. A CREATE receipt is not a per-packet delivery acknowledgement.'}
end
return M
