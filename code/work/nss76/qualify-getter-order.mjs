import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';
import {connectRouter} from '../nss20/connect-router.mjs';import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';import {verifyPreparation as previous} from '../nss75/session-binding.mjs';
const root='work/nss76',fast=fs.readFileSync(root+'/fast-path.lua','utf8'),hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const getter=fast.slice(fast.indexOf(' local function getter('),fast.indexOf(' local function state()'));
const alignment=fast.slice(fast.indexOf(' local function alignLearning('),fast.indexOf(' function out.run('));assert.ok(getter.length>100&&alignment.length>500);
assert.ok(alignment.indexOf('record.preLearningGetter=getter')<alignment.indexOf('classifier.preLearningReady()'));
assert.ok(fast.includes("assert(now()<due-3 and now()-record.corePhase.observedAt<1.2,'Fresh learning margin lost after A')"));
assert.ok(fast.includes('now()-record.corePhase.observedAt<1.5 and now()<due-2.5'));
const fixture=String.raw`
local j=require('luci.jsonc');local cases={};local function yes(x,n)assert(x,n);cases[#cases+1]=n end
local clock,mode,record,P,phase,classifier,stopped,now,pause
local function reset(m)
 clock=100;mode=m;record={deadline=145};P={coreGuard={}}
 now=function()return clock end;pause=function(s)clock=clock+s end;stopped=function()end
 phase={scan=function()return{}end,waitFresh=function(g,scan,now,pause,ending)clock=clock+1;scan();return{observedAt=clock-(mode=='OLD_CORE'and 1 or 0)}end}
 classifier={preLearningReady=function()assert(record.preLearningGetter~=nil,'getter preceded final readiness '..mode);clock=clock+0.03;if mode=='MISSING_FLOW'then return false,'missing exact identity',false end;return true,nil,false end,
 resampleClosed=function()clock=clock+0.04;local age=(mode=='LATE_SOURCE'and 2.8 or 1);return{provenance={startedAtUptime=clock-age},flows={{validUntilUptime=clock+(mode=='SHORT_FLOW'and 3.2 or 6)},{validUntilUptime=clock+6}}}end}
end
__GETTER__
__ALIGNMENT__
local function live()
 clock=clock+0.45;local raw={nftables={}}
 for _,slot in ipairs({'tcp','udp'})do for _,d in ipairs({'up','down'})do for _,kind in ipairs({'total','expected','unexpected'})do
  local packets=kind=='unexpected'and 0 or 1;if mode=='BAD_TAG'and kind=='expected'then packets=2 end
  raw.nftables[#raw.nftables+1]={rule={comment='test:'..slot..'_post_'..d..'_'..kind,expr={{counter={packets=packets,bytes=packets*100}}}}}
 end end end
 raw.nftables[#raw.nftables+1]={rule={comment='test:udp_post_neighbor_nonzero',expr={{counter={packets=0,bytes=0}}}}};return raw
end
reset('FRESH');local fresh,due=alignLearning(live);yes(due-now()>3.25,'source reserve survives actual 450ms counter read');yes(now()-record.corePhase.observedAt<1.2,'old core barrier retained');yes(record.preLearningProofAt<now(),'live tag proof precedes classifier proof');yes(due<=fresh.provenance.startedAtUptime+6,'source never exceeds six seconds');
reset('LATE_SOURCE');local ok,e=pcall(alignLearning,live);yes(not ok and tostring(e):find('No joint fresh classifier/core phase'),'insufficient source margin cannot open');
reset('OLD_CORE');ok,e=pcall(alignLearning,live);yes(not ok and tostring(e):find('No joint fresh classifier/core phase'),'old core cannot open');
reset('SHORT_FLOW');ok,e=pcall(alignLearning,live);yes(not ok and tostring(e):find('No joint fresh classifier/core phase'),'short selected validity cannot open');
reset('MISSING_FLOW');ok,e=pcall(alignLearning,live);yes(not ok and tostring(e):find('Pre%-learning admission refused'),'identity rejection remains terminal');
reset('BAD_TAG');ok,e=pcall(alignLearning,live);yes(not ok and tostring(e):find('Tag getter mismatch'),'tag rejection still blocks learning');
print(j.stringify({passed=true,checks=#cases,cases=cases,ramOnly=true,routerWrites=false,nssPermissionGranted=false,actualGetterAndAlignmentExecuted=true,clockCoreAndClassifierMocked=true}))`;
const code=fixture.replace('__GETTER__',()=>getter).replace('__ALIGNMENT__',()=>alignment);
const c=await connectRouter();try{
 const e=encode("/usr/bin/lua - <<'NSS76_GETTER_RAM'\n"+code+"\nNSS76_GETTER_RAM\n");const r=receipt(await c.run(e.command),e);fs.writeFileSync(root+'/getter-v2-raw-private.json',JSON.stringify(r,null,2)+'\n',{flag:'wx'});assert.equal(r.code,0,r.stderr);const result=JSON.parse(r.stdout);assert.equal(result.passed,true);
 const compile=encode("/usr/bin/lua - <<'NSS76_FAST_COMPILE'\nassert(loadstring([====["+fast+"]====]));print('COMPILED')\nNSS76_FAST_COMPILE\n");const cr=receipt(await c.run(compile.command),compile);assert.equal(cr.code,0,cr.stderr);assert.equal(cr.stdout.trim(),'COMPILED');fs.writeFileSync(root+'/compile-raw-private.json',JSON.stringify(cr,null,2)+'\n',{flag:'wx'});
 const proof={...result,observedAt:new Date().toISOString(),fastPathSha256:hash(fast),getterBeforeFinalClassifierProof:true,fullFastPathSyntaxCompiled:true,nativeAndSixSecondExpiryUnchanged:true,baseBoundInputs:Object.keys(previous().sourceManifest).length,sourceManifest:{}};
 for(const f of ['fast-path.lua','payload.mjs','module-stage.mjs','real-session.mjs','current-audit-diagnostic.mjs','record-candidates.mjs','read-real-candidates.mjs','session-binding.mjs','change-contract.json','build-getter-order.mjs','qualify-getter-order.mjs'])proof.sourceManifest[root+'/'+f]=hash(fs.readFileSync(root+'/'+f));
 fs.writeFileSync(root+'/entry-qualified.json',JSON.stringify(proof,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({passed:true,checks:result.checks,boundInputs:Object.keys((await import('./session-binding.mjs')).verifyPreparation().sourceManifest).length,ramOnly:true,routerWrites:false}));
}finally{c.close()}
