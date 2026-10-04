// RAM-only differential validation and interleaved CPU timings; no installer.
import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {connectRouter} from '../nss20/connect-router.mjs';
import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
const label=process.argv[2];assert.match(label,/^[a-z0-9-]+$/);
const ctx=JSON.parse(fs.readFileSync('work/nss47/deployment-latest.json'));
const helper=fs.readFileSync('work/nss64/json-project.lua','utf8'),fixtures=fs.readFileSync('work/nss64/project-fixtures.lua','utf8');
const code=String.raw`local j=require('luci.jsonc');local n=require('nixio');local fs=require('nixio.fs')
local function read(p,l)local f=assert(io.open(p));local s=f:read(l+1)or'';f:close();assert(#s<=l);return s end
local function now()return tonumber(read('/proc/uptime',128):match('^[%d.]+'))end
local base,hash=[===[${ctx.base}]===],[===[${ctx.configHash}]===]
assert(read('/root/router-project/game-classifier-generation',512)==base..' '..hash..'\n')
for _,k in ipairs({'front_end_ipv4_stop','front_end_ipv6_stop'})do assert(tonumber(read('/sys/kernel/debug/ecm/'..k,128))==1)end
local original=assert(dofile(base..'/owned.lua')).jsonProject
local candidate=assert(loadstring([====[${helper}]====]))()
local tests=assert(loadstring([====[${fixtures}]====]))()
local raw=read('/tmp/router-project-game-classifier/snapshot.json',4194304);local tree=assert(j.parse(raw))
assert(tree.configSha256==hash and tree.status=='running'and tree.nssPermit==false and not tree.error)
local validation=tests(original,candidate,j,n,tree);local rows={};local started=now()
local function bench(name,fn,dataset,scope)
 collectgarbage('collect');local at,cpu=now(),os.clock();local p=fn(dataset);local stopped=now();local used=os.clock()-cpu
 assert(type(p)=='table');rows[#rows+1]={mode=name,scope=scope,wallSeconds=stopped-at,cpuSeconds=used}
 io.stderr:write(j.stringify(rows[#rows])..'\n');io.stderr:flush()
end
for round=1,3 do
 if round%2==1 then bench('original',original,tree,'real-full-snapshot');bench('candidate',candidate,tree,'real-full-snapshot')
 else bench('candidate',candidate,tree,'real-full-snapshot');bench('original',original,tree,'real-full-snapshot')end
end
-- 512 repeated real-shaped flows are an offline scale fixture, never live CT.
local scaled={snapshot={flows={},provenance=tree.snapshot.provenance},nssPermit=false}
assert(#tree.snapshot.flows>0);for i=1,512 do scaled.snapshot.flows[i]=tree.snapshot.flows[((i-1)%#tree.snapshot.flows)+1]end
bench('original',original,scaled,'synthetic-512-shared-flow-shapes')
bench('candidate',candidate,scaled,'synthetic-512-shared-flow-shapes')
local oldEncoded=assert(j.stringify(original(scaled)));local newEncoded=assert(j.stringify(candidate(scaled)))
-- Field order is jsonc dependent; compare all parsed values, not strings.
local function equal(a,b)
 if type(a)~=type(b)then return false end;if type(a)~='table'then return a==b end
 for k,v in pairs(a)do if not equal(v,b[k])then return false end end;for k in pairs(b)do if a[k]==nil then return false end end;return true
end
assert(equal(j.parse(oldEncoded),j.parse(newEncoded)),'Scaled native JSON differs')
validation.scaledNativeRoundTrip=true
for _,k in ipairs({'front_end_ipv4_stop','front_end_ipv6_stop'})do assert(tonumber(read('/sys/kernel/debug/ecm/'..k,128))==1)end
print(j.stringify({passed=true,validation=validation,rows=rows,realFlows=#tree.snapshot.flows,realBytes=#raw,syntheticFlows=512,
 syntheticBytes=#oldEncoded,startedAt=started,finishedAt=now(),readonly=true,candidateInstalled=false,nssAdmissionAllowed=false,sourceSequence=tree.snapshot.provenance.sequence}))`;
const body="/usr/bin/lua - <<'NSS64_DIFFERENTIAL'\n"+code+'\nNSS64_DIFFERENTIAL\n';
const e=encode(ctx.base+'/group-runner 6 /bin/sh -c '+"'"+body.replaceAll("'","'\\''")+"'");
const c=await connectRouter();try{
 const raw=receipt(await c.run(e.command),e);
 fs.writeFileSync('work/nss64/'+label+'-compare-raw-private.json',JSON.stringify(raw,null,2)+'\n',{flag:'wx'});
 assert.equal(raw.code,0,raw.stderr);const result=JSON.parse(raw.stdout);assert.equal(result.passed,true);
 result.observedAt=new Date().toISOString();result.helperSha256=crypto.createHash('sha256').update(helper).digest('hex');
 fs.writeFileSync('work/nss64/'+label+'-compare.json',JSON.stringify(result,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(result));
}finally{c.close()}
