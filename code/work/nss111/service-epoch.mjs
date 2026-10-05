// Permit only the independently diagnosed, unselected failed WAN4 process epoch.
// Commands, instance sets, all other services and routing stay exact.
import assert from 'node:assert/strict';
import {verifyEpochServices as original} from '../nss50/service-epoch.mjs';
export function failedWan4Service(a,b){
 assert.deepEqual(a.command,b.command,'WAN4 command changed');
 for(const v of [a,b]){
  assert.equal(typeof v.running,'boolean');
  assert.deepEqual(Object.keys(v).sort(),v.running?['command','pid','running']:['command','running']);
  if(v.running)assert.ok(Number.isSafeInteger(v.pid)&&v.pid>1&&v.pid<=2147483647,'Invalid WAN4 PID');
 }
 return {processChanged:a.running!==b.running||a.pid!==b.pid,commandChanged:false,outsideSelectedFlowWan:true};
}
export function verifyEpochServices(expected,current){
 const a=expected['router-project-minieap'].wan4,b=current['router-project-minieap'].wan4;
 const proof=failedWan4Service(a,b),adjusted=structuredClone(current);
 adjusted['router-project-minieap'].wan4=structuredClone(a);original(expected,adjusted);
 return proof;
}
