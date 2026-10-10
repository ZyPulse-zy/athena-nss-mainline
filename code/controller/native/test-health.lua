-- Pure reducers only; no router state or traffic required.
local root=assert(arg[0]:match('^(.*)/[^/]+$'));local m=dofile(root..'/health.lua');local checks=0
local function sample(at,fresh,flows,queues)return{atUptime=at,sourceFresh=fresh,flows=flows or{},queues=queues or{},readSeconds=0.01,actualNss=0,gateNowMs=at*1000}end
local function flow(packets,serial,generation,untilMs)return{key='private-full-identity',class='RT',budgetAdmitted=true,replyPackets=packets,owned=true,identityMatches=true,state=1,createAck=1,createPending=0,receiptPresent=1,receiptState=0,untilMs=untilMs or 110000,serial=serial or 5,generation=generation or 9}end
local function check(ok)assert(ok);checks=checks+1 end
local i={key='one',connectionId=12,mark=65536,protocol=17,class='RT',
 original={src='192.0.2.1',sport=2000,dst='198.51.100.1',dport=3000},
 reply={src='198.51.100.1',sport=3000,dst='203.0.113.1',dport=4000}}
local owner={};for k,v in pairs(i)do owner[k]=v end
check(m.identity(i,owner,{id=12}));check(not m.identity(i,owner,{id=13}))
owner.reply={src='198.51.100.1',sport=3000,dst='203.0.113.1',dport=4001};check(not m.identity(i,owner,{id=12}))
local queues=m.queues('qdisc nsshtb 7a00: root\n Sent 0 bytes 0 pkt (dropped 4, overlimits 0)\nqdisc nssfq_codel 7a16: parent 7a00:16\n Sent 4 bytes 2 pkt (dropped 1, overlimits 0)\nqdisc nssfq_codel 7a15: parent 7a00:15\n Sent 4 bytes 2 pkt (dropped 100, overlimits 0)\nqdisc nssfq_codel 7a26: parent 7a00:26\n Sent 4 bytes 2 pkt (dropped 2, overlimits 0)','athenaigs')
check(#queues==2 and queues[1].drops==1 and queues[2].drops==2)
local s=m.new();m.tick(s,sample(100,true));m.tick(s,sample(101,true));check(s.rtNotCreatedSamples==0 and #s.events==0)
m.tick(s,sample(102,true,{flow(1)}));m.tick(s,sample(103,true,{flow(2)}));check(s.rtCreatedSamples==1 and s.rtNotCreatedSamples==0)
m.tick(s,sample(104,true,{flow(3,6,10)}));check(s.rtRebindings==1 and s.events[1].kind=='active-rt-binding-changed')
local bad=flow(4);bad.identityMatches=false;m.tick(s,sample(105,true,{bad}));check(s.rtNotCreatedSamples==1)
local pending=flow(5);pending.createPending=1;m.tick(s,sample(106,true,{pending}));check(s.rtNotCreatedSamples==2)
m.tick(s,sample(107,false,{flow(6)}));check(s.sourceGaps==1)
m.tick(s,sample(108,false,{flow(7,5,9,108000)}));check(s.events[#s.events].kind=='active-rt-during-source-gap')
m.tick(s,sample(109,true,{flow(8,5,9,108000)}));check(s.sourceRestores==1 and s.events[#s.events].kind=='active-rt-without-current-create')
-- No traffic progression means no binding warning; flow departure is ordinary.
local count=s.rtRebindings;m.tick(s,sample(110,true,{flow(8,20,30,120000)}));check(s.rtRebindings==count)
m.tick(s,sample(111,true,{}));m.tick(s,sample(112,true,{flow(20,30,40,120000)}));check(s.rtRebindings==count)
m.tick(s,sample(113,true,{},{{key='wan/RT',class='RT',drops=100}}));m.tick(s,sample(114,true,{},{{key='wan/RT',class='RT',drops=103}}));check(s.rtQueueDropDelta==3)
m.tick(s,sample(115,true,{},{{key='wan/RT',class='RT',drops=1}}));check(s.counterResets==1 and s.rtQueueDropDelta==3)
m.tick(s,sample(116,true,{},{}));check(s.rtQueueDropDelta==3)
local report=m.report(s);check(report.endToEndLossMeasured==false and report.readOnly and not report.generatedTraffic)
local text=require('luci.jsonc').stringify(report);check(not text:find('private-full-identity',1,true))
for t=117,260 do local row=sample(t,true);row.unconfirmed=1;m.tick(s,row)end;check(#s.events==128 and s.eventsOmitted>0)
local tags={up={{RT=0x7e16,BE=0x7e15}},down={{RT=0x7a16,BE=0x7a15}}}
local f=flow(1);f.wan=1;f.qosObserved=1;f.igsObserved=1;f.qosDirection=1
f.flowQos=0x7e160006;f.returnQos=0x7a160006;f.igsFlow=0;f.igsReturn=0x7a16
check(m.labels(f,tags,true).status=='verified')
f.qosDirection=2;f.flowQos,f.returnQos=f.returnQos,f.flowQos;f.igsFlow,f.igsReturn=f.igsReturn,f.igsFlow
check(m.labels(f,tags,true).status=='verified')
f.returnQos=0x7e260006;check(m.labels(f,tags,true).status=='mismatch')
f.qosDirection=nil;check(m.labels(f,tags,true).status=='direction-unverified')
f.qosDirection=1;f.igsObserved=nil;check(m.labels(f,tags,true).status=='unobserved')
check(m.labels(f,tags,false).status=='not-created')
local h=m.hardware('ipv4_rx_byts = 9000 common\nipv4_rx_bytes = 100 special\nipv4_tx_bytes = 110 special')
check(h.rx==100 and h.tx==110);check(not m.hardware('ipv4_rx_byts = 9000 common'))
local a=m.new();local row=sample(100,true,{flow(1)});row.hardware=h;m.tick(a,row)
row=sample(101,true,{flow(2)});row.hardware={rx=130,tx=150};m.tick(a,row)
check(a.hardwareDelta.rx==30 and a.hardwareDelta.tx==40 and m.report(a).hardware.measured)
row=sample(102,true);m.tick(a,row);row=sample(103,true);row.hardware={rx=200,tx=250};m.tick(a,row)
check(a.hardwareDelta.rx==30 and a.hardwareIntervals==1,'Missing read must break byte window')
row=sample(104,true);row.hardware={rx=1,tx=1};m.tick(a,row);check(a.hardwareResets==1 and a.hardwareDelta.rx==30)
check(not m.coverage({hardwareBytes=100,totalBytes=110}).measured)
check(m.coverage({sameCohort=true,sameWindow=true,sameDirection=true,sameByteBasis=true,hardwareBytes=100,totalBytes=200}).ratio==0.5)
check(not m.coverage({sameCohort=true,sameWindow=true,sameDirection=true,sameByteBasis=true,hardwareBytes=201,totalBytes=200}).measured)
local gone=flow(3);gone.receiptState=2;row=sample(105,true,{gone});m.tick(a,row)
check(not m.report(a).flowEvidence[1].createAcknowledged and not m.report(a).byteCoverage.measured)
local hw=flow(1);hw.qosDirection=1;hw.policyApplied=1;hw.policyGeneration=hw.generation;hw.syncSamples=1
hw.hardwareFlowRxBytes=100;hw.hardwareReturnRxBytes=200;hw.lastSyncMs=100000
local x=m.flowHardware(hw,nil,true,101000);check(x.measured and x.up==100 and x.down==200 and x.fresh)
check(not m.flowHardware(hw,nil,false,101000).measured)
hw.policyGeneration=hw.generation+1;check(not m.flowHardware(hw,nil,true,101000).measured);hw.policyGeneration=hw.generation
local prev={serial=hw.serial,generation=hw.generation,up=40,down=50,samples=1}
x=m.flowHardware(hw,prev,true,107000);check(x.delta.up==60 and x.delta.down==150 and not x.fresh)
prev.generation=8;check(not m.flowHardware(hw,prev,true,101000).delta)
hw.qosDirection=2;x=m.flowHardware(hw,nil,true,101000);check(x.up==200 and x.down==100)
print(require('luci.jsonc').stringify({passed=true,checks=checks,dataPlaneWrites=false,modelOnly=true}))
