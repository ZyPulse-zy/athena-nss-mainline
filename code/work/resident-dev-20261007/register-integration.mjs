import fs from 'node:fs';
import assert from 'node:assert/strict';
import {entryRoot,read,save,hash} from './materialize.mjs';
import {verifyDeployment} from './deployment-binding.mjs';
const a=read(entryRoot+'/active-private.json');assert.equal(a.hardwareCompleted,true);assert.equal(a.restorationPassed,true);assert.equal(a.state,'RESTORED');assert.ok(!fs.existsSync(entryRoot+'/active-lock'));
const p=read(a.runtimeRoot+'/pilot-reference-private.json'),c=read(p.directory+'/case-reference-private.json');
const r=read(c.dir+'/last-record-private.json'),result=read(c.dir+'/result.json');
assert.equal(result.passed,true);assert.equal(result.automaticLifecycleEpochCompleted,true);assert.equal(r.phases.length,1);
const phase=r.phases[0],samples=r.samples.filter(x=>x.phase==='B');
assert.equal(phase.completed,true);assert.ok(phase.seconds>=90&&phase.seconds<=91.5&&phase.sampleCount>=178);
assert.ok(samples.length>=178&&samples.every(x=>x.counts['ecm_nss_ipv4/accelerated_count']===3));
assert.ok(r.renewals.length>0);
const flags=['moduleUnloaded','qosModuleUnloaded','qosRestored','wanRestored','dualPhysicalQueuesRestored','stateNodeRemoved','automaticPacketTagsCompleted','firmwareZeroAfterRetirement'];
for(const f of flags)assert.equal(r[f],true,f);
const q=read(a.runtimeRoot+'/entry-qualified.json');for(const[f,h]of Object.entries(q.sourceManifest))assert.equal(hash(fs.readFileSync(f)),h,f);
const out={passed:true,scope:'two-TCP-BULK-and-one-UDP-RT-Multi-WAN-controller',runtimeRoot:a.runtimeRoot,
 configHash:verifyDeployment().deployment.configHash,phaseSeconds:phase.seconds,samples:samples.length,
 renewals:r.renewals.length,allBSamplesEcmThree:true,restorationPassed:true,
 selectedWanBySlot:Object.fromEntries(Object.entries(read(p.directory+'/continuity-private.json').selected).map(([s,f])=>[s,f.wan])),
 closedLearningRaceCorrection:true,tcpBulkShapeCorrection:true,restorationFlags:Object.fromEntries(flags.map(f=>[f,r[f]])),
 longerSoakPassed:false,defaultPermanentNss:false,newCpuBenchmark:false,cs2OrSteamOperated:false};
save(entryRoot+'/integration-qualified.json',out);console.log(JSON.stringify(out));
