import fs from 'node:fs';import assert from 'node:assert/strict';import{verifyStartupCandidate}from'./startup-health.mjs';
const q={passed:true,hardwareExecuted:false,normalProcessOwnedSource:true,optionalSlotNative:true,independentQualifiedAdmission:true,rtAndQosPolicyUnchanged:true,normalEntryCreatesTraffic:false,normalEntryOperatesDesktop:false,defaultPermanentNss:false,sixDataPlaneLuaByteExactWithRc1:false,onlyPublicationReadChanged:false,limits:{bundle:73728,exec:9000,source:6}};
let checks=0;verifyStartupCandidate(q);checks++;
for(const k of Object.keys(q).filter(k=>k!=='limits')){const b=structuredClone(q);b[k]=!b[k];assert.throws(()=>verifyStartupCandidate(b));checks++;}
for(const k of Object.keys(q.limits)){const b=structuredClone(q);b.limits[k]++;assert.throws(()=>verifyStartupCandidate(b));checks++;}
const error=JSON.parse(fs.readFileSync('work/resident-service-run-20261008064058-aa377e05/failure-private.json'));
assert.equal(error.state.generationsStarted,0);assert.equal(error.state.state,'FAILED_SOFTWARE');assert.ok(error.stack.includes('startup-health.mjs:6:59'));checks++;
console.log(JSON.stringify({passed:true,checks,routerAccess:false,modelOnly:true,originalStartupAssertionFailurePreserved:true}));
