import fs from 'node:fs';import assert from 'node:assert/strict';
const root='work/nss37',read=p=>JSON.parse(fs.readFileSync(p));
const pick=(o,ks)=>Object.fromEntries(ks.filter(k=>k in o).map(k=>[k,o[k]]));
const current=read(root+'/deployment-latest.json'),cfg=read(current.localDir+'/config.json');
const differential=read(root+'/normalizer-qualified.json'),lifecycle=read(root+'/lifecycle-qualified.json'),native=read(root+'/native-normalizer-qualified.json'),trial=read(root+'/normalizer-trial-qualified.json');
const audit=read(root+'/final-audit.json'),closure=read(root+'/final-closure.json'),inspection=read(root+'/classifier-final-inspection.json'),affinity=read(root+'/affinity-qualified.json');
assert.ok(current.committed&&differential.passed&&lifecycle.passed&&native.passed&&trial.passed&&audit.passed&&closure.passed&&affinity.passed);
assert.equal(cfg.files['conntrack-source.lua'],differential.sourceSha256);assert.equal(lifecycle.ctSourceSha256,differential.sourceSha256);assert.equal(affinity.configuration.configSha256,current.configHash);
function window(label){
 const path=root+'/'+label+'-observation.json',d=read(path),rows=d.rows,a=rows[0],b=rows.at(-1),dt=b.uptime-a.uptime;
 assert.equal(rows.length,35);assert.ok(d.semantic.passed&&d.semantic.identityDecisionLeafAndExpiryEqual);
 const cpu=s=>s.cpu.trim().split(/\s+/).slice(1,9).map(Number),x=cpu(a),y=cpu(b),delta=y.map((v,i)=>v-x[i]),total=delta.reduce((s,n)=>s+n,0);
 const squeeze=s=>s.softnet.trim().split('\n').reduce((n,l)=>n+parseInt(l.trim().split(/\s+/)[2],16),0);
 const healthy=rows.every(v=>v.status==='running'&&v.guardianHealthy&&v.accel===0&&v.frontend===1);assert.ok(healthy);assert.equal(new Set(rows.map(v=>v.producer)).size,1);
 return {observationFileCompletedAt:fs.statSync(path).mtime.toISOString(),samples:rows.length,allHealthy:healthy,sameProducerWithinWindow:true,seconds:dt,lan4DownMbps:(b.txBytes-a.txBytes)*8/dt/1e6,lan4DownPps:(b.txPackets-a.txPackets)/dt,cpuBusyPercent:100*(total-delta[3]-delta[4])/total,softirqPercent:100*delta[6]/total,timeSqueezeDelta:squeeze(b)-squeeze(a),queryAgeRangeSeconds:[Math.min(...rows.map(v=>v.age)),Math.max(...rows.map(v=>v.age))],publicationDelayRangeSeconds:[Math.min(...rows.map(v=>v.publishDelay)),Math.max(...rows.map(v=>v.publishDelay))],parseMaxSeconds:Math.max(...rows.map(v=>v.parseSeconds)),ageUnderOneSecond:rows.filter(v=>v.age<1).length,semantic:d.semantic,ecmClosedAndZero:healthy,measurement:'Natural light-load software forwarding with observer overhead; these windows do not form a matched performance ABA.'};
}
const windows=Object.fromEntries(['before','trial','permanent'].map(k=>[k,window(k)]));
const deployments=[root+'/'+trial.trialTransaction,current.localDir].map(path=>{
 const cp=read(path+'/checkpoint.json'),armed=read(path+'/armed-proof.json'),stage=read(path+'/stage.json'),detached=read(path+'/stage-detached.json');
 assert.ok(cp.gzipVerified&&armed.passed&&armed.independentOfSsh&&stage.rollbackBeforeFirstWrite&&stage.parentIdentityVerified&&stage.pipeInodesVerified);
 assert.equal(detached.parent,1);assert.deepEqual(detached.fds,{'0':'/dev/null','1':'/dev/null','2':'/dev/null'});
 return {checkpointDownloadedAndHashVerified:true,checkpointGzipVerified:cp.gzipVerified,transactionTimeoutSeconds:180,stageTimeoutSeconds:480,rollbackVerifiedBeforeConfigMutation:true,independentOfControlConnection:true};
});
const final=inspection.files,permanent=read(root+'/permanent-observation.json');
assert.equal(final['classification.json'].producer,permanent.rows[0].producer);assert.equal(audit.producer,final['classification.json'].producer);assert.equal(final['classification.json'].configSha256,current.configHash);
assert.notEqual(final['last-error.json'].producer,final['classification.json'].producer);assert.equal(final['last-error.json'].producer,trial.protectedAudit.producer);assert.ok(final['last-error.json'].error.includes('Installation rollback deadline reached'));
const out={round:'NSS37',updatedAt:new Date().toISOString(),
 hypothesis:'Preserve normalized output, rejection behavior and source deadlines while reducing repeated attribute scans; then safely retain the optimization without opening ECM.',
 change:{file:'conntrack-source.lua',function:'attrs',onlyAttributeSearchChanged:true,oldSha256:differential.originalSha256,newSha256:differential.sourceSha256,literalKeySearch:true,whitespaceBoundaryAndDuplicateSemanticsPreserved:true,sourceScopePolicyAndDeadlinesUnchanged:true,workerGuardianCoreAndBackendUnchanged:true},
 localChecks:differential.checks+lifecycle.checks,differential,lifecycle,
 nativeProfile:read(root+'/normalizer-profile.json'),nativeBenchmark:native,
 automaticRollback:pick(trial.independentRollback,['passed','observedAt','independent180SecondRollback','automaticExpiryWithoutControllerRollback','previousWorkerAndConfigRestored','previousNormalizerAndGuardianRestored','previousClassifierHealthyAndFresh','ecmClosedAndZero']),
 installations:deployments,windows,
 classifier:{committed:true,commitAt:current.commitAt,deploymentReference:'work/nss37/deployment-latest.json',configSha256:current.configHash,workerSha256:cfg.files['worker.lua'],guardianSha256:cfg.files['guardian.lua'],sourceSha256:cfg.files['conntrack-source.lua'],nssEnabled:false},
 controller:{configuration:pick(affinity.configuration,['configSha256','workerSha256','guardianSha256','classifierCoreSha256','ctSourceSha256','policyUnchanged','ctSourceChangedOnlyAttributeSearch','normalizationDifferentialChecks','sourceAndPublicationDeadlinesUnchanged','independentRollbackPreviouslyVerified']),sourceManifestEntries:Object.keys(affinity.sourceManifest).length,newSyntheticSelectionChecks:affinity.checks.length,targetPreflight:pick(read(root+'/mainline-preflight-qualified.json'),['passed','observedAt','readOnly','routerMutationAttempted','exactPackedPolicyRoundtrip','stagedBytes','stageExecBytes','unchangedTransportExecCeiling','abaRuntimeQualified']),historicalNss36ConsumerAndBackendProofsReusedOnlyWhereCodeUnchanged:true,realSessionReadiness:read(root+'/real-session-readiness.json')},
 finalState:{observedAt:inspection.observedAt,protectedAudit:pick(audit,['passed','protectedConfigurationUnchanged','exactOwnedNativeAudit','selectors','queryAge','sequence','ecmClosedAndZero']),sameProducerSincePermanentObservation:true,classificationHealthy:final['classification.json'].dataHealthy&&final['classification.json'].status==='running',guardianHealthy:final['guardian.json'].healthy,lastErrorBelongsToExpiredTrial:true,lastErrorIsCurrentProducer:false,closure},
 actualFastPathTrial:{attempted:false,gateModuleLoaded:false,ecmOpened:false,acceleratedFlowCount:0,bulkRtLeafTrafficMeasured:false,acceleratedPbrMarkNatWanAffinityRevalidated:false},
 limitations:{realHighLoadABACompleted:false,nssCpuBenefitProved:false,gameJitterLossMissCaptured:false,productionCrashInjected:false,wholeSteam300MbpsAccelerated:false,highLoadPublicationTimingQualified:false,allPublicationDelayCausesProved:false,longTermClassifierStabilityQualified:false,parserCpuIsNotRouterCpu:true,lifecycleUsesSyntheticCountersAndIo:true},
 next:'Read-only freshness and publication timing under representative load before a concentrated real same-WAN CS2/Steam attempt. Keep all identity, policy, source-age, tag and independent rollback limits. No second WAN or QoS side branch.',upstreamSubmission:false};
assert.equal(out.localChecks,9113);assert.equal(out.controller.sourceManifestEntries,66);assert.equal(out.controller.newSyntheticSelectionChecks,10);
fs.writeFileSync('outputs/nss37-normalizer-observations.json',JSON.stringify(out,null,2)+'\n');
console.log(JSON.stringify({localChecks:out.localChecks,nativePairedSamples:native.results.reduce((n,r)=>n+r.samples.length,0),windows,configSha256:current.configHash,automaticRollback:true,committed:true,finalState:out.finalState}));
