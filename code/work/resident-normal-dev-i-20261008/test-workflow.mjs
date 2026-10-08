import fs from 'node:fs';import assert from 'node:assert/strict';import {normalPlan,normalWorkflow} from './workflow.mjs';
let checks=[];const test=async(name,fn)=>{await fn();checks.push(name);};
async function model(options={}){
 let t=1000,calls=0,reads=0,fixtures=0;const visited=[];
 const ops={now:()=>t,stopped:()=>options.stop===true||options.stopAfter===calls,wait:async()=>{t+=10;},observe:async()=>{reads++;if(options.readError)throw Error('read failure');return{pairs:options.empty?[]:[{}]};},
  runGeneration:async(g)=>{calls++;visited.push(g);t+=options.duration??220;return{code:options.failed===g?1:0,hardwareCompleted:options.failed!==g,restorationPassed:options.dirty!==g,nssSeconds:options.short?2:90};}};
 if(options.harness)ops.beforeObservation=async()=>{fixtures++;};
 const result=await normalWorkflow(ops);return{result,calls,reads,fixtures,visited};
}
await test('four normal generations without product fixture operations',async()=>{const r=await model();assert.equal(r.result.passed,true);assert.equal(r.calls,4);assert.equal(r.fixtures,0);assert.equal(r.result.controllerSeconds,900);assert.equal(r.result.nssSeconds,360);});
await test('empty normal traffic never writes or starts a generation',async()=>{const r=await model({empty:true});assert.equal(r.calls,0);assert.equal(r.fixtures,0);assert.equal(r.result.state,'NO_QUALIFYING_LOAD');assert.equal(r.result.passed,false);});
await test('dirty restore stops next admission',async()=>assert.rejects(model({dirty:1}),/P0/));
await test('refused generation is not automatically retried',async()=>{const r=await model({failed:1});assert.equal(r.calls,1);assert.equal(r.result.state,'REFUSED_RESTORED');});
await test('operator stop before generation',async()=>{const r=await model({stop:true});assert.equal(r.calls,0);assert.equal(r.result.state,'STOPPED');});
await test('operator stop after complete restore',async()=>{const r=await model({stopAfter:1});assert.equal(r.calls,1);assert.equal(r.result.state,'STOPPED');});
await test('new generation requires360sec cleanup margin',async()=>{const r=await model({duration:300});assert.equal(r.calls,3);assert.equal(r.result.state,'PARTIAL_SOAK_RESTORED');});
await test('repeated readonly refusal is bounded',async()=>{const r=await model({readError:true});assert.equal(r.reads,3);assert.equal(r.calls,0);assert.equal(r.result.state,'READ_REFUSED');});
await test('short active phase is not a successful soak',async()=>assert.rejects(model({short:true}),/P1/));
await test('separate external harness launches once per successful planned generation',async()=>{const r=await model({harness:true});assert.equal(r.fixtures,4);assert.equal(r.calls,4);});
await test('lifetime caps and no permanent NSS preserved',async()=>{assert.equal(normalPlan.sourceSeconds,6);assert.equal(normalPlan.kernelMaximumSeconds,120);assert.equal(normalPlan.ownerSeconds,180);assert.equal(normalPlan.clientSeconds,180);assert.equal(normalPlan.defaultPermanentNss,false);assert.equal(normalPlan.uninterruptedNssClaim,false);assert.equal(normalPlan.automaticFixtureRetries,0);});
const result={passed:true,checks,modelOnly:true,routerAccess:false,normalEntryCreatesTraffic:false,originalPerGenerationCapsPreserved:true};const file='work/resident-normal-dev-i-20261008/workflow-tests-'+Date.now()+'.json';fs.writeFileSync(file,JSON.stringify(result,null,2)+'\n',{flag:'wx'});fs.writeFileSync('work/resident-normal-dev-i-20261008/workflow-tests-latest.json',JSON.stringify({...result,file},null,2)+'\n');console.log(JSON.stringify({passed:true,checks:checks.length}));
