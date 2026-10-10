-- Pure affected-policy/codec tests. No tc/nft/ECM mutations or live traffic.
local root=assert(arg[0]:match('^(.*)/[^/]+$'))
assert(root~='/tmp/athena-dorm-native')
local j=require('luci.jsonc');local collector=dofile(root..'/collector.lua')
local plan=dofile(root..'/queue_plan.lua');local codec=dofile(root..'/flow_json.lua')
local original=plan.plan(0x7a00,{70000,70000,70000,70000,70000})
assert(#plan.changes(original,original)==0)
local fresh=plan.plan(0x7a00,{64000,70000,70000,70000,70000})
local changes=plan.changes(original,fresh);assert(#changes==4)
for _,line in ipairs(changes) do
 assert(line:match('^class change ') and not line:find('qdisc',1,true))
 assert(not line:find('classid 7a00:1 ',1,true) and not line:find('classid 7a00:ff ',1,true))
end
assert(original.tags[1].RT==fresh.tags[1].RT and fresh.rates[2]==original.rates[2])
local stations=collector.station_clients({
 ['02:00:00:00:00:01']={assoc=true,authorized=true},
 ['02:00:00:00:00:02']={assoc=false,authorized=true},
 ['02:00:00:00:00:03']={assoc=true,authorized=false},
 ['malformed']={assoc=true,authorized=true}},'phy2-ap0')
assert(#stations==1 and stations[1].mac=='02:00:00:00:00:01' and stations[1].ifname=='phy2-ap0')
local shared={src='192.0.2.1',dst='198.51.100.1',sport=42001,dport=27015}
local value={flows={{class='RT',original=shared,budgetAdmitted=true},{class='BULK',original=shared,budgetAdmitted=false}},
 summary={sourceFresh=false,tracked=2},operations={},wans={rpwan1='198.51.100.1'}}
local decoded=assert(j.parse(codec.stringify(value,j)))
assert(#decoded.flows==2 and decoded.flows[2].budgetAdmitted==false and decoded.summary.sourceFresh==false)
assert(decoded.flows[1].original.sport==42001 and decoded.flows[2].original.dport==27015)
assert(codec.stringify({flows={},summary={tracked=0}},j):find('"flows":[]',1,true))
print(j.stringify({passed=true,selectiveBudgetClasses=true,authorizedAssociationsOnly=true,
 chunkedFlowRoundTrip=true,dataPlaneWrites=false,modelOnly=true}))
