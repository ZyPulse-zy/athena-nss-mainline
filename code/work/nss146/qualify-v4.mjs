import fs from'node:fs';import assert from'node:assert/strict';import crypto from'node:crypto';import{spawnSync}from'node:child_process';
import{verifyPreparation as prior}from'../nss145/session-binding.mjs';
import{tokens,packLua}from'./pack-lua.mjs';import{packGuardian}from'./pack-guardian.mjs';import{buildPayload}from'./payload.mjs';
import{packetTemplate}from'./uplink-tag-plan.mjs';import{mapClassifiedPair}from'../nss127/class-leaf-map.mjs';
import{connectRouter}from'../nss27/connect-router.mjs';import{encode,receipt}from'../nss11/v7-observe-repair/observe2/transport.mjs';
const root='work/nss146',h=b=>crypto.createHash('sha256').update(b).digest('hex'),q=prior();
const fast=fs.readFileSync(root+'/fast-path.lua','utf8'),consumer=fs.readFileSync(root+'/classifier.lua','utf8');
assert.equal(fast.replace("if not active then stopped()end\n  local frame=A.observe();local C=A.compareObserved(not active)","local frame=A.observe();local C=A.compareObserved()").replace("if C.action~='KEEP_IMMUTABLE_EPOCH'then\n   R.rejectedComparison=C","if C.action~='KEEP_IMMUTABLE_EPOCH'then"),fs.readFileSync('work/nss140/fast-path.lua','utf8'));
assert.equal(consumer.replace('function M.compareEpoch(epoch,s,c,now,closed)','function M.compareEpoch(epoch,s,c,now)').replace('or(not closed and now>=epoch.epochUntil)then','or now>=epoch.epochUntil then').replace('function out.compareObserved(closed)','function out.compareObserved()').replace('Consumer.compareEpoch(epoch,out.lastObservedSnapshot,out.lastObservedContext,now(),closed)','Consumer.compareEpoch(epoch,out.lastObservedSnapshot,out.lastObservedContext,now())'),fs.readFileSync('work/nss140/classifier.lua','utf8'));
for(const name of['qos-physical.lua','tag-normalizer.lua','module-stage-guardian.lua','pack-lua.mjs','pack-guardian.mjs','compact-default-queues.mjs','uplink-tag-plan.mjs','parse-ecm-any-wan.mjs','failed-wan-owner.lua','declared-baseline.mjs','service-epoch.mjs'])assert.equal(h(fs.readFileSync(root+'/'+name)),h(fs.readFileSync('work/nss140/'+name)),name);
const oldCase='work/nss145/controlled-matched-aba-20261006024853-c64cba7b';
const frame=JSON.parse(fs.readFileSync(oldCase+'/post-checkpoint-controlled-receipt-private.json'));
const plan=JSON.parse(fs.readFileSync(oldCase+'/stage-plan-private.json'));
const selected=structuredClone(plan.selected);for(const f of Object.values(selected))delete f.classifierKey;
const mapped=mapClassifiedPair(frame,selected),template=packetTemplate(mapped,plan.tagPlan.owner,plan.selected.udp.original.sport===59999?59998:59999);
template.expected.nftables=template.expected.nftables.filter(x=>x.chain?.name!=='forward'&&x.rule?.chain!=='forward');
const input={tagPlan:{table:template.expected.nftables[0].table.name,owner:plan.tagPlan.owner,mode:'rt',expected:template.expected}};
const helpers={qos:fs.readFileSync(root+'/qos-physical.lua','utf8'),phase:fs.readFileSync('work/nss69/core-guard-phase.lua','utf8'),classifier:consumer,tags:fs.readFileSync('work/nss49/classified-tags.lua','utf8'),normalizer:fs.readFileSync(root+'/tag-normalizer.lua','utf8')};
const payload=buildPayload(input,helpers),payloadBytes=Buffer.byteLength(payload.stagedCode);assert.ok(payloadBytes<=73728,'Original payload budget exceeded');
for(const k of['guardianSourceSha256','selectedGuardianSha256','oneEpochControlledPair','phaseSourceSha256','qosSourceSha256','execBytes'])delete plan[k];
plan.qosCodeBytes=payloadBytes;plan.qosCodeSha256=h(payload.stagedCode);
const guardian=packGuardian(fs.readFileSync(root+'/module-stage-guardian.lua','utf8')).replace('__PLAN__',()=>JSON.stringify(plan)).replace('__CORE_PHASE__',()=> 'return{}').replace('__QOS_PHYSICAL__',()=> 'return{}');
const ge=encode("/usr/bin/lua - <<'NSS20_STAGE_BEGIN'\n"+guardian+"\nNSS20_STAGE_BEGIN\n");assert.ok(ge.execBytes<=9000);
const cut=(text,a,b)=>text.slice(text.indexOf(a),text.indexOf(b,text.indexOf(a)));
const consumerPart=consumer.slice(0,consumer.indexOf('local describeSelection='));
const prefix=consumer.slice(consumer.indexOf('local function int('),consumer.indexOf('function M.inspect('));
const pairAndCompare=cut(consumer,'function M.pair(','\nreturn M').replaceAll('M.pair','Consumer.pair').replaceAll('M.compareEpoch','Consumer.compareEpoch').replaceAll('M.inspect','Consumer.inspect');
const fixtureInspector="function Consumer.inspect(s,c,t)local p=s.snapshot.provenance;assert(t<p.startedAtUptime+6);local flows={};for _,f in ipairs(s.snapshot.flows)do if f.leaf.candidate then flows[#flows+1]=f end end;return{candidates=flows,producer=s.producer,provenance=p}end";
const modelConsumer='local Consumer={};'+prefix+fixtureInspector+pairAndCompare;
const model=fs.readFileSync(root+'/phase-models.lua','utf8')
 .replace('__CONSUMER__',()=>modelConsumer)
 .replace('__VERIFY_RENEWAL__',()=>cut(fast,'function M.verifyRenewalAck(','function M.verifyReclassification('))
 .replace('__SAMPLE__',()=>cut(fast,' local function S()',' local function observe()'))
 .replace('__OBSERVE__',()=>cut(fast,' local function observe()',' local function counters(raw)'))
 .replace('__RENEW__',()=>cut(fast,' local function X(O)',' retire=function(C)'))
 .replace('__TICK_MEASURE__',()=>cut(fast,' local function tick(name)',' function out.align(deadline)'));
const code="local j=require('luci.jsonc');\n"+model;
fs.writeFileSync(root+'/phase-models-rendered-v4-private.lua',code,{flag:'wx'});
let enc;try{enc=encode("lua - <<'NSS146_PHASE_RAM'\n"+code+"\nNSS146_PHASE_RAM\n")}catch(error){fs.writeFileSync(root+'/phase-model-v4-size-refusal.json',JSON.stringify({error:String(error),rawBytes:Buffer.byteLength(code),beforeRouterConnection:true},null,2));throw error;}
const consumerCode="local j=require('luci.jsonc');\n"+fs.readFileSync(root+'/consumer-models.lua','utf8').replace('__CONSUMER__',()=>packLua(consumerPart));
const ce=encode("lua - <<'NSS146_ACTUAL_CONSUMER_RAM'\n"+consumerCode+"\nNSS146_ACTUAL_CONSUMER_RAM\n");
const c=await connectRouter();let models,consumerModels;
try{const cr=receipt(await c.run(ce.command),ce);fs.writeFileSync(root+'/consumer-models-raw-private.json',JSON.stringify(cr,null,2)+'\n',{flag:'wx'});assert.equal(cr.code,0,cr.stderr);consumerModels=JSON.parse(cr.stdout);assert.ok(consumerModels.passed&&consumerModels.checks===8);const raw=receipt(await c.run(enc.command),enc);fs.writeFileSync(root+'/phase-models-v4-raw-private.json',JSON.stringify(raw,null,2)+'\n',{flag:'wx'});assert.equal(raw.code,0,raw.stderr);models=JSON.parse(raw.stdout);assert.ok(models.passed&&models.checks===9);}finally{c.close()}
const sourceManifest={};for(const name of fs.readdirSync(root))if(/\.(mjs|py|ps1|lua)$/.test(name)&&!name.includes('private')){
 const file=root+'/'+name;sourceManifest[file]=h(fs.readFileSync(file));if(name.endsWith('.mjs')){const p=spawnSync(process.execPath,['--check',file],{encoding:'utf8',windowsHide:true});assert.equal(p.status,0,p.stderr);}
 if(name.endsWith('.py')){const p=spawnSync('C:/Users/lishu/AppData/Local/Programs/Python/Python312/python.exe',['-c','import sys;compile(open(sys.argv[1],encoding="utf-8").read(),sys.argv[1],"exec")',file],{encoding:'utf8',windowsHide:true});assert.equal(p.status,0,p.stderr);}
}
const proof={passed:true,at:new Date().toISOString(),controlledCurrentFactory:true,nativePayloadUnchanged:false,
 controlledClosedPhaseCorrection:true,inheritedBoundInputs:Object.keys(q.sourceManifest).length,sourceManifest,
 budgets:[6,27,100,9000,65536,73728],payloadBytes,qualificationGuardianExecBytes:ge.execBytes,
 modelExecBytes:enc.execBytes,changedSoftwarePhaseLoopsExecutedWithMockedBackend:true,actualConsumerAndPhaseFunctions:true,wholeFactoryAbaExecutedWithMockedBackend:false,
 models,consumerModels,completeActualConsumerTestedSeparately:true,phaseInspectorMockedExplicitly:true,activeNativeExpiryUnchanged:true,freshSourceAndIdentityChecksUnchanged:true,
 closedHardwareStoppedAndAllEcmZeroRequired:true,oneTcpOneUdp:true,offeredDownloadMbps:32,
 desktopOperated:false,productionExecution:false,currentHardwareAbaCompleted:false};
fs.writeFileSync(root+'/entry-qualified.json',JSON.stringify(proof,null,2)+'\n',{flag:'wx'});
const qualified=(await import('./session-binding.mjs')).verifyPreparation();
console.log(JSON.stringify({passed:true,bindings:Object.keys(qualified.sourceManifest).length,payloadBytes,guardianExecBytes:ge.execBytes,modelExecBytes:enc.execBytes,changedPhaseModelChecks:models.checks,actualConsumerChecks:consumerModels.checks,routerWrites:false}));
