-- RAM-only read/parse/project/stringify measurements. No file or QoS writes.
local j=require('luci.jsonc');local n=require('nixio');local fs=require('nixio.fs')
local base=assert(arg[1]);local hash=assert(arg[2]);assert(base:match('^/root/router%-project/classifier/nss23%-[%w%-]+$'))
local function read(p,l)local f=assert(io.open(p));local s=f:read(l+1)or'';f:close();assert(#s<=l);return s end
local function now()return tonumber(read('/proc/uptime',128):match('^[%d.]+'))end
local function closed()for _,k in ipairs({'front_end_ipv4_stop','front_end_ipv6_stop'})do assert(tonumber(read('/sys/kernel/debug/ecm/'..k,128))==1)end
 for _,k in ipairs({'ecm_db/connection_count','ecm_nss_ipv4/accelerated_count','ecm_nss_ipv6/accelerated_count','ecm_nss_ipv4/pending_accel_count','ecm_nss_ipv6/pending_accel_count','ecm_nss_ipv4/pending_decel_count','ecm_nss_ipv6/pending_decel_count'})do assert(tonumber(read('/sys/kernel/debug/ecm/'..k,128))==0)end end
closed();assert(not fs.lstat('/root/router-project/active-transaction'))
assert(read('/root/router-project/game-classifier-generation',512)==base..' '..hash..'\n')
local own=assert(dofile(base..'/owned.lua'));local path='/tmp/router-project-game-classifier/snapshot.json'
local f=assert(n.open(path,'r'));local st=assert(f:stat());assert(st.type=='reg'and st.uid==0 and st.gid==0 and st.nlink==1 and st.size<=4194304)
local t0,c0=now(),os.clock();local parts={};local size=0
while true do local s=assert(f:read(65536));if #s==0 then break end;size=size+#s;assert(size<=4194304);parts[#parts+1]=s end
local raw=table.concat(parts);local st2=assert(f:stat());f:close();for _,k in ipairs({'dev','ino','size','mtime','ctime'})do assert(st[k]==st2[k],'Held snapshot changed')end
local rows={{stage='held-file-read',wallSeconds=now()-t0,cpuSeconds=os.clock()-c0}}
local tree
local function measure(stage,fn)
 collectgarbage('collect');local a,b=now(),os.clock();local value=fn();rows[#rows+1]={stage=stage,wallSeconds=now()-a,cpuSeconds=os.clock()-b};return value
end
tree=measure('full-json-parse',function()return assert(j.parse(raw))end)
assert(tree.configSha256==hash and tree.status=='running'and tree.nssPermit==false and not tree.error)
assert(type(tree.snapshot.flows)=='table');local projected=measure('json-tree-projection',function()return own.jsonProject(tree)end)
local encoded=measure('projected-json-stringify',function()return assert(j.stringify(projected))end)
local reparsed=measure('serialized-json-parse',function()return assert(j.parse(encoded))end)
local function same(a,b)
 if type(a)~=type(b)then return false end;if type(a)~='table'then return a==b end
 for k,v in pairs(a)do if not same(v,b[k])then return false end end;for k in pairs(b)do if a[k]==nil then return false end end;return true
end
assert(same(tree,reparsed),'JSON round trip changed fields')
closed();print(j.stringify({passed=true,rows=rows,rawBytes=#raw,encodedBytes=#encoded,flows=#tree.snapshot.flows,
 sourceSequence=tree.snapshot.provenance.sequence,sourceAgeAtStart=t0-tree.snapshot.provenance.startedAtUptime,
 publicationAgeAtStart=t0-tree.atUptime,startedAt=t0,finishedAt=now(),semanticRoundTrip=true,
 readonly=true,nssAdmissionAllowed=false,liveFixture=true,offeredLoadControlled=false}))
