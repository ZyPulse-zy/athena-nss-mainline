import{launchInitialFour,fourOwnedPidsReady}from'./fixture-startup.mjs';
import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {entryRoot,materialize,inspection,stopRequest,read,save,limits,hash} from './materialize.mjs';
import {requireWindowsIdentity} from './platform-preflight.mjs';

const root='work/v45-run-'+new Date().toISOString().replace(/\D/g,'').slice(0,14)+'-'+crypto.randomBytes(4).toString('hex');
const q=materialize(root,Date.now()+600000);const checks=[];
const test=(name,f)=>{f();checks.push(name);};
test('inspect has no traffic or remote writes',()=>{const x=inspection();assert.ok(x.passed&&!x.routerWrites&&!x.trafficGenerated&&!x.liveNetworkAudited);});
test('runtime inherits every 3354 binding',()=>assert.equal(q.inheritedBindings,3354));
test('fixed policy and exact data plane retained',()=>assert.ok(q.dataPlaneByteExact&&q.classificationAndQosPolicyUnchanged&&q.limits.client===180&&q.limits.bundle===73728));
test('existing namespace refused',()=>assert.throws(()=>materialize(root,Date.now()+600000),/Fresh namespace/));
test('escaping namespace refused',()=>assert.throws(()=>materialize('work/../v45-other',Date.now()+600000)));
test('extended cutoff refused before namespace creation',()=>assert.throws(()=>materialize(root,Date.now()+3600000),/Fresh cutoff/));
test('short cutoff refused before namespace creation',()=>assert.throws(()=>materialize(root,Date.now()+290000),/Fresh cutoff/));
test('unreadable process identity refuses admission',()=>assert.throws(()=>requireWindowsIdentity({identityReadable:false}),/process identity unavailable/));
test('incomplete process identity refuses admission',()=>assert.throws(()=>requireWindowsIdentity({identityReadable:true,processId:1,creationDatePresent:true,executablePathPresent:true,commandLinePresent:false}),/process identity unavailable/));
test('readable process identity alone makes no network writes',()=>{const x=requireWindowsIdentity({identityReadable:true,processId:1,creationDatePresent:true,executablePathPresent:true,commandLinePresent:true,networkSocketCommandsPresent:true});assert.ok(x.passed&&!x.routerWrites&&!x.trafficGenerated);});
const auditSource=fs.readFileSync(root+'/current-audit-diagnostic.mjs','utf8');
const guardLiteral=auditSource.split('assert.match(caseDir,')[1].split(');')[0];
const auditGuard=Function('return ('+guardLiteral+');')();
test('generated readonly audit accepts exact owned session path',()=>assert.ok(auditGuard.test(root+'/session-20261007090000-aabbccdd')));
test('generated namespace prefixes retain trailing separator and reject escape',()=>{
 assert.ok(!auditGuard.test(root+'session-20261007090000-aabbccdd')&&!auditGuard.test(root+'/../session-20261007090000-aabbccdd'));
 const prefix='work\\/v42-counter-window\\/',expected=root.replaceAll('/','\\/')+'\\/';
 let checked=0;
 for(const origin of Object.keys(q.originHashes)){
  const source=fs.readFileSync(origin,'utf8'),count=source.split(prefix).length-1;
  if(count){const generated=fs.readFileSync(root+'/'+origin.split('/').at(-1),'utf8');assert.ok(generated.split(expected).length-1>=count,origin);checked+=count;}
 }
 assert.ok(checked>0);
});
test('stop before client only writes own intent',()=>{const x=stopRequest(root);assert.ok(x.requested&&!x.clientControlWritten&&x.beforeClientLaunch);});
const load=root+'/load-model';fs.mkdirSync(load);save(root+'/load-latest-private.json',{dir:load,clientPid:111});save(load+'/client-config-private.json',{session:'a'.repeat(16),seconds:180,mbps:32});save(load+'/status-private.json',{session:'a'.repeat(16),pid:111});
test('stop writes session-bound owned client control',()=>{const x=stopRequest(root);assert.ok(x.clientControlWritten&&!x.routerWrites&&!x.forceKillController&&!x.restorationConfirmed);assert.deepEqual(read(load+'/control.json'),{session:'a'.repeat(16),stop:true});});
save(load+'/result-private.json',{modelOnly:true});test('ended client is not restarted',()=>assert.ok(stopRequest(root).clientAlreadyEnded));
const labelOf=p=>{
 const source=fs.readFileSync(p+'/read-final-health.mjs','utf8');
 const m=source.match(/current-audit-diagnostic\.mjs','([^']+)','prewrite'/);
 assert.ok(m,'Final readonly audit invocation is explicit');return m[1];
};
test('final audit label includes its complete fresh runtime namespace',()=>assert.equal(labelOf(root),root.slice(5)+'-final'));
const secondRoot='work/v45-run-'+new Date().toISOString().replace(/\D/g,'').slice(0,14)+'-'+crypto.randomBytes(4).toString('hex');
materialize(secondRoot,Date.now()+600000);
test('separate runtime final labels cannot collide in shared publication outputs',()=>{
 const source=fs.readFileSync('work/nss122/wait-publication-metadata.mjs','utf8');
 assert.ok(source.includes("'work/nss122/'+label+'-join-raw-private.json'"));
 assert.notEqual(labelOf(root),labelOf(secondRoot));
 assert.notEqual('work/nss122/'+labelOf(root)+'-join-raw-private.json','work/nss122/'+labelOf(secondRoot)+'-join-raw-private.json');
});
const childStatus={pid:999,errors:[],elapsed:1,at:100,tcpChildren:['tcp','tcp2','tcp3','tcp4'].map((slot,i)=>({slot,ownerPid:1000+i,connected:false,bytes:0}))};
test('four published PIDs permit only earlier observation before payload',()=>assert.ok(fourOwnedPidsReady(childStatus,100.5)));
test('missing or duplicate owned child PID cannot begin acquisition observation',()=>{
 for(const pid of [undefined,0,-1,1.5,1000]){const s=structuredClone(childStatus);s.tcpChildren[3].ownerPid=pid;assert.ok(!fourOwnedPidsReady(s,100.5));}
});
test('stale status or fixture errors cannot begin acquisition observation',()=>{
 assert.ok(!fourOwnedPidsReady(childStatus,102)&&!fourOwnedPidsReady(childStatus,99.9));
 assert.ok(!fourOwnedPidsReady({...childStatus,errors:['original failure']},100.5));
});
const launched=[],pending=[];
const launching=launchInitialFour((slot,attempt)=>{launched.push({slot,attempt});return new Promise(resolve=>pending.push(resolve));},()=>false);
test('a slow first initial connection does not prevent the other three spawning',()=>{
 assert.deepEqual(launched,['tcp','tcp2','tcp3','tcp4'].map(slot=>({slot,attempt:1})));assert.equal(pending.length,4);
});
for(const resolve of pending)resolve();await launching;
test('stopped fixture spawns no initial child',()=>{const calls=[];launchInitialFour(slot=>calls.push(slot),()=>true);assert.deepEqual(calls,[]);});
test('NSS selection still requires all first payloads and original full five-WAN classification',()=>{
 const s=fs.readFileSync(root+'/match-controlled.mjs','utf8');
 assert.ok(s.includes('status.tcpConnected')&&s.includes('Natural five-WAN acquisition window ended'));
 for(const name of ['match-controlled.mjs','read-controlled.mjs','fixture-retry-policy.mjs','download-server.py','guard-fixture.ps1']){
  if(!fs.existsSync(root+'/'+name))continue;
  const origin=fs.readFileSync('work/v42-counter-window/'+name,'utf8'),expected=origin.replaceAll('work\\/v42-counter-window\\/',root.replaceAll('/','\\/')+'\\/').replaceAll('work/v42-counter-window',root).replaceAll('v42-counter-window-',root.slice(5)+'-').replaceAll('v42-final',root.slice(5)+'-final');
  assert.equal(fs.readFileSync(root+'/'+name,'utf8'),expected,name);
 }
});
test('only initial startup and process readiness import the startup helper',()=>{
 assert.ok(fs.readFileSync(root+'/native-client.mjs','utf8').includes('await launchInitialFour(startTcp,()=>ended)'));
 assert.ok(fs.readFileSync(root+'/wait-four-ssh.mjs','utf8').includes('fourOwnedPidsReady(s,Date.now()/1000)'));
 assert.ok(q.sourceManifest[entryRoot+'/fixture-startup.mjs']);
});
const sourceHashes=Object.fromEntries(['entry.mjs','materialize.mjs','check-model.mjs','platform-preflight.mjs','fixture-startup.mjs'].map(n=>[entryRoot+'/'+n,hash(fs.readFileSync(entryRoot+'/'+n))]));
const out={passed:true,checks,modelOnly:true,modelRuntimeRoot:root,trafficGenerated:false,routerWrites:false,hardwareExecuted:false,sourceBindings:q.actualBindings,sourceHashes,limits};const receipt=entryRoot+'/model-'+Date.now()+'-'+crypto.randomBytes(4).toString('hex')+'.json';save(receipt,out);fs.writeFileSync(entryRoot+'/entry-model-latest-private.json',JSON.stringify({receipt})+'\n');console.log(JSON.stringify(out));
