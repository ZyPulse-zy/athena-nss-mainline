-- Pure full-identity/size/order regression; real target nft roundtrip is separate.
local root=assert(arg[0]:match('^(.*)/[^/]+$'));local m=dofile(root..'/tag_rules.lua')
local plan=dofile(root..'/queue_plan.lua');local j=require('luci.jsonc')
local budgets={up=plan.plan(0x7e00,{40000,40000,40000,40000,40000}),down=plan.plan(0x7a00,{70000,70000,70000,70000,70000})}
local function policy(id,protocol)
 return{flow={connectionId=id,mark=65536+256,protocol=protocol or 17,
  original={src='192.0.2.12',sport=41000,dst='198.51.100.99',dport=27015},
  reply={src='198.51.100.99',sport=27015,dst='203.0.113.1',dport=50000}},up=0x7e160006,down=0x7a160006}
end
local count=0;local function check(value)assert(value);count=count+1 end
local empty=m.render({},budgets);check(not empty:find('elements',1,true)and not empty:find('map ',1,true))
local a,b=policy(12),policy(13,6)
local text=m.render({a,b},budgets)
check(text==m.render({b,a},budgets))
check(text:find('type filter hook postrouting priority 0;',1,true)~=nil)
check(text:find('ct id @flow_ids jump exact_labels',1,true)~=nil)
check(text:find('elements = { 12, 13 };',1,true)~=nil)
check(text:find('ct mark 65792 meta l4proto udp',1,true)~=nil)
check(text:find('ct original ip saddr 192.0.2.12 ct original proto-src 41000 ct original ip daddr 198.51.100.99 ct original proto-dst 27015',1,true)~=nil)
check(text:find('ct reply ip saddr 198.51.100.99 ct reply proto-src 27015 ct reply ip daddr 203.0.113.1 ct reply proto-dst 50000',1,true)~=nil)
check(text:find('meta priority set '..string.format('%.0f',a.up)..' return',1,true)~=nil)
check(text:find('meta priority set '..string.format('%.0f',a.down)..' return',1,true)~=nil)
check(not text:find('map ',1,true))
local collision=policy(12,6);collision.flow.mark=65536+512
local shared=m.render({a,collision},budgets);check(shared:find('elements = { 12 };',1,true)~=nil)
check(shared:find('ct mark 66048 meta l4proto tcp',1,true)~=nil)
check(not pcall(m.render,{a,a},budgets))
local many={};for i=1,80 do many[i]=policy(i)end
local full=m.render(many,budgets);local rules=0;for line in full:gmatch('[^\n]+')do if line:match('^ct direction')and line:find(' return',1,true)then rules=rules+1 end end
check(rules==160 and #full<65536)
many[81]=policy(81);check(not pcall(m.render,many,budgets))
local isolated=m.render({a,b},budgets,{tableName='athena_dorm_model_labels',hook=false})
check(not isolated:find('hook',1,true));check(not pcall(m.render,{a},budgets,{tableName='fw4',hook=false}))
check(not pcall(m.render,{a},budgets,{tableName='athena_dorm_model_labels',hook=true}))
local replaced=m.render({a},budgets,{removePrevious=true});check(replaced:match('^delete table inet athena_dorm_qos\n')~=nil)
print(j.stringify({passed=true,checks=count,allElevenIdentityFields=true,scalarIdGateNotSufficientForLabel=true,boundedPolicies=80,modelOnly=true,dataPlaneWrites=false}))
