from pathlib import Path
w=Path(__file__).resolve().parents[3];p=w/'athena-nss-mainline/tools/check_repository.py';s=p.read_text(encoding='utf-8')
old="x153=json.loads((root/'evidence/nss153-mainline.json').read_text());rt153=json.loads((root/'evidence/current-runtime.json').read_text())"
assert s.count(old)==1;s=s.replace(old,old.replace("evidence/current-runtime.json","evidence/nss153-runtime.json"))
anchor="print(json.dumps({'passed':True,'filesChecked':count,'sourceHashesChecked':len(manifest['sources']),'markdownLinksChecked':links,'obviousSecretChecksPassed':True,'scope':'Curated allowlist plus pattern checks; not a claim of comprehensive secret detection.'}))"
assert s.count(anchor)==1
new='''# NSS154: direct finite supervisor terminated, reconstructed from disk journal.
x154=json.loads((root/'evidence/nss154-mainline.json').read_text());rt154=json.loads((root/'evidence/current-runtime.json').read_text())
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
'''
s=s.replace(anchor,new+'\n'+anchor);p.write_text(s,encoding='utf-8')
attrs=w/'athena-nss-mainline/.gitattributes';a=attrs.read_text(encoding='utf-8');a+='\n# Preserve exact inherited guardian and archived NSS153 runtime bytes.\n/code/work/nss154/endpoint-firewall-guardian.py whitespace=cr-at-eol,-blank-at-eof\n/evidence/nss153-runtime.json -text\n';attrs.write_text(a,encoding='utf-8')
print('Historical NSS153 runtime redirected to its exact archive; NSS154 checker appended.')
