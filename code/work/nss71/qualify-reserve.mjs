import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';
import {connectRouter} from '../nss20/connect-router.mjs';import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';import {verifyPreparation as previous} from '../nss70/session-binding.mjs';
const old=fs.readFileSync('work/nss53/classifier.lua','utf8'),source=fs.readFileSync('work/nss71/classifier.lua','utf8');
const reserve=";assert(now()<e.epochUntil-4,'Fresh epoch lacks tag setup reserve')";assert.equal(old.replace(reserve,''),source);
const take=s=>s.slice(s.indexOf(' function out.ready()'),s.indexOf(' function out.sample()'));
const fixture=String.raw`local checks=0
local function test(src,age,changed)
 local t=1000+age;local function now()return t end;local record={};local sourceDiagnostic;local out={};local P={selected={}};local function readContext()sourceDiagnostic={startedAtUptime=1000};return{snapshot={admissionProjection=false}},{}end
 local Consumer={pair=function(s,c,at)assert(not changed,'Selected CT/NAT tuple drift');assert(at<1002,'Pre-learning time margin insufficient');return{epochUntil=1005}end};local function describeSelection()return{}end
 local run=assert(loadstring('return function(out,now,record,P,readContext,Consumer,describeSelection) '..src..' return out.ready() end'))()
 return run(out,now,record,P,readContext,Consumer,describeSelection)
end
local a,r,retry=test(OLD,1.12,false);assert(not a and retry and r:find('Fresh epoch lacks tag setup reserve',1,true));checks=checks+1
assert(test(NEW,1.12,false));checks=checks+1
assert(test(NEW,1.99,false));checks=checks+1
assert(test(OLD,0.9,false));checks=checks+1
local a,r,retry=test(NEW,2,false);assert(not a and retry and r:find('Pre-learning time margin insufficient',1,true));checks=checks+1
local a,r,retry=test(NEW,6,false);assert(not a and retry);checks=checks+1
local a,r,retry=test(NEW,0.1,true);assert(not a and not retry and r:find('Selected CT/NAT tuple drift',1,true));checks=checks+1
print(require('luci.jsonc').stringify({passed=true,checks=checks,obsoleteReserveFailureReproduced=true,validFrameCanReachOriginalPinBarrier=true,pairBoundaryStillRefuses=true,changedIdentityStillRefuses=true,fixtureUsesMockedContextAndUnchangedPairContract=true,ramOnly=true,routerWrites=false,nssPermissionGranted=false}))`;
const c=await connectRouter();try{const code='local OLD=[====['+take(old)+']====]\nlocal NEW=[====['+take(source)+']====]\n'+fixture;const e=encode("/usr/bin/lua - <<'NSS71_RESERVE_RAM'\n"+code+"\nNSS71_RESERVE_RAM\n");const raw=receipt(await c.run(e.command),e);fs.writeFileSync('work/nss71/reserve-raw-private.json',JSON.stringify(raw,null,2)+'\n',{flag:'wx'});assert.equal(raw.code,0,raw.stderr);const result=JSON.parse(raw.stdout);assert.ok(result.passed&&result.checks===7);const hash=x=>crypto.createHash('sha256').update(x).digest('hex');const proof={...result,observedAt:new Date().toISOString(),sourceSha256:hash(source),oldSourceSha256:hash(old),fullSourceExactlyOneAssertionRemoved:true,consumerAndLearningBarriersUnchanged:true};fs.writeFileSync('work/nss71/reserve-qualified.json',JSON.stringify(proof,null,2)+'\n',{flag:'wx'});const q=previous(),sourceManifest={};for(const f of ['classifier.lua','module-stage.mjs','current-audit-diagnostic.mjs','real-session.mjs','record-candidates.mjs','read-real-candidates.mjs','session-binding.mjs','change-contract.json','qualify-reserve.mjs','reserve-qualified.json'])sourceManifest['work/nss71/'+f]=hash(fs.readFileSync('work/nss71/'+f));fs.writeFileSync('work/nss71/entry-qualified.json',JSON.stringify({passed:true,baseBoundInputs:Object.keys(q.sourceManifest).length,readinessSetupReserveRemoved:true,learningBarrierUnchanged:true,sourceManifest},null,2)+'\n',{flag:'wx'});const checked=(await import('./session-binding.mjs')).verifyPreparation();console.log(JSON.stringify({...proof,boundInputs:Object.keys(checked.sourceManifest).length}));}finally{c.close()}
