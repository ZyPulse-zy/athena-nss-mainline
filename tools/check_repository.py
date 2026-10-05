"""Verify curated source identity, artifact links, and obvious secret exclusions."""
import hashlib, json, re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'source-manifest.json').read_text(encoding='utf-8'))
for item in manifest['sources']:
    file=root/item['path']; assert file.is_file(), item['path']
    assert hashlib.sha256(file.read_bytes()).hexdigest()==item['sha256'],item['path']
rules={
 'private-key':r'-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----',
 'github-token':r'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{35,})\b',
 'openai-token':r'\bsk-(?:proj-)?[A-Za-z0-9_-]{35,}',
 'credential-url':r'https?://[^\s/]+:[^\s/@]+@',
 'literal-password':r'''(?i)(?:password|passwd|access_token|refresh_token)\s*[:=]\s*["'][^"'\s]{8,}["']''',
}
count=0; links=0
for file in root.rglob('*'):
    # Python replay caches are already excluded by .gitignore; they are not exported artifacts.
    if not file.is_file() or any(p in file.relative_to(root).parts for p in ('.git','.local','__pycache__')): continue
    rel=file.relative_to(root).as_posix()
    assert not re.search(r'(?i)(?:^|/)(?:connect-router[^/]*|.*private.*|.*credential.*|deployment-latest\.json)$',rel), 'Excluded filename: '+rel
    assert file.suffix.lower() not in ('.ko','.o','.key','.pem','.pfx','.clixml','.zip','.gz'),rel
    text=file.read_text(encoding='utf-8'); assert '\ufffd' not in text,rel
    for name,pattern in rules.items():
        if re.search(pattern,text): raise AssertionError('Potential secret ('+name+') in '+rel)
    if file.suffix=='.md':
        for dest in re.findall(r'\[[^\]]+\]\(([^)]+)\)',text):
            if re.match(r'^https?://',dest): continue
            assert (file.parent/dest.split('#')[0]).resolve().exists(),rel+' -> '+dest
            links+=1
    count+=1
s=json.loads((root/'evidence/nss33-summary.json').read_text())
assert s['realTrial']['passed'] is False and s['realTrial']['rollbackPassed'] is True
assert not s['nssHighLoadCpuBenefitProved'] and not s['cs2JitterLossMissCaptured']
assert s['realTrial']['bulkLeaf']['packets']==s['realTrial']['rtLeaf']['packets']==0
n=json.loads((root/'evidence/nss35-address-recovery.json').read_text())
c=json.loads((root/'evidence/nss45-runtime.json').read_text())
assert n['checks']==136 and n['classifier']['committed'] and n['automaticRollback']['passed']
assert c['round']=='NSS45' and c['deploymentReference']=='work/nss39/deployment-latest.json'
assert n['protectedAudit']['ecmClosedAndZero'] and not n['safety']['nssGateOrQdiscLoaded']
assert not n['limitations']['productionAddressFailureInjected'] and not n['limitations']['highLoadCpuBenefitProved']
assert not n['limitations']['cs2JitterLossMissCaptured']
x=json.loads((root/'evidence/nss36-mainline.json').read_text())
assert x['checks']==299 and x['controller']['configuration']['configSha256']==n['classifier']['configSha256']
t=x['actualTrial']
assert t['attempted'] and not t['passed'] and not t['matchedForwardingABACompleted'] and t['rollbackPassed']
assert t['probeCount']==44 and t['readyCount']==0 and sum(t['refusalCounts'].values())==44
assert t['physicalLan4QosTreePrepared'] and not t['packetTagRulesInstalled'] and not t['gateModuleLoaded'] and not t['nssPermissionGranted']
assert t['bulkLeaf']['packets']==t['rtLeaf']['packets']==0
assert x['finalState']['previousAuditRejectedStaleSnapshot'] and x['finalState']['subsequentAuditPassed'] and x['finalState']['ecmClosedAndZero']
assert not x['limitations']['nssCpuBenefitProved'] and not x['limitations']['gameJitterLossMissCaptured']
y=json.loads((root/'evidence/nss37-normalizer.json').read_text())
assert y['localChecks']==9113 and y['differential']['checks']==9087 and y['lifecycle']['checks']==26
assert y['classifier']['committed']
assert y['change']['onlyAttributeSearchChanged'] and y['change']['sourceScopePolicyAndDeadlinesUnchanged']
assert hashlib.sha256((root/'code/work/nss35/conntrack-source.lua').read_bytes()).hexdigest()==y['change']['oldSha256']
assert y['change']['newSha256']==y['classifier']['sourceSha256']==y['differential']['sourceSha256']
assert hashlib.sha256((root/'code/work/nss37/conntrack-source.lua').read_bytes()).hexdigest()==y['change']['newSha256']
assert y['automaticRollback']['automaticExpiryWithoutControllerRollback'] and y['automaticRollback']['previousNormalizerAndGuardianRestored']
assert len(y['installations'])==2 and all(v['rollbackVerifiedBeforeConfigMutation'] and v['independentOfControlConnection'] for v in y['installations'])
assert sum(len(v['samples']) for v in y['nativeBenchmark']['results'])==16
assert all(v['allOutputsEqual'] and v['cpuReductionPercent']>20 for v in y['nativeBenchmark']['results'])
assert all(v['allHealthy'] and v['samples']==35 and v['ecmClosedAndZero'] for v in y['windows'].values())
assert y['controller']['sourceManifestEntries']==66 and y['controller']['newSyntheticSelectionChecks']==10
assert y['controller']['configuration']['configSha256']==y['classifier']['configSha256']
assert y['finalState']['protectedAudit']['ecmClosedAndZero'] and y['finalState']['sameProducerSincePermanentObservation']
assert not y['actualFastPathTrial']['attempted'] and not y['actualFastPathTrial']['ecmOpened']
assert not y['limitations']['realHighLoadABACompleted'] and not y['limitations']['nssCpuBenefitProved'] and not y['limitations']['gameJitterLossMissCaptured']
z=json.loads((root/'evidence/nss38-mainline.json').read_text())
assert z['deploymentReference']=='work/nss37/deployment-latest.json' and not z['permanentClassifierChanged']
t=z['actualTrial'];assert t['attempted'] and not t['passed'] and t['rollbackPassed']
assert t['wan']==2 and t['tcpMark']==t['udpMark']==131072 and t['sameNat']
assert t['probeCount']==32 and t['readyCount']==0 and sum(t['refusalCounts'].values())==32
assert t['bulkLeaf']['packets']==t['rtLeaf']['packets']==0
assert not t['gateModuleLoaded'] and not t['nssPermissionGranted'] and not t['packetTagRulesInstalled']
assert t['frozenSourceProofCopies']==70 and t['physicalLan4QosTreePrepared']
candidate=z['candidate'];assert not candidate['installed'] and not candidate['operationalBindingUpdated']
assert candidate['localChecks']=={'decisionCases':1470,'inspectionCountChecks':5,'admissionCases':212,'renewalRetirementCases':21}
assert candidate['trace']['admissionAndDiagnosticChecks']==230 and candidate['trace']['decisionCases']==1470
for name,key in [('candidate-classifier.lua','adapterSha256'),('candidate-traced-classifier.lua',None),('candidate-traced-fast-path.lua',None)]:
    expected=candidate[key] if key else candidate['trace']['adapterSha256' if 'classifier' in name else 'fastSha256']
    assert hashlib.sha256((root/'code/work/nss38'/name).read_bytes()).hexdigest()==expected
assert len(candidate['nativeBenchmark']['rows'])==12 and candidate['nativeBenchmark']['successfulReadyCalls']==120
assert z['classifierRestart']['exitCode']==143 and z['classifierRestart']['exactRecoveryLogged']
assert not z['classifierRestart']['underlyingBlockOrSignalCauseProved']
assert all(x['exitCode']==0 and x['cakeRoots']==1 for x in z['classifierRestart']['subsequentProbe']['rows'])
assert z['finalState']['currentClassifierHealthy'] and not z['finalState']['sameProducerSinceBegin']
assert z['finalState']['protectedAudit']['ecmClosedAndZero'] and z['finalState']['closure']['passed']
assert not z['limitations']['realHighLoadABACompleted'] and not z['limitations']['nssCpuBenefitProved']
assert not z['limitations']['gameJitterLossMissCaptured'] and not z['limitations']['completeHighLoadLifecycleQualified']
v=json.loads((root/'evidence/nss39-mainline.json').read_text())
assert v['classifier']['committed'] and v['classifier']['configSha256']==c['classifierConfigSha256']
assert v['change']['onlyTcSupervisionAndFailureDiagnosticsChanged'] and v['change']['policySourceScopeAndDeadlinesUnchanged']
assert v['change']['tcDeadlineSeconds']==2 and v['change']['outerMutationDeadlineSeconds']==6 and v['change']['failedCommandStillFatal']
assert hashlib.sha256((root/'code/work/nss39/worker.lua').read_bytes()).hexdigest()==v['classifier']['workerSha256']
assert len(v['installations'])==4 and sum(i['automaticRollbackVerified'] for i in v['installations'])==3 and v['installations'][-1]['committed']
assert all(i['checkpointVerified'] and i['rollbackVerifiedBeforeConfigMutation'] and i['deadlineSeconds']==180 for i in v['installations'])
assert v['helperChecks']['localCases']==16 and v['helperChecks']['nativeArgumentCases']==13 and len(v['helperChecks']['nativeProcessCases'])==8
assert all(i['allFixtureChildrenGone'] for i in v['helperChecks']['nativeProcessCases'])
assert v['startup']['thirdInitialUnhealthySamples']==3 and v['startup']['oldPublicationNeverAuthorized']
assert not v['windows']['thirdColdStart']['allHealthy'] and v['windows']['retained']['allHealthy']
q=v['controller'];assert q['boundToCurrentDeployment'] and q['configuration']['configSha256']==c['classifierConfigSha256']
assert q['sourceManifestEntries']==68 and q['admissionChecks']==230 and q['renewalLocalChecks']==21 and q['coreLifecycleChecks']==26 and q['ownedLifecycleChecks']==19
assert q['nativeConsumerChecks']==17 and q['nativeAbaCases']==11 and q['affinityChecks']==10 and q['exactTagPolicyRoundtrip'] and q['nativeTemporaryStageIndependentlyRemoved']
assert q['nativeIoAndClocksMocked'] and not q['hardwareHighLoadQualified'] and q['stageExecBytes']<=q['transportExecCeiling']==9000
assert v['finalState']['ecmClosedAndZero'] and v['finalState']['sameProducerSinceRetainedObservation'] and v['finalState']['closure']['passed']
assert not v['actualFastPathTrial']['attempted'] and not v['limitations']['realHighLoadABACompleted'] and not v['limitations']['nssCpuBenefitProved'] and not v['limitations']['gameJitterLossMissCaptured']
w=json.loads((root/'evidence/nss40-mainline.json').read_text())
assert w['classifierConfigSha256']==c['classifierConfigSha256'] and not w['permanentClassifierChanged']
a=w['realReadOnlyAdmission'];assert a['samples']==94 and a['ready']==4 and sum(a['refusals'].values())==90
assert a['selectedWan']==5 and a['fullTcpMark']==a['fullUdpMark']==327680 and a['sameNat'] and a['zoneZero']
assert a['actualApplicationOwnershipChecked'] and a['tupleAndInstanceValidated']
assert 300<a['performance']['lan4DownMbps']<350 and a['performance']['timeSqueezeDelta']==0
assert a['observationCostIncludedInCpu'] and a['notMatchedForwardingABA'] and not a['nssOpened']
assert a['initialAgeLimitSeconds']==1 and a['prelearningAgeLimitSeconds']==2 and a['execBytes']<=9000
t=w['actualTrial'];assert t['prewriteAuditRefused'] and t['frozenBoundFiles']==72 and t['originalLine']==32
assert not any(t[k] for k in ['productionMutationAttempted','checkpointCreated','wanChanged','qdiscCreated','tagRulesInstalled','gateModuleLoaded','ecmOpened','matchedForwardingABACompleted'])
assert t['hardwareLeafCounters'] is None and not t['exactFailedAgesRecorded'] and not t['failedPhaseTimingRecorded']
assert t['selectedPairNotFrozenBeforePrewriteRefusal'] and t['rawApplicationLatestWasRefreshedAfterward']
d=w['diagnosticFollowup'];assert d['firstReadonlyPassed'] and d['secondReadonlyPassed'] and d['originalAssertionsRetained'] and d['perInvocationApplicationArchiveVerified']
assert not d['failedHighLoadAuditRootCauseProved'] and d['timingOrderingDoesNotProveFailureCause']
assert w['closingSoftwareWindow']['samples']==35 and w['closingSoftwareWindow']['allHealthy'] and w['closingSoftwareWindow']['semantic']['identityDecisionLeafAndExpiryEqual']
assert w['finalState']['protectedAudit']['ecmClosedAndZero'] and w['finalState']['sameProducerSinceTurnStart'] and w['finalState']['sameProducerSinceNss39LastInspection'] and w['finalState']['closure']['passed']
assert not any(w['conclusions'][k] for k in ['reliableHighLoadAdmissionProved','realHighLoadNssLoopCompleted','nssCpuBenefitProvedThisRound','cs2JitterLossMissCaptured','highLoadCauseOfStaleProtectedSnapshotKnown','secondWanExpansionAllowed'])
rows=json.loads((root/'evidence/nss40-admission-timing.json').read_text())['rows']
assert len(rows)==94 and sum(x['ready'] for x in rows)==4 and all('sourceSequence' in x and 'sourceAge' in x for x in rows)
assert c['historicalNss40StaleProtectedSnapshotRejection']
assert not c['realForwardingABACompleted'] and not c['completePerformanceAndGameAcceptance']
assert c['historicalNss41NativeForwardingABACompleted'] and c['historicalNss41RecoveryAlignmentRefused']
j=json.loads((root/'evidence/nss41-mainline.json').read_text(encoding='utf-8'))
assert j['classifierConfigSha256']==c['classifierConfigSha256'] and not j['permanentClassifierChanged']
assert j['entry']['runtimeBoundFiles']==68 and j['entry']['totalBoundFiles']==83 and j['entry']['deadlinesNotExtended']
assert j['entry']['schedulingWaitOutsideLock'] and j['entry']['schedulingCannotAuthorizeNss']
assert j['localChecks']['newIndependentCases']==18 and j['schedulingQualification']['newNativeCases']==3
t=j['actualTrial'];assert t['attempted'] and t['nativeFunctionalPathRevalidated'] and not t['originalControllerTerminalPassed']
assert t['originalFailurePreserved'] and not t['legacyPostparserIncludedInPreauditManifest'] and t['boundFilesFrozen']==83
assert t['checkpointCreatedAndVerified'] and t['independentOwnerVerifiedBeforeChanges'] and t['independentOwnerDeadlineSeconds']==45
assert all(t['cleanup'].values()) and t['baselineAuditRecovered']['configurationMatches']
assert t['recoveryAuditUsedOriginalLockedFreshnessPredicates'] and t['recoveryAuditCannotAuthorizeNss']
assert t['automaticExpiryNotExercisedThisTrial'] and t['retirementExplicitAndEarly']
n=t['nativeExperiment'];assert n['actualAcceleratedFlows']==2 and n['wan']==1 and n['fullTcpMark']==n['fullUdpMark']==65536
assert n['sameNat'] and n['zoneZero'] and n['packetTagsEstablishedBeforeLearning'] and n['nativeFullStateRevalidated']
assert n['nativeRenewals']==1 and n['sameQueuePlanAcrossPhases'] and not n['allSteamFlowsAccelerated']
assert [p['name'] for p in n['phases']]==['A','B','A2'] and [p['acceleratedCount'] for p in n['phases']]==[0,2,0]
assert all(300<p['lan4DownMbps']<450 and p['samples']==11 for p in n['phases'])
assert n['leafCounters']['bulk']['packets']==6171 and n['leafCounters']['rt']['packets']==517
assert t['parserCorrection']['checks']==7 and t['parserCorrection']['posttrialValidationSourcesNowFrozen']
assert hashlib.sha256((root/'code/work/nss41/parse-ecm-any-wan.mjs').read_bytes()).hexdigest()==t['parserCorrection']['candidateParserSha256']
assert not any(j['conclusions'][k] for k in ['nssCpuBenefitProvedThisRound','cs2QualityImprovementProved','realHighLoadNssLoopCompleted','secondWanExpansionAllowed'])
assert j['finalState']['protectedAudit']['ecmClosedAndZero'] and j['finalState']['closure']['passed']
k=json.loads((root/'evidence/nss42-mainline.json').read_text(encoding='utf-8'))
assert k['classifierConfigSha256']==c['classifierConfigSha256'] and not k['permanentClassifierChanged'] and not k['routerConfigurationWrites']
e=k['entry'];assert e['qualificationVersion']==2 and e['totalBoundInputs']==102 and e['historicalRuntimeBoundInputs']==68
assert e['workspaceGraphFiles']==40 and e['workspaceGraphEdges']==69 and e['postparserBound']
assert e['learningAndRecoveryAuditSeparated'] and e['originalLockedAuditPredicatesRetained'] and e['deadlinesUnchanged']
assert [e['initialAgeSeconds'],e['prelearningAgeSeconds'],e['lockedSourceAgeSeconds'],e['lockedPublicationAgeSeconds'],e['ownerDeadlineSeconds'],e['alignmentInnerSeconds'],e['alignmentOuterSeconds']]==[1,2,6,9,45,5,6]
assert e['externalSourceBindingHashOnly'] and not e['externalTransportCodeOrCredentialsCopied'] and not e['newEntryHardwareAbATested']
assert k['localChecks']['newCases']==90 and sum(v['checks'] for v in k['localChecks']['groups'].values())==90
assert k['localChecks']['groups']['parser']['checks']==43 and k['localChecks']['groups']['controller']['checks']==8
assert k['nativeDiagnosticRamChecks']['checks']==4 and k['nativeDiagnosticRamChecks']['simulation'] and not k['nativeDiagnosticRamChecks']['productionFaultInjected']
assert len(k['nativeReadonlyAudits'])==5 and all(v['passed'] and not v['nssAdmissionAllowed'] and v['ecmClosedAndZero'] for v in k['nativeReadonlyAudits'])
assert {v['auditPurpose'] for v in k['nativeReadonlyAudits']}=={'recovery','prewrite'}
w=k['stability'];assert w['samples']==w['successfulReads']==21 and w['failedReads']==0 and 599<w['seconds']<602
assert w['sameWorkerProducer'] and w['sameGuardianProducer'] and w['allSampledWorkersHealthy'] and w['allSampledGuardiansHealthy'] and w['ecmClosedAndZeroAllSamples']
assert w['sequenceAdvanced'] and w['sequenceNeverRegressed'] and not w['syntheticTrafficGenerated']
assert k['finalState']['protectedAudit']['ecmClosedAndZero'] and k['finalState']['sameProducerSinceNss41'] and k['finalState']['lastErrorBelongsToEarlierInstallation']
assert k['finalState']['closure']['passed'] and not k['actualFastPathTrial']['attempted']
assert k['actualFastPathTrial']['leafCounters'] is None and k['actualFastPathTrial']['gameTelemetry'] is None
p=k['priorComparabilityAssessment'];assert p['controlledBytes']==9803650 and p['controlledPackets']==6688 and p['counterWindowIncludesRetirement']
assert 4<p['controlledLeafByteSharePercent']<5 and not p['exactFastPathOffloadShareMeasured'] and not p['sameOfferedLoadVerified']
assert not any(k['conclusions'][v] for v in ['newProductionDeploymentInstalled','realHighLoadNssTrialExecutedThisRound','nssCpuBenefitProvedThisRound','cs2JitterLossMissCaptured','completeHighLoadLifecycleQualified','secondWanExpansionAllowed'])
timing=json.loads((root/'evidence/nss42-stability-timing.json').read_text())['rows'];assert len(timing)==21 and all(r['ecmAcceleratedCount']==0 for r in timing)
assert hashlib.sha256((root/'code/work/nss42/parse-ecm-any-wan.mjs').read_bytes()).hexdigest()==k['localChecks']['groups']['parser']['testedSourceManifest']['work/nss42/parse-ecm-any-wan.mjs']
assert k['repositoryReplay']['passed'] and k['repositoryReplay']['checks']==65 and not k['repositoryReplay']['routerAccess'] and not k['repositoryReplay']['privateHardwareStateRead']
assert not k['reportVerification']['browserRendered']
m=json.loads((root/'evidence/nss43-mainline.json').read_text(encoding='utf-8'))
assert m['classifierConfigSha256']==c['classifierConfigSha256'] and not m['permanentClassifierChanged']
assert not m['routerConfigurationWrites'] and not m['nssEntryChanged']
assert m['budgetMbps']==20 and m['gateFlows']=={'tcp':1,'udp':1} and m['ownerDeadlineSeconds']==45
assert m['localChecks']['checks']==20 and m['localChecks']['passed'] and not m['localChecks']['routerAccess']
assert len(m['readonlyAudits'])==2 and all(a['passed'] and a['ecmClosedAndZero'] and not a['nssAdmissionAllowed'] for a in m['readonlyAudits'])
assert m['sourceProof']['sources']==13 and m['sourceProof']['readonlyOnly'] and not m['sourceProof']['newProductionEntryQualified']
for source,expected in m['sourceProof']['sourceHashes'].items():
    assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==expected,source
load=json.loads((root/'evidence/nss43-load-profile.json').read_text(encoding='utf-8'))
assert load['samples']==13 and 48<load['seconds']<49 and load['bulkInstancesObserved']==23
assert 270<load['performance']['interfaces']['lan4']['txMbps']<285 and load['performance']['timeSqueezeDelta']==49
assert len(load['intervals'])==12 and len(load['flowRates'])==20
assert load['byWan']['5']['wholeWindowInstances']==0 and not load['nssAdmissionAllowed']
assert load['allSamplesEcmClosedAndZero'] and load['sameClassifierProducer']
assert not load['scope']['sensitivityPredictsCpuOrLatency'] and not load['scope']['actualSteamPayloadRateMeasured']
assert not m['priorAbaObservedLoadComparison']['similarObservedLoad'] and not m['priorAbaObservedLoadComparison']['permitsCausalCpuClaim']
assert m['queueBudget']['captureAfterSteamProfile'] and all(r['unitsVerifiedByAdjacentReads'] for r in m['queueBudget']['rows'])
assert m['finalState']['classifierHealthy'] and m['finalState']['sameProducerSinceOpening'] and m['finalState']['closure']['passed']
assert m['localFailures'][0]['successfulReads']==0 and m['localFailures'][0]['calls']==13 and m['localFailures'][0]['originalErrorsRetained']
assert not any(m['decision'][v] for v in ('raiseBudgetNow','expandFlowsNow','changeTtlNow','criterionAuthorizesNss'))
assert not m['actualFastPathTrial']['attempted'] and m['actualFastPathTrial']['leafCounters'] is None and m['actualFastPathTrial']['gameTelemetry'] is None
assert not any(m['conclusions'][v] for v in ('nssCpuBenefitProvedThisRound','cs2JitterLossMissCaptured','completeHighLoadLifecycleQualified','secondWanExpansionAllowed'))
assert m['reportVerification']['sourceValidated'] and not m['reportVerification']['browserRendered']
v=json.loads((root/'evidence/nss44-mainline.json').read_text(encoding='utf-8'))
assert v['classifierConfigSha256']==c['classifierConfigSha256'] and not v['permanentClassifierChanged']
assert not v['routerConfigurationWrites'] and v['originalNss42EntryUnmodified']
assert v['budgetMbps']==20 and v['gateFlows']=={'tcp':1,'udp':1} and v['ownerDeadlineSeconds']==45
t=v['actualAttempt']
assert t['attempted'] and t['realApplicationPairFound'] and t['selectedWan']==1
assert t['fullTcpMark']==t['fullUdpMark']==65536 and t['sameNat'] and t['zoneZero']
assert not t['originalControllerTerminalPassed'] and t['originalFailurePreserved'] and t['boundSourceFilesFrozen']==102
assert t['rejectedBeforeCheckpointOrStaging'] and t['prewriteAlignmentFailed'] and t['alignmentPolls']==39
assert t['fullSourceSequencesObserved']==[13555,13556] and t['fullPublicationDelays']==[2.91,3.01]
assert t['everyPollHealthy'] and not any(t[k] for k in ('checkpointCreated','independentExperimentOwnerStarted','productionMutationAttempted','wanChanged','nssQdiscCreated','packetTagsInstalled','gateModuleLoaded','ecmOpened','forwardingABACompleted','nativeFastPathAffinityVerified'))
assert t['leafCounters'] is None and t['gameTelemetry'] is None
failed=json.loads((root/'evidence/nss44-failed-admission-timing.json').read_text(encoding='utf-8'))
assert not failed['passed'] and len(failed['rows'])==39
assert all(r['healthy'] and r['sourceAge']>2 for r in failed['rows'])
restart=v['classifierRestart']
assert restart['observed'] and not restart['injectionOrManualRestart'] and not restart['configChanged']
assert not restart['firstExactRecoveryPassed'] and restart['recoveryRawStatus']==31744 and restart['recoverySeconds']==6.18
assert restart['oldFailureRetained'] and restart['newProducerHealthy'] and restart['sameNewProducerSincePostrefusalInspection']
assert not restart['restartCausationByNssExperimentProved'] and not restart['fullHighLoadLifecycleQualified']
candidate=v['readonlySchedulingCandidate']
assert not candidate['installedOrUsedForProduction'] and not candidate['productionEntryQualified']
assert candidate['originalFullAuditRetained'] and candidate['originalSchedulerLibraryUnchanged']
assert candidate['ageLimitsUnchanged']=={'schedulingHintSeconds':2,'lockedSourceSeconds':6,'lockedPublicationSeconds':9,'initialLearningSeconds':1,'prelearningSeconds':2}
assert candidate['boundsUnchanged']=={'innerWaitSeconds':5,'outerWaitSeconds':6,'ownerSeconds':45}
assert candidate['nativeReadonlyAuditPassed'] and candidate['nativeReadonlyEcmClosedAndZero'] and not candidate['nativeReadonlyAdmissionAllowed']
assert not candidate['highLoadNssProof'] and not candidate['fixesClassifierApplyOrRecoveryTimeout']
assert v['localChecks']['passed'] and v['localChecks']['checks']==30 and not v['localChecks']['routerAccess'] and not v['localChecks']['productionEntryQualified']
assert v['sourceProof']['sources']==16 and v['sourceProof']['readonlyOrUninstalledCandidatesOnly']
for source,expected in v['sourceProof']['sourceHashes'].items():
    assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==expected,source
light=v['passiveFollowup']
assert light['frames']==105 and 27<light['seconds']<28 and light['performance']['lan4DownMbps']<1
assert light['naturalLightLoad'] and light['actualApplicationPairNotConfirmed'] and light['notMatchedForwardingABA'] and not light['syntheticTrafficGenerated']
hash_candidate=v['hashCandidate']
assert not hash_candidate['installed'] and not hash_candidate['hashesCached'] and hash_candidate['allPayloadsStillCheckedEveryInvocation']
assert hash_candidate['payloadCount']==12 and hash_candidate['nativeReadOnlyPairs']==3 and hash_candidate['savedMeanMs']<40
assert hash_candidate['hashChildCpuNotCounted'] and not hash_candidate['resolvedPublicationDelay']
assert all(v['finalState']['protectedAudit'].values()) and v['finalState']['classifierHealthy'] and v['finalState']['closure']['passed']
assert not v['finalState']['sameProducerSinceOpening'] and v['finalState']['lastErrorIsThisRoundsRestart']
assert not any(v['conclusions'][k] for k in ('newNssFastPathTrialExecuted','nssCpuBenefitProvedThisRound','cs2JitterLossMissCaptured','classifierHighLoadStable','readinessCandidateProvedUnderHighLoad','completeHighLoadLoopPassed','secondWanExpansionAllowed'))
assert c['classifierWorkerRestartObservedThisRound'] and c['historicalNss44StaleSnapshotRejection'] and not c['historicalNss44FirstExactRecoveryPassed']
assert c['finalClassifierHealthyAndExactOwnedAuditPassed']
assert v['reportVerification']['sourceValidated'] and not v['reportVerification']['browserRendered']
x45=json.loads((root/'evidence/nss45-mainline.json').read_text(encoding='utf-8'))
assert x45['deploymentReference']=='work/nss39/deployment-latest.json' and x45['classifierConfigSha256']==c['classifierConfigSha256']
assert x45['routerConfigurationWrites'] and not x45['permanentClassifierChanged'] and not x45['nssOpened']
assert x45['originalNss42EntryUnmodified'] and x45['budgetMbps']==20 and x45['gateFlows']=={'tcp':1,'udp':1} and x45['ownerDeadlineSeconds']==45
assert x45['openingObservation']['naturalPriorWorkerExitsObserved']==3 and not x45['openingObservation']['manualRestartOrFaultInjection']
trials=x45['temporaryClassifierTrials'];assert len(trials)==2
assert trials[0]['changedSources']==['backend.lua'] and sorted(trials[1]['changedSources'])==['conntrack-source.lua','guardian.lua','worker.lua']
for trial in trials:
    assert trial['checkpointDownloadedHashAndGzipVerified'] and trial['independentRollbackVerifiedBeforeProductionWrite'] and trial['independentOfControlConnection']
    assert trial['automaticExpirySeconds']==180 and trial['stageAutomaticExpirySeconds']==480 and not trial['committed'] and not trial['nssEnabled']
    assert trial['activeWindow']['samples']==35 and trial['activeWindow']['allHealthy'] and trial['activeWindow']['oneProducer']
    assert trial['activeOriginalCompleteProtectionAuditPassed'] and trial['originalAgeAndPermissionPredicatesRetained']
    rb=trial['automaticRollback'];assert rb['passed'] and rb['automaticExpiryWithoutControllerRollback'] and rb['previousBackendRestored'] and rb['previousClassifierHealthyAndFresh'] and rb['ecmClosedAndZero']
    assert trial['predeadlineFailClosedExitExpectedAndObserved'] and trial['full180SecondContinuousHealthNotClaimed']
    assert not trial['realOverloadOrStaleSoftwareFaultInjected'] and not trial['highLoadLifecycleQualified']
assert x45['localChecks']['totalUniqueLocalCases']==114 and x45['localChecks']['recoveryUniqueCases']==24
assert x45['nativeChecks']['realQueryChildCases']==7 and x45['nativeChecks']['doesNotAddRepeatedCasesToLocalTotal']
assert x45['sourceProof']['sources']==53 and not x45['sourceProof']['nssProductionEntryQualified']
for source,expected in x45['sourceProof']['sourceHashes'].items():
    assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==expected,source
bench=x45['recoveryReadReuse'];assert bench['originalEmptyReadCalls']==60 and bench['candidateEmptyReadCalls']==40 and bench['nativeReadonlyPairs']==3
assert bench['candidateMeanSeconds']<bench['originalMeanSeconds'] and bench['freshPrewriteAndPostwriteChecksRetained'] and bench['cacheDisabledAfterFirstWrite']
assert bench['journalProjectedEmptyInRam'] and not bench['nativeSelectorsRecoveredDuringBenchmark'] and bench['tcChildCpuExcludedFromObserverCpu'] and bench['doesNotResolveHistoricalHighLoadRecoveryTimeout']
row=x45['rowOverflowCandidate'];assert row['localChecks']==row['sameNativeRamCases']==48 and row['nativeRealQueryChildCases']==7
assert row['temporarilyInstalledThenAutomaticallyRestored'] and row['noPartialRowsAdmitted'] and row['queryCleanupProofRequired'] and row['unknownErrorsRemainTerminal']
expiry=x45['softwareExpiryCandidate'];assert expiry['localHelperCases']==expiry['sameNativeHelperCases']==34 and expiry['localJournalIntegrationCases']==expiry['sameNativeJournalCases']==8
assert expiry['originalSixSecondSoftwareDeadline'] and expiry['originalSixSecondMutationDeadline'] and expiry['publicationAgeSeconds']==9
assert expiry['bothPublicationsWithdrawnBeforePreciseRecovery'] and expiry['unknownWriterPreserved']
assert not any(expiry[k] for k in ['realApplyChildAndServiceFaultRecoveryQualified','installed','productionEntryQualified'])
query=json.loads((root/'evidence/nss45-query-cleanup.json').read_text());assert query['passed'] and query['checks']==7 and query['routerWrites']==False and not query['installed']
assert all(v['actualQueryChildReaped'] and v['syntheticOutput'] and v['realNativeChild'] for v in query['cases'])
assert all(x45['finalState']['protectedAudit'].values()) and x45['finalState']['classifierHealthy'] and x45['finalState']['closure']['passed']
assert x45['finalState']['lastErrorIsControlledTrialPredeadlineExit'] and not x45['finalState']['lastErrorBelongsToCurrentWorker']
assert not any(x45['conclusions'][k] for k in ['newNssFastPathTrialExecuted','nssCpuBenefitProvedThisRound','cs2JitterLossMissCaptured','classifierHighLoadStable','completeSoftwareExpiryChildServiceRecoveryProved','completeHighLoadLoopPassed','secondWanExpansionAllowed'])
assert c['plannedClassifierReplacementAndRollbackThisRound'] and c['experimentalConfigurationWritesThisRound'] and c['temporaryClassifierTrials']==2 and c['allNaturalExpiryRestorationsPassed']
assert not c['nssOpenedThisRound'] and c['lastErrorIsControlledTrialPredeadlineExit'] and not c['lastErrorBelongsToCurrentWorker']
assert x45['reportVerification']['sourceValidated'] and not x45['reportVerification']['browserRendered']
x46=json.loads((root/'evidence/nss46-mainline.json').read_text());historical46=json.loads((root/'evidence/nss46-runtime.json').read_text())
assert historical46['round']=='NSS46' and historical46['deploymentReference']==x46['deploymentReference']=='work/nss46/deployment-latest.json'
assert x46['classifierCommitted'] and x46['permanentClassifierChanged'] and not x46['nssOpened']
assert historical46['classifierConfigSha256']==x46['classifierConfigSha256'] and historical46['classifierReliabilityChangesRetained']==3
assert len(x46['retainedChanges'])==3 and all(p['committed'] and p['checkpointDownloadedHashAndGzipVerified'] and p['independentRollbackVerifiedBeforeWrite'] and p['independentRollbackSeconds']==180 for p in x46['retainedChanges'])
expiry=x46['realSoftwareExpiry'];assert expiry['passed'] and expiry['realApplyChild'] and expiry['applyChildReaped'] and expiry['expiredProducerBound'] and expiry['refusedBeforeBatch'] and expiry['exactRecoveryConfirmed']
assert 6<expiry['ageAtWriteCheck']<7 and expiry['actualRecoveryChildSeconds']<1 and expiry['realConnectionMetadataUnmodified'] and not expiry['fakeFlow']
crash=x46['realWorkerCrash'];assert crash['passed'] and crash['oneExactWorkerCrash'] and crash['oldPid']!=crash['newPid'] and crash['recoveredSeconds']<9
assert len(x46['independentFaultTrialRollbacks'])==2 and all(p['automaticNaturalTransactionRollbackPassed'] and p['allFourSourcesConfigAndPointerRestored'] for p in x46['independentFaultTrialRollbacks'])
entry=x46['entry'];assert entry['passed'] and entry['boundInputs']==112 and entry['localCases']==99 and entry['classificationHintSourceAgeSeconds']<2
assert entry['fullLockedAudit']['passed'] and entry['nssLuaPayloadsByteIdenticalToQualifiedNss39'] and entry['initialAndNativeDeadlinesUnchanged'] and not entry['actualNssTrafficTestThisRound']
assert x46['budgetMbps']==20 and x46['gateFlows']=={'tcp':1,'udp':1} and x46['ownerDeadlineSeconds']==45 and x46['softwareSourceAgeSeconds']==6 and x46['publicationAgeSeconds']==9
for name in ['worker.lua','guardian.lua','conntrack-source.lua']:
    assert hashlib.sha256((root/'code/deployed-classifier'/name).read_bytes()).hexdigest()==hashlib.sha256((root/'code/work/nss46'/name).read_bytes()).hexdigest()
assert hashlib.sha256((root/'code/deployed-classifier/backend.lua').read_bytes()).hexdigest()==hashlib.sha256((root/'code/work/nss45/candidate-backend.lua').read_bytes()).hexdigest()
assert x46['sourceProof']['sources']==84
for source,expected in x46['sourceProof']['sourceHashes'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==expected
assert all(x46['finalState']['protectedAudit'].values()) and x46['finalState']['classifierHealthy'] and x46['finalState']['closure']['passed']
assert not x46['finalState']['lastErrorBelongsToCurrentWorker'] and x46['finalState']['lastErrorIsControlledTrialPredeadlineExit']
assert x46['retainedNaturalObservation']['passed'] and x46['retainedNaturalObservation']['samples']==60
assert not any(x46['conclusions'][k]for k in ['newNssFastPathTrialExecuted','nssCpuBenefitProvedThisRound','cs2JitterLossMissCaptured','classifierHighLoadStable','completeHighLoadLoopPassed','secondWanExpansionAllowed'])
x49=json.loads((root/'evidence/nss49-mainline.json').read_text());latest=json.loads((root/'evidence/nss49-runtime.json').read_text())
assert latest['round']=='NSS49' and latest['deploymentReference']==x49['deploymentReference']=='work/nss47/deployment-latest.json'
assert latest['classifierConfigSha256']==x49['classifierConfigSha256']=='478818d553903aa859c853cab99383e038d4d325f500d68843ffff8b7517a900'
assert latest['pureIpv4ParserCacheRetained'] and latest['nssOpenedThisRound'] and not latest['nssPermanentlyEnabled']
assert latest['realForwardingABACompleted'] and not latest['completePerformanceAndGameAcceptance']
assert all(latest['audit'][k] for k in ['passed','protectedConfigurationUnchanged','exactOwnedNativeAudit','ecmClosedAndZero']) and latest['finalClosure']['passed']
cache=x49['classifierCache'];assert cache['committed'] and cache['natural180SecondRollbackVerified'] and cache['secondInstallationCheckpointAndIndependentRollbackVerified']
assert cache['freshCtIdentityMarkNatAndCountersNotCached'] and cache['policyAndSourceBoundAndDeadlinesUnchanged'] and cache['cacheCap']==1024
assert cache['differentialCases']==4550 and cache['nativeRows']==527 and cache['nativeTraversalsPerVersion']==80 and cache['completeNativeSnapshotsEqual']==3
assert 26<cache['nativeParserCpuReductionPercent']<27 and not cache['wholeRouterCpuBenefitProved']
assert hashlib.sha256((root/'code/deployed-classifier/classifier-core.lua').read_bytes()).hexdigest()==cache['candidateSha256']
assert hashlib.sha256((root/'code/work/nss29/classifier-core.lua').read_bytes()).hexdigest()==cache['originalSha256']
assert cache['boundedChecks']==9612 and cache['distinctCacheAddresses']==1200 and not cache['rejectedLiteralScannerInstalled']
for round in ['nss47','nss48','nss49']:
    frozen=json.loads((root/'evidence'/f'{round}-source-proof.json').read_text())
    assert frozen['sources']==len(frozen['sourceHashes']) and frozen['notAdditionalProductionAdmission']
    for source,expected in frozen['sourceHashes'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==expected
entry=x49['entry'];assert entry['boundInputs']==121 and entry['localEntryCases']==99 and entry['nativeRamSyntheticCases']==13
assert entry['onlyInitialZeroTrafficReadinessChanged'] and entry['initialTagNoTrafficWaitSeconds']==1.2 and entry['wrongTagStillImmediatelyRejected'] and entry['zeroTrafficCannotAuthorizeNss']
assert entry['ownerSeconds']==45 and entry['initialSourceAgeSeconds']==1 and entry['prelearningSourceAgeSeconds']==2 and entry['epochSeconds']==5
assert entry['controlledBudgetMbps']==20 and entry['tcpSlots']==entry['udpSlots']==1
assert hashlib.sha256((root/'code/work/nss49/fast-path.lua').read_bytes()).hexdigest()==entry['fastHelperSha256']
for name in ['classified-tags.lua','classifier.lua','core-guard-phase.lua','qos-physical.lua','tag-normalizer.lua','wan-scope.lua','state-node.lua','module-stage-guardian.lua']:
    assert hashlib.sha256((root/'code/work/nss49'/name).read_bytes()).hexdigest()==hashlib.sha256((root/'code/work/nss48'/name).read_bytes()).hexdigest()
assert len(x49['actualFailures'])==2 and all(not p['passed'] and not p['nssPermitOpened'] and p['rollbackPassed'] and p['afterOriginalFullAuditPassed'] for p in x49['actualFailures'])
actual=x49['actualForwardingABA'];assert actual['passed'] and not actual['realHumanGameplay'] and actual['oneWan']==2 and actual['ctMark']==131072
assert actual['checkpointDownloadedAndHashAndGzipVerified'] and actual['independent45SecondOwnerVerifiedBeforeWrites'] and actual['explicitEarlyRetirement'] and not actual['natural45SecondExpiryTriggeredThisCase']
assert actual['scopedRollbackPassed'] and actual['afterFullProtectionAuditPassed'] and actual['nativeRenewals']==1 and actual['initialTagGetterSeconds']<0.3
phases=actual['measurements']['phases'];assert [p['acceleratedCount'] for p in phases]==[0,2,0] and all(5<p['seconds']<5.1 for p in phases)
assert not actual['throughputMatched'] and not actual['offeredLoadEqualityProven'] and not actual['cpuAndGameAcceptancePassed']
assert actual['measurements']['totalThroughputRelativeSpread']>0.1 and actual['measurements']['selectedWanThroughputRelativeSpread']>0.1
for kind,tag in [('tcp',2399469568),('udp',2399535104)]:
    p=actual['runtimeState'][kind];assert p['accelerated'] and p['natCorrect'] and p['wanAffinity']==2 and p['ctMark']==131072 and p['downTag']==tag and p['upTag']==0
assert actual['measurements']['leafDeltasAroundFastPath']['counters']['8f06:']=={'bytes':644562,'packets':713,'drops':0}
client=x49['clientEvidence'];assert not client['nssBHudCovered'] and client['assignedPhaseFrameCounts']['B']==0 and client['hudAbsenceNotConvertedToZero']
assert client['secondAttempt']['actualBulkCandidates']==0 and not client['secondAttempt']['routerWrites'] and not client['secondAttempt']['nssPermissionGranted'] and client['secondAttemptNoForwardingABA']
assert x49['automaticGuiSession']['clientTestServerExited'] and not x49['automaticGuiSession']['humanPlayThisRound'] and not x49['automaticGuiSession']['newPurchaseOrUnownedGameInstalled']
assert x49['finalState']['sameCacheRetainedWorker'] and x49['finalState']['closure']['passed'] and x49['reportVerification']['sourceValidated']
assert not any(x49['conclusions'][k]for k in ['wholeRouterCpuBenefitProved','clientNssBHudMetricsCaptured','realHumanExperienceProved','completeHighLoadLifecycleQualified','secondSimultaneousWanAllowed','sharedBudgetAllowed','upstreamSubmitted'])
x52=json.loads((root/'evidence/nss52-mainline.json').read_text());current=json.loads((root/'evidence/nss52-runtime.json').read_text())
assert current['round']=='NSS52' and current['classifierConfigSha256']==x52['classifierConfigSha256']==x49['classifierConfigSha256']
assert current['deploymentReference']=='work/nss47/deployment-latest.json' and not x52['permanentClassifierChanged']
assert not x52['ecmOpenedThisTurn'] and not x52['forwardingABACompletedThisTurn'] and not current['nssOpenedThisTurn']
assert current['historicalNss49FunctionABACompleted'] and not current['completePerformanceAndGameAcceptance']
assert x52['budgetMbps']==20 and x52['gateFlows']=={'tcp':1,'udp':1} and x52['ownerSeconds']==45 and x52['allOriginalDeadlinesUnchanged']
assert len(x52['attempts'])==6 and sum(a['productionTemporaryStageOccurred']for a in x52['attempts'])==4
assert all(not a['passed'] and not a['ecmPermitOpened'] and not a['forwardingABACompleted']for a in x52['attempts'])
assert [a['completedPhases']for a in x52['attempts']]==[[],[],[],['A'],['A'],[]]
for a in x52['attempts']:
    if a['productionTemporaryStageOccurred']:
        assert a['rollbackPassed'] and a['stageCleanupPassed'] and a['afterFullProtectedAuditPassed']
        assert a['checkpointHashAndGzipVerified'] and a['independent45SecondRollbackVerifiedBeforeWrite']
        assert not a['natural45SecondNssExpiryProvedThisCase']
    else:assert a['rejectedBeforeCheckpointOrStaging'] and not a['routerConfigurationWrites']
assert x52['serviceEpochFix']['localBoundaryCases']==24 and x52['serviceEpochFix']['entryBoundInputs']==128
assert x52['serviceEpochFix']['allDuringExperimentServiceChangesRejected'] and x52['serviceEpochFix']['nativeFullReadonlyAuditPassed']
assert x52['phase51']['entryBoundInputs']==140 and x52['phase51']['highLoadReadOnlySuccesses']==1 and x52['phase51']['highLoadReadOnlyAttempts']==3
assert not x52['phase51']['highLoadReliablyFixed'] and not x52['phase51']['forwardingSucceededThisEntry']
assert [g['passedAttempts']for g in x52['readonlyProfiling']['groups']]==[3,0,3,1]
candidate=x52['phase52UninstalledCandidate'];assert candidate['reusedProcessModelCases']==22 and candidate['newParentDifferentialCases']==12
assert len(candidate['caseResults'])==34 and all(c['passed']for c in candidate['caseResults'])
assert candidate['notInstalled'] and candidate['notBoundToProductionEntry'] and not candidate['highLoadQualified']
assert candidate['waitFreshByteIdentical'] and candidate['benchmarkIsPureParserOnly'] and candidate['notWholeRouterCpuBenefit']
assert len(candidate['liveReadOnlyPhases'])==2 and all(p['scanSeconds']<=0.2 and p['birthAgeSeconds']<=0.2 for p in candidate['liveReadOnlyPhases'])
for round in ['nss50','nss51','nss52']:
    frozen=json.loads((root/'evidence'/f'{round}-source-proof.json').read_text())
    assert frozen['sources']==len(frozen['sourceHashes']) and frozen['notAdditionalProductionAdmission']
    for source,expected in frozen['sourceHashes'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==expected
phase51=(root/'code/work/nss51/core-guard-phase.lua').read_text();phase52=(root/'code/work/nss52/core-guard-phase.lua').read_text()
delta=json.loads((root/'code/work/nss52/phase-delta.json').read_text());assert phase52.replace(delta['to'],delta['from'])==phase51
assert hashlib.sha256((root/'code/work/nss52/core-guard-phase.lua').read_bytes()).hexdigest()==candidate['sourceSha256']
for p in x52['partialSoftwareMeasurements']['cases']:
    assert p['softwareForwarding'] and p['commonNssLan4QueueTreeStaged'] and not p['ecmPermitOpened'] and p['phasesBAndA2Missing']
    assert p['samples']==11 and not p['cpuBenefitConclusion'] and not p['gameBenefitConclusion'] and p['rollbackPassed']
client=x52['clientSoftwareMeasurements'];assert client['noNssPhaseOccurred'] and not client['humanGameplay']
assert [len(p['frames'])for p in client['cases']]==[4,5] and all(p['phase']=='A' and p['fullContextVerified']for p in client['cases'])
assert x52['clientEndState']['steam']['downloadCompleted'] and not x52['clientEndState']['steam']['launched']
assert x52['clientEndState']['cs2']['restored'] and x52['clientEndState']['cs2']['testServerExited']
assert x52['finalState']['sameCacheRetainedWorker'] and current['classifierWorkerContinuousAfterCacheRetain']
assert all(current['audit'][k]for k in ['passed','protectedConfigurationUnchanged','exactOwnedNativeAudit','ecmClosedAndZero']) and current['finalClosure']['passed']
assert not any(x52['conclusions'][k]for k in ['nssBClientHudCapturedThisTurn','softwareVersusNssCpuBenefitProvedThisTurn','realHumanExperienceProved','highLoadPhaseFixValidated','secondWanExpansionAllowed','sharedBudgetAllowed','upstreamSubmitted'])
assert x52['reportVerification']['sourceValidated'] and not x52['reportVerification']['browserRendered']
x53=json.loads((root/'evidence/nss53-mainline.json').read_text())
current53=json.loads((root/'evidence/nss53-runtime.json').read_text())
assert current53['round']=='NSS53' and current53['classifierConfigSha256']==x53['classifierConfigSha256']==x49['classifierConfigSha256']
assert current53['historical52RuntimePreservedSha256']==hashlib.sha256((root/'evidence/nss52-runtime.json').read_bytes()).hexdigest()
assert current53['deploymentReference']=='work/nss47/deployment-latest.json'
assert not x53['routerConfigurationWrites'] and not x53['permanentClassifierChanged'] and not x53['ecmOpenedThisTurn']
assert not current53['experimentalConfigurationWritesThisTurn'] and not current53['nssOpenedThisTurn']
assert current53['qualifiedExperimentalEntry']=='work/nss53/real-session.mjs' and current53['qualifiedExperimentalEntryBoundInputs']==159
assert current53['entryPreparationQualified'] and current53['entryNotInstalledAsResidentClassifier'] and not current53['entryFullHighLoadForwardingQualified']
assert x53['budgetMbps']==20 and x53['gateFlows']=={'tcp':1,'udp':1} and x53['ownerSeconds']==45 and x53['allOriginalDeadlinesUnchanged']
entry53=json.loads((root/'code/work/nss53/entry-qualified.json').read_text())
assert entry53['passed'] and entry53['baseBoundInputs']+entry53['newBoundInputs']==x53['entry']['boundInputs']==159
for source,expected in entry53['sourceManifest'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==expected,source
assert entry53['controllerDecisionAndRecoveryBarriersUnchanged'] and entry53['sameSourceDiagnosticOnly'] and entry53['waitFreshByteIdentical']
assert x53['entry']['historical99And13CasesReusedNotReexecuted'] and not x53['entry']['actualNssABATestedThisEntry']
assert (root/'code/work/nss53/core-guard-phase.lua').read_bytes()==(root/'code/work/nss52/core-guard-phase.lua').read_bytes()
diag53=x53['diagnostics'];assert diag53['localChecks']==60 and diag53['originalAdapterChecksReplayed']==21 and diag53['additionalLocalAssertions']==39
assert diag53['nativeDiagnosticHelperChecks']==14 and diag53['extraAdmissionClassificationReads']==0 and diag53['maximumAfterRejectionDiagnosticReads']==1
assert diag53['embeddedConsumerByteIdentical'] and diag53['originalAssertionsRetained'] and diag53['completeDiagnosticRequiresMatchingProducerAndQuery']
assert diag53['projectionAbsenceDoesNotProveFullCtAbsence'] and diag53['unknownDoesNotChangeDecisionOrRetry']
assert diag53['nativeActualReadyLight']['sameSourceCompleteDiagnosticObserved']
high_ready=diag53['nativeActualReadyUnderDownload'];assert high_ready['passed'] and high_ready['syntheticAbsentKeys'] and high_ready['ecmClosedAndZero']
assert not high_ready['sameSourceCompleteDiagnosticObserved'] and high_ready['completeSlotReasons'] is None
assert high_ready['completeDiagnosticUnavailable'].endswith('Complete diagnostic source differs') and high_ready['retryable'] is False
load53=x53['phaseDiscovery'];assert load53['actualAttempts']==load53['actualPasses']==6
assert len(load53['readonlyWindows'])==2 and all(len(g['attempts'])==3 for g in load53['readonlyWindows'])
load_rows=[p for g in load53['readonlyWindows'] for p in g['attempts']]
assert all(p['passed'] and p['allNewChildBirthAgesWithinOriginal200ms'] and 0<=p['acceptedMaxBirthAgeSeconds']<=0.2 for p in load_rows)
assert min(p['lan4Mbps'] for p in load_rows)>290 and max(p['lan4Mbps'] for p in load_rows)>360
assert sum(p['lan4Mbps']>=300 for p in load_rows)==load53['attemptsAtLeast300Mbps']==4
assert load53['maxCallbackSeconds']<=0.2+1e-8 and load53['maxObservedBirthAgeSeconds']<0.2
assert all(g['ecmClosedThroughout'] and g['noRouterWrites'] and g['guardUntouched'] and g['completeConsumerCandidatesPathExecuted'] for g in load53['readonlyWindows'])
assert x53['applicationReadiness']['actualGameCandidates']==0 and x53['applicationReadiness']['actualBulkCandidates']==24 and x53['applicationReadiness']['sameWanPairs']==0
assert x53['steamLoad']['pausedConfirmed'] and x53['steamLoad']['networkBpsAfterPause']==0 and not x53['steamLoad']['purchaseOrUninstallOccurred'] and not x53['steamLoad']['newGameLaunched']
assert x53['finalState']['sameCacheRetainedWorkerAndGuardianAndProducer'] and x53['finalState']['sequenceAdvanced']
assert all(current53['audit'][k] for k in ['passed','protectedConfigurationUnchanged','exactOwnedNativeAudit','ecmClosedAndZero']) and current53['finalClosure']['passed']
assert not any(x53['conclusions'][k] for k in ['newNssFastPathTrialExecuted','softwareVersusNssCpuBenefitProvedThisTurn','gameJitterLossMissCapturedThisTurn','realHumanExperienceProved','completeHighLoadLifecycleQualified','completeHighLoadLoopPassed','secondWanExpansionAllowed','sharedBudgetAllowed','upstreamSubmitted'])
assert x53['reportVerification']['sourceValidated'] and not x53['reportVerification']['browserRendered']
frozen53=json.loads((root/'evidence/nss53-source-proof.json').read_text());assert frozen53['sources']==len(frozen53['sourceHashes'])==24 and frozen53['notAdditionalProductionAdmission']
for source,expected in frozen53['sourceHashes'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==expected,source
x63=json.loads((root/'evidence/nss63-mainline.json').read_text())
runtime63=json.loads((root/'evidence/nss63-runtime.json').read_text())
assert runtime63['round']=='NSS63' and runtime63['deploymentReference']=='work/nss47/deployment-latest.json'
assert runtime63['historical53RuntimePreservedSha256']==hashlib.sha256((root/'evidence/nss53-runtime.json').read_bytes()).hexdigest()
assert runtime63['classifierConfigSha256']==x63['classifierConfigSha256']==x53['classifierConfigSha256']
assert not x63['permanentClassifierChanged'] and x63['routerConfigurationWrites'] and x63['ecmOpenedThisTurn']
assert x63['budgetMbps']==20 and x63['gateFlows']=={'tcp':1,'udp':1} and x63['ownerSeconds']==45 and x63['allOriginalDeadlinesUnchanged']
cases=x63['actualCases'];assert len(cases)==12 and sum(a['productionTemporaryStageOccurred'] for a in cases)==5
assert sum(a['ecmPermitOpened'] for a in cases)==1 and not any(a['controllerPassed'] or a['completeABA'] for a in cases)
assert [a['completedPhases'] for a in cases]==[[],[],[],['A','B'],[],['A'],[],[],[],[],['A'],[]]
for a in cases:
    if a['productionTemporaryStageOccurred']:
        assert a['wan'] in (1,2) and ((a['ctMark']>>16)&255)==a['wan'] and a['checkpointDownloadedHashAndGzipVerified'] and a['independent45SecondRollbackVerifiedBeforeWrite']
        assert a['independentOfControlConnection'] and a['scopedRollbackPassed'] and a['stageCleanupPassed'] and all(a['rollbackFlags'].values())
        assert not a['natural45SecondExpiryProvedThisCase']
        assert a['immediateAfterOriginalFullAuditPassed'] or a['laterOriginalFullRecoveryAuditPassed']
    else:assert a['rejectedBeforeCheckpointOrStaging'] and not a['ecmPermitOpened']
assert [a['wan'] for a in cases if a['productionTemporaryStageOccurred']]==[1,2,2,2,2]
assert len(x63['offlineEvidenceCorrection']['changes'])==4 and x63['offlineEvidenceCorrection']['actualRouterSelectionAndAdmissionUnaffected']
assert cases[9]['immediateAfterOriginalFullAuditPassed'] is False and cases[9]['configurationComparisonPassed'] is None
assert cases[9]['laterOriginalFullRecoveryAuditPassed']
entry63=json.loads((root/'evidence/nss63-entry-binding.json').read_text());assert entry63['passed'] and entry63['boundInputs']==241
assert entry63['moduleResolutionChecked'] and entry63['originalFullAuditAndExactQueryCheckRetained'] and entry63['nss62NativeRamChecksReused']==15
assert entry63['notInstalled'] and not entry63['fullHighLoadAbaQualified']
for source,expected in entry63['sourceManifest'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==expected,source
for n in range(54,64):
    proof=json.loads((root/'evidence'/f'nss{n}-source-proof.json').read_text())
    assert proof['sources']==len(proof['sourceHashes']) and proof['privateConnectionAndCapturesExcluded'] and proof['notAdditionalProductionAdmission']
    for source,expected in proof['sourceHashes'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==expected,source
assert (root/'code/work/nss63/core-guard-phase.lua').read_bytes()==(root/'code/work/nss62/core-guard-phase.lua').read_bytes()
proof63v2=json.loads((root/'evidence/nss63-source-proof-v2.json').read_text())
assert proof63v2['sources']==1 and proof63v2['notAdditionalProductionAdmission']
for source,expected in proof63v2['sourceHashes'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==expected,source
assert (root/'code/work/nss63/payload.mjs').read_bytes()==(root/'code/work/nss59/payload.mjs').read_bytes()
partial=x63['partialForwarding'];assert partial['analysisPassed'] and not partial['controllerPassed'] and partial['missingA2']
assert partial['actualAcceleratedStateValidated'] and partial['oneWan']==1 and partial['ctMark']==65536 and partial['connectionCount']==2
assert [p['acceleratedCount'] for p in partial['phases']]==[0,2] and all(p['samples']==11 for p in partial['phases'])
assert partial['twoPhaseOnlyThroughputSpread']['total']>0.1 and partial['twoPhaseOnlyThroughputSpread']['selectedWan']>0.1
assert partial['leafDeltasAroundFastPath']['counters']['8f06:']=={'bytes':503139,'packets':549,'drops':0}
assert partial['renewals']==1 and all(partial['rollback'].values()) and not partial['cpuBenefitConclusive']
for slot in ['tcp','udp']:
    assert partial['runtimeProof'][slot]['accelerated'] and partial['runtimeProof'][slot]['natCorrect'] and partial['runtimeProof'][slot]['wanAffinity']==1
client=x63['clientHud'];assert client['actualClientHudCaptured'] and len(client['frames'])==10 and client['missingA2'] and not client['humanGameplay']
assert client['clockUncertaintyMs']==100 and client['rollingOrPeakDisplayNotIndependentInstantaneousSamples'] and not client['gameBenefitAccepted']
assert all(f['fullContextVisuallyVerified'] for f in client['frames']) and sum(f['phase']=='B' for f in client['frames'])==5
assert x63['clientEndState']['steam']['currentNetworkBps']==0 and x63['clientEndState']['steam']['immediateQueueItems']==0
assert x63['clientEndState']['steam']['previouslyPausedQueueAutomaticallyAdvanced'] and len(x63['clientEndState']['steam']['downloadedTestTitlesThisTurn'])==4
assert not x63['clientEndState']['steam']['purchased'] and not x63['clientEndState']['steam']['newTitlesLaunched']
assert x63['clientEndState']['cs2']['restored'] and x63['clientEndState']['cs2']['serverExited']
assert x63['finalState']['naturalWorkerRestartObserved'] and not x63['finalState']['sameCacheRetainedWorkerThroughout']
assert not x63['finalState']['manualWorkerRestartOrCrashInjected'] and not x63['finalState']['workerRestartCauseProved']
assert runtime63['naturalWorkerRestartObservedThisTurn'] and not runtime63['classifierWorkerContinuousAfterCacheRetain']
assert all(runtime63['audit'][k] for k in ['passed','protectedConfigurationUnchanged','exactOwnedNativeAudit','ecmClosedAndZero']) and runtime63['finalClosure']['passed']
assert runtime63['entryFullHighLoadForwardingQualified'] is False and not runtime63['nssPermanentlyEnabled']
assert not any(x63['conclusions'][k] for k in ['softwareVersusNssCpuBenefitProved','gameBenefitProved','realHumanExperienceProved','completeHighLoadLifecycleQualified','completeHighLoadLoopPassed','secondWanExpansionAllowed','sharedBudgetAllowed','upstreamSubmitted'])
assert x63['reportVerification']['sourceValidated'] and not x63['reportVerification']['browserRendered']
x64=json.loads((root/'evidence/nss64-mainline.json').read_text())
runtime64=json.loads((root/'evidence/nss64-runtime.json').read_text())
assert runtime64['round']==x64['round']=='NSS64' and runtime64['deploymentReference']=='work/nss47/deployment-latest.json'
assert runtime64['historical63RuntimePreservedSha256']==hashlib.sha256((root/'evidence/nss63-runtime.json').read_bytes()).hexdigest()
assert runtime64['classifierConfigSha256']==x64['classifierConfigSha256']==runtime63['classifierConfigSha256']
assert not any(x64[k]for k in ['permanentClassifierChanged','routerConfigurationWrites','newNssForwardingExperiment','ecmOpenedThisTurn'])
assert x64['checkpointCount']==x64['rollbackTrialCount']==0 and x64['allOriginalDeadlinesUnchanged']
assert x64['currentEntry']=={'path':'work/nss63/real-session.mjs','boundInputs':241,'unchanged':True,'fullHighLoadForwardingQualified':False}
assert x64['budgetMbps']==20 and x64['gateFlows']=={'tcp':1,'udp':1} and x64['ownerSeconds']==45
encode64=x64['completeEncoding'];assert encode64['passed'] and encode64['cases']==29 and encode64['projectValidation']['cases']==36
assert encode64['completePublicationFieldEquality'] and encode64['sameFrozenInMemoryFixtureWithinPairs']
assert encode64['realFlows']==319 and encode64['originalProjectorContractDifferentiallyChecked'] and not encode64['exactOriginalProjectorFunctionUsed']
assert 23<encode64['cpuReductionPercent']<25 and encode64['notWholeRouterCpuBenefit'] and not encode64['controlledHighNetworkLoad']
scale64=x64['encodingOnlyScale'];assert scale64['passed'] and scale64['excludesProjectionCpu'] and scale64['syntheticScaleFixture']
assert [v['flows']for v in scale64['rows']]==[128,256,512,1024] and all(v['semanticEquality']for v in scale64['rows'])
assert scale64['rows'][-1]['originalCpu']>2*scale64['rows'][-1]['candidateCpu']
assert scale64['installedJsonStringifyIsC'] and not scale64['candidateInstalled']
natural64=x64['naturalPipeline'];assert natural64['passed'] and natural64['readonly'] and natural64['lan4Mbps']<1
assert len(natural64['completeObservedCycles'])==2 and natural64['visibilityAreObservationBounds'] and natural64['observerCostIncluded']
assert not natural64['backgroundLoadControlled'] and not natural64['nssAdmissionAllowed']
candidate64=x64['candidateWorker'];compiled64=x64['nativeCompilation']
assert candidate64['candidateOnly'] and not candidate64['installed'] and candidate64['candidateBytes']==compiled64['bytes']==32019
assert candidate64['originalAllDeadlinesRetained'] and candidate64['classifierPolicyAndLearningUnchanged']
assert compiled64['compiledExactCandidateInRam'] and compiled64['originalWorkerByteRestorationVerified']
assert not any(compiled64[k]for k in ['executed','installed','configurationWrites','nssAdmissionAllowed'])
assert candidate64['candidateWorkerSha256']==compiled64['sha256']==hashlib.sha256((root/'code/work/nss64/candidate-worker.lua').read_bytes()).hexdigest()
assert candidate64['originalWorkerSha256']==hashlib.sha256((root/'code/deployed-classifier/worker.lua').read_bytes()).hexdigest()
assert [v['code']for v in x64['failedPreparationCases']]==[124,2] and all(v['originalEvidenceRetainedLocally']for v in x64['failedPreparationCases'])
assert x64['historicalLatency']['historicalEvidenceReanalyzedNotNewExperiment'] and not x64['historicalLatency']['allPostStampTimeAttributedToJson']
final64=x64['finalState'];assert final64['sameWorkerGuardianAndProducerSinceOpening']
assert all(final64[k]for k in ['ecmStoppedAndZero','noActiveTransaction','noStaging','noExperimentState','noExperimentalModule'])
assert final64['protectedAudit']['passed'] and final64['protectedAudit']['originalFullLockedAudit']
assert all(runtime64['audit'][k]for k in ['passed','protectedConfigurationUnchanged','exactOwnedNativeAudit','ecmClosedAndZero']) and runtime64['finalClosure']['passed']
assert not any(runtime64[k]for k in ['experimentalConfigurationWritesThisTurn','nssOpenedThisTurn','naturalWorkerRestartObservedThisTurn','publicationCandidateInstalled','nssPermanentlyEnabled','completePerformanceAndGameAcceptance'])
assert not any(x64['conclusions'][k]for k in ['wholeRouterCpuBenefitProved','highLoadPublicationFixed','realHumanGameImprovementProved','completeMatchedABACompleted','secondWanExpansionAllowed','upstreamSubmitted'])
proof64=json.loads((root/'evidence/nss64-source-proof.json').read_text())
assert proof64['sources']==len(proof64['sourceHashes'])==20 and proof64['notAdditionalProductionAdmission'] and not proof64['candidateInstalled']
assert x64['proofBoundary']['old99And13NotReexecuted'] and x64['proofBoundary']['noNewGameDownloadOrGameGuiThisTurn']
for source,expected in proof64['sourceHashes'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==expected,source
assert x64['reportVerification']['sourceValidated'] and not x64['reportVerification']['browserRendered']
x65=json.loads((root/'evidence/nss65-mainline.json').read_text());runtime65=json.loads((root/'evidence/nss65-runtime.json').read_text())
assert x65['round']==runtime65['round']=='NSS65'
assert runtime65['historical64RuntimePreservedSha256']==hashlib.sha256((root/'evidence/nss64-runtime.json').read_bytes()).hexdigest()
assert runtime65['historical63RuntimePreservedSha256']==hashlib.sha256((root/'evidence/nss63-runtime.json').read_bytes()).hexdigest()
assert x65['classifierConfigSha256']==runtime65['classifierConfigSha256']==runtime64['classifierConfigSha256']
assert x65['routerConfigurationWrites'] and x65['publicationCandidateActuallyInstalled'] and not x65['candidateRetainedAtEnd']
assert not x65['permanentClassifierChanged'] and not x65['nssOpenedThisTurn'] and not x65['newNssForwardingExperiment']
assert x65['checkpointCount']==x65['rollbackTrialCount']==1
assert x65['currentEntry']=={'path':'work/nss63/real-session.mjs','boundInputs':241,'unchanged':True,'candidateEntryBindingCreated':False}
assert x65['candidateWorkerSha256']==candidate64['candidateWorkerSha256']
assert x65['onlyPublicationBoundaryAndTransactionIdentityChanged'] and x65['sourcePolicyClassifierLearningAndAllDeadlinesUnchanged']
assert x65['untouchedNormalizerGuardianBackendCore'] and x65['originalNonSnapshotSerializationUnchanged']
protect65=x65['protection'];assert all(protect65[k]for k in ['checkpointDownloadedHashAndGzipVerified','independentStageGuardianVerifiedBeforeUpload','independentProductionUndoVerifiedBeforeMutation','independentOfControlConnection','originalSixSecondRunnerUnchanged'])
assert protect65['productionUndoSeconds']==180 and protect65['stageGuardianSeconds']==480
install65=x65['installation'];assert install65['passed'] and install65['workerBytes']==32019 and install65['guardVerifiedIndependentParent']==1
assert install65['originalFullLockedAuditPassesDuringTrial']==2 and install65['candidateWorkerGuardianAndProducerContinuousBetweenAudits']
assert install65['sequenceBetweenAudits']==[16,37] and all(0<=x<6 for x in install65['fullSnapshotSourceAgeSecondsAtAudits'])
assert x65['rollback']['passed'] and x65['rollback']['automaticExpiryWithoutControllerRollback'] and x65['rollback']['previousWorkerAndConfigRestored']
assert x65['rollback']['unchangedNormalizerAndGuardianVerified'] and x65['rollback']['unchangedBackendVerified'] and x65['rollback']['unchangedClassifierCoreVerified']
assert x65['stageCleanup']['onlyOwnedPassiveStageCancelled'] and x65['stageCleanup']['productionNatural180SecondUndoAlreadyProven'] and x65['stageCleanup']['stageAbsent']
assert not x65['stageCleanup']['stageNatural480SecondExpiryClaimed']
assert len(x65['naturalWindows'])==3
for w in x65['naturalWindows']:
    assert w['passed'] and w['lan4Mbps']<1 and w['seconds']>=4 and w['observerCostIncluded']
    assert not w['backgroundLoadControlled'] and not w['nssAdmissionAllowed'] and w['allEcmCountsZeroThroughout']
    assert w['visibilityAreObservationBounds'] and len(w['completeObservedCycles'])==1
assert x65['proofBoundary']['liveTrialNotJsonContractCaseRerun'] and x65['proofBoundary']['naturalWindowsNotMatchedTrafficComparison']
assert not x65['proofBoundary']['oldNative36And29Reexecuted'] and not x65['proofBoundary']['old99And13Reexecuted']
assert x65['proofBoundary']['noNewGameDownloadOrGameGuiThisTurn'] and not x65['proofBoundary']['realSteamHighLoadPresent'] and not x65['proofBoundary']['realCs2Present']
assert x65['conclusions']['publicationCandidateLiveAndOriginalAuditPassed'] and x65['conclusions']['preciseIndependentNaturalUndoPassed']
assert not any(x65['conclusions'][k]for k in ['highLoadPublicationFixed','wholeRouterCpuBenefitProved','realHumanGameImprovementProved','completeMatchedABACompleted','secondWanExpansionAllowed','upstreamSubmitted'])
assert all(x65['finalState'][k]for k in ['ecmStoppedAndZero','noActiveTransaction','noStaging','noExperimentState','noExperimentalModule'])
assert x65['finalState']['expectedWorkerAndGuardianRestartForTrialAndRestore'] and not x65['finalState']['sameInstancesSinceOpening']
assert runtime65['expectedClassifierRestartForTrialAndRestore'] and runtime65['independentNatural180SecondUndoVerified'] and runtime65['finalClosure']['passed']
assert runtime65['workerPid']==20030 and runtime65['guardianPid']==20031
assert all(runtime65['audit'][k]for k in ['passed','protectedConfigurationUnchanged','exactOwnedNativeAudit','ecmClosedAndZero'])
assert not any(runtime65[k]for k in ['naturalWorkerRestartObservedThisTurn','publicationCandidateInstalled','nssPermanentlyEnabled','completePerformanceAndGameAcceptance'])
proof65=json.loads((root/'evidence/nss65-source-proof.json').read_text())
assert proof65['sources']==len(proof65['sourceHashes'])==8 and proof65['notAdditionalProductionAdmission'] and proof65['publicationCandidateInstalledDuringTrial'] and not proof65['candidateRetainedAtEnd']
for source,expected in proof65['sourceHashes'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==expected,source
assert x65['reportVerification']['sourceValidated'] and not x65['reportVerification']['browserRendered']
for number in (66,67):
    new=json.loads((root/f'evidence/nss{number}-mainline.json').read_text())
    proof=json.loads((root/f'evidence/nss{number}-source-proof.json').read_text())
    assert new['round']==f'NSS{number}' and new['classifierConfigSha256']==runtime65['classifierConfigSha256']
    assert new['publicationCandidateActuallyInstalled'] and new['routerConfigurationWrites']
    assert new['checkpointCount']==new['rollbackTrialCount']==1
    assert new['protection']['productionUndoSeconds']==180 and new['protection']['stageGuardianSeconds']==480
    assert new['protection']['independentOfControlConnection'] and new['protection']['originalSixSecondRunnerUnchanged']
    assert new['rollback']['passed'] and new['rollback']['automaticExpiryWithoutControllerRollback']
    assert new['rollback']['previousWorkerAndConfigRestored'] and new['untouchedNormalizerGuardianBackendCore']
    assert new['currentEntry']=={'path':'work/nss63/real-session.mjs','boundInputs':241,'unchanged':True,'candidateEntryBindingCreated':False}
    assert not new['candidateRetainedAtEnd'] and not new['permanentClassifierChanged'] and not new['nssOpenedThisTurn']
    assert new['installation']['candidateWorkerGuardianAndProducerContinuousBetweenAudits']
    assert all(a['passed']and a['queryAge']<6 and a['originalFullLockedAudit']and a['ecmStoppedAndZero']for a in new['candidateAudits'])
    assert len(new['candidateAudits'])==(2 if number==66 else 3)
    loaded=[w for w in new['actualTrafficWindows']if w['mode']=='publication-candidate-loaded']
    assert len(loaded)==(2 if number==66 else 3)
    assert all(w['passed']and w['seconds']>=4 and w['observerCostIncluded']and not w['backgroundLoadControlled']and not w['nssAdmissionAllowed']for w in loaded)
    assert all(w['ecmStoppedAndZeroThroughout']for w in new['actualTrafficWindows'])
    assert all((w['lan4Mbps']>=300)==(number==67)for w in loaded)
    assert new['conclusions']['testedAbove300MbpsPublicationWindowSupported']==(number==67)
    assert not any(new['conclusions'][k]for k in ['generalHighLoadStabilityProved','wholeRouterCpuBenefitProved','realHumanGameImprovementProved','completeMatchedABACompleted','secondWanExpansionAllowed','upstreamSubmitted'])
    assert new['lateExpiredContextFailure']['afterIndependentProductionDeadline'] and new['lateExpiredContextFailure']['expiredCandidateContextAgainstRestoredOriginal']
    assert not new['lateExpiredContextFailure']['sourceStalenessFailure'] and new['lateExpiredContextFailure']['originalFailurePreserved']
    assert new['client']['networkLoadNoLongerRunning'] and new['client']['noGameLaunched'] and new['client']['noPurchaseOrUninstall']
    assert new['stageCleanup']['stageAbsent'] and not new['stageCleanup']['stageNatural480SecondExpiryClaimed']
    assert new['finalState']['protectedAudit']['passed'] and all(new['finalState'][k]for k in ['ecmStoppedAndZero','noActiveTransaction','noStaging','noExperimentState','noExperimentalModule'])
    assert proof['sources']==len(proof['sourceHashes'])==(10 if number==66 else 12)
    assert proof['notAdditionalProductionAdmission'] and not proof['candidateRetainedAtEnd']
    for source,expected in proof['sourceHashes'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==expected
    assert new['reportVerification']['sourceValidated'] and not new['reportVerification']['browserRendered']
new67=json.loads((root/'evidence/nss67-mainline.json').read_text());latest=json.loads((root/'evidence/nss67-runtime.json').read_text())
assert latest['round']=='NSS67' and latest['workerPid']==9454 and latest['guardianPid']==9455
assert latest['historical65RuntimePreservedSha256']==hashlib.sha256((root/'evidence/nss65-runtime.json').read_bytes()).hexdigest()
assert latest['historical64RuntimePreservedSha256']==hashlib.sha256((root/'evidence/nss64-runtime.json').read_bytes()).hexdigest()
assert latest['finalClosure']['passed'] and latest['above300MbpsPublicationActuallyObserved']
assert not latest['publicationCandidateInstalled'] and not latest['nssOpenedThisTurn'] and not latest['candidateEntryBindingCreated']
assert all(latest['audit'][k]for k in ['passed','protectedConfigurationUnchanged','exactOwnedNativeAudit','ecmClosedAndZero'])
assert 0<new67['exactRestoredAuditLoad']['queryAge']<6 and new67['exactRestoredAuditLoad']['lan4Mbps']>=300
assert new67['exactRestoredAuditLoad']['measurementCoversActualAudit'] and new67['exactRestoredAuditLoad']['passed']
assert new67['client']['downloadPausedAtUiPercent']==17 and new67['client']['networkBpsAtFinalUi']==new67['client']['diskBpsAtFinalUi']==0
assert not new67['client']['downloadCompleted'] and new67['client']['partialAuthorizedDownloadLeftPaused']
x68=json.loads((root/'evidence/nss68-mainline.json').read_text());l68=json.loads((root/'evidence/nss68-runtime.json').read_text())
assert l68['round']=='NSS68' and x68['candidateRetainedAtEnd'] and l68['publicationCandidateInstalled']
assert l68['deploymentReference']=='work/nss68/deployment-latest.json' and l68['classifierConfigSha256']==x68['classifierConfigSha256']
assert l68['candidateEntryBindingCreated'] and l68['qualifiedExperimentalEntryBoundInputs']==257
assert x68['entry']['baseInputs']==241 and x68['entry']['overlayInputs']==16 and x68['entry']['checks']==17
assert not x68['entry']['nativeGateStagingExecutedThisTurn'] and not l68['nssOpenedThisTurn']
assert x68['retention']['remoteCommittedReceiptVerified'] and x68['retention']['checkpointCount']==1
assert x68['retention']['productionUndoSeconds']==180 and x68['retention']['stageGuardianSeconds']==480
assert not x68['retention']['newNaturalUndoTrialClaimed'] and x68['workerLifecycle']['naturalRestartObserved']
assert x68['workerLifecycle']['applyRawStatus']==256 and x68['workerLifecycle']['tcSupervisorByteIdenticalToPrevious47']
assert l68['finalClosure']['passed'] and l68['audit']['passed'] and l68['audit']['ecmClosedAndZero']
assert l68['historical67RuntimePreservedSha256']==hashlib.sha256((root/'evidence/nss67-runtime.json').read_bytes()).hexdigest()
assert x68['actualTrafficWindow']['lan4Mbps']<300 and not x68['actualTrafficWindow']['qualifiedHighLoad']
assert all(not x68['conclusions'][k]for k in ['wholeRouterCpuBenefitProved','realHumanExperienceProved','completeMatchedABACompleted','generalLongTermStabilityProved','upstreamSubmitted'])
assert len(manifest['sources'])>868
proof77=json.loads((root/'evidence/nss77-source-proof.json').read_text())
assert hashlib.sha256(json.dumps(manifest['sources'][:868],sort_keys=True,separators=(',',':')).encode()).hexdigest()==proof77['historicPrefixCanonicalSha256']
proof78=json.loads((root/'evidence/nss78-source-proof.json').read_text())
assert hashlib.sha256(json.dumps(manifest['sources'][:990],sort_keys=True,separators=(',',':')).encode()).hexdigest()==proof78['historicPrefixCanonicalSha256']
assert 992==868+proof77['sources']+proof78['sources']
for source,digest in proof77['sourceHashes'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==digest
x77=json.loads((root/'evidence/nss77-mainline.json').read_text());rt77=json.loads((root/'evidence/nss77-runtime.json').read_text())
assert x77['latestBoundInputs']==355 and x77['latestCandidateRamChecks']==9 and not x77['latestCandidateLiveTested']
assert len(x77['trials'])==10 and sum(t['independentStageBeforeWriteVerified']for t in x77['trials'])==9
assert all(t['protectedBaselineMatches']for t in x77['trials'])
for t in x77['trials']:
    assert not t['completeABA'] and not t['cpuBenefitClaimed'] and not t['humanExperienceClaimed']
    if t['independentStageBeforeWriteVerified']:assert t['checkpointVerified'] and all(t['stageUndo'].values()) and all(t['restore'].values())
assert sum(t['acceleratedCountTwoObserved']for t in x77['trials'])==1
assert x77['knownReasons']['nativeSixSecondExpiryAnd45SecondOwnerUnchanged']
assert x77['client']['computerUseStoppedByPhysicalEscape'] and x77['client']['taskGuardWithdrawn']['passed']
assert not x77['client']['latestFinalUiRestoreClaimed']
assert rt77['round']=='NSS77' and not rt77['entryFullHighLoadForwardingQualified'] and not rt77['nssPermanentlyEnabled']
assert rt77['finalClosure']['passed'] and rt77['audit']['configurationMatches'] and rt77['audit']['originalFullLockedAudit']
assert rt77['historical68RuntimePreservedSha256']==hashlib.sha256((root/'evidence/nss68-runtime.json').read_bytes()).hexdigest()

rt78=json.loads((root/'evidence/nss78-runtime.json').read_text())
x78=json.loads((root/'evidence/nss78-mainline.json').read_text())
assert rt78['round']=='NSS78' and rt78['qualifiedExperimentalEntry']=='work/nss77/real-session.mjs'
assert rt78['qualifiedExperimentalEntryBoundInputs']==355 and not rt78['entryFullHighLoadForwardingQualified']
assert rt78['historical77RuntimePreservedSha256']==hashlib.sha256((root/'evidence/nss77-runtime.json').read_bytes()).hexdigest()
assert all(rt78['audit'][k] for k in ['passed','configurationMatches','originalFullLockedAudit','ecmStoppedAndZero','noStaging','noExperimentState','noExperimentalModule'])
assert not any(x78['changes'].values()) and not x78['load']['highLoad']
assert x78['load']['sameWanPairs']==0 and x78['timing']['samples']==154 and x78['timing']['publications']==6
assert x78['timing']['initialAgeEligible']==64 and x78['timing']['originalTagAgeEligible']==82
assert x78['timing']['jointFreshSamples']==2 and x78['interpretation']['jointFreshSamplesAreNotAdmission']
assert not x78['interpretation']['selectedPairAdmissionVerified'] and not x78['interpretation']['cpuOrSoftirqBenefitProved']
assert not x78['interpretation']['nss77LiveForwardingTested'] and not x78['rollback']['newRollbackTestClaimed']
assert proof78['sources']==len(proof78['sourceHashes'])==2 and proof78['notAdditionalProductionAdmission']
for source,digest in proof78['sourceHashes'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==digest

proof82=json.loads((root/'evidence/nss82-source-proof.json').read_text())
assert proof82['historicPrefixSources']==992 and proof82['sources']==58
assert len(manifest['sources'])>=992+proof82['sources']
assert hashlib.sha256(json.dumps(manifest['sources'][:992],sort_keys=True,separators=(',',':')).encode()).hexdigest()==proof82['historicPrefixCanonicalSha256']
for source,digest in proof82['sourceHashes'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==digest
assert proof82['privateOwnedHostBootstrapExcluded'] and proof82['completePrivateSourceInputsRetained']
trials82=json.loads((root/'evidence/nss82-trials.json').read_text())
assert len(trials82)==5 and sum(t['passed'] for t in trials82)==2
assert [t['ecmOpened'] for t in trials82]==[True,False,True,False,True]
for t in trials82:
    assert t['checkpointDownloadedShaAndGzipVerified'] and t['guardianVerifiedBeforeFirstWrite']
    assert t['guardianPpid']==1 and t['independentOwnerSeconds']==45 and all(t['rollback'].values())
    assert t['baseline']['configurationMatches'] and all(t['baseline']['checks'].values())
    assert t['beforeFullAudit']['passed'] and t['afterFullAudit']['passed']
    assert t['beforeFullAudit']['exactOwnedNativeAudit'] and t['afterFullAudit']['exactOwnedNativeAudit']
    assert t['sourceInputsCurrentBytesMatchActualRun'] and not t['gameQualityConclusion'] and not t['highLoad300MbpsConclusion']
    for c in t['softwareTagCounters'].values():
        assert all(c[k]['packets']==c[k]['bytes']==0 for k in c if k.endswith('_unexpected') or k=='udp_post_neighbor_nonzero')
matched82=json.loads((root/'evidence/nss82-matched18.json').read_text())
sat82=json.loads((root/'evidence/nss82-saturated32.json').read_text())
for m in (matched82,sat82):
    assert m['passed'] and [p['acceleratedCounts'] for p in m['phases']]==[[0],[2],[0]]
    assert m['qosParentMbps']==20 and m['renewals']==1 and m['protectedConfigurationRestored']
    assert all(5<=p['seconds']<=6.5 and p['sampleCount']==11 for p in m['phases'])
    assert all(p['timeSqueezeDelta']==p['softnetDropDelta']==0 for p in m['phases'])
    assert not m['gameQualityConclusion'] and not m['highLoad300MbpsConclusion']
tcp82=[p['clientTcpMbps'] for p in matched82['phases']];assert max(tcp82)/min(tcp82)<1.01
assert sat82['leafCountersAcrossBObservation']['8f05:']['dropped']==143
assert sat82['leafCountersAcrossBObservation']['8f06:']['dropped']==0
assert sat82['phases'][1]['udp']['sent']==sat82['phases'][1]['udp']['received']==213
tags82=json.loads((root/'evidence/nss82-tag-reader.json').read_text())
ack=tags82['actual80FinalAckCounters'];down=tags82['actual81InitialDownCounters']
assert ack['tcp_post_up_expected']['packets']-ack['tcp_post_up_total']['packets']==1
assert ack['tcp_post_up_expected']['bytes']-ack['tcp_post_up_total']['bytes']==60
assert down['tcp_post_down_expected']['packets']-down['tcp_post_down_total']['packets']==1
assert down['tcp_post_down_expected']['bytes']-down['tcp_post_down_total']['bytes']==1500
assert tags82['nativeQualification']['passed'] and tags82['nativeQualification']['cases']==17
assert tags82['secondGetterOriginalStrictPredicatesRetained'] and tags82['secondSnapshotPassed']
assert tags82['actual82RereadUsedTcpDownPredicate'] and not tags82['actual82AckPredicateLiveUseClaimed']
assert not tags82['firmwareMisTagProved'] and not tags82['kernelBugProved'] and not tags82['upstreamSubmitted']
x82=json.loads((root/'evidence/nss82-mainline.json').read_text());rt82=json.loads((root/'evidence/nss82-runtime.json').read_text())
assert x82['successfulCompleteABA']==2 and x82['stageCases']==5 and not x82['permanentClassifierChanged']
assert x82['matched18']['matchedShortWindowSoftirqBenefitSupported']
assert 50<x82['matched18']['relativeReductionAgainstMeanSoftwarePercent']<60
assert not x82['saturated32']['actualThroughputMatched'] and not x82['saturated32']['cpuBenefitAcceptance']
assert rt82['round']=='NSS82' and rt82['qualifiedExperimentalEntryBoundInputs']==405 and rt82['nssOpenedThisTurn']
assert not rt82['nssPermanentlyEnabled'] and not rt82['entryFullHighLoadForwardingQualified'] and not rt82['realHumanGameAcceptance']
assert all(rt82['audit'][k] for k in ['passed','configurationMatches','originalFullLockedAudit','ecmStoppedAndZero','noActiveTransaction','noStaging','noExperimentState','noExperimentalModule'])
assert rt82['workerPid']==4859 and rt82['guardianPid']==17139
assert rt82['historical78RuntimePreservedSha256']==hashlib.sha256((root/'evidence/nss78-runtime.json').read_bytes()).hexdigest()
closure82=json.loads((root/'evidence/nss82-endpoint-closure.json').read_text())
assert closure82['temporaryFirewallRulesRemaining']==0 and closure82['canonicalFirewallBaselineRestored']
assert closure82['ownedUnitInactiveMainPidZeroPortsClosed'] and closure82['clientExited'] and closure82['clientGuardPassed']

proof92=json.loads((root/'evidence/nss92-source-proof.json').read_text())
assert proof92['historicPrefixSources']==1050 and proof92['sources']==29
assert len(manifest['sources'])>=1050+proof92['sources']
assert hashlib.sha256(json.dumps(manifest['sources'][:1050],sort_keys=True,separators=(',',':')).encode()).hexdigest()==proof92['historicPrefixCanonicalSha256']
assert proof92['privateOwnedHostBootstrapExcluded'] and proof92['completePrivateSourceInputsRetained']
for source,digest in proof92['sourceHashes'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==digest
trials92=json.loads((root/'evidence/nss92-trials.json').read_text())
assert len(trials92)==6 and sum(t['passed']for t in trials92)==1
assert [t['ecmOpened']for t in trials92]==[False,False,False,False,True,False]
for t in trials92:
    assert t['checkpointDownloadedShaAndGzipVerified'] and t['guardianVerifiedBeforeFirstWrite']
    assert t['guardianPpid']==1 and t['independentOwnerSeconds']==45 and all(t['rollback'].values())
    assert t['baseline']['configurationMatches'] and all(t['baseline']['checks'].values())
    assert t['beforeFullAudit']['passed'] and t['afterFullAudit']['passed']
    assert t['sourceInputsCurrentBytesMatchActualRun'] and not t['gameQualityConclusion']
    for c in t['softwareTagCounters'].values():
        assert all(c[k]['packets']==c[k]['bytes']==0 for k in c if k.endswith('_unexpected')or k=='udp_post_neighbor_nonzero')
assert trials92[1]['clientFailure']['windowsStatusRenameEpermCaptured']
matched92=json.loads((root/'evidence/nss92-matched32.json').read_text())
assert matched92['passed'] and matched92['oneWan']==2 and matched92['requestedTcpMbps']==32 and matched92['qosParentMbps']==60
assert [p['acceleratedCounts']for p in matched92['phases']]==[[0],[2],[0]]
assert matched92['renewals']==2 and matched92['protectedConfigurationRestored']
tcp92=[p['clientTcpMbps']for p in matched92['phases']];assert max(tcp92)/min(tcp92)<1.01 and min(tcp92)>31
assert all(5<=p['seconds']<=6.5 and p['sampleCount']==11 and p['udp']['unreturned']==0 and p['timeSqueezeDelta']==p['softnetDropDelta']==0 for p in matched92['phases'])
assert all(x['dropped']==0 for x in matched92['leafCountersAcrossBObservation'].values())
assert not matched92['gameQualityConclusion'] and not matched92['highLoad300MbpsConclusion']
tags92=json.loads((root/'evidence/nss92-tag-reader.json').read_text())
assert tags92['nativeQualification']['passed'] and tags92['nativeQualification']['cases']==30
assert tags92['maximumRereadsPerGetter']==1 and tags92['monotonicAndCrossSnapshotOverlapRequired']
assert tags92['allWrongTagPacketAndByteCountersZeroRequired'] and tags92['completeExactOwnedPolicyNormalizerUnchanged']
assert tags92['bidirectionalPositiveCountersBeforeEcmRequired'] and tags92['initialMissingTrafficStillRefusedWithinOriginal1p2Seconds']
assert [x['key']for x in tags92['actual91TwoBoundaryBrackets']]==['tagsBeforeA2','tagsAfterA2']
assert all(x['reads']==1 and not x['nssAdmissionAllowed']for x in tags92['actual91TwoBoundaryBrackets'])
for key in ['tagsBeforeA2','tagsAfterA2']:
    first=trials92[4]['softwareTagCounters'][key+'First'];last=trials92[4]['softwareTagCounters'][key]
    for stem in ['tcp_post_up','tcp_post_down','udp_post_up','udp_post_down']:
        for unit in ['packets','bytes']:
            a,b=first[stem+'_total'][unit],first[stem+'_expected'][unit]
            c,d=last[stem+'_total'][unit],last[stem+'_expected'][unit]
            assert c>=a and d>=b and a<=d and b<=c
assert not tags92['firmwareMisTagProved'] and not tags92['kernelBugProved'] and not tags92['upstreamSubmitted']
obs92=json.loads((root/'evidence/nss92-load-observations.json').read_text())
assert obs92['endpointTap88']['outgoingEchoes']==obs92['endpointTap88']['matchingClientRepliesAtRead']==249
assert obs92['endpointTap89']['outgoingEchoes']==246 and obs92['endpointTap89']['matchingClientRepliesAtRead']==33
assert obs92['capture87NoTxWasInstrumentationLimitation'] and obs92['routerOrUpstreamOrWindowsRootCauseUnproved']
assert obs92['clientPublicationFixQualification']['passed'] and obs92['clientPublicationFixQualification']['cases']==3
closures92=json.loads((root/'evidence/nss92-endpoint-closure.json').read_text());assert len(closures92)==9
for c in closures92:
    assert c['temporaryFirewallRulesRemaining']==0 and c['canonicalFirewallBaselineRestored']
    assert c['ownedUnitInactiveMainPidZeroPortsClosed'] and c['clientExited'] and c['clientGuardPassed']
    assert c['independentFirewallExpirySeconds']==180 and c['independentClientDeadlineSeconds']==210
x92=json.loads((root/'evidence/nss92-mainline.json').read_text());rt92=json.loads((root/'evidence/nss92-runtime.json').read_text())
assert x92['round']==rt92['round']=='NSS92' and x92['stageCases']==6 and x92['successfulCompleteABA']==1
assert not x92['permanentClassifierChanged'] and not x92['productionFirmwareKernelChanged']
assert x92['matched32']['actualThroughputMatched'] and 60<x92['matched32']['relativeReductionAgainstMeanSoftwarePercent']<70
assert not x92['offered52']['matchedABACompleted'] and x92['offered52']['noEcmOpeningInTwoUpdatedGetterTrials']
assert x92['qos']['rateAccuracyAt60NotYetSaturationTested']
identity92=trials92[4]['acceleratedIdentityProof']
assert identity92['passed'] and identity92['connectionCount']==2
assert identity92['proof']['tcp']['upTag']==identity92['proof']['udp']['upTag']==0
assert x92['qos']['onlyLanEgressDownlinkLeavesInstalled'] and not x92['qos']['acceleratedUplinkQosGuaranteed']
assert not x92['humanCs2Acceptance'] and not x92['highLoad300MbpsAcceptance'] and not x92['secondWanEnabled'] and not x92['upstreamSubmitted']
assert rt92['qualifiedExperimentalEntry']=='work/nss91/controlled-session.mjs' and rt92['qualifiedExperimentalEntryBoundInputs']==555
assert rt92['historical82RuntimePreservedSha256']==hashlib.sha256((root/'evidence/nss82-runtime.json').read_bytes()).hexdigest()
assert rt92['workerPid']==4859 and rt92['guardianPid']==17139 and not rt92['nssPermanentlyEnabled'] and not rt92['realHumanGameAcceptance']
assert all(rt92['audit'][k]for k in ['passed','configurationMatches','originalFullLockedAudit','ecmStoppedAndZero','noActiveTransaction','noStaging','noExperimentState','noExperimentalModule'])
assert x92['reportVerification']['sourceValidated'] and not x92['reportVerification']['browserRendered']

proof98=json.loads((root/'evidence/nss98-source-proof.json').read_text())
assert proof98['historicPrefixSources']==1079 and proof98['sources']==31
assert len(manifest['sources'])==1079+proof98['sources']
assert hashlib.sha256(json.dumps(manifest['sources'][:1079],sort_keys=True,separators=(',',':')).encode()).hexdigest()==proof98['historicPrefixCanonicalSha256']
for source,digest in proof98['sourceHashes'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==digest
assert proof98['privateOwnedHostBootstrapExcluded'] and proof98['completePrivateSourceInputsRetained'] and proof98['notAdditionalProductionAdmission']
trials98=json.loads((root/'evidence/nss98-trials.json').read_text())
assert [t['passed']for t in trials98]==[False,True,True]and[t['ecmOpened']for t in trials98]==[False,True,True]
assert [t['sourceInputs']for t in trials98]==[533,556,580]
for t in trials98:
    assert t['checkpointDownloadedShaAndGzipVerified']and t['guardianVerifiedBeforeFirstWrite']and t['guardianPpid']==1 and t['independentOwnerSeconds']==45
    assert all(t['rollback'].values())and t['baseline']['configurationMatches']and all(t['baseline']['checks'].values())
    assert t['beforeFullAudit']['passed']and t['afterFullAudit']['passed']and t['sourceInputsCurrentBytesMatchActualRun']and not t['gameQualityConclusion']
    for c in t['softwareTagCounters'].values():assert all(c[k]['packets']==c[k]['bytes']==0 for k in c if k.endswith('_unexpected')or k=='udp_post_neighbor_nonzero')
assert trials98[0]['beforeStageUdpBaseline']['sent']==120 and trials98[0]['beforeStageUdpBaseline']['returned']==0
assert not trials98[0]['completeABA']and not trials98[0]['phases']and'no bidirectional traffic'in trials98[0]['error']
m98=json.loads((root/'evidence/nss98-matched48.json').read_text());sat98=json.loads((root/'evidence/nss98-congested40.json').read_text())
for m in [m98,sat98]:
    assert m['passed']and[p['acceleratedCounts']for p in m['phases']]==[[0],[2],[0]]and m['renewals']==2
    assert m['classifierToLeafAndNatAffinityVerified']and m['checkpointAndIndependentOwnerRollbackVerified']and m['protectedConfigurationRestored']
    assert not m['gameQualityConclusion']and not m['highLoad300MbpsConclusion']and m['leafStatsAsynchronous']
    assert all(5<=p['seconds']<=6.5 and p['sampleCount']==11 and p['timeSqueezeDelta']==p['softnetDropDelta']==0 for p in m['phases'])
assert m98['requestedTcpMbps']==48 and m98['qosParentMbps']==60 and m98['oneWan']==2
b,a2=m98['phases'][1:];assert abs(b['clientTcpMbps']/a2['clientTcpMbps']-1)<.001
assert max(p['clientTcpMbps']for p in m98['phases'])/min(p['clientTcpMbps']for p in m98['phases'])>1.01
assert m98['phases'][0]['udp']['unreturned']==77 and b['udp']['unreturned']==a2['udp']['unreturned']==0
assert all(v['dropped']==0 for v in m98['leafCountersAcrossBObservation'].values())
assert sat98['requestedTcpMbps']==48 and sat98['qosParentMbps']==40 and sat98['oneWan']==3
assert sat98['leafCountersAcrossBObservation']['8f05:']['dropped']==148 and sat98['leafCountersAcrossBObservation']['8f06:']['dropped']==0
assert sat98['phases'][1]['udp']['sent']==sat98['phases'][1]['udp']['received']==223
assert trials98[2]['nativeQueueOptions']['nativeOptionsValidated']and trials98[2]['nativeQueueOptions']['queueCount']==4 and trials98[2]['nativeQueueOptions']['classCount']==5
assert trials98[2]['leafAdditionalStatsDelta']['8f05:']['dropOverlimit']==0
for t in trials98[1:]:
    p=t['acceleratedIdentityProof'];assert p['passed']and p['connectionCount']==2
    assert p['proof']['tcp']['upTag']==p['proof']['udp']['upTag']==0
    assert p['proof']['tcp']['natCorrect']and p['proof']['udp']['natCorrect']
obs98=json.loads((root/'evidence/nss98-return-localization.json').read_text());assert len(obs98)==2
assert [x['summary']['routerSamples']for x in obs98]==[104,64]
for x in obs98:assert not x['summary']['routerWrites']and not x['summary']['nssOpened']and x['serverClientSequenceMatched']and x['captureAndCompleteCtInputsKeptPrivate']
d94=obs98[1]['summary'];assert len(d94['lowReplyIntervals'])==8
for x in d94['lowReplyIntervals']:assert x['routerCtDownDelta']==0 and x['counters']['cakeDrops']==x['counters']['redirectDrops']==x['counters']['softnetDropped']==0
g32,g52=d94['aggregates'];assert g32['serverEgress']==g32['serverEgressMatchedClient']==1144
assert g52['serverEgress']==1092 and g52['serverEgressMatchedClient']==701 and g52['routerCtDownDelta']==701
closures98=json.loads((root/'evidence/nss98-endpoint-closure.json').read_text());assert len(closures98)==5
for c in closures98:
    assert c['temporaryFirewallRulesRemaining']==0 and c['canonicalFirewallBaselineRestored']and c['ownedUnitInactiveMainPidZeroPortsClosed']
    assert c['clientExited']and c['clientGuardPassed']and c['endpointGuardianVerifiedBeforeWrite']and c['noExistingVpsServiceReplaced']
    assert c['independentFirewallExpirySeconds']==180 and c['independentClientDeadlineSeconds']==210
x98=json.loads((root/'evidence/nss98-mainline.json').read_text());rt98=json.loads((root/'evidence/current-runtime.json').read_text())
assert x98['round']==rt98['round']=='NSS98'and x98['stageCases']==3 and x98['successfulCompleteABA']==x98['ecmOpenedCases']==2
assert x98['matched48']['acceptedCpuComparison']=='B vs A2 only'and not x98['matched48']['allThreeThroughputWithinOnePercent']
assert 70<x98['matched48']['relativeSoftirqReductionAgainstA2Percent']<75
assert not x98['congested40']['cpuComparisonAccepted']and not x98['congested40']['longTermExactRateAccuracyAccepted']and not x98['congested40']['ecnAccepted']
assert x98['returnDeficit52']['unreportedRouterIngressOrUpstreamStillNotSeparated']and x98['returnDeficit52']['ecmOpeningRefused']
assert x98['qosScope']['onlyLanEgressDownlinkLeavesInstalled']and not x98['qosScope']['acceleratedUplinkQosGuaranteed']and not x98['qosScope']['fullCakeReplacementAccepted']
assert x98['early95ClosureCheckRefusedBeforeExpiry']and x98['later95IndependentExpiryClosurePassed']
assert not any(x98[k]for k in ['permanentClassifierChanged','productionFirmwareKernelChanged','humanCs2Acceptance','highLoad300MbpsAcceptance','secondWanEnabled','upstreamSubmitted'])
assert rt98['workerPid']==4859 and rt98['guardianPid']==17139 and not rt98['nssPermanentlyEnabled']and not rt98['realHumanGameAcceptance']
assert rt98['qualifiedExperimentalEntryBoundInputs']==556 and rt98['congestionEntryBoundInputs']==580
assert rt98['historical92RuntimePreservedSha256']==hashlib.sha256((root/'evidence/nss92-runtime.json').read_bytes()).hexdigest()
assert rt98['historical82RuntimePreservedSha256']==hashlib.sha256((root/'evidence/nss82-runtime.json').read_bytes()).hexdigest()
assert all(rt98['audit'][k]for k in ['passed','configurationMatches','originalFullLockedAudit','ecmStoppedAndZero','noActiveTransaction','noStaging','noExperimentState','noExperimentalModule'])
assert x98['reportVerification']['sourceValidated']and not x98['reportVerification']['browserRendered']

print(json.dumps({'passed':True,'filesChecked':count,'sourceHashesChecked':len(manifest['sources']),'markdownLinksChecked':links,'obviousSecretChecksPassed':True,'scope':'Curated allowlist plus pattern checks; not a claim of comprehensive secret detection.'}))
