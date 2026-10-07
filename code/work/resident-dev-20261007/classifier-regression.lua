local Old=assert(loadfile(arg[1]))()
local New=assert(loadfile(arg[2]))()
local Source=assert(loadfile(arg[3]))()
local P=assert(loadfile(arg[4]))()
package.preload['luci.jsonc']=function()
 return{parse=function(s)
  assert(s=='fixture-addresses')
  local out={};for wan=1,5 do out[#out+1]={ifname='rpwan'..wan,addr_info={{family='inet',scope='global',['local']='198.51.100.'..wan}}}end
  return out
 end}
end
package.preload['nixio']=function()return{}end

local tests={}
local function test(name,fn)fn();tests[#tests+1]=name;print('PASS '..name)end
local function check(v,message)assert(v,message)end
local function harness(factory,protocol)
 local h={now=100,protocol=protocol or'tcp',wan=2,mark=131072,id=11,port=51000,
  c={upBytes=10000,downBytes=150000,upPackets=100,downPackets=100},empty=false}
 local boot='fixture-boot'
 local observer={version=1,authorizedClient='192.168.237.0/24',conntrackPath='/usr/sbin/conntrack',
  groupRunnerPath='/root/router-project/classifier/nss23-fixture/group-runner',queryTimeoutSeconds=1,
  maxQueryAgeSeconds=2,maxSourceBytes=524288,maxSourceRows=2048}
 local function row()
  local proto=h.protocol=='tcp'and'tcp 6 120 ESTABLISHED'or'udp 17 120'
  return'ipv4 2 '..proto..' src=192.168.237.207 dst=192.0.2.9 sport='..h.port..' dport=45817 packets='..h.c.upPackets..' bytes='..h.c.upBytes..
   ' src=192.0.2.9 dst=198.51.100.'..h.wan..' sport=45817 dport='..h.port..' packets='..h.c.downPackets..' bytes='..h.c.downBytes..
   ' [ASSURED] mark='..h.mark..' use=1 id='..h.id..' zone=0\n'
 end
 local runtime={boot=function()return boot end,now=function()return h.now end,
  query=function(command,limit)
   assert(command==table.concat(Source.argv(observer),' '));assert(limit==524288)
   if h.queryError then return{rawStatus=256,stdout='',stderr='fixture query failed'}end
   local text=h.empty and''or(h.overrideRow or row())
   return{rawStatus=0,stdout=text,stderr='conntrack v1.4.8 (conntrack-tools): '..(h.empty and 0 or 1)..' flow entries have been shown.\n'}
  end}
 h.step=factory({observer=observer,boot=boot},P.policy,
  function(p)assert(p=='/proc/sys/net/netfilter/nf_conntrack_acct');return'1\n'end,
  function(command)assert(command=='ip -j -4 address show');return'fixture-addresses'end,Source,runtime)
 function h:sample(delta,dt)
  self.now=self.now+(dt or 3)
  for key,value in pairs(delta or{})do self.c[key]=self.c[key]+value end
  local s=self.step();return s.flows[1],s
 end
 return h
end
local high={upPackets=1000,downPackets=1000,upBytes=52000,downBytes=1500000}
local small={upPackets=60,downPackets=60,upBytes=9360,downBytes=9360}
local function learned(factory)
 local h=harness(factory);check(h:sample().decision.class=='UNKNOWN','cold flow admitted')
 check(h:sample(high).decision.class=='BULK','high rate failed to learn BULK');return h
end
for _,case in ipairs(P.cases)do
 test('captured '..case.label..' reproduces old BE and corrects active BULK',function()
  local a,b=learned(Old),learned(New)
  local before=a:sample(case.increments,case.dt);local after=b:sample(case.increments,case.dt)
  check(before.decision.class=='BE'and before.decision.reason=='cooldown','original refusal not reproduced')
  check(math.abs(before.decision.rateKbps-case.originalRateKbps)<0.00001,'captured byte-rate changed')
  check(math.abs(before.decision.pps-case.originalPps)<0.00001,'captured packet-rate changed')
  check(after.decision.class=='BULK'and after.decision.reason=='bulk'and after.bulkRT.bulk,'active download misclassified')
  check(after.decision.rateKbps==before.decision.rateKbps and after.decision.pps==before.decision.pps,'measured rates rewritten')
  check(not after.decision.budgetAdmitted and not after.bulkRT.rt,'download admitted as realtime')
  check(after.validUntilUptime==before.validUntilUptime,'source TTL extended')
 end)
end
test('sustained shaped large-packet TCP stays BULK for 90 seconds',function()
 local h=learned(New)
 for n=1,30 do local f=h:sample({upPackets=150,downPackets=150,upBytes=7800,downBytes=225000})
  check(f.decision.class=='BULK'and f.decision.rateKbps<2000,'shaped transfer lost BULK')
 end
end)
test('stopping a learned download immediately leaves BULK',function()
 local h=learned(New);h:sample(P.cases[1].increments,P.cases[1].dt)
 local f=h:sample();check(f.decision.class=='BE'and f.decision.reason=='cooldown'and not f.bulkRT.bulk,'idle BULK retained')
end)
test('current small-packet activity retires learned BULK without granting RT',function()
 local h=learned(New);local f=h:sample(small)
 check(f.decision.class=='BE'and not f.decision.budgetAdmitted,'small-packet class forced')
end)
test('one-way large-packet sample cannot preserve learned BULK',function()
 local h=learned(New);local f=h:sample({downPackets=150,downBytes=225000})
 check(f.decision.class=='BE','one-way transfer qualified')
end)
test('fewer than six downstream packets cannot preserve learned BULK',function()
 local h=learned(New);local f=h:sample({upPackets=1,downPackets=5,upBytes=52,downBytes=7500})
 check(f.decision.class=='BE','insufficient packet evidence qualified')
end)
test('existing 900-byte threshold remains strict',function()
 for _,size in ipairs({899,900})do local h=learned(New);local f=h:sample({upPackets=6,downPackets=6,upBytes=312,downBytes=6*size})
  check(f.decision.class=='BE','packet-size boundary relaxed')
 end
 local h=learned(New);check(h:sample({upPackets=6,downPackets=6,upBytes=312,downBytes=5406}).decision.class=='BULK','qualified large packets lost')
end)
test('large upstream payload is not mistaken for a download ACK',function()
 local h=learned(New);local f=h:sample({upPackets=6,downPackets=6,upBytes=9006,downBytes=9006})
 check(f.decision.class=='BE','bidirectional large payload accidentally qualified')
end)
test('cold low-rate large TCP stays unqualified',function()
 local h=harness(New);h:sample();local f=h:sample(P.cases[1].increments,P.cases[1].dt)
 check(f.decision.class=='BE'and f.decision.reason=='large-packets'and not f.bulkRT.bulk,'cold low-rate flow promoted')
end)
test('the original 30-second learned-BULK bound is retained',function()
 local h=learned(New);local f=h:sample({upPackets=6,downPackets=6,upBytes=312,downBytes=9000},30)
 check(f.decision.class=='BE'and f.decision.reason=='large-packets','expired BULK history reused')
end)
test('the original six-second evidence interval is retained',function()
 local h=learned(New);local f=h:sample({upPackets=6,downPackets=6,upBytes=312,downBytes=9000},6.01)
 check(f.decision.class=='BE','stale interval qualified')
end)
for _,field in ipairs({'id','port','mark','wan'})do
 test('changed '..field..' cannot inherit BULK identity',function()
  local h=learned(New);h[field]=h[field]+1
  if field=='wan'then h.mark=h.wan*65536 end
  local f=h:sample(P.cases[1].increments,P.cases[1].dt)
  check(f.decision.class=='UNKNOWN','changed identity inherited BULK')
 end)
end
test('counter reset invalidates learned BULK and cooldown history',function()
 local h=learned(New);h.c={upPackets=1,downPackets=1,upBytes=52,downBytes=1500}
 local f=h:sample();check(f.decision.class=='UNKNOWN'and f.decision.blockedUntil==0,'reset inherited eligibility')
end)
test('missing CT and reappearance require fresh learning',function()
 local h=learned(New);h.empty=true;local f=h:sample();check(f==nil,'missing CT retained')
 h.empty=false;check(h:sample(P.cases[1].increments).decision.class=='UNKNOWN','reappeared CT inherited state')
end)
test('discarded observation never carries active class into a new sample',function()
 local h=learned(New);h.step('discard-observation-history')
 check(h:sample(P.cases[1].increments).decision.class=='UNKNOWN','discarded observation retained active class')
end)
test('new worker never imports learned class',function()
 learned(New);local h=harness(New);check(h:sample(P.cases[1].increments).decision.class=='UNKNOWN','restart imported BULK')
end)
test('query errors do not produce candidate snapshots',function()
 local h=learned(New);h.queryError=true;local ok=pcall(function()h:sample(high)end)
 check(not ok,'failed CT query admitted')
end)
test('UDP RT warmup, admission, budget and counters stay identical',function()
 local a,b=harness(Old,'udp'),harness(New,'udp')
 for n=1,35 do
  local delta=n==1 and{}or small
  local x,y=a:sample(delta),b:sample(delta)
  for k,v in pairs(x.decision)do check(v==y.decision[k],'UDP decision changed: '..k)end
  check(x.decision.class==y.decision.class and x.validUntilUptime==y.validUntilUptime,'UDP TTL/admission changed')
  if n>=3 then check(y.decision.class=='RT'and y.decision.budgetAdmitted,'UDP RT lost')end
 end
end)
test('over-rate UDP remains BULK then cooldown, without TCP shape exception',function()
 local a,b=harness(Old,'udp'),harness(New,'udp');a:sample();b:sample();a:sample(high);b:sample(high)
 local x,y=a:sample(P.cases[1].increments),b:sample(P.cases[1].increments)
 check(x.decision.class=='BE'and y.decision.class=='BE'and x.decision.reason==y.decision.reason,'UDP classification relaxed')
end)
test('above-ceiling TCP rate still classifies BULK without prior history',function()
 local h=harness(New);h:sample();local f=h:sample(high)
 check(f.decision.class=='BULK'and f.decision.rateKbps>2000,'original rate test changed')
end)
print('RESULT checks='..#tests..' passed=true routerAccess=false actualLua51=true')
