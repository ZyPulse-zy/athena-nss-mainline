from pathlib import Path
w=Path(__file__).resolve().parents[3];p=w/'athena-nss-mainline/tools/check_repository.py';s=p.read_text(encoding='utf-8')
old="x155=json.loads((root/'evidence/nss155-mainline.json').read_text());rt155=json.loads((root/'evidence/current-runtime.json').read_text())"
assert s.count(old)==1;s=s.replace(old,old.replace('evidence/current-runtime.json','evidence/nss155-runtime.json'))
anchor="print(json.dumps({'passed':True,'filesChecked':count,'sourceHashesChecked':len(manifest['sources']),'markdownLinksChecked':links,'obviousSecretChecksPassed':True,'scope':'Curated allowlist plus pattern checks; not a claim of comprehensive secret detection.'}))"
assert s.count(anchor)==1
new='''# NSS156: actual owned TCP exit and new TCP/original UDP successor.
x156=json.loads((root/'evidence/nss156-mainline.json').read_text());rt156=json.loads((root/'evidence/current-runtime.json').read_text())
assert x156['passed'] and x156['round']==rt156['round']=='NSS156' and x156['status']=='OWNED_FLOW_EXIT_NEW_TCP_ORIGINAL_UDP_LIFECYCLE_PASSED'
assert x156['boundInputs']==rt156['boundInputs']==1909 and x156['completed20SecondSuccessorEpochs']==rt156['completed20SecondSuccessorEpochs']==1
for k in ['actualOldPairExitAndRestoration','newTcpSuccessorPassed','sameUdpSocketCtMarkNatWan','newQueryCheckpointOwnerPinsBothCis','oldGateNeverReopened','nssScopeOneTcpBulkOneUdp','otherOwnTcpSocketsClosedBeforeStage','nativeFullFactoryUnchangedFrom155','classSpecific151RetirementMustBeMergedBeforeDeployablePilot','classifierKernelGateAndQoSUnchanged','ownedSshKeepaliveOnlyChanged']:assert x156[k]
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
assert proof156['sources']==x156['exportedSources']==90 and len(manifest['sources'])>=2520
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
f156=json.loads((root/'evidence/nss156-failures.json').read_text());assert len(f156)==x156['failuresPreserved']==8
for f in f156[:6]:assert not f['passed'] and not f['routerCheckpointOrNssStageStarted'] and f['originalErrorAndSourcesPreserved'] and not f['rootCauseOfNetworkTimeoutProven']
assert f156[6]['refusedBeforeRouterConnect'] and f156[6]['oldSourceRetained'] and f156[6]['correctedOnlyNamespace'] and f156[6]['analysisRanOnlyAfterRepair']
assert f156[7]['failedBeforeGitWorkspaceMutation'] and f156[7]['submissionChainStoppedBeforeCommit'] and f156[7]['originalSourcePreserved'] and f156[7]['onlyProofFileExtensionsCorrected']
d156=json.loads((root/'evidence/nss156-software-preparation.json').read_text());assert len(d156)==6 and all(d['noNssStage'] and d['causeNotProven'] for d in d156)
assert d156[-1]['seconds']>=80 and d156[-1]['serverConfirmedBytes']>260000000 and not d156[-1]['clientErrors']
for field,file,rtfield in [('finalAudit','final-audit','audit'),('physicalRestore','physical-final','physicalRootRestoreAudit'),('endpointClosure','endpoint-client-closure','endpointClientClosureAudit')]:assert x156[field]==json.loads((root/f'evidence/nss156-{file}.json').read_text())==rt156[rtfield]
for k in ['passed','originalFullLockedNativeAudit','unrelatedConfigurationMatches','exactWan4AutomaticFailoverProved','ecmStoppedAndZero','noActiveTransaction','noStaging','noExperimentState','noExperimentalModule']:assert rt156['audit'][k]
assert rt156['audit']['queryAge']<6 and rt156['audit']['nativeDynamicSelectorsVerifiedByOriginalOwnershipAudit'] and not rt156['audit']['wan4Up']
assert rt156['physicalRootRestoreAudit']['physicalWanOriginalMqFourFqCodelRestored'] and rt156['physicalRootRestoreAudit']['lan4OriginalMqFourFqCodelRestored'] and rt156['physicalRootRestoreAudit']['defaultQueueOptionsAndHandlesExact']
end156=rt156['endpointClientClosureAudit'];assert end156['passed'] and end156['previousLoadsChecked']==end156['ownedUnitsInactiveMainPidZero']==34 and end156['temporaryFirewallRulesRemaining']==end156['ownedClientOrGuardProcessesRemaining']==0
assert end156['tcpAndUdpPortsClosed'] and end156['allCanonicalFirewallBaselinesMatch'] and not end156['remoteWrites'] and not end156['productionWrites']
for k,file in [('ownedReceiverClosureAudit','receiver-closure'),('ownedDownloadReceiverClosureAudit','download-receiver-closure')]:assert rt156[k]==json.loads((root/f'evidence/nss156-{file}.json').read_text()) and rt156[k]['passed'] and rt156[k]['exactOwnedReceiverAndTimeoutProcessesRemaining']==0
assert manifest['lastAppendExport']=='NSS156'
'''
s=s.replace(anchor,new+'\n'+anchor);p.write_text(s,encoding='utf-8')
attrs=w/'athena-nss-mainline/.gitattributes';a=attrs.read_text(encoding='utf-8')
a+='\n# Preserve the exact inherited NSS156 guardian/native and archived NSS155 runtime.\n/code/work/nss156/endpoint-firewall-guardian.py whitespace=cr-at-eol,-blank-at-eof\n/code/work/nss156/fast-path.lua whitespace=cr-at-eol,-blank-at-eol\n/evidence/nss155-runtime.json -text\n';attrs.write_text(a,encoding='utf-8')
print('NSS155 runtime separated; actual NSS156 lifecycle scope and failures checked.')
