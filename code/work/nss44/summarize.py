"""NSS44 failed real admission and read-only follow-up; no raw endpoint export."""
import json,hashlib,sys,statistics,shutil
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,'work/nss43');from load_model import cpu_delta,softnet_totals
r=Path('work/nss44');attempt=Path('work/nss42/real-matched-aba-20261004023857-0c4f4549')
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
selected=read(attempt/'selected-preaudit-private.json');result=read(attempt/'result.json');assert result['passed'] is False
manifest=read(attempt/'source-manifest-preaudit.json');assert len(manifest)==102
assert all(sha(attempt/'frozen'/p)==v and sha(p)==v for p,v in manifest.items())
assert not any((attempt/name).exists() for name in ('stage-receipt-private.json','stage-plan-private.json','selected-private.json'))
application=read(attempt/'application-preaudit/real-reader-qualified.json')
alignment=read('work/nss42/'+attempt.name+'-before-alignment-private.json');rows=alignment['rejectedPolls'];assert not alignment['passed'] and not alignment['nssAdmissionAllowed']
opening=read(r/'opening-diagnostic-audit-private.json');assert not opening['passed']
pub=read(r/'publication-private.json');a,b=pub['telemetry'];duration=b['uptime']-a['uptime'];sn0,sn1=softnet_totals(a['softnet']),softnet_totals(b['softnet'])
performance=cpu_delta(a['cpu'],b['cpu'])|{'seconds':duration,'lan4DownMbps':(b['txBytes']-a['txBytes'])*8/duration/1e6,
 'lan4DownPps':(b['txPackets']-a['txPackets'])/duration,'timeSqueezeDelta':sn1[1]-sn0[1]}
updates={}
for name,values in pub['updates'].items():
 updates[name]=[{'relativeObservedSeconds':p['observed']-a['uptime'],'sequence':p['sequence'],'readSeconds':p['readSeconds'],
  'publicationDelay':p['published']-p['queryStart'],'querySeconds':p['queryFinished']-p['queryStart'],'flowCount':p['flows'],'bytes':p['bytes']} for p in values]
timing={'readonly':True,'routerConfigurationWrites':False,'syntheticTrafficGenerated':False,'nssOpened':False,'observerCpuSeconds':pub['observerCpuSeconds'],
 'performance':performance,'updates':updates,
 'frames':[{'relativeSeconds':p['at']-a['uptime'],**{k:p[k] for k in ('compactSequence','compactAge','fullSequence','fullAge','guardianHealthy')}} for p in pub['frames']],
 'actualApplicationOwnershipNotCheckedDuringPassiveWindow':True,'notRealMatchedGamePerformance':True}
save(r/'publication-timing-sanitized.json',timing)
producerAliases={};sanitizedRows=[]
for row in rows:
 seq=row['sequence'];sanitizedRows.append({'relativeSeconds':row['at']-alignment['startedAt'],'sourceSequence':seq,'sourceAge':row['sourceAge'],'publicationAge':row['publicationAge'],
  'queryToPublishSeconds':row['published']-row['queryStart'],'healthy':row['healthy']})
save(r/'failed-admission-timing-sanitized.json',{'passed':False,'seconds':alignment['finishedAt']-alignment['startedAt'],
 'rows':sanitizedRows,'routerConfigurationWrites':False,'nssAdmissionAllowed':False,'lockHeld':False})
final=read(r/'final-audit.json');inspection=read(r/'classifier-final-inspection.json');files=inspection['files'];initial=read(r/'classifier-opening-inspection.json')['files']
log=(r/'classifier-service-log-private.txt').read_text();assert 'Classifier snapshot stale before write' in log and 'exactRecovery=false' in log
candidate=read(r/'candidate-prewrite-audit.json');candidateAlignment=read(r/'candidate-prewrite-alignment-private.json');local=read(r/'candidate-local-qualified.json');bench=read(r/'hash-benchmark.json')
original=statistics.mean(x['seconds'] for x in bench['rows'] if x['mode']=='individual');batch=statistics.mean(x['seconds'] for x in bench['rows'] if x['mode']=='batch')
names=['audit-renderer.mjs','current-audit-diagnostic.mjs','inspect-classifier.mjs','final-closure.mjs','session-binding.mjs','read-classifier-log.mjs','observe-publication.mjs',
 'hash-batch.lua','build-hash-candidate.py','candidate-worker.lua','benchmark-hash-readonly.mjs','wait-ready-candidate.mjs','candidate-audit-readonly.mjs','test_candidates.py','summarize.py','render_report.py']
sources={str(r/name).replace('\\','/'):sha(r/name) for name in names};frozen=r/'readonly-frozen';frozen.mkdir(exist_ok=False)
for name in names:shutil.copyfile(r/name,frozen/name)
save(r/'readonly-source-proof-private.json',{'sourceHashes':sources,'frozenSourceFiles':len(names),'candidateOnly':True,'productionEntryQualified':False,
 'actualAttemptDirectory':str(attempt).replace('\\','/'),'actualAttemptBoundSourceFiles':102,'originalQualificationStillUnmodified':True})
out={'round':'NSS44','updatedAt':datetime.now(timezone.utc).isoformat(),'deploymentReference':'work/nss39/deployment-latest.json',
 'classifierConfigSha256':read('work/nss39/deployment-latest.json')['configHash'],'permanentClassifierChanged':False,'routerConfigurationWrites':False,
 'originalNss42EntryUnmodified':True,'budgetMbps':20,'gateFlows':{'tcp':1,'udp':1},'ownerDeadlineSeconds':45,
 'actualAttempt':{'attempted':True,'realApplicationPairFound':True,'actualGameCandidates':application['actualCs2RtCandidates'],'actualSteamBulkCandidates':application['actualSteamBulkCandidates'],
  'selectedWan':selected['tcp']['wan'],'fullTcpMark':selected['tcp']['mark'],'fullUdpMark':selected['udp']['mark'],'sameNat':selected['tcp']['reply']['dst']==selected['udp']['reply']['dst'],
  'zoneZero':selected['tcp']['zone']==selected['udp']['zone']==0,'originalControllerTerminalPassed':False,'boundSourceFilesFrozen':102,'originalFailurePreserved':True,
  'rejectedBeforeCheckpointOrStaging':True,'prewriteAlignmentFailed':True,'alignmentSeconds':alignment['finishedAt']-alignment['startedAt'],'alignmentPolls':len(rows),
  'fullSourceSequencesObserved':sorted(set(x['sequence'] for x in rows)),'fullPublicationDelays':sorted(set(round(x['published']-x['queryStart'],3) for x in rows)),
  'sourceAgeRangeSeconds':[min(x['sourceAge'] for x in rows),max(x['sourceAge'] for x in rows)],'everyPollHealthy':all(x['healthy'] for x in rows),
  'checkpointCreated':False,'independentExperimentOwnerStarted':False,'productionMutationAttempted':False,'wanChanged':False,'nssQdiscCreated':False,'packetTagsInstalled':False,
  'gateModuleLoaded':False,'ecmOpened':False,'forwardingABACompleted':False,'nativeFastPathAffinityVerified':False,'leafCounters':None,'gameTelemetry':None},
 'openingAuditFailure':{'originalAssertionRetained':True,'sourceAgeSeconds':opening['diagnostic']['freshness']['sourceAge'],'sourceAgeLimitSeconds':6,
  'publicationAgeSeconds':opening['diagnostic']['freshness']['publicationAge'],'stage':'Original complete locked freshness predicate'},
 'classifierRestart':{'observed':True,'injectionOrManualRestart':False,'configChanged':False,'sameProducerSinceOpening':False,
  'newProducerHealthy':files['classification.json']['dataHealthy'] and files['guardian.json']['healthy'],
  'sameNewProducerSincePostrefusalInspection':files['classification.json']['producer']==read(r/'classifier-postrefusal-inspection.json')['files']['classification.json']['producer'],
  'loggedCause':'Classifier snapshot stale before write; apply rawStatus 256, wall time 3.79 seconds',
  'staleFailureLogBeijing':'2026-10-04 10:41:17','mutationFailureLogBeijing':'2026-10-04 10:41:23',
  'firstExactRecoveryPassed':False,'recoveryRawStatus':31744,'recoverySeconds':6.18,'oldFailureRetained':True,
  'finalExactOwnedAuditPassed':final['exactOwnedNativeAudit'],'restartCausationByNssExperimentProved':False,'fullHighLoadLifecycleQualified':False},
 'passiveFollowup':{'seconds':duration,'frames':len(pub['frames']),'observerCpuSeconds':pub['observerCpuSeconds'],'performance':performance,
  'compactPublicationDelayRangeSeconds':[min(x['publicationDelay'] for x in updates['classification']),max(x['publicationDelay'] for x in updates['classification'])],
  'fullPublicationDelayRangeSeconds':[min(x['publicationDelay'] for x in updates['snapshot']),max(x['publicationDelay'] for x in updates['snapshot'])],
  'completeFlowCountRange':[min(x['flowCount'] for x in updates['snapshot']),max(x['flowCount'] for x in updates['snapshot'])],
  'naturalLightLoad':True,'actualApplicationPairNotConfirmed':True,'syntheticTrafficGenerated':False,'notMatchedForwardingABA':True},
 'readonlySchedulingCandidate':{'installedOrUsedForProduction':False,'productionEntryQualified':False,'originalFullAuditRetained':True,'originalSchedulerLibraryUnchanged':True,
  'change':'Wait on existing before-software-baseline classification publication; afterward execute original complete locked snapshot/native audit',
  'ageLimitsUnchanged':{'schedulingHintSeconds':2,'lockedSourceSeconds':6,'lockedPublicationSeconds':9,'initialLearningSeconds':1,'prelearningSeconds':2},
  'boundsUnchanged':{'innerWaitSeconds':5,'outerWaitSeconds':6,'ownerSeconds':45},
  'nativeReadonlyAuditPassed':candidate['passed'],'nativeReadonlyEcmClosedAndZero':candidate['ecmClosedAndZero'],'nativeReadonlyAdmissionAllowed':candidate['nssAdmissionAllowed'],
  'nativeReadonlyFullAuditQueryAge':candidate['queryAge'],'nativeHintSourceAge':candidateAlignment['alignment']['sourceAge'],
  'highLoadNssProof':False,'fixesClassifierApplyOrRecoveryTimeout':False},
 'hashCandidate':{'installed':False,'allPayloadsStillCheckedEveryInvocation':True,'payloadCount':12,'hashesCached':False,
  'nativeReadOnlyPairs':3,'individualMeanMs':original*1000,'batchMeanMs':batch*1000,'savedMeanMs':(original-batch)*1000,
  'backgroundLan4Mbps':bench['backgroundLan4Mbps'],'hashChildCpuNotCounted':True,'resolvedPublicationDelay':False,'lifecycleUnchanged':True},
 'localChecks':{'passed':local['passed'],'checks':local['checks'],'routerAccess':False,'scope':local['scope'],'productionEntryQualified':False},
 'sourceProof':{'sources':len(names),'sourceHashes':sources,'readonlyOrUninstalledCandidatesOnly':True,'credentialsAndRawCapturesNotExported':True},
 'finalState':{'protectedAudit':{k:final[k] for k in ('passed','protectedConfigurationUnchanged','exactOwnedNativeAudit','ecmClosedAndZero')},
  'classifierHealthy':files['classification.json']['dataHealthy'] and files['guardian.json']['healthy'],'sameProducerSinceOpening':False,
  'lastErrorIsThisRoundsRestart':True,'closure':read(r/'final-closure.json')},
 'conclusions':{'realPairFound':True,'newNssFastPathTrialExecuted':False,'nssCpuBenefitProvedThisRound':False,'cs2JitterLossMissCaptured':False,
  'classifierHighLoadStable':False,'publishingSourceMismatchExplainsAdmissionRefusalMechanism':True,'readinessCandidateProvedUnderHighLoad':False,
  'completeHighLoadLoopPassed':False,'secondWanExpansionAllowed':False},
 'next':'First qualify the correct publication source and restore reliable classifier apply/recovery within existing deadlines. Bind a new production entry before one future concentrated real window. Do not ask user to keep gaming or downloading for preparation.',
 'reportVerification':{'sourceValidated':False,'browserRendered':False,'reason':'Existing local-browser rendering policy block retained; no workaround attempted'}}
save('outputs/nss44-mainline-observations.json',out)
print(json.dumps({'saved':True,'realAttemptRefusedBeforeWrites':True,'restartObserved':True,'candidateChecks':30,'frozenSources':len(names),'routerConfigurationWrites':False}))
