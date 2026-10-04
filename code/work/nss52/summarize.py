"""Explicit sanitized projections. Never exports raw snapshots, sockets or screenshots."""
import hashlib,json
from pathlib import Path
from datetime import datetime,timezone
root=Path(__file__).resolve().parents[2]
def read(path):return json.loads((root/path).read_text(encoding='utf-8-sig'))
def save(path,value):
    with (root/path).open('x',encoding='utf-8',newline='\n')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
def sha(path):return hashlib.sha256((root/path).read_bytes()).hexdigest()
cases=[('nss49','20261004081047-630838a7','selected-class-not-admitted'),('nss49','20261004081723-2112487f','locked-source-age-6.47s'),('nss49','20261004082036-376a3195','historical-service-pid-baseline'),('nss50','20261004083435-f36f1fcc','core-sleep-deadline'),('nss50','20261004083901-c4b7888d','core-sleep-deadline'),('nss51','20261004091358-67970a14','selected-class-not-admitted')]
attempts=[]
for number,(round,ident,reason)in enumerate(cases,1):
    directory=f'work/{round}/real-matched-aba-{ident}'
    result=read(directory+'/result.json');assert not result['passed'] and not result['matchedForwardingABACompleted']
    record=read(directory+'/last-record-private.json')if(root/directory/'last-record-private.json').exists()else{}
    assert record.get('newNssPermit')is not True
    staged=(root/directory/'stage-undo-verified.json').exists()
    row={'attempt':number,'entryRound':round.upper(),'case':f'real-matched-aba-{ident}','passed':False,'failure':reason,'checkpointAndTemporaryStageCreated':staged,'productionTemporaryStageOccurred':staged,'ecmPermitOpened':False,'forwardingABACompleted':False,'completedPhases':['A']if number in (4,5)else[],'phasesBAndA2Missing':True,'retrospectiveSelectedFlowCauseProven':False}
    if staged:
        undo=read(directory+'/stage-undo-verified.json');after=read(directory+'-after-audit.json');assert all(undo.values())and after['passed']and after['protectedConfigurationUnchanged']and after['ecmClosedAndZero']
        row.update({'independent45SecondRollbackVerifiedBeforeWrite':True,'checkpointHashAndGzipVerified':True,'rollbackPassed':True,'stageCleanupPassed':True,'afterFullProtectedAuditPassed':True,'natural45SecondNssExpiryProvedThisCase':False,'qosRestored':record.get('qosRestored') is True})
        alignment=record.get('initialAlignment')or{}
        row['initialAdmissionDiagnostic']={'probes':len(alignment.get('probes',[])),'seconds':alignment.get('stop',0)-alignment.get('start',0),'sourceAgeSeconds':((alignment.get('diagnostics')or[{}])[-1].get('adapter')or{}).get('sourceAge')}
    else:row.update({'rejectedBeforeCheckpointOrStaging':True,'routerConfigurationWrites':False,'rollbackRequired':False})
    attempts.append(row)
assert sum(x['productionTemporaryStageOccurred']for x in attempts)==4
overlay=read('work/nss50/entry-overlay-qualified.json');phase51=read('work/nss51/phase-qualified.json');entry51=read('work/nss51/entry-qualified.json');phase52=read('work/nss52/phase-qualified-sanitized.json')
groups=[]
for name in ['paused-exact','download-exact','candidate-paused','candidate-download']:
    trace=read('work/nss51/'+name+'-exact-private.json');rows=[]
    for a in trace['attempts']:
        rows.append({'passed':a['passed'],'seconds':a['seconds'],'scans':len(a['rows']),'maximumScanSeconds':max(x['scanSeconds']for x in a['rows']),'maximumConsumerSeconds':max(x.get('observationSeconds',0)for x in a['rows']),'newChildObservations':[{'birthAgeSeconds':x['birthAge'],'scanSeconds':x['scanSeconds'],'priorGapSeconds':x.get('priorGap')}for x in a['rows']if x.get('changed')]})
    groups.append({'name':name,'passedAttempts':sum(x['passed']for x in rows),'attempts':rows})
assert [x['passedAttempts']for x in groups]==[3,0,3,1]
timing={'readonly':True,'ecmClosedThroughout':True,'guardUntouched':True,'consumerCandidatesPathExecuted':True,'unusedAdapterFunctionsOmittedOnlyInReadonlyProfiler':True,'phaseCommentsOmittedOnlyInReadonlyProfiler':True,'offeredLoadEqualityNotProven':True,'groups':groups}
save('work/nss52/trace-summary-v2-sanitized.json',timing)
ctx=read('work/nss47/deployment-latest.json');final=read('work/nss51/final-post-game-audit.json');closure=read('work/nss50/final-post-game-cleanup-audit.json')
owned=read('work/nss51/final-post-game-ownership-private.json');prior_owned=read('work/nss49/post-game-exit-ownership-private.json')
same_worker=all(owned[k]==prior_owned[k]for k in ['pid','guardianPid','producer'])
assert final['passed']and closure['passed']and final['ecmClosedAndZero']and same_worker
partial=read('work/nss50/partial-a-sanitized.json');client=read('work/nss50/client-reviewed-sanitized.json')
data={'round':'NSS50–NSS52','observedAt':datetime.now(timezone.utc).isoformat(),'deploymentReference':'work/nss47/deployment-latest.json','classifierConfigSha256':ctx['configHash'],'permanentClassifierChanged':False,'qualifiedExperimentalEntry':'work/nss51/real-session.mjs','uninstalledNextCandidate':'work/nss52/core-guard-phase.lua','ecmOpenedThisTurn':False,'forwardingABACompletedThisTurn':False,'budgetMbps':20,'gateFlows':{'tcp':1,'udp':1},'ownerSeconds':45,'allOriginalDeadlinesUnchanged':True,'attempts':attempts,'partialSoftwareMeasurements':partial,'clientSoftwareMeasurements':client,
 'serviceEpochFix':{'localBoundaryCases':24,'entryBoundInputs':128,'preExperimentHealthyCoreGuardPidOnlyDriftAccepted':True,'sameCommandsAndRunningStateRequired':True,'allDuringExperimentServiceChangesRejected':True,'nativeFullReadonlyAuditPassed':read('work/nss50/overlay-readonly-audit.json')['passed'],'classifierNativeOwnershipAuditRetained':True,'causeOfHistoricalPidChangeProven':False},
 'phase51':{'sourceSha256':phase51['sourceSha256'],'originalSourceSha256':phase51['originalSourceSha256'],'reusedProcessModelCases':22,'liveReadonlyPhases':2,'entryBoundInputs':140,'onlyPinnedGuardChildDiscoveryChanged':True,'waitFreshByteIdentical':True,'nativeFullReadonlyEntryAuditPassed':read('work/nss51/nss51-readonly-entry-audit.json')['passed'],'highLoadReadOnlySuccesses':1,'highLoadReadOnlyAttempts':3,'highLoadReliablyFixed':False,'forwardingSucceededThisEntry':False},
 'readonlyProfiling':timing,'phase52UninstalledCandidate':phase52,
 'clientEndState':{'steam':read('work/nss50/client-download-final-sanitized.json'),'cs2':read('work/nss50/hud-settings-restored.json'),'screenshotsAndRawIdentitiesExported':False,'humanGameplay':False,'newPurchase':False,'doomLaunched':False},
 'finalState':{'protectedAudit':final,'closure':closure,'sameCacheRetainedWorker':same_worker,'servicePidEpochUnchangedDuringExperiments':True,'nssPermanentlyEnabled':False},
 'conclusions':{'historical49FunctionProofStillValid':True,'actualSoftwareClientHudCaptured':True,'nssBClientHudCapturedThisTurn':False,'softwareVersusNssCpuBenefitProvedThisTurn':False,'realHumanExperienceProved':False,'highLoadPhaseFixValidated':False,'secondWanExpansionAllowed':False,'sharedBudgetAllowed':False,'upstreamSubmitted':False},
 'nextAction':'Qualify efficient process discovery under the next real download window, preserve selected-flow continuity, then run one same-load software→NSS→software comparison with actual client HUD; do not repeat classifier installation prep.',
 'reportVerification':{'sourceValidated':False,'browserRendered':False}}
save('outputs/nss52-mainline-observations.json',data)
save('outputs/nss50-mainline-observations.json',{'round':'NSS50','attempts':attempts[:5],'serviceEpochFix':data['serviceEpochFix'],'partialSoftwareMeasurements':partial,'clientSoftwareMeasurements':client,'ecmOpened':False,'forwardingABACompleted':False})
save('outputs/nss51-mainline-observations.json',{'round':'NSS51','phase':data['phase51'],'readonlyProfiling':timing,'attempt':attempts[-1],'ecmOpened':False,'forwardingABACompleted':False})
print(json.dumps({'sanitized':True,'attempts':len(attempts),'temporaryStagingCases':4,'phase51HighLoadPassed':1,'phase51HighLoadAttempts':3,'finalAuditPassed':True,'sameWorker':same_worker,'ecmOpened':False}))
