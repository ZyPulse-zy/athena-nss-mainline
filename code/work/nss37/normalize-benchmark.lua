local n=require('nixio');local j=require('luci.jsonc');local base='__BASE__'
local function read(p,l)local f=assert(io.open(p));local s=f:read((l or 4194304)+1);f:close();assert(#s<=(l or 4194304));return s end
local function now()return tonumber(read('/proc/uptime',128):match('^[%d.]+'))end
local function boot()return read('/proc/sys/kernel/random/boot_id',128):gsub('%s+$','')end
local function check(p,h)local f=assert(io.popen('/usr/bin/sha256sum '..p));local s=f:read(256);f:close();assert(s:match('^(%x+) ')==h)end
check(base..'/config.json','__CONFIG_HASH__');check(base..'/conntrack-source.lua','__SOURCE_HASH__')
local cfg=assert(j.parse(read(base..'/config.json',131072)));local source=dofile(base..'/conntrack-source.lua')
__QUERY__
local captured;local rows,p=source.collect(cfg.source,{boot=boot,now=now,query=function(...)captured=query(...);return captured end},boot(),1)
local Candidate=assert(loadstring([===[__CANDIDATE__]===]))()
local function same(a,b)if type(a)~=type(b)then return false end;if type(a)~='table'then return a==b end;for k,v in pairs(a)do if not same(v,b[k])then return false end end;for k in pairs(b)do if a[k]==nil then return false end end;return true end
local datasets={{name='live-captured-text',raw=captured.stdout,stderr=captured.stderr,synthetic=false}}
local lines={};for line in captured.stdout:gmatch('[^\n]+')do if line:match('^ipv4%s+%d+%s+[ut][dc]p%s')then lines[#lines+1]=line end end;assert(#lines>0)
local expanded={};for i=1,512 do local line=lines[(i-1)%#lines+1];local replaced,count=line:gsub('(%sid=)%d+',function(k)return k..i end);assert(count==1);expanded[i]=replaced end
datasets[2]={name='synthetic-512-rows-from-captured-grammar',raw=table.concat(expanded,'\n')..'\n',stderr='',synthetic=true}
local begin=now();local tx=tonumber(read('/sys/class/net/lan4/statistics/tx_bytes',128));local results={}
for _,d in ipairs(datasets)do
 local original,originalSummary=source.normalize(cfg.source,p,d.raw,d.stderr,p.boot,p.finishedAtUptime)
 local rowsNew,summaryNew=Candidate.normalize(cfg.source,p,d.raw,d.stderr,p.boot,p.finishedAtUptime);assert(same(original,rowsNew)and same(originalSummary,summaryNew))
 local r={name=d.name,synthetic=d.synthetic,bytes=#d.raw,rows=#original,samples={},allOutputsEqual=true}
 for iteration=1,8 do
  local function run(lib)local w=now();local cpu=os.clock();local a,b=lib.normalize(cfg.source,p,d.raw,d.stderr,p.boot,p.finishedAtUptime);local c=os.clock()-cpu;local elapsed=now()-w;assert(same(a,original)and same(b,originalSummary));return{cpuSeconds=c,wallSeconds=elapsed}end
  local a,b;if iteration%2==1 then a=run(source);b=run(Candidate)else b=run(Candidate);a=run(source)end
  r.samples[#r.samples+1]={old=a,new=b}
 end
 results[#results+1]=r
end
local done=now();print(j.stringify({passed=true,routerWrites=false,candidateInstalled=false,sourceHashesVerified=true,trafficGenerated=false,sourceReadOnce=true,results=results,observerSeconds=done-begin,lan4Mbps=(tonumber(read('/sys/class/net/lan4/statistics/tx_bytes',128))-tx)*8/(done-begin)/1e6,scope='Alternating old/new normalization of identical strings in target Lua RAM. Synthetic expansion is not kernel traffic or forwarding performance.'}))
