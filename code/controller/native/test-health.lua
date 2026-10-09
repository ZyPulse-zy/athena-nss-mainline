-- Pure reducers only; no router state or traffic required.
local root=assert(arg[0]:match('^(.*)/[^/]+$'));local m=dofile(root..'/health.lua');local checks=0
local function sample(at,fresh,flows,queues)return{atUptime=at,sourceFresh=fresh,flows=flows or{},queues=queues or{},readSeconds=0.01,actualNss=0,gateNowMs=at*1000}end
local function flow(packets,serial,generation,untilMs)return{key='private-full-identity',class='RT',budgetAdmitted=true,replyPackets=packets,owned=true,identityMatches=true,state=1,createAck=1,createPending=0,untilMs=untilMs or 110000,serial=serial or 5,generation=generation or 9}end
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
print(require('luci.jsonc').stringify({passed=true,checks=checks,dataPlaneWrites=false,modelOnly=true}))
