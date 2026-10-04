// Exact old/new parser and classifier in RAM. No production installation.
import fs from 'node:fs';import assert from 'node:assert/strict';
import {connectRouter} from '../nss20/connect-router.mjs';
import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
const delta=JSON.parse(fs.readFileSync('work/nss47/cache-delta.json'));
const q=JSON.parse(fs.readFileSync('work/nss47/cache-qualified.json'));assert.ok(q.passed&&q.candidateSha256===delta.candidateSha256);
const d=JSON.parse(fs.readFileSync('work/nss46/deployment-latest.json'));
const worker=fs.readFileSync('work/nss46/worker.lua','utf8');
const query=worker.slice(worker.indexOf('local function query(cmd,limit)'),worker.indexOf('local AddressQuery='));
const lua=String.raw`local n=require('nixio');local fs=require('nixio.fs');local j=require('luci.jsonc');local base='${d.base}'
local function read(p,l)local f=assert(io.open(p));local s=f:read((l or 4194304)+1)or'';f:close();assert(#s<=(l or 4194304));return s end
local function now()return tonumber(read('/proc/uptime',128):match('^[%d.]+'))end
local function boot()return read('/proc/sys/kernel/random/boot_id',128):gsub('%s+$','')end
local function hash(p,h)local f=assert(io.popen('/usr/bin/sha256sum '..p));local s=f:read(256);f:close();assert(s:match('^(%x+) ')==h)end
hash(base..'/config.json','${d.configHash}');local cfg=assert(j.parse(read(base..'/config.json',131072)));hash(base..'/classifier-core.lua','${delta.originalSha256}')
hash(base..'/worker.lua',cfg.files['worker.lua']);hash(base..'/conntrack-source.lua',cfg.files['conntrack-source.lua'])
local function replace(s,a,b)local first,last=s:find(a,1,true);assert(first and not s:find(a,last+1,true));return s:sub(1,first-1)..b..s:sub(last+1)end
local old=read(base..'/classifier-core.lua');local candidate=replace(old,[===[${delta.old}]===],[===[${delta.new}]===])
 candidate=replace(candidate,[===[${delta.resetOld}]===],[===[${delta.resetNew}]===])
local function parser(s)return assert(loadstring(replace(s,'return function(action)','if scope.testParser then return parse end\nreturn function(action)')))()({testParser=true},cfg.policy)end
local a,b=parser(old),parser(candidate);local source=dofile(base..'/conntrack-source.lua');${query}
local f=assert(io.popen('ip -j -4 address show'));local addressText=f:read(65537);f:close();assert(#addressText<=65536)
local addresses={};for _,entry in ipairs(assert(j.parse(addressText)))do for _,v in ipairs(entry.addr_info or{})do if v.family=='inet'and v.scope=='global'then addresses[entry.ifname]=v['local']end end end
local captured;local rows,p=source.collect(cfg.source,{now=now,boot=boot,query=function(...)local r=query(...);captured=r;return r end},boot(),1)
local function same(a,b)if type(a)~=type(b)then return false end;if type(a)~='table'then return a==b end;for k,v in pairs(a)do if not same(v,b[k])then return false end end;for k in pairs(b)do if a[k]==nil then return false end end;return true end
local accepted=0;for _,r in ipairs(rows)do local x,y=a(r.line,addresses),b(r.line,addresses);assert(same(x,y),'Actual parser differs');if x then accepted=accepted+1 end end
local cpu,wall={old=0,new=0},{old=0,new=0};local loops=20
for round=1,4 do local order=round%2==1 and{'old','new'}or{'new','old'};for _,name in ipairs(order)do
 local fn=name=='old'and a or b;local w,c=now(),os.clock();for i=1,loops do fn=parser(name=='old'and old or candidate);for _,r in ipairs(rows)do fn(r.line,addresses)end end
 cpu[name]=cpu[name]+os.clock()-c;wall[name]=wall[name]+now()-w
end end
local clock=p.startedAtUptime;local mock={boot=boot,now=function()return clock end,query=function()clock=clock+0.1;return captured end}
local function make(s)local t=p.startedAtUptime;local r={boot=boot,now=function()return t end,query=function()t=t+0.1;return captured end};return assert(loadstring(s))()({observer=cfg.source,boot=boot()},cfg.policy,read,function()return addressText end,source,r)end
local x,y=make(old),make(candidate);for i=1,3 do assert(same(x(),y()),'Complete classifier differs')end
assert(tonumber(read('/sys/kernel/debug/ecm/front_end_ipv4_stop',64))==1);assert(tonumber(read('/sys/kernel/debug/ecm/ecm_nss_ipv4/accelerated_count',64))==0)
print(j.stringify({passed=true,actualRows=#rows,acceptedRows=accepted,parserMetadataEqual=true,completeClassifierRepeatedEqual=3,parserTraversalsPerVersion=loops*4,cpuSeconds=cpu,wallSeconds=wall,readonly=true,productionInstalled=false,nssEnabled=false}))`;
const c=await connectRouter();try{const e=encode("/usr/bin/lua - <<'NSS47_NATIVE_PARSER'\n"+lua+"\nNSS47_NATIVE_PARSER\n");const r=receipt(await c.run(e.command),e);assert.equal(r.code,0,r.stderr);const out=JSON.parse(r.stdout);out.observedAt=new Date().toISOString();out.originalSha256=delta.originalSha256;out.candidateSha256=delta.candidateSha256;out.execBytes=e.execBytes;fs.writeFileSync('work/nss47/native-cache-qualified.json',JSON.stringify(out,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(out));}finally{c.close()}
