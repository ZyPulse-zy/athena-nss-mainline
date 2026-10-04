// Exact native jsonc comparison, including all publication fields. No installer.
import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {connectRouter} from '../nss20/connect-router.mjs';
import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
const label=process.argv[2];assert.match(label,/^[a-z0-9-]+$/);
const variant=process.argv[3]??'flow-json';assert.ok(['flow-json','flow-json-stream'].includes(variant));
const projection=process.argv[4]??'original';assert.ok(['original','fast'].includes(projection));
const ctx=JSON.parse(fs.readFileSync('work/nss47/deployment-latest.json'));
const helper=fs.readFileSync('work/nss64/'+variant+'.lua','utf8');
const projector=fs.readFileSync('work/nss64/json-project-fast.lua','utf8');
const fixture=fs.readFileSync('work/nss64/project-fixtures.lua','utf8');
const code=String.raw`local j=require('luci.jsonc');local n=require('nixio');local fs=require('nixio.fs')
local function read(p,l)local f=assert(io.open(p));local s=f:read(l+1)or'';f:close();assert(#s<=l);return s end
local function now()return tonumber(read('/proc/uptime',128):match('^[%d.]+'))end
local base,hash=[===[${ctx.base}]===],[===[${ctx.configHash}]===]
assert(read('/root/router-project/game-classifier-generation',512)==base..' '..hash..'\n')
assert(not fs.lstat('/root/router-project/active-transaction'))
local function closed()for _,k in ipairs({'front_end_ipv4_stop','front_end_ipv6_stop'})do assert(tonumber(read('/sys/kernel/debug/ecm/'..k,128))==1)end;for _,k in ipairs({'ecm_db/connection_count','ecm_nss_ipv4/accelerated_count','ecm_nss_ipv6/accelerated_count','ecm_nss_ipv4/pending_accel_count','ecm_nss_ipv6/pending_accel_count','ecm_nss_ipv4/pending_decel_count','ecm_nss_ipv6/pending_decel_count'})do assert(tonumber(read('/sys/kernel/debug/ecm/'..k,128))==0)end end
closed();local own=assert(dofile(base..'/owned.lua'));local candidate=assert(loadstring([====[${helper}]====]))()
local fast=assert(loadstring([====[${projector}]====]))();local selectedProjection=${projection==='fast'?'fast':'own.jsonProject'}
local function original(v)return assert(j.stringify(own.jsonProject(v)))end
local function changed(v)return assert(candidate(v,j,selectedProjection))end
local function same(a,b)
 if type(a)~=type(b)then return false end;if type(a)~='table'then return a==b end
 for k,v in pairs(a)do if not same(v,b[k])then return false end end;for k in pairs(b)do if a[k]==nil then return false end end;return true
end
local cases=0
local function good(v)local a,b=original(v),changed(v);assert(same(j.parse(a),j.parse(b)),'Complete JSON values differ');cases=cases+1 end
local function bad(v)assert(not pcall(original,v)and not pcall(changed,v),'Invalid tree accepted');cases=cases+1 end
good({});good({warming=true});good({snapshot={flows={}}});good({snapshot={flows={{x=1},{x=2}}}})
good({snapshot={flows={'x',false,3.5}}});good({snapshot={flows={[1]={},[3]={}}}})
good({snapshot={flows={named={}}}});good({snapshot={flows={{baseline={dev={[1]={x=1},[48]={x=48}}}}}}})
good({snapshot={flows={{x='quote"\\\n\0/中文',z=1e100,enabled=false}}},unknown={deep={future=true}},nssPermit=false})
local r={id=1,nat={x=2}};good({snapshot={flows={{identity=r,leaf={identity=r}},{identity=r}}},meta=r})
good({snapshot={flows=false}});good({snapshot={}});good({snapshot={flows={},[1]='number'}})
good({snapshot={flows={{{'nested','list'}}}}});good({1,2,3});good(false);good('scalar')
good({current={dev={1,2}},baseline={dev={3,4}},snapshot={flows={{x=1}},current={dev={5,6}}}})
local rootCycle={snapshot={flows={}}};rootCycle.snapshot.flows[1]=rootCycle;bad(rootCycle)
local crossCycle={snapshot={flows={{}}},meta={}};crossCycle.meta.x=crossCycle.snapshot.flows[1];crossCycle.snapshot.flows[1].x=crossCycle.meta;bad(crossCycle)
local snapshotCycle={snapshot={flows={}}};snapshotCycle.snapshot.extra=snapshotCycle.snapshot;bad(snapshotCycle)
bad({snapshot={flows={{bad=math.huge}}}});bad({snapshot={flows={{bad=0/0}}}})
bad({snapshot={flows={{[1]='x',['1']='collision'}}}});bad({snapshot={flows={{x=function()end}}}})
local cyc={};cyc.x=cyc;bad({snapshot={flows={cyc}}});bad({[true]=1})
local raw=read('/tmp/router-project-game-classifier/snapshot.json',4194304);local tree=assert(j.parse(raw))
assert(tree.configSha256==hash and tree.status=='running'and tree.nssPermit==false and not tree.error);assert(#tree.snapshot.flows>0)
good(tree);local rows={};local started=now()
local projectValidation=assert(loadstring([====[${fixture}]====]))()(own.jsonProject,fast,j,n,tree)
local function bench(name,fn,v,scope)
 collectgarbage('collect');local a,b=now(),os.clock();local text=fn(v);local at,cpu=now()-a,os.clock()-b
 rows[#rows+1]={mode=name,scope=scope,wallSeconds=at,cpuSeconds=cpu,bytes=#text};io.stderr:write(j.stringify(rows[#rows])..'\n');io.stderr:flush();return text
end
for round=1,3 do if round%2==1 then bench('original',original,tree,'real-complete');bench('candidate',changed,tree,'real-complete')else bench('candidate',changed,tree,'real-complete');bench('original',original,tree,'real-complete')end end
local scaled={snapshot={flows={},provenance=tree.snapshot.provenance},nssPermit=false}
for i=1,512 do scaled.snapshot.flows[i]=tree.snapshot.flows[((i-1)%#tree.snapshot.flows)+1]end
local a=bench('original',original,scaled,'synthetic-512');local b=bench('candidate',changed,scaled,'synthetic-512')
assert(same(j.parse(a),j.parse(b)),'Scaled complete JSON differs');cases=cases+1
closed();print(j.stringify({passed=true,cases=cases,rows=rows,realFlows=#tree.snapshot.flows,realBytes=#raw,sourceSequence=tree.snapshot.provenance.sequence,
 completePublicationFieldEquality=true,sharedAliasesPreserved=true,unknownFieldsPreserved=true,originalJsonProjectionRetained=true,
 originalFullAuditUnchanged=true,originalFreshnessUnchanged=true,projectValidation=projectValidation,startedAt=started,finishedAt=now(),readonly=true,candidateInstalled=false,nssAdmissionAllowed=false}))`;
const body="/usr/bin/lua - <<'NSS64_ENCODING'\n"+code+'\nNSS64_ENCODING\n';
const e=encode(ctx.base+'/group-runner 6 /bin/sh -c '+"'"+body.replaceAll("'","'\\''")+"'");
const c=await connectRouter();try{
 const raw=receipt(await c.run(e.command),e);
 fs.writeFileSync('work/nss64/'+label+'-encoding-raw-private.json',JSON.stringify(raw,null,2)+'\n',{flag:'wx'});
 assert.equal(raw.code,0,raw.stderr);const result=JSON.parse(raw.stdout);assert.equal(result.passed,true);
 result.observedAt=new Date().toISOString();result.helperSha256=crypto.createHash('sha256').update(helper).digest('hex');
 result.variant=variant;
 result.projection=projection;result.projectorSha256=crypto.createHash('sha256').update(projector).digest('hex');
 fs.writeFileSync('work/nss64/'+label+'-encoding.json',JSON.stringify(result,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(result));
}finally{c.close()}
