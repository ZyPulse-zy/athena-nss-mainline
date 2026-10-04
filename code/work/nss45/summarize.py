"""Separate native child proofs, temporary trials, mocks, and final runtime."""
import json,hashlib,statistics,sys,shutil
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,'work/nss43');from load_model import cpu_delta,softnet_totals
r=Path('work/nss45')
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
names=['audit-renderer.mjs','current-audit-diagnostic.mjs','final-closure.mjs','inspect-classifier.mjs','session-binding.mjs','read-classifier-log.mjs','read-real-candidates.mjs',
 'build-row-candidate.py','original-worker.lua','original-guardian.lua','original-conntrack-source.lua','worker.lua','guardian.lua','conntrack-source.lua','test-row-candidate.py','row-replay.lua','check-row-native.mjs',
 'build-recovery-candidate.py','original-backend.lua','candidate-backend.lua','test-recovery-candidate.py','recovery-fixtures.lua','benchmark-recovery-readonly.mjs',
 'build-stale-candidate.py','stale-worker.lua','stale-guardian.lua','test-stale-candidate.py','stale-replay.lua','prepare-stale-native.py','check-stale-native.mjs','stale-native-patches.json',
 'prepare-backend-trial.py','upgrade-backend.mjs','prepare-trial-observers.py','audit-backend-trial.mjs','observe-backend-trial.mjs','verify-backend-rollback.mjs',
 'build-query-cleanup-replay.py','query-cleanup-replay.lua','check-query-cleanup-native.mjs','prepare-row-trial.py','upgrade-row.mjs','audit-row-trial.mjs','observe-row-trial.mjs','verify-row-rollback.mjs','closure-backend.mjs',
 'test-expiry-journal.py','expiry-journal-replay.lua','prepare-expiry-journal-native.py','expiry-journal-native.lua','check-expiry-journal-native.mjs','summarize.py','render_report.py']
row=read(r/'row-qualified.json');stale=read(r/'stale-qualified.json');backend=read(r/'recovery-qualified.json');joint=read(r/'expiry-journal-qualified.json')
assert row['passed']and row['checks']==48 and stale['passed']and stale['checks']==34 and joint['passed']and joint['checks']==8
assert backend['passed']and len(backend['results'])==2 and all(x['checks']==24 and x['passed']for x in backend['results'])
trials=[];timing={}
for kind in ['backend','row']:
 ctx=read(r/(kind+'-trial')/'deployment-latest.json');path=Path(ctx['localDir']);arm=read(path/'armed-proof.json');checkpoint=read(path/'checkpoint.json');rollback=read(path/'rollback-qualified.json');audit=read(path/'active-audit.json')
 obs=read(r/(kind+'-trial-active-observation.json'));rows=obs['rows'];a,b=rows[0],rows[-1];seconds=b['uptime']-a['uptime'];sn0,sn1=softnet_totals(a['softnet']),softnet_totals(b['softnet'])
 assert arm['passed']and arm['independentOfSsh']and checkpoint['gzipVerified']and rollback['passed']and rollback['automaticExpiryWithoutControllerRollback']
 assert rollback['previousBackendRestored']and audit['passed']and audit['protectedConfigurationUnchanged']and audit['exactOwnedNativeAudit']and audit['ecmClosedAndZero']
 assert len(rows)==35 and all(x['guardianHealthy']and x['status']=='running'and x['accel']==0 and x['frontend']==1 for x in rows)
 assert len({x['producer']for x in rows})==1 and obs['semantic']['passed']
 expectedOld=read('work/nss39/deployment-latest.json')['configHash'];assert ctx['previous']['configHash']==expectedOld and not ctx['committed']
 changed=[n for n,h in read(path/'config.json')['files'].items()if h!=read(Path(ctx['previous']['localDir'])/'config.json')['files'][n]]
 assert sorted(changed)==(['backend.lua']if kind=='backend'else['conntrack-source.lua','guardian.lua','worker.lua'])
 performance=cpu_delta(a['cpu'],b['cpu'])|{'seconds':seconds,'lan4DownMbps':(b['txBytes']-a['txBytes'])*8/seconds/1e6,'lan4DownPps':(b['txPackets']-a['txPackets'])/seconds,'timeSqueezeDelta':sn1[1]-sn0[1],'softnetDroppedDelta':sn1[0]-sn0[0],'containsObserverOverhead':True}
 timing[kind]={'frames':[{'relativeSeconds':x['uptime']-a['uptime'],'age':x['age'],'sourceSequence':x['sequence'],'status':x['status'],'guardianHealthy':x['guardianHealthy'],'acceleratedCount':x['accel']}for x in rows],'performance':performance,'notForwardingABA':True,'sameOfferedLoadProved':False}
 trials.append({'kind':kind,'changedSources':changed,'checkpointDownloadedHashAndGzipVerified':True,'independentRollbackVerifiedBeforeProductionWrite':True,'independentOfControlConnection':True,'automaticExpirySeconds':180,
  'stageAutomaticExpirySeconds':480,'committed':False,'nssEnabled':False,'activeWindow':{'samples':35,'allHealthy':True,'oneProducer':True,'performance':performance,'semanticProjectionVerified':True,'heuristicSoftwareVerifiedRt':obs['semantic']['softwareVerifiedRt'],'actualCs2Observed':False},
  'activeOriginalCompleteProtectionAuditPassed':True,'originalAgeAndPermissionPredicatesRetained':True,'automaticRollback':{k:rollback[k]for k in ['passed','observedAt','independent180SecondRollback','automaticExpiryWithoutControllerRollback','previousWorkerAndConfigRestored','previousNormalizerAndGuardianRestored','previousBackendRestored','previousClassifierHealthyAndFresh','sourceAge','ecmClosedAndZero']},
  'predeadlineFailClosedExitExpectedAndObserved':True,'full180SecondContinuousHealthNotClaimed':True,'realOverloadOrStaleSoftwareFaultInjected':False,'highLoadLifecycleQualified':False})
save(r/'trial-timing-sanitized.json',timing)
bench=read(r/'recovery-readonly-qualified.json');original=statistics.mean(x['seconds']for x in bench['rows']if x['method']=='original');candidate=statistics.mean(x['seconds']for x in bench['rows']if x['method']=='candidate')
assert bench['passed']and bench['pairs']==3 and all(x['routerWrites']==False and x['projectedEmptyJournal']and not x['nativeSelectorsRecovered']for x in bench['rows'])
initial=read(r/'classifier-opening-inspection.json')['files'];final=read(r/'classifier-final-inspection.json');files=final['files'];audit=read(r/'final-audit.json');closure=read(r/'final-closure.json');app=read(r/'final-app/real-reader-qualified.json')
assert all(audit[k]for k in ['passed','protectedConfigurationUnchanged','exactOwnedNativeAudit','ecmClosedAndZero'])and closure['passed']
assert files['classification.json']['status']=='running'and files['guardian.json']['healthy']and files['classification.json']['dataHealthy']
assert 'Installation rollback deadline reached'in files['last-error.json']['error']and files['last-error.json']['producer']!=files['classification.json']['producer']
assert 'Source rows exceed bound'in initial['last-error.json']['error']
log=(r/'classifier-final-log-private.txt').read_text();assert all('sh['+str(pid)+']'in log and 'Source rows exceed bound'in log for pid in [13248,1428,3084])
assert log.count('Installation rollback deadline reached')>=4
rowNative=read(r/'row-native-replay-qualified.json');staleNative=read(r/'stale-native-replay-qualified.json');query=read(r/'query-cleanup-native-qualified.json');jointNative=read(r/'expiry-journal-native-qualified.json')
assert all(x['passed']for x in [rowNative,staleNative,query,jointNative])and query['checks']==7 and jointNative['checks']==8
sources={str(r/name).replace('\\','/'):sha(r/name)for name in names};frozen=r/'source-frozen';frozen.mkdir(exist_ok=False)
for name in names:shutil.copyfile(r/name,frozen/name)
save(r/'source-proof-private.json',{'sourceHashes':sources,'frozenSourceFiles':len(names),'nssProductionEntryQualified':False,'temporaryClassifierTrialsOnly':True,'originalNss42EntryUnmodified':True})
out={'round':'NSS45','updatedAt':datetime.now(timezone.utc).isoformat(),'deploymentReference':'work/nss39/deployment-latest.json','classifierConfigSha256':read('work/nss39/deployment-latest.json')['configHash'],
 'permanentClassifierChanged':False,'routerConfigurationWrites':True,'nssOpened':False,'originalNss42EntryUnmodified':True,'budgetMbps':20,'gateFlows':{'tcp':1,'udp':1},'ownerDeadlineSeconds':45,
 'openingObservation':{'naturalPriorWorkerExitsObserved':3,'exitLogTimesBeijing':['2026-10-04 11:07:30','2026-10-04 11:08:02','2026-10-04 11:08:10'],'cause':'Untyped Source rows exceed bound at existing 2048-row cap','manualRestartOrFaultInjection':False,'originalProtectedAuditPassed':read(r/'opening-audit.json')['passed']},
 'recoveryReadReuse':{'originalEmptyReadCalls':60,'candidateEmptyReadCalls':40,'nativeReadonlyPairs':3,'originalMeanSeconds':original,'candidateMeanSeconds':candidate,'wallTimeReductionPercent':(original-candidate)*100/original,
  'actualNativeQueueStateRead':True,'journalProjectedEmptyInRam':True,'nativeSelectorsRecoveredDuringBenchmark':False,'nativeWritesDeniedByCallback':True,'onlyInitialEnumerationReused':True,'freshPrewriteAndPostwriteChecksRetained':True,'cacheDisabledAfterFirstWrite':True,'tcChildCpuExcludedFromObserverCpu':True,'doesNotProveGlobalCpuBenefit':True,'doesNotResolveHistoricalHighLoadRecoveryTimeout':True},
 'rowOverflowCandidate':{'localChecks':48,'sameNativeRamCases':48,'nativeSyntaxSources':3,'nativeRealQueryChildCases':7,'same2048RowAnd524288ByteCaps':True,'noPartialRowsAdmitted':True,'queryCleanupProofRequired':True,'exactOwnedRecoveryRequired':True,'unknownErrorsRemainTerminal':True,'temporarilyInstalledThenAutomaticallyRestored':True,'realOverloadOnProductionServiceInjected':False,'fullHighLoadLifecycleQualified':False},
 'softwareExpiryCandidate':{'localHelperCases':34,'sameNativeHelperCases':34,'nativeSyntaxSources':2,'localJournalIntegrationCases':8,'sameNativeJournalCases':8,'originalSixSecondSoftwareDeadline':True,'originalSixSecondMutationDeadline':True,'publicationAgeSeconds':9,
  'typedApplyCatchAndBoundResponse':True,'bothPublicationsWithdrawnBeforePreciseRecovery':True,'historyResetBeforeRecovery':True,'freshObservationRequiredAfterRecovery':True,'unknownWriterPreserved':True,'realQueryChildReapingProvedSeparately':True,'realApplyChildAndServiceFaultRecoveryQualified':False,'installed':False,'finalCombinedCandidateNotInstalled':True,'productionEntryQualified':False},
 'localChecks':{'row':48,'recoveryUniqueCases':24,'recoveryCasesExecutedOnOldAndNew':True,'softwareExpiry':34,'journalIntegration':8,'totalUniqueLocalCases':114,'scope':'Synthetic data and IO. Real source/helpers/backend/ownership algorithms; no full production child/service fault injection.'},
 'nativeChecks':{'rowCasesRepeated':48,'softwareExpiryCasesRepeated':34,'journalCasesRepeated':8,'realQueryChildCases':7,'syntaxSourceCompilations':5,'doesNotAddRepeatedCasesToLocalTotal':True,'allPassed':True},
 'temporaryClassifierTrials':trials,
 'preparationFailures':{'localRecoveryFixtureCorrections':4,'localJournalFixtureCorrections':1,'nativeSyntaxPayloadCapRefusalsBeforeConnecting':2,'localReaderOutputScopeRegexRefusalBeforeConnecting':1,'originalFailuresPreserved':True,'productionChangeFromThosePreparationFailures':False,'capsOrSafetyChecksRelaxed':False},
 'actualFastPathTrial':{'attempted':False,'gateLoaded':False,'qdiscModuleLoaded':False,'packetTagsInstalled':False,'ecmOpened':False,'nativeFastPathAffinityVerifiedThisRound':False,'leafCounters':None,'gameTelemetry':None,'steamHighLoadGenerated':False,'forwardingABACompleted':False},
 'sourceProof':{'sources':len(names),'sourceHashes':sources,'temporaryClassifierTrialsAndUninstalledCandidatesOnly':True,'nssProductionEntryQualified':False,'credentialsRawConfigsAndCheckpointsNotExported':True},
 'finalApplicationObservation':app,
 'finalState':{'observedAt':final['observedAt'],'protectedAudit':{k:audit[k]for k in ['passed','protectedConfigurationUnchanged','exactOwnedNativeAudit','ecmClosedAndZero']},'selectors':audit['selectors'],'queryAge':audit['queryAge'],'classifierHealthy':True,
  'lastErrorIsControlledTrialPredeadlineExit':True,'lastErrorBelongsToCurrentWorker':False,'earlierNaturalRowOverflowLogPreserved':True,'sameFinalProducerAsRowRollback':files['classification.json']['pid']==read(Path(read(r/'row-trial/deployment-latest.json')['localDir'])/'rollback-qualified.json')['pid'],'closure':closure},
 'conclusions':{'initialRecoveryReadDuplicationReduced':True,'rowLimitChildReapingAndTypedBoundaryProved':True,'rowTrialColdStartAndIndependentRestoreProved':True,'softwareExpiryJournalConsistencyProvedInSimulation':True,'completeSoftwareExpiryChildServiceRecoveryProved':False,'classifierHighLoadStable':False,
  'newNssFastPathTrialExecuted':False,'nssCpuBenefitProvedThisRound':False,'cs2JitterLossMissCaptured':False,'completeHighLoadLoopPassed':False,'secondWanExpansionAllowed':False},
 'next':'Qualify full apply-child/source-expiry recovery and bound lifecycle within existing deadlines, then separately integrate fixes and qualify the classification-hint/original-complete-audit entry. Do not ask user to keep gaming or downloading during preparation.',
 'reportVerification':{'sourceValidated':False,'browserRendered':False,'reason':'Existing local-file browser policy refusal retained; no workaround attempted'}}
save('outputs/nss45-mainline-observations.json',out)
print(json.dumps({'saved':True,'temporaryTrials':2,'independentExpiryRestorations':2,'uniqueLocalCases':114,'realNativeQueryChildCases':7,'frozenSources':len(names),'nssOpened':False}))
