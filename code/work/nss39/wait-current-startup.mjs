// Readiness is bound to this installation. Old publication is never accepted.
import fs from'node:fs';import assert from'node:assert/strict';import{connectRouter}from'../nss20/connect-router.mjs';import{encode,receipt}from'../nss11/v7-observe-repair/observe2/transport.mjs';
const d=JSON.parse(fs.readFileSync('work/nss39/deployment-latest.json'));assert.equal(d.committed,false);
const code=String.raw`local j=require('luci.jsonc');local n=require('nixio');local rows={}
local function read(p,l)local f=assert(io.open(p));local s=f:read(l+1)or'';f:close();assert(#s<=l);return s end
local function now()return tonumber(read('/proc/uptime',128):match('^[%d.]+'))end
local consecutive=0;local previous
for i=1,20 do
 local ok,value=pcall(function()
  local s=assert(j.parse(read('/tmp/router-project-game-classifier/classification.json',4194304)));local g=assert(j.parse(read('/tmp/router-project-game-classifier/guardian.json',8192)));local p=assert(s.snapshot.provenance)
  assert(s.configSha256=='${d.configHash}'and g.configSha256==s.configSha256 and s.producer==g.producer,'Current installation not yet published')
  assert(s.status=='running'and s.dataHealthy and s.nssPermit==false and g.healthy and p.sequence>=2 and now()-p.startedAtUptime<6 and now()-g.atUptime<6,'Current installation not yet healthy')
  assert(read('/proc/'..s.pid..'/cmdline',8192)==table.concat({'/usr/bin/lua','${d.base}/worker.lua','watch','${d.base}','${d.configHash}'},'\0')..'\0')
  local a={};for v in read('/proc/'..s.pid..'/stat',8192):match('^%d+ %b() (.*)$'):gmatch('%S+')do a[#a+1]=v end;assert(a[20]==s.start and a[1]~='Z')
  return{producer=s.producer,sequence=p.sequence,sourceAge=now()-p.startedAtUptime,configSha256=s.configSha256}
 end)
 rows[#rows+1]={ready=ok,result=value};if ok and previous==value.producer then consecutive=consecutive+1 else consecutive=ok and 1 or 0 end;previous=ok and value.producer or nil
 if consecutive>=2 then print(j.stringify({passed=true,rows=rows,currentInstallationBound=true,oldPublicationNeverAccepted=true}));return end
 n.nanosleep(0,500000000)
end
error('Current classifier startup did not qualify within fixed readiness window')`;
const c=await connectRouter();try{const e=encode("/usr/bin/lua - <<'NSS39_STARTUP'\n"+code+'\nNSS39_STARTUP\n'),r=receipt(await c.run(e.command),e);assert.equal(r.code,0,r.stderr);const p=JSON.parse(r.stdout);p.observedAt=new Date().toISOString();fs.writeFileSync(d.localDir+'/startup-qualified.json',JSON.stringify(p,null,2)+'\n');console.log(JSON.stringify({passed:true,probes:p.rows.length,currentInstallationBound:true}));}finally{c.close()}
