"""Preserve historical 158 checks and validate actual download/quality distinction."""
from pathlib import Path
w=Path(__file__).resolve().parents[2];p=w/'athena-nss-mainline/tools/check_repository.py';s=p.read_text(encoding='utf-8')
a="rt158=json.loads((root/'evidence/current-runtime.json').read_text())";assert s.count(a)==1;s=s.replace(a,a.replace('current-runtime.json','nss158-runtime.json'))
a="assert manifest['lastAppendExport'] in ['NSS156','NSS158']";assert s.count(a)==1;s=s.replace(a,a[:-1]+",'NSS159']")
a="assert manifest['lastAppendExport']=='NSS158'";assert s.count(a)==1;s=s.replace(a,"assert manifest['lastAppendExport'] in ['NSS158','NSS159']")
anchor="print(json.dumps({'passed':True,'filesChecked':count,'sourceHashesChecked':len(manifest['sources']),'markdownLinksChecked':links,'obviousSecretChecksPassed':True,'scope':'Curated allowlist plus pattern checks; not a claim of comprehensive secret detection.'}))";assert s.count(anchor)==1
check='''# NSS159: actual bounded DOWNLOAD; functional success is not RT quality acceptance.
load159=lambda n:json.loads((root/f'evidence/nss159-{n}.json').read_text())
x159=load159('mainline');rt159=json.loads((root/'evidence/current-runtime.json').read_text())
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
assert manifest['lastAppendExport']=='NSS159'
'''
p.write_text(s.replace(anchor,check+'\n'+anchor),encoding='utf-8')
print('Historical NSS158 checks preserved; actual NSS159 download and quality gap checks appended')
