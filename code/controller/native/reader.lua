-- Router-local reader. Only publishes desired state; it never writes tc/nft/ECM.
local j=require('luci.jsonc');local n=require('nixio');local fs=require('nixio.fs')
local root=assert(arg[0]:match('^(.*)/[^/]+$'))
local core=dofile(root..'/core.lua');local collector=dofile(root..'/collector.lua')
local cfg={version=1,mode='shadow',policyGeneration='native-abi1',lanAddress='192.168.237.0',lanBits=24,
 maxTracked=2048,maxCandidates=32,includeBestEffort=true}
local state=core.new(cfg)
local function atomic(name,text)
 local p=root..'/'..name;local f=assert(io.open(p..'.new','w'));assert(f:write(text));assert(f:close());assert(fs.rename(p..'.new',p))
end
while not fs.stat(root..'/stop')do
 local topology=collector.topology();local projection,full=collector.publications()
 local result=core.tick(state,projection,full,topology,collector.now())
 result.wans=topology.wans
 -- Contains private CT/topology identities; the directory must remain 0700.
 atomic('desired.json',j.stringify(result));atomic('heartbeat',tostring(collector.now()))
 n.nanosleep(1)
end
