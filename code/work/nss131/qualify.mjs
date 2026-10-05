import fs from'node:fs';import assert from'node:assert/strict';import crypto from'node:crypto';import{spawnSync}from'node:child_process';
import{verifyPreparation as previous}from'../nss129/session-binding.mjs';
import{connectRouter}from'../nss27/connect-router.mjs';import{encode,receipt}from'../nss11/v7-observe-repair/observe2/transport.mjs';
import{buildPayload}from'./payload.mjs';import{mapClassifiedPair}from'../nss127/class-leaf-map.mjs';import{packetTemplate}from'./uplink-tag-plan.mjs';import{validateAcceleratedState}from'./parse-ecm-any-wan.mjs';
import{packLua,tokens}from'./pack-lua.mjs';
const root='work/nss131',h=b=>crypto.createHash('sha256').update(b).digest('hex'),old=previous(),checks=[];
const adapter=fs.readFileSync(root+'/classifier.lua','utf8'),before=fs.readFileSync('work/nss73/classifier.lua','utf8');
const cut=s=>s.slice(s.indexOf('local Consumer=(function()')+'local Consumer=(function()'.length,s.indexOf('\nend)()\nlocal describeSelection'));
assert.equal(cut(adapter),cut(before));checks.push({name:'original-admission-and-epoch-comparator-byte-exact',passed:true});
for(const f of['module-stage-guardian.lua','qos-physical.lua','tag-normalizer.lua','bounded-pacer.mjs'])assert.equal(h(fs.readFileSync(root+'/'+f)),h(fs.readFileSync('work/nss128/'+f)));checks.push({name:'same-native-owner-queues-tags-and-bounded-pacer',passed:true});
const caseDir='work/nss128/controlled-matched-aba-20261005205520-95105879',record=JSON.parse(fs.readFileSync(caseDir+'/last-record-private.json')),selected=JSON.parse(fs.readFileSync(caseDir+'/selected-private.json'));
validateAcceleratedState(record.acceleratedState,selected);
const udpSerial=validateAcceleratedState(record.acceleratedState,selected).proof.udp.serial;
const udpRaw=record.acceleratedState.split('\n').filter(l=>l.startsWith('conns.conn.'+udpSerial+'.')).join('\n')+'\n';validateAcceleratedState(udpRaw,selected,true);
assert.throws(()=>validateAcceleratedState(record.acceleratedState,selected,true));assert.throws(()=>validateAcceleratedState(udpRaw.replace('accel_mode=2','accel_mode=0'),selected,true));checks.push({name:'single-udp-validator-reuses-exact-NAT-mark-affinity-and-tags',passed:true,historicalActualFrameReplay:true,syntheticSingleRemoval:true});
const fast=fs.readFileSync(root+'/fast-path.lua','utf8'),a=fast.indexOf('function M.verifyReclassification('),b=fast.indexOf('function M.new(',a);assert.ok(a>0&&b>a);
for(const s of["local a=1 .. 2;return a", "return 1e-3 + .5", "return 'x--y'..\"q\\\"z\"", 'return 1 - -2 -- comment\n', "local f=function()return 3 end;return f()"]){assert.deepEqual(tokens(packLua(s)),tokens(s));}assert.throws(()=>packLua('return [=[raw]=]'));assert.throws(()=>packLua("return 'unterminated"));checks.push({name:'lexical-packing-preserves-string-number-and-operator-tokens',passed:true});
const d=adapter.slice(adapter.indexOf('local describeSelection=(function()')+'local describeSelection=(function()'.length,adapter.indexOf('\nend)()\nlocal A='));
const prefix=fs.readFileSync('work/nss23/consumer-fixtures.lua','utf8').split('local s,c,w=make();local epoch=')[0].replace("local M=assert(loadstring([===[__CONSUMER__]===]))()",'');
const da=adapter.indexOf(' local function diagnose('),db=adapter.indexOf(' function out.ready()',da);const diagnostic=adapter.slice(da,db);
const models=String.raw`
local Consumer=M;local P={};local ram='/tmp/mock';local complete;local reads=0
local function stable()reads=reads+1;return j.stringify(complete)end
local function now()return 101.12 end
${diagnostic}
local function setup()
 local s,c,w=make();P.selected=w;complete=j.parse(j.stringify(s));s.snapshot.admissionProjection={scope='bulk-and-admitted-rt'};return s,c,w
end
local s,c,w=setup();local epoch=M.pair(complete,c,now(),w);table.remove(s.snapshot.flows,1);local f=complete.snapshot.flows[1];f.decision.class='BE';f.decision.reason='cooldown';f.decision.budgetAdmitted=false;f.leaf.class='BE';f.leaf.candidate=false;f.leaf.downTag=0
local t={};diagnose(s,c,now(),t);local comp=M.compareEpoch(epoch,s,c,now());comp.evidence=t
M.verifyReclassification(comp,complete.producer);yes(comp.affected[1]=='tcp'and #comp.affected==1,'only changed TCP is affected');yes(t.completeSelected.authenticatedSelectedFlows[1].decision.class=='BE','actual complete selected class retained');yes(not t.completeSelected.nssAdmissionAllowed,'complete diagnostic never authorizes relearning')
for _,kind in ipairs({'missing','unknown','wrongreason','udp','producer','identity','expired'})do
 local x=j.parse(j.stringify(comp));if kind=='missing'then x.evidence.completeSelected=nil elseif kind=='unknown'then x.evidence.completeSelected.slots.tcp.class='UNKNOWN'elseif kind=='wrongreason'then x.evidence.completeSelected.slots.tcp.reason='warming'elseif kind=='udp'then x.affected={'tcp','udp'}elseif kind=='producer'then x.evidence.completeSelected.producer='other'elseif kind=='identity'then x.evidence.completeSelected.slots.tcp.ctMatches=false else x.evidence.completeSelected.slots.udp.validRemainingSeconds=0 end
 yes(not pcall(M.verifyReclassification,x,complete.producer),'retirement evidence refuses '..kind)
end
s,c,w=setup();table.remove(s.snapshot.flows,1);complete.snapshot.provenance.sequence=complete.snapshot.provenance.sequence+1;t={};diagnose(s,c,now(),t);yes(t.completeSelected==nil and t.completeSelectionUnavailable~=nil,'different complete query remains unknown')
s,c,w=setup();table.remove(s.snapshot.flows,1);complete.producer='foreign';t={};diagnose(s,c,now(),t);yes(t.completeSelected==nil,'different complete producer remains unknown')
print(j.stringify({passed=true,checks=#cases,cases=cases,ramOnly=true,mockedInputs=true,routerWrites=false,nssAdmissionAllowed=false}))`;
const c=await connectRouter();let native;
try{
 const script='local M=(function()'+cut(adapter)+'\nend)();\n'+fast.slice(a,b)+'local describeSelection=(function()'+d+'\nend)()\n'+prefix+models;
 const e=encode("lua - <<'NSS131_COMPLETE_RETIRE_MODELS'\n"+script+"\nNSS131_COMPLETE_RETIRE_MODELS\n");const raw=receipt(await c.run(e.command),e);fs.writeFileSync(root+'/retirement-model-v2-raw-private.json',JSON.stringify(raw,null,2)+'\n',{flag:'wx'});assert.equal(raw.code,0,raw.stderr);native=JSON.parse(raw.stdout);assert.ok(native.passed&&native.checks===12);checks.push({name:'complete-same-query-retirement-policy-models',passed:true,nativeRamChecks:native.checks});
 const lexFixtures="local x=assert(loadstring([====["+packLua("local a=1 .. 2;local b=1 - -2;local c='x--y';return a,b,c")+"]====]));local a,b,c=x();assert(a=='12'and b==3 and c=='x--y');";
 const e2=encode("lua - <<'NSS131_FAST_SYNTAX'\nassert(loadstring([====["+packLua(fast)+"]====]));"+lexFixtures+"print('COMPILED')\nNSS131_FAST_SYNTAX\n");const raw2=receipt(await c.run(e2.command),e2);fs.writeFileSync(root+'/fast-syntax-v2-private.json',JSON.stringify(raw2,null,2)+'\n',{flag:'wx'});assert.equal(raw2.code,0,raw2.stderr);checks.push({name:'actual-target-packed-fast-and-lexical-fixtures-compile',passed:true});
}finally{c.close()}
const frame=JSON.parse(fs.readFileSync(caseDir+'/post-checkpoint-controlled-receipt-private.json')),mapping=mapClassifiedPair(frame,selected),plan=packetTemplate(mapping,'a'.repeat(32),59999);plan.expected.nftables=plan.expected.nftables.filter(x=>x.chain?.name!=='forward'&&x.rule?.chain!=='forward');
const helpers={qos:fs.readFileSync(root+'/qos-physical.lua','utf8'),phase:fs.readFileSync('work/nss69/core-guard-phase.lua','utf8'),classifier:adapter,tags:fs.readFileSync('work/nss49/classified-tags.lua','utf8'),normalizer:fs.readFileSync(root+'/tag-normalizer.lua','utf8')},payload=buildPayload({tagPlan:{table:plan.expected.nftables[0].table.name,owner:'a'.repeat(32),mode:'rt',expected:plan.expected}},helpers);assert.ok(Buffer.byteLength(payload.stagedCode)<=73728);checks.push({name:'complete-guarded-bundle-within-original-byte-budget',passed:true,payloadBytes:Buffer.byteLength(payload.stagedCode)});
for(const name of fs.readdirSync(root).filter(x=>x.endsWith('.mjs'))){const p=spawnSync(process.execPath,['--check',root+'/'+name],{encoding:'utf8',windowsHide:true});assert.equal(p.status,0,p.stderr);}
const sourceManifest={};for(const name of fs.readdirSync(root))if(/\.(mjs|py|lua|ps1)$/.test(name)&&!name.includes('private'))sourceManifest[root+'/'+name]=h(fs.readFileSync(root+'/'+name));
const result={passed:true,productionExecution:false,retirementOnlyCompleteFrame:true,productionPairStillRestrictedToTcpBulkUdpRt:true,classifierMaximumLeaseSeconds:6,nativeSessionSeconds:27,independentOwnerSeconds:100,payloadBytes:Buffer.byteLength(payload.stagedCode),sourceManifest,inheritedBoundInputs:Object.keys(old.sourceManifest).length,checks,nativeModels:native};fs.writeFileSync(root+'/entry-qualified.json',JSON.stringify(result,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({passed:true,checks:checks.length,nativeModelChecks:native.checks,sourceBindings:Object.keys(sourceManifest).length,payloadBytes:result.payloadBytes,productionExecution:false}));
