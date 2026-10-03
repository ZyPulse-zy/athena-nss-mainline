import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {connectRouter} from '../nss20/connect-router.mjs';import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
const root='work/nss35',ctx=JSON.parse(fs.readFileSync('work/nss33/deployment-latest.json'));const cfg=JSON.parse(fs.readFileSync(ctx.localDir+'/config.json'));
const module=fs.readFileSync(root+'/address-query.lua','utf8'),policy=fs.readFileSync(root+'/observation-policy.lua','utf8');
const code=String.raw`local n=require('nixio');local j=require('luci.jsonc');local fs=require('nixio.fs')
local function read(p,l)local f=assert(io.open(p));local s=f:read(l+1)or'';f:close();assert(#s<=l);return s end
local function now()return tonumber(read('/proc/uptime',128):match('^[%d.]+'))end
local M=(function()
${module}
end)()
local P=(function()
${policy}
end)()
local runner='${ctx.base}/group-runner'
local cases={};local function record(name,pass,elapsed,reason,exitCode)assert(pass,name);cases[#cases+1]={name=name,passed=pass,seconds=elapsed,reason=reason,exitCode=exitCode}end
local started=now();local raw=M.run(n,now,j.parse,runner);local value=assert(j.parse(raw));record('real-address-inventory',#value>0,now()-started)
local fixtures={
 {'complete-json',"io.write('[{\"ifname\":\"fixture0\",\"addr_info\":[]}]')",false},
 {'timeout-after-partial-output',"io.write('[');io.flush();require('nixio').nanosleep(4)",'command-exit',124},
 {'timeout-cleans-descendant-group',"local n=require('nixio');local p=assert(n.fork());if p~=0 then io.write('[');io.flush()end;n.nanosleep(4)",'command-exit',124},
 {'child-exit-143',"io.write('[');os.exit(143)",'command-exit',143},
 {'partial-json-exit-zero',"io.write('[')",'invalid-json',0},
 {'wrong-json-type',"io.write('123')",'invalid-json',0},
 {'wrong-address-schema',"io.write('[{\"ifname\":false}]')",'invalid-json',0},
 {'stdout-overflow',"io.write(string.rep('x',65537));io.flush();require('nixio').nanosleep(4)",'stdout-overflow'},
 {'stderr-overflow',"io.stderr:write(string.rep('x',4097));io.stderr:flush();require('nixio').nanosleep(4)",'stderr-overflow'},
 {'reserved-runner-failure',"os.exit(3)",'fatal'}
}
for _,f in ipairs(fixtures)do
 local marker='NSS35_READONLY_FIXTURE_'..f[1];local script='local marker='..string.format('%q',marker)..';'..f[2]
 local proxy=setmetatable({exec=function(path,seconds,program,...)
  assert(path==runner and seconds=='2'and program=='/sbin/ip');return n.exec(runner,seconds,'/usr/bin/lua','-e',script)
 end},{__index=n})
 local began=now();local ok,out=pcall(M.run,proxy,now,j.parse,runner);local elapsed=now()-began
 local pass=f[3]==false and ok or f[3]=='fatal'and not ok and type(out)=='string'or not ok and P.accept(out)and out.reason==f[3]and(not f[4]or out.exitCode==f[4])
 record(f[1],pass and elapsed<5.5,elapsed,type(out)=='table'and out.reason or nil,type(out)=='table'and out.exitCode or nil)
 local alive=0;for pid in fs.dir('/proc')do if pid:match('^%d+$')then local h=io.open('/proc/'..pid..'/cmdline');if h then local cmd=h:read(8192)or'';h:close();if cmd:find(script,1,true)then alive=alive+1 end end end end
 assert(alive==0,'fixture descendant remains')
end
print(j.stringify({passed=true,checks=#cases,cases=cases,scope='Actual target Lua/nixio and existing group runner; RAM-only child fixtures, no classifier service or network state mutation',allFixtureDescendantsGone=true,routerConfigurationWrites=false,productionFaultInjected=false}))`;
fs.writeFileSync(root+'/native-query-fixtures.lua',code);
const c=await connectRouter();try{
 const h=await c.run('/usr/bin/sha256sum '+ctx.base+'/group-runner');assert.equal(h.code,0);assert.equal(h.stdout.split(/\s/)[0],cfg.files['group-runner']);
 const e=encode("/usr/bin/lua - <<'NSS35_QUERY'\n"+code+"\nNSS35_QUERY\n");const r=receipt(await c.run(e.command),e);fs.writeFileSync(root+'/query-native-raw-private.json',JSON.stringify(r,null,2)+'\n');assert.equal(r.code,0,r.stderr+' '+r.stdout);
 const out=JSON.parse(r.stdout);out.observedAt=new Date().toISOString();out.querySha256=crypto.createHash('sha256').update(module).digest('hex');out.runnerSha256=cfg.files['group-runner'];out.execBytes=e.execBytes;fs.writeFileSync(root+'/query-native-qualified.json',JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify(out));
}finally{c.close()}
