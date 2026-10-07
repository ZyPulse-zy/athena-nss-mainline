import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {entryRoot,materialize,inspection,stopRequest,read,save,limits} from './materialize.mjs';

const root='work/v43-run-'+new Date().toISOString().replace(/\D/g,'').slice(0,14)+'-'+crypto.randomBytes(4).toString('hex');
const q=materialize(root,Date.now()+600000);const checks=[];
const test=(name,f)=>{f();checks.push(name);};
test('inspect has no traffic or remote writes',()=>{const x=inspection();assert.ok(x.passed&&!x.routerWrites&&!x.trafficGenerated&&!x.liveNetworkAudited);});
test('runtime inherits every 3354 binding',()=>assert.equal(q.inheritedBindings,3354));
test('fixed policy and exact data plane retained',()=>assert.ok(q.dataPlaneByteExact&&q.classificationAndQosPolicyUnchanged&&q.limits.client===180&&q.limits.bundle===73728));
test('existing namespace refused',()=>assert.throws(()=>materialize(root,Date.now()+600000),/Fresh namespace/));
test('escaping namespace refused',()=>assert.throws(()=>materialize('work/../v43-other',Date.now()+600000)));
test('extended cutoff refused',()=>assert.throws(()=>materialize(root+'a',Date.now()+3600000)));
test('stop before client only writes own intent',()=>{const x=stopRequest(root);assert.ok(x.requested&&!x.clientControlWritten&&x.beforeClientLaunch);});
const load=root+'/load-model';fs.mkdirSync(load);save(root+'/load-latest-private.json',{dir:load,clientPid:111});save(load+'/client-config-private.json',{session:'a'.repeat(16),seconds:180,mbps:32});save(load+'/status-private.json',{session:'a'.repeat(16),pid:111});
test('stop writes session-bound owned client control',()=>{const x=stopRequest(root);assert.ok(x.clientControlWritten&&!x.routerWrites&&!x.forceKillController&&!x.restorationConfirmed);assert.deepEqual(read(load+'/control.json'),{session:'a'.repeat(16),stop:true});});
save(load+'/result-private.json',{modelOnly:true});test('ended client is not restarted',()=>assert.ok(stopRequest(root).clientAlreadyEnded));
const out={passed:true,checks,modelOnly:true,modelRuntimeRoot:root,trafficGenerated:false,routerWrites:false,hardwareExecuted:false,sourceBindings:q.actualBindings,limits};save(entryRoot+'/entry-model-qualified.json',out);console.log(JSON.stringify(out));
