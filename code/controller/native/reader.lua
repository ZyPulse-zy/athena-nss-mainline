-- Router-local reader. Only publishes desired state; it never writes tc/nft/ECM.
local j=require('luci.jsonc');local n=require('nixio');local fs=require('nixio.fs')
local root=assert(arg[0]:match('^(.*)/[^/]+$'))
local core=dofile(root..'/core.lua');local collector=dofile(root..'/collector.lua')
local flowJson=dofile(root..'/flow_json.lua')
local cfg={version=1,mode='shadow',policyGeneration='native-abi1',lanAddress='192.168.237.0',lanBits=24,
 maxTracked=2048,maxCandidates=32,includeBestEffort=false}
local state=core.new(cfg)
local previousEncodeSeconds=0
local function atomic(name,text)
 local p=root..'/'..name;local f=assert(io.open(p..'.new','w'));assert(f:write(text));assert(f:close());assert(fs.rename(p..'.new',p))
end
while not fs.stat(root..'/stop')do
 local began=collector.now();local topology=collector.topology();local topologyAt=collector.now()
 local projection,full=collector.publications(false);local publicationAt=collector.now()
 local result=core.tick(state,projection,full,topology,publicationAt)
 result.wans=topology.wans
 result.summary.reader={classificationSource='candidate-projection',topologySeconds=topologyAt-began,
  publicationSeconds=publicationAt-topologyAt,policySeconds=collector.now()-publicationAt,
  previousEncodeSeconds=previousEncodeSeconds,stationSources=topology.stationSources,collection=topology.collection,
  topologyComplete=topology.complete,sourceLeaseSeconds=6}
 -- Contains private CT/topology identities; the directory must remain 0700.
 local encodingAt=collector.now();local text=flowJson.stringify(result,j);previousEncodeSeconds=collector.now()-encodingAt
 atomic('desired.json',text);atomic('heartbeat',tostring(collector.now()))
 n.nanosleep(1)
end
