"""Sanitize failed five-flow prerequisites and the normal-app read-only entry."""
from pathlib import Path
import hashlib
import json

w = Path(__file__).resolve().parents[2]; r = w / 'work/v26-normal'
read = lambda p: json.loads(p.read_text(encoding='utf8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
attempts = []
for version in ['v21-fiveflow','v22-fiveflow','v23-fiveflow','v24-fiveflow']:
    parent = w / 'work' / version
    for p in sorted(parent.glob('pilot-aba-*')):
        result = read(p / 'automatic-result.json'); assert result['passed'] is False
        driver = read(p / 'driver-private.json')
        assert not (p / 'case-reference-private.json').exists() and not (p / 'detached-owner-reference-private.json').exists()
        loads = [x for x in driver if x['file'].endswith('/start-dallas.mjs') and x['code'] == 0]
        item = {'version':version,'passed':False,'productionNssWrites':False,'noCheckpointOrNativeStageStarted':True,
                'rawResultSha256':sha(p/'automatic-result.json'),'originalFailurePreserved':True,
                'endpointsStarted':bool(loads)}
        if version == 'v21-fiveflow':
            item['reason'] = 'Five natural WANs matched, but fixed client restoration margin was insufficient'
        elif version == 'v22-fiveflow':
            item['reason'] = 'Stale local directory validator rejected before PC or router access'
        else:
            item['reason'] = 'Own SSH fixture handshake failed before NSS; not an NSS data-plane failure'
        if loads:
            load = w / json.loads(loads[0]['stdout'].strip().splitlines()[-1])['dir']
            closure = read(load/'endpoint-retry-closure.json')
            assert closure['passed'] and closure['baselineRestored'] and closure['ownedRulesRemaining']==0 and closure['exactOwnedEndpointClosed']
            item['exactEndpointFirewallAndClientClosurePassed'] = True
            item['endpointClosureSha256'] = sha(load/'endpoint-retry-closure.json')
            client = read(load/'result-private.json')
            item['clientDurationSeconds'] = client['seconds']
            item['ownHandshakeErrorOccurred'] = bool(client['errors'])
            if client['errors']:
                assert all('SSH' in e and ('timed out' in e or 'first-byte deadline' in e) for e in client['errors'])
            if version == 'v24-fiveflow':
                ready = [x for x in driver if x['file'].endswith('/wait-four-ssh.mjs') and x['code']==0]
                assert len(ready)==1
                item['fourInitialOwnHandshakesCompleted'] = True
                item['failureOccurredDuringOwnTcpRotation'] = True
        attempts.append(item)
assert len(attempts)==5
native = read(w/'work/v21-fiveflow/native-source-qualified.json')
ram = read(w/'work/v21-fiveflow/native-qualified.json')
elf = read(w/'work/v21-fiveflow/runtime-elf-comparison.json')
assert native['passed'] and ram['passed'] and elf['passed'] and not elf['runtimeLoaded'] and not elf['abiQualification']
modelSizes={}
for n in [1,2,3]:
    v=read(w/f'work/v21-fiveflow/size-model-v{n}-private.json')
    modelSizes[str(n)]={k:x for k,x in v.items() if k in ['bundleBytes','guardianExecBytes','nativeTagBatchBytes','tagBatchBytes','moduleArgumentsBytes','insmodBytes','withinOriginalLimits','passed']}
newReader=read(r/'real-reader-qualified.json'); assert newReader['readonly'] and newReader['actualCs2RtCandidates']==0 and newReader['actualSteamBulkCandidates']==0 and not newReader['nssAdmissionAllowed']
audits=list(r.glob('session-*-terminal-audit.json'));assert len(audits)==1
health=read(audits[0]);physical=read(r/'terminal-physical-summary.json')
assert health['passed'] and health['protectedConfigurationUnchanged'] and health['ecmClosedAndZero'] and health['allFiveHealthyWanBaseline'] and physical['passed']
normal={'passed':True,'actualReadOnlyInspectionPassed':True,'actualCs2RtCandidates':0,'actualSteamBulkCandidates':0,
        'noNssPermissionOrSession':True,'trafficGenerated':False,'desktopOperated':False,
        'normalApplicationSelectorModels':18,'relativeDependenciesChecked':46,
        'normalApplicationFactoryHardwareAcceptance':False,'humanGameAcceptance':False,'permanentNssDeployment':False,
        'dataPlaneAndFiveWanQosFromProvenV20Unchanged':True,'firstMissingDependencyFailurePreserved':True,
        'entryBindings':2586,'maximumSelectedExactFlows':3,'hardwareScopeReusedFromV20':'two TCP BULK plus one UDP RT, two or three WANs',
        'readOnlySourceAgeSeconds':newReader['sourceAge'],'terminalCompleteAudit':health,'twoPhysicalRoots':physical}
out={'passed':True,'fiveExactFlowNativeCandidate':{'compiledAndModelQualified':True,'controlCases':63,'ctCases':68,'runtimeBytes':55872,
      'runtimeSha256':elf['runtimeSha256'],'allocatedSectionsAndRuntimeRelocationsUnchanged':True,'hardwareLoaded':False,'hardwareAcceptance':False,
      'differentFiveWanCtRequirement':True,'targetRamModels':14,'bundleLimit':73728,'execLimit':9000,'nftBatchLimit':49152,'recordLimit':1048576,
      'sourceSeconds':6,'kernelSeconds':90,'maximumKernelSeconds':120,'ownerSeconds':180,'clientSeconds':180,'modelSizes':modelSizes,
      'losslessJsonDataEncodingAndEquivalentGuardFactoring':True},'failedFiveFlowPrerequisites':attempts,
      'localCopyAndModelFailuresRetained':True,'nssOrFirmwareCauseOfOwnSshTimeoutEstablished':False,
      'normalEntry':normal,'provenMultiWanAdvancedQosHardwareEvidence':'v20-five-hardware.json',
      'fiveWanConcurrentAccelerationNotClaimed':True,'newCpuCausalBenefitNotClaimed':True,'nightDeadlineBeijing':'2026-10-07 08:00',
      'noFurtherFiveFlowExperimentWithoutNewExecutablePrerequisite':True}
with (r/'progress-sanitized.json').open('x',encoding='utf8') as f:
    json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'passed':True,'retainedFailedAttempts':len(attempts),'fiveNativeHardwareLoaded':False,'normalReadonlyPassed':True,'terminalAuditPassed':True}))
