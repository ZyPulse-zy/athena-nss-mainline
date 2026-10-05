import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';import {connectRouter} from '../nss20/connect-router.mjs';import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';import {verifyPreparation as previous} from '../nss76/session-binding.mjs';
const root='work/nss77',fast=fs.readFileSync(root+'/fast-path.lua','utf8'),hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const actual=fast.slice(fast.indexOf(' function out.align('),fast.indexOf(' local function alignLearning('));assert.ok(actual.length>500);
const old=fs.readFileSync('work/nss76/fast-path.lua','utf8');const addition="\n   if ready then\n    local source=assert(record.lastAdmissionProbe and record.lastAdmissionProbe.source,'Missing readiness provenance')\n    assert(type(source.startedAtUptime)=='number')\n    if at>=source.startedAtUptime+1.65 then ready=false;reason='Tag publication setup margin insufficient';retryable=true end\n   end";
assert.equal(fast.replace(addition,''),old);assert.ok(actual.includes('math.min(now()+9,deadline-32)'));
const fixture=String.raw`
local j=require('luci.jsonc');local cases={};local function yes(x,n)assert(x,n);cases[#cases+1]=n end
local clock=100;local mode;local reads;local out={};local record,P,now,pause,stopped,command,phase,classifier,fs,read
local function reset(m)
 clock=100;mode=m;reads=0;record={};P={openFrontend=true,coreGuard={sha256='abc123'}}
 now=function()return clock end;pause=function(s)clock=clock+s end;stopped=function()end;command=function()return'abc123 'end
 phase={scan=function()clock=clock+0.02;return{}end};classifier={preLearningReady=function()
  reads=reads+1;clock=clock+0.03;local age=(mode=='LATE'and 2.94 or mode=='BOUNDARY'and 1.65 or mode=='NEXT'and reads==1 and 2.94 or 0.8)
  record.lastAdmissionProbe={source={startedAtUptime=clock-age},sourceAge=age}
  if mode=='MISSING'then record.lastAdmissionProbe={}end
  if mode=='TERMINAL'then return false,'exact identity missing',false end
  return true,nil,false
 end}
end
__ACTUAL__
reset('FRESH');out.align(145);yes(#record.initialAlignment.probes==1 and record.initialAlignment.probes[1][2],'fresh input proceeds');yes(record.initialAlignment.stop==109,'old nine-second initial wait remains');
reset('LATE');local ok,e=pcall(out.align,145);yes(not ok and tostring(e):find('Insufficient fresh%-classifier margin'),'actual NSS76 age 2.94s is rejected before tag setup');yes(record.initialAlignment.probes[1][4]==true,'late source is retryable only while closed');
reset('BOUNDARY');ok,e=pcall(out.align,145);yes(not ok,'exact 1.65s boundary refused');
reset('NEXT');out.align(145);yes(#record.initialAlignment.probes==2,'new fresh publication accepted after old source refused');yes(record.initialAlignment.probes[1][2]==false and record.initialAlignment.probes[2][2]==true,'no stale source promoted');
reset('MISSING');ok,e=pcall(out.align,145);yes(not ok and tostring(e):find('Missing readiness provenance'),'missing source is terminal');
reset('TERMINAL');ok,e=pcall(out.align,145);yes(not ok and reads==1 and tostring(e):find('Initial admission refused'),'identity rejection not retried');
print(j.stringify({passed=true,checks=#cases,cases=cases,ramOnly=true,routerWrites=false,nssPermissionGranted=false,actualInitialAlignmentExecuted=true,ioClockAndClassifierMocked=true,actualNss76AgeReplayed=2.94}))`;
const c=await connectRouter();try{
 const code=fixture.replace('__ACTUAL__',()=>actual);const e=encode("/usr/bin/lua - <<'NSS77_INITIAL_RAM'\n"+code+"\nNSS77_INITIAL_RAM\n");const r=receipt(await c.run(e.command),e);fs.writeFileSync(root+'/initial-v3-raw-private.json',JSON.stringify(r,null,2)+'\n',{flag:'wx'});assert.equal(r.code,0,r.stderr);const result=JSON.parse(r.stdout);assert.equal(result.passed,true);
 const compile=encode("/usr/bin/lua - <<'NSS77_FAST_COMPILE'\nassert(loadstring([====["+fast+"]====]));print('COMPILED')\nNSS77_FAST_COMPILE\n");const cr=receipt(await c.run(compile.command),compile);assert.equal(cr.code,0,cr.stderr);assert.equal(cr.stdout.trim(),'COMPILED');fs.writeFileSync(root+'/compile-raw-private.json',JSON.stringify(cr,null,2)+'\n',{flag:'wx'});
 const proof={...result,observedAt:new Date().toISOString(),fastPathSha256:hash(fast),fullFastPathSyntaxCompiled:true,initialTagPublicationReserveAligned:true,originalTagAndNativeDeadlinesUnchanged:true,baseBoundInputs:Object.keys(previous().sourceManifest).length,sourceManifest:{}};
 for(const f of ['fast-path.lua','payload.mjs','module-stage.mjs','real-session.mjs','current-audit-diagnostic.mjs','record-candidates.mjs','read-real-candidates.mjs','session-binding.mjs','change-contract.json','build-initial-reserve.mjs','qualify-initial-reserve.mjs'])proof.sourceManifest[root+'/'+f]=hash(fs.readFileSync(root+'/'+f));
 fs.writeFileSync(root+'/entry-qualified.json',JSON.stringify(proof,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({passed:true,checks:result.checks,boundInputs:Object.keys((await import('./session-binding.mjs')).verifyPreparation().sourceManifest).length,ramOnly:true,routerWrites:false}));
}finally{c.close()}
