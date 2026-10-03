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
    if not file.is_file() or '.git' in file.relative_to(root).parts or '.local' in file.relative_to(root).parts: continue
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
c=json.loads((root/'evidence/current-runtime.json').read_text())
assert n['checks']==136 and n['classifier']['committed'] and n['automaticRollback']['passed']
assert c['round']=='NSS40' and c['deploymentReference']=='work/nss39/deployment-latest.json'
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
assert hashlib.sha256((root/'code/deployed-classifier/conntrack-source.lua').read_bytes()).hexdigest()==y['change']['newSha256']
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
assert hashlib.sha256((root/'code/deployed-classifier/worker.lua').read_bytes()).hexdigest()==v['classifier']['workerSha256']
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
assert c['staleSnapshotRejectedEarlierInRound'] and not c['plannedClassifierReplacementAndRollbackThisRound'] and not c['experimentalConfigurationWritesThisRound']
print(json.dumps({'passed':True,'filesChecked':count,'sourceHashesChecked':len(manifest['sources']),'markdownLinksChecked':links,'obviousSecretChecksPassed':True,'scope':'Curated allowlist plus pattern checks; not a claim of comprehensive secret detection.'}))
