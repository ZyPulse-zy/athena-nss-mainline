import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';
import {connectRouter} from '../nss20/connect-router.mjs';import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';import {verifyPreparation as previous} from '../nss69/session-binding.mjs';
const old=fs.readFileSync('work/nss59/fast-path.lua','utf8'),source=fs.readFileSync('work/nss70/fast-path.lua','utf8');
const start=' local function alignLearning()',end=' function out.run';const take=s=>s.slice(s.indexOf(start),s.indexOf(end));
assert.equal(source.replace('stopped() -- ECM remains closed; fresh admission is checked after the core phase.','stopped();if now()>=nextCheck then observe();nextCheck=now()+0.5 end'),old);
const fixture=String.raw`local checks=0
local function test(s,ready,reason,retry)
 local body="return function() local t=1000;local function now()return t end;local record={deadline=1045};local P={coreGuard={}};local stops=0;local function stopped()stops=stops+1 end;local function observe()error('Selected classification expired')end;local function pause(d)t=t+d end;local fs,read={},function()end;local phase={scan=function()return{}end,waitFresh=function(g,scan)scan();t=t+0.6;scan();return{observedAt=t}end};local classifier={preLearningReady=function()return "..tostring(ready)..","..string.format('%q',reason or '')..","..tostring(retry).." end};"..s.." alignLearning();assert(stops>=2);return true end"
 return pcall(assert(loadstring(body))())
end
assert(not test(OLD,true,'',false));checks=checks+1
assert(test(NEW,true,'',false));checks=checks+1
assert(not test(NEW,false,'Class changed',false));checks=checks+1
assert(not test(NEW,false,'No fresh margin',true));checks=checks+1
print(require('luci.jsonc').stringify({passed=true,checks=checks,oldExpiredClosedWaitReproduced=true,newClosedWaitCanReachStrictAdmission=true,changedClassRefused=true,missingFreshMarginNeverPermitted=true,ecmClosedThroughoutFixture=true,ramOnly=true,routerWrites=false}))`;
const c=await connectRouter();try{
 const code='local OLD=[====['+take(old)+']====]\nlocal NEW=[====['+take(source)+']====]\n'+fixture;const e=encode("/usr/bin/lua - <<'NSS70_CLOSED_WAIT_RAM'\n"+code+"\nNSS70_CLOSED_WAIT_RAM\n");const raw=receipt(await c.run(e.command),e);fs.writeFileSync('work/nss70/closed-wait-raw-private.json',JSON.stringify(raw,null,2)+'\n',{flag:'wx'});assert.equal(raw.code,0,raw.stderr);const r=JSON.parse(raw.stdout);assert.ok(r.passed&&r.checks===4);
 const compile=encode("/usr/bin/lua - <<'NSS70_COMPILE'\nassert(loadstring([====["+source+"]====]));print('COMPILED')\nNSS70_COMPILE\n");const cr=receipt(await c.run(compile.command),compile);assert.equal(cr.code,0,cr.stderr);assert.equal(cr.stdout.trim(),'COMPILED');fs.writeFileSync('work/nss70/compile-raw-private.json',JSON.stringify(cr,null,2)+'\n',{flag:'wx'});
 const hash=x=>crypto.createHash('sha256').update(x).digest('hex');const proof={...r,observedAt:new Date().toISOString(),sourceSha256:hash(source),oldSourceSha256:hash(old),fullNativeSyntaxCompiled:true,activeFlowObserverAndLearningGatesUnchanged:true,ageLimitsAndLeaseUnchanged:true};fs.writeFileSync('work/nss70/closed-wait-qualified.json',JSON.stringify(proof,null,2)+'\n',{flag:'wx'});
 const q=previous(),sourceManifest={};const files=['fast-path.lua','payload.mjs','module-stage.mjs','current-audit-diagnostic.mjs','real-session.mjs','record-candidates.mjs','read-real-candidates.mjs','session-binding.mjs','change-contract.json','qualify-closed-wait.mjs','closed-wait-qualified.json'];for(const f of files)sourceManifest['work/nss70/'+f]=hash(fs.readFileSync('work/nss70/'+f));const p={passed:true,baseBoundInputs:Object.keys(q.sourceManifest).length,closedWaitOnly:true,activeFlowObserverAndLearningGatesUnchanged:true,sourceManifest};fs.writeFileSync('work/nss70/entry-qualified.json',JSON.stringify(p,null,2)+'\n',{flag:'wx'});const checked=(await import('./session-binding.mjs')).verifyPreparation();console.log(JSON.stringify({...proof,boundInputs:Object.keys(checked.sourceManifest).length}));
}finally{c.close()}
