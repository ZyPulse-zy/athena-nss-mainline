import fs from'node:fs';import assert from'node:assert/strict';import crypto from'node:crypto';import{connectRouter}from'../nss20/connect-router.mjs';import{encode,receipt}from'../nss11/v7-observe-repair/observe2/transport.mjs';
const root='work/nss39',sha=s=>crypto.createHash('sha256').update(s).digest('hex'),d=JSON.parse(fs.readFileSync('work/nss37/deployment-latest.json')),cfg=JSON.parse(fs.readFileSync(d.localDir+'/config.json'));
const helper=fs.readFileSync(root+'/tc-command.lua','utf8'),worker=fs.readFileSync(root+'/worker.lua','utf8');
const lua=String.raw`local n=require('nixio');local fs=require('nixio.fs');local j=require('luci.jsonc')
local helper=[====[${helper}]====];local runner='${d.base}/group-runner';local rows={};local checks={}
local function read(p)local f=io.open(p);if not f then return nil end;local s=f:read(8192)or'';f:close();return s end
local function now()return tonumber(assert(read('/proc/uptime')):match('^[%d.]+'))end
local function quote(s)return "'"..s:gsub("'","'\\''").."'"end
local M=assert(loadstring(helper))();local pid=n.getpid()
local good={{{'-j','qdisc','show','dev','rpwan1'},65536},{{'-d','filter','show','dev','rpifb5','parent','800a:'},262144},{{'-batch','/tmp/router-project-game-classifier/batch.'..pid},65536}}
for _,a in ipairs(good)do assert(M.validate(a[1],a[2],pid));checks[#checks+1]='approved-shape'end
local bad={{{'-j','qdisc','show','dev','br-lan'},65536},{{'-j','qdisc','show','dev','rpwan6'},65536},{{'-j','qdisc','show','dev','rpwan1; reboot'},65536},{{'-j','qdisc','show','dev','rpwan1','extra'},65536},{{'-j','qdisc','show','dev','rpwan1'},65537},{{'-d','filter','show','dev','rpifb5','parent','x;:'},262144},{{'-batch','/tmp/router-project-game-classifier/batch.'..(pid+1)},65536},{{'-batch','/tmp/foreign'},65536},{{'-batch','/tmp/router-project-game-classifier/batch.'..pid},262144},{{'qdisc','del','dev','rpwan1','root'},65536}}
for _,a in ipairs(bad)do assert(not pcall(M.validate,a[1],a[2],pid));checks[#checks+1]='unapproved-shape-rejected'end
local cases={
 {name='success',leaf='io.write("fixture-ok")',success=true,outer=6},
 {name='partial-nonzero',leaf='io.write("partial");io.flush();os.exit(7)',want='code=7',outer=6},
 {name='stdout-overflow',leaf='io.write(string.rep("x",65537));io.flush()',want='stdout exceeded bound',outer=6},
 {name='stderr-overflow',leaf='io.stderr:write(string.rep("x",4097));io.stderr:flush()',want='stderr exceeded bound',outer=6},
 {name='partial-timeout',leaf='io.write("partial");io.flush();n.nanosleep(4)',want='2 second deadline',outer=6},
 {name='term-ignored-timeout',leaf='n.signal(15,"ign");n.nanosleep(4)',want='code=9',outer=6},
 {name='batch-partial-fatal',leaf='io.write("partial");io.flush();os.exit(8)',want='filter-batch failed',batch=true,outer=6},
 {name='outer-cancel',leaf='n.nanosleep(4)',outer=1,rc=124}
}
for _,case in ipairs(cases)do
 local marker='NSS39_TC_FIXTURE_'..case.name
 local leaf='local marker='..string.format('%q',marker)..';local n=require("nixio");'..case.leaf
 local child='local n=require("nixio");local j=require("luci.jsonc");local M=assert(loadstring('..string.format('%q',helper)..'))();local function now()local f=assert(io.open("/proc/uptime"));local s=f:read(128);f:close();return tonumber(s:match("^[%d.]+"))end;local test={};for k,v in pairs(n)do test[k]=v end;test.exec=function(path,...)assert(path=="/sbin/tc");n.exec("/usr/bin/lua","-e",'..string.format('%q',leaf)..')end;local argv='..(case.batch and'{"-batch","/tmp/router-project-game-classifier/batch."..n.getpid()}'or'{"-j","qdisc","show","dev","rpwan1"}')..';local t=now();local ok,result=pcall(M.run,test,now,argv,65536);print(j.stringify({ok=ok,result=result,elapsed=now()-t}))'
 local command=runner..' '..case.outer..' /usr/bin/lua -e '..quote(child)..' 2>&1; r=$?; printf "\n__NSS39_RC__%s\n" "$r"'
 local started=now();local p=assert(io.popen(command));local raw=p:read(16385)or'';p:close();assert(#raw<=16384)
 local body,rc=raw:match('^(.*)\n__NSS39_RC__(%d+)\n$');assert(body and tonumber(rc)==(case.rc or 0),raw)
 local value;if not case.rc then value=assert(j.parse(body))end;if value then assert(value.ok==(case.success==true));if case.success then assert(value.result=='fixture-ok')else assert(value.result:find(case.want,1,true),value.result)end end
 local alive=0;for id in fs.dir('/proc')do if id:match('^%d+$')then local cmd=read('/proc/'..id..'/cmdline');if cmd and cmd:find(marker,1,true)then alive=alive+1 end end end;assert(alive==0,'Fixture remains')
 rows[#rows+1]={name=case.name,seconds=now()-started,outerExit=tonumber(rc),result=value,allFixtureChildrenGone=true,productionFaultInjected=false}
end
print(j.stringify({passed=true,checks=#checks,rows=rows,productionFaultInjected=false,routerConfigurationWrites=false}))`;
fs.writeFileSync(root+'/tc-native-rendered.lua',lua);const e=encode("/usr/bin/lua - <<'NSS39_TC_NATIVE'\n"+lua+'\nNSS39_TC_NATIVE\n');
if(process.argv.includes('--prepare-only')){console.log(JSON.stringify({execBytes:e.execBytes,bytes:e.bytes}));process.exit(0)}
const c=await connectRouter();try{const h=await c.run('/usr/bin/sha256sum '+d.base+'/group-runner');assert.equal(h.code,0);assert.equal(h.stdout.split(/\s/)[0],cfg.files['group-runner']);
const r=receipt(await c.run(e.command),e);fs.writeFileSync(root+'/tc-native-raw-private.json',JSON.stringify(r,null,2)+'\n');assert.equal(r.code,0,r.stderr);const out=JSON.parse(r.stdout);Object.assign(out,{observedAt:new Date().toISOString(),helperSha256:sha(helper),workerSha256:sha(worker),runnerSha256:cfg.files['group-runner'],execBytes:e.execBytes});fs.writeFileSync(root+'/tc-native-qualified.json',JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify(out));}finally{c.close()}
