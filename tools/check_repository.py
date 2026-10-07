"""Verify curated source identity, artifact links, and obvious secret exclusions."""
import hashlib, json, re, copy
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
assert len(manifest['sources'])>=1079+proof98['sources']
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
x98=json.loads((root/'evidence/nss98-mainline.json').read_text());rt98=json.loads((root/'evidence/nss98-runtime.json').read_text())
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

proof107=json.loads((root/'evidence/nss107-source-proof.json').read_text())
assert proof107['historicPrefixSources']==1110 and proof107['sources']==45
assert len(manifest['sources'])>=1110+proof107['sources']
assert hashlib.sha256(json.dumps(manifest['sources'][:1110],sort_keys=True,separators=(',',':')).encode()).hexdigest()==proof107['historicPrefixCanonicalSha256']
for source,digest in proof107['sourceHashes'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==digest
assert proof107['privateOwnedHostBootstrapExcluded']and proof107['completePrivateSourceInputsRetained']and proof107['lostFirstBackgroundRawIsExplicitException']
trials107=json.loads((root/'evidence/nss107-trials.json').read_text())
assert [t['sourceInputs']for t in trials107]==[608,636,636,662]
assert [t['completeABA']for t in trials107]==[True,True,False,True]
assert [t['ecmOpened']for t in trials107]==[True,True,False,True]
assert [t['renewals']for t in trials107]==[7,6,0,7]
for t in trials107:
    assert t['sourceInputsCurrentAndFrozenMatch']and t['checkpointDownloadedShaAndGzipVerified']and t['guardianVerifiedBeforeFirstWrite']
    assert t['guardianPpid']==1 and t['independentOwnerSeconds']==100 and t['fixedNativeSessionSeconds']==27 and t['classifierMaximumLeaseSeconds']==6
    assert all(t['rollback'].values())and t['baseline']['configurationMatches']and all(t['baseline']['checks'].values())and t['beforeFullAudit']['passed']and t['afterFullAudit']['passed']
    assert not t['gameQualityConclusion']
    if t['completeABA']:
        assert [p['acceleratedCounts']for p in t['metrics']['phases']]==[[0],[2],[0]]
        assert all(p['sampleCount']==41 and 20<=p['whole']['seconds']<=21.5 for p in t['metrics']['phases'])
        assert t['actualAcceleratedIdentity']['passed']and t['actualAcceleratedIdentity']['connectionCount']==2
        assert all(t['actualAcceleratedIdentity']['proof'][k]['upTag']==0 and t['actualAcceleratedIdentity']['proof'][k]['natCorrect']for k in ['tcp','udp'])
assert trials107[2]['softwareTagCounters']['initialTags']['tcp_post_down_unexpected']=={'packets':1,'bytes':1500}
assert 'Unexpected tag observed'in trials107[2]['error']and not trials107[2]['phases']
for t in [trials107[0],trials107[1]]:
    assert t['metrics']['leafAcrossBNearbySnapshots']['8f06:']['delta']['dropped']==0
assert trials107[0]['metrics']['leafAcrossBNearbySnapshots']['8f05:']['delta']['dropped']==363
new107=trials107[3];assert new107['zeroNewWrongTagsConfirmed']and new107['startupEpoch']['rawCountersNeverReset']
assert not new107['startupEpoch']['nssAdmissionAllowed']and not new107['startupEpoch']['onePacketStartupExceptionActuallyTriggered']
for c in new107['measurementEpochCounters'].values():assert all(c[k]['packets']==c[k]['bytes']==0 for k in c if k.endswith('_unexpected')or k=='udp_post_neighbor_nonzero')
assert new107['metrics']['leafAcrossBNearbySnapshots']['8f05:']['delta']['dropped']==293
assert new107['metrics']['leafAcrossBNearbySnapshots']['8f06:']['delta']['dropped']==0
assert [p['whole']['udp']['received']for p in new107['metrics']['phases']]==[761,867,794]
assert [p['whole']['udp']['sent']for p in new107['metrics']['phases']]==[793,904,820]
assert all(p['whole']['timeSqueezeDelta']==p['whole']['softnetDropDelta']==0 for p in new107['metrics']['phases'])
assert new107['leafAdditionalStats']['8f06:']['afterBacklogPackets']==0
epoch107=json.loads((root/'evidence/nss107-startup-epoch-qualification.json').read_text())
assert epoch107['passed']and len(epoch107['checks'])==18 and epoch107['strictCounterAuditByteIdentical']
assert epoch107['maximumInitialWaitSeconds']==1.2 and epoch107['warmupSeconds']==.1
assert epoch107['sourceSha256']==hashlib.sha256((root/'code/work/nss105/fast-path.lua').read_bytes()).hexdigest()
bg107=json.loads((root/'evidence/nss107-background-before.json').read_text());after107=json.loads((root/'evidence/nss107-background-after.json').read_text())
assert bg107['toolReturnedSummaryValuesRetained']and not bg107['originalRawObservationAvailable']and bg107['interfaces']['lan4']['txMbps']>150
assert after107['interfaces']['lan4']['txMbps']<.1
closures107=json.loads((root/'evidence/nss107-endpoint-closure.json').read_text());assert len(closures107)==6
for c in closures107:
    assert c['temporaryFirewallRulesRemaining']==0 and c['canonicalFirewallBaselineRestored']and c['ownedUnitInactiveMainPidZeroPortsClosed']
    assert c['clientExited']and c['clientGuardPassed']and c['endpointGuardianVerifiedBeforeWrite']
    assert c['independentFirewallExpirySeconds']==180 and c['independentClientDeadlineSeconds']==210
x107=json.loads((root/'evidence/nss107-mainline.json').read_text());rt107=json.loads((root/'evidence/nss107-runtime.json').read_text())
assert x107['round']==rt107['round']=='NSS107'and x107['stageCases']==4 and x107['successfulFunctionalABA']==3 and x107['startupEpochActualPassed']
assert x107['newEntryInputs']==rt107['qualifiedExperimentalEntryBoundInputs']==662
assert not any(x107[k]for k in ['newCpuComparisonAccepted','rateAccuracyAccepted','endToEndUdpQosAccepted','humanCs2Acceptance','highLoad300MbpsAcceptance','permanentClassifierChanged','nssPermanentlyEnabled','secondWanSimultaneousAcceleration','acceleratedUplinkQosGuaranteed','fullCakeReplacementAccepted','upstreamSubmitted'])
assert rt107['workerPid']==4859 and rt107['guardianPid']==17139 and not rt107['realHumanGameAcceptance']
assert all(rt107['audit'][k]for k in ['passed','configurationMatches','originalFullLockedAudit','ecmStoppedAndZero','noActiveTransaction','noStaging','noExperimentState','noExperimentalModule'])
assert rt107['historical98RuntimePreservedSha256']==hashlib.sha256((root/'evidence/nss98-runtime.json').read_bytes()).hexdigest()
assert rt107['historical92RuntimePreservedSha256']==hashlib.sha256((root/'evidence/nss92-runtime.json').read_bytes()).hexdigest()
assert rt107['historical82RuntimePreservedSha256']==hashlib.sha256((root/'evidence/nss82-runtime.json').read_bytes()).hexdigest()
assert x107['reportVerification']['sourceValidated']and not x107['reportVerification']['browserRendered']

proof109=json.loads((root/'evidence/nss109-source-proof.json').read_text())
assert proof109['historicPrefixSources']==1155 and proof109['sources']==30
assert len(manifest['sources'])>=1155+proof109['sources']+2
assert hashlib.sha256(json.dumps(manifest['sources'][:1155],sort_keys=True,separators=(',',':')).encode()).hexdigest()==proof109['historicPrefixCanonicalSha256']
for source,digest in proof109['sourceHashes'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==digest
assert proof109['privateOwnedHostBootstrapExcluded']and proof109['successfulRepairAndCaptureCurrentSourcesAndPrivateInputsRetained']
assert proof109['prewriteUncompressedInstallerVariantNotClaimedFrozen']and proof109['firstInterruptedServerCaptureNotClaimedComplete']
x109=json.loads((root/'evidence/nss109-mainline.json').read_text());rt109=json.loads((root/'evidence/nss109-runtime.json').read_text())
assert x109['round']==rt109['round']=='NSS109'
assert x109['eligibleRequests']==484 and x109['missingBeforeEarliestRouterLinuxTap']==19 and x109['missingInObservedRouterDownstreamChain']==0
assert not any(x109[k]for k in ['routerPhysicalNicVsUpstreamSeparated','wan4AuthenticationRecovered','nssOpenedThisTurn','newMatchedABA','newCpuComparisonAccepted','sameWanCongestionComparison','humanCs2Acceptance','highLoad300MbpsAcceptance','fullCakeReplacementAccepted','acceleratedUplinkQosGuaranteed','residentClassifierChanged','nssPermanentlyEnabled','upstreamSubmitted'])
assert x109['tcpBulkWan']==3 and x109['udpRtWan']==2 and x109['temporaryEndpointsClosed']==2
localization109=json.loads((root/'evidence/nss109-path-localization-v2.json').read_text())
assert [t['qualifiedSequences']for t in localization109['trials']]==[236,248]
assert [t['unreturned']for t in localization109['trials']]==[9,10]
for t in localization109['trials']:
    assert t['passed']and t['socketDrops']==0 and t['allRouterDownAndPcSetsIdentical']and t['routerDownstreamMissingAfterEarliestTap']==0
    counts=t['counts'];assert counts['serverIngress']==counts['serverEgress']==counts['physicalWanUp']==t['qualifiedSequences']
    assert counts['physicalWanDown']==counts['privateWanDown']==counts['ifbDown']==counts['bridgeDown']==counts['lanDown']==counts['pcReceived']
    assert t['boundaryTrimmed']and t['pcFinalLogUsed']and t['routerAndServerClocksNotAssumedAligned']and t['notMatchedNssABA']and t['notCs2Metric']
assert not localization109['identity']['sameWanPair']and not localization109['identity']['nssPermissionGranted']
assert not localization109['identity']['experimentChangedPbrOrNat']and localization109['identity']['naturalWan4FailoverObservedAndIndependentlyProved']
assert not localization109['identity']['pbrTransitionTimingWithinCaptureWindowsMeasured']and localization109['identity']['noClaimThatAllRuntimePbrWasUnchanged']
clarification109=json.loads((root/'evidence/nss109-routing-clarification.json').read_text())
assert clarification109['oldV1EvidenceRetained']and clarification109['countsAndRawSequenceEvidenceUnchanged']and clarification109['metadataCorrectionOnly']
assert clarification109['oldV1Sha256']==hashlib.sha256((root/'evidence/nss109-path-localization.json').read_bytes()).hexdigest()
assert clarification109['newV2Sha256']==hashlib.sha256((root/'evidence/nss109-path-localization-v2.json').read_bytes()).hexdigest()
assert clarification109['newSourceSha256']==hashlib.sha256((root/'code'/clarification109['newSource']).read_bytes()).hexdigest()
assert clarification109['prior1185SourcePrefixSha256']==hashlib.sha256(json.dumps(manifest['sources'][:1185],sort_keys=True,separators=(',',':')).encode()).hexdigest()
assert clarification109['textChecksumsUsePublishedLfBytes']and clarification109['originalCommittedV1BytesRetained']
assert clarification109['publicTextNormalizationSourceSha256']==hashlib.sha256((root/'code'/clarification109['publicTextNormalizationSource']).read_bytes()).hexdigest()
auth109=json.loads((root/'evidence/nss109-auth-repair.json').read_text())
assert auth109['committed']and auth109['independent180SecondRollbackVerifiedBeforeWrite']and auth109['originalNativeAuditPassed']
assert not auth109['authenticatorRestarted']and not auth109['interfacesRestarted']and not auth109['naturalRollbackTested']
assert auth109['qualification']['passed']and auth109['qualification']['originalMissingPidExitCode']==1 and len(auth109['qualification']['checks'])==6
assert auth109['latestNaturalRecoveryRequest']['result']==0 and not auth109['latestNaturalRecoveryRequest']['authenticationSucceeded']
assert auth109['newAuthSha256']==hashlib.sha256((root/'code/work/nss108/auth-candidate.sh').read_bytes()).hexdigest()
assert auth109['oldAuthSha256']==hashlib.sha256((root/'code/work/nss108/auth-before.sh').read_bytes()).hexdigest()
instrument109=json.loads((root/'evidence/nss109-instrumentation.json').read_text())
assert instrument109['firstCaptureSocketDrops']==160 and instrument109['firstCaptureExitCode']==2 and not instrument109['firstCaptureAccepted']
assert not instrument109['firstServerCompletedCaptureRetained']and instrument109['firstServerInterruptedOnRouterFailure']
assert instrument109['qualifiedNewCaptures']==2 and instrument109['qualifiedCaptureDrops']==[0,0]
assert instrument109['actualRouterAfPacketAndBpfVerified']and not instrument109['wslAfPacketKernelTestSupported']
failover109=json.loads((root/'evidence/nss109-wan4-failover.json').read_text())
assert failover109['passed']and failover109['exact300BucketSourceAlgorithmReproduced']and failover109['removedWan4Buckets']==60
assert failover109['newBucketCounts']==[75,75,75,0,75]and failover109['currentAppliedWeights']==[100,100,100,0,100]
assert failover109['onlyThreeWan4DhcpRulesRemoved']and failover109['unchangedProtectedHealthControllerSource']and not failover109['experimentRoutingMutation']
assert failover109['healthControllerSha256']==hashlib.sha256((root/'code/work/nss109/health-controller.lua').read_bytes()).hexdigest()
for c in json.loads((root/'evidence/nss109-endpoint-closure.json').read_text()):
    assert c['temporaryFirewallRulesRemaining']==0 and c['canonicalFirewallBaselineRestored']and c['ownedUnitInactiveMainPidZeroPortsClosed']and c['clientExited']and c['clientGuardPassed']
    assert c['endpointGuardianVerifiedBeforeWrite']and c['independentFirewallExpirySeconds']==180 and c['independentClientDeadlineSeconds']==210
assert rt109['workerPid']==4859 and rt109['guardianPid']==17139 and rt109['authRecoverySourceChangedAndCommitted']
assert not rt109['currentNssAdmissionQualified']and rt109['historicalEntryMustAdoptDeclaredAuthRepairAndActualFailoverBaselineBeforeWrite']
assert all(rt109['audit'][k]for k in ['passed','originalFullLockedNativeAudit','unrelatedConfigurationMatches','ecmStoppedAndZero','noActiveTransaction','noStaging','noExperimentState','noExperimentalModule'])
assert not rt109['audit']['allFiveWanHealthy']and not rt109['audit']['fullOriginalNssAdmissionEpochPassed']and not rt109['audit']['nssAdmissionAllowed']
for n in [107,98,92,82]:assert rt109[f'historical{n}RuntimePreservedSha256']==hashlib.sha256((root/f'evidence/nss{n}-runtime.json').read_bytes()).hexdigest()
assert x109['reportVerification']['sourceValidated']and not x109['reportVerification']['browserRendered']
last109=json.loads((root/rt109['lastReadonlyAuditReference']).read_text())
assert last109['observedAt']==rt109['checkedAt']and last109['readonlyRepeatAfterEvidenceExport']
assert all(last109[k]for k in ['passed','originalFullLockedNativeAudit','unrelatedConfigurationMatches','ecmStoppedAndZero','noActiveTransaction','noStaging','noExperimentState','noExperimentalModule'])
assert last109['workerPid']==4859 and last109['guardianPid']==17139 and not last109['wan4Up']and not last109['nssAdmissionAllowed']
assert rt109['priorDeclaredBaselineAuditRetained']

proof115=json.loads((root/'evidence/nss115-source-proof.json').read_text())
assert proof115['historicPrefixSources']==1187 and proof115['sources']==109
assert len(manifest['sources'])>=1187+proof115['sources']
assert hashlib.sha256(json.dumps(manifest['sources'][:1187],sort_keys=True,separators=(',',':')).encode()).hexdigest()==proof115['historicPrefixCanonicalSha256']
for source,digest in proof115['sourceHashes'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==digest
assert proof115['privateOwnedHostBootstrapExcluded']and proof115['actualCaseSourceInputsAndHistoricFrozenTreesRetained']
x115=json.loads((root/'evidence/nss115-mainline.json').read_text());rt115=json.loads((root/'evidence/nss115-runtime.json').read_text())
assert x115['round']==rt115['round']=='NSS115' and x115['newQualifiedEntryBoundInputs']==793
assert x115['actualSingleWanStageCases']==4 and x115['preStageTransportRefusals']==1 and x115['completeFunctionalABA']==3 and x115['overallSuccessfulABA']==2
assert x115['newDualPhysicalQosPassed']and x115['dualPhysicalQosHardwareRound']==114 and x115['dualPhysicalQosOneWan']==2 and x115['actualAcceleratedCount']==[0,2,0]
assert all(x115[k]for k in ['onlyOneTcpUdpPairAtATime','physicalLan4DownlinkQosProven','physicalWanUplinkLeafRoutingProven','residentPublicationUpTagStillZero','controlledUpTagDerivedFromActualBulkRtClass','originalFailuresPreserved'])
assert not any(x115[k]for k in ['uplinkCongestionLatencyAccepted','authEapolContinuityWhileQueueActiveAccepted','newMatchedCpuComparisonAccepted','humanCs2Acceptance','highLoad300MbpsAcceptance','fullCakeReplacementAccepted','residentClassifierChanged','nssPermanentlyEnabled','unknownRoutingChangesAllowed','wan4AuthenticationRecovered','uiOperated','newSteamDownloadsStarted','upstreamSubmitted'])
tr115=json.loads((root/'evidence/nss115-trials.json').read_text());assert len(tr115)==5
assert not tr115[0]['passed']and tr115[0]['completeABA']and tr115[0]['stageUndoVerified']and tr115[0]['originalStrictRecoveryRejected']
assert tr115[1]['passed']and tr115[1]['completeABA']
assert not tr115[2]['detachedStageStarted']and not tr115[2]['queueWrites']and not tr115[2]['ecmOpened']
assert not tr115[3]['passed']and not tr115[3]['ecmOpened']and tr115[3]['bothPhysicalQueuesConstructedAndRestoredBeforeEcm']
assert 'Unapproved setter'in tr115[3]['error']and tr115[3]['baseline']['failedUnselectedWan4ProcessEpoch']['processChanged']
assert tr115[4]['passed']and tr115[4]['completeABA']and [p['acceleratedCounts']for p in tr115[4]['metrics']['phases']]==[[0],[2],[0]]
for i in [1,3,4]:
    t=tr115[i];assert t['sourceInputsCurrentAndFrozenMatch']and t['guardianVerifiedBeforeFirstWrite']and t['checkpointDownloadedShaAndGzipVerified']and all(t['rollback'].values())
    assert t['independentOwnerSeconds']==100 and t['fixedNativeSessionSeconds']==27 and t['classifierMaximumLeaseSeconds']==6
    assert t['baseline']['configurationMatches']and t['beforeFullAudit']['passed']and t['afterFullAudit']['passed']
up115=json.loads((root/'evidence/nss115-uplink-proof.json').read_text());assert up115['passed']and up115['actualEcmTagsVerified']and up115['bothUplinkLeavesAdvancedNearAcceleratedPhase']
assert up115['uplinkDevice']=='wan'and up115['physicalIfindex']==6 and up115['physicalAeId']==5
assert up115['uplinkBulkTag']==0x8e050000 and up115['uplinkRtTag']==0x8e060000
for name in ['8e05:','8e06:']:assert up115['uplinkLeafDelta'][name]['packets']>0 and up115['uplinkLeafDelta'][name]['dropped']==0
assert up115['bothPhysicalRootsRestored']and up115['ownedModuleRemoved']and up115['pbrCtMarkNatWanAffinityVerified']and up115['queueStatisticsAsynchronous']
assert not up115['upstreamCongestionLatencyAccepted']and not up115['humanGameAcceptance']
for slot,up,down in [('tcp',0x8e050000,0x8f050000),('udp',0x8e060000,0x8f060000)]:
    v=tr115[4]['actualAcceleratedIdentity']['proof'][slot];assert v['upTag']==up and v['downTag']==down and v['ctMark']==0x20000 and v['natCorrect']and v['wanAffinity']==2
prep115=json.loads((root/'evidence/nss115-preparation.json').read_text())
assert len(prep115['qos20TargetRamCases']['checks'])==20 and len(prep115['qosEntry30Checks'])==30 and len(prep115['planAndOwner21Checks'])==21 and len(prep115['normalizer27TargetRamChecks']['checks'])==27
assert prep115['limitsUnchanged']=={'execBytes':9000,'transportRawBytes':65536,'stagedCodeBytes':73728,'classifierLeaseSeconds':6,'nativeSessionSeconds':27,'independentOwnerSeconds':100}
assert not prep115['payloadCapFirstRefusal']['passed']and prep115['payloadCapFirstRefusal']['payloadBytes']==75489
assert prep115['normalizer27TargetRamChecks']['uplinkTagsSimulated']and not prep115['normalizer27TargetRamChecks']['configurationWrites']
assert prep115['normalizer27TargetRamChecks']['sourceSha256']==hashlib.sha256((root/'code/work/nss114/tag-normalizer.lua').read_bytes()).hexdigest()
closures115=json.loads((root/'evidence/nss115-endpoint-closure.json').read_text());assert len(closures115)==5
for c in closures115:
    assert c['temporaryFirewallRulesRemaining']==0 and c['canonicalFirewallBaselineRestored']and c['ownedUnitInactiveMainPidZeroPortsClosed']and c['clientExited']and c['clientGuardPassed']and c['endpointGuardianVerifiedBeforeWrite']
    assert c['independentFirewallExpirySeconds']==180 and c['independentClientDeadlineSeconds']==210
assert closures115[0]['firstTwoSshClosureTimeoutsRetained']and closures115[0]['separateReadOnlyClosureAfterOsDeadlinePassed']
assert rt115['workerPid']==4859 and rt115['guardianPid']==17139 and rt115['currentNssAdmissionMustBeRefreshedBeforeWrite']
assert rt115['historical109RuntimePreservedSha256']==hashlib.sha256((root/'evidence/nss109-runtime.json').read_bytes()).hexdigest()
assert all(rt115['audit'][k]for k in ['passed','originalFullLockedNativeAudit','unrelatedConfigurationMatches','ecmStoppedAndZero','noActiveTransaction','noStaging','noExperimentState','noExperimentalModule'])
assert all(rt115['physicalRootRestoreAudit'][k]for k in ['passed','physicalWanOriginalMqFourFqCodelRestored','lan4OriginalMqFourFqCodelRestored','defaultQueueOptionsAndHandlesExact'])
assert x115['reportVerification']['sourceValidated']and not x115['reportVerification']['browserRendered']

proof117=json.loads((root/'evidence/nss117-source-proof.json').read_text())
assert proof117['historicPrefixSources']==1296 and proof117['sources']==35
assert len(manifest['sources'])>=1296+35
assert hashlib.sha256(json.dumps(manifest['sources'][:1296],sort_keys=True,separators=(',',':')).encode()).hexdigest()==proof117['historicPrefixCanonicalSha256']
for source,digest in proof117['sourceHashes'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==digest
assert proof117['privateOwnedHostBootstrapExcluded']and proof117['actualBindingTreesRetained']
x117=json.loads((root/'evidence/nss117-mainline.json').read_text());rt117=json.loads((root/'evidence/nss117-runtime.json').read_text())
assert x117['round']==rt117['round']=='NSS117'and x117['boundInputs']==rt117['qualifiedExperimentalEntryBoundInputs']==825
assert x117['directionOnlyNewVariable']==rt117['bulkDirection']=='upload'and x117['offeredUploadMbps']==48
assert all(x117[k]for k in ['queueRatesUnchangedFrom114','routerPayloadByteExactFrom114','serverConfirmedReceivedBytesUsed','firstPublicationCoherenceFailurePreserved','unchangedEntryRetriedOnce','successfulSingleWanABA','shaperActivityObserved'])
assert not any(x117[k]for k in ['newCpuComparisonAccepted','uplinkCongestionLatencyAccepted','humanCs2Acceptance','highLoad300MbpsAcceptance','fullCakeReplacementAccepted','residentClassifierChanged','nssPermanentlyEnabled','secondWanSimultaneouslyAccelerated','upstreamSubmitted','tcpRampCauseProved'])
assert (x117['nativeSessionSeconds'],x117['independentOwnerSeconds'],x117['phaseSeconds'],x117['classifierMaximumLeaseSeconds'])==(27,100,20,6)
tr117=json.loads((root/'evidence/nss117-trials.json').read_text());assert len(tr117)==2
assert not tr117[0]['passed']and not tr117[0]['ecmOpened']and 'publication changed during read'in tr117[0]['error']
assert tr117[1]['passed']and tr117[1]['completeABA']and [p['acceleratedCounts']for p in tr117[1]['metrics']['phases']]==[[0],[2],[0]]
for t in tr117:
    assert t['sourceInputsCurrentAndFrozenMatch']and t['guardianVerifiedBeforeFirstWrite']and t['checkpointDownloadedShaAndGzipVerified']and all(t['rollback'].values())
    assert t['independentOwnerSeconds']==100 and t['fixedNativeSessionSeconds']==27 and t['classifierMaximumLeaseSeconds']==6
    assert t['baseline']['configurationMatches']and t['beforeFullAudit']['passed']and t['afterFullAudit']['passed']
m117=json.loads((root/'evidence/nss117-metrics.json').read_text());assert m117['bulkDirection']=='upload'and m117['localSubmittedBytesNotUsedForThroughput']and m117['qosBytesUnchangedFrom114']
assert len(m117['phases'])==3 and m117['renewals']==6 and m117['oneWan']==1
assert all(p['whole']['timeSqueezeDelta']==p['whole']['softnetDropDelta']==p['whole']['udp']['unreturned']==0 for p in m117['phases'])
assert [p['whole']['udp']['sent']for p in m117['phases']]==[864,820,850]
up117=json.loads((root/'evidence/nss117-uplink-proof.json').read_text());assert up117['passed']and up117['actualEcmTagsVerified']and up117['bothUplinkLeavesAdvancedNearAcceleratedPhase']
assert up117['uplinkLeafDelta']['8e05:']['dropped']==21 and up117['uplinkLeafDelta']['8e06:']['dropped']==0
assert up117['uplinkDevice']=='wan'and up117['uplinkBulkTag']==0x8e050000 and up117['uplinkRtTag']==0x8e060000
for slot,up,down in [('tcp',0x8e050000,0x8f050000),('udp',0x8e060000,0x8f060000)]:
    v=tr117[1]['actualAcceleratedIdentity']['proof'][slot];assert v['upTag']==up and v['downTag']==down and v['ctMark']==0x10000 and v['natCorrect']and v['wanAffinity']==1
trans117=json.loads((root/'evidence/nss117-uplink-transient.json').read_text());assert trans117['passed']and trans117['shaperActivityObserved']and trans117['rtAllRepliesReceivedInEachPhase']
assert trans117['uplinkParentAndLeafClassDelta']['8e00:50']['overlimits']==12640 and trans117['actualBulkLeafDrops']==21 and trans117['actualRtLeafDrops']==0
assert trans117['bulkRampObservedAcrossBins']and trans117['phaseBNotSteadyThirtyMbps']and not trans117['rateAccuracyAccepted']and not trans117['tcpRampCauseProved']
assert len(json.loads((root/'evidence/nss117-qualification.json').read_text()))==12
closures117=json.loads((root/'evidence/nss117-endpoint-closure.json').read_text());assert len(closures117)==2
for c in closures117:
    assert c['temporaryFirewallRulesRemaining']==0 and c['canonicalFirewallBaselineRestored']and c['ownedUnitInactiveMainPidZeroPortsClosed']and c['clientExited']and c['clientGuardPassed']and c['endpointGuardianVerifiedBeforeWrite']
    assert c['independentFirewallExpirySeconds']==180 and c['independentClientDeadlineSeconds']==210
assert rt117['workerPid']==4859 and rt117['guardianPid']==17139 and rt117['currentNssAdmissionMustBeRefreshedBeforeWrite']
assert rt117['historical115RuntimePreservedSha256']==hashlib.sha256((root/'evidence/nss115-runtime.json').read_bytes()).hexdigest()
assert all(rt117['audit'][k]for k in ['passed','originalFullLockedNativeAudit','unrelatedConfigurationMatches','ecmStoppedAndZero','noActiveTransaction','noStaging','noExperimentState','noExperimentalModule'])
assert all(rt117['physicalRootRestoreAudit'][k]for k in ['passed','physicalWanOriginalMqFourFqCodelRestored','lan4OriginalMqFourFqCodelRestored','defaultQueueOptionsAndHandlesExact'])
assert not rt117['nssPermanentlyEnabled']and not rt117['realHumanGameAcceptance']and not rt117['newMatchedCpuComparisonAccepted']
assert x117['reportVerification']['sourceValidated']and not x117['reportVerification']['browserRendered']

proof118=json.loads((root/'evidence/nss118-source-proof.json').read_text())
assert proof118['historicPrefixSources']==1331 and proof118['sources']==33 and len(manifest['sources'])>=1364
assert hashlib.sha256(json.dumps(manifest['sources'][:1331],sort_keys=True,separators=(',',':')).encode()).hexdigest()==proof118['historicPrefixCanonicalSha256']
for source,digest in proof118['sourceHashes'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==digest
assert proof118['privateOwnedHostBootstrapExcluded']and proof118['actualBindingTreesRetained']
x118=json.loads((root/'evidence/nss118-mainline.json').read_text());rt118=json.loads((root/'evidence/nss118-runtime.json').read_text())
assert x118['round']==rt118['round']=='NSS118'and x118['boundInputs']==rt118['qualifiedExperimentalEntryBoundInputs']==857
assert x118['onlyOfferedUploadChanged']and x118['offeredAveragePerConnectionMbps']==32 and x118['instantaneousLoadCatchupStillPossible']
assert x118['hardwarePayloadByteExactFrom116']and x118['queueRatesUnchanged']and x118['completeFunctionalABA']and x118['shaperActivityObserved']
assert (x118['phaseSeconds'],x118['nativeSessionSeconds'],x118['independentOwnerSeconds'],x118['classifierMaximumLeaseSeconds'])==(20,27,100,6)
assert x118['rtRepliesComplete']and x118['rtLeafDrop']==0 and x118['bulkLeafDrop']==32 and x118['temporaryEndpointsClosed']==1
assert not any(x118[k]for k in ['smallerRateTransitionRestoredThroughput','newMatchedCpuComparisonAccepted','strictRateAccuracyAccepted','tcpThroughputRootCauseProved','humanCs2Acceptance','highLoad300MbpsAcceptance','fullCakeReplacementAccepted','residentClassifierChanged','nssPermanentlyEnabled','uiOperated','upstreamSubmitted'])
t118=json.loads((root/'evidence/nss118-trial.json').read_text());assert t118['passed']and t118['completeABA']
assert t118['sourceInputsCurrentAndFrozenMatch']and t118['guardianVerifiedBeforeFirstWrite']and t118['checkpointDownloadedShaAndGzipVerified']and all(t118['rollback'].values())
assert t118['baseline']['configurationMatches']and t118['beforeFullAudit']['passed']and t118['afterFullAudit']['passed']
m118=json.loads((root/'evidence/nss118-metrics.json').read_text());assert m118['offeredTcpMbps']==32 and m118['localSubmittedBytesNotUsedForThroughput']and m118['renewals']==7
assert [p['acceleratedCounts']for p in m118['phases']]==[[0],[2],[0]]and [p['whole']['udp']['sent']for p in m118['phases']]==[703,817,864]
assert all(p['whole']['udp']['unreturned']==p['whole']['timeSqueezeDelta']==p['whole']['softnetDropDelta']==0 for p in m118['phases'])
assert m118['phases'][1]['whole']['clientTcpMbps']<20 and m118['phases'][2]['whole']['clientTcpMbps']>32
trans118=json.loads((root/'evidence/nss118-uplink-transient.json').read_text());assert trans118['shaperActivityObserved']and trans118['uplinkParentAndLeafClassDelta']['8e00:50']['overlimits']==10573
assert len(json.loads((root/'evidence/nss118-qualification.json').read_text()))==9
c118=json.loads((root/'evidence/nss118-endpoint-closure.json').read_text())
assert c118['temporaryFirewallRulesRemaining']==0 and c118['canonicalFirewallBaselineRestored']and c118['ownedUnitInactiveMainPidZeroPortsClosed']and c118['clientExited']and c118['clientGuardPassed']and c118['endpointGuardianVerifiedBeforeWrite']
assert c118['independentFirewallExpirySeconds']==180 and c118['independentClientDeadlineSeconds']==210
assert rt118['historical117RuntimePreservedSha256']==hashlib.sha256((root/'evidence/nss117-runtime.json').read_bytes()).hexdigest()
assert rt118['workerPid']==4859 and rt118['guardianPid']==17139 and rt118['currentNssAdmissionMustBeRefreshedBeforeWrite']
assert all(rt118['audit'][k]for k in ['passed','originalFullLockedNativeAudit','unrelatedConfigurationMatches','ecmStoppedAndZero','noActiveTransaction','noStaging','noExperimentState','noExperimentalModule'])
assert all(rt118['physicalRootRestoreAudit'][k]for k in ['passed','physicalWanOriginalMqFourFqCodelRestored','lan4OriginalMqFourFqCodelRestored','defaultQueueOptionsAndHandlesExact'])

proof119=json.loads((root/'evidence/nss119-source-proof.json').read_text())
assert proof119['historicPrefixSources']==1364 and proof119['sources']==35 and len(manifest['sources'])>=1399
assert hashlib.sha256(json.dumps(manifest['sources'][:1364],sort_keys=True,separators=(',',':')).encode()).hexdigest()==proof119['historicPrefixCanonicalSha256']
for source,digest in proof119['sourceHashes'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==digest
x119=json.loads((root/'evidence/nss119-mainline.json').read_text());rt119=json.loads((root/'evidence/nss119-runtime.json').read_text())
assert x119['round']==rt119['round']=='NSS119'and x119['boundInputs']==rt119['qualifiedExperimentalEntryBoundInputs']==890
assert x119['onlyUploadPacingChanged']and x119['offeredUploadMbps']==32 and x119['maximumPacerCreditBytes']==65536
assert not x119['instantaneousLoadCatchupStillPossible']and not x119['sameWanAs118']and not x119['boundedPacerRestoredNssThroughput']
assert x119['hardwarePayloadByteExactFrom116']and x119['queueRatesUnchanged']and x119['completeFunctionalABA']and x119['shaperActivityObserved']
assert (x119['phaseSeconds'],x119['nativeSessionSeconds'],x119['independentOwnerSeconds'],x119['classifierMaximumLeaseSeconds'])==(20,27,100,6)
assert x119['rtRepliesComplete']and x119['rtLeafDrop']==0 and x119['bulkLeafDrop']==36 and x119['temporaryEndpointsClosed']==1
assert not any(x119[k]for k in ['newMatchedCpuComparisonAccepted','strictRateAccuracyAccepted','tcpThroughputRootCauseProved','humanCs2Acceptance','highLoad300MbpsAcceptance','fullCakeReplacementAccepted','residentClassifierChanged','nssPermanentlyEnabled','uiOperated','upstreamSubmitted'])
t119=json.loads((root/'evidence/nss119-trial.json').read_text());assert t119['passed']and t119['completeABA']
assert t119['sourceInputsCurrentAndFrozenMatch']and t119['guardianVerifiedBeforeFirstWrite']and t119['checkpointDownloadedShaAndGzipVerified']and all(t119['rollback'].values())
assert t119['baseline']['configurationMatches']and t119['beforeFullAudit']['passed']and t119['afterFullAudit']['passed']
m119=json.loads((root/'evidence/nss119-metrics.json').read_text());assert m119['offeredTcpMbps']==32 and m119['localSubmittedBytesNotUsedForThroughput']and m119['renewals']==6 and m119['oneWan']==5
assert [p['acceleratedCounts']for p in m119['phases']]==[[0],[2],[0]]and [p['whole']['udp']['sent']for p in m119['phases']]==[798,811,814]
assert all(p['whole']['udp']['unreturned']==p['whole']['timeSqueezeDelta']==p['whole']['softnetDropDelta']==0 for p in m119['phases'])
assert 30<m119['phases'][0]['whole']['clientTcpMbps']<32 and m119['phases'][1]['whole']['clientTcpMbps']<20 and 30<m119['phases'][2]['whole']['clientTcpMbps']<32
assert len(json.loads((root/'evidence/nss119-qualification.json').read_text()))==4
c119=json.loads((root/'evidence/nss119-endpoint-closure.json').read_text())
assert c119['temporaryFirewallRulesRemaining']==0 and c119['canonicalFirewallBaselineRestored']and c119['ownedUnitInactiveMainPidZeroPortsClosed']and c119['clientExited']and c119['clientGuardPassed']and c119['endpointGuardianVerifiedBeforeWrite']
assert c119['independentFirewallExpirySeconds']==180 and c119['independentClientDeadlineSeconds']==210
assert rt119['historical118RuntimePreservedSha256']==hashlib.sha256((root/'evidence/nss118-runtime.json').read_bytes()).hexdigest()
assert rt119['workerPid']==4859 and rt119['guardianPid']==17139 and rt119['currentNssAdmissionMustBeRefreshedBeforeWrite']
assert all(rt119['audit'][k]for k in ['passed','originalFullLockedNativeAudit','unrelatedConfigurationMatches','ecmStoppedAndZero','noActiveTransaction','noStaging','noExperimentState','noExperimentalModule'])
assert all(rt119['physicalRootRestoreAudit'][k]for k in ['passed','physicalWanOriginalMqFourFqCodelRestored','lan4OriginalMqFourFqCodelRestored','defaultQueueOptionsAndHandlesExact'])

label119=json.loads((root/'evidence/nss119-runtime-label-correction.json').read_text());v1raw=(root/'evidence/nss119-v1-runtime.json').read_bytes();v1=json.loads(v1raw)
assert label119['passed']and label119['originalExportV1PreservedSha256']==hashlib.sha256(v1raw).hexdigest()
assert v1.pop('historical117RuntimePreservedSha256')==rt119['historical118RuntimePreservedSha256']
v2=rt119.copy();v2.pop('historical118RuntimePreservedSha256');assert v1==v2
assert not label119['actualMeasurementsChanged']and label119['originalSourceExportUntouched']and label119['originalFailedCheckerRetained']
assert label119['historicPrefixSources']==1399 and len(manifest['sources'])>=1400
assert label119['historicPrefixCanonicalSha256']==hashlib.sha256(json.dumps(manifest['sources'][:1399],sort_keys=True,separators=(',',':')).encode()).hexdigest()
assert label119['newSourceSha256']==hashlib.sha256((root/'code'/label119['newSource']).read_bytes()).hexdigest()

proof124=json.loads((root/'evidence/nss124-source-proof.json').read_text())
assert proof124['historicPrefixSources']==1400 and proof124['sources']==98 and len(manifest['sources'])>=1498
assert proof124['historicPrefixCanonicalSha256']==hashlib.sha256(json.dumps(manifest['sources'][:1400],sort_keys=True,separators=(',',':')).encode()).hexdigest()
for source,digest in proof124['sourceHashes'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==digest
assert proof124['privateOwnedHostBootstrapExcluded']and proof124['actualBindingTreesRetained']
x124=json.loads((root/'evidence/nss124-mainline.json').read_text());rt124=json.loads((root/'evidence/nss124-runtime.json').read_text())
assert x124['round']==rt124['round']=='NSS124'and x124['boundInputs']==rt124['qualifiedExperimentalEntryBoundInputs']==1000
assert (x124['offeredUploadMbps'],x124['uplinkGroupMbps'],x124['uplinkBulkMbps'],x124['uplinkRtMbps'],x124['downlinkGroupMbps'])==(32,60,59,1,30)
assert (x124['phaseSeconds'],x124['nativeSessionSeconds'],x124['independentOwnerSeconds'],x124['classifierMaximumLeaseSeconds'])==(20,27,100,6)
assert all(x124[k]for k in ['routerQosOnlyUplinkBudgetChangedFrom119','sameWanAs119','completeFunctionalABA','comparableSelectedTransferRateObserved','nssThroughputRestoredWithLargerUplinkBudget','atomicHintFailureAndFiniteMatchingFailurePreserved','readOnlyAtomicRenameHandlingAdded'])
assert not any(x124[k]for k in ['allWanBackgroundObserved','exactRootCauseOfThirtyMbpsLossProved','newStrictCpuComparisonAccepted','rtRepliesComplete','strictRateAccuracyAccepted','humanCs2Acceptance','highLoad300MbpsAcceptance','fullCakeReplacementAccepted','residentClassifierChanged','nssPermanentlyEnabled','uiOperated','upstreamSubmitted'])
f124=json.loads((root/'evidence/nss124-prewrite-refusal.json').read_text());match124=json.loads((root/'evidence/nss124-matching-refusal.json').read_text())
assert f124['originalFailurePreserved']and not any(f124[k]for k in ['passed','ecmOpened','detachedStageStarted','queueWrites','checkpointStarted'])
assert match124['originalFailurePreserved']and match124['preparationOnly']and match124['resolvedByKeepingUdpSocketAndPeerFixedAndOnlyRotatingOwnedTcp']
assert not any(match124[k]for k in ['passed','ecmOpened','queueWrites','productionRouterWrites','actualNewUdpWanOrNatPeerProved','campusPolicyOrPbrChanged'])
t124=json.loads((root/'evidence/nss124-trial.json').read_text());m124=json.loads((root/'evidence/nss124-metrics.json').read_text())
assert t124['passed']and t124['completeABA']and t124['sourceInputs']==1000 and t124['sourceInputsCurrentAndFrozenMatch']and t124['guardianVerifiedBeforeFirstWrite']and t124['checkpointDownloadedShaAndGzipVerified']and all(t124['rollback'].values())
assert t124['baseline']['configurationMatches']and t124['beforeFullAudit']['passed']and t124['afterFullAudit']['passed']
assert m124['oneWan']==5 and m124['bulkDirection']=='upload'and m124['localSubmittedBytesNotUsedForThroughput']and m124['renewals']==6
assert [p['acceleratedCounts']for p in m124['phases']]==[[0],[2],[0]]and [p['whole']['udp']['unreturned']for p in m124['phases']]==[0,1,0]
assert all(30<p['whole']['clientTcpMbps']<32 and p['whole']['timeSqueezeDelta']==p['whole']['softnetDropDelta']==0 for p in m124['phases'])
assert m124['qosParentMbps']==30 and m124['uplinkParentMbps']==60 and not m124['qosBytesUnchangedFrom114']and not m124['allWanBackgroundObserved']
up124=json.loads((root/'evidence/nss124-uplink-proof.json').read_text());assert up124['passed']and up124['actualEcmTagsVerified']and up124['bothUplinkLeavesAdvancedNearAcceleratedPhase']
assert up124['uplinkLeafDelta']['8e05:']['dropped']==up124['uplinkLeafDelta']['8e06:']['dropped']==0
for slot,up,down in [('tcp',0x8e050000,0x8f050000),('udp',0x8e060000,0x8f060000)]:
    v=t124['actualAcceleratedIdentity']['proof'][slot];assert v['upTag']==up and v['downTag']==down and v['ctMark']==0x50000 and v['natCorrect']and v['wanAffinity']==5
q124=json.loads((root/'evidence/nss124-qualification.json').read_text());assert q124['atomicReadMaximumRetries']==1 and q124['waitSeconds']==5 and q124['runnerSeconds']==6 and q124['originalFullAuditUnchanged']and q124['qualifiedPayloadBytes']==73506
assert len(q124['atomicHintTargetRam'])==8 and all(c['passed']and c['targetRamOnly']for c in q124['atomicHintTargetRam'])
hint124=json.loads((root/'evidence/nss124-actual-readonly-hint.json').read_text());assert hint124['passed']and hint124['readonly']and hint124['fullAuditUnchanged']and not hint124['productionRouterWrites']and not hint124['nssAdmissionAllowed']
cs124=json.loads((root/'evidence/nss124-endpoint-closure.json').read_text());assert len(cs124)==3
for c in cs124:
    assert c['temporaryFirewallRulesRemaining']==0 and c['canonicalFirewallBaselineRestored']and c['ownedUnitInactiveMainPidZeroPortsClosed']and c['clientExited']and c['clientGuardPassed']and c['endpointGuardianVerifiedBeforeWrite']
    assert c['independentFirewallExpirySeconds']==180 and c['independentClientDeadlineSeconds']==210
assert cs124[-1]['initialClosureSshTimeoutPreserved']and cs124[-1]['subsequentReadOnlyClosurePassed']
assert rt124['historical119RuntimePreservedSha256']==hashlib.sha256((root/'evidence/nss119-runtime.json').read_bytes()).hexdigest()
assert rt124['workerPid']==4859 and rt124['guardianPid']==17139 and rt124['currentNssAdmissionMustBeRefreshedBeforeWrite']
assert all(rt124['audit'][k]for k in ['passed','originalFullLockedNativeAudit','unrelatedConfigurationMatches','ecmStoppedAndZero','noActiveTransaction','noStaging','noExperimentState','noExperimentalModule'])
assert all(rt124['physicalRootRestoreAudit'][k]for k in ['passed','physicalWanOriginalMqFourFqCodelRestored','lan4OriginalMqFourFqCodelRestored','defaultQueueOptionsAndHandlesExact'])

proof126=json.loads((root/'evidence/nss126-source-proof.json').read_text())
assert proof126['historicPrefixSources']==1498 and proof126['sources']==35 and len(manifest['sources'])>=1533
assert proof126['historicPrefixCanonicalSha256']==hashlib.sha256(json.dumps(manifest['sources'][:1498],sort_keys=True,separators=(',',':')).encode()).hexdigest()
for source,digest in proof126['sourceHashes'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==digest
x126=json.loads((root/'evidence/nss126-mainline.json').read_text());rt126=json.loads((root/'evidence/nss126-runtime.json').read_text());m126=json.loads((root/'evidence/nss126-metrics.json').read_text())
assert x126['round']==rt126['round']=='NSS126'and x126['hardwareEntryRound']==125 and x126['boundInputs']==rt126['qualifiedExperimentalEntryBoundInputs']==1033
assert (x126['offeredUploadMbps'],x126['uplinkGroupMbps'],x126['downlinkGroupMbps'],x126['phaseSeconds'],x126['nativeSessionSeconds'],x126['independentOwnerSeconds'],x126['classifierMaximumLeaseSeconds'])==(32,60,30,20,27,100,6)
assert all(x126[k]for k in ['onlyCommonReadOnlyInterfaceListChanged','allWanBackgroundObserved','completeFunctionalABA','firstSshHandshakeTimeoutPreserved','unchangedQualifiedEntryRetriedOnce','selectedTransferRateComparable','unselectedTrafficSmallInEachPhase','strictBackgroundRangeCriterionMarginallyFailed','repeatCpuSignalSupportsContinuingEngineering','noAdditionalCpuProbeToChaseThresholdPlanned'])
assert not any(x126[k]for k in ['strictPresetComparisonAccepted','humanCs2Acceptance','highLoad300MbpsAcceptance','fullCakeReplacementAccepted','preciseRateAccuracyAccepted','residentClassifierChanged','nssPermanentlyEnabled','uiOperated','upstreamSubmitted'])
assert .25<x126['backgroundRangeMbps']<.26 and x126['temporaryEndpointsClosed']==2
f126=json.loads((root/'evidence/nss126-preparation-failure.json').read_text());assert f126['originalFailurePreserved']and f126['clientUploadBytes']==0 and not any(f126[k]for k in ['passed','productionRouterWrites','ecmOpened','queueWrites','entryOrTimeoutChangedBeforeRetry'])
t126=json.loads((root/'evidence/nss126-trial.json').read_text());assert t126['passed']and t126['completeABA']and t126['sourceInputs']==1033 and t126['sourceInputsCurrentAndFrozenMatch']and t126['guardianVerifiedBeforeFirstWrite']and t126['checkpointDownloadedShaAndGzipVerified']and all(t126['rollback'].values())
assert t126['baseline']['configurationMatches']and t126['beforeFullAudit']['passed']and t126['afterFullAudit']['passed']
assert m126['allWanBackgroundObserved']and m126['counterObserverSameInAllPhases']and m126['qosBytesUnchangedFrom124']and m126['oneWan']==2 and m126['renewals']==6
assert [p['acceleratedCounts']for p in m126['phases']]==[[0],[2],[0]]and [p['whole']['udp']['unreturned']for p in m126['phases']]==[0,2,0]
assert all(29<p['whole']['clientTcpMbps']<32 and p['whole']['timeSqueezeDelta']==p['whole']['softnetDropDelta']==0 for p in m126['phases'])
assert all(set(p['whole']['interfaces'])=={'rpwan1','rpwan2','rpwan3','rpwan4','rpwan5','wan','lan4'}for p in m126['phases'])
comparison126=json.loads((root/'evidence/nss126-comparison.json').read_text());assert comparison126['passed']and not comparison126['comparabilityAccepted']and comparison126['softirqRelativeReductionPercent']is None
assert not comparison126['checks']['unselected_wan_total_range_below_0_25Mbps']and all(v for k,v in comparison126['checks'].items()if k!='unselected_wan_total_range_below_0_25Mbps')
assert all(0<=v<.5 for v in comparison126['unselectedWanTotalRxPlusTxMbps'])and 10<comparison126['softwareMeanSoftirqPercent']<11 and 4<comparison126['nssSoftirqPercent']<5
up126=json.loads((root/'evidence/nss126-uplink-proof.json').read_text());assert up126['passed']and up126['actualEcmTagsVerified']and up126['bothUplinkLeavesAdvancedNearAcceleratedPhase']
assert up126['uplinkLeafDelta']['8e05:']['dropped']==up126['uplinkLeafDelta']['8e06:']['dropped']==0
for slot,up,down in [('tcp',0x8e050000,0x8f050000),('udp',0x8e060000,0x8f060000)]:
    v=t126['actualAcceleratedIdentity']['proof'][slot];assert v['upTag']==up and v['downTag']==down and v['ctMark']==0x20000 and v['natCorrect']and v['wanAffinity']==2
assert len(json.loads((root/'evidence/nss126-qualification.json').read_text()))==4
cs126=json.loads((root/'evidence/nss126-endpoint-closure.json').read_text());assert len(cs126)==2
for c in cs126:
    assert c['temporaryFirewallRulesRemaining']==0 and c['canonicalFirewallBaselineRestored']and c['ownedUnitInactiveMainPidZeroPortsClosed']and c['clientExited']and c['clientGuardPassed']and c['endpointGuardianVerifiedBeforeWrite']
    assert c['independentFirewallExpirySeconds']==180 and c['independentClientDeadlineSeconds']==210
assert rt126['historical124RuntimePreservedSha256']==hashlib.sha256((root/'evidence/nss124-runtime.json').read_bytes()).hexdigest()
assert rt126['workerPid']==4859 and rt126['guardianPid']==17139 and rt126['currentNssAdmissionMustBeRefreshedBeforeWrite']
assert all(rt126['audit'][k]for k in ['passed','originalFullLockedNativeAudit','unrelatedConfigurationMatches','ecmStoppedAndZero','noActiveTransaction','noStaging','noExperimentState','noExperimentalModule'])
assert all(rt126['physicalRootRestoreAudit'][k]for k in ['passed','physicalWanOriginalMqFourFqCodelRestored','lan4OriginalMqFourFqCodelRestored','defaultQueueOptionsAndHandlesExact'])

proof128=json.loads((root/'evidence/nss128-source-proof.json').read_text())
assert proof128['historicPrefixSources']==1533 and proof128['sources']==37 and len(manifest['sources'])>=1570
assert proof128['historicPrefixCanonicalSha256']==hashlib.sha256(json.dumps(manifest['sources'][:1533],sort_keys=True,separators=(',',':')).encode()).hexdigest()
for source,digest in proof128['sourceHashes'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==digest
x128=json.loads((root/'evidence/nss128-mainline.json').read_text());rt128=json.loads((root/'evidence/nss128-runtime.json').read_text());m128=json.loads((root/'evidence/nss128-metrics.json').read_text())
assert x128['round']==rt128['round']=='NSS128'and x128['boundInputs']==rt128['qualifiedExperimentalEntryBoundInputs']==1069
assert (x128['offeredUploadMbps'],x128['uplinkGroupMbps'],x128['downlinkGroupMbps'],x128['phaseSeconds'],x128['nativeSessionSeconds'],x128['independentOwnerSeconds'],x128['classifierMaximumLeaseSeconds'])==(32,60,30,20,27,100,6)
assert all(x128[k]for k in ['onlyMappingSourceChanged','mappingByActualClass','allWanBackgroundObserved','completeFunctionalABA','sameHardwareBundleForSameActualClassAndTuples','mappedBeforeEcmLearning','productionPairRestrictedToTcpBulkUdpRt','genericTcpRtUdpBulkModelsOnly','scopedShortCpuComparisonAccepted','rtAllProbeRepliesReceived','residentUpTagZeroUnchanged'])
assert not any(x128[k]for k in ['physicalClassChangeRetirementAccepted','humanCs2Acceptance','highLoad300MbpsAcceptance','fullCakeReplacementAccepted','preciseRateAccuracyAccepted','residentClassifierChanged','nssPermanentlyEnabled','uiOperated','upstreamSubmitted'])
t128=json.loads((root/'evidence/nss128-trial.json').read_text());assert t128['passed']and t128['completeABA']and t128['sourceInputs']==1069 and t128['sourceInputsCurrentAndFrozenMatch']and t128['guardianVerifiedBeforeFirstWrite']and t128['checkpointDownloadedShaAndGzipVerified']and all(t128['rollback'].values())
assert t128['baseline']['configurationMatches']and t128['beforeFullAudit']['passed']and t128['afterFullAudit']['passed']
assert m128['allWanBackgroundObserved']and m128['counterObserverSameInAllPhases']and m128['qosBytesUnchangedFrom124']and m128['oneWan']==1 and m128['renewals']==6
assert m128['newCpuComparisonAccepted']is None and m128['cpuInterpretationRequiresSeparateSameLoadComparison']and m128['onlyActualClassToUplinkMappingChangedFrom125']
assert [p['acceleratedCounts']for p in m128['phases']]==[[0],[2],[0]]and all(29<p['whole']['clientTcpMbps']<32 and p['whole']['udp']['unreturned']==p['whole']['timeSqueezeDelta']==p['whole']['softnetDropDelta']==0 for p in m128['phases'])
comparison128=json.loads((root/'evidence/nss128-comparison.json').read_text());assert comparison128['passed']and comparison128['comparabilityAccepted']and all(comparison128['checks'].values())
assert 48<comparison128['softirqRelativeReductionPercent']<49 and comparison128['softirqRelativeReductionPercent']==x128['scopedSoftirqRelativeReductionPercent']==rt128['scopedSoftirqRelativeReductionPercent']
assert not comparison128['humanCs2Acceptance']and not comparison128['highLoad300MbpsAcceptance']and not comparison128['productionNssRetained']
mapped128=json.loads((root/'evidence/nss128-actual-class-mapping.json').read_text());assert all(mapped128[k]for k in ['passed','actualHardwareExecution','mappingUsesActualClassNotProtocol','initialAndPostCheckpointFullIdentityAndLeaseChecked','mappedPlanCreatedBeforeFrontendOpened','actualDetachedClassificationRepeatedBeforeTagPublication','exactClassifierPairClassAndActualEcmBidirectionalTagsMatch','residentUpTagZeroUnchanged','kernelPinDefaultDenyAndSixSecondRenewalRetained','productionPairRestrictedToTcpBulkUdpRt'])
assert not mapped128['tcpRtAndUdpBulkHardwareAccepted']and not mapped128['classChangePhysicalRetirementAccepted']and not mapped128['permanentNssEnabled']
for slot,up,down in [('tcp',0x8e050000,0x8f050000),('udp',0x8e060000,0x8f060000)]:
    v=t128['actualAcceleratedIdentity']['proof'][slot];assert v['upTag']==up and v['downTag']==down and v['ctMark']==0x10000 and v['natCorrect']and v['wanAffinity']==1
q128=json.loads((root/'evidence/nss128-qualification.json').read_text());assert len(q128['classMapping'])==14 and len(q128['entry'])==3 and q128['originalNativeBundleEquivalent']and q128['genericCrossProtocolModelsNotHardwareProof']and q128['payloadBytes']==73523
assert sum(bool(v['historicalReplayOnly'])for v in q128['classMapping'])==1 and sum(bool(v['syntheticMutationOnly'])for v in q128['classMapping'])==13
c128=json.loads((root/'evidence/nss128-endpoint-closure.json').read_text());assert c128['temporaryFirewallRulesRemaining']==0 and c128['canonicalFirewallBaselineRestored']and c128['ownedUnitInactiveMainPidZeroPortsClosed']and c128['clientExited']and c128['clientGuardPassed']and c128['endpointGuardianVerifiedBeforeWrite']
assert c128['independentFirewallExpirySeconds']==180 and c128['independentClientDeadlineSeconds']==210
assert rt128['historical126RuntimePreservedSha256']==hashlib.sha256((root/'evidence/nss126-runtime.json').read_bytes()).hexdigest()
assert rt128['workerPid']==4859 and rt128['guardianPid']==17139 and rt128['currentNssAdmissionMustBeRefreshedBeforeWrite']and rt128['actualClassDerivedMappingHardwarePassed']and rt128['scopedShortCpuComparisonAccepted']
assert all(rt128['audit'][k]for k in ['passed','originalFullLockedNativeAudit','unrelatedConfigurationMatches','ecmStoppedAndZero','noActiveTransaction','noStaging','noExperimentState','noExperimentalModule'])
assert all(rt128['physicalRootRestoreAudit'][k]for k in ['passed','physicalWanOriginalMqFourFqCodelRestored','lan4OriginalMqFourFqCodelRestored','defaultQueueOptionsAndHandlesExact'])

label128=json.loads((root/'evidence/nss128-analysis-label-correction.json').read_text())
assert label128['passed']and label128['historicPrefixSources']==1570 and len(manifest['sources'])>=1571
assert label128['historicPrefixCanonicalSha256']==hashlib.sha256(json.dumps(manifest['sources'][:1570],sort_keys=True,separators=(',',':')).encode()).hexdigest()
assert label128['newSourceSha256']==hashlib.sha256((root/'code'/label128['newSource']).read_bytes()).hexdigest()
assert not label128['actualMeasurementsChanged']and not label128['executionSourceAndFrozenInputsChanged']and not label128['routerWrites']and label128['original37SourcesUntouched']and label128['initialFailedCheckerRecorded']
for name,target in [('metrics',m128),('trial',t128)]:
    raw=(root/f'evidence/nss128-v1-{name}.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==label128['originalPublishedV1RetainedSha256'][name]
    v1=json.loads(raw);v2=copy.deepcopy(target);leaf=v2 if name=='metrics'else v2['metrics'];assert leaf['newCpuComparisonAccepted']is None;leaf['newCpuComparisonAccepted']=False;assert v1==v2

proof139=json.loads((root/'evidence/nss139-source-proof.json').read_text())
assert proof139['historicPrefixSources']==1571 and proof139['sources']==261 and len(manifest['sources'])>=1832
assert proof139['historicPrefixCanonicalSha256']==hashlib.sha256(json.dumps(manifest['sources'][:1571],sort_keys=True,separators=(',',':')).encode()).hexdigest()
assert len(proof139['sourceHashes'])==261 and proof139['actualBindingTreesRetained']and proof139['privateHostBootstrapExcluded']
for source,digest in proof139['sourceHashes'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==digest
x139=json.loads((root/'evidence/nss139-mainline.json').read_text());rt139=json.loads((root/'evidence/nss139-runtime.json').read_text())
assert x139['round']==rt139['round']=='NSS139'and x139['hardwareEntryRound']==138 and x139['boundInputs']==rt139['qualifiedExperimentalEntryBoundInputs']==1340 and x139['oneWan']==2
assert (x139['classifierMaximumLeaseSeconds'],x139['nativeSessionSeconds'],x139['independentOwnerMaximumSeconds'],x139['clientMaximumSeconds'])==(6,27,100,180)
assert all(x139[k]for k in ['onlyTcpBulkAndUdpRt','completeSameQueryClassEvidence','exactAffectedTcpCiRetired','remainingUdpSameCiRtTagsVerified','sameSocketCtMarkNatWanAcrossEpochs','newKernelPinAndDifferentEcmCiVerified','successOnlyOwnerEarlyCompletionAfterFullRestoration','failureOwnerMaximumUnchanged','firstRetirementAlsoPassedIn135','residentUpTagZeroUnchanged','naturalWorkerRecoveryObserved'])
assert not any(x139[k]for k in ['projectionAbsenceAloneAccepted','overall135RelearningPassed','residentClassifierChanged','classifierFailureRootCauseProved','newCpuComparison','humanCs2Acceptance','highLoad300MbpsAcceptance','fullCakeReplacementAccepted','nssPermanentlyEnabled','uiOperated','newDownloadStarted','upstreamSubmitted'])
assert x139['ecmCountsFirst']==[2,1,0]and x139['ecmCountsSecond']==[0,2,0]and x139['finiteLoadsClosed']==7 and x139['ownedSshReceiversRemaining']==0
life139=json.loads((root/'evidence/nss139-class-lifecycle.json').read_text());lp=life139['proof']
assert lp['passed']and lp['oldClass']=='BULK'and lp['newClass']=='BE'and lp['reason']=='cooldown'and lp['affectedSlots']==['tcp']and lp['sourceQuerySequence']==1031
assert all(lp[k]for k in ['realClassChange','sameQueryCompleteClassifierFrame','sameSocketCtMarkNatWan','cpuReaderBarrierConfirmed','actualCiAbsenceAndRemainingUdpAcceleratedVerified','remainingUdpSameCiAndRtTags','oldGenerationNeverReopenedOrExtendedAfterTerminal','oldTagsRemovedAfterCiAbsence','freshIndependentCheckpointAndOwnerForRelearning','freshKernelPinAndNativeGeneration','sameTcpUdpCtIdentitiesAcrossGenerations','newClassificationAndDifferentEcMSerials'])
assert not lp['projectionAbsenceAloneAccepted']and not lp['barrierIsFirmwareDestroyAck']and not lp['gameQualityConclusion']and not lp['cpuComparisonThisRound']and not lp['fullProductionNssRetained']
assert lp['twoDirectionRetirementRequests']==2 and lp['ecmCounts']==[2,1,0]and 2<lp['remainingOldLeaseAtSingleRetirementSeconds']<3 and .15<lp['queryDurationSeconds']<.25
for t in [life139['first'],life139['second']]:
    assert t['passed']and not t['completeABA']and t['sourceInputs']==1340 and t['sourceInputsCurrentAndFrozenMatch']and t['guardianVerifiedBeforeFirstWrite']and t['checkpointDownloadedShaAndGzipVerified']and all(t['rollback'].values())
    assert t['baseline']['configurationMatches']and t['beforeFullAudit']['passed']and t['afterFullAudit']['passed']and t['error']is None
    for slot,up,down in [('tcp',0x8e050000,0x8f050000),('udp',0x8e060000,0x8f060000)]:
        v=t['actualAcceleratedIdentity']['proof'][slot];assert v['upTag']==up and v['downTag']==down and v['ctMark']==0x20000 and v['natCorrect']and v['wanAffinity']==2
for slot in ['tcp','udp']:assert life139['first']['actualAcceleratedIdentity']['proof'][slot]['serial']!=life139['second']['actualAcceleratedIdentity']['proof'][slot]['serial']
owners139=json.loads((root/'evidence/nss139-owner-completion.json').read_text());assert len(owners139)==2
for o in owners139:
    assert o['successOnlyEarlyOwnerCompletion']and o['successRecordGraceSeconds']==5 and o['independentMaximumSeconds']==100 and o['guardianVerifiedBeforeWrite']and o['completeUndoVerified']and o['allOriginalQueuesAndModulesRestoredBeforeEarlyCompletion']
    assert o['execBytes']<=9000 and o['qosBundleBytes']<=73728
q139=json.loads((root/'evidence/nss139-qualification.json').read_text());assert q139['actualBindingInputs']==1340 and q139['newSuccessOnlyTargetRamChecks']==11 and q139['earlierCompleteReclassificationTargetRamChecks']==12 and q139['earlierModelsInheritedByteExactNotReexecuted']and q139['modelInputsAreMocked']
assert len(q139['entryChecks'])==11 and all(v['passed']for v in q139['entryChecks'])and q139['wholeStageRecordReadMaximumBytes']==1048576
prior135=json.loads((root/'evidence/nss139-first-retirement.json').read_text());assert prior135['passed']and not prior135['overallTwoEpochDriverPassed']and not prior135['freshGenerationRelearningAttempted']and all(prior135['rollback'].values())
failed133=json.loads((root/'evidence/nss139-failed-class-change.json').read_text());assert not failed133['passed']and failed133['ecmOpened']and not failed133['actualApplicationPauseOccurred']and not failed133['classChangePhysicallyProved']and all(failed133['rollback'].values())
staging131=json.loads((root/'evidence/nss139-staging-recovery.json').read_text());assert staging131['originalFailurePreserved']and staging131['checkpointDownloadedShaAndGzipVerified']and staging131['guardianVerifiedBeforeWrite']and all(staging131['undo'].values())and staging131['laterOriginalFullOperationalAuditPassed']and staging131['actualActivationStateUnavailable']and not staging131['activationOrEcmOpeningProved']
failures139=json.loads((root/'evidence/nss139-failures.json').read_text());assert len(failures139)==8 and all(v['originalFailurePreserved']for v in failures139)
recovery139=json.loads((root/'evidence/nss139-classifier-recovery.json').read_text());assert recovery139['previousWorkerPid']==4859 and recovery139['currentWorkerPid']==31657 and recovery139['guardianPid']==17139 and recovery139['naturalProcdRecovery']and recovery139['fullOriginalAuditPassedAfterRecovery']and recovery139['sourceConfigUnchanged']
assert not recovery139['forcedRestartOrReinstall']and not recovery139['rootCauseProved']and recovery139['orphanBatchPidCollisionIsUnconfirmedHypothesis']and recovery139['actualChildPidAndStderrUnavailable']
closures139=json.loads((root/'evidence/nss139-endpoint-closure.json').read_text());assert len(closures139)==7
for c in closures139:assert c['temporaryFirewallRulesRemaining']==0 and c['canonicalFirewallBaselineRestored']and c['ownedUnitInactiveMainPidZeroPortsClosed']and c['clientExited']and c['clientGuardPassed']and c['endpointGuardianVerifiedBeforeWrite']
receiver139=json.loads((root/'evidence/nss139-receiver-closure.json').read_text());assert receiver139['passed']and receiver139['readonly']and receiver139['exactOwnedReceiverAndTimeoutProcessesRemaining']==0
assert rt139['historical128RuntimePreservedSha256']==proof139['oldNss128RuntimeRetainedExactSha256']==hashlib.sha256((root/'evidence/nss128-runtime.json').read_bytes()).hexdigest()
assert rt139['workerPid']==31657 and rt139['guardianPid']==17139 and rt139['currentNssAdmissionMustBeRefreshedBeforeWrite']and rt139['physicalClassChangeRetirementAccepted']and rt139['freshEpochRelearningSameCtAccepted']
assert not rt139['nssPermanentlyEnabled']and not rt139['realHumanGameAcceptance']and not rt139['newCpuComparisonAcceptedThisTurn']
assert all(rt139['audit'][k]for k in ['passed','originalFullLockedNativeAudit','unrelatedConfigurationMatches','ecmStoppedAndZero','noActiveTransaction','noStaging','noExperimentState','noExperimentalModule'])
assert all(rt139['physicalRootRestoreAudit'][k]for k in ['passed','physicalWanOriginalMqFourFqCodelRestored','lan4OriginalMqFourFqCodelRestored','defaultQueueOptionsAndHandlesExact'])

proof141=json.loads((root/'evidence/nss141-source-proof.json').read_text())
assert proof141['historicPrefixSources']==1832 and proof141['sources']==53 and len(manifest['sources'])>=1885
assert proof141['historicPrefixCanonicalSha256']==hashlib.sha256(json.dumps(manifest['sources'][:1832],sort_keys=True,separators=(',',':')).encode()).hexdigest()
assert len(proof141['sourceHashes'])==53 and proof141['preparedInputsCurrentAndFrozenMatch']and proof141['preparedBindings']==1385 and proof141['privateHostBootstrapExcluded']and proof141['originalFailuresKept']
for source,digest in proof141['sourceHashes'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==digest
x141=json.loads((root/'evidence/nss141-mainline.json').read_text());rt141=json.loads((root/'evidence/nss141-runtime.json').read_text());q141=json.loads((root/'evidence/nss141-entry-qualification.json').read_text());f141=json.loads((root/'evidence/nss141-fast-qualification.json').read_text())
assert x141['round']==rt141['round']=='NSS141'and x141['preparedEntryRound']==140 and x141['preparedBindings']==rt141['preparedRealEntryBoundInputs']==1385 and x141['inheritedBindings']==1340 and x141['newEntryBindings']==45
assert all(x141[k]for k in ['realEntryIntegrated','readonlyDefaultInspectExecuted','historicalFullFrameMappingReplayOnly','fullFactorySyntaxCompiled','residentUpTagZeroUnchanged','partialClassChangeNeverCompletesAba','freshCheckpointAndNewEpochRequiredAfterClassChange','originalByteAndDeadlineCapsKept'])
assert not any(x141[k]for k in ['wholeFactoryAbaExecutedThisRound','newVersionHardwareAbaPassed','newCpuComparison','humanCs2Acceptance','productionWrites','checkpointOrStageStarted','ecmOpened','residentClassifierChanged','nssPermanentlyEnabled','fullCakeReplacementAccepted','uiOperated','newDownloadStarted','upstreamSubmitted'])
assert x141['currentRealGameCandidates']==x141['currentRealBulkCandidates']==x141['currentSameWanPairs']==0
assert (x141['sourceMaximumSeconds'],x141['nativeMaximumSeconds'],x141['ownerMaximumSeconds'],x141['packetBundleBytes'],x141['guardianExecBytes'])==(6,27,100,73574,8907)
assert q141['passed']and q141['integratedRealEntry']and not q141['productionExecution']and q141['partialClassChangeIsNotCompletedAba']and q141['fullRowsRetainedForClassMapping']and not q141['actualHardwareAbaThisVersion']and q141['wholeFactoryAbaNotExecutedThisRound']
assert q141['inheritedBoundInputs']==1340 and len(q141['newEntrySourceHashes'])==45 and len(q141['checks'])==6 and all(c['passed']for c in q141['checks'])and q141['nativeModels']['checks']==10
for source,digest in q141['newEntrySourceHashes'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==digest
assert f141['passed']and f141['checks']==10 and f141['wholeFactoryCompiledInTargetRam']and f141['onlyNewObserveAndRetireBranchesExecutedWithMockedBackend']and f141['wholeFactoryAbaNotExecutedThisRound']and not f141['actualHardwareTestThisVersion']
assert f141['sourceSha256']==hashlib.sha256((root/'code/work/nss140/fast-path.lua').read_bytes()).hexdigest()and all(v['passed']and v['targetRamOnly']and v['mockedClockCountersClassifierAndFirmware']and not v['routerWrites']and not v['hardwareProof']for v in f141['cases'])
ready141=json.loads((root/'evidence/nss141-readonly-readiness.json').read_text());reader141=json.loads((root/'evidence/nss141-readonly-reader.json').read_text())
assert ready141['mode']=='inspect'and ready141['sameWanPairs']==0 and not ready141['routerWrites']and not ready141['trafficGenerated']and not ready141['openFrontend']and not ready141['nssPermissionGranted']
assert reader141['readonly']and reader141['actualCs2RtCandidates']==reader141['actualSteamBulkCandidates']==0 and not reader141['nssAdmissionAllowed']
size141=json.loads((root/'evidence/nss141-size-review.json').read_text());assert size141['passed']and size141['sizeReviewOnly']and size141['packetProtocolFieldsValidated']and size141['invalidV1SizeModelRetained']and len(size141['cases'])==3 and size141['noBudgetWidened']and size141['oversizedFutureRealInputMustRefuseBeforeStage']
for c in size141['cases']:assert c['renderingOnly']and not c['currentNssAuthorization']and not c['productionWrites']and c['qosBundleFitsOriginal73728']and c['guardianFitsOriginal9000']and c['qosBundleBytes']<=73728 and c['guardianExecBytes']<=9000
fail141=json.loads((root/'evidence/nss141-failures.json').read_text());assert len(fail141)==5 and all(not v['passed']and v['originalPreserved']and not v['routerConnectionStarted']and not v['checkpointOrStageStarted']and not v['ecmOpened']for v in fail141)
assert fail141[0]['actualRecord']['firstQualificationSourcesFrozen']==43 and fail141[1]['originalReportedPassedButModelInvalid']
assert fail141[4]['approvalOrCommitChainStoppedBeforeCommit']and not fail141[4]['sourceBytesChanged']and fail141[4]['line']==209 and len(fail141[4]['files'])==4
assert rt141['historical139RuntimePreservedSha256']==proof141['oldNss139RuntimeRetainedExactSha256']==hashlib.sha256((root/'evidence/nss139-runtime.json').read_bytes()).hexdigest()
assert rt141['workerPid']==31657 and rt141['guardianPid']==17139 and rt141['currentNssAdmissionMustBeRefreshedBeforeWrite']and not rt141['preparedRealEntryHardwareAbaTested']and not rt141['nssPermanentlyEnabled']and not rt141['realHumanGameAcceptance']and not rt141['newCpuComparisonAcceptedThisTurn']
assert all(rt141['audit'][k]for k in ['passed','originalFullLockedNativeAudit','unrelatedConfigurationMatches','ecmStoppedAndZero','noActiveTransaction','noStaging','noExperimentState','noExperimentalModule'])
assert all(rt141['physicalRootRestoreAudit'][k]for k in ['passed','physicalWanOriginalMqFourFqCodelRestored','lan4OriginalMqFourFqCodelRestored','defaultQueueOptionsAndHandlesExact'])
assert json.loads((root/'evidence/nss141-receiver-closure.json').read_text())['exactOwnedReceiverAndTimeoutProcessesRemaining']==0
proof142=json.loads((root/'evidence/nss142-source-proof.json').read_text())
assert proof142['historicPrefixSources']==1885 and proof142['sources']==7 and len(manifest['sources'])>=1892
assert proof142['historicPrefixCanonicalSha256']==hashlib.sha256(json.dumps(manifest['sources'][:1885],sort_keys=True,separators=(',',':')).encode()).hexdigest()
assert len(proof142['sourceHashes'])==7 and proof142['preparedBindings']==1385 and proof142['preparedInputsCurrentAndPreviouslyFrozenMatch']and proof142['privateHostBootstrapExcluded']and proof142['credentialsCtNoncesConfigurationCheckpointsAndBinariesExcluded']and proof142['originalFailuresKept']
for source,digest in proof142['sourceHashes'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==digest
x142=json.loads((root/'evidence/nss142-mainline.json').read_text());rt142=json.loads((root/'evidence/nss142-runtime.json').read_text())
assert x142['round']==rt142['round']=='NSS142'and x142['preparedBindings']==rt142['preparedRealEntryBoundInputs']==1385
assert all(x142[k]for k in ['morningClosureAfterBeijing0940','readonlyOnly','originalFullLockedNativeAuditPassed','bothPhysicalRootsExact','endpointsAndClientsClosed','currentAndPreviouslyFrozenInputsExact','residentUpTagZeroUnchanged','knownWan4AuthenticationFailureStillPresent','existingFourWanAutomaticFailoverExact','localToolSyntaxRejectionPreserved','historicEvidenceAndFailuresKept','pauseThisNightHeartbeatImmediatelyAfterPublishedArchiveVerification'])
assert not any(x142[k]for k in ['residentClassifierChanged','productionWrites','checkpointOrStageStarted','ecmOpened','modelsReplayed','newHardwareAbaProof','newCpuComparison','humanCs2Acceptance','steamDownloadOperated','desktopOperated','nssPermanentlyEnabled','fullCakeReplacementAccepted'])
assert x142['previousEndpointLoadsChecked']==7 and x142['ownedSshReceiversRemaining']==0
assert rt142['historical141RuntimePreservedSha256']==proof142['oldNss141RuntimeRetainedExactSha256']==hashlib.sha256((root/'evidence/nss141-runtime.json').read_bytes()).hexdigest()
assert rt142['morningReadonlyClosureCompleted']and rt142['currentNssAdmissionMustBeRefreshedBeforeWrite']and not rt142['preparedRealEntryHardwareAbaTested']and not rt142['nssPermanentlyEnabled']and not rt142['realHumanGameAcceptance']and not rt142['newCpuComparisonAcceptedThisTurn']
assert all(rt142['audit'][k]for k in ['passed','readonly','originalFullLockedNativeAudit','unrelatedConfigurationMatches','exactWan4AutomaticFailoverProved','ecmStoppedAndZero','noActiveTransaction','noStaging','noExperimentState','noExperimentalModule'])and not rt142['audit']['allFiveWanHealthy']
assert all(rt142['physicalRootRestoreAudit'][k]for k in ['passed','readonly','physicalWanOriginalMqFourFqCodelRestored','lan4OriginalMqFourFqCodelRestored','defaultQueueOptionsAndHandlesExact'])
end142=json.loads((root/'evidence/nss142-endpoint-client-closure.json').read_text());assert end142==rt142['endpointClientClosureAudit']and end142['passed']and end142['readonly']and end142['previousLoadsChecked']==end142['ownedUnitsInactiveMainPidZero']==7 and end142['allSevenCanonicalFirewallBaselinesMatch']and end142['tcpAndUdpPortsClosed']and end142['clientProcessesMatchedByExactOwnedLoadPaths']and end142['temporaryFirewallRulesRemaining']==end142['ownedClientOrGuardProcessesRemaining']==0 and not end142['remoteWrites']and not end142['productionWrites']and not end142['desktopOperated']
assert json.loads((root/'evidence/nss142-receiver-closure.json').read_text())['exactOwnedReceiverAndTimeoutProcessesRemaining']==0
bind142=json.loads((root/'evidence/nss142-prepared-bindings.json').read_text());assert bind142['passed']and bind142['boundInputs']==1385 and bind142['currentAndPreviouslyFrozenInputsExact']and not bind142['modelsReplayed']and not bind142['routerConnected']and not bind142['productionWrites']and not bind142['newHardwareAbaProof']
reader142=json.loads((root/'evidence/nss142-inherited-readers.json').read_text());assert reader142['passed']and reader142['readOnlyReaders']and len(reader142['files'])==3
for f in reader142['files']:
 old=(root/'code/work/nss141'/f['file']).read_bytes();new=(root/'code/work/nss142'/f['file']).read_bytes()
 assert f['namespaceOnlyChange']and hashlib.sha256(old).hexdigest()==f['priorSha256']and hashlib.sha256(new).hexdigest()==f['sha256']and new.replace(b'work/nss142',b'work/nss141')==old
fail142=json.loads((root/'evidence/nss142-failures.json').read_text());assert len(fail142)==1 and not fail142[0]['passed']and fail142[0]['originalFailurePreserved']and not fail142[0]['nestedToolsDispatched']and not fail142[0]['routerAuditStarted']and not fail142[0]['productionWrites']
proof148=json.loads((root/'evidence/nss148-source-proof.json').read_text())
assert proof148['historicPrefixSources']==1892
assert proof148['historicPrefixCanonicalSha256']==hashlib.sha256(json.dumps(manifest['sources'][:1892],sort_keys=True,separators=(',',':')).encode()).hexdigest()
assert proof148['sources']==len(proof148['sourceHashes']) and len(manifest['sources'])>=1892+proof148['sources']+2
assert proof148['sourcesByRound']=={'143':7,'144':21,'145':23,'146':45,'147':37,'148':9}
assert all(proof148[k]for k in ['sourceBindingsActualAndFrozenMatch','privateHostBootstrapExcluded','credentialsCtNoncesConfigurationCheckpointsAndBinariesExcluded','historicFilesExceptCurrentRuntimeAllBytesRetained','originalFailuresKept','wholeFactoryRamAbaNotClaimed','actualWholeFactoryHardwareAbaPassed'])
assert proof148['boundInputsInActualControlledCase']==1518 and proof148['realPreparedBoundInputs']==1527
for source,digest in proof148['sourceHashes'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==digest
rt148=json.loads((root/'evidence/nss148-runtime.json').read_text());x148=json.loads((root/'evidence/nss148-mainline.json').read_text())
assert rt148['round']==x148['round']=='NSS148'
assert rt148['historical142RuntimePreservedSha256']==proof148['oldNss142RuntimeRetainedExactSha256']==hashlib.sha256((root/'evidence/nss142-runtime.json').read_bytes()).hexdigest()
assert rt148['workerPid']==31657 and rt148['guardianPid']==17139 and rt148['classifierConfigSha256']==rt142['classifierConfigSha256']
assert rt148['qualifiedExperimentalEntry']=='work/nss147/controlled-session.mjs' and rt148['qualifiedExperimentalEntryBoundInputs']==1518
assert rt148['preparedRealEntry']=='work/nss148/real-session.mjs' and rt148['preparedRealEntryBoundInputs']==1527
assert rt148['controlledExperimentalFactoryHardwareAbaPassed'] and not rt148['preparedRealEntryHardwareAbaTested']
assert all(x148[k]for k in ['backgroundOwnedTcpAndUdpUsed','controlledHardwareAbaPassed','realDefaultInspectExecuted','residentUpTagZeroUnchanged','actualClassToFourTagsAndFourLeaves','pbrFullCtMarkNatWanAffinityUnchanged','rollbackAndAllEndpointsClosed','harnessBugRootCauseProved','oldNativeEpochOnlyBypassedWhenBothFrontendsStoppedAndEcmAllZero','sourceAndActiveNativeDeadlinesNotWidened','originalFailuresKept','nightHeartbeatRemainsPaused'])
assert not any(x148[k]for k in ['residentClassifierChanged','desktopOperatedThisBackgroundTest','steamOrCs2OperatedThisBackgroundTest','preparedRealWrapperHardwareAbaPassed','newCpuComparisonAccepted','humanCs2Acceptance','highLoad300MbpsAcceptance','longTermAcceptance','fullCakeReplacementAccepted','productionNssPermanentlyEnabled','upstreamNssDefectClaimed','upstreamSubmitted'])
assert not rt148['nssPermanentlyEnabled'] and not rt148['realHumanGameAcceptance'] and not rt148['newCpuComparisonAcceptedThisTurn'] and rt148['nightHeartbeatRemainsPaused']
t148=json.loads((root/'evidence/nss148-trial.json').read_text())
assert t148['round']=='NSS147' and t148['passed'] and t148['controlledRealWanPair'] and not t148['realCs2SteamPair']
assert t148['oneWan']==5 and t148['tcpClass']=='BULK' and t148['udpClass']=='RT'
assert t148['frames']==123 and t148['nativeRenewals']==7 and t148['sourceBindingsActualAndFrozen']==1518
assert t148['guardianExecBytesActual']==8899 and t148['packetBundleBytesActual']==73686
assert (t148['sourceMaximumSeconds'],t148['nativeMaximumSeconds'],t148['ownerMaximumSeconds'],t148['recordReadMaximumBytes'])==(6,27,100,1048576)
assert [p['name']for p in t148['phases']]==['A','B','A2']
assert [p['acceleratedCounts']for p in t148['phases']]==[[0],[2],[0]]
assert all(p['completed']and 20<=p['seconds']<21.5 and p['samples']==41 for p in t148['phases'])
assert all(t148[k]for k in ['newCheckpointDownloadedShaAndGzipVerified','independentRollbackVerifiedBeforeFirstWrite','detachedOwnerParentAndPipeIdentityVerified','actualFourEcmTagsVerified','pbrFullCtMarkNatWanAffinityVerified','allFourFqCodelLeavesHavePackets','freshSourceAndIdentityCheckedInSoftwarePhases','ecmStoppedAndAllCountsZeroRequiredBeforeClosedComparison','activeNativeLeaseAndRenewalStillStrict','terminalReclassificationBodyUnchangedFrom140','explicitEarlyRetirementAndFirmwareZero','fullProtectedBaselineRestored','bothPhysicalRootsRestored','exactStageStateModuleRemovalVerified'])
assert not any(t148[k]for k in ['humanGameAcceptance','strictCpuComparabilityAccepted','fullCakeReplacementAccepted','nssPermanentlyEnabled'])
m148=json.loads((root/'evidence/nss148-metrics.json').read_text())
assert m148['passed']and m148['oneWan']==5 and m148['direction']=='download'
assert not m148['comparabilityAccepted']and m148['softirqRelativeReductionPercent'] is None
assert set(k for k,v in m148['comparisonChecks'].items() if not v)=={'unselectedWanTotalLe0_5MbpsEach','unselectedWanTotalRangeLe0_25Mbps'}
assert len(m148['comparisonChecks'])==7 and m148['actualDualEcmTagsVerified']and m148['pbrCtMarkNatWanAffinityVerified']
assert all(not p['classifierCheckDurationObserved']and p['classifierCheckSecondsMean'] is None and p['classifierQueryAgeSecondsMean']>=0 for p in m148['phases'])
assert [p['whole']['udp']['sent']for p in m148['phases']]==[864,875,838]
assert [p['whole']['udp']['received']for p in m148['phases']]==[863,873,824]
assert all(p['whole']['timeSqueezeDelta']==p['whole']['softnetDropDelta']==0 and not p['whole']['udp']['isCs2Metric']for p in m148['phases'])
assert all(25<p['whole']['clientTcpReceivedMbps']<28 for p in m148['phases'])
leaf148=m148['leafDeltasAcrossBNearbyAsyncSnapshots']
assert leaf148['down']['8f05:']['dropped']==379 and leaf148['down']['8f06:']['dropped']==0 and leaf148['up']['8e06:']['dropped']==0 and leaf148['up']['8e05:']['dropped']==0
assert m148['leafStatisticsAsynchronous']and not m148['humanCs2Acceptance']and not m148['highLoad300MbpsAcceptance']and not m148['fullCakeReplacementAccepted']and not m148['productionNssRetained']
q147=json.loads((root/'evidence/nss148-controlled-entry-qualification.json').read_text());q148=json.loads((root/'evidence/nss148-real-entry-qualification.json').read_text())
assert q147['passed']and q147['actualFacadeIncluded']and q147['inheritedBoundInputs']==1481 and len(q147['sourceManifest'])==37
assert q147['models']['checks']==9 and len(q147['models']['cases'])==9 and all(c['passed']and not c['hardwareProof']and not c['routerWrites']for c in q147['models']['cases'])
assert q147['consumerModels']['checks']==8 and q147['completeActualConsumerTestedSeparately']and q147['phaseInspectorMockedExplicitly']
assert not q147['wholeFactoryAbaExecutedWithMockedBackend']and not q147['productionExecution']
assert q147['budgets']==q148['budgets']==[6,27,100,9000,65536,73728]
assert q147['payloadBytes']==73685 and q147['qualificationGuardianExecBytes']==8903 and q147['modelExecBytes']==8375
assert q148['passed']and q148['sameTestedNss147Factory']and q148['candidateVisibilityAdapter143']and q148['defaultReadonly']
assert q148['inheritedBindings']==1518 and len(q148['sourceManifest'])==9 and q148['controlledHardwareAbaAccepted']and not q148['realWrapperHardwareAbaAccepted']
assert q148['auditCaseNamespaceAndExactSourceDependenciesChecked']
for q in [q147,q148]:
 for source,digest in q['sourceManifest'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==digest
# Verify the exact corrective diff; unchanged active lease and retirement code
# cannot be replaced by a model-only passing receipt.
c140=(root/'code/work/nss140/classifier.lua').read_text();c146=(root/'code/work/nss146/classifier.lua').read_text();c147=(root/'code/work/nss147/classifier.lua').read_text()
assert c146.replace('function M.compareEpoch(epoch,s,c,now,closed)','function M.compareEpoch(epoch,s,c,now)').replace('or(not closed and now>=epoch.epochUntil)then','or now>=epoch.epochUntil then').replace('function out.compareObserved(closed)','function out.compareObserved()').replace('Consumer.compareEpoch(epoch,out.lastObservedSnapshot,out.lastObservedContext,now(),closed)','Consumer.compareEpoch(epoch,out.lastObservedSnapshot,out.lastObservedContext,now())')==c140
assert c147.replace('function A.compareObserved(closed)return assert(activeInstance).compareObserved(closed)end','function A.compareObserved()return assert(activeInstance).compareObserved()end')==c146
fast140=(root/'code/work/nss140/fast-path.lua').read_text();fast147=(root/'code/work/nss147/fast-path.lua').read_text()
assert fast147.replace('  if not active then stopped()end\n','').replace('A.compareObserved(not active)','A.compareObserved()').replace('   R.rejectedComparison=C\n','')==fast140
real148=(root/'code/work/nss148/real-session.mjs').read_text();audit148=(root/'code/work/nss148/current-audit-diagnostic.mjs').read_text()
assert "from '../nss147/module-stage.mjs'"in real148 and "process.argv[2]??'inspect'"in real148
assert "real-matched-aba"in audit148
assert "'../nss143/candidate-adapter.mjs'"in (root/'code/work/nss148/read-real-candidates.mjs').read_text()
for f in ['failed-wan-owner.lua','declared-baseline.mjs']:assert (root/'code/work/nss148'/f).read_bytes()==(root/'code/work/nss147'/f).read_bytes()
r148=json.loads((root/'evidence/nss148-readonly-readiness.json').read_text())
assert r148['mode']=='inspect'and r148['sameWanPairs']==0 and not r148['routerWrites']and not r148['trafficGenerated']and not r148['openFrontend']and not r148['nssPermissionGranted']
assert r148==rt148['latestRealReadonlyInspect']
end148=json.loads((root/'evidence/nss148-endpoint-client-closure.json').read_text())
assert end148==rt148['endpointClientClosureAudit']and end148['passed']and end148['readonly']
assert end148['previousLoadsChecked']==end148['ownedUnitsInactiveMainPidZero']==11 and end148['temporaryFirewallRulesRemaining']==end148['ownedClientOrGuardProcessesRemaining']==0
assert end148['allCanonicalFirewallBaselinesMatch']and end148['tcpAndUdpPortsClosed']and end148['existingEndpointServicesUnchanged']and not end148['remoteWrites']and not end148['desktopOperated']
assert all(rt148['audit'][k]for k in ['passed','originalFullLockedNativeAudit','unrelatedConfigurationMatches','exactWan4AutomaticFailoverProved','ecmStoppedAndZero','noActiveTransaction','noStaging','noExperimentState','noExperimentalModule'])and not rt148['audit']['allFiveWanHealthy']
assert all(rt148['physicalRootRestoreAudit'][k]for k in ['passed','physicalWanOriginalMqFourFqCodelRestored','lan4OriginalMqFourFqCodelRestored','defaultQueueOptionsAndHandlesExact'])
assert rt148['ownedReceiverClosureAudit']['passed']and rt148['ownedReceiverClosureAudit']['exactOwnedReceiverAndTimeoutProcessesRemaining']==0
fail148=json.loads((root/'evidence/nss148-failures.json').read_text())
assert len(fail148)==11 and all(not f['passed']and f['originalPreserved']for f in fail148)
assert all(not f['ecmOpened']for f in fail148 if 'ecmOpened'in f)
assert fail148[1]['firstUiClickDispatchedAfterFailedGuardCheck']and fail148[1]['downloadResumeWasNotProvenGuardedBeforeEffect']and not fail148[1]['finalUiRestoreClaimed']
assert not fail148[4]['immediateRecoveryBaselineAuditPassed']and fail148[4]['subsequentOriginalFullHealthAuditPassed']and fail148[4]['rejectionReason']=='epoch expired'
assert fail148[-1]['correctedDurationIsNullAndObservedFalse']and not fail148[-1]['hardwareExperimentRerun']
pub148=json.loads((root/'evidence/nss148-publication-failure.json').read_text())
assert not pub148['passed']and pub148['originalFailurePreserved']and pub148['firstExportPartiallyCompleted']and pub148['originalScriptAndExportedEvidenceBytesKept']
assert not pub148['commitOrPushStarted']and not pub148['productionWrites']and not pub148['hardwareTestRerun']
pubproof148=json.loads((root/'evidence/nss148-publication-recovery-source-proof.json').read_text())
assert pubproof148['historicPrefixSources']==2041 and pubproof148['sources']==1
assert pubproof148['historicPrefixCanonicalSha256']==hashlib.sha256(json.dumps(manifest['sources'][:2041],sort_keys=True,separators=(',',':')).encode()).hexdigest()
for source,digest in pubproof148['sourceHashes'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==digest
assert pubproof148['originalPublicationSourceAndEvidenceBytesKept']and pubproof148['noOperationalBindingChanged']and not pubproof148['hardwareTestRerun']and not pubproof148['productionWrites']
validation148=json.loads((root/'evidence/nss148-validation-failure.json').read_text())
assert not validation148['passed']and validation148['originalFailurePreserved']and validation148['commitOrPushChainStopped']and validation148['actualTrialEvidenceWasAlreadyCorrect']
assert validation148['actualStageBundleBytes']==t148['packetBundleBytesActual']==73686 and validation148['qualificationModelBundleBytes']==q147['payloadBytes']==73685
assert not validation148['operationalSourceOrRuntimeChanged']and not validation148['hardwareTestRerun']
whitespace148=json.loads((root/'evidence/nss148-whitespace-failure.json').read_text())
assert not whitespace148['passed']and whitespace148['originalFailurePreserved']and whitespace148['commitOrPushChainStoppedBeforeCommit']
assert len(whitespace148['files'])==6 and not whitespace148['sourceBytesChanged']
attributes148=(root/'.gitattributes').read_text()
for f in whitespace148['files']:
 assert hashlib.sha256((root/f['path']).read_bytes()).hexdigest()==f['sha256']
 assert '/'+f['path']+' whitespace=cr-at-eol,'+f['attribute']in attributes148
whitespace2148=json.loads((root/'evidence/nss148-whitespace-attribute-failure.json').read_text())
assert not whitespace2148['passed']and whitespace2148['originalFailurePreserved']and whitespace2148['commitOrPushChainStoppedBeforeCommit']
assert whitespace2148['attributeOverrideDroppedInheritedCrAtEol']and not whitespace2148['sourceBytesChanged']
archivefail148=json.loads((root/'evidence/nss148-archive-verifier-failure.json').read_text())
assert not archivefail148['passed']and archivefail148['originalFailurePreserved']and archivefail148['firstPublishedArchiveRepositoryCheckerPassed']
assert archivefail148['failingHistoricalFileOriginalGitBlobUnchanged']and archivefail148['worktreeContainsCrLf']and archivefail148['normalizationOnlyExplainsMismatch']
assert not archivefail148['historicalSourceOrEvidenceChanged']and not archivefail148['hardwareTestRerun']
archiveproof148=json.loads((root/'evidence/nss148-archive-recovery-source-proof.json').read_text())
assert archiveproof148['historicPrefixSources']==2042 and archiveproof148['sources']==1
assert archiveproof148['historicPrefixCanonicalSha256']==hashlib.sha256(json.dumps(manifest['sources'][:2042],sort_keys=True,separators=(',',':')).encode()).hexdigest()
for source,digest in archiveproof148['sourceHashes'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==digest
assert archiveproof148['comparisonUsesOriginalGitBlobs']and archiveproof148['failedFirstVerifierSourceBytesRetained']and not archiveproof148['operationalBindingsChanged']
# NSS150 is a bounded automatic successor proof, not matched CPU or human-game acceptance.
x150=json.loads((root/'evidence/nss150-mainline.json').read_text());rt150=json.loads((root/'evidence/nss150-runtime.json').read_text())
assert x150['round']==rt150['round']=='NSS150' and x150['passed'] and x150['boundedTwoEpochAutomaticLifecyclePassed']
assert len(manifest['sources'])>=2148 and x150['exportedSources']==105
proof150=json.loads((root/'evidence/nss150-source-proof.json').read_text())
assert proof150['historicPrefixSources']==2043 and proof150['sources']==len(proof150['sourceHashes'])==105
assert proof150['historicPrefixCanonicalSha256']==hashlib.sha256(json.dumps(manifest['sources'][:2043],sort_keys=True,separators=(',',':')).encode()).hexdigest()
assert proof150['historicManifestPrefixUnchanged'] and proof150['originalFailuresKept'] and proof150['credentialsCtNoncesConfigurationCheckpointsAndBinariesExcluded'] and proof150['qualifiedActualEntryBindings']==1609
for source,digest in proof150['sourceHashes'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==digest
assert x150['actualWan']==rt150['controlledWan']==3 and x150['generations']==rt150['generations']==2
assert x150['sourceBindingsActual']==rt150['boundInputs']==1609
assert x150['qualifiedController']==rt150['qualifiedExperimentalController']=='work/nss150/run-v5.mjs'
assert x150['factory']==rt150['controlledFactory']=='work/nss149/module-stage.mjs'
assert rt150['workerPid']==rt148['workerPid']==31657 and rt150['guardianPid']==rt148['guardianPid']==17139
assert rt150['classifierConfigSha256']==rt148['classifierConfigSha256'] and rt150['classifierDeployment']=='NSS68'
assert rt150['historical148RuntimePreservedSha256']==x150['oldNss148RuntimeRetainedExactSha256']==hashlib.sha256((root/'evidence/nss148-runtime.json').read_bytes()).hexdigest()
assert all(x150[k]for k in ['unchangedSocketCtMarkNatWanAcrossGenerations','newOwnerCheckpointTagNamespaceFrozenHashAndClassifierSequence','newNativeCisForBothFlows','oldNativeGateNeverReopened','oldEpochNeverExtended','classChangeRetirementCodeInheritedExactly','historical139ClassChangeProofNotRerun','wan5DownstreamUdpGapUnresolved','nightHeartbeatRemainsPaused','oldHistoryExperimentIndexEmptyPreserved','actualTrialReferencesRecoveredFromExactDriverReceipts','reportExportV1FailedBeforeRepositoryWrites'])
assert not any(x150[k]for k in ['matchedCpuABARunThisTurn','cs2ExperienceConclusion','highLoad300MbpsConclusion','permanentNssControllerInstalled','permanentNssEnabled','autoClassChangeRelearnInThisNewSupervisorTested','desktopOperated','steamOrCs2Started'])
assert x150['cpuReductionConclusion'] is None and rt150['cpuConclusion'] is None
assert rt150['controlledAutomaticLifecyclePassed'] and rt150['nightHeartbeatRemainsPaused'] and not rt150['nssPermanentlyEnabled'] and not rt150['realHumanGameAcceptance']
assert (x150['sourceNativeOwnerBudgets'],x150['clientHardSeconds'],x150['clientPreparationRemainingSeconds'])==([6,27,100],180,70)
trials150=json.loads((root/'evidence/nss150-trials.json').read_text());assert trials150==x150['trials'] and len(trials150)==2
for t150 in trials150:
 assert t150['passed'] and 20<=t150['stableSeconds']<21.5 and t150['sampleCount']==41 and t150['nativeRenewals']==6
 assert t150['observedEcmSequence']==[0,2,0] and t150['actualTagAndLeafCount']==4 and t150['sourceBindingsActual']==1609
 assert t150['payloadBytesActual']<=73728 and t150['guardianExecBytesActual']<=9000
 assert (t150['fixedNativeSessionSeconds'],t150['independentOwnerMaxSeconds'],t150['successGraceSeconds'])==(27,100,5)
 assert all(t150[k]for k in ['fullMarkNatWanAffinityCorrect','originalCtAndSocketHeld','newKernelPin','newCheckpointDownloadedShaGzipVerified','independentRollbackBeforeFirstWrite','parentAndPipeIdentityVerified','gateRemoved','physicalRootsRestored']) and all(t150['undoVerified'].values())
 mt150=t150['metrics'];assert mt150['selectedWan']==3 and 25<mt150['clientTcpReceivedMbps']<28 and mt150['sampleCount']==41 and mt150['nativeRenewals']==6
 assert mt150['timeSqueezeDelta']==mt150['softnetDropDelta']==mt150['udp']['unreturned']==0
 assert mt150['udp']['sent']==mt150['udp']['received'] and not mt150['udp']['cs2Metric'] and mt150['causalCpuReductionPercent'] is None
 assert not any(mt150[k]for k in ['sameLoadSoftwareNssSoftwareComparison','cs2Acceptance','permanentController','highLoad300Mbps'])
 leaves150=mt150['nssLeavesNearbyAsynchronousSnapshots'];assert all(v['packets']>0 for d in leaves150.values()for v in d.values())
 assert leaves150['down']['8f06:']['dropped']==leaves150['up']['8e06:']['dropped']==0
assert [t['metrics']['udp']['sent']for t in trials150]==[918,910]
ar150=json.loads((root/'evidence/nss150-automatic-result.json').read_text());assert ar150['passed'] and ar150['completedEpochs']==2
assert all(ar150[k]for k in ['finiteAutomaticSuccessorExecuted','sameSocketAndCtAcrossEpochs','newCheckpointOwnerClassificationPinAndCi','oldEpochNeverExtendedOrReopened'])
assert not any(ar150[k]for k in ['matchedCpuComparison','cs2Acceptance','permanentNssDeployment'])
q149=json.loads((root/'evidence/nss150-qualification149.json').read_text());q150=json.loads((root/'evidence/nss150-qualification-initial.json').read_text())
assert q149['passed'] and q149['inheritedBoundInputs']==1518 and len(q149['sourceManifest'])==40
assert q149['actualNewRunModeled'] and not q149['fullFactoryModeled'] and not q149['productionExecution'] and q149['finiteTwoEpochSupervisor']
assert q149['payloadBytes']==73636 and q149['qualificationGuardianExecBytes']==8923 and q149['modelExecBytes']==7622
assert q149['policyModels']['checks']==35 and q149['nativeModels']['checks']==5 and q149['nativeModels']['fullFactoryNotModeled'] and q149['nativeModels']['actualNewRunFunctionExecuted']
assert all(v['passed']and v['modelOnly']for v in q149['policyModels']['cases'])
assert all(v['passed']and v['actualNewRunAndMeasurementFunctions']and v['mockedBackend']and not v['hardwareProof']for v in q149['nativeModels']['cases'])
assert all(q149[k]for k in ['exactPermanentClassifierAndNativeGateUnchanged','actualClassChangeRetirementImplementationUnchanged','newOwnerAfterCompleteRestorationOnly'])
assert q150['passed'] and q150['inheritedBindings']==1558 and len(q150['sourceManifest'])==24 and q150['policyModels']['checks']==36
assert q150['sameActuallyTested149Factory'] and q150['onlyClientPreparationMarginChanged'] and q150['clientIsNotRequiredForIndependentRollback'] and q150['actualSourceNativeOwnerBoundsUnchanged']
assert (q150['requiredClientRemainingSeconds'],q150['clientHardDeadlineSeconds'],q150['independentOwnerHardDeadlineSeconds'])==(70,180,100)
qs150=[q149,q150]
for ver,old_count,new_count in [('v2',1582,7),('v3',1589,7),('v4',1596,6),('v5',1602,7)]:
 qv150=json.loads((root/('evidence/nss150-qualification-'+ver+'.json')).read_text());assert qv150['passed'] and qv150['inheritedBindings']==old_count and len(qv150['sourceManifest'])==new_count and not qv150['productionExecution'];qs150.append(qv150)
for qv150 in qs150:
 assert qv150['budgets']==[6,27,100,9000,65536,73728]
 for source,digest in qv150['sourceManifest'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==digest
assert qs150[-1]['pbrNatAndFirewallScopeUnchanged'] and qs150[-1]['noUdpRotationWithinLoad'] and qs150[-1]['independentDeadlinesUnchanged'] and qs150[-1]['wan5MissingDownstreamUdpTagRefusalRetained']
assert (root/'code/work/nss149/classifier.lua').read_bytes()==(root/'code/work/nss147/classifier.lua').read_bytes()
for f in ['download-server.py','client-watchdog.ps1','endpoint-firewall-guardian.py']:
 assert (root/'code/work/nss150'/f).read_bytes()==(root/'code/work/nss149'/f).read_bytes()
assert "from '../nss149/module-stage.mjs'"in (root/'code/work/nss150/controlled-session-v5.mjs').read_text()
fail150=json.loads((root/'evidence/nss150-failures.json').read_text());assert len(fail150)==x150['failuresPreserved']==10
assert all(not f['passed']and f['originalPreserved']for f in fail150)
assert fail150[4]['completedEpochs']==1 and not fail150[4]['secondEpochWrites']
assert fail150[-1]['case']=='150-v4-WAN5' and fail150[-1]['checkpointCreated'] and not fail150[-1]['ecmOpened'] and fail150[-1]['physicalRootsRestored'] and not fail150[-1]['downstreamGapRootCauseResolved']
for f in fail150:
 if 'ecmOpened'in f:assert not f['ecmOpened']
for key,name in [('finalAudit','nss150-final-audit.json'),('physicalRestore','nss150-physical-final.json'),('endpointClosure','nss150-endpoint-client-closure.json'),('receiverClosure','nss150-receiver-closure.json')]:
 assert x150[key]==json.loads((root/'evidence'/name).read_text())
assert rt150['audit']==x150['finalAudit'] and rt150['physicalRootRestoreAudit']==x150['physicalRestore'] and rt150['endpointClientClosureAudit']==x150['endpointClosure'] and rt150['ownedReceiverClosureAudit']==x150['receiverClosure']
assert all(rt150['audit'][k]for k in ['passed','readonly','originalFullLockedNativeAudit','unrelatedConfigurationMatches','exactWan4AutomaticFailoverProved','ecmStoppedAndZero','noActiveTransaction','noStaging','noExperimentState','noExperimentalModule'])
assert rt150['audit']['queryAge']<6 and rt150['audit']['selectors']==2 and not rt150['audit']['allFiveWanHealthy'] and not rt150['audit']['wan4Up']
assert all(rt150['physicalRootRestoreAudit'][k]for k in ['passed','readonly','physicalWanOriginalMqFourFqCodelRestored','lan4OriginalMqFourFqCodelRestored','defaultQueueOptionsAndHandlesExact'])
end150=rt150['endpointClientClosureAudit'];assert end150['passed'] and end150['readonly'] and end150['previousLoadsChecked']==end150['ownedUnitsInactiveMainPidZero']==16
assert end150['temporaryFirewallRulesRemaining']==end150['ownedClientOrGuardProcessesRemaining']==0 and end150['allCanonicalFirewallBaselinesMatch'] and end150['tcpAndUdpPortsClosed'] and end150['existingEndpointServicesUnchanged']
assert not end150['remoteWrites'] and not end150['productionWrites'] and not end150['desktopOperated']
assert rt150['ownedReceiverClosureAudit']['passed'] and rt150['ownedReceiverClosureAudit']['readonly'] and rt150['ownedReceiverClosureAudit']['exactOwnedReceiverAndTimeoutProcessesRemaining']==0
validation150=json.loads((root/'evidence/nss150-publication-validation-failure.json').read_text())
assert not validation150['passed'] and validation150['originalFailurePreserved'] and validation150['commitOrPushChainStoppedBeforeCommit'] and validation150['originalOperationalSourcesAndTrialEvidenceUnchanged'] and not validation150['hardwareTestRerun']
whitespace150=json.loads((root/'evidence/nss150-whitespace-failure.json').read_text())
assert not whitespace150['passed'] and whitespace150['originalFailurePreserved'] and whitespace150['commitOrPushChainStoppedBeforeCommit'] and not whitespace150['sourceBytesChanged'] and not whitespace150['hardwareTestRerun']
assert len(whitespace150['files'])==3
for f in whitespace150['files']:
 assert hashlib.sha256((root/f['path']).read_bytes()).hexdigest()==f['sha256']
 assert '/'+f['path']+' whitespace=cr-at-eol,'+f['attribute']in (root/'.gitattributes').read_text()
# NSS151/152: actual automatic class change and exact PC-controller crash recovery.
x152=json.loads((root/'evidence/nss152-mainline.json').read_text());rt152=json.loads((root/'evidence/nss152-runtime.json').read_text())
assert x152['round']==rt152['round']=='NSS152' and x152['passed']
for k in ['actualAutomaticClassTransitionAndRelearningPassed','actualControllerCrashIndependentRecoveryPassed','nightHeartbeatRemainsPaused']:assert x152[k] and rt152[k]
assert x152['actual151Bindings']==1678 and x152['actual152Bindings']==rt152['boundInputs']==1725
assert x152['qualified151Controller']=='work/nss151/run-v5.mjs' and x152['qualified152Controller']==rt152['qualifiedExperimentalController']=='work/nss152/crash-controller-v4.mjs'
assert x152['nativeFactoriesUnchanged']==[138,149] and x152['sourceNativeOwnerSeconds']==[6,27,100]
assert x152['clientHardSeconds']==180 and x152['execRawBundleRecordBytes']==[9000,65536,73728,1048576]
for k in ['matchedCpuComparison','realHumanGameAcceptance','highLoad300MbpsAcceptance','permanentNssControllerInstalled','nssPermanentlyEnabled','desktopOperated','steamOrCs2Started']:assert not x152[k]
assert x152['cpuReductionConclusion'] is None and rt152['cpuConclusion'] is None and not rt152['nssPermanentlyEnabled'] and not rt152['permanentNssControllerInstalled']
assert rt152['classifierDeployment']=='NSS68' and rt152['classifierConfigSha256']==rt150['classifierConfigSha256']
assert rt152['workerPid']==31657 and rt152['guardianPid']==17139
assert x152['old150RuntimeRetainedSha256']==rt152['historical150RuntimePreservedSha256']==hashlib.sha256((root/'evidence/nss150-runtime.json').read_bytes()).hexdigest()
proof152=json.loads((root/'evidence/nss152-source-proof.json').read_text())
assert proof152['passed'] and proof152['historicPrefixSources']==2148 and proof152['sources']==x152['exportedSources']==127 and len(manifest['sources'])>=2275
assert proof152['historicPrefixCanonicalSha256']==hashlib.sha256(json.dumps(manifest['sources'][:2148],sort_keys=True,separators=(',',':')).encode()).hexdigest()
for k in ['historicManifestPrefixUnchanged','privateCapabilityInputContentsExcluded','originalFailureSourcesKept','permanentClassifierAndKernelGateUnchanged']:assert proof152[k]
assert proof152['privateCapabilityInputsBoundLocally']==3 and proof152['actual151Bindings']==1678 and proof152['actual152Bindings']==1725
for source,digest in proof152['sourceHashes'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==digest
cp152=json.loads((root/'evidence/nss152-class-transition.json').read_text());assert cp152==x152['classTransition'] and cp152['passed']
assert cp152['tcpClassBefore']=='BULK' and cp152['tcpClassAfter']=='BE' and cp152['reason']=='cooldown'
for k in ['realApplicationPause','originalTcpSocketAndCtStayedPresent','sameQueryCompleteActualClassEvidence','onlyTcpAffected','projectionAbsenceNotTreatedAsCtExit','learningStoppedBeforeTcpCloseAndDrain','targetTcpCiAbsentIndependentlyVerified','originalUdpCiAndRtDualTagsPreserved','cpuBarrierNotFirmwareAck','noTagChangeBeforeWithdrawal','oldEpochClosedAndFullyRestored','newQueryCheckpointOwnerPinAndBothCis','sameSocketCtMarkNatWanInSuccessor','oldTerminalGateNeverReopened']:assert cp152[k]
assert cp152['nativeBudgetsUnchanged']==[6,27,100]
cr152=json.loads((root/'evidence/nss152-controller-crash.json').read_text());assert cr152==x152['controllerCrash'] and cr152['passed']
for k in ['originalControllerKilledDuringEcm2','exactFlowMarkNatWanAndDualTagsAtCrash','routerGuardianIndependentOfController','automatic20SecondEpochFinishedWithoutPcController','restoredWithoutManualRouterUndo','noRouterGuardianOrServiceKilled','physicalRootsTagsModulesRoutingRestored','normalHostControllerReceiptAbsent','controllerIsExperimentalPcController','permanentClassifierNotKilled','routerServiceNotKilled','noManualRouterRollbackDuringRecovery']:assert cr152[k]
assert cr152['nativeRenewalsWithoutPcController']==6 and not cr152['matchedCpuComparison'] and not cr152['cs2Acceptance'] and not cr152['permanentNssDeployment']
tr152=json.loads((root/'evidence/nss152-trials.json').read_text());assert tr152==x152['trials'] and len(tr152)==3
assert [t['test']for t in tr152]==['real-class-transition','automatic-successor','controller-crash-independent-recovery']
assert [t['wan']for t in tr152]==[5,5,1] and [t['sourceBindingsActual']for t in tr152]==[1678,1678,1725]
for i,t in enumerate(tr152):
 assert t['passed'] and t['actualTagsAndFqCodelLeaves']==4 and t['payloadBytesActual']<=73728 and t['guardianExecBytesActual']<=9000
 assert t['observedEcmSequence']==([0,2,1,0]if i==0 else[0,2,0]) and (t['nativeHardSeconds'],t['ownerMaxSeconds'],t['successGraceSeconds'])==(27,100,5)
 for k in ['fullMarkNatWanAffinityCorrect','checkpointDownloadedShaGzipVerified','independentRollbackBeforeFirstWrite','detachedParentPidOne','unchangedQoS','firmwareZeroAndAllOriginalStateRestored']:assert t[k]
 assert all(t['undo'].values())
 if i:
  m=t['metric'];assert m['direction']=='upload' and m['tcpMetric']=='server-confirmed received bytes' and 20<=m['seconds']<=21.5 and t['nativeRenewals']==m['nativeRenewals']==6
  assert m['selectedWan']==t['wan'] and m['causalCpuReductionPercent'] is None and not m['sameLoadSoftwareNssSoftwareComparison'] and not m['cs2Acceptance'] and not m['permanentController'] and not m['highLoad300Mbps']
  assert 0<m['serverConfirmedTcpUploadMbps']<35 and m['udp']['received']<=m['udp']['sent'] and not m['udp']['cs2Metric']
  assert all(v['packets']>0 for d in m['nssLeavesNearbyAsynchronousSnapshots'].values()for v in d.values())
 else:assert t['metric'] is None
fail152=json.loads((root/'evidence/nss152-failures.json').read_text());assert len(fail152)==x152['failuresPreserved']==10 and all(not f['passed'] and f['originalPreserved']for f in fail152)
assert fail152[-1]['normalChildEpochSucceeded'] and not fail152[-1]['controllerKilled'] and not fail152[-1]['beforeProductionStage']
for field,file,rtfield in [('finalAudit','final-audit','audit'),('physicalRestore','physical-final','physicalRootRestoreAudit'),('endpointClosure','endpoint-client-closure','endpointClientClosureAudit'),('receiverClosure','receiver-closure','ownedReceiverClosureAudit'),('downloadReceiverClosure','download-receiver-closure','ownedDownloadReceiverClosureAudit')]:assert x152[field]==json.loads((root/f'evidence/nss152-{file}.json').read_text())==rt152[rtfield]
assert rt152['audit']['queryAge']<6 and rt152['audit']['nativeDynamicSelectorsVerifiedByOriginalOwnershipAudit'] and not rt152['audit']['wan4Up']
for k in ['passed','originalFullLockedNativeAudit','unrelatedConfigurationMatches','exactWan4AutomaticFailoverProved','ecmStoppedAndZero','noActiveTransaction','noStaging','noExperimentState','noExperimentalModule']:assert rt152['audit'][k]
assert rt152['physicalRootRestoreAudit']['physicalWanOriginalMqFourFqCodelRestored'] and rt152['physicalRootRestoreAudit']['lan4OriginalMqFourFqCodelRestored'] and rt152['physicalRootRestoreAudit']['defaultQueueOptionsAndHandlesExact']
end152=rt152['endpointClientClosureAudit'];assert end152['passed'] and end152['previousLoadsChecked']==end152['ownedUnitsInactiveMainPidZero']==20
assert end152['temporaryFirewallRulesRemaining']==end152['ownedClientOrGuardProcessesRemaining']==0 and end152['tcpAndUdpPortsClosed'] and end152['allCanonicalFirewallBaselinesMatch'] and not end152['remoteWrites'] and not end152['productionWrites']
for k in ['ownedReceiverClosureAudit','ownedDownloadReceiverClosureAudit']:assert rt152[k]['passed'] and rt152[k]['readonly'] and rt152[k]['exactOwnedReceiverAndTimeoutProcessesRemaining']==0
visibility152=json.loads((root/'evidence/nss152-repository-visibility.json').read_text())
assert visibility152==x152['repositoryVisibility'] and visibility152['passed'] and x152['repositoryPrivateVisibilityRestored']
assert visibility152['repository']=='ZyPulse-zy/athena-nss-mainline' and visibility152['beforeVisibility']=='public' and visibility152['afterVisibility']=='private'
for k in ['authenticatedOwnerVerified','adminVerified','restoredRequestedPrivateVisibility','zeroStarsForksAndPagesBeforeChange','onlyPrivateFieldPatched','otherCheckedSettingsUnchanged']:assert visibility152[k]
assert not visibility152['credentialsSavedOrPrinted']
# NSS153: one actual child-controller crash, independent completion, then a
# fresh automatic successor on the original pair. Parent supervisor stayed up.
x153=json.loads((root/'evidence/nss153-mainline.json').read_text());rt153=json.loads((root/'evidence/nss153-runtime.json').read_text())
assert x153['passed'] and x153['round']==rt153['round']=='NSS153'
assert x153['boundInputs']==rt153['boundInputs']==1752 and x153['completedEpochs']==rt153['completedEpochs']==2
for k in ['actualChildControllerCrashThenAutomaticRelearning','sameSocketCtMarkNatWanInSuccessor','newQueryCheckpointOwnerKernelPinAndBothCis','oldTerminalGateNeverReopened','controllerActuallyTerminatedDuringEcm2','routerGuardianNotKilled','parentSupervisorStayedAlive','nightHeartbeatRemainsPaused','repositoryVisibilityCorrectedToUserRequestedPublic']:assert x153[k]
for k in ['routerRebootOrParentSupervisorCrashTested','matchedCpuComparison','realHumanGameAcceptance','highLoad300MbpsAcceptance','permanentNssControllerInstalled','nssPermanentlyEnabled','desktopOperated','steamOrCs2Started']:assert not x153[k]
assert x153['qualifiedController']==rt153['qualifiedExperimentalController']=='work/nss153/supervisor.mjs'
assert x153['nativeFactoryUnchanged']==149 and x153['sourceNativeOwnerSeconds']==[6,27,100] and x153['clientHardSeconds']==180 and x153['execRawBundleRecordBytes']==[9000,65536,73728,1048576]
assert x153['cpuReductionConclusion'] is None and rt153['cpuConclusion'] is None
assert x153['old152RuntimeRetainedSha256']==rt153['historical152RuntimePreservedSha256']==hashlib.sha256((root/'evidence/nss152-runtime.json').read_bytes()).hexdigest()
assert rt153['classifierDeployment']=='NSS68' and rt153['classifierConfigSha256']==rt152['classifierConfigSha256'] and rt153['workerPid']==31657 and rt153['guardianPid']==17139
proof153=json.loads((root/'evidence/nss153-source-proof.json').read_text())
assert proof153['passed'] and proof153['historicPrefixSources']==2275 and proof153['sources']==x153['exportedSources']==42 and len(manifest['sources'])>=2317
assert proof153['historicPrefixCanonicalSha256']==hashlib.sha256(json.dumps(manifest['sources'][:2275],sort_keys=True,separators=(',',':')).encode()).hexdigest()
for k in ['historicManifestPrefixUnchanged','privateCapabilityInputContentsExcluded','originalRefusalSourcesKept','permanentClassifierAndKernelGateUnchanged']:assert proof153[k]
assert proof153['actualBindings']==1752 and proof153['privateCapabilityInputsBoundLocally']==3 and proof153['nativeFactoryUnchanged']==149
for source,digest in proof153['sourceHashes'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==digest
q153=json.loads((root/'evidence/nss153-qualification.json').read_text())
assert q153['passed'] and q153['inheritedBindings']==1725 and len(q153['sourceManifest'])==27 and q153['finiteCrashSuccessor'] and not q153['productionExecution'] and q153['nativeFactoryUnchanged']==149
assert q153['budgets']==[6,27,100,180,9000,65536,73728]
pc153=q153['policyChecks'];assert pc153['passed'] and pc153['newParentPolicyRefusals']==14 and pc153['historicalNativeRecordWithExplicitModelTerminationAccepted']==1
assert pc153['legacyMissingTerminationRefused'] and pc153['terminationProvenancePartlyModelOnly'] and pc153['normalHostReceiptNotInvented'] and not pc153['newHardwareExecution'] and not pc153['completeIntegratedFactoryModelExecuted']
for source,digest in q153['sourceManifest'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==digest
auto153=json.loads((root/'evidence/nss153-automatic-result.json').read_text());assert auto153['passed'] and auto153['completedEpochs']==2
for k in ['controllerActuallyKilled','routerGuardianCompletedWithoutPcController','automaticSuccessorAfterVerifiedRestoration','newQueryCheckpointOwnerPinAndBothCis','sameSocketCtMarkNatWan','oldTerminalGateNeverReopened','finiteTwoEpochBudgetKept']:assert auto153[k]
assert not auto153['matchedCpuComparison'] and not auto153['cs2Acceptance'] and not auto153['permanentNssDeployment']
tr153=json.loads((root/'evidence/nss153-trials.json').read_text());assert tr153==x153['trials'] and len(tr153)==2
assert [t['generation']for t in tr153]==[1,2] and [t['wan']for t in tr153]==[3,3] and [t['hostNormalCompletionReceiptPresent']for t in tr153]==[False,True]
for t in tr153:
 assert t['passed'] and t['observedEcmSequence']==[0,2,0] and t['fourTagsFourFqCodelLeaves'] and t['completeClassCtMarkNatWanAffinityCorrect'] and t['sourceBindingsActual']==1752
 assert t['payloadBytesActual']<=73728 and t['guardianExecBytesActual']<=9000 and t['nativeHardSeconds']==27 and t['ownerMaxSeconds']==100 and t['nativeRenewals']==7
 assert t['checkpointDownloadedShaGzipVerified'] and t['rollbackBeforeFirstWrite'] and t['detachedParentPidOne'] and t['fullyRestored'] and all(t['undo'].values())
 m=t['metric'];assert m['direction']=='upload' and m['tcpMetric']=='server-confirmed received bytes' and 20<=m['seconds']<=21.5 and 0<m['serverConfirmedTcpUploadMbps']<35
 assert m['causalCpuReductionPercent'] is None and not m['sameLoadSoftwareNssSoftwareComparison'] and not m['cs2Acceptance'] and not m['permanentController'] and not m['highLoad300Mbps']
 assert m['selectedWan']==3 and m['nativeRenewals']==7 and m['udp']['received']<=m['udp']['sent'] and not m['udp']['cs2Metric']
 assert all(v['packets']>0 for d in m['nssLeavesNearbyAsynchronousSnapshots'].values()for v in d.values())
fail153=json.loads((root/'evidence/nss153-failures.json').read_text());assert len(fail153)==x153['failuresPreserved']==4 and all(not f['passed']and f['originalPreserved']and f['beforeConnectionAndProductionWrites']for f in fail153)
for field,file,rtfield in [('finalAudit','final-audit','audit'),('physicalRestore','physical-final','physicalRootRestoreAudit'),('endpointClosure','endpoint-client-closure','endpointClientClosureAudit'),('receiverClosure','receiver-closure','ownedReceiverClosureAudit'),('downloadReceiverClosure','download-receiver-closure','ownedDownloadReceiverClosureAudit')]:assert x153[field]==json.loads((root/f'evidence/nss153-{file}.json').read_text())==rt153[rtfield]
for k in ['passed','originalFullLockedNativeAudit','unrelatedConfigurationMatches','exactWan4AutomaticFailoverProved','ecmStoppedAndZero','noActiveTransaction','noStaging','noExperimentState','noExperimentalModule']:assert rt153['audit'][k]
assert rt153['audit']['queryAge']<6 and rt153['audit']['nativeDynamicSelectorsVerifiedByOriginalOwnershipAudit'] and not rt153['audit']['wan4Up']
assert rt153['physicalRootRestoreAudit']['physicalWanOriginalMqFourFqCodelRestored'] and rt153['physicalRootRestoreAudit']['lan4OriginalMqFourFqCodelRestored'] and rt153['physicalRootRestoreAudit']['defaultQueueOptionsAndHandlesExact']
end153=rt153['endpointClientClosureAudit'];assert end153['passed'] and end153['previousLoadsChecked']==end153['ownedUnitsInactiveMainPidZero']==21 and end153['temporaryFirewallRulesRemaining']==end153['ownedClientOrGuardProcessesRemaining']==0
assert end153['tcpAndUdpPortsClosed'] and end153['allCanonicalFirewallBaselinesMatch'] and not end153['remoteWrites'] and not end153['productionWrites']
for k in ['ownedReceiverClosureAudit','ownedDownloadReceiverClosureAudit']:assert rt153[k]['passed'] and rt153[k]['readonly'] and rt153[k]['exactOwnedReceiverAndTimeoutProcessesRemaining']==0
visibility153=json.loads((root/'evidence/nss153-repository-visibility-correction.json').read_text())
assert visibility153['passed'] and visibility153['repository']=='ZyPulse-zy/athena-nss-mainline' and visibility153['beforeVisibility']=='private' and visibility153['afterVisibility']==rt153['repositoryVisibility']=='public'
for k in ['authenticatedOwnerVerified','adminVerified','correctedNss152VisibilityMistake','userPublicInstructionFromOtherChatVerified','onlyPrivateFieldPatched','otherCheckedSettingsUnchanged','historicalNss152ReceiptPreserved']:assert visibility153[k]
assert not visibility153['credentialsSavedOrPrinted']
# NSS154: direct finite supervisor terminated, reconstructed from disk journal.
x154=json.loads((root/'evidence/nss154-mainline.json').read_text());rt154=json.loads((root/'evidence/nss154-runtime.json').read_text())
assert x154['passed'] and x154['round']==rt154['round']=='NSS154'
assert x154['boundInputs']==rt154['boundInputs']==1795 and x154['completedEpochs']==rt154['completedEpochs']==2
for k in ['actualSupervisorItselfCrashAndRestart','newSupervisorReconstructedFromDiskJournal','sameSocketCtMarkNatWanInSuccessor','newQueryCheckpointOwnerKernelPinAndBothCis','oldTerminalGateNeverReopened','supervisorActuallyTerminatedDuringEcm2','routerGuardianNotKilled']:assert x154[k]
for k in ['separateHostEpochChildUsed','routerRebootTested','matchedCpuComparison','realHumanGameAcceptance','highLoad300MbpsAcceptance','permanentNssControllerInstalled','nssPermanentlyEnabled','desktopOperated','steamOrCs2Started']:assert not x154[k]
assert x154['qualifiedController']==rt154['qualifiedExperimentalController']=='work/nss154/pilot-supervisor-v3.mjs'
assert x154['nativeFactoryUnchanged']==149 and x154['sourceNativeOwnerSeconds']==[6,27,100] and x154['clientHardSeconds']==180 and x154['execRawBundleRecordBytes']==[9000,65536,73728,1048576]
assert x154['cpuReductionConclusion'] is None and rt154['cpuConclusion'] is None
assert x154['dayHeartbeatActiveUntilBeijing']==rt154['dayHeartbeatActiveUntilBeijing']=='2026-10-06T20:00:00+08:00'
assert x154['repositoryVisibility']==rt154['repositoryVisibility']=='public'
assert x154['old153RuntimeRetainedSha256']==rt154['historical153RuntimePreservedSha256']==hashlib.sha256((root/'evidence/nss153-runtime.json').read_bytes()).hexdigest()
assert rt154['classifierDeployment']=='NSS68' and rt154['classifierConfigSha256']==rt153['classifierConfigSha256'] and rt154['guardianPid']==rt153['guardianPid']
proof154=json.loads((root/'evidence/nss154-source-proof.json').read_text())
assert proof154['passed'] and proof154['historicPrefixSources']==2317 and proof154['sources']==x154['exportedSources']==54 and len(manifest['sources'])>=2371
assert proof154['historicPrefixCanonicalSha256']==hashlib.sha256(json.dumps(manifest['sources'][:2317],sort_keys=True,separators=(',',':')).encode()).hexdigest()
for k in ['historicManifestPrefixUnchanged','privateCapabilityInputContentsExcluded','originalRefusalSourcesKept','permanentClassifierAndKernelGateUnchanged']:assert proof154[k]
assert proof154['actualBindings']==1795 and proof154['privateCapabilityInputsBoundLocally']==3 and proof154['nativeFactoryUnchanged']==149
for source,digest in proof154['sourceHashes'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==digest
q154=json.loads((root/'evidence/nss154-qualification.json').read_text());assert q154['passed'] and q154['actualBindings']==1795 and len(q154['versions'])==3
assert [q['inheritedBindings'] for q in q154['versions']]==[1752,1778,1787] and [len(q['sourceManifest']) for q in q154['versions']]==[26,9,8]
for q in q154['versions']:
 assert q['passed'] and not q['productionExecution'] and q['nativeFactoryUnchanged']==149 and q['budgets']==[6,27,100,180,9000,65536,73728]
 for source,digest in q['sourceManifest'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==digest
models154=q154['versions'][0]['journalModels'];assert models154['passed'] and models154['acceptedSchemaModels']==2 and models154['rejectedMalformedJournalModels']==15 and not models154['hardwareExecution'] and not models154['fullFactoryModelExecuted']
assert q154['versions'][2]['exactHistoricalDependencyRestored'] and q154['versions'][2]['literalAndRelativeDependenciesPresent']
a154=json.loads((root/'evidence/nss154-automatic-result.json').read_text());assert a154['passed'] and a154['completedEpochs']==2
for k in ['supervisorItselfActuallyKilled','newSupervisorProcessFromDiskJournal','oldSupervisorAbsenceVerified','independentNativeRecoveryBeforeSuccessor','newQueryCheckpointOwnerKernelPinBothCis','sameSocketCtMarkNatWan','noOldGateReopenOrLeaseExtension','externalHarnessOnlyLoadKillRestart']:assert a154[k]
assert not a154['matchedCpuComparison'] and not a154['cs2Acceptance'] and not a154['permanentNssDeployment']
tr154=json.loads((root/'evidence/nss154-trials.json').read_text());assert tr154==x154['trials'] and len(tr154)==2
assert [t['generation'] for t in tr154]==[1,2] and tr154[0]['wan']==tr154[1]['wan'] and tr154[0]['wan'] in [1,2,3,5] and [t['hostNormalCompletionReceiptPresent'] for t in tr154]==[False,True]
for t in tr154:
 assert t['passed'] and t['observedEcmSequence']==[0,2,0] and t['fourTagsFourFqCodelLeaves'] and t['completeClassCtMarkNatWanAffinityCorrect'] and t['sourceBindingsActual']==1795
 assert t['payloadBytesActual']<=73728 and t['guardianExecBytesActual']<=9000 and t['nativeHardSeconds']==27 and t['ownerMaxSeconds']==100 and t['nativeRenewals']>0
 assert t['checkpointDownloadedShaGzipVerified'] and t['rollbackBeforeFirstWrite'] and t['detachedParentPidOne'] and t['fullyRestored'] and all(t['undo'].values())
 m=t['metric'];assert m['direction']=='upload' and m['tcpMetric']=='server-confirmed received bytes' and 20<=m['seconds']<=21.5 and 0<m['serverConfirmedTcpUploadMbps']<35
 assert m['causalCpuReductionPercent'] is None and not m['sameLoadSoftwareNssSoftwareComparison'] and not m['cs2Acceptance'] and not m['permanentController'] and not m['highLoad300Mbps']
 assert m['selectedWan']==t['wan'] and m['nativeRenewals']==t['nativeRenewals'] and m['udp']['received']<=m['udp']['sent'] and not m['udp']['cs2Metric']
 assert all(v['packets']>0 for d in m['nssLeavesNearbyAsynchronousSnapshots'].values() for v in d.values())
fail154=json.loads((root/'evidence/nss154-failures.json').read_text());assert len(fail154)==x154['failuresPreserved']==2
assert all(not f['passed'] and f['originalPreserved'] and f['beforeCheckpointAndNssStage'] and not f['supervisorActuallyKilled'] and not f['nssOrFirmwareFailure'] for f in fail154)
for field,file,rtfield in [('finalAudit','final-audit','audit'),('physicalRestore','physical-final','physicalRootRestoreAudit'),('endpointClosure','endpoint-client-closure','endpointClientClosureAudit'),('receiverClosure','receiver-closure','ownedReceiverClosureAudit'),('downloadReceiverClosure','download-receiver-closure','ownedDownloadReceiverClosureAudit')]:assert x154[field]==json.loads((root/f'evidence/nss154-{file}.json').read_text())==rt154[rtfield]
for k in ['passed','originalFullLockedNativeAudit','unrelatedConfigurationMatches','exactWan4AutomaticFailoverProved','ecmStoppedAndZero','noActiveTransaction','noStaging','noExperimentState','noExperimentalModule']:assert rt154['audit'][k]
assert rt154['audit']['queryAge']<6 and rt154['audit']['nativeDynamicSelectorsVerifiedByOriginalOwnershipAudit'] and not rt154['audit']['wan4Up']
assert rt154['physicalRootRestoreAudit']['physicalWanOriginalMqFourFqCodelRestored'] and rt154['physicalRootRestoreAudit']['lan4OriginalMqFourFqCodelRestored'] and rt154['physicalRootRestoreAudit']['defaultQueueOptionsAndHandlesExact']
end154=rt154['endpointClientClosureAudit'];assert end154['passed'] and end154['previousLoadsChecked']==end154['ownedUnitsInactiveMainPidZero']==24 and end154['temporaryFirewallRulesRemaining']==end154['ownedClientOrGuardProcessesRemaining']==0
assert end154['tcpAndUdpPortsClosed'] and end154['allCanonicalFirewallBaselinesMatch'] and not end154['remoteWrites'] and not end154['productionWrites']
for k in ['ownedReceiverClosureAudit','ownedDownloadReceiverClosureAudit']:assert rt154[k]['passed'] and rt154[k]['readonly'] and rt154[k]['exactOwnedReceiverAndTimeoutProcessesRemaining']==0

# NSS155 proves whole-pair flow exit only; all successor failures preserved.
x155=json.loads((root/'evidence/nss155-mainline.json').read_text());rt155=json.loads((root/'evidence/nss155-runtime.json').read_text())
assert x155['passed'] and x155['round']==rt155['round']=='NSS155' and x155['status']=='FLOW_EXIT_PASSED_NEW_TCP_SUCCESSOR_PENDING'
assert x155['boundInputs']==rt155['boundInputs']==1836 and x155['flowExitCasesPassed']==rt155['flowExitCasesPassed']==2
assert x155['completed20SecondSuccessorEpochs']==rt155['completed20SecondSuccessorEpochs']==0
assert x155['actualOldPairExitAndRestoration'] and x155['wholePairWithdrawal'] and x155['classifierKernelGateAndQoSUnchanged']
for k in ['newTcpSuccessorPassed','exactSingleCiRetirementClaimed','ctExitInferredFromProjection','native149FullFactoryUnchanged','matchedCpuComparison','realHumanGameAcceptance','highLoad300MbpsAcceptance','permanentNssControllerInstalled','nssPermanentlyEnabled','desktopOperated','steamOrCs2Started']:assert not x155[k]
assert x155['qualifiedController']==rt155['qualifiedExperimentalController']=='work/nss155/pilot-supervisor-v3.mjs'
assert x155['sourceNativeOwnerSeconds']==[6,27,100] and x155['clientHardSeconds']==180 and x155['execRawBundleRecordBytes']==[9000,65536,73728,1048576] and x155['originalEightCandidateTcpPortBudget']==8
assert x155['cpuReductionConclusion'] is None and rt155['cpuConclusion'] is None
assert x155['repositoryVisibility']==rt155['repositoryVisibility']=='public' and not rt155['newTcpSuccessorPassed']
assert x155['old154RuntimeRetainedSha256']==rt155['historical154RuntimePreservedSha256']==hashlib.sha256((root/'evidence/nss154-runtime.json').read_bytes()).hexdigest()
assert rt155['classifierDeployment']=='NSS68' and rt155['classifierConfigSha256']==rt154['classifierConfigSha256'] and rt155['guardianPid']==rt154['guardianPid']
q155=json.loads((root/'evidence/nss155-qualification.json').read_text());assert q155['passed'] and q155['wholePairExitOnly'] and q155['actualBindings']==1836 and len(q155['versions'])==3
assert [q['inheritedBindings'] for q in q155['versions']]==[1795,1825,1831] and [len(q['sourceManifest']) for q in q155['versions']]==[30,6,5]
for q in q155['versions']:
 assert q['passed'] and not q['productionExecution']
 for source,digest in q['sourceManifest'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==digest
assert q155['versions'][0]['wholePairTerminalOnly'] and not q155['versions'][0]['fullFactoryRamModel']
assert q155['versions'][2]['originalEightPortBudgetUnchanged'] and q155['versions'][2]['reservedSuccessorCandidateCheckedBeforeStaging']
proof155=json.loads((root/'evidence/nss155-source-proof.json').read_text());assert proof155['passed'] and proof155['historicPrefixSources']==2371 and proof155['actualBindings']==1836 and proof155['actualFlowExitBindings']==[1831,1836]
assert proof155['sources']==x155['exportedSources'] and len(manifest['sources'])>=2371+proof155['sources']
assert proof155['historicPrefixCanonicalSha256']==hashlib.sha256(json.dumps(manifest['sources'][:2371],sort_keys=True,separators=(',',':')).encode()).hexdigest()
for k in ['historicManifestPrefixUnchanged','privateCapabilityInputContentsExcluded','originalRefusalSourcesKept','classifierKernelGateAndQoSUnchanged']:assert proof155[k]
assert proof155['newNativeWholePairTerminalBranch']==155 and not proof155['fullFactoryRamModelExecuted']
for source,digest in proof155['sourceHashes'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==digest
t155=json.loads((root/'evidence/nss155-trials.json').read_text());assert len(t155)==2 and [t['boundInputs'] for t in t155]==[1831,1836] and [t['wan'] for t in t155]==[5,2]
for t in t155:
 assert t['passed'] and t['controlledTcpActuallyClosed'] and t['udpApplicationContinued'] and t['wholePairFirmwareZero'] and t['fullOriginalRestore']
 assert not t['newConnectionLearned'] and not t['ctExitInferredFromProjection'] and not t['exactSingleCiRetirementClaimed']
 assert t['originalPreCloseCtMarkNatWanFourTagsCorrect'] and t['checkpointDownloadedShaGzipVerified'] and t['independentPpidOneRollbackVerifiedBeforeWrite']
 assert t['payloadBytes']<=73728 and t['guardianExecBytes']<=9000 and t['nativeHardSeconds']==27 and t['ownerMaxSeconds']==100 and all(t['undo'].values())
 assert not t['performanceComparison'] and t['cpuReductionConclusion'] is None and not t['cs2Acceptance'] and t['udpRepliesAfterClientClose']>10
f155=json.loads((root/'evidence/nss155-failures.json').read_text());assert len(f155)==5 and x155['failuresPreserved']==5
assert f155[4]['commitAndPushIncorrectlyContinuedAfterFailedCheck'] and f155[4]['workflowErrorAcknowledged'] and not f155[4]['frozenSourceEdited'] and not f155[4]['forcePushOrHistoryRewrite']
for t in f155[:3]:assert not t['overallSuccessorPassed'] and not t['successorNssStageOccurred'] and t['originalFailureAndSourcesPreserved']
assert not f155[0]['routerNssStageOccurred'] and f155[1]['oldFlowExitPassed'] and f155[2]['oldFlowExitPassed']
assert f155[3]['correctedOnlyOutputNamespace'] and not f155[3]['previousEvidenceOverwritten'] and f155[3]['publicationStoppedUntilChecksPassed']
d155=json.loads((root/'evidence/nss155-software-transport-diagnostics.json').read_text());assert len(d155)==2 and [d['offeredTcpMbps'] for d in d155]==[2.62144,32]
for d in d155:assert d['readonlyRouter'] and not d['productionConfigurationWrites'] and not d['nssEnabled'] and not d['rootCauseProven'] and len(d['twoSequentialConnections'])==2 and all(not x['errors'] and x['received']>0 for x in d['twoSequentialConnections'])
for k in ['passed','originalFullLockedNativeAudit','unrelatedConfigurationMatches','exactWan4AutomaticFailoverProved','ecmStoppedAndZero','noActiveTransaction','noStaging','noExperimentState','noExperimentalModule']:assert rt155['audit'][k]
assert rt155['audit']['queryAge']<6 and rt155['audit']['nativeDynamicSelectorsVerifiedByOriginalOwnershipAudit'] and not rt155['audit']['wan4Up']
assert rt155['physicalRootRestoreAudit']['physicalWanOriginalMqFourFqCodelRestored'] and rt155['physicalRootRestoreAudit']['lan4OriginalMqFourFqCodelRestored']
end155=rt155['endpointClientClosureAudit'];assert end155['passed'] and end155['previousLoadsChecked']==end155['ownedUnitsInactiveMainPidZero']==27 and end155['temporaryFirewallRulesRemaining']==end155['ownedClientOrGuardProcessesRemaining']==0
assert end155['tcpAndUdpPortsClosed'] and end155['allCanonicalFirewallBaselinesMatch']
for k in ['ownedReceiverClosureAudit','ownedDownloadReceiverClosureAudit']:assert rt155[k]['passed'] and rt155[k]['exactOwnedReceiverAndTimeoutProcessesRemaining']==0

# NSS156: actual owned TCP exit and new TCP/original UDP successor.
x156=json.loads((root/'evidence/nss156-mainline.json').read_text());rt156=json.loads((root/'evidence/nss156-runtime.json').read_text())
assert x156['passed'] and x156['round']==rt156['round']=='NSS156' and x156['status']=='OWNED_FLOW_EXIT_NEW_TCP_ORIGINAL_UDP_LIFECYCLE_PASSED'
assert x156['boundInputs']==rt156['boundInputs']==1909 and x156['completed20SecondSuccessorEpochs']==rt156['completed20SecondSuccessorEpochs']==1
for k in ['actualOldPairExitAndRestoration','newTcpSuccessorPassed','sameUdpSocketCtMarkNatWan','newQueryCheckpointOwnerPinsBothCis','oldGateNeverReopened','nssScopeOneTcpBulkOneUdpRt','otherOwnTcpSocketsClosedBeforeStage','nativeFullFactoryUnchangedFrom155','classSpecific151RetirementMustBeMergedBeforeDeployablePilot','classifierKernelGateAndQoSUnchanged','ownedSshKeepaliveOnlyChanged']:assert x156[k]
for k in ['matchedCpuComparison','realHumanGameAcceptance','highLoad300MbpsAcceptance','permanentNssControllerInstalled','nssPermanentlyEnabled','desktopOperated','steamOrCs2Started','ctExitInferredFromProjection','keepaliveTimeoutRootCauseProven','systemSshConfigurationChanged']:assert not x156[k]
assert x156['ecmSequence']==[0,2,0,2,0] and rt156['newTcpSuccessorPassed']
assert x156['qualifiedController']==rt156['qualifiedExperimentalController']=='work/nss156/pilot-supervisor-v7.mjs'
assert x156['nativeWholePairFactoryVersion']==155 and x156['sourceNativeOwnerSeconds']==[6,27,100] and x156['clientHardSeconds']==180 and x156['execRawBundleRecordBytes']==[9000,65536,73728,1048576]
assert x156['softwarePreparationProbeCount']==4 and x156['maximumTotalOwnedTcpPorts']==8 and x156['softwarePreparationTotalOfferedMbps']==32 and x156['globalMaximumPacerCreditBytes']==65536
assert x156['cpuReductionConclusion'] is None and rt156['cpuConclusion'] is None and x156['repositoryVisibility']==rt156['repositoryVisibility']=='public'
assert x156['old155RuntimeRetainedSha256']==rt156['historical155RuntimePreservedSha256']==hashlib.sha256((root/'evidence/nss155-runtime.json').read_bytes()).hexdigest()
assert rt156['classifierDeployment']=='NSS68' and rt156['classifierConfigSha256']==rt155['classifierConfigSha256'] and rt156['guardianPid']==rt155['guardianPid']
q156=json.loads((root/'evidence/nss156-qualification.json').read_text());assert q156['passed'] and q156['actualBindings']==1909 and len(q156['versions'])==7 and not q156['fullFactoryModelExecuted']
assert [q['inheritedBindings'] for q in q156['versions']]==[1836,1865,1874,1880,1885,1890,1898] and [len(q['sourceManifest']) for q in q156['versions']]==[29,9,6,5,5,8,11]
for q in q156['versions']:
 assert q['passed'] and not q['productionExecution']
 for source,digest in q['sourceManifest'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==digest
assert q156['versions'][0]['budgets']==[6,27,100,180,9000,65536,73728] and q156['versions'][0]['nonceAuthenticationAndCounterModels']['caseCount']==4
assert q156['versions'][1]['pendingPolicyModel']['caseCount']==8 and q156['versions'][1]['knownAuthenticatedFlowNeverRotatedByTimeout']
assert q156['versions'][4]['exactInputDirectoryCheckPassed'] and q156['versions'][5]['hardClientAndReceiverDeadlinesRetained'] and not q156['versions'][5]['systemSshConfigurationChanged']
assert q156['versions'][6]['softwareOnlyFourProbeCohort'] and q156['versions'][6]['cohortPolicyModel']['cases']==8 and q156['versions'][6]['otherOwnTcpSocketsClosedBeforeNss'] and not q156['versions'][6]['pbrMarkNatWanPolicyChanged']
proof156=json.loads((root/'evidence/nss156-source-proof.json').read_text());assert proof156['passed'] and proof156['historicPrefixSources']==2430 and proof156['actualBindings']==1909 and proof156['actualProductionEpochCount']==2
assert proof156['sources']==x156['exportedSources']==91 and len(manifest['sources'])>=2521
assert proof156['historicPrefixCanonicalSha256']==hashlib.sha256(json.dumps(manifest['sources'][:2430],sort_keys=True,separators=(',',':')).encode()).hexdigest()
for k in ['historicManifestPrefixUnchanged','allActualFullInputsAndFrozenCopiesVerified','privateInputContentsExcluded','nativeWholePairFactoryBytesSameAs155','classifierKernelGateAndQoSUnchanged']:assert proof156[k]
assert not proof156['fullNewFactoryModelExecuted']
for source,digest in proof156['sourceHashes'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==digest
t156=json.loads((root/'evidence/nss156-trials.json').read_text());assert t156==x156['trials'] and len(t156)==2 and [t['wan'] for t in t156]==[3,3]
assert [t['case'] for t in t156]==['old-pair-exit','new-tcp-original-udp'] and t156[0]['metrics'] is None
for t in t156:
 assert t['passed'] and t['ecmSequence']==[0,2,0] and t['boundInputs']==1909 and t['payloadBytes']<=73728 and t['guardianExecBytes']<=9000 and t['nativeHardSeconds']==27 and t['ownerMaxSeconds']==100
 assert t['checkpointDownloadedShaGzipVerified'] and t['independentPpidOneRollbackVerifiedBeforeWrite'] and t['ctMarkNatWanFourTagsCorrect'] and t['completeSameSourceClassMapping'] and all(t['allOriginalRestoreChecks'].values())
 assert not t['matchedCpuComparison'] and not t['realCs2Acceptance']
m156=t156[1]['metrics'];assert 20<=m156['seconds']<=21.5 and 0<m156['serverConfirmedTcpUploadMbps']<35 and m156['nativeRenewals']==7 and m156['selectedWan']==3
assert m156['causalCpuReductionPercent'] is None and not m156['sameLoadSoftwareNssSoftwareComparison'] and not m156['cs2Acceptance'] and not m156['permanentController'] and not m156['highLoad300Mbps']
assert m156['udp']['received']==m156['udp']['sent']==696 and not m156['udp']['cs2Metric'] and m156['timeSqueezeDelta']==m156['softnetDropDelta']==0
assert all(v['packets']>0 and v['dropped']==0 for d in m156['nssLeavesNearbyAsynchronousSnapshots'].values() for v in d.values())
f156=json.loads((root/'evidence/nss156-failures.json').read_text());assert len(f156)==x156['failuresPreserved']==9
for f in f156[:6]:assert not f['passed'] and not f['routerCheckpointOrNssStageStarted'] and f['originalErrorAndSourcesPreserved'] and not f['rootCauseOfNetworkTimeoutProven']
assert f156[6]['refusedBeforeRouterConnect'] and f156[6]['oldSourceRetained'] and f156[6]['correctedOnlyNamespace'] and f156[6]['analysisRanOnlyAfterRepair']
assert f156[7]['failedBeforeGitWorkspaceMutation'] and f156[7]['submissionChainStoppedBeforeCommit'] and f156[7]['originalSourcePreserved'] and f156[7]['onlyProofFileExtensionsCorrected']
assert f156[8]['submissionChainStoppedBeforeCommit'] and f156[8]['exactFieldNameOnlyCorrected'] and f156[8]['frozenSourcesAndHardwareEvidenceUnchanged']
d156=json.loads((root/'evidence/nss156-software-preparation.json').read_text());assert len(d156)==6 and all(d['noNssStage'] and d['causeNotProven'] for d in d156)
assert d156[-1]['seconds']>=80 and d156[-1]['serverConfirmedBytes']>260000000 and not d156[-1]['clientErrors']
for field,file,rtfield in [('finalAudit','final-audit','audit'),('physicalRestore','physical-final','physicalRootRestoreAudit'),('endpointClosure','endpoint-client-closure','endpointClientClosureAudit')]:assert x156[field]==json.loads((root/f'evidence/nss156-{file}.json').read_text())==rt156[rtfield]
for k in ['passed','originalFullLockedNativeAudit','unrelatedConfigurationMatches','exactWan4AutomaticFailoverProved','ecmStoppedAndZero','noActiveTransaction','noStaging','noExperimentState','noExperimentalModule']:assert rt156['audit'][k]
assert rt156['audit']['queryAge']<6 and rt156['audit']['nativeDynamicSelectorsVerifiedByOriginalOwnershipAudit'] and not rt156['audit']['wan4Up']
assert rt156['physicalRootRestoreAudit']['physicalWanOriginalMqFourFqCodelRestored'] and rt156['physicalRootRestoreAudit']['lan4OriginalMqFourFqCodelRestored'] and rt156['physicalRootRestoreAudit']['defaultQueueOptionsAndHandlesExact']
end156=rt156['endpointClientClosureAudit'];assert end156['passed'] and end156['previousLoadsChecked']==end156['ownedUnitsInactiveMainPidZero']==34 and end156['temporaryFirewallRulesRemaining']==end156['ownedClientOrGuardProcessesRemaining']==0
assert end156['tcpAndUdpPortsClosed'] and end156['allCanonicalFirewallBaselinesMatch'] and not end156['remoteWrites'] and not end156['productionWrites']
for k,file in [('ownedReceiverClosureAudit','receiver-closure'),('ownedDownloadReceiverClosureAudit','download-receiver-closure')]:assert rt156[k]==json.loads((root/f'evidence/nss156-{file}.json').read_text()) and rt156[k]['passed'] and rt156[k]['exactOwnedReceiverAndTimeoutProcessesRemaining']==0
assert manifest['lastAppendExport'] in ['NSS156','NSS158','NSS159','NSS160_V1_FROZEN','V11_BOUNDED_ENTRY','V13_TWO_WAN_NIGHT','V14_TWO_WAN_DURATION','V15_WAN_CLASS_QOS','V16_THREE_FLOW_MULTIWAN','V17_BUDGET_RT','V18_BORROW_RETIRED','V19_BORROW_PASS','V20_FIVE_QUEUE_MAP','V26_NORMAL_APP_ENTRY','V27_OWN_RAW_PREREQUISITE']

# NSS158: actual NSS157 precise class retirement + new NSS158 functional ABA.
load158=lambda n:json.loads((root/f'evidence/nss158-{n}.json').read_text())
x158=load158('mainline');rt158=json.loads((root/'evidence/nss158-runtime.json').read_text())
assert x158['passed'] and x158['round']==rt158['round']=='NSS158'
assert x158['status']=='INTEGRATED_CLASS_RETIRE_RELEARN_AND_FUNCTIONAL_ABA_PASSED_CPU_COMPARABILITY_FAILED'
for k in ['functionalTwentySecondABA','exactClassLifecycleIntegratedIntoNormalABA','classSpecificChangeEndsOldPairBeforeFreshEpoch','old156NewTcpSuccessorHistoricalPassed','nssScopeOneTcpBulkOneUdpRt','permanentClassifierKernelGateAndQoSUnchanged','pbrCtMarkNatWanAffinityUnchanged']:assert x158[k]
for k in ['newTcpSuccessorInLatestCombinedClosePilotsPassed','realHumanGameAcceptance','highLoad300MbpsAcceptance','permanentNssControllerInstalled','nssPermanentlyEnabled','desktopOperated','steamOrCs2Started','ctExitInferredFromProjection','cpuBarrierIsFirmwareAck','fullFactoryModelExecuted']:assert not x158[k]
assert x158['cpuReductionConclusion'] is None and rt158['cpuConclusion'] is None and not rt158['cpuComparabilityAccepted']
assert x158['boundInputs']==rt158['boundInputs']==2042 and x158['classPilotBoundInputs']==2020
assert x158['qualifiedExperimentalController']==rt158['qualifiedExperimentalController']=='work/nss158/pilot-supervisor.mjs'
assert x158['classController']=='work/nss157/pilot-supervisor-live.mjs'
assert x158['sourceNativeOwnerClientSeconds']==[6,27,100,180] and x158['execRawBundleRecordBytes']==[9000,65536,73728,1048576]
assert x158['softwareMaximumTcpPorts']==8 and x158['softwareTotalOfferedMbps']==32 and x158['globalPacerCreditBytes']==65536
assert x158['repositoryVisibility']==rt158['repositoryVisibility']=='public'
assert x158['old156RuntimeRetainedSha256']==rt158['historical156RuntimePreservedSha256']==hashlib.sha256((root/'evidence/nss156-runtime.json').read_bytes()).hexdigest()
assert rt158['classifierDeployment']=='NSS68' and rt158['classifierConfigSha256']==rt156['classifierConfigSha256'] and rt158['guardianPid']==rt156['guardianPid']
ct158=load158('class-lifecycle');assert ct158==x158['classPilot157'] and ct158['passed'] and ct158['wan']==3 and ct158['ecmSequence']==[0,2,1,0,2,0]
assert ct158['actualClassesAfterPause']=={'tcp':'BE','udp':'RT'} and ct158['affectedSlots']==['tcp']
for k in ['sameSingleCompleteQueryEvidence','targetTcpCiAbsentAndOriginalUdpCiTagsRetained','oldPairRestoredBeforeNewEpoch','sameTcpSocketCtAndOriginalUdp','freshQueryCheckpointOwnerPinsBothCis','oldGateNotReopened','exactRetirementAndNewEpochBothPassed']:assert ct158[k]
assert ct158['completeReadCount']==2 and 0<ct158['completeWaitSeconds']<.65 and not ct158['matchedCpuComparison'] and not ct158['cs2Acceptance']
cm158=ct158['metrics'];assert 20<=cm158['seconds']<=21.5 and cm158['udp']['sent']==cm158['udp']['received']==771
assert cm158['timeSqueezeDelta']==cm158['softnetDropDelta']==0 and cm158['causalCpuReductionPercent'] is None
assert all(v['packets']>0 and v['dropped']==0 for d in cm158['nssLeavesNearbyAsynchronousSnapshots'].values() for v in d.values())
m158=load158('aba-metrics');cmp158=load158('aba-comparison');assert m158==x158['abaMetrics'] and cmp158==x158['abaComparison']
assert m158['passed'] and m158['oneWan']==x158['abaSelectedWan']==5 and [p['acceleratedCounts'] for p in m158['phases']]==[[0],[2],[0]]
assert [p['phase'] for p in m158['phases']]==['A','B','A2'] and all(p['sampleCount']==41 and 20<=p['whole']['seconds']<=21.5 for p in m158['phases'])
assert [(p['whole']['udp']['sent'],p['whole']['udp']['received']) for p in m158['phases']]==[(855,855),(861,861),(824,824)]
assert all(p['whole']['timeSqueezeDelta']==p['whole']['softnetDropDelta']==0 for p in m158['phases'])
assert [p['whole']['interfaces']['wan']['rxDroppedDelta'] for p in m158['phases']]==[1,0,1]
assert cmp158['passed'] and not cmp158['comparabilityAccepted'] and len(cmp158['checks'])==7 and sum(cmp158['checks'].values())==5
assert not cmp158['checks']['unselected_wan_total_below_0_5Mbps_each'] and not cmp158['checks']['unselected_wan_total_range_below_0_25Mbps']
assert cmp158['softirqRelativeReductionPercent'] is None and not cmp158['humanCs2Acceptance'] and not cmp158['highLoad300MbpsAcceptance'] and not cmp158['productionNssRetained']
assert cmp158['serverConfirmedMbps']==[p['whole']['clientTcpMbps'] for p in m158['phases']]
assert cmp158['nssSoftirqPercent']==m158['phases'][1]['whole']['softirqPercent']
assert max(cmp158['unselectedWanTotalRxPlusTxMbps'])>.5 and max(cmp158['unselectedWanTotalRxPlusTxMbps'])-min(cmp158['unselectedWanTotalRxPlusTxMbps'])>.25
q158=load158('qualification');assert q158['passed'] and len(q158['classVersions'])==9 and not q158['fullFactoryModelExecuted']
for q in q158['classVersions']+[q158['aba']]:
 assert q['passed'] and not q['productionExecution']
 for source,digest in q['sourceManifest'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==digest
assert q158['aba']['inheritedBindings']==2020 and len(q158['aba']['sourceManifest'])==22
assert q158['completeWait']['models']['checks']==14 and q158['completeWait']['maximumWaitSeconds']==.65 and q158['completeWait']['maximumCompleteReadAttempts']==15
for q in [q158['native157'],q158['native158']]:assert q['passed'] and q['model']['checks']==9 and not q['fullFactoryModeled'] and not q['productionExecuted']
st158=load158('actual-stages');assert st158==x158['actualStagedEpochs'] and len(st158)==8
for e in st158:
 assert e['checkpointDownloadedShaGzipVerified'] and e['independentPpidOneRollbackVerifiedBeforeWrite'] and e['payloadBytes']<=73728 and e['guardianExecBytes']<=9000
 assert e['firmwareZeroAndPhysicalQueuesRestored'] and e['fullPrivateInputsAndFrozenCopiesHashChecked'] and all(e['allOriginalRestoreChecks'].values())
f158=load158('finite-matching');assert f158==x158['latestClosePilots'] and f158['lastTcpWans']==[2,2,5,5] and f158['lastUdpWans']==[1] and f158['lastSameWanPairs']==0
assert not f158['pbrChanged'] and not f158['forcedWanOrExpandedPorts'] and not f158['rootCauseProven'] and len(f158['closePilots'])==4
assert sum(v['initialEpochStarted'] for v in f158['closePilots'])==2 and not any(v['wholePilotPassed'] or v['newSuccessorEpochStarted'] for v in f158['closePilots'])
assert all(v['oldPairExitPassed'] and v['oldPairFirmwareZero'] and v['independentRestorePassed'] for v in f158['closePilots'] if v['initialEpochStarted'])
proof158=load158('source-proof');assert proof158['passed'] and proof158['historicPrefixSources']==2521 and proof158['sources']==x158['exportedSources']==len(proof158['sourceHashes'])
assert proof158['historicPrefixCanonicalSha256']==hashlib.sha256(json.dumps(manifest['sources'][:2521],sort_keys=True,separators=(',',':')).encode()).hexdigest()
assert proof158['allEightActualEpochFullInputsFrozenCopiesVerified'] and proof158['actualStagedEpochs']==8 and not proof158['fullFactoryModelExecuted'] and proof158['old156RuntimeExactGitBytes']
for source,digest in proof158['sourceHashes'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==digest
assert len(load158('failures'))==x158['failuresPreserved']==18
for field,file,rf in [('finalAudit','final-audit','audit'),('physicalRestore','physical-final','physicalRootRestoreAudit'),('endpointClosure','endpoint-client-closure','endpointClientClosureAudit')]:assert x158[field]==load158(file)==rt158[rf]
assert rt158['audit']['queryAge']<6 and not rt158['audit']['wan4Up']
for k in ['passed','originalFullLockedNativeAudit','unrelatedConfigurationMatches','exactWan4AutomaticFailoverProved','ecmStoppedAndZero','noActiveTransaction','noStaging','noExperimentState','noExperimentalModule']:assert rt158['audit'][k]
assert rt158['physicalRootRestoreAudit']['physicalWanOriginalMqFourFqCodelRestored'] and rt158['physicalRootRestoreAudit']['lan4OriginalMqFourFqCodelRestored']
ep158=rt158['endpointClientClosureAudit'];assert ep158['passed'] and ep158['previousLoadsChecked']==ep158['ownedUnitsInactiveMainPidZero']==46 and ep158['temporaryFirewallRulesRemaining']==ep158['ownedClientOrGuardProcessesRemaining']==0
assert ep158['allCanonicalFirewallBaselinesMatch'] and ep158['tcpAndUdpPortsClosed'] and not ep158['remoteWrites'] and not ep158['productionWrites']
for field,file in [('ownedReceiverClosureAudit','receiver-closure'),('ownedDownloadReceiverClosureAudit','download-receiver-closure')]:assert rt158[field]==load158(file) and rt158[field]['passed'] and rt158[field]['exactOwnedReceiverAndTimeoutProcessesRemaining']==0

wp158=load158('publication-whitespace-check');assert wp158['exitCode']==1 and wp158['commitAndPushStopped'] and not wp158['frozenSourceBytesChanged'] and wp158['sourceHashesStillMatch'] and len(wp158['exactPathAttributes'])==4
assert hashlib.sha256((root/'code'/wp158['repairSource']).read_bytes()).hexdigest()==wp158['repairSourceSha256']
assert manifest['lastAppendExport'] in ['NSS158','NSS159','NSS160_V1_FROZEN','V11_BOUNDED_ENTRY','V13_TWO_WAN_NIGHT','V14_TWO_WAN_DURATION','V15_WAN_CLASS_QOS','V16_THREE_FLOW_MULTIWAN','V17_BUDGET_RT','V18_BORROW_RETIRED','V19_BORROW_PASS','V20_FIVE_QUEUE_MAP','V26_NORMAL_APP_ENTRY','V27_OWN_RAW_PREREQUISITE']

# NSS159: actual bounded DOWNLOAD; functional success is not RT quality acceptance.
load159=lambda n:json.loads((root/f'evidence/nss159-{n}.json').read_text())
x159=load159('mainline');rt159=json.loads((root/'evidence/nss159-runtime.json').read_text())
assert x159['passed'] and x159['round']==rt159['round']=='NSS159'
assert x159['status']=='DOWNLOAD_FUNCTIONAL_ABA_PASSED_RT_ECHO_GAP_UNRESOLVED_CPU_COMPARABILITY_FAILED'
assert x159['functionalTwentySecondDownloadABA'] and x159['downloadFlowDataRatherThanAck'] and x159['schoolPolicyPbrCtMarkNatAffinityUnchanged']
assert x159['boundInputs']==rt159['boundInputs']==2086 and x159['qualifiedExperimentalController']==rt159['qualifiedExperimentalController']=='work/nss159/pilot-supervisor-v4.mjs'
assert not any(x159[k] for k in ['realTimeQualityAccepted','permanentNssEnabled','permanentControllerInstalled','humanCs2Acceptance','highLoad300MbpsAcceptance','desktopOperated'])
assert not rt159['realTimeQualityAccepted'] and not rt159['cpuComparabilityAccepted'] and rt159['cpuConclusion'] is None and x159['cpuConclusion'] is None
assert rt159['classifierDeployment']=='NSS68' and rt159['classifierConfigSha256']==rt158['classifierConfigSha256'] and rt159['guardianPid']==17139
assert x159['prior158RuntimeSha256']==rt159['historical158RuntimePreservedSha256']==hashlib.sha256((root/'evidence/nss158-runtime.json').read_bytes()).hexdigest()
m159=load159('download-metrics');assert m159==x159['downloadMetrics'] and m159['passed'] and m159['direction']=='download' and not m159['downlinkMainlyAckAndSmallUdp']
assert m159['tcpMetric']=='application received payload bytes' and m159['oneWan']==3 and m159['nativeRenewals']==7
assert [v['acceleratedCounts'] for v in m159['phases']]==[[0],[2],[0]] and all(20<=v['whole']['seconds']<21.5 and v['sampleCount']>=38 for v in m159['phases'])
assert [(v['whole']['udp']['received'],v['whole']['udp']['sent']) for v in m159['phases']]==[(856,856),(848,884),(850,850)]
assert all(v['whole']['timeSqueezeDelta']==v['whole']['softnetDropDelta']==0 for v in m159['phases'])
leaves=m159['fourLeavesNearbyAsynchronousSnapshots'];assert leaves['down']['8f05:']['dropped']==370 and leaves['down']['8f06:']['dropped']==leaves['up']['8e06:']['dropped']==0
assert all(v['packets']>0 for d in leaves.values() for v in d.values())
gap159=load159('udp-gap');assert gap159==x159['udpGap'] and gap159['sent']==884 and gap159['received']==848 and gap159['unreturned']==36 and gap159['missingRunLengths']==[36]
assert not any(gap159[k] for k in ['lossLocationProven','causedByNssProven','applicationGameMetric','realTimeQualityAccepted'])
assert gap159['allClientLogReadUntilAfterSoftwareA2AndClientExit'] and 10<gap159['missingRunsBRelativeSeconds'][0]['start']<12
cmp159=load159('download-comparison');assert cmp159==x159['downloadComparison'] and cmp159['passed'] and not cmp159['comparabilityAccepted'] and sum(cmp159['checks'].values())==5
assert cmp159['clientReceivedMbps']==[v['whole']['clientTcpMbps'] for v in m159['phases']] and cmp159['softirqRelativeReductionPercent'] is None
assert not cmp159['checks']['unselected_wan_total_below_0_5Mbps_each'] and not cmp159['checks']['unselected_wan_total_range_below_0_25Mbps']
inspect159=load159('renewal-source-inspection');assert inspect159==x159['renewalSourceInspection'] and inspect159['readOnlySourceInspection'] and inspect159['compiledGateSourceHashVerified']
assert inspect159['temporalOverlapIsNotCausation'] and inspect159['firmwareAndWireTracingStillNeeded'] and not inspect159['rootCauseProven'] and not inspect159['kernelGateModified']
fp159=load159('flow-rollback');assert fp159==x159['flowAndRollbackProof'] and fp159['payloadBytes']==73428 and fp159['guardianExecBytes']==8947 and fp159['bindings']==2086
for k in ['passed','linuxPbrCtMarkNatWanAffinityCorrect','tcpBulkUdpRtFourTagsCorrect','fourFqCodelLeavesHavePackets','fullPrivateInputsAndFrozenCopiesHashChecked','checkpointDownloadedShaGzipVerified','independentPpidOneRollbackVerifiedBeforeWrite','noGlobalConntrackFlush','classifierKernelGateAndQosSourceUnchanged']:assert fp159[k]
assert all(fp159['allOriginalRestoreChecks'].values()) and fp159['wholeAbaEcmCounts']==[0,2,0]
qs159=load159('qualification');assert len(qs159)==4 and qs159[-1]['inheritedBindings']==2079 and qs159[-1]['fixturePolicyCases']==24
for q in qs159:
 assert q['passed'] and not q['productionExecution'] and q['native158ByteUnchanged'] and q['onlyOneRemoteSenderAtATime'] and q['senderStopAcknowledgementBeforeNext']
 assert q['originalBudgetsSeconds']==[6,27,100,180] and q['byteLimits']==[9000,65536,73728,1048576]
 for source,digest in q['sourceManifest'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==digest
fixtures159=load159('fixture-trials');assert fixtures159==x159['fixtureTrials'] and len(fixtures159)==2 and all(v['confirmedOldSendersClosedBeforeNext']>0 for v in fixtures159)
for v in fixtures159:
 assert v['onlyOneRemoteSenderAtATime'] and not v['clientErrors'] and v['offeredMbps']==32 and v['globalCreditBytes']==65536 and v['firewallAndEndpointRestored'] and v['exactTwoTemporaryFirewallRulesIndependent180ExpiryVerifiedBeforeWrite']
proof159=load159('source-proof');assert proof159['passed'] and proof159['historicPrefixSources']==2687 and proof159['historicPrefixCanonicalSha256']==hashlib.sha256(json.dumps(manifest['sources'][:2687],sort_keys=True,separators=(',',':')).encode()).hexdigest()
assert proof159['historicManifestPrefixUnchanged'] and proof159['old158RuntimeExactGitBytes'] and proof159['actualInputsAndFrozenCopiesVerified'] and proof159['sources']==x159['sourcesAdded']==len(proof159['sourceHashes'])
for source,digest in proof159['sourceHashes'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==digest
assert len(load159('failures'))==7 and load159('failures')==x159['failuresPreserved']
for field,file,rf in [('eveningAudit','evening-final-audit','audit'),('physicalRestore','evening-physical-final','physicalRootRestoreAudit'),('endpointClosure','evening-endpoint-client-closure','endpointClientClosureAudit'),('ownedReceiverClosure','evening-receiver-closure','ownedReceiverClosureAudit'),('ownedDownloadSenderClosure','evening-download-sender-closure','ownedDownloadReceiverClosureAudit')]:assert x159[field]==load159(file)==rt159[rf]
assert rt159['audit']['observedAt']>='2026-10-06T11:40:00' and rt159['audit']['queryAge']<6 and rt159['audit']['wan4Up'] and rt159['audit']['wan4Ipv4Present'] and rt159['audit']['allFiveWanHealthy']
for k in ['passed','originalFullLockedNativeAudit','unrelatedConfigurationMatches','exactWan4AutomaticRecoveryProved','ecmStoppedAndZero','noActiveTransaction','noStaging','noExperimentState','noExperimentalModule']:assert rt159['audit'][k]
assert rt159['physicalRootRestoreAudit']['physicalWanOriginalMqFourFqCodelRestored'] and rt159['physicalRootRestoreAudit']['lan4OriginalMqFourFqCodelRestored']
ep159=rt159['endpointClientClosureAudit'];assert ep159['passed'] and ep159['previousLoadsChecked']==ep159['ownedUnitsInactiveMainPidZero']==48 and ep159['temporaryFirewallRulesRemaining']==ep159['ownedClientOrGuardProcessesRemaining']==0
assert ep159['allCanonicalFirewallBaselinesMatch'] and ep159['tcpAndUdpPortsClosed'] and not ep159['remoteWrites']
for field in ['ownedReceiverClosureAudit','ownedDownloadReceiverClosureAudit']:assert rt159[field]['passed'] and rt159[field]['exactOwnedReceiverAndTimeoutProcessesRemaining']==0
recovery159=load159('wan4-natural-recovery');assert recovery159['passed'] and recovery159['unchangedProtectedHealthControllerSource'] and recovery159['tenRecoveryRampStepsReproduced'] and recovery159['exact300BucketSourceAlgorithmReproduced']
assert recovery159['priorBucketCounts']==[75,75,75,0,75] and recovery159['newBucketCounts']==[60,60,60,60,60]
assert recovery159['onlyThreeWan4DhcpRulesRestored'] and recovery159['wan4RulesDerivedFromActualLease'] and not recovery159['experimentRoutingMutation'] and not recovery159['nssPermissionGranted']
assert manifest['lastAppendExport'] in ['NSS159','NSS160_V1_FROZEN','V11_BOUNDED_ENTRY','V13_TWO_WAN_NIGHT','V14_TWO_WAN_DURATION','V15_WAN_CLASS_QOS','V16_THREE_FLOW_MULTIWAN','V17_BUDGET_RT','V18_BORROW_RETIRED','V19_BORROW_PASS','V20_FIVE_QUEUE_MAP','V26_NORMAL_APP_ENTRY','V27_OWN_RAW_PREREQUISITE']

publication159=load159('publication-whitespace-repair');assert publication159==x159['publicationWhitespaceRepair'] and publication159['passed'] and not publication159['initialStagedDiffCheckPassed'] and publication159['commitChainStoppedBeforeCommit'] and publication159['frozenSourceBytesUnchanged'] and publication159['noGlobalWhitespaceRelaxation']
assert publication159['sourceSha256']==hashlib.sha256((root/publication159['sourcePath']).read_bytes()).hexdigest()

# Final finite v1 observation: real game traffic is not human experience acceptance.
load160=lambda n:json.loads((root/f'evidence/nss160-{n}.json').read_text(encoding='utf-8'))
x160=load160('mainline');rt160=json.loads((root/'evidence/current-runtime.json').read_text(encoding='utf-8'))
assert x160['round']==rt160['round']=='NSS160' and x160['passed']
assert x160['coreFunctionalAcceptanceComplete'] and rt160['coreFunctionalAcceptanceComplete']
assert not x160['v1FunctionalAcceptanceComplete'] and not rt160['v1FunctionalAcceptanceComplete']
assert x160['humanSubjectiveAcceptance'] is None and rt160['humanSubjectiveAcceptance'] is None
assert x160['userSelectedHudOnly'] and not x160['humanAcceptedInThisTrial']
assert x160['noFurtherAutomaticExperiments'] and rt160['noFurtherAutomaticExperiments']
assert not x160['permanentNssEnabled'] and not rt160['nssPermanentlyEnabled']
assert not x160['permanentNssControllerInstalled'] and x160['kernelGateAndQosUnchanged']
assert x160['boundInputs']==rt160['boundInputs']==2137
assert x160['qualifiedFrozenEntry']=='work/nss160/real-session-v4.mjs'
assert x160['sourceNativeOwnerClientSeconds']==[6,27,100,180] and x160['execRawBundleRecordBytes']==[9000,65536,73728,1048576]
assert x160['original159RuntimeSha256']==rt160['historical159RuntimePreservedSha256']==hashlib.sha256((root/'evidence/nss159-runtime.json').read_bytes()).hexdigest()
m160=load160('functional-metrics');assert m160==x160['functionalMetrics'] and m160['passed']
assert m160['oneWan']==5 and m160['realCs2DeathmatchAndExistingSteamUpdate'] and m160['humanSubjectiveAcceptance'] is None
assert [p['ecmAcceleratedCount'] for p in m160['phases']]==[0,2,0]
assert all(20<=p['seconds']<21.5 and p['sampleCount']==41 for p in m160['phases'])
assert m160['nativeRenewals']==6 and m160['actualBindingsAndFrozenCopiesVerified']==2137
assert m160['payloadBytes']==73422 and m160['guardianExecBytes']==8947 and m160['nativeRecordBytes']<1048576
assert m160['checkpointDownloadedShaGzipVerified'] and m160['independentPpidOneRollbackVerifiedBeforeWrite'] and all(m160['allOriginalRestoreChecks'].values())
assert not m160['wholePcWasAccelerated'] and not m160['hudA2Captured'] and not m160['newCpuCausalBenefitClaimed'] and m160['newCpuCausalReductionPercent'] is None
for slot,protocol,up,down in [('tcp',6,0x8e050000,0x8f050000),('udp',17,0x8e060000,0x8f060000)]:
 f=m160['flowProof'][slot];assert f['protocol']==protocol and f['ctMark']==0x50000 and f['upTag']==up and f['downTag']==down
 assert f['accelerated'] and f['natCorrect'] and f['wanAffinity']==5 and f['fromLan4'] and f['fromBridgeLan']
assert all(v['packets']>0 for d in m160['fourLeavesNearbyAsynchronousSnapshots'].values() for v in d.values())
assert m160['fourLeavesNearbyAsynchronousSnapshots']['down']['8f06:']['dropped']==m160['fourLeavesNearbyAsynchronousSnapshots']['up']['8e06:']['dropped']==0
gap160=load160('gap-decision');assert gap160==x160['gapDecision'] and gap160['decision']=='KNOWN_LIMITATION_NO_ESTABLISHED_V1_BLOCKER'
assert gap160['originalNss159Unreturned']==36 and not gap160['fixed'] and not gap160['locationProven'] and not gap160['nssCauseProven']
assert not gap160['newNssEchoReproductionPerformed'] and gap160['oneBoundedInvestigationClosed'] and gap160['furtherGapExperimentsStopped']
cpu160=load160('historical-cpu-reuse');assert cpu160==x160['historicalCpuEvidence'] and cpu160['passed'] and cpu160['currentFinalTrialCpuCausalConclusion'] is None
digest160=load160('publication-archive-correction');archive_failure160=load160('publication-archive-failure')
assert digest160['passed'] and digest160['onlyLineEndingsDiffer'] and digest160['jsonContentExactlyEqual']
assert digest160['originalMetadataAndFailedCommitRetained'] and digest160['originalCpuMetricsUnchanged'] and digest160['originalExperimentalAndFrozenSourceBytesUnchanged'] and digest160['noNewProductionExperiment']
assert digest160['originalRecordedWorkspaceBytesSha256']==cpu160['historicalEvidenceSha256']
assert digest160['historicalEvidencePath']==cpu160['historicalEvidenceReused']
assert digest160['actualGitBlobSha256']==hashlib.sha256((root/cpu160['historicalEvidenceReused']).read_bytes().replace(b'\r\n',b'\n')).hexdigest()
assert not archive_failure160['passed'] and archive_failure160['exitCode']==1 and archive_failure160['commitChainStoppedAfterFailedArchive'] and archive_failure160['failedArchiveRetainedLocally'] and not archive_failure160['experimentOrCpuMetricChanged']
assert archive_failure160['commit']==digest160['failedPublicationCommit']
assert 48<cpu160['softirqRelativeReductionPercent']<49 and not cpu160['newCpuExperimentRequired']
assert x160['finalAudit']==rt160['audit']==load160('final-audit') and rt160['audit']['queryAge']<6
for k in ['passed','originalFullLockedNativeAudit','unrelatedConfigurationMatches','allFiveWanHealthy','ecmStoppedAndZero','noActiveTransaction','noStaging','noExperimentState','noExperimentalModule']:assert rt160['audit'][k]
assert x160['originalRecoveryAudit']==load160('original-recovery-audit') and x160['originalRecoveryAudit']['passed']
ui160=load160('client-restore');assert ui160==x160['clientRestore']==rt160['clientRestore'] and ui160['humanSubjectiveAcceptance'] is None
for k in ['passed','cs2DisconnectedFromTestServer','cs2MainMenuVisuallyVerified','steamExistingUpdateCompleted','steamNoActiveDownload','originalSteamLimitDisabledAndEmptyRestored','ownedClientGuardCancelledAfterRestore','noFurtherDesktopTest']:assert ui160[k]
assert load160('failures')==x160['failuresPreserved'] and all(v['originalFailurePreserved'] for v in load160('failures'))
for q in load160('qualification'):
 assert q['passed'] and not q['productionExecution']
 for source,digest in q['sourceManifest'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==digest
proof160=load160('source-proof');assert proof160['passed'] and proof160['historicPrefixSources']==2753 and proof160['sources']==len(proof160['sourceHashes'])
assert proof160['historicPrefixCanonicalSha256']==hashlib.sha256(json.dumps(manifest['sources'][:2753],sort_keys=True,separators=(',',':')).encode()).hexdigest()
assert proof160['historicManifestPrefixUnchanged'] and proof160['old159RuntimeExactGitBytes'] and proof160['actualInputsAndFrozenCopiesVerified']==2137
for source,digest in proof160['sourceHashes'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==digest
assert manifest['lastAppendExport'] in ['NSS160_V1_FROZEN','V11_BOUNDED_ENTRY','V13_TWO_WAN_NIGHT','V14_TWO_WAN_DURATION','V15_WAN_CLASS_QOS','V16_THREE_FLOW_MULTIWAN','V17_BUDGET_RT','V18_BORROW_RETIRED','V19_BORROW_PASS','V20_FIVE_QUEUE_MAP','V26_NORMAL_APP_ENTRY','V27_OWN_RAW_PREREQUISITE']
publication160=load160('publication-whitespace')
assert publication160['passed'] and not publication160['initialStagedDiffCheckPassed'] and publication160['exitCode']==1
assert publication160['commitChainStoppedBeforeCommit'] and publication160['frozenSourceBytesUnchanged'] and publication160['noGlobalWhitespaceRelaxation'] and not publication160['productionChanges']
assert hashlib.sha256((root/publication160['sourcePath']).read_bytes()).hexdigest()==publication160['sourceSha256']
assert publication160['exactPathAttributes']==['/code/work/nss160/endpoint-firewall-guardian.py whitespace=cr-at-eol,-blank-at-eof']
if manifest['lastAppendExport'] in ['V11_BOUNDED_ENTRY','V13_TWO_WAN_NIGHT','V14_TWO_WAN_DURATION','V15_WAN_CLASS_QOS','V16_THREE_FLOW_MULTIWAN','V17_BUDGET_RT','V18_BORROW_RETIRED','V19_BORROW_PASS','V20_FIVE_QUEUE_MAP','V26_NORMAL_APP_ENTRY','V27_OWN_RAW_PREREQUISITE']:
 v11=json.loads((root/'evidence/v11-entry-delivery.json').read_text(encoding='utf-8'))
 pq11=json.loads((root/'evidence/v11-package-qualification.json').read_text(encoding='utf-8'))
 live11=json.loads((root/'evidence/v11-live-start-stop.json').read_text(encoding='utf-8'))
 sp11=json.loads((root/'evidence/v11-source-proof.json').read_text(encoding='utf-8'))
 assert v11['v1Frozen'] and v11['oneSessionPerEnable'] and v11['automationRemainsPaused']
 assert not v11['permanentNssDeployment'] and not v11['newIntegratedHardwareSessionExecuted']
 assert pq11['passed'] and pq11['nativeSourcesUnchanged'] and pq11['noNewRouterSideLua']
 assert pq11['inheritedV1Bindings']==2137 and pq11['totalBoundInputs']==2151 and pq11['hostCases']==11
 assert live11['passed'] and live11['sessionsStarted']==0 and not live11['routerExperimentStarted']
 assert live11['duplicateInvocationRefused'] and live11['activeAdmissionFileRemoved']
 assert live11['finalPhase']=='STOPPED_NO_NSS_SESSION'
 assert sp11['historicPrefixSources']==2805 and sp11['oldV1RuntimeUnchanged']
 assert sp11['historicPrefixCanonicalSha256']==hashlib.sha256(json.dumps(manifest['sources'][:2805],sort_keys=True,separators=(',',':')).encode()).hexdigest()
 for src,digest in {**sp11['sourceHashes'],**pq11['sourceManifest']}.items():
  assert hashlib.sha256((root/'code'/src).read_bytes()).hexdigest()==digest,src
if manifest['lastAppendExport'] in ['V13_TWO_WAN_NIGHT','V14_TWO_WAN_DURATION','V15_WAN_CLASS_QOS','V16_THREE_FLOW_MULTIWAN','V17_BUDGET_RT','V18_BORROW_RETIRED','V19_BORROW_PASS','V20_FIVE_QUEUE_MAP','V26_NORMAL_APP_ENTRY','V27_OWN_RAW_PREREQUISITE']:
 night=json.loads((root/'evidence/v13-night-mainline.json').read_text(encoding='utf-8'))
 np=json.loads((root/'evidence/v13-night-source-proof.json').read_text(encoding='utf-8'))
 nq=json.loads((root/'evidence/v13-night-qualification.json').read_text(encoding='utf-8'))
 nh=json.loads((root/'evidence/v13-night-hardware.json').read_text(encoding='utf-8'))
 assert night['userAuthorizedExpansion'] and night['oneTcpBulkOneUdpRtOnly'] and night['linuxPbrAndConnectionAffinityPreserved']
 assert np['passed'] and np['historicPrefixSources']==2825 and np['oldV1AndV11CodeEvidenceUnchanged']
 assert np['historicPrefixCanonicalSha256']==hashlib.sha256(json.dumps(manifest['sources'][:2825],sort_keys=True,separators=(',',':')).encode()).hexdigest()
 assert nq['passed'] and nq['twoExactSlotsOnly'] and nq['distinctNaturalWansRequired'] and nq['sourceFreshnessSeconds']==6
 assert not nh['humanGameAcceptance'] and not nh['sameLoadCpuBenefitClaim'] and not nh['permanentNssDeployment']
 assert night['actualHardwareTwoWanCompletion']==nh['actualHardwareNssSessionCompleted']
 for src,digest in np['sourceHashes'].items():assert hashlib.sha256((root/'code'/src).read_bytes()).hexdigest()==digest,src
if manifest['lastAppendExport'] in ['V14_TWO_WAN_DURATION','V15_WAN_CLASS_QOS','V16_THREE_FLOW_MULTIWAN','V17_BUDGET_RT','V18_BORROW_RETIRED','V19_BORROW_PASS','V20_FIVE_QUEUE_MAP','V26_NORMAL_APP_ENTRY','V27_OWN_RAW_PREREQUISITE']:
 duration=json.loads((root/'evidence/v14-duration-hardware.json').read_text(encoding='utf-8'))
 dp=json.loads((root/'evidence/v14-duration-source-proof.json').read_text(encoding='utf-8'))
 assert duration['passed'] and duration['actualHardware'] and duration['actualBoundInputs']==2300
 assert 60<=duration['phase']['seconds']<61 and duration['phase']['sampleCount']==121 and duration['renewals']==20
 assert duration['ecmCountsThroughoutB']==[2] and duration['finalEcmCount']==0 and all(duration['originalRecoveryFlags'].values())
 assert not duration['newCpuCausalBenefitClaimed'] and not duration['humanCs2Acceptance'] and not duration['fiveWanOrPermanentNssAcceptance']
 assert duration['sourceFreshnessSeconds']==6 and duration['kernelSeconds']==90 and duration['ownerSeconds']==180 and duration['nativeRecordBytes']<1048576
 assert dp['passed'] and dp['historicPrefixSources']==3316 and dp['oldV13AndV1EvidenceUnchanged']
 assert dp['historicPrefixCanonicalSha256']==hashlib.sha256(json.dumps(manifest['sources'][:3316],sort_keys=True,separators=(',',':')).encode()).hexdigest()
 for f,h in dp['sourceHashes'].items():assert hashlib.sha256((root/'code'/f).read_bytes()).hexdigest()==h,f
if manifest['lastAppendExport'] in ['V15_WAN_CLASS_QOS','V16_THREE_FLOW_MULTIWAN','V17_BUDGET_RT','V18_BORROW_RETIRED','V19_BORROW_PASS','V20_FIVE_QUEUE_MAP','V26_NORMAL_APP_ENTRY','V27_OWN_RAW_PREREQUISITE']:
 h=json.loads((root/'evidence/v15-qos-hardware.json').read_text(encoding='utf-8'))
 p=json.loads((root/'evidence/v15-qos-source-proof.json').read_text(encoding='utf-8'))
 assert h['passed'] and h['actualHardware'] and h['actualBoundInputs']==2335 and h['nativeGateUnchanged'] and h['residentClassifierUnchanged']
 assert 60<=h['phase']['seconds']<61 and h['ecmCountsThroughoutB']==[2] and h['finalEcmCount']==0 and h['renewals']==20 and all(h['originalRecoveryFlags'].values())
 assert h['perWanTagAndBudgetRuntimeConfigured'] and not h['saturatedRateAccuracyProven'] and not h['twoSimultaneousBulkFlowsProven']
 assert not h['newCpuCausalBenefitClaimed'] and not h['humanCs2Acceptance'] and not h['fiveWanOrPermanentNssAcceptance'] and h['nativeRecordBytes']<1048576
 assert p['historicPrefixSources']==3346 and p['oldEvidenceAndSourcesUnchanged']
 assert p['historicPrefixCanonicalSha256']==hashlib.sha256(json.dumps(manifest['sources'][:3346],sort_keys=True,separators=(',',':')).encode()).hexdigest()
 for f,d in p['sourceHashes'].items():assert hashlib.sha256((root/'code'/f).read_bytes()).hexdigest()==d,f
 for slot,wan,cls in [('tcp',3,5),('udp',2,6)]:
  v=h['flowProof'][slot];assert v['ctMark']==wan<<16 and v['wanAffinity']==wan and v['natCorrect'] and v['downTag']==(0x8f00+wan*16+cls)<<16 and v['upTag']==(0x8e00+wan*16+cls)<<16
if manifest['lastAppendExport'] in ['V16_THREE_FLOW_MULTIWAN','V17_BUDGET_RT','V18_BORROW_RETIRED','V19_BORROW_PASS','V20_FIVE_QUEUE_MAP','V26_NORMAL_APP_ENTRY','V27_OWN_RAW_PREREQUISITE']:
 h=json.loads((root/'evidence/v16-three-hardware.json').read_text(encoding='utf-8'));p=json.loads((root/'evidence/v16-three-source-proof.json').read_text(encoding='utf-8'))
 assert h['passed'] and h['actualHardware'] and h['actualBoundInputs']==2389 and h['newThreeSlotNativeGateHardwareQualified'] and h['residentClassifierUnchanged']
 assert 60<=h['phase']['seconds']<61 and h['ecmCountsThroughoutB']==[3] and h['finalEcmCount']==0 and h['renewals']==20 and all(h['originalRecoveryFlags'].values())
 assert h['twoSimultaneousBulkFlowsProven'] and not h['saturatedRateAccuracyProven'] and not h['newCpuCausalBenefitClaimed'] and not h['humanCs2Acceptance'] and not h['fiveWanOrPermanentNssAcceptance'] and h['nativeRecordBytes']<1048576
 assert p['historicPrefixSources']==3382 and p['oldEvidenceAndSourcesUnchanged'] and p['historicPrefixCanonicalSha256']==hashlib.sha256(json.dumps(manifest['sources'][:3382],sort_keys=True,separators=(',',':')).encode()).hexdigest()
 for f,d in p['sourceHashes'].items():assert hashlib.sha256((root/'code'/f).read_bytes()).hexdigest()==d,f
 for slot,wan,cls in [('tcp',1,5),('udp',2,6),('tcp2',2,5)]:
  x=h['flowProof'][slot];assert x['ctMark']==wan<<16 and x['wanAffinity']==wan and x['natCorrect'] and x['downTag']==(0x8f00+wan*16+cls)<<16 and x['upTag']==(0x8e00+wan*16+cls)<<16
if manifest['lastAppendExport'] in ['V17_BUDGET_RT','V18_BORROW_RETIRED','V19_BORROW_PASS','V20_FIVE_QUEUE_MAP','V26_NORMAL_APP_ENTRY','V27_OWN_RAW_PREREQUISITE']:
 h=json.loads((root/'evidence/v17-cap-hardware.json').read_text(encoding='utf8'));p=json.loads((root/'evidence/v17-cap-source-proof.json').read_text(encoding='utf8'))
 assert h['passed'] and h['actualHardware'] and h['actualBoundInputs']==2425 and h['nativeGateUnchangedFromV16'] and h['residentClassifierUnchanged']
 assert 60<=h['phase']['seconds']<61 and h['ecmCountsThroughoutB']==[3] and h['finalEcmCount']==0 and h['renewals']==20 and all(h['originalRecoveryFlags'].values()) and h['nativeRecordBytes']<1048576
 assert h['twoSimultaneousBulkFlowsProven'] and not h['boundedPerWanSaturationObserved'] and not h['longTermRateAccuracyProven'] and not h['newCpuCausalBenefitClaimed'] and not h['humanCs2Acceptance'] and not h['fiveWanOrPermanentNssAcceptance']
 assert h['rtLeafDrop']=={'down':0,'up':0} and h['rtEchoDuringInteriorB']['sent']==2365 and h['rtEchoDuringInteriorB']['returned']==2365 and h['rtEchoDuringInteriorB']['unreturned']==0 and h['rtEchoDuringInteriorB']['cs2Metrics']==False
 assert p['historicPrefixSources']==3432 and p['oldEvidenceAndSourcesUnchanged'] and p['historicPrefixCanonicalSha256']==hashlib.sha256(json.dumps(manifest['sources'][:3432],sort_keys=True,separators=(',',':')).encode()).hexdigest()
 for f,d in p['sourceHashes'].items():assert hashlib.sha256((root/'code'/f).read_bytes()).hexdigest()==d,f
if manifest['lastAppendExport'] in ['V18_BORROW_RETIRED','V19_BORROW_PASS','V20_FIVE_QUEUE_MAP','V26_NORMAL_APP_ENTRY','V27_OWN_RAW_PREREQUISITE']:
 h=json.loads((root/'evidence/v18-borrow-retirement.json').read_text(encoding='utf8'));p=json.loads((root/'evidence/v18-borrow-source-proof.json').read_text(encoding='utf8'))
 assert h['expectedPreciseRetirementVerified'] and not h['fullSixtySecondAcceptance'] and not h['borrowThroughputProven'] and h['originalControllerReportedFailurePreserved'] and h['sameQueryCompleteClassification'] and h['residentThresholdsUnchanged'] and h['ctExitNotInferred']
 assert 3<=h['phaseSeconds']<4 and h['actualNaturalWanSet']==[1,4,5] and h['ecm3BeforeRetirement'] and h['finalEcmCount']==0 and all(h['originalRecoveryFlags'].values()) and h['completeBaselineAuditPassed'] and h['endpointClosedAndRestored']
 assert h['classification']['tcp2']['class']=='BE' and h['classification']['tcp2']['reason']=='cooldown' and h['classification']['tcp2']['rateKbps']<h['actualFlowMaxKbps']==2000
 assert p['historicPrefixSources']==3467 and p['oldEvidenceAndSourcesUnchanged'] and p['historicPrefixCanonicalSha256']==hashlib.sha256(json.dumps(manifest['sources'][:3467],sort_keys=True,separators=(',',':')).encode()).hexdigest()
 for f,d in p['sourceHashes'].items():assert hashlib.sha256((root/'code'/f).read_bytes()).hexdigest()==d,f
if manifest['lastAppendExport'] in ['V19_BORROW_PASS','V20_FIVE_QUEUE_MAP','V26_NORMAL_APP_ENTRY','V27_OWN_RAW_PREREQUISITE']:
 h=json.loads((root/'evidence/v19-borrow-hardware.json').read_text(encoding='utf8'));p=json.loads((root/'evidence/v19-borrow-source-proof.json').read_text(encoding='utf8'))
 assert h['passed'] and h['actualHardware'] and h['actualBoundInputs']==2497 and h['nativeGateUnchangedFromV16'] and h['qosUnchangedFromV18'] and h['residentClassifierUnchanged']
 assert 60<=h['phase']['seconds']<61 and h['ecmCountsThroughoutB']==[3] and h['finalEcmCount']==0 and h['renewals']==20 and all(h['originalRecoveryFlags'].values()) and h['nativeRecordBytes']<1048576
 assert h['sharedBudgetBorrowingObserved'] and h['bulkWithinSharedDownBudget'] and h['twoSimultaneousBulkFlowsProven'] and not h['longTermRateAccuracyProven'] and not h['newCpuCausalBenefitClaimed'] and not h['humanCs2Acceptance'] and not h['fiveWanOrPermanentNssAcceptance']
 assert h['rtLeafDrop']=={'down':0,'up':0} and h['rtEchoDuringInteriorB']['sent']==2470 and h['rtEchoDuringInteriorB']['returned']==2470 and not h['rtEchoDuringInteriorB']['cs2Metrics']
 assert p['historicPrefixSources']==3502 and p['oldEvidenceAndSourcesUnchanged'] and p['historicPrefixCanonicalSha256']==hashlib.sha256(json.dumps(manifest['sources'][:3502],sort_keys=True,separators=(',',':')).encode()).hexdigest()
 for f,d in p['sourceHashes'].items():assert hashlib.sha256((root/'code'/f).read_bytes()).hexdigest()==d,f
if manifest['lastAppendExport'] in ['V20_FIVE_QUEUE_MAP','V26_NORMAL_APP_ENTRY','V27_OWN_RAW_PREREQUISITE']:
 h=json.loads((root/'evidence/v20-five-hardware.json').read_text(encoding='utf8'));p=json.loads((root/'evidence/v20-five-source-proof.json').read_text(encoding='utf8'))
 assert h['passed'] and h['actualHardware'] and h['actualBoundInputs']==2533 and h['nativeGateUnchangedFromV16'] and h['onlyQosMapExpandedFromV19'] and h['residentClassifierUnchanged']
 assert 60<=h['phase']['seconds']<61 and h['ecmCountsThroughoutB']==[3] and h['finalEcmCount']==0 and h['renewals']==20 and all(h['originalRecoveryFlags'].values()) and h['nativeRecordBytes']<1048576
 assert h['fiveWanQueueCoverageVerified'] and h['queueWanSet']==[1,2,3,4,5] and h['simultaneouslyAdmittedExactFlowCount']==3 and not h['fiveWanConcurrentFastPathProven']
 assert h['sharedBudgetBorrowingObserved'] and h['bulkWithinSharedDownBudget'] and h['twoSimultaneousBulkFlowsProven'] and not h['longTermRateAccuracyProven'] and not h['newCpuCausalBenefitClaimed'] and not h['humanCs2Acceptance'] and not h['fiveWanOrPermanentNssAcceptance']
 assert h['rtLeafDrop']=={'down':0,'up':0} and h['rtEchoDuringInteriorB']['sent']==2434 and h['rtEchoDuringInteriorB']['returned']==2434 and not h['rtEchoDuringInteriorB']['cs2Metrics']
 assert p['historicPrefixSources']==3537 and p['oldEvidenceAndSourcesUnchanged'] and p['historicPrefixCanonicalSha256']==hashlib.sha256(json.dumps(manifest['sources'][:3537],sort_keys=True,separators=(',',':')).encode()).hexdigest()
 for f,d in p['sourceHashes'].items():assert hashlib.sha256((root/'code'/f).read_bytes()).hexdigest()==d,f
if manifest['lastAppendExport'] in ['V26_NORMAL_APP_ENTRY','V27_OWN_RAW_PREREQUISITE']:
 p=json.loads((root/'evidence/v26-progress.json').read_text(encoding='utf8'));a=json.loads((root/'evidence/v26-restoration-limits.json').read_text(encoding='utf8'));q=json.loads((root/'evidence/v26-normal-entry-qualification.json').read_text(encoding='utf8'));s=json.loads((root/'evidence/v26-source-proof.json').read_text(encoding='utf8'))
 assert p['passed'] and len(p['failedFiveFlowPrerequisites'])==5 and all(not x['passed'] and not x['productionNssWrites'] and x['noCheckpointOrNativeStageStarted'] for x in p['failedFiveFlowPrerequisites'])
 assert p['fiveWanConcurrentAccelerationNotClaimed'] and not p['fiveExactFlowNativeCandidate']['hardwareLoaded'] and not p['fiveExactFlowNativeCandidate']['hardwareAcceptance']
 assert p['normalEntry']['actualReadOnlyInspectionPassed'] and p['normalEntry']['actualCs2RtCandidates']==p['normalEntry']['actualSteamBulkCandidates']==0 and not p['normalEntry']['normalApplicationFactoryHardwareAcceptance'] and not p['normalEntry']['humanGameAcceptance'] and not p['normalEntry']['permanentNssDeployment']
 assert q['passed'] and q['selectorModels']==18 and q['relativeDependenciesExist']==46 and not q['hardwareExecuted'] and not q['wholeFactoryModeled']
 assert p['normalEntry']['terminalCompleteAudit']['ecmClosedAndZero'] and p['normalEntry']['twoPhysicalRoots']['passed'] and a['passed'] and len(a['exactClientClosures'])==4
 assert s['historicPrefixSources']==3572 and s['oldCodeAndEvidenceUnmodified'] and s['binariesCredentialsRawCtAndCheckpointsExcluded'] and s['historicPrefixCanonicalSha256']==hashlib.sha256(json.dumps(manifest['sources'][:3572],sort_keys=True,separators=(',',':')).encode()).hexdigest()
 for f,h in s['sourceHashes'].items():assert hashlib.sha256((root/'code'/f).read_bytes()).hexdigest()==h,f
if manifest['lastAppendExport']=='V27_OWN_RAW_PREREQUISITE':
 h=json.loads((root/'evidence/v27-raw-prerequisite.json').read_text(encoding='utf8'));q=json.loads((root/'evidence/v27-entry-qualification.json').read_text(encoding='utf8'));p=json.loads((root/'evidence/v27-source-proof.json').read_text(encoding='utf8'))
 assert h['passed'] and not h['prerequisiteTestPassed'] and h['originalControllerFailurePreserved'] and not any(h[k] for k in ['productionNssWrites','checkpointOrNativeStageStarted','fiveSlotModuleHardwareLoaded','fiveWanConcurrentFastPathProven'])
 assert h['client']['tcpPayloadBytes']==0 and 8<=h['client']['seconds']<9 and h['sourceBindings']==2761 and q['passed'] and q['nativeAndQosByteEquivalent'] and not q['fiveSlotHardwareExecuted']
 assert h['localActualSenderChecks']==10 and h['localProtocolModels']==33 and all(h['exactClientClosure'][k] for k in ['passed','clientExitedBeforeDeadline','exactClientOnly']) and h['exactEndpointClosure']['passed'] and h['terminalCompleteAudit']['ecmClosedAndZero'] and h['terminalPhysicalRoots']['passed']
 assert p['historicPrefixSources']==3801 and p['oldEvidenceAndSourcesUnmodified'] and p['historicPrefixCanonicalSha256']==hashlib.sha256(json.dumps(manifest['sources'][:3801],sort_keys=True,separators=(',',':')).encode()).hexdigest()
 for f,d in p['sourceHashes'].items():assert hashlib.sha256((root/'code'/f).read_bytes()).hexdigest()==d,f
if (root/'evidence/morning-preparation.json').exists():
 mp=json.loads((root/'evidence/morning-preparation.json').read_text(encoding='utf8'));ms=json.loads((root/'evidence/morning-preparation-source-proof.json').read_text(encoding='utf8'))
 assert mp['passed'] and mp['preparationOnly'] and not mp['morningFinalAuditPerformed'] and not mp['productionExperimentPermissionGranted'] and mp['localKnownEndpointUnitCount']==17
 assert ms['historicPrefixSources']==3857 and ms['oldCodeAndEvidenceUnmodified'] and ms['historicPrefixCanonicalSha256']==hashlib.sha256(json.dumps(manifest['sources'][:3857],sort_keys=True,separators=(',',':')).encode()).hexdigest()
 for f,d in ms['sourceHashes'].items():assert hashlib.sha256((root/'code'/f).read_bytes()).hexdigest()==d,f
if (root/'evidence/morning-final.json').exists():
 mf=json.loads((root/'evidence/morning-final.json').read_text(encoding='utf8'));sp=json.loads((root/'evidence/morning-final-source-proof.json').read_text(encoding='utf8'))
 assert mf['passed'] and mf['readonly'] and not mf['productionExperimentsStarted']
 assert '2026-10-06T23:40:00Z'<=mf['observedAt']<'2026-10-07T00:00:00Z'
 assert mf['fullAudit']['passed'] and mf['fullAudit']['protectedConfigurationUnchanged'] and mf['fullAudit']['ecmClosedAndZero'] and mf['fullAudit']['allFiveHealthyWanBaseline'] and not mf['fullAudit']['nssAdmissionAllowed'] and mf['fullAudit']['queryAge']<6
 assert mf['physicalQueues']['passed'] and mf['physicalQueues']['defaultQueueOptionsAndHandlesExact'] and mf['physicalQueues']['physicalWanOriginalMqFourFqCodelRestored'] and mf['physicalQueues']['lan4OriginalMqFourFqCodelRestored']
 assert mf['endpointClosure']['passed'] and mf['endpointClosure']['knownOwnedUnitsChecked']==17 and mf['endpointClosure']['ownedUnitsInactiveMainPidZero'] and mf['endpointClosure']['canonicalFirewallBaselineMatched'] and mf['endpointClosure']['temporaryFirewallRulesRemaining']==0 and mf['endpointClosure']['tcpAndUdpEndpointPortsClosed'] and not mf['endpointClosure']['remoteWrites']
 assert mf['clientClosure']['passed'] and mf['clientClosure']['knownNightFixtureNamespacesChecked']==16 and mf['clientClosure']['ownedClientControllerGuardOrSenderProcessesRemaining']==0
 assert sp['passed'] and sp['historicPrefixSources']==3863 and sp['oldCodeAndEvidenceUnmodified'] and sp['gitFilteredBaselineAndOriginalWorktreeBytesChecked'] and sp['rawProcessSshCtCredentialsAndCheckpointsExcluded'] and sp['actualReadonlyProcessExitCodes']==[0,0,0,0]
 assert sp['historicPrefixCanonicalSha256']==hashlib.sha256(json.dumps(manifest['sources'][:3863],sort_keys=True,separators=(',',':')).encode()).hexdigest()
 for f,d in sp['sourceHashes'].items():assert hashlib.sha256((root/'code'/f).read_bytes()).hexdigest()==d,f
 assert sp['localReadCorrection']['originalReadFailed'] and sp['localReadCorrection']['originalExitCode']==1 and not sp['localReadCorrection']['productionAuditAffected']
 assert sp['firstPublisherFailurePreserved']['beforeAnyAppend'] and sp['firstPublisherFailurePreserved']['onlyCRLFConversionVerified'] and sp['firstPublisherFailurePreserved']['oldEvidenceNotEdited']
if (root/'evidence/v29-peer-source-proof.json').exists():
 peer=json.loads((root/'evidence/v28-peer-path.json').read_text(encoding='utf8'));short=json.loads((root/'evidence/v29-peer-proof.json').read_text(encoding='utf8'));end=json.loads((root/'evidence/v29-peer-restoration.json').read_text(encoding='utf8'));sp=json.loads((root/'evidence/v29-peer-source-proof.json').read_text(encoding='utf8'))
 assert manifest['lastAppendExport']=='V27_OWN_RAW_PREREQUISITE' and manifest['lastPrerequisiteDiagnosticExport']=='V29_PROTOCOL_SPECIFIC_PEER_PROOF'
 assert peer['diagnosticCompleted'] and not peer['configurationWrites'] and not peer['nssStarted'] and peer['tcpPeerWasNotNonceAuthenticated'] and not peer['tcpAndUdpPublicSourceEqual']
 assert not peer['correlationLimits']['tcpSynSourcePortMatchesOwnedClient'] and not peer['correlationLimits']['tcpSynSourcePortMatchesExactCtReplyPort']
 assert {(x['protocol'],x['wan'],x['mark']) for x in peer['ctWanMarks']}=={('tcp',1,65536),('udp',5,327680)}
 assert short['passed'] and short['tcpAuthenticatedReady'] and short['tcpPayloadBytes']==22960476 and 0<short['firstPayloadSeconds']<short['firstPayloadDeadlineSeconds']==8 and 25<=short['clientSeconds']<26
 assert not short['clientErrors'] and short['singleTcpSlotMbps']==8 and short['protocolSpecificPublicPeersDiffer'] and short['exactFirewallRules']==2 and short['eachSourceRemainsOneIPv4Address']
 assert short['independentFirewallExpirySeconds']==180 and short['independentEndpointExpirySeconds']==250 and short['clientIndependentDeadlineSeconds']==25 and short['checkpointDownloadShaAndGzipVerifiedBeforeWrite'] and short['guardianByteIdenticalToV27'] and short['serverAndProtocolByteIdenticalToV27']
 assert not any(short[k] for k in ['nssStarted','routerConfigurationWrites','fourTcpOrFiveWanFixtureQualified','historicalV27ExactFailureCauseProven']) and short['udpCountersAreWholeDiagnosticNotLossAcceptance']
 assert end['passed'] and end['readonly'] and not end['productionNssWrites'] and end['fullAudit']['ecmClosedAndZero'] and end['fullAudit']['protectedConfigurationUnchanged'] and end['fullAudit']['queryAge']<6 and end['fullAudit']['allFiveHealthyWanBaseline']
 assert end['physicalQueues']['defaultQueueOptionsAndHandlesExact'] and end['physicalQueues']['physicalWanOriginalMqFourFqCodelRestored'] and end['physicalQueues']['lan4OriginalMqFourFqCodelRestored']
 close=end['endpointAndClientClosure']; assert close['passed'] and close['canonicalFirewallBaselineMatched'] and close['temporaryFirewallRulesRemaining']==0 and close['endpointPortsClosed'] and close['ownedUnitInactiveMainPidZero'] and close['independentGuardianPastNaturalDeadline'] and not close['sameGuardianStillLive'] and close['clientClosure']['ownedDiagnosticClientProcessesRemaining']==0 and not close['remoteWrites']
 assert sp['passed'] and sp['historicPrefixSources']==3866 and sp['oldCodeAndEvidenceUnmodified'] and sp['oldCodeAndEvidenceBlobsChecked']==4391 and sp['rawCtPublicPeerAddressesNoncesCredentialsCheckpointsAndBinariesExcluded'] and sp['noNewNssCpuGameOrFiveWanHardwareAcceptanceClaim']
 assert sp['historicPrefixCanonicalSha256']==hashlib.sha256(json.dumps(manifest['sources'][:3866],sort_keys=True,separators=(',',':')).encode()).hexdigest()
 assert sp['firstRestorationFailure']['preserved'] and sp['firstRestorationFailure']['code']==1 and sp['firstRestorationFailure']['refusedBeforeFullRestorationAudit'] and sp['firstRestorationFailure']['oneLaterReadonlyRecheckPassed']
 for f,d in sp['sourceHashes'].items(): assert hashlib.sha256((root/'code'/f).read_bytes()).hexdigest()==d,f
 for item in sp['actualTrialSourceInputs']: assert hashlib.sha256((root/'code'/item['path']).read_bytes()).hexdigest()==item['sha256'],item['path']
 assert hashlib.sha256((root/'code/work/v27-raw/endpoint-firewall-guardian.py').read_bytes()).hexdigest()==sp['guardianSha256']
if (root/'evidence/v31-normal-source-proof.json').exists():
 sp=json.loads((root/'evidence/v31-normal-source-proof.json').read_text(encoding='utf8'))
 q30=json.loads((root/'evidence/v30-normal-entry-qualification.json').read_text(encoding='utf8'))
 q31=json.loads((root/'evidence/v31-normal-entry-qualification.json').read_text(encoding='utf8'))
 refused=json.loads((root/'evidence/v30-normal-refusal.json').read_text(encoding='utf8'))
 model=json.loads((root/'evidence/v31-last-selection-models.json').read_text(encoding='utf8'))
 inspected=json.loads((root/'evidence/v31-normal-inspect.json').read_text(encoding='utf8'))
 end=json.loads((root/'evidence/v31-normal-restoration.json').read_text(encoding='utf8'))
 assert manifest['lastNormalApplicationExport']=='V31_PRESTAGE_TCP_SELECTION'
 assert sp['passed'] and sp['baseCommit']=='e09c8cf4005a08613fc38b93130392522fb711d9' and sp['historicPrefixSources']==3878
 assert sp['historicPrefixCanonicalSha256']==hashlib.sha256(json.dumps(manifest['sources'][:3878],sort_keys=True,separators=(',',':')).encode()).hexdigest()
 assert sp['oldCodeAndEvidenceBlobsChecked']==4407 and sp['oldCodeAndEvidenceUnmodified'] and sp['actualFailedTrialBoundInputsAndFrozenCopiesExact']==2615
 assert sp['v30Bindings']==2615 and sp['v31Bindings']==2651 and sp['unchangedDataPlaneAndImmutableCandidatePolicy'] and sp['oldQualifiedV30SourcesPreserved']
 assert sp['onlyPreDetachedStageHostTcpSelectionChanged'] and sp['noInstalledGateRetargeting'] and sp['rawCtNoncesCredentialsConfigurationsCheckpointsBinariesAndProcessCommandLinesExcluded'] and sp['originalFailuresPreservedLocally'] and sp['partialUiRestorationExplicitlyReported']
 for src,digest in sp['sourceHashes'].items():assert hashlib.sha256((root/'code'/src).read_bytes()).hexdigest()==digest,src
 for q in (q30,q31):
  assert q['passed'] and not q['hardwareExecuted'] and not q['wholeFactoryModeled'] and not q['normalApplicationFactoryHardwareAcceptance'] and not q['humanAcceptance'] and not q['permanentNssDeployment']
  assert q['sourceFreshnessSeconds']==6 and q['kernelSessionSeconds']==90 and q['kernelMaximumSeconds']==120 and q['ownerSeconds']==180 and q['phaseSeconds']==60 and q['maximumExactFlows']==3 and q['defaultInspectOnly']
  for src,digest in q['sourceManifest'].items():assert hashlib.sha256((root/'code'/src).read_bytes()).hexdigest()==digest,src
 assert q30['inheritedBindings']==2586 and len(q30['sourceManifest'])==29 and q30['relativeDependenciesExist']==48
 assert q31['inheritedBindings']==2615 and len(q31['sourceManifest'])==36 and q31['relativeDependenciesExist']==61 and q31['actualRefusalRegressionModels']==14 and q31['clientMaximumSeconds']==180
 for name in ['candidate-policy.mjs','classifier.lua','classified-tags.lua','fast-path.lua','qos-physical.lua','module-stage-guardian.lua','native-qualified.json','normalizer-qualified.json','qos-native-qualified.json']:
  assert (root/'code/work/v31-normal'/name).read_bytes()==(root/'code/work/v30-normal'/name).read_bytes(),name
 assert not refused['trial']['passed'] and refused['trial']['errors']==['AssertionError [ERR_ASSERTION]: Controlled exact pair changed after original full audit']
 diag=refused['diagnosis'];assert diag['passed'] and diag['refusalBeforeCheckpoint'] and not diag['anyCheckpointCreated'] and not diag['anyDetachedStageStarted'] and not diag['nssHardwareAcceptance']
 assert not diag['slots']['tcp']['exactApplicationOwnedIdentityStillPresent'] and diag['slots']['udp']['exactApplicationOwnedIdentityStillPresent'] and diag['slots']['tcp2']['exactApplicationOwnedIdentityStillPresent'] and diag['producerMatchesInitial']
 assert refused['actualReader']['actualCs2RtCandidates']==1 and refused['actualReader']['actualSteamBulkCandidates']==24 and refused['actualFrozenInputsExact']==2615
 assert refused['missingQualifiedProjectionDoesNotProveCtExit'] and not refused['tcpLifetimeCauseEstablished'] and refused['originalFailureAndPrivateInputBytesPreserved']
 assert not any(refused[k] for k in ['checkpointCreated','detachedStageStarted','ecmOpened'])
 assert model['passed'] and model['modelOnly'] and model['checks']==14 and model['actualHistoricalRefusalFrameUsed'] and not model['hardwareExecuted']
 assert model['actualFrameSha256']==diag['frameSha256'] and model['originalGameRetained'] and model['provisionalTcpMayChangeOnlyBeforeDetachedStage']
 assert model['unchangedWanFullMarkNatAddressAndProtectedInputsRequired'] and model['originalImmutableRefinementStillRefusesChangedTcp'] and model['noGateRetargeting'] and model['noRouterWrites']
 for src,digest in model['sourceHashes'].items():assert hashlib.sha256((root/'code'/src).read_bytes()).hexdigest()==digest,src
 assert inspected['actualReader']['readonly'] and inspected['actualReader']['actualCs2RtCandidates']==1 and inspected['actualReader']['actualSteamBulkCandidates']==0 and not inspected['actualReader']['nssAdmissionAllowed']
 assert inspected['declinedForNoBulkAndInsufficientRemainingClientTime'] and not any(inspected[k] for k in ['fullControllerSessionStarted','oneSessionAttemptFileCreated','checkpointCreated','detachedStageStarted','ecmOpened','clientDeadlineReset','newGuardForRetryStarted','factoryHardwareAcceptance','subjectiveHumanAcceptance'])
 audit=end['reusedOriginalFullAudit'];assert audit['passed'] and audit['queryAge']<6 and audit['ecmClosedAndZero'] and audit['protectedConfigurationUnchanged'] and audit['allFiveHealthyWanBaseline'] and audit['serviceEpochPinned']
 assert end['protectedBaseline']['configurationMatches'] and all(end['protectedBaseline']['checks'].values()) and end['protectedBaseline']['rawRulesetIdentical'] and end['noRouterConfigurationWritesAfterThatAudit']
 physical=end['currentPhysicalQueues'];assert physical['passed'] and physical['readonly'] and physical['defaultQueueOptionsAndHandlesExact'] and physical['physicalWanOriginalMqFourFqCodelRestored'] and physical['lan4OriginalMqFourFqCodelRestored']
 clients=end['clientProcessClosure'];assert clients['passed'] and clients['readonly'] and clients['ownedTestProcessesRemaining']==clients['cs2ProcessesRemaining']==clients['steamProcessesRemaining']==0
 assert len(clients['guards'])==2 and all(g['readyBeforeDownload'] and g['naturalTimedExitPassed'] and g['guardProcessGone'] and g['deadlineSeconds']==180 and not g['originalClientUiRestoredByGuard'] for g in clients['guards'])
 assert clients['independentProcessExitDoesNotProveOriginalUiRestoration'] and clients['noNewControllerOrGuardStarted']
 ui=end['clientUiObservations'];assert not ui['automatedSubjectiveHumanExperience'] and not ui['v30']['nssEntered'] and not ui['v30']['nssOrSubjectiveGameQualityAcceptance']
 assert ui['v31']['downloadPausedVisuallyVerifiedBeforeGuardExit'] and ui['v31']['networkAndDiskVisuallyZeroAfterPause'] and ui['v31']['originalLimitDisabledVisuallyVerifiedBeforeGuardExit']
 assert not ui['v31']['jitterLossMissVisible'] and not ui['v31']['nssOrSubjectiveGameQualityAcceptance'] and not ui['v31']['inactiveLimitNumericValueByteRestorationProven']
 assert ui['currentRestoration']['downloadAndLimitRestoredBeforeGuardExit'] and ui['currentRestoration']['ephemeralLoginWindowNotAutomated'] and not ui['currentRestoration']['originalUiRestorationComplete']
 assert end['routerAndOwnedTestProcessClosurePassed'] and not any(end[k] for k in ['originalClientUiRestorationComplete','permanentNssDeployment','newCpuCausalAcceptance','normalFactoryHardwareAcceptance'])
 whitespace=json.loads((root/'evidence/v31-publication-whitespace.json').read_text(encoding='utf8'))
 assert whitespace['passed'] and not whitespace['initialStagedDiffCheckPassed'] and whitespace['originalFailureExitCode']==2 and whitespace['submissionStoppedBeforeCommit'] and whitespace['postAttributeStagedDiffCheckExitCode']==0
 assert whitespace['inheritedFromV26ExactBytes'] and whitespace['noGlobalWhitespacePolicyChange'] and whitespace['experimentalSourcesAndPrivateInputsUnchanged']
 assert whitespace['exactPathAttributes']==['/code/work/v30-normal/fast-path.lua whitespace=cr-at-eol,-blank-at-eol','/code/work/v31-normal/fast-path.lua whitespace=cr-at-eol,-blank-at-eol']
 for src,digest in whitespace['sourceHashes'].items():
  assert hashlib.sha256((root/src).read_bytes()).hexdigest()==digest==hashlib.sha256((root/'code/work/v26-normal/fast-path.lua').read_bytes()).hexdigest()
 for attr in whitespace['exactPathAttributes']:assert attr in (root/'.gitattributes').read_text(encoding='utf8')
print(json.dumps({'passed':True,'filesChecked':count,'sourceHashesChecked':len(manifest['sources']),'markdownLinksChecked':links,'obviousSecretChecksPassed':True,'scope':'Curated allowlist plus pattern checks; not a claim of comprehensive secret detection.'}))
