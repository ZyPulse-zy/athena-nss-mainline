import fs from 'node:fs';import assert from 'node:assert/strict';
import {rtScope} from './rt-scope.mjs';
import {selectNormalCandidates} from '../resident-normal-dev-i-20261008/normal-policy.mjs';
import {activeMask} from '../resident-general-dev-i-20261008/selection.mjs';
const baseline=JSON.parse(fs.readFileSync('work/resident-rc1-run-20261007163534-ae83fa69/controlled-candidates-private.json'));
const flows=[...baseline.tcp,...baseline.udp],base={...baseline,flows,routerWrites:false,nssAdmissionAllowed:false};
const pc={at:'2026-10-08T00:00:00.0000000Z',ageSeconds:0.1,processes:[],tcp:[],udp:[]};
for(const [n,f]of flows.entries()){
 const pid=1000+n;pc.processes.push({pid,start:'2026-10-07T23:00:00.1234567Z',executable:'C:\\test\\client-'+n+'.exe',commandReadable:true});
 const e={LocalAddress:f.identity.original.src,LocalPort:f.identity.original.sport,OwningProcess:pid};
 if(f.identity.protocolNumber===6){Object.assign(e,{RemoteAddress:f.identity.original.dst,RemotePort:f.identity.original.dport});pc.tcp.push(e);}else pc.udp.push(e);
}
const frame=selectNormalCandidates(base,pc),scope=rtScope(frame);let checks=0;
const check=fn=>{fn();checks++;};
check(()=>{assert.equal(scope.owners.length,1);assert.equal(scope.tcp.length,0);assert.equal(scope.udp.length,1);assert.equal(activeMask(selectNormalCandidates(base,pc,scope).pairs[0]),2);});
check(()=>{const s=structuredClone(scope);s.owners[0].start='2026-10-07T23:00:00.1234568Z';assert.equal(selectNormalCandidates(base,pc,s).pairs.length,0);});
check(()=>{const s=structuredClone(scope);s.udp[0].dport++;assert.equal(selectNormalCandidates(base,pc,s).pairs.length,0);});
check(()=>{const f=structuredClone(frame);f.udp[0].decision.budgetAdmitted=false;assert.throws(()=>rtScope(f));});
check(()=>{const f=structuredClone(frame);f.udp[0].decision.class='BE';assert.throws(()=>rtScope(f));});
check(()=>{const f=structuredClone(frame);f.sourceAge=6;assert.throws(()=>rtScope(f));});
check(()=>{const f=structuredClone(frame);delete f.owners[f.udp[0].key];assert.throws(()=>rtScope(f));});
check(()=>{const f=structuredClone(frame);f.udp.push(structuredClone(f.udp[0]));assert.throws(()=>rtScope(f));});
check(()=>{const f=structuredClone(frame);f.nssAdmissionAllowed=true;assert.throws(()=>rtScope(f));});
check(()=>assert.equal(scope.owners[0].start,'2026-10-07T23:00:00.1234567Z'));
console.log(JSON.stringify({passed:true,checks,routerAccess:false,testScopeOnlyNarrows:true,activeMask:2,source6Unchanged:true}));
