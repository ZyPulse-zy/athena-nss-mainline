import fs from'node:fs';import assert from'node:assert/strict';import crypto from'node:crypto';import{connectRouter}from'../nss20/connect-router.mjs';import{encode,receipt}from'../nss11/v7-observe-repair/observe2/transport.mjs';
const root='work/nss39',d=JSON.parse(fs.readFileSync('work/nss37/deployment-latest.json')),helper=fs.readFileSync(root+'/tc-command.lua','utf8'),source=fs.readFileSync(root+'/original-worker.lua','utf8');
const start=source.indexOf('local function direct('),end=source.indexOf("assert(direct('/usr/bin/sha256sum",start);assert.ok(start>0&&end>start);const direct=source.slice(start,end);
const lua=String.raw`local n=require('nixio');local j=require('luci.jsonc')
local function read(p)local f=assert(io.open(p));local s=f:read(65536);f:close();return s end
local function now()return tonumber(read('/proc/uptime'):match('^[%d.]+'))end
local function quote(s)return "'"..s:gsub("'","'\\''").."'"end
local helper=[====[${helper}]====];local direct=[====[${direct}]====];local runner='${d.base}/group-runner'
local setup=[===[local n=require("nixio");local j=require("luci.jsonc");local function now()local f=assert(io.open("/proc/uptime"));local s=f:read(128);f:close();return tonumber(s:match("^[%d.]+"))end;local function quote(s)return "'"..s:gsub("'","'\\''").."'"end;]===]
local function child(method,wans)
 local s=setup..'local M=assert(loadstring('..string.format('%q',helper)..'))();'..direct
 s=s..'\nlocal begin=now();local calls=0;local shapes={};local function call(args,cap)calls=calls+1;'
 if method=='old'then s=s..'return direct("/usr/bin/timeout -k 1 2 /bin/sh -c "..quote("/sbin/tc "..table.concat(args," ")),cap)'else s=s..'return M.run(n,now,args,cap)'end
 return s..'end;for k=1,'..wans..' do for _,prefix in ipairs({"rpwan","rpifb"})do local dev=prefix..k;local qs=assert(j.parse(call({"-j","qdisc","show","dev",dev},65536)));local q;for _,v in ipairs(qs)do if v.kind=="cake" and v.root then assert(not q);q=v end end;assert(q);local raw=call({"-d","filter","show","dev",dev,"parent",q.handle},262144);shapes[#shapes+1]={dev=dev,kind=q.kind,handle=q.handle,filterBytes=#raw}end end;print(j.stringify({callSeconds=now()-begin,calls=calls,shapes=shapes}))'
end
local rows={};local begin=now();local before=tonumber(read('/sys/class/net/lan4/statistics/tx_bytes'))
for _,wans in ipairs({1,5})do for pair=1,4 do local row={wans=wans,pair=pair};for _,method in ipairs(pair%2==1 and{'old','candidate'}or{'candidate','old'})do
 local cmd=runner..' 6 /usr/bin/lua -e '..quote(child(method,wans))..' 2>&1; r=$?; printf "\n__NSS39_RC__%s\n" "$r"';local t=now();local f=assert(io.popen(cmd));local raw=f:read(16385)or'';f:close();assert(#raw<=16384);local body,rc=raw:match('^(.*)\n__NSS39_RC__(%d+)\n$');assert(rc=='0',raw);local result=assert(j.parse(body));assert(result.calls==wans*4);result.totalSeconds=now()-t;row[method]=result
end;for i,q in ipairs(row.old.shapes)do local c=row.candidate.shapes[i];assert(q.dev==c.dev and q.handle==c.handle and q.kind==c.kind)end;rows[#rows+1]=row end end
local dt=now()-begin;local tx=tonumber(read('/sys/class/net/lan4/statistics/tx_bytes'))-before
print(j.stringify({passed=true,rows=rows,backgroundLan4Mbps=tx*8/dt/1000000,elapsedSeconds=dt,routerWrites=false,allQueriesReadOnly=true,queueKindAndHandleEqual=true}))`;
fs.writeFileSync(root+'/tc-benchmark-rendered.lua',lua);const e=encode("/usr/bin/lua - <<'NSS39_TC_BENCH'\n"+lua+'\nNSS39_TC_BENCH\n');
if(process.argv.includes('--prepare-only')){console.log(JSON.stringify({execBytes:e.execBytes}));process.exit(0)}
const c=await connectRouter();try{const r=receipt(await c.run(e.command),e);fs.writeFileSync(root+'/tc-benchmark-raw-private.json',JSON.stringify(r,null,2)+'\n');assert.equal(r.code,0,r.stderr);const out=JSON.parse(r.stdout);out.observedAt=new Date().toISOString();out.helperSha256=crypto.createHash('sha256').update(helper).digest('hex');out.groups=[1,5].map(wans=>{const rows=out.rows.filter(r=>r.wans===wans),mean=(m,k)=>rows.reduce((v,r)=>v+r[m][k],0)/rows.length;return{wans,queriesPerRun:wans*4,pairs:rows.length,oldCallsMs:mean('old','callSeconds')*1000,candidateCallsMs:mean('candidate','callSeconds')*1000,oldTotalMs:mean('old','totalSeconds')*1000,candidateTotalMs:mean('candidate','totalSeconds')*1000}});fs.writeFileSync(root+'/tc-benchmark-qualified.json',JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify({passed:true,groups:out.groups,backgroundLan4Mbps:out.backgroundLan4Mbps,routerWrites:false}));}finally{c.close()}
