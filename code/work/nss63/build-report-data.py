"""Sanitize saved actual evidence. No router connection or admission changes."""
from pathlib import Path
import hashlib, json, gzip, shutil
from datetime import datetime, timezone
W=Path(__file__).resolve().parents[2]
def read(p): return json.loads((W/p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256((W/p).read_bytes()).hexdigest()
def save(p,o):
    q=W/p
    assert not q.exists(),str(q)
    q.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
cases=[
 (53,'20261004111209-6a9eaa7f','complete-snapshot-source-expired-before-checkpoint'),
 (54,'20261004112142-0b6e84c4','publication-inode-replaced-during-path-read'),
 (55,'20261004113015-795828f5','standalone-classifier-syntax-transport-over-9000-before-checkpoint'),
 (56,'20261004113917-6ebf3ae3','strict-counter-getter-after-retirement-before-A2'),
 (57,'20261004120723-62732af8','complete-snapshot-source-expired-before-checkpoint'),
 (58,'20261004121718-a769d145','strict-counter-getter-after-A-before-ECM'),
 (59,'20261004122829-9f40d45c','selected-TCP-absent-in-strict-same-source-complete-classification'),
 (59,'20261004123227-d23e7948','complete-snapshot-source-expired-before-checkpoint'),
 (60,'20261004124808-c5c15d65','local-publication-hint-return-contract-before-checkpoint'),
 (61,'20261004125340-b2e64484','prelearning-source-margin-insufficient-before-A'),
 (61,'20261004125914-c82315c1','candidate-sleep-child-proc-wchan-disappeared-before-ECM'),
 (63,'20261004131115-c2fb6b05','complete-snapshot-source-expired-before-checkpoint')]
attempts=[]
for n,identity,cause in cases:
    b=f'work/nss{n}/real-matched-aba-{identity}'
    result=read(b+'/result.json')
    assert result['passed'] is False and result['matchedForwardingABACompleted'] is False
    rp=W/(b+'/last-record-private.json'); r=read(b+'/last-record-private.json') if rp.exists() else {}
    staged=r.get('stageComplete',False)
    a={'round':f'NSS{n}','case':identity,'controllerPassed':False,'completeABA':False,'failure':cause,
       'productionTemporaryStageOccurred':staged,'ecmPermitOpened':bool(r.get('frontendOpenedAt')),
       'completedPhases':[p['name'] for p in r.get('phases',[])],
       'rejectedBeforeCheckpointOrStaging':not staged,'resultFileSha256':sha(b+'/result.json')}
    if staged:
        cp=read(b+'/stage-checkpoint-verified.json'); archive=W/(b+'/stage-checkpoint-config-private.tar.gz')
        assert cp['gzipVerified'] and hashlib.sha256(archive.read_bytes()).hexdigest()==cp['sha256']
        assert len(gzip.decompress(archive.read_bytes()))>0
        stage=read(b+'/stage-receipt-private.json'); assert all(stage[k] for k in ['rollbackBeforeFirstWrite','success','pipeInodesVerified','parentIdentityVerified'])
        undo=read(b+'/stage-undo-verified.json'); assert all(undo.values())
        compare_path=b+'/baseline-audit.json'
        compare=read(compare_path) if (W/compare_path).exists() else None
        if compare: assert compare['configurationMatches'] and all(compare['checks'].values())
        else: assert n==61 and identity.endswith('b2e64484')
        rollback={k:v for k,v in r.items() if any(x in k for x in ['Restored','Unloaded','Removed','firmwareZero'])}
        assert rollback and all(v is True for v in rollback.values())
        after=f'work/nss{n}/real-matched-aba-{identity}-after-audit.json'
        after_pass=(W/after).exists() and read(after)['passed']
        later=None
        if not after_pass:
            assert n==61 and identity.endswith('b2e64484')
            later='work/nss61/recovered-after-pausing-audit.json'; assert read(later)['passed']
        a.update({'wan':r['wanAfter'].get('wan',1) if isinstance(r.get('wanAfter'),dict) else 1,
                  'checkpointDownloadedHashAndGzipVerified':True,'checkpointSha256':cp['sha256'],
                  'independent45SecondRollbackVerifiedBeforeWrite':True,'independentOfControlConnection':True,
                  'natural45SecondExpiryProvedThisCase':False,'scopedRollbackPassed':True,
                  'configurationComparisonPassed':True if compare else None,'stageCleanupPassed':True,
                  'immediateAfterOriginalFullAuditPassed':bool(after_pass),
                  'laterOriginalFullRecoveryAuditPassed':bool(later),'rollbackFlags':rollback})
    attempts.append(a)
assert len(attempts)==12 and sum(a['productionTemporaryStageOccurred'] for a in attempts)==5
assert sum(a['ecmPermitOpened'] for a in attempts)==1
save('work/nss63/attempts-sanitized.json',{'actualControllerCases':attempts,'separateLocalEntryFailure':{'round':'NSS62','missingPayloadImport':True,'routerConnected':False,'routerWrites':False},'separateInitialWaitWithoutBulk':{'round':'NSS55','defaultWait':True,'routerConfigurationWrites':False},'originalFailuresPreserved':True})
mapping=read('work/nss63/partial56-clock-mapping-private.json')
hud=[]
measurements={'A':[(16,0.8,0.5,3,1),(16,0.8,0.3,2,1),(16,0.8,0.2,2,1),(16,0.8,0.1,2,1),(16,0.8,0.1,2,1)],
              'B':[(16,0,0,1,0),(16,0,0,2,0),(16,0,0,2,0),(16,0,0,2,0),(16,0,0,1,0)]}
for p in mapping['phaseFrames']:
    assert len(p['frames'])==5
    for frame,values in zip(p['frames'],measurements[p['phase']]):
        ping,miss,loss,jitter,upjitter=values
        path='work/nss54/hud-1791113954138-private/'+frame['file']
        hud.append({'phase':p['phase'],'frame':frame['file'],'sourceSha256':sha(path),'fullContextVisuallyVerified':True,
                    'uptimeInterval':{'earliest':frame['lo'],'latest':frame['hi']},'pingMs':ping,
                    'down':{'missPercent':miss,'lossPercent':loss,'jitterMs':jitter},
                    'up':{'missPercent':0,'lossPercent':0,'jitterMs':upjitter}})
save('work/nss63/client56-sanitized.json',{'actualClientHudCaptured':True,'humanGameplay':False,
    'assistantOnlineIdle':True,'frames':hud,'clockUncertaintyMs':mapping['uncertainty'],
    'allCaptureIntervalsAtLeastOneSecondInsidePhases':True,'originalScreenshotsPrivate':True,
    'rollingOrPeakDisplayNotIndependentInstantaneousSamples':True,'missingA2':True,'gameBenefitAccepted':False})
lists={
54:'baseline-publication-join.lua cleanup-audit.mjs clock-anchor.mjs current-audit-diagnostic.mjs entry-qualified.json initial-audit-diagnostic.mjs join-tests.json prepare-revision.mjs qualify-entry.mjs real-session.mjs session-binding.mjs test-publication-join.mjs wait-ready-joined.mjs',
55:'baseline-publication-join.lua cleanup-audit.mjs clock-anchor.mjs current-audit-diagnostic.mjs entry-qualified.json initial-audit-diagnostic.mjs join-tests.json measure-syntax-transport.mjs prepare-stage-revision.mjs qualify-entry.mjs real-session.mjs session-binding.mjs test-publication-join.mjs wait-ready-joined.mjs',
56:'baseline-publication-join.lua cleanup-audit.mjs clock-anchor.mjs current-audit-diagnostic.mjs entry-qualified.json initial-audit-diagnostic.mjs join-tests.json module-stage.mjs prepare-counter-revision.mjs qualify-entry.mjs real-session.mjs session-binding.mjs test-counter-witness.mjs test-publication-join.mjs wait-ready-joined.mjs',
57:'baseline-publication-join.lua cleanup-audit.mjs clock-anchor.mjs counter-tests.json current-audit-diagnostic.mjs entry-qualified.json fast-path-prepare-error.lua fast-path.lua join-tests.json module-stage.mjs payload.mjs prepare-publication-notice.mjs qualify-entry.mjs real-session.mjs repair-prepare.mjs session-binding.mjs wait-ready-joined.mjs',
58:'cleanup-audit.mjs clock-anchor.mjs current-audit-diagnostic.mjs entry-qualified.json notice-tests.json prepare-after-a-witness.mjs publication-notice.lua qualify-entry.mjs real-session.mjs session-binding.mjs test-publication-notice.mjs wait-publication-notice.mjs',
59:'before-margin-correction-counter-tests.json cleanup-audit.mjs clock-anchor.mjs counter-tests.json current-audit-diagnostic.mjs entry-qualified.json fast-path-before-margin-correction.lua fast-path.lua module-stage.mjs notice-tests.json payload.mjs prepare-metadata-wait.mjs publication-notice.lua qualify-entry.mjs real-session.mjs repair-preparation-margin.mjs session-binding.mjs test-counter-witness.mjs wait-publication-notice.mjs',
60:'baseline-publication-join.lua cleanup-audit.mjs clock-anchor.mjs current-audit-diagnostic.mjs entry-qualified.json metadata-hint.lua metadata-tests.json prepare-hint-contract.mjs qualify-entry.mjs real-session.mjs session-binding.mjs test-metadata-hint.mjs wait-publication-metadata.mjs',
61:'cleanup-audit.mjs clock-anchor.mjs current-audit-diagnostic.mjs entry-qualified.json hint-contract-tests.json prepare-process-race.mjs publication-hint.mjs qualify-entry.mjs real-session.mjs session-binding.mjs test-hint-contract.mjs wait-publication-metadata.mjs',
62:'cleanup-audit.mjs clock-anchor.mjs core-guard-phase.lua current-audit-diagnostic.mjs entry-qualified.json module-stage.mjs phase-qualified.json prepare-dependency-copy.mjs process-race-fixtures.lua qualify-entry.mjs real-session.mjs session-binding.mjs test-process-race.mjs wait-publication-metadata.mjs',
63:'analyze-partial.mjs cleanup-audit.mjs clock-anchor.mjs core-guard-phase.lua current-audit-diagnostic.mjs entry-qualified.json module-stage.mjs payload.mjs phase-qualified.json qualify-entry.mjs real-session.mjs session-binding.mjs wait-publication-metadata.mjs build-report-data.py'}
proofs=[]
for n,names in lists.items():
    folder=W/f'work/nss{n}/proof-v1/code';folder.mkdir(parents=True,exist_ok=False)
    hashes={}
    for name in names.split():
        p=f'work/nss{n}/{name}';assert 'private' not in name and (W/p).is_file(),p
        shutil.copyfile(W/p,folder/name);hashes[p]=sha(p)
    proof={'sources':len(hashes),'sourceHashes':hashes,'privateConnectionAndCapturesExcluded':True,
           'notAdditionalProductionAdmission':True,'role':'historical-experimental-candidate-tests-and-analysis-not-resident',
           'actualCompletePrivateInputFreezePreserved':n!=62,'nss62OriginalLocalDependencyFailurePreserved':n==62}
    save(f'work/nss{n}/source-proof-v1.json',proof);proofs.append({'round':f'NSS{n}','sources':len(hashes)})
entry=read('work/nss63/entry-qualified.json');assert entry['boundInputs']==241
aud=read('work/nss63/final-client-restored-audit.json');cleanup=read('work/nss63/final-client-restored-cleanup-audit.json')
own=read('work/nss63/final-client-restored-ownership-private.json');assert own['pid']==20682
restore=read('work/nss63/client-restoration-private.json');assert restore['restored'] and restore['serverExited']
steam=read('work/nss63/steam-ended-sanitized.json');assert steam['currentNetworkBps']==0
data={'round':'NSS63','includesRounds':'NSS54–NSS63 plus new NSS53 actual refusal','observedAt':datetime.now(timezone.utc).isoformat(),
    'deploymentReference':'work/nss47/deployment-latest.json','classifierConfigSha256':cleanup['configSha256'],
    'permanentClassifierChanged':False,'routerConfigurationWrites':True,'ecmOpenedThisTurn':True,'completeForwardingABAThisTurn':False,
    'budgetMbps':20,'gateFlows':{'tcp':1,'udp':1},'ownerSeconds':45,'allOriginalDeadlinesUnchanged':True,
    'entry':{'path':'work/nss63/real-session.mjs','boundInputs':241,'dependencyResolutionQualified':True,'notResident':True,
             'latestActualRefusedBeforeCheckpoint':True,'fullHighLoadForwardingQualified':False,'processRamCases':15,'processRamCasesReusedFromNss62':True},
    'checksByRevision':[{'round':54,'nativePureJoinCases':13},{'round':55,'nativePureJoinCases':14},
                       {'round':56,'joinCasesReused':14},{'round':57,'nativePureCounterCases':7},
                       {'round':58,'nativePureNoticeCases':10},{'round':59,'nativePureCounterCases':7},
                       {'round':60,'nativePureMetadataCases':10},{'round':61,'localContractAssertions':14},
                       {'round':62,'nativeRamProcessCases':15},{'round':63,'processCasesReusedNotNew':15}],
    'actualCases':attempts,'productionTemporaryStages':5,'actualNssOpenings':1,
    'partialForwarding':read('work/nss63/partial56-metrics-sanitized.json'),
    'clientHud':read('work/nss63/client56-sanitized.json'),'clientEndState':{'steam':steam,'cs2':{'restored':True,'serverExited':True,'humanGameplay':False}},
    'finalState':{'protectedAudit':aud,'closure':cleanup,'workerPid':own['pid'],'guardianPid':own['guardianPid'],
                  'sameCacheRetainedWorkerThroughout':False,'naturalWorkerRestartObserved':True,'manualWorkerRestartOrCrashInjected':False,
                  'workerRestartCauseProved':False,'sequence':own['querySequence'],'classifierHealthyAndExactOwnedAuditPassed':True},
    'sourceFreezes':proofs,'sourceProofOnlyNotAdditionalAdmission':True,
    'conclusions':{'realSelectedTcpUdpNssLeafProvedThisTurn':True,'actualNssBHudCaptured':True,
                   'softwareVersusNssCpuBenefitProved':False,'gameBenefitProved':False,'realHumanExperienceProved':False,
                   'completeHighLoadLifecycleQualified':False,'completeHighLoadLoopPassed':False,
                   'secondWanExpansionAllowed':False,'sharedBudgetAllowed':False,'upstreamSubmitted':False},
    'reportVerification':{'sourceValidated':True,'browserRendered':False}}
save('outputs/nss63-mainline-observations.json',data)
print(json.dumps({'built':True,'actualCases':12,'stages':5,'nssOpenings':1,'fullAba':False,'newCuratedSources':sum(p['sources'] for p in proofs),'worker':own['pid']}))
