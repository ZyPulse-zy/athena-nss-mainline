-- Target Lua/nft parser regression for the real empty-map failure. Run from
-- the flattened RAM staging directory, after stop. No native/tc/nft writes.
local root=assert(arg[0]:match('^(.*)/[^/]+$'))
local fs=require('nixio.fs');local j=require('luci.jsonc')
assert(not fs.stat(root..'/lock'),'Stop the transaction before this check')
assert(not fs.stat('/sys/module/athena_ecm_gate'))
local plan=dofile(root..'/queue_plan.lua')
local r={wans={},ingress={up=plan.plan(0x7e00,{40000,40000,40000,40000,40000}),
 down=plan.plan(0x7a00,{70000,70000,70000,70000,70000})}}
for w=1,5 do r.wans['rpwan'..w]='198.51.100.'..w end
local parsed=false
local function command(c)
 if c:match('^/sbin/tc %-j %-d qdisc show dev rp')then
  return j.stringify({{kind='cake',options={bandwidth=c:find('rpifb',1,true) and 8750000 or 5000000}}})
 end
 if c=='/usr/sbin/nft -c -f '..root..'/tags.nft' then
  local f=assert(io.popen(c..' 2>&1; printf "\\nATHENA_EXIT_%s\\n" "$?"'))
  local s=f:read('*a');f:close();assert(s:match('ATHENA_EXIT_0\n$'),s);parsed=true;return s
 end
 if c=='/usr/sbin/nft -f '..root..'/tags.nft' then return '' end -- Mock publication only.
 error('Unexpected mutation: '..c)
end
local function read(p)assert(p=='/sys/kernel/debug/athena_ecm_gate/status');return 'abi=1 capacity=32 stopping=0 firmware_receipts=1\n' end
local function put(p,s)
 assert(p==root..'/tags.nft');local f=assert(io.open(p,'w'));assert(f:write(s));assert(f:close())
end
local writer=dofile(root..'/writer.lua').new(root,command,read,put,function()return 100 end,function()end,r)
writer.tick({wans=r.wans,flows={},operations={},summary={tracked=0,clients=0,exits={},classes={},sourceFresh=false,sourceSequence=1}})
assert(parsed and r.flowState.nativeOwned==0)
print(j.stringify({passed=true,emptyMapParsed=true,dataPlaneWrites=false,mockedKernel=true}))
