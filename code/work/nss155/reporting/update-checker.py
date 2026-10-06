from pathlib import Path
w=Path(__file__).resolve().parents[3];p=w/'athena-nss-mainline/tools/check_repository.py';s=p.read_text(encoding='utf-8')
old="x154=json.loads((root/'evidence/nss154-mainline.json').read_text());rt154=json.loads((root/'evidence/current-runtime.json').read_text())";assert s.count(old)==1;s=s.replace(old,old.replace('evidence/current-runtime.json','evidence/nss154-runtime.json'))
anchor="print(json.dumps({'passed':True,'filesChecked':count,'sourceHashesChecked':len(manifest['sources']),'markdownLinksChecked':links,'obviousSecretChecksPassed':True,'scope':'Curated allowlist plus pattern checks; not a claim of comprehensive secret detection.'}))";assert s.count(anchor)==1
new='''# NSS155 proves whole-pair flow exit only; all successor failures preserved.
x155=json.loads((root/'evidence/nss155-mainline.json').read_text());rt155=json.loads((root/'evidence/current-runtime.json').read_text())
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
f155=json.loads((root/'evidence/nss155-failures.json').read_text());assert len(f155)==4 and x155['failuresPreserved']==4
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
'''
s=s.replace(anchor,new+'\n'+anchor);p.write_text(s,encoding='utf-8')
attrs=w/'athena-nss-mainline/.gitattributes';a=attrs.read_text(encoding='utf-8');a+='\n# Exact inherited guardian and archived NSS154 runtime bytes.\n/code/work/nss155/endpoint-firewall-guardian.py whitespace=cr-at-eol,-blank-at-eof\n/evidence/nss154-runtime.json -text\n';attrs.write_text(a,encoding='utf-8')
print('NSS154 runtime preserved independently; NSS155 partial-scope checks appended.')
