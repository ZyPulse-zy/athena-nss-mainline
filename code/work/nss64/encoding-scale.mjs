// Isolate jsonc conversion from tree projection on identical prevalidated trees.
import fs from 'node:fs';import assert from 'node:assert/strict';
import {connectRouter} from '../nss20/connect-router.mjs';
import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
const label=process.argv[2];assert.match(label,/^[a-z0-9-]+$/);
const ctx=JSON.parse(fs.readFileSync('work/nss47/deployment-latest.json'));
const helper=fs.readFileSync('work/nss64/flow-json.lua','utf8');
const code=String.raw`local j=require('luci.jsonc');local fs=require('nixio.fs');local n=require('nixio')
local function read(p,l)local f=assert(io.open(p));local x=f:read(l+1)or'';f:close();assert(#x<=l);return x end
local function now()return tonumber(read('/proc/uptime',128):match('^[%d.]+'))end
local base,hash=[===[${ctx.base}]===],[===[${ctx.configHash}]===]
assert(read('/root/router-project/game-classifier-generation',512)==base..' '..hash..'\n');assert(not fs.lstat('/root/router-project/active-transaction'))
local function closed()for _,k in ipairs({'front_end_ipv4_stop','front_end_ipv6_stop'})do assert(tonumber(read('/sys/kernel/debug/ecm/'..k,128))==1)end;for _,k in ipairs({'ecm_db/connection_count','ecm_nss_ipv4/accelerated_count','ecm_nss_ipv6/accelerated_count','ecm_nss_ipv4/pending_accel_count','ecm_nss_ipv6/pending_accel_count','ecm_nss_ipv4/pending_decel_count','ecm_nss_ipv6/pending_decel_count'})do assert(tonumber(read('/sys/kernel/debug/ecm/'..k,128))==0)end end
closed();local own=assert(dofile(base..'/owned.lua'));local split=assert(loadstring([====[${helper}]====]))()
local raw=read('/tmp/router-project-game-classifier/snapshot.json',4194304);local tree=assert(j.parse(raw));assert(tree.configSha256==hash and tree.nssPermit==false and tree.status=='running'and #tree.snapshot.flows>0)
local function same(a,b)if type(a)~=type(b)then return false end;if type(a)~='table'then return a==b end;for k,v in pairs(a)do if not same(v,b[k])then return false end end;for k in pairs(b)do if a[k]==nil then return false end end;return true end
local rows={};local started=now()
for _,count in ipairs({128,256,512,1024})do
 local v={snapshot={flows={},provenance=tree.snapshot.provenance},nssPermit=false}
 for i=1,count do v.snapshot.flows[i]=tree.snapshot.flows[((i-1)%#tree.snapshot.flows)+1]end
 local p=own.jsonProject(v);collectgarbage('collect');local w,c=now(),os.clock();local a=assert(j.stringify(p));local oldWall,oldCpu=now()-w,os.clock()-c
 collectgarbage('collect');w,c=now(),os.clock();local b=assert(split(p,j,function(x)return x end));local newWall,newCpu=now()-w,os.clock()-c
 assert(#a<=4194304 and #a==#b and same(j.parse(a),j.parse(b)),'Complete encoded fields differ')
 local row={flows=count,bytes=#a,originalCpu=oldCpu,candidateCpu=newCpu,originalWall=oldWall,candidateWall=newWall,semanticEquality=true}
 rows[#rows+1]=row;io.stderr:write(j.stringify(row)..'\n');io.stderr:flush()
end
closed();print(j.stringify({passed=true,rows=rows,startedAt=started,finishedAt=now(),installedJsonStringifyIsC=debug.getinfo(j.stringify).what=='C',
 excludesProjectionCpu=true,syntheticScaleFixture=true,originalFullPublicationFieldsRetained=true,readonly=true,nssAdmissionAllowed=false,candidateInstalled=false}))`;
const body="/usr/bin/lua - <<'NSS64_SCALE'\n"+code+'\nNSS64_SCALE\n';
const e=encode(ctx.base+'/group-runner 6 /bin/sh -c '+"'"+body.replaceAll("'","'\\''")+"'");
const c=await connectRouter();try{
 const raw=receipt(await c.run(e.command),e);
 fs.writeFileSync('work/nss64/'+label+'-scale-raw-private.json',JSON.stringify(raw,null,2)+'\n',{flag:'wx'});
 assert.equal(raw.code,0,raw.stderr);const result=JSON.parse(raw.stdout);result.observedAt=new Date().toISOString();
 fs.writeFileSync('work/nss64/'+label+'-scale.json',JSON.stringify(result,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(result));
}finally{c.close()}
