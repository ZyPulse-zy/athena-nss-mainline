-- Read-only, bounded capture. No full classifier snapshot or per-station dump.
local root=assert(arg[0]:match('^(.*)/[^/]+$'))
local seconds=tonumber(arg[1]or'60');assert(seconds and seconds%1==0 and seconds>=1 and seconds<=180,'Duration must be 1..180 seconds')
local queryQueues,queryCoverage=false,false
for i=2,3 do local option=arg[i]or'';assert(option==''or option=='--queues' or option=='--coverage','Unknown diagnostic option')
 queryQueues=queryQueues or option=='--queues';queryCoverage=queryCoverage or option=='--coverage'end
local j=require('luci.jsonc');local n=require('nixio');local health=dofile(root..'/health.lua')
local coverage=queryCoverage and dofile(root..'/coverage.lua');local coverageState=coverage and coverage.new()
local core=coverage and dofile(root..'/core.lua')
local function read(p,cap)
 local f=io.open(p);if not f then return nil end;local s=f:read((cap or 4194304)+1)or'';f:close()
 assert(#s<=(cap or 4194304),'Observation exceeds read bound');return s
end
local function json(p)return j.parse(read(p)or'')or{}end
local function now()return tonumber(assert(read('/proc/uptime',128)):match('^[%d.]+'))end
local function run(c)
 -- This timeout only owns its read-only tc child. Never kill a service/writer.
 local f=assert(io.popen('/usr/bin/timeout -k 1 2 '..c..' 2>/dev/null; printf "\nATHENA_READ_EXIT_%s\n" "$?"'))
 local text=f:read(262145)or'';f:close();assert(#text<=262144,'Queue statistics exceed read bound')
 local body,code=text:match('^(.*)\nATHENA_READ_EXIT_(%d+)\n$');return code=='0'and body or nil
end
local function collect()
 local at=now();local s=json('/tmp/athena-dorm-native/status.json');local d=json('/tmp/athena-dorm-native/desired.json')
 local p=json('/tmp/router-project-game-classifier/classification.json');local gate=read('/sys/kernel/debug/athena_ecm_gate/status',65536)or''
 local slots={};for line in gate:gmatch('[^\n]+')do local e={};for k,v in line:gmatch('([%w_]+)=(%d+)')do e[k]=tonumber(v)end
  if e.slot then slots[e.slot]=e elseif e.telemetry_slot and slots[e.telemetry_slot] then for k,v in pairs(e)do slots[e.telemetry_slot][k]=v end end end
 local owned={};for _,v in ipairs(s.ownedFlows or{})do owned[v.key]=v end
 local flows={};for _,f in ipairs(d.flows or{})do
  local a=owned[f.key];local g=a and slots[a.slot]or{}
  flows[#flows+1]={key=f.key,class=f.class,budgetAdmitted=f.budgetAdmitted,replyPackets=f.reply and f.reply.packets,owned=a~=nil,
   identityMatches=health.identity(f,a,g),
   state=g.state,createAck=g.create_ack,createPending=g.create_pending,untilMs=g.until_ms,serial=g.serial,generation=g.generation,
   receiptPresent=g.receipt_present,receiptState=g.receipt,qosObserved=g.qos_observed,igsObserved=g.igs_observed,qosDirection=g.qos_direction,
   flowQos=g.flow_qos,returnQos=g.return_qos,igsFlow=g.igs_flow,igsReturn=g.igs_return,wan=f.wan,egress=f.egress,wireless=f.wireless,
   policyApplied=g.policy_applied,policyGeneration=g.policy_generation,incomingFlowQos=g.incoming_flow_qos,incomingReturnQos=g.incoming_return_qos,
   hardwareFlowRxBytes=g.hardware_flow_rx_bytes,hardwareReturnRxBytes=g.hardware_return_rx_bytes,syncSamples=g.sync_samples,lastSyncMs=g.last_sync_ms}
 end
 local hardwareAt=now();local cohort
 if coverage then cohort=coverage.cohort(json('/tmp/router-project-game-classifier/snapshot.json'),s.wans,now(),core)end
 local queues={};local queueReads=0
 if queryQueues and gate:match('^abi=2 capacity=32 ')then
  for _,dev in ipairs{'wan','athenaigs'}do
   local text=run('/root/router-project/experiments/nss8-htb2-20261001/tc-nss -s -d qdisc show dev '..dev)
   if text then local rows=health.queues(text,dev);if #rows==5 then queueReads=queueReads+1 end
    for _,q in ipairs(rows)do queues[#queues+1]=q end
   end
  end
 end
 local started=p.snapshot and p.snapshot.provenance and p.snapshot.provenance.startedAtUptime
 local fresh=d.summary and d.summary.sourceFresh==true and p.status=='running'and type(started)=='number'and started<=at and at-started<6
 return{atUptime=at,phase=s.phase,sourceFresh=fresh==true,actualNss=tonumber(read('/sys/kernel/debug/ecm/ecm_nss_ipv4/accelerated_count',128)),
  unconfirmed=s.native and s.native.unconfirmed,gateNowMs=tonumber(gate:match('now_ms=(%d+)')),flows=flows,queues=queues,
  tags={up=s.ingress and s.ingress.up and s.ingress.up.tags,down=s.ingress and s.ingress.down and s.ingress.down.tags},
  hardware=health.hardware(read('/sys/kernel/debug/qca-nss-drv/stats/ipv4',65536)or''),
  reader=s.flowState and s.flowState.reader,budgetUpdates=s.flowState and s.flowState.budgetUpdates,
  cohort=cohort,hardwareAt=hardwareAt,queueReads=queueReads,readSeconds=now()-at}
end
local state=health.new();local start=now();local queueReadFailures=0;local last
repeat
 last=collect();health.tick(state,last);if queryQueues and last.queueReads~=2 then queueReadFailures=queueReadFailures+1 end
 if coverage then
  local hardware={};for _,f in ipairs(last.flows)do
   local h=state.flowHardware[f.key];if h then hardware[f.key]=h end
  end
  coverage.tick(coverageState,last.hardwareAt,last.cohort,hardware)
 end
 local remaining=start+seconds-now();if remaining<=0 then break end
 local wait=math.min(3,remaining);n.nanosleep(math.floor(wait),math.floor((wait%1)*1000000000))
until false
local report=health.report(state);report.lastPhase=last.phase
report.byteCoverageRequested=queryCoverage;if coverage then report.byteCoverage=coverage.report(coverageState)end
report.queueStatisticsRequested=queryQueues;report.rtQueueDropsMeasured=queryQueues and queueReadFailures==0
if queryQueues then report.queueReadIncompleteSamples=queueReadFailures end
if not report.rtQueueDropsMeasured then report.rtQueueDropDelta=nil end
report.requestedSeconds=seconds;report.scopeNotice='Includes non-game RT flows. Hardware tc queries require explicit --queues; missing or unrequested queue counters do not prove zero drops.'
report.reader=last.reader;report.budgetUpdates=last.budgetUpdates
print(j.stringify(report))
