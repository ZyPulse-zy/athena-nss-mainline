import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';
import {connectRouter} from '../nss20/connect-router.mjs';import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
import {verifyPreparation as previous} from '../nss72/session-binding.mjs';
const root='work/nss73',adapter=fs.readFileSync(root+'/classifier.lua','utf8'),fast=fs.readFileSync(root+'/fast-path.lua','utf8'),old=fs.readFileSync('work/nss72/classifier.lua','utf8');
const cut=s=>s.slice(s.indexOf('local Consumer=(function()')+'local Consumer=(function()'.length,s.indexOf('\nend)()\nlocal describeSelection'));
const strip=s=>s.split('\n').filter(l=>!/^\s*--/.test(l)).join('\n');assert.equal(cut(adapter),strip(cut(old)));
const d=old.slice(old.indexOf('local describeSelection=(function()')+'local describeSelection=(function()'.length,old.indexOf('\nend)()\nlocal A='));
const prefix=fs.readFileSync('work/nss23/consumer-fixtures.lua','utf8').split('local s,c,w=make();local epoch=')[0].replace("local M=assert(loadstring([===[__CONSUMER__]===]))()",'');
const helper=fs.readFileSync(root+'/diagnostic-helper.lua','utf8');
const fixture=String.raw`
local Consumer=M;local P={};local record={};local ram='/tmp/mock';local complete;local reads=0
local function stable()reads=reads+1;return j.stringify(complete)end
local function now()return 101.12 end
${helper}
local function setup()
 local s,c,w=make();P.selected=w;complete=j.parse(j.stringify(s));s.snapshot.admissionProjection={scope='bulk-and-admitted-rt'};return s,c,w
end
local s,c,w=setup();table.remove(s.snapshot.flows,1);local f=complete.snapshot.flows[1];f.decision.class='BE';f.decision.reason='cooldown';f.decision.budgetAdmitted=false;f.leaf.class='BE';f.leaf.candidate=false;f.leaf.downTag=0;local t={};diagnose(s,c,now(),t)
yes(t.selected.slots.tcp.reasonCode=='NOT_IN_ADMISSION_PROJECTION','projection absence is not CT exit');yes(t.completeSelected.slots.tcp.present and t.completeSelected.slots.tcp.reason=='cooldown','same-source complete diagnostic reveals excluded class');yes(t.completeSelected.slots.tcp.ctMatches and t.completeSelected.slots.tcp.markMatches,'diagnostic preserves identity facts');yes(not t.completeSelected.nssAdmissionAllowed,'diagnostic never grants admission');yes(reads==1,'complete frame read once after rejection')
s,c,w=setup();table.remove(s.snapshot.flows,1);complete.snapshot.provenance.sequence=complete.snapshot.provenance.sequence+1;t={};diagnose(s,c,now(),t);yes(t.completeSelected==nil and t.completeSelectionUnavailable~=nil,'different source remains unknown')
s,c,w=setup();t={};local before=reads;diagnose(s,c,now(),t);yes(reads==before and t.completeSelected==nil,'no full frame read when projection contains both slots')
print(j.stringify({passed=true,checks=#cases,cases=cases,ramOnly=true,ioTimeAndInputsMocked=true,routerWrites=false,nssPermissionGranted=false}))`;
const c=await connectRouter();try{
 const e=encode("/usr/bin/lua - <<'NSS73_DIAGNOSTIC_RAM'\nlocal M=(function()"+cut(adapter)+'\nend)();local describeSelection=(function()'+d+'\nend)()\n'+prefix+fixture+"\nNSS73_DIAGNOSTIC_RAM\n");const r=receipt(await c.run(e.command),e);fs.writeFileSync(root+'/diagnostic-recheck-raw-private.json',JSON.stringify(r,null,2)+'\n',{flag:'wx'});assert.equal(r.code,0,r.stderr);const p=JSON.parse(r.stdout);assert.ok(p.passed&&p.checks===7);
 let adapterDeferred=false;for(const[name,s]of[['fast',fast],['adapter',adapter]]){let x;try{x=encode("/usr/bin/lua - <<'NSS73_COMPILE'\nassert(loadstring([====["+s+"]====]));print('COMPILED')\nNSS73_COMPILE\n");}catch(error){assert.equal(name,'adapter');assert.equal(String(error),'Error: Transport length refused');adapterDeferred=true;continue;}const rr=receipt(await c.run(x.command),x);assert.equal(rr.code,0,rr.stderr);assert.equal(rr.stdout.trim(),'COMPILED');}
 const hash=s=>crypto.createHash('sha256').update(s).digest('hex');fs.writeFileSync(root+'/diagnostic-qualified.json',JSON.stringify({...p,observedAt:new Date().toISOString(),consumerAdmissionByteEquivalentIgnoringWholeLineComments:true,adapterSha256:hash(adapter),fastPathSha256:hash(fast),fullFastSourceCompiled:true,adapterSyntaxDeferredToExactGuardedBundle:adapterDeferred,transportLimitsUnchanged:true},null,2)+'\n',{flag:'wx'});
 const sourceManifest={};for(const f of ['classifier.lua','fast-path.lua','payload.mjs','module-stage.mjs','current-audit-diagnostic.mjs','real-session.mjs','record-candidates.mjs','read-real-candidates.mjs','session-binding.mjs','change-contract.json','diagnostic-helper.lua','qualify-diagnostic.mjs','diagnostic-qualified.json'])sourceManifest[root+'/'+f]=hash(fs.readFileSync(root+'/'+f));fs.writeFileSync(root+'/entry-qualified.json',JSON.stringify({passed:true,diagnosticOnly:true,noDiagnosticResultAffectsAdmission:true,baseBoundInputs:Object.keys(previous().sourceManifest).length,sourceManifest},null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({passed:true,checks:p.checks,boundInputs:Object.keys((await import('./session-binding.mjs')).verifyPreparation().sourceManifest).length}));
}finally{c.close()}
