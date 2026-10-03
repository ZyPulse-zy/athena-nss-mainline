// Read-only single collection plus RAM replay. No production source or state changes.
import fs from 'node:fs';import assert from 'node:assert/strict';
import {connectRouter} from '../nss20/connect-router.mjs';
import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
import {verifyCurrentClassifier} from './binding.mjs';
const {deployment:d,config:cfg}=verifyCurrentClassifier();
const worker=fs.readFileSync(d.localDir+'/worker.lua','utf8');
const query=worker.slice(worker.indexOf('local function query(cmd,limit)'),worker.indexOf('local AddressQuery='));
assert.ok(query.includes('queryCleanupCompleted=true')&&query.endsWith('\n'));
const address=fs.readFileSync('work/nss35/address-query.lua','utf8');
const pub=fs.readFileSync('work/nss33/admission-publication.lua','utf8');
const spec={base:d.base,configSha256:d.configHash,files:{'worker.lua':cfg.files['worker.lua'],'conntrack-source.lua':cfg.files['conntrack-source.lua'],'classifier-core.lua':cfg.files['classifier-core.lua'],'owned.lua':cfg.files['owned.lua'],'backend.lua':cfg.files['backend.lua']}};
const code=String.raw`local n=require('nixio');local j=require('luci.jsonc');local S=assert(j.parse([===[${JSON.stringify(spec)}]===]))
local function read(p,l)local f=assert(io.open(p));local s=f:read((l or 4194304)+1);f:close();assert(#s<=(l or 4194304));return s end
local function now()return tonumber(read('/proc/uptime',128):match('^[%d.]+'))end
local function boot()return read('/proc/sys/kernel/random/boot_id',128):gsub('%s+$','')end
local function check(p,h)local f=assert(io.popen('/usr/bin/sha256sum '..p));local s=f:read(256);f:close();assert(s:match('^(%x+) ')==h)end
check(S.base..'/config.json',S.configSha256);for f,h in pairs(S.files)do check(S.base..'/'..f,h)end
local cfg=assert(j.parse(read(S.base..'/config.json',131072)));local source=dofile(S.base..'/conntrack-source.lua');local factory=dofile(S.base..'/classifier-core.lua');local own=dofile(S.base..'/owned.lua');local Backend=dofile(S.base..'/backend.lua')
${query}
local Address=assert(loadstring([===[${address}]===]))();local Project=assert(loadstring([===[${pub}]===]))()
local t0=now();local addressRaw=Address.run(n,now,j.parse,S.base..'/group-runner');local t1=now()
local normalize=source.normalize;local normSeconds=0;source.normalize=function(...)local a=now();local rows,summary=normalize(...);normSeconds=normSeconds+now()-a;return rows,summary end
local rows,p=source.collect(cfg.source,{boot=boot,now=now,query=query},boot(),1);local t2=now()
local replaySource={collect=function()return rows,p end};local runtime={boot=boot,now=now}
local step=factory({observer=cfg.source,boot=boot()},cfg.policy,read,function(c)assert(c=='ip -j -4 address show');return addressRaw end,replaySource,runtime)
local t3=now();local snap=step();local t4=now();for _,f in ipairs(snap.flows)do f.leaf=Backend.leaf(f);f.applied={backend='CAKE-software-baseline',verified=false,softwareReconcilePending=true}end;local t5=now()
local small=Project.project(snap);local t6=now();local raw=assert(j.stringify(own.jsonProject(small)));local t7=now()
local liveRaw=read('/tmp/router-project-game-classifier/classification.json',4194304);local t8=now();local live=assert(j.parse(liveRaw));local t9=now();local roundtrip=assert(j.stringify(own.jsonProject(live)));local t10=now()
print(j.stringify({readonly=true,routerWrites=false,sourceHashesVerified=true,trafficGenerated=false,productionWorkerInstrumented=false,oneBoundedCtCollection=true,sourceRows=#rows,classifiedRows=#snap.flows,coldReplayCandidateRows=#small.flows,addressQuerySeconds=t1-t0,ctQuerySeconds=p.finishedAtUptime-p.startedAtUptime,sourceNormalizeSeconds=normSeconds,collectTotalSeconds=t2-t1,coreReplaySeconds=t4-t3,leafSeconds=t5-t4,projectionSeconds=t6-t5,coldEncodeSeconds=t7-t6,liveReadSeconds=t8-t7,liveParseSeconds=t9-t8,liveEncodeSeconds=t10-t9,liveBytes=#liveRaw,roundtripBytes=#roundtrip,liveCandidateRows=live.snapshot and #live.snapshot.flows,liveCompleteRows=live.snapshot and live.snapshot.admissionProjection.completeInputFlowCount,liveStatus=live.status,totalSeconds=t10-t0,scope='Independent single read-only collection; cold classification RAM replay and same-frame publication microbenchmark. Not a production worker trace or game performance ABA.'}))`;
const c=await connectRouter();try{const e=encode("/usr/bin/lua - <<'NSS36_PROFILE_READONLY'\n"+code+"\nNSS36_PROFILE_READONLY\n");const r=receipt(await c.run(e.command),e);assert.equal(r.code,0,r.stderr);const out=JSON.parse(r.stdout);out.observedAt=new Date().toISOString();out.execBytes=e.execBytes;fs.writeFileSync('work/nss36/publication-path-profile.json',JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify(out));}finally{c.close()}
