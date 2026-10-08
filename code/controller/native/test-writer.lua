-- Target Lua/nft parser regression for the real empty-map failure. Run from
-- the flattened RAM staging directory, after stop. No native/tc/nft writes.
local root=assert(arg[0]:match('^(.*)/[^/]+$'))
local fs=require('nixio.fs');local j=require('luci.jsonc')
assert(root~='/tmp/athena-dorm-native','Use a separate model directory')
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
  local input=assert(io.open(root..'/tags.nft'));local text=input:read('*a');input:close()
  -- Publication is mocked, so remove only the mock previous-table deletion.
  -- Every generated table/map still goes through the real nft parser.
  text=text:gsub('^delete table inet athena_dorm_qos\n','')
  local output=assert(io.open(root..'/tags-parser.nft','w'));assert(output:write(text));output:close()
  local f=assert(io.popen('/usr/sbin/nft -c -f '..root..'/tags-parser.nft 2>&1; printf "\\nATHENA_EXIT_%s\\n" "$?"'))
  local s=f:read('*a');f:close();assert(s:match('ATHENA_EXIT_0\n$'),s);parsed=true;return s
 end
 if c=='/usr/sbin/nft -f '..root..'/tags.nft' then return '' end -- Mock publication only.
 error('Unexpected mutation: '..c)
end
local row='';local additions=0;local writes=0;local nixio=require('nixio');local originalOpen=nixio.open
nixio.open=function(p,mode)
 if p~='/sys/kernel/debug/athena_ecm_gate/control' then return originalOpen(p,mode)end
 return {write=function(_,text)
  writes=writes+1
  if text:match('^add 0 ')then additions=additions+1;row='slot=0 state=1 generation='..additions..' id=12 serial=20 selected=1 receipt_present=1 receipt=0 create_pending=0 create_ack=1\n'
  elseif text=='revoke 0\n' then row='slot=0 state=6 generation=1 id=12 serial=20 selected=1 receipt_present=0 receipt=0 create_pending=0 create_ack=0 removal_response=4 removal_error=5\n'
  else error('Unexpected native model write: '..text)end
  return #text
 end,close=function()end}
end
local function read(p)assert(p=='/sys/kernel/debug/athena_ecm_gate/status');return 'abi=2 capacity=32 stopping=0 firmware_receipts=1\n'..row end
local function put(p,s)
 assert(p==root..'/tags.nft');local f=assert(io.open(p,'w'));assert(f:write(s));assert(f:close())
end
local writer=dofile(root..'/writer.lua').new(root,command,read,put,function()return 100 end,function()end,r)
writer.tick({wans=r.wans,flows={},operations={},summary={tracked=0,clients=0,exits={},classes={},sourceFresh=false,sourceSequence=1}})
assert(parsed and r.flowState.nativeOwned==0)
local flow={key='one',binding='source',class='BULK',candidate=true,budgetAdmitted=false,client='192.0.2.12',egress='phy0-ap0',
 connectionId=12,mark=65536,protocol=6,wan=1,validUntil=106,sequence=2,
 original={src='192.0.2.12',sport=41000,dst='198.51.100.99',dport=443},reply={src='198.51.100.99',sport=443,dst='198.51.100.1',dport=50000}}
local summary={tracked=1,clients=1,exits={['phy0-ap0']=1},classes={BULK=1},sourceFresh=true,sourceSequence=2}
writer.tick({wans=r.wans,flows={flow},operations={},summary=summary})
assert(additions==1 and #r.ownedFlows==1 and r.ownedFlows[1].connectionId==12)
writer.tick({wans=r.wans,flows={},operations={},summary=summary})
assert(#r.ownedFlows==1 and r.ownedFlows[1].retiring and r.ownedFlows[1].original.sport==41000 and r.ownedFlows[1].serial==20)
writer.tick({wans=r.wans,flows={},operations={},summary=summary})
assert(r.flowState.retiredFirmwareAbsent==1 and r.flowState.nativeOwned==0 and #r.ownedFlows==0)
flow.sequence=4;writer.tick({wans=r.wans,flows={flow},operations={},summary=summary})
assert(additions==2 and writes==3 and r.flowState.nativeOwned==1)
nixio.open=originalOpen
print(j.stringify({passed=true,emptyMapParsed=true,retiringIdentityPreserved=true,firmwareAbsentSlotReused=true,dataPlaneWrites=false,mockedKernel=true}))
