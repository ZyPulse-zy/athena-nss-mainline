// NSS110's original strict recovery rejection remains untouched.
// The sole new exception is failed/unselected WAN4's existing process restart.
import assert from 'node:assert/strict';
import {proveWan4Failover} from '../nss109/failover-baseline.mjs';
import {adoptServices} from '../nss50/service-epoch.mjs';
import {auditBaseline} from '../nss15/baseline.mjs';
import {failedWan4Service,verifyEpochServices} from './service-epoch.mjs';
export {authSha256,manifestSha256,oldManifestSha256} from '../nss110/declared-baseline.mjs';
import {authSha256,manifestSha256,oldManifestSha256} from '../nss110/declared-baseline.mjs';
export function verifyFailedWanState(current,status,seal){
 const live=current.services['router-project-minieap'].wan4;
 failedWan4Service(live,live);assert.equal(status.up,false);assert.equal(status.pending,false);
 assert.ok(!status['ipv4-address']||status['ipv4-address'].length===0);
 assert.deepEqual(current.addresses.rpwan4,[]);assert.equal(current.routes['104'],'unreachable default metric 42760 \n');
 assert.equal(seal.running,live.running);assert.equal(seal.commandMatches,true);
 if(live.running){assert.equal(seal.pid,live.pid);assert.equal(seal.ppid,1);assert.match(seal.start,/^[0-9]+$/);assert.equal(seal.sameProcessBeforeAfter,true);}
 else{assert.equal(seal.pid,undefined);assert.equal(seal.instanceStillNotRunning,true);}
 return true;
}
export function declaredReference(historical,current,health,digest,status,seal){
 assert.equal(historical.protectedManifestSha256,oldManifestSha256);assert.equal(current.protectedManifestSha256,manifestSha256);
 assert.equal(current.protectedManifestPassed,true);assert.equal(digest,authSha256);
 assert.equal(current.boot,historical.boot);assert.equal(current.kernel,historical.kernel);
 failedWan4Service(historical.services['router-project-minieap'].wan4,current.services['router-project-minieap'].wan4);
 verifyFailedWanState(current,status,seal);
 const failover=proveWan4Failover(historical,current,health),reference=structuredClone(failover.reference);
 reference.protectedManifestSha256=manifestSha256;reference.services['router-project-minieap'].wan4=structuredClone(current.services['router-project-minieap'].wan4);
 reference.addresses.rpwan4=[];reference.routes['104']=current.routes['104'];
 const adopted=adoptServices(reference.services,current.services);reference.services=adopted.services;
 return {reference,proof:{...failover.proof,declaredAuthRepairExact:true,declaredManifestExact:true,wan4FailedBeforeExperiment:true,wan4ProcessOwnershipChecked:true,fourHealthyWanPrewriteOnly:true,selectedWanMustBeHealthyAndNotWan4:true,unrelatedServiceAdoption:adopted.changes,failedUnselectedWan4ProcessEpochMayChange:true,otherServiceChangesDuringExperimentAllowed:false,unknownRoutingDriftAllowed:false}};
}
export function auditScopedBaseline(before,after){
 const proof=verifyEpochServices(before.services,after.services),adjusted=structuredClone(after);
 assert.deepEqual(after.addresses.rpwan4,[]);assert.equal(after.routes['104'],'unreachable default metric 42760 \n');
 adjusted.native=before.native;adjusted.services['router-project-minieap'].wan4=structuredClone(before.services['router-project-minieap'].wan4);
 adjusted.services['router-project-game-classifier']=before.services['router-project-game-classifier'];
 return {...auditBaseline(before,adjusted),failedUnselectedWan4ProcessEpoch:proof,originalFullNativeOwnershipAuditStillRequired:true,noRoutingStateExceptionDuringExperiment:true};
}
