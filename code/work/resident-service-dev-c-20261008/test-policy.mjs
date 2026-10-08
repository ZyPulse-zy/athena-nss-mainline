import assert from 'node:assert/strict';import {residentLoop,servicePlan} from './policy.mjs';
const checks=[];async function test(name,fn){await fn();checks.push(name);}
async function model(options={}){
 let t=0,reads=0,calls=0,verified=0;const started=[],states=[];
 const result=await residentLoop({now:()=>t,stopped:()=>options.stopped===true||t>=(options.until??1500),wait:async()=>{t+=30;},
  publish:s=>states.push(structuredClone(s)),verify:()=>{verified++;if(options.bindingChanged)throw Error('Source changed');},
  observe:async()=>{reads++;if(options.readError)throw Error('Read refused');return{sourceAge:1,sourceSequence:reads,tcp:[{},{}],udp:[{}],pairs:options.empty?[]:[{}]};},
  runGeneration:async()=>{calls++;started.push(t);t+=100;const gone=options.candidateGone===true||(options.firstGone===true&&calls===1);return{code:options.refused||gone?1:0,hardwareCompleted:!options.refused&&!gone,restorationPassed:!options.dirty,nssSeconds:gone?0:options.short?5:90,safeCandidateDisappearedBeforeWrite:gone};}});
 return{result,started,states,reads,calls,verified};
}
await test('idle residency continues without creating traffic or NSS generations',async()=>{const m=await model({empty:true,until:2400});assert.equal(m.calls,0);assert.equal(m.reads,80);assert.equal(m.result.state,'STOPPED');});
await test('four starts per rolling20minute window then safe waiting',async()=>{const m=await model({until:1450});assert.equal(m.calls,6);assert.ok(m.started[4]-m.started[0]>=1200);for(const t of m.started)assert.ok(m.started.filter(x=>x<=t&&t-x<1200).length<=4);assert.ok(m.states.some(s=>s.state==='WAITING_WINDOW'));});
await test('new generation only after prior restoration returned',async()=>{const m=await model({until:1450});assert.equal(m.verified,m.calls);assert.equal(m.result.nssSeconds,540);});
await test('P0 restoration refusal stops further admission',async()=>assert.rejects(model({dirty:true}),/P0/));
await test('short successful phase is a targeted P1 refusal',async()=>assert.rejects(model({short:true}),/P1/));
await test('restored entry refusal latches admission without blind retry',async()=>{const m=await model({refused:true});assert.equal(m.calls,1);assert.ok(m.states.some(s=>s.state==='PAUSED_ENTRY_REFUSED'));});
await test('verified candidate loss returns to fresh normal observation',async()=>{const m=await model({firstGone:true,until:300});assert.equal(m.calls,3);assert.equal(m.result.generationsCompleted,2);assert.ok(m.states.some(s=>s.lastGeneration?.safeCandidateDisappearedBeforeWrite===true&&s.state==='WAITING_FLOW'&&s.admissionPaused===false));assert.ok(!m.states.some(s=>s.state==='PAUSED_ENTRY_REFUSED'));});
await test('repeated safe waits still obey original four-start window',async()=>{const m=await model({candidateGone:true,until:1199});assert.equal(m.calls,4);assert.equal(m.result.generationsCompleted,0);assert.ok(m.states.some(s=>s.state==='WAITING_WINDOW'));});
await test('safe-wait marker cannot bypass dirty restoration P0',async()=>assert.rejects(model({candidateGone:true,dirty:true}),/P0/));
await test('three read failures pause admission and cease router polling',async()=>{const m=await model({readError:true});assert.equal(m.reads,3);assert.equal(m.calls,0);assert.ok(m.states.some(s=>s.state==='PAUSED_SOURCE_UNAVAILABLE'));});
await test('changed binding pauses before calling entry',async()=>{const m=await model({bindingChanged:true});assert.equal(m.calls,0);assert.equal(m.verified,1);assert.ok(m.states.some(s=>s.state==='PAUSED_BINDING_CHANGED'));});
await test('stop request before work causes no source read or entry',async()=>{const m=await model({stopped:true});assert.equal(m.calls,0);assert.equal(m.reads,0);});
await test('stop during restored generation ends with no successor',async()=>{const m=await model({until:90});assert.equal(m.calls,1);assert.equal(m.result.state,'STOPPED');});
await test('stop during refused generation still requires restoration',async()=>{const m=await model({until:90,refused:true});assert.equal(m.calls,1);assert.equal(m.result.state,'STOPPED');});
await test('original per-generation bounds and no task auto restart preserved',async()=>{assert.deepEqual([servicePlan.phaseSeconds,servicePlan.sourceSeconds,servicePlan.kernelMaximumSeconds,servicePlan.ownerSeconds,servicePlan.clientSeconds],[90,6,120,180,180]);assert.equal(servicePlan.generationCutoffSeconds,600);assert.equal(servicePlan.minimumGenerationMarginSeconds,360);assert.equal(servicePlan.automaticFixtureRetries,0);assert.equal(servicePlan.normalEntryCreatesTraffic,false);assert.equal(servicePlan.automaticStartAtLogon,false);assert.equal(servicePlan.automaticRestartOnFailure,false);});
console.log(JSON.stringify({passed:true,checks:checks.length,names:checks,modelOnly:true,routerAccess:false}));
