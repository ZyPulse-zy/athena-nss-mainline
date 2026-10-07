import fs from 'node:fs';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {soakPlan,soakWorkflow} from './soak-workflow.mjs';
let checks=0;
async function run(options={}){
 let t=1000,calls=0;const visited=[];
 const result=await soakWorkflow({now:()=>t,stopped:()=>options.stop===true||options.stopAfter===calls,
  wait:async()=>{t++;},runGeneration:async n=>{calls++;visited.push(n);t+=options.duration??240;
   return{code:options.failed===n?1:0,restorationPassed:options.dirty!==n,hardwareCompleted:options.failed!==n,nssSeconds:90};}});
 return{result,calls,visited};
}
let r=await run();assert.equal(r.result.passed,true);assert.deepEqual(r.visited,[1,2]);assert.equal(r.result.controllerSeconds,480);checks++;
r=await run({failed:1});assert.equal(r.result.state,'REFUSED_RESTORED');assert.equal(r.calls,1);checks++;
await assert.rejects(run({dirty:1}),/P0/);checks++;
r=await run({duration:370});assert.equal(r.result.state,'DEADLINE');assert.equal(r.calls,1);checks++;
r=await run({stop:true});assert.equal(r.calls,0);assert.equal(r.result.state,'STOPPED');checks++;
r=await run({stopAfter:1});assert.equal(r.calls,1);assert.equal(r.result.state,'STOPPED');checks++;
r=await run({duration:400});assert.equal(r.calls,1);assert.equal(r.result.passed,false);checks++;
r=await run({duration:180});assert.equal(r.result.controllerSeconds,480);assert.equal(r.result.nssSeconds,180);checks++;
assert.equal(soakPlan.automaticFixtureRetries,0);assert.equal(soakPlan.clientSeconds,180);assert.equal(soakPlan.ownerSeconds,180);assert.equal(soakPlan.kernelMaximumSeconds,120);assert.equal(soakPlan.uninterruptedNssClaim,false);checks++;
const out={passed:true,checks,routerAccess:false,dirtyRestoreStopsNextGeneration:true,environmentRefusalIsNotRetried:true,soakPlan};
fs.writeFileSync('work/resident-dev-20261007/soak-tests-'+Date.now()+'-'+crypto.randomBytes(4).toString('hex')+'.json',JSON.stringify(out,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify(out));
