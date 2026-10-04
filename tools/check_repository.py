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
x46=json.loads((root/'evidence/nss46-mainline.json').read_text());latest=json.loads((root/'evidence/current-runtime.json').read_text())
assert latest['round']=='NSS46' and latest['deploymentReference']==x46['deploymentReference']=='work/nss46/deployment-latest.json'
assert x46['classifierCommitted'] and x46['permanentClassifierChanged'] and not x46['nssOpened']
assert latest['classifierConfigSha256']==x46['classifierConfigSha256'] and latest['classifierReliabilityChangesRetained']==3
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
print(json.dumps({'passed':True,'filesChecked':count,'sourceHashesChecked':len(manifest['sources']),'markdownLinksChecked':links,'obviousSecretChecksPassed':True,'scope':'Curated allowlist plus pattern checks; not a claim of comprehensive secret detection.'}))
