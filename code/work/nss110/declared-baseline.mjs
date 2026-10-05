// Adopt exactly one committed source repair and the already observed WAN4 failure.
// No routing mutation or general drift exception. The native ownership audit stays full.
import assert from 'node:assert/strict';
import {proveWan4Failover} from '../nss109/failover-baseline.mjs';
import {adoptServices} from '../nss50/service-epoch.mjs';
export const authSha256='7d187998681dff2b3c15d476dfe096d1e33ee42c4028843a75381b069cdc0e44';
export const oldManifestSha256='71ba5eccf89d131da847a5bbb98ccfd2362cc8e4a351238f405b53f736d187ba';
export const manifestSha256='165de08d8733842151c770d23c5060dcd11a4b56b1ea756dc00ace494333de31';
export function declaredReference(historical,current,health,authDigest,wan4Status){
 assert.equal(historical.protectedManifestSha256,oldManifestSha256);
 assert.equal(current.protectedManifestSha256,manifestSha256);
 assert.equal(current.protectedManifestPassed,true);assert.equal(authDigest,authSha256);
 assert.equal(current.boot,historical.boot);assert.equal(current.kernel,historical.kernel);
 const prior=historical.services['router-project-minieap'].wan4,live=current.services['router-project-minieap'].wan4;
 assert.deepEqual(Object.keys(live).sort(),['command','running']);
 assert.equal(live.running,false);assert.deepEqual(live.command,prior.command);
 assert.equal(wan4Status.up,false);assert.equal(wan4Status.pending,false);
 assert.ok(!wan4Status['ipv4-address']||wan4Status['ipv4-address'].length===0);
 assert.deepEqual(current.addresses.rpwan4,[]);
 assert.equal(current.routes['104'],'unreachable default metric 42760 \n');
 const failover=proveWan4Failover(historical,current,health);
 const reference=structuredClone(failover.reference);
 reference.protectedManifestSha256=manifestSha256;
 reference.services['router-project-minieap'].wan4=structuredClone(live);
 reference.addresses.rpwan4=[];reference.routes['104']=current.routes['104'];
 const adopted=adoptServices(reference.services,current.services);reference.services=adopted.services;
 return {reference,proof:{...failover.proof,declaredAuthRepairExact:true,declaredManifestExact:true,wan4FailedBeforeExperiment:true,wan4InstanceNotRunning:true,fourHealthyWanPrewriteOnly:true,unrelatedServiceAdoption:adopted.changes,selectedWanMustBeHealthy:true,serviceChangesDuringExperimentAllowed:false}};
}
