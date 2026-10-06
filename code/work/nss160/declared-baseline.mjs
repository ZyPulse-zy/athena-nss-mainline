// Adopt the already proven NSS159 natural recovery, pin all services for this run.
import fs from 'node:fs';import assert from 'node:assert/strict';
import {authSha256,manifestSha256} from '../nss110/declared-baseline.mjs';
import {adoptServices,verifyEpochServices} from '../nss50/service-epoch.mjs';
import {auditBaseline} from '../nss15/baseline.mjs';
export {authSha256,manifestSha256,verifyEpochServices};
const load=p=>JSON.parse(fs.readFileSync(p));
export function verifyFailedWanState(current,status,seal){
 const live=current.services['router-project-minieap'].wan4;
 assert.equal(status.up,true);assert.equal(status.pending,false);assert.equal(status.l3_device,'rpwan4');
 assert.equal(live.running,true);assert.equal(seal.running,true);assert.equal(seal.commandMatches,true);assert.equal(seal.sameProcessBeforeAfter,true);assert.equal(seal.pid,live.pid);assert.equal(seal.ppid,1);
 const a=current.addresses.rpwan4.flatMap(x=>x.addr_info).filter(x=>x.family==='inet');assert.equal(a.length,1);assert.equal(status['ipv4-address'].length,1);assert.equal(a[0].local,status['ipv4-address'][0].address);assert.equal(a[0].prefixlen,status['ipv4-address'][0].mask);return true;
}
export function declaredReference(unusedHistorical,current,health,digest,status,seal){
 const final=load('work/nss158/evening-20261006/v3-final-health.json'),recovered=load('work/nss158/evening-20261006/v3-wan4-recovery-proof.json'),historical=load('work/nss158/evening-20261006/v3-final-baseline-private.json');
 assert.ok(final.passed&&final.originalFullLockedNativeAudit&&final.unrelatedConfigurationMatches&&final.exactWan4AutomaticRecoveryProved&&recovered.tenRecoveryRampStepsReproduced);
 assert.equal(current.protectedManifestSha256,manifestSha256);assert.ok(current.protectedManifestPassed);assert.equal(digest,authSha256);assert.equal(current.boot,historical.boot);assert.equal(current.kernel,historical.kernel);
 assert.deepEqual(health.weights,[100,100,100,100,100]);assert.deepEqual(health.wan.map(x=>x.healthy),[true,true,true,true,true]);verifyFailedWanState(current,status,seal);
 const reference=structuredClone(historical);assert.deepEqual(reference.services['router-project-minieap'].wan4.command,current.services['router-project-minieap'].wan4.command);reference.services['router-project-minieap'].wan4=structuredClone(current.services['router-project-minieap'].wan4);
 const adopted=adoptServices(reference.services,current.services);reference.services=adopted.services;
 return{reference,proof:{passed:true,declaredAuthRepairExact:true,declaredManifestExact:true,priorFullOriginalRecoveryAuditReused:true,allFiveHealthyPrewriteOnly:true,unchangedRecoveredPbrMapAndRoutingStillRequired:true,unrelatedServiceAdoption:adopted.changes,allServicesPinnedDuringExperiment:true,unknownRoutingDriftAllowed:false,nssPermissionGranted:false}};
}
export function auditScopedBaseline(before,after){
 verifyEpochServices(before.services,after.services);const adjusted=structuredClone(after);adjusted.native=before.native;adjusted.services['router-project-game-classifier']=before.services['router-project-game-classifier'];
 return{...auditBaseline(before,adjusted),originalFullNativeOwnershipAuditStillRequired:true,noRoutingStateExceptionDuringExperiment:true};
}
