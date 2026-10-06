"""Keep NSS156 historical audit and validate latest actual class/ABA scopes."""
from pathlib import Path
w=Path(__file__).resolve().parents[3];r=w/'athena-nss-mainline';p=r/'tools/check_repository.py'
s=p.read_text(encoding='utf-8')
old="rt156=json.loads((root/'evidence/current-runtime.json').read_text())"
assert s.count(old)==1
s=s.replace(old,old.replace('current-runtime.json','nss156-runtime.json'))
assert s.count("assert manifest['lastAppendExport']=='NSS156'")==1
s=s.replace("assert manifest['lastAppendExport']=='NSS156'","assert manifest['lastAppendExport'] in ['NSS156','NSS158']")
anchor="print(json.dumps({'passed':True,'filesChecked':count,'sourceHashesChecked':len(manifest['sources']),'markdownLinksChecked':links,'obviousSecretChecksPassed':True,'scope':'Curated allowlist plus pattern checks; not a claim of comprehensive secret detection.'}))"
assert s.count(anchor)==1
new='''# NSS158: actual NSS157 precise class retirement + new NSS158 functional ABA.
load158=lambda n:json.loads((root/f'evidence/nss158-{n}.json').read_text())
x158=load158('mainline');rt158=json.loads((root/'evidence/current-runtime.json').read_text())
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
assert manifest['lastAppendExport']=='NSS158'
'''
s=s.replace(anchor,new+'\n'+anchor)
p.write_text(s,encoding='utf-8')
attrs=r/'.gitattributes';a=attrs.read_text(encoding='utf-8');a+='\n# Frozen actual NSS156 runtime bytes.\n/evidence/nss156-runtime.json -text\n'
attrs.write_text(a,encoding='utf-8')
print('Historical NSS156 remains exact; actual NSS157/158 function and failed CPU comparability asserted')
