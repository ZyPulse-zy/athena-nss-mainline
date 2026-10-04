"""Build explicit, sanitized evidence; raw sockets, CT, checkpoints remain private."""
import hashlib,json
from datetime import datetime,timezone,timedelta
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'work/nss49'
def read(path):return json.loads((ROOT/path).read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def save(path,value):
    dst=ROOT/path;dst.parent.mkdir(parents=True,exist_ok=True)
    dst.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
def pick(value,keys):return {key:value[key] for key in keys if key in value}

good='work/nss49/real-matched-aba-20261004065238-cdfa8d7a'
bad48='work/nss48/real-matched-aba-20261004064149-5a61c61c'
bad46='work/nss46/real-matched-aba-20261004060746-edfce255'
cache='work/nss47/cache-retain/nss47-retain-20261004063506-0d92279f'
record=read(good+'/last-record-private.json');result=read(good+'/result.json')
metrics=read(good+'/metrics-sanitized.json');state=read(good+'/actual-accelerated-state-proof.json')
assert result['passed'] and not result['errors'] and record['abaCompleted']
assert state['passed'] and state['connectionCount']==2 and metrics['routerRollbackVerified']
proof={kind:{key:value for key,value in row.items() if key!='serial'} for kind,row in state['proof'].items()}
for kind,tag in [('tcp',2399469568),('udp',2399535104)]:
    p=proof[kind]
    assert p['accelerated'] and p['ctMark']==131072 and p['natCorrect'] and p['wanAffinity']==2
    assert p['downTag']==tag and p['upTag']==0 and p['fromLan4'] and p['fromBridgeLan']
assert [p['acceleratedCount'] for p in metrics['phases']]==[0,2,0]
assert len(record['renewals'])==1
receipt=read(good+'/stage-receipt-private.json');undo=read(good+'/stage-undo-verified.json')
assert receipt['rollbackBeforeFirstWrite'] and receipt['success'] and receipt['parentIdentityVerified']
assert all(undo.values()) and read(good+'/stage-checkpoint-verified.json')['gzipVerified']
entry=read('work/nss49/entry-qualified.json');manifest=read(good+'/source-manifest.json')
assert len(manifest)==121
for path,expected in manifest.items():assert sha(path)==expected,(path,'Actual attempt binding drift')
for name in ['classified-tags.lua','classifier.lua','core-guard-phase.lua','qos-physical.lua','tag-normalizer.lua','wan-scope.lua','state-node.lua','module-stage-guardian.lua']:
    assert sha('work/nss49/'+name)==sha('work/nss48/'+name)
assert sha('work/nss49/fast-path.lua')==read('work/nss49/getter-delta.json')['candidateSha256']
qualified=read('work/nss49/aba-qualified.json');assert qualified['passed'] and len(qualified['cases'])==13
final=read('work/nss49/final-nss49-audit.json');closure=read('work/nss49/final-cleanup-audit.json')
assert final['passed'] and final['ecmClosedAndZero'] and final['protectedConfigurationUnchanged'] and closure['passed']
deployment=read('work/nss47/deployment-latest.json');assert deployment['committed']
assert entry['configuration']['configSha256']==deployment['configHash']
cacheProof=read('work/nss47/cache-qualified.json');nativeCache=read('work/nss47/native-cache-qualified.json')
cacheBound=read('work/nss47/cache-bound-qualified.json');cacheRollback=read('work/nss47/cache-trial/nss47-cache-20261004062759-59a8cfe0/rollback-qualified.json')
assert all(p['passed'] for p in [cacheProof,nativeCache,cacheBound,cacheRollback])
assert cacheProof['candidateSha256']==sha('work/nss47/classifier-core-cache.lua')
assert read(cache+'/permanent-commit.json')['committed'] and read(cache+'/armed-proof.json')['independentOfSsh']

anchor=read('work/nss49/clock-after-first-private.json')
def wall(uptime):return anchor['routerWallSeconds']+uptime-anchor['routerUptime']
def cst(uptime):return datetime.fromtimestamp(wall(uptime),timezone(timedelta(hours=8))).isoformat(timespec='milliseconds')
phaseWindows=[]
for phase in record['phases']:
    samples=record['samples'][phase['sampleStart']-1:phase['sampleEnd']]
    phaseWindows.append({'phase':phase['name'],'startUptime':samples[0]['uptime'],'endUptime':samples[-1]['uptime'],
       'startCst':cst(samples[0]['uptime']),'endCst':cst(samples[-1]['uptime']),'samples':len(samples)})
frames=read('work/nss49/hud-private/frames.json')
offset=anchor['routerWallSeconds']-(anchor['localRequestMs']+anchor['localReceiptMs'])/2000
def captureWall(text):return datetime.fromisoformat(text.replace('Z','+00:00')).timestamp()+offset
hudCounts={p['phase']:0 for p in phaseWindows}
for f in frames:
    for p in phaseWindows:
        if captureWall(f['beforeAt'])>=wall(p['startUptime'])+0.1 and captureWall(f['afterAt'])<=wall(p['endUptime'])-0.1:
            hudCounts[p['phase']]+=1
assert hudCounts['B']==0
second=read('work/nss49/second-attempt-readiness-private.json')
assert not second['routerWrites'] and not second['nssPermissionGranted'] and second['actualBulkCandidates']==0

failureEvidence=[]
for path,label,reason in [(bad46,'NSS46 original entry under actual applications','initial compact publication > 1 second'),(bad48,'NSS48 cache-bound entry','TCP initial tag counters all zero in the 0.3 second wait')]:
    raw=read(path+'/last-record-private.json');error=read(path+'/controller-error.json')['error'].split('\n')[0]
    after=read(path+'-after-audit.json');u=read(path+'/stage-undo-verified.json')
    assert after['passed'] and after['ecmClosedAndZero'] and all(u.values())
    failureEvidence.append({'label':label,'passed':False,'reason':reason,'error':error,'nssPermitOpened':bool(raw.get('newNssPermit',False)),
       'checkpointGzipVerified':read(path+'/stage-checkpoint-verified.json')['gzipVerified'],
       'independentRollbackVerifiedBeforeWrite':read(path+'/stage-receipt-private.json')['rollbackBeforeFirstWrite'],
       'rollbackPassed':True,'afterOriginalFullAuditPassed':True,'frozenBoundInputs':len(read(path+'/source-manifest.json'))})
    assert not failureEvidence[-1]['nssPermitOpened']
raw48=read(bad48+'/last-record-private.json')
counters={}
for obj in raw48['initialTags']['nftables']:
    if 'rule' in obj:
        for expr in obj['rule']['expr']:
            if 'counter' in expr:counters[obj['rule']['comment'].rsplit(':',1)[-1]]=expr['counter']['packets']
assert all(counters['tcp_post_'+d+'_'+field]==0 for d in ['up','down'] for field in ['total','expected','unexpected'])
assert all(counters['udp_post_'+d+'_total']>0 and counters['udp_post_'+d+'_expected']==counters['udp_post_'+d+'_total'] and counters['udp_post_'+d+'_unexpected']==0 for d in ['up','down'])
failureEvidence[-1]['initialTagPacketCounters']=counters

out={
 'round':'NSS49','coversRounds':['NSS47','NSS48','NSS49'],'generatedAt':datetime.now(timezone.utc).isoformat(),
 'deploymentReference':'work/nss47/deployment-latest.json','entryReference':'work/nss49/real-session.mjs',
 'classifierConfigSha256':deployment['configHash'],'classifierCommitted':True,'nssPermanentlyEnabled':False,
 'automaticGuiSession':{'authorizedByUser':True,'steamExistingDownloadResumed':True,'existingDownloadCompleted':True,
    'cs2OnlineDeathmatchSpectator':True,'humanPlayThisRound':False,'clientTestServerExited':True,'syntheticTrafficUsed':False,
    'newPurchaseOrUnownedGameInstalled':False,'gameQualityConclusion':False},
 'classifierCache':{'committed':True,'candidateSha256':cacheProof['candidateSha256'],'originalSha256':cacheProof['originalSha256'],
    'change':'Two pure IPv4 validation/arithmetic caches, independently capped at 1024 and reset for every discovery observation.',
    'freshCtIdentityMarkNatAndCountersNotCached':True,'policyAndSourceBoundAndDeadlinesUnchanged':True,
    'differentialCases':cacheProof['cases'],'acceptedCases':cacheProof['acceptedCases'],
    'nativeRows':nativeCache['actualRows'],'nativeAcceptedRows':nativeCache['acceptedRows'],
    'nativeTraversalsPerVersion':nativeCache['parserTraversalsPerVersion'],'completeNativeSnapshotsEqual':nativeCache['completeClassifierRepeatedEqual'],
    'nativeParserCpuSeconds':nativeCache['cpuSeconds'],
    'nativeParserCpuReductionPercent':(1-nativeCache['cpuSeconds']['new']/nativeCache['cpuSeconds']['old'])*100,
    'wholeRouterCpuBenefitProved':False,'cacheCap':1024,'boundedChecks':cacheBound['checks'],'distinctCacheAddresses':cacheBound['distinctValidAddresses'],
    'natural180SecondRollbackVerified':True,'trialLiveCacheTimingCaptured':False,
    'secondInstallationCheckpointAndIndependentRollbackVerified':True,'commitAt':deployment['commitAt'],
    'retainedInstallationArming':pick(read(cache+'/armed-proof.json'),['passed','independentOfSsh','deadline','observedUptime']),
    'rejectedLiteralScannerInstalled':False},
 'actualFailures':failureEvidence,
 'entry':{'boundInputs':len(manifest),'configurationMatchesCurrentClassifier':True,'localEntryCases':99,'nativeRamSyntheticCases':13,
    'nativeRamGateTimeIoMocked':True,'onlyInitialZeroTrafficReadinessChanged':True,
    'initialTagNoTrafficWaitSeconds':1.2,'previousInitialTagWaitSeconds':0.3,'wrongTagStillImmediatelyRejected':True,
    'zeroTrafficCannotAuthorizeNss':True,'otherNssLuaByteIdenticalToNss48':True,
    'fastHelperSha256':sha('work/nss49/fast-path.lua'),'nativeNssKernelDataPlaneUnmodified':True,
    'ownerSeconds':45,'initialSourceAgeSeconds':1,'prelearningSourceAgeSeconds':2,'softwareSourceAgeSeconds':6,'publicationAgeSeconds':9,
    'epochSeconds':5,'controlledBudgetMbps':20,'tcpSlots':1,'udpSlots':1,
    'legacyNssRouterPayloadsUnchangedFlagIsInheritedAndDoesNotDescribeHelperDelta':True},
 'actualForwardingABA':{'passed':True,'sameControlledApplicationPair':True,'realHumanGameplay':False,
    'oneWan':2,'ctMark':131072,'phases':phaseWindows,'runtimeState':proof,'measurements':metrics,
    'initialTagGetterSeconds':record['initialTagReadiness']['completedAt']-record['initialTagReadiness']['startedAt'],
    'initialTagGetterProbes':record['initialTagReadiness']['probes'],'extendedNoTrafficWaitNeededThisCase':False,
    'nativeRenewals':len(record['renewals']),'checkpointDownloadedAndHashAndGzipVerified':True,
    'independent45SecondOwnerVerifiedBeforeWrites':True,'explicitEarlyRetirement':record['explicitEarlyRetirement'],
    'natural45SecondExpiryTriggeredThisCase':False,'postRetirementFirmwareZero':record['firmwareZeroAfterRetirement'],
    'scopedRollbackPassed':True,'afterFullProtectionAuditPassed':read(good+'-after-audit.json')['passed'],
    'sourceInputsFrozenPrivately':True,'commonQueuePlanAndCounterLoop':record['unchangedQoSPlan'],
    'throughputMatched':False,'offeredLoadEqualityProven':False,'totalLoad300MbpsPlusThisWholeWindow':False,
    'cpuAndGameAcceptancePassed':False},
 'clientEvidence':{'firstActualSkyFrames':len(frames),'clockAnchorRoundTripMs':anchor['roundTripMs'],'assignedPhaseFrameCounts':hudCounts,
    'nssBHudCovered':False,'hudAbsenceNotConvertedToZero':True,'clientExperienceNotMeasured':True,
    'secondAttempt':pick(second,['observedAt','actualGameCandidates','actualBulkCandidates','sameWanPairs','routerWrites','nssPermissionGranted','status']),
    'secondAttemptNoForwardingABA':True,'secondCaptureNotGameAcceptanceEvidence':True,
    'laterForegroundOcclusionObserved':True,'screenshotsExportedToGit':False},
 'finalState':{'classifierHealthy':True,'sameCacheRetainedWorker':final['producer'].endswith(':5411:191326402'),
    'protectedAudit':pick(final,['passed','protectedConfigurationUnchanged','exactOwnedNativeAudit','selectors','queryAge','sequence','ecmClosedAndZero']),
    'closure':closure,'entryCannotAuthorizeWithoutFreshPair':True},
 'conclusions':{'automaticClassificationToNativeBulkRtLeavesProvedThisRound':True,
    'fullControllerSoftwareNssSoftwareSucceeded':True,'markNatWanAffinityProved':True,
    'wholeRouterCpuBenefitProved':False,'clientNssBHudMetricsCaptured':False,'realHumanExperienceProved':False,
    'completeHighLoadLifecycleQualified':False,'secondSimultaneousWanAllowed':False,'sharedBudgetAllowed':False,
    'hostFairnessRestorationRequired':False,'n100Required':False,'upstreamSubmitted':False},
 'reportVerification':{'sourceValidated':False,'browserRendered':False,'reason':'Existing local-file browser policy refusal retained; no workaround.'}
}
save('outputs/nss49-mainline-observations.json',out)
save('work/nss49/actual-aba-sanitized.json',out['actualForwardingABA'])
save('work/nss49/entry-binding-sanitized.json',out['entry'])
save('work/nss49/failed-attempts-sanitized.json',failureEvidence)
save('work/nss49/client-evidence-sanitized.json',out['clientEvidence'])
print(json.dumps({'passed':True,'actualABA':True,'nativeAcceleration':[0,2,0],'realHumanGameplay':False,'cpuBenefitProved':False,'allScopedCleanupPassed':True,'boundInputs':len(manifest),'hudPhaseCounts':hudCounts}))
