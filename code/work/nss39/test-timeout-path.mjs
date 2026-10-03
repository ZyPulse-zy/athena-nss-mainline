import fs from'node:fs';import assert from'node:assert/strict';import crypto from'node:crypto';import{connectRouter}from'../nss20/connect-router.mjs';import{encode,receipt}from'../nss11/v7-observe-repair/observe2/transport.mjs';
const root='work/nss39',d=JSON.parse(fs.readFileSync('work/nss37/deployment-latest.json')),cfg=JSON.parse(fs.readFileSync(d.localDir+'/config.json'));
const source=fs.readFileSync(root+'/original-worker.lua','utf8'),start=source.indexOf('local function direct('),end=source.indexOf("assert(direct('/usr/bin/sha256sum",start);assert.ok(start>0&&end>start);const direct=source.slice(start,end);
const code=String.raw`local n=require('nixio');local fs=require('nixio.fs');local j=require('luci.jsonc')
local function quote(s)return "'"..s:gsub("'","'\\''").."'"end
local function read(p)local f=assert(io.open(p));local s=f:read(8192)or'';f:close();return s end
local function now()return tonumber(read('/proc/uptime'):match('^[%d.]+'))end
local runner='${d.base}/group-runner';local direct=[====[${direct}]====];local rows={}
for _,case in ipairs({{name='normal',outer=6,inner=0,expected=0},{name='inner-query-timeout',outer=6,inner=4,expected=1},{name='outer-maintenance-timeout',outer=1,inner=4,expected=124}})do
 local marker='NSS39_ISOLATED_'..case.name;local leaf='local marker='..string.format('%q',marker)..';local n=require("nixio");n.nanosleep('..case.inner..');io.write("fixture-result")'
 local query='/usr/bin/timeout -k 1 2 /bin/sh -c '..quote('/usr/bin/lua -e '..quote(leaf))
 local child=direct..'\nlocal out=direct('..string.format('%q',query)..',65536);assert(out=="fixture-result");print("CHILD_OK")'
 local cmd=runner..' '..case.outer..' /usr/bin/lua -e '..quote(child)..' 2>&1; r=$?; printf "\n__NSS39_OUTER_RC__%s\n" "$r"'
 local begin=now();local p=assert(io.popen(cmd));local raw=p:read(16385)or'';p:close();assert(#raw<=16384)
 local body,rc=raw:match('^(.*)\n__NSS39_OUTER_RC__(%d+)\n$');assert(body and tonumber(rc)==case.expected,case.name..' '..raw)
 local inner=body:match('__NSS23_RC__(%d+)');local alive=0
 for pid in fs.dir('/proc')do if pid:match('^%d+$')then local h=io.open('/proc/'..pid..'/cmdline');if h then local s=h:read(8192)or'';h:close();if s:find(marker,1,true)then alive=alive+1 end end end end
 assert(alive==0,'Fixture child remains')
 rows[#rows+1]={name=case.name,seconds=now()-begin,outerSeconds=case.outer,outerExit=tonumber(rc),innerExit=inner and tonumber(inner),readFailureReported=body:find('Command failed',1,true)~=nil,allFixtureDescendantsGone=true,raw=body}
end
print(j.stringify({passed=true,routerConfigurationWrites=false,productionFaultInjected=false,rows=rows}))`;
fs.writeFileSync(root+'/timeout-path-rendered.lua',code);const c=await connectRouter();try{const h=await c.run('/usr/bin/sha256sum '+d.base+'/group-runner');assert.equal(h.code,0);assert.equal(h.stdout.split(/\s/)[0],cfg.files['group-runner']);const e=encode("/usr/bin/lua - <<'NSS39_TIMEOUT_PATH'\n"+code+'\nNSS39_TIMEOUT_PATH\n');const r=receipt(await c.run(e.command),e);fs.writeFileSync(root+'/timeout-path-raw-private.json',JSON.stringify(r,null,2)+'\n');assert.equal(r.code,0,r.stderr);const out=JSON.parse(r.stdout);out.observedAt=new Date().toISOString();out.originalWorkerSha256=crypto.createHash('sha256').update(source).digest('hex');out.runnerSha256=cfg.files['group-runner'];fs.writeFileSync(root+'/timeout-path-qualified-private.json',JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify({...out,rows:out.rows.map(({raw,...x})=>x)}));}finally{c.close()}
