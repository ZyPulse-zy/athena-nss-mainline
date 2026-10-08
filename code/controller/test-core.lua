if not package.preload.athena_core then
  local base=assert(arg[0]:match('^(.*)/[^/]+$'))
  package.preload.athena_core=function() return dofile(base..'/core.lua') end
  package.preload.athena_collector=function() return dofile(base..'/collector.lua') end
end
local core=require('athena_core')
local collector=require('athena_collector')
local checks=0
local function check(v,message) checks=checks+1;assert(v,message) end
local function copy(t)
  if type(t)~='table' then return t end
  local out={};for k,v in pairs(t) do out[k]=copy(v) end;return out
end
local cfg={version=1,mode='shadow',policyGeneration='test',lanAddress='192.168.237.0',lanBits=24,maxTracked=64,maxCandidates=32}
local topology={wans={rpwan1='172.16.1.1'},clients={
  ['192.168.237.10']={valid=true,mac='02:00:00:00:00:10',ifname='lan2',wireless=false},
  ['192.168.237.11']={valid=true,mac='02:00:00:00:00:11',ifname='phy2-ap0',wireless=true}}}
local function flow(id,client,class)
  return {key='flow-'..id,identity={connectionId=tostring(id),zone='0',mark=65536,wan=1,
    protocolNumber=class=='RT' and 17 or 6,original={src=client,dst='1.1.1.1',sport=40000+id,dport=443},
    reply={src='1.1.1.1',dst='172.16.1.1',sport=443,dport=40000+id},instanceTagSafe=true,
    instanceMetadataComplete=true,queryProvenance={querySequence=1,idFieldPresent=true,
    fullMarkFieldPresent=true,zoneSource='explicit-row-zone0'}},
    decision={class=class,reason=class=='BULK' and 'bulk' or 'interactive',budgetAdmitted=class=='RT',rateKbps=class=='RT' and 500 or 20000},
    observationStartedAtUptime=9,validUntilUptime=15,applied={verified=true}}
end
local function pub(rows,seq,started)
  rows=copy(rows);seq=seq or 1;started=started or 9
  for _,f in ipairs(rows) do f.identity.queryProvenance.querySequence=seq;f.observationStartedAtUptime=started;f.validUntilUptime=started+6 end
  return {status='running',dataHealthy=true,nssPermit=false,producer='producer-1',boot='boot-1',
    snapshot={flows=rows,provenance={boot='boot-1',queryFamily='ipv4',queryZone=0,exitCode=0,
      sequence=seq,startedAtUptime=started,finishedAtUptime=started+0.2}}}
end
local rows={flow(1,'192.168.237.10','RT'),flow(2,'192.168.237.11','RT'),
  flow(3,'192.168.237.10','BULK'),flow(4,'192.168.237.11','BULK'),
  flow(5,'192.168.237.10','RT'),flow(6,'192.168.237.11','RT')}
local state=core.new(cfg);local p=pub(rows);local r=core.tick(state,p,p,topology,10)
check(r.summary.tracked==6 and r.summary.candidates==6,'Dynamic table must exceed three legacy slots')
check(r.summary.classes.RT==4 and r.summary.clients==2,'All client RT flows must be represented')
check(r.summary.exits.lan2==3 and r.summary.exits['phy2-ap0']==3,'Use actual wired/wireless exit')
check(r.summary.accelerated==0 and not r.summary.hardwareWrites,'Shadow must not claim hardware success')
check(r.summary.softwareProtectionVerified==6,'Report read-back software protection separately')
local mixed=copy(rows);mixed[1].identity.protocolNumber=6;mixed[3].identity.protocolNumber=17
local mixedState=core.new(cfg);local mixedPub=pub(mixed)
local mixedResult=core.tick(mixedState,mixedPub,mixedPub,topology,10)
check(mixedResult.summary.candidates==6,'Business class must not be inferred from TCP versus UDP')
local nextRows=copy(rows);table.remove(nextRows,2);p=pub(nextRows,2,12)
r=core.tick(state,p,p,topology,13)
check(r.summary.tracked==5 and #r.operations==6,'One flow ending must retain the other five')
local partial=pub({},3,13);partial.snapshot.admissionProjection={version=1}
r=core.tick(state,partial,nil,topology,14)
check(r.summary.tracked==5 and not r.summary.completeObservation,'Projection absence is not CT exit')
r=core.tick(state,nil,nil,topology,18)
check(r.summary.tracked==0 and not r.summary.sourceFresh,'Stopped renewal must expire leases')
state=core.new(cfg);p=pub(rows);core.tick(state,p,p,topology,10)
local changed=copy(topology);changed.clients['192.168.237.11'].mac='02:00:00:00:00:99'
p=pub(rows,2,12);r=core.tick(state,p,p,changed,13)
local bindingRetires=0;for _,op in ipairs(r.operations) do if op.reason=='client-or-egress-changed' then bindingRetires=bindingRetires+1 end end
check(bindingRetires==3 and r.summary.tracked==6,'Random MAC change affects only its own flows')
local reused={flow(1,'192.168.237.10','RT')};p=pub(reused,3,14);p.snapshot.flows[1].identity.reply.dport=51001
r=core.tick(state,p,p,topology,15)
check(r.summary.tracked==1 and r.flows[1].reply.dport==51001,'CT ID reuse must not retain old NAT identity')
local bad=pub(reused,4,16);bad.snapshot.flows[1].identity.mark=65536+8192
r=core.tick(state,bad,bad,topology,17);check(r.summary.tracked==0,'Proxy-marked flows stay out of direct NSS candidates')
state=core.new(cfg);p=pub(rows,10,9);core.tick(state,p,p,topology,10)
r=core.tick(state,pub(rows,9,10),nil,topology,11);check(not r.summary.sourceFresh,'Source sequence reversal cannot renew')
p=pub(rows,1,12);p.producer='new-producer';r=core.tick(state,p,p,topology,13)
check(r.summary.sourceSequence==1 and r.summary.retired==6,'New classifier instance retires prior bindings')
local small=copy(cfg);small.maxCandidates=2;state=core.new(small);p=pub(rows)
r=core.tick(state,p,p,topology,10)
check(r.summary.candidates==2 and r.summary.candidateOverflow==4,'Capacity exhaustion keeps software traffic')
check(r.flows[1].class=='RT' and r.flows[2].class=='RT','RT is preferred without per-device shares')
local n={{dst='192.168.237.10',lladdr='02:00:00:00:00:10'}}
local fdb={{mac=n[1].lladdr,ifname='lan2',age=1,localEntry=false}}
local c=collector.resolve(n,{},fdb,{},100)
check(c[n[1].dst].valid and c[n[1].dst].ifname=='lan2','Static client needs no Windows or DHCP process')
c=collector.resolve(n,{{ip=n[1].dst,mac='02:00:00:00:00:20',expires=200}},fdb,{},100)
check(not c[n[1].dst].valid and c[n[1].dst].reason=='dhcp-neighbor-conflict','DHCP/MAC disagreement cannot bind a new client')
local station={{mac=n[1].lladdr,ifname='phy2-ap0'}}
c=collector.resolve(n,{}, {},station,100)
check(c[n[1].dst].valid and c[n[1].dst].wireless,'Station association resolves an NSS-offloaded wireless exit')
station[2]={mac=n[1].lladdr,ifname='phy0-ap0'};c=collector.resolve(n,{}, {},station,100)
check(not c[n[1].dst].valid,'Ambiguous roaming does not select an old AP')
local nativeCfg=copy(cfg);nativeCfg.includeBestEffort=true
local bePub=pub({flow(7,'192.168.237.11','BE')});local beState=core.new(nativeCfg)
local beResult=core.tick(beState,bePub,bePub,topology,10)
check(beResult.summary.candidates==1 and beResult.flows[1].class=='BE','Shared-account native profile may admit validated best effort without a client quota')
print(require('luci.jsonc').stringify({passed=true,checks=checks,modelOnly=true,routerNetworkWrites=false}))
