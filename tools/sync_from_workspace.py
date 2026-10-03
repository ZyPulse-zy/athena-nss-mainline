"""Curated export. Never recursively copy captures, credentials, or backups."""
import argparse, hashlib, json, re, shutil
from datetime import datetime, timezone
from pathlib import Path

parser=argparse.ArgumentParser()
parser.add_argument('workspace', type=Path)
args=parser.parse_args()
workspace=args.workspace.resolve()
repo=Path(__file__).resolve().parents[1]
assert workspace.is_dir() and repo != workspace
def read(path): return json.loads((workspace/path).read_text(encoding='utf-8-sig'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path, value):
    dst=repo/path; dst.parent.mkdir(parents=True,exist_ok=True)
    dst.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
def keys(obj,names): return {k:obj[k] for k in names if k in obj}

current=read('work/nss39/deployment-latest.json')
assert current['committed'] is True
cfg=read(current['localDir']+'/config.json')
sources=[]
allowlist={
 'work/nss42': ['audit-renderer.mjs','build-qualification.mjs','check-diagnostics-native.mjs','current-audit-diagnostic.mjs','dependency-closure.mjs','final-closure.mjs','inspect-classifier.mjs','opening-audit.mjs','parse-dependency-graph.mjs','parse-ecm-any-wan.mjs','prepare.mjs','publication-wait.lua','read-real-candidates.mjs','real-session.mjs','record-candidates.mjs','session-binding.mjs','test-binding.mjs','test-controller.mjs','test-dependencies.mjs','test-parser.mjs','test-publication-wait.py','wait-full-publication.mjs','watch-classifier.mjs'],
 'work/nss42/report': ['summarize.mjs','render.mjs'],
 'work/nss12/forward-tag-trial': ['model.mjs'],
 'work/nss41': ['prepare.mjs','prepare-alignment.mjs','session-binding.mjs','real-session.mjs','current-audit-diagnostic.mjs','audit-renderer.mjs','record-candidates.mjs','read-real-candidates.mjs','inspect-classifier.mjs','final-closure.mjs','publication-wait.lua','wait-full-publication.mjs','qualify-entry.mjs','test-publication-wait.py','test-preaudit-archive.mjs','finite-download.py','observe-publication.lua','run-audit-load.mjs','summarize.mjs','summarize-live.mjs','render-report.mjs','render-live-report.mjs','validate-actual-state.mjs','parse-ecm-any-wan.mjs','prepare-posttrial-audit.mjs','posttrial-protected-audit.mjs'],
 'work/nss25': ['parse-ecm.mjs'],
 'work/nss40': ['prepare.mjs','prepare-session.mjs','session-binding.mjs','current-audit.mjs','inspect-classifier.mjs','final-closure.mjs','read-real-candidates.mjs','real-session.mjs','rehearse-admission.mjs','trace-protected-audit.mjs','observe-compact.mjs','record-candidates.mjs','prepare-diagnostic-audit.mjs','audit-renderer.mjs','current-audit-diagnostic.mjs','summarize.mjs','render-report.mjs'],
 'work/nss39': ['prepare.mjs','original-worker.lua','tc-command.lua','tc-command-fixtures.lua','test-worker.py','build-worker.mjs','test-timeout-path.mjs','inspect-timeout-runtime.mjs','read-busybox-source.py','test-tc-native.mjs','benchmark-tc-readonly.mjs','worker.lua','guardian.lua','conntrack-source.lua','prepare-install.mjs','upgrade.mjs','verify-rollback.mjs','qualify-trial.mjs','commit-channel.mjs','retain-qualified.mjs','wait-current-startup.mjs','cancel-restored-stage.mjs','observe-compact.mjs','deployment-audit.mjs','current-audit.mjs','inspect-classifier.mjs','final-closure.mjs','prepare-mainline.mjs','binding.mjs','classifier.lua','fast-path.lua','core-guard-phase.lua','classified-tags.lua','qos-physical.lua','tag-normalizer.lua','wan-scope.lua','state-node.lua','module-stage-guardian.lua','read-prerequisites.lua','aba-fixtures.lua','pair-policy.mjs','payload.mjs','module-stage.mjs','real-session.mjs','read-real-candidates.mjs','preflight-mainline.mjs','qualification.mjs','qualify-affinity.mjs','test-admission.py','test-consumer-local.py','test-lifecycle.py','test-owned-lifecycle.py','native-qualification.mjs','summarize.mjs','render-report.mjs'],
 'work/nss38': ['current-audit.mjs','final-closure.mjs','inspect-classifier.mjs','inspect-game-class.mjs','read-real-candidates.mjs','real-session.mjs','classifier.lua','fast-path.lua','observe-publication.lua','observe-publication.mjs','rehearse-admission.mjs','profile-admission-loop.lua','profile-admission-loop.mjs','freeze-attempt.mjs','build-candidate.mjs','candidate-classifier.lua','test-adapter-differential.py','adapter-differential.lua','test-admission.py','test-consumer-local.py','benchmark-adapter.lua','benchmark-adapter.mjs','build-traced-candidate.mjs','candidate-traced-classifier.lua','candidate-traced-fast-path.lua','check-candidate-native.mjs','read-classifier-errors.mjs','probe-qdisc-read.mjs','summarize.mjs','render-report.mjs'],
 'work/nss11': ['group-runner.c','test-group-runner.py'],
 'work/nss37': ['conntrack-source.lua','original-conntrack-source.lua','worker.lua','guardian.lua','prepare.mjs','build.mjs','test-normalizer.py','test-lifecycle.py','profile-normalizer.mjs','benchmark-native.mjs','normalize-benchmark.lua','prepare-install.mjs','upgrade.mjs','verify-rollback.mjs','qualify-trial.mjs','commit-channel.mjs','observe-compact.mjs','operational-audit.mjs','deployment-audit.mjs','current-audit.mjs','inspect-classifier.mjs','final-closure.mjs','prepare-mainline.mjs','binding.mjs','classifier.lua','fast-path.lua','core-guard-phase.lua','classified-tags.lua','qos-physical.lua','tag-normalizer.lua','wan-scope.lua','state-node.lua','module-stage-guardian.lua','read-prerequisites.lua','aba-fixtures.lua','pair-policy.mjs','payload.mjs','module-stage.mjs','real-session.mjs','read-real-candidates.mjs','preflight-mainline.mjs','qualification.mjs','qualify-affinity.mjs','summarize.mjs','render-report.mjs'],
 'work/nss33': [
  'admission-publication.lua','worker.lua','guardian.lua','conntrack-source.lua',
  'classifier.lua','fast-path.lua','core-guard-phase.lua','classified-tags.lua','qos-physical.lua',
  'tag-normalizer.lua','wan-scope.lua','state-node.lua','module-stage-guardian.lua','read-prerequisites.lua',
  'aba-fixtures.lua','pair-policy.mjs','payload.mjs','module-stage.mjs','real-session.mjs',
  'read-real-candidates.mjs','qualification.mjs','qualify-affinity.mjs','preflight-mainline.mjs',
  'test-aba.mjs','test-projection.mjs','upgrade.mjs','commit-channel.mjs','verify-rollback.mjs',
  'operational-audit.mjs','final-closure.mjs','rehearse-admission.mjs'],
 'work/nss23': ['consumer-fixtures.lua','adapter-fixtures.lua','operational-audit.lua','backend-fixtures.lua','core-fixtures.lua'],
 'work/nss27': ['renewal-consumer-fixtures.lua','flow-selection.mjs'],
 'work/nss27/endpoint-gate': ['rp_ecm_gate_lab_ct.c','two_slot_predicate.h','ecm_ae_classifier_public.h','predicate_test.c','ct_harness.py','control_harness.py','Makefile'],
 'work/nss32': ['fast-path.lua','classifier.lua','aba-fixtures.lua','test-consumer-local.py','verify-native.mjs'],
 'work/nss34': ['profile-initial-loop.mjs','read-real-candidates.mjs','final-closure.mjs','test-admission-replay.py','inspect-classifier-restart.mjs','read-classifier-log.mjs','probe-address-query.mjs'],
 'work/nss35': ['worker.lua','guardian.lua','conntrack-source.lua','address-query.lua','observation-policy.lua','build.mjs',
  'test-recovery.py','test-query-local.py','query-local-fixtures.lua','test-query-native.mjs','test-history-native.mjs','test-projection.mjs',
  'upgrade.mjs','commit-channel.mjs','verify-rollback.mjs','operational-audit.mjs','observe-compact.mjs','qualify-trial.mjs','final-closure.mjs','summarize.mjs'],
 'work/nss36': ['classifier.lua','fast-path.lua','core-guard-phase.lua','classified-tags.lua','qos-physical.lua','tag-normalizer.lua','wan-scope.lua','state-node.lua','module-stage-guardian.lua','read-prerequisites.lua','aba-fixtures.lua','pair-policy.mjs','payload.mjs','module-stage.mjs','real-session.mjs','read-real-candidates.mjs','preflight-mainline.mjs','test-aba.mjs','binding.mjs','qualification.mjs','qualify-affinity.mjs','test-consumer-local.py','test-admission.py','test-lifecycle.py','test-owned-lifecycle.py','operational-audit.mjs','final-closure.mjs','inspect-classifier.mjs','rehearse-admission.mjs','profile-publication-path.mjs','freeze-attempt.mjs','summarize.mjs','render-report.mjs'],
}
def copy(source, destination, role):
    src=workspace/source; dst=repo/destination
    assert src.is_file(), str(source)
    assert src.suffix in ('.lua','.mjs','.py','.c','.h','.sh') or src.name=='Makefile'
    body=src.read_bytes(); body.decode('utf-8')
    dst.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(src,dst)
    sources.append({'path':str(destination).replace('\\','/'),'workspaceSource':str(source).replace('\\','/'),'sha256':sha(src),'bytes':len(body),'role':role})
for base,names in allowlist.items():
    for name in names: copy(Path(base)/name,Path('code')/base/name,'experimental-source-or-test')

deployed=[]
for name,expected in cfg['files'].items():
    if not name.endswith(('.lua','.sh')):
        deployed.append({'name':name,'sha256':expected,'included':False,'reason':'binary helper retained in private workspace'})
        continue
    candidates=sorted((workspace/'work').glob('nss*/'+name),reverse=True)
    matches=[path for path in candidates if sha(path)==expected]
    assert matches, 'Missing matching deployed source: '+name
    copy(matches[0].relative_to(workspace),Path('code/deployed-classifier')/name,'matches-current-deployed-config-hash')
    deployed.append({'name':name,'sha256':expected,'included':True})

s=read('outputs/nss33-classifier-readiness-observations.json')
t=s['realTrial']; c=s['permanentClassifier']; p=s['sameFramePublicationProfile']
summary={
 'round':'NSS33','sourceReport':'outputs/nss33-classifier-readiness-report.html',
 'highLoadSoftwareBaseline':s['highLoadSoftwareBaseline'],
 'measurementLimit':'Diagnostic LAN4 aggregate; read-only observation overhead; not matched forwarding ABA.',
 'publicationProfile':keys(p,['fullFlows','compactFlows','fullBytes','compactBytes','fullEncodeSeconds','compactBuildEncodeSeconds','parseSeconds','compactParseSeconds']),
 'projectionChecks':s['projectionTests'],
 'classifier':{'committed':c['committed'],'configSha256':c['configSha256'],'workerSha256':c['workerSha256'],'rollbackPassed':c['independentRollbackQualified'],'semanticProjection':c['semanticProjection'],'highLoadPerformanceQualified':False},
 'realTrial':keys(t,['passed','matchedForwardingABACompleted','actualApplicationPair','wan','tcpMark','udpMark','failure','exactInitialRefusalReasonsRecorded','gateModuleLoaded','nssPermissionGranted','controlDeadlineSeconds','initialAlignmentBudgetSeconds','bulkLeaf','rtLeaf','defaultLeaf','wanBeforeMode','wanDuringMode','wanAfterMode','wanHealthAfterUndo','authIdentityAndDhcpPreserved','renewalOrReauthenticationTested','rollbackPassed','initialFailureRootCauseConclusive']),
 'admissionRehearsal':keys(s['readOnlyAdmissionRehearsal'],['samples','ready','reasons','selectedTcpPresent','selectedGamePresent','minSourceAgeSeconds','maxReadSeconds','publicationDelayRangeSeconds','routerWrites','nssOpened']),
 'nssHighLoadCpuBenefitProved':False,'cs2JitterLossMissCaptured':False,'upstreamSubmission':False,
}
save('evidence/nss33-summary.json',summary)
r=read('work/nss33/admission-rehearsal-20261003071535-private.json')
start=r['rows'][0]['at']
save('evidence/nss33-admission-timing.json',{'routerWrites':False,'selectedEndpointsOmitted':True,'sampleMeaning':'Actual complete admission checks during a later readonly rehearsal, not the failed live attempt.','rows':[
 {'atSeconds':round(row['at']-start,4),**keys(row,['ready','sourceAge','publicationDelay','readSeconds','querySeconds']), 'reason':re.sub(r'^\[string .*?\]:\d+: ','',row.get('reason','')),'tcpPresent':row['selected']['tcp']['present'],'udpPresent':row['selected']['udp']['present']}
 for row in r['rows']]})
loop=read('work/nss34/loop-profile.json'); rows=loop['rows']; start=rows[0]['at']
save('evidence/nss34-loop-profile.json',{
 'observedAt':loop['observedAt'],'routerWrites':False,'nssOpened':False,'actualFlowAdmissionChecked':False,
 'summary':{'samples':len(rows),'fullInventory':sum(x['fullInventory'] for x in rows),'meanPhaseSeconds':sum(x['phaseSeconds'] for x in rows)/len(rows),'maxPhaseSeconds':max(x['phaseSeconds'] for x in rows),'maxIterationReads':max(x['iterationReads'] for x in rows),'ageOnlyReserveAvailable':sum(x['ageOnlyReserveAvailable'] for x in rows)},
 'rows':[{'atSeconds':round(x['at']-start,4),**keys(x,['closedSeconds','phaseSeconds','readSeconds','parseSeconds','iterationReads','fullInventory','refreshInventory','sourceAge','publicationDelay','ageOnlyReserveAvailable','classifiedFlowCount','status'])} for x in rows]})
auditPath='work/nss42/closing-recovery-audit.json'
audit=read(auditPath)
checked=datetime.fromtimestamp((workspace/auditPath).stat().st_mtime,timezone.utc).isoformat()
pc=read('work/nss42/real-reader-qualified.json')
save('evidence/current-runtime.json',{
 'checkedAt':checked,'round':'NSS42','deploymentReference':'work/nss39/deployment-latest.json',
 'classifierConfigSha256':current['configHash'],'deployedTextSources':deployed,
 'audit':keys(audit,['passed','protectedConfigurationUnchanged','exactOwnedNativeAudit','selectors','queryAge','sequence','ecmClosedAndZero']),
 'lastApplicationObservation':keys(pc,['observedAt','readonly','gameProcessRunning','steamProcessRunning','actualCs2RtCandidates','actualSteamBulkCandidates','sameWanCandidates','sourceAge','nssAdmissionAllowed']),
 'applicationEndpointsReadThisRound':True,
 'freshApplicationPairCheckedThisRound':True,
 'realForwardingABACompleted':False,
 'historicalNss41NativeForwardingABACompleted':True,
 'completePerformanceAndGameAcceptance':False,
 'staleSnapshotRejectedEarlierInRound':False,
 'historicalNss40StaleProtectedSnapshotRejection':True,
 'recoveryAlignmentRefusedEarlierInRound':False,
 'historicalNss41RecoveryAlignmentRefused':True,
 'historicalNss36StaleSnapshotRejection':True,
 'classifierWorkerRestartObservedThisRound':False,
 'plannedClassifierReplacementAndRollbackThisRound':False,
 'experimentalConfigurationWritesThisRound':False,
 'finalClosure':keys(read('work/nss42/final-closure.json'),['passed','observedAt','readonly','noActiveRootTransaction','noNssStagingDirectory','noExperimentStateNodeDirectory','noExperimentalGateOrQdiscModule']),
 'requiresLiveRevalidation':True,
})
replay=read('work/nss34/admission-replay-qualified.json')
save('evidence/nss34-admission-replay.json',keys(replay,['passed','checks','cases','alignmentScenarios','adapterSha256','fastSourceSha256','routerWrites','trafficGenerated','hardwareQualified','sourceModified','scope']))
restart=read('work/nss34/classifier-restart-inspection.json')
probe=read('work/nss34/address-query-probe.json')
error=restart['files']['last-error.json']['error']
assert "'/sbin/ip -j -4 address show'" in error and '__NSS23_RC__143' in error
log=(workspace/'work/nss34/classifier-service-log-private.txt').read_text(encoding='utf-8')
assert '15:54:43 2026 daemon.err sh[22608]' in log and '16:00:11 2026 daemon.err sh[3344]' in log
save('evidence/nss34-classifier-restarts.json',{
 'observedAt':restart['observedAt'],'routerWrites':False,'classifierWorkerChanged':True,
 'restartTriggerLogTimes':['2026-10-03T15:54:43+08:00','2026-10-03T16:00:11+08:00'],
 'latestFailure':{'command':'/sbin/ip -j -4 address show','wrapperTimeoutSeconds':2,'killAfterSeconds':1,'returnCode':143,'handler':'worker direct() asserts nonzero command status; watch loop exits, then procd respawns'},
 'currentAtInspection':{'classificationStatus':restart['files']['classification.json']['status'],'dataHealthy':restart['files']['classification.json']['dataHealthy'],'guardianHealthy':restart['files']['guardian.json']['healthy']},
 'subsequentAddressQueryProbe':probe,'blockingOrSignalRootCauseProved':False,
 'operationalConsequence':'Candidate history and producer instance change on restart; current health is not proof of continuous classification stability.',
 'nextGate':'Diagnose and qualify bounded fail-closed address discovery recovery before real high-load NSS retry.',
})
save('source-manifest.json',{'generatedAt':datetime.now(timezone.utc).isoformat(),'preservesOriginalSourceBytes':True,'routerCredentialsIncluded':False,'rawCapturesIncluded':False,'binariesIncluded':False,'sources':sources})
n35=read('outputs/nss35-address-recovery-observations.json')
assert n35['classifier']['committed'] and n35['classifier']['configSha256']==read('work/nss35/deployment-latest.json')['configHash']
assert n35['automaticRollback']['passed'] and n35['checks']==136
save('evidence/nss35-address-recovery.json',n35)
n36=read('outputs/nss36-admission-timing-observations.json')
assert n36['checks']==299 and not n36['actualTrial']['passed'] and n36['actualTrial']['rollbackPassed']
save('evidence/nss36-mainline.json',n36)
save('evidence/nss36-admission-timing.json',read('work/nss36/admission-timing-sanitized.json'))
save('evidence/nss36-admission-replay.json',keys(read('work/nss36/admission-qualified.json'),['passed','checks','cases','alignmentScenarios','differentialAdmissionCases','capturedTimingCases','adapterSha256','fastSourceSha256','routerWrites','hardwareQualified','scope']))
n37=read('outputs/nss37-normalizer-observations.json')
assert n37['localChecks']==9113 and n37['classifier']['committed'] and n37['classifier']['configSha256']==read('work/nss37/deployment-latest.json')['configHash']
assert n37['automaticRollback']['automaticExpiryWithoutControllerRollback']
assert n37['finalState']['protectedAudit']['ecmClosedAndZero'] and not n37['actualFastPathTrial']['attempted']
save('evidence/nss37-normalizer.json',n37)
n38=read('outputs/nss38-mainline-observations.json')
assert n38['deploymentReference']=='work/nss37/deployment-latest.json' and not n38['permanentClassifierChanged']
assert n38['actualTrial']['probeCount']==32 and n38['actualTrial']['rollbackPassed'] and not n38['actualTrial']['nssPermissionGranted']
assert n38['classifierRestart']['observed'] and n38['finalState']['currentClassifierHealthy']
assert not n38['candidate']['installed'] and not n38['candidate']['operationalBindingUpdated']
save('evidence/nss38-mainline.json',n38)
save('evidence/nss38-loop-timing.json',read('work/nss38/loop-timing-sanitized.json'))
save('evidence/nss38-adapter-differential.json',read('work/nss38/traced-adapter-differential-qualified.json'))
save('evidence/nss38-admission-replay.json',read('work/nss38/traced-admission-qualified.json'))
save('evidence/nss38-native-syntax.json',read('work/nss38/native-candidate-syntax.json'))
n39=read('outputs/nss39-mainline-observations.json')
assert n39['classifier']['committed'] and n39['classifier']['configSha256']==current['configHash']
assert sum(x['automaticRollbackVerified'] for x in n39['installations'])==3
assert n39['controller']['boundToCurrentDeployment'] and not n39['actualFastPathTrial']['attempted']
save('evidence/nss39-mainline.json',n39)
n40=read('outputs/nss40-mainline-observations.json')
assert n40['deploymentReference']=='work/nss39/deployment-latest.json' and not n40['permanentClassifierChanged']
assert n40['realReadOnlyAdmission']['samples']==94 and n40['realReadOnlyAdmission']['ready']==4
assert n40['actualTrial']['prewriteAuditRefused'] and not n40['actualTrial']['productionMutationAttempted']
assert n40['finalState']['protectedAudit']['passed'] and not n40['conclusions']['realHighLoadNssLoopCompleted']
save('evidence/nss40-mainline.json',n40)
save('evidence/nss40-admission-timing.json',read('work/nss40/admission-timing-sanitized.json'))
n41=read('outputs/nss41-mainline-observations.json')
assert n41['deploymentReference']=='work/nss39/deployment-latest.json' and not n41['permanentClassifierChanged']
assert n41['actualTrial']['nativeFunctionalPathRevalidated'] and n41['actualTrial']['checkpointCreatedAndVerified']
assert not n41['actualTrial']['originalControllerTerminalPassed'] and n41['actualTrial']['originalFailurePreserved']
assert n41['finalState']['protectedAudit']['passed'] and not n41['conclusions']['nssCpuBenefitProvedThisRound']
save('evidence/nss41-mainline.json',n41)
save('evidence/nss41-load-publication.json',read('work/nss41/load-publication-sanitized.json'))
n42=read('outputs/nss42-mainline-observations.json')
assert n42['deploymentReference']=='work/nss39/deployment-latest.json' and not n42['routerConfigurationWrites']
assert n42['localChecks']['newCases']==90 and n42['nativeDiagnosticRamChecks']['checks']==4
assert n42['entry']['totalBoundInputs']==102 and n42['entry']['postparserBound']
assert n42['finalState']['protectedAudit']['passed'] and not n42['actualFastPathTrial']['attempted']
save('evidence/nss42-mainline.json',n42)
save('evidence/nss42-stability-timing.json',read('work/nss42/stability-timing-sanitized.json'))
print(json.dumps({'sourceFiles':len(sources),'codeBytes':sum(s['bytes'] for s in sources),'evidenceFiles':len(list((repo/'evidence').glob('*.json'))),'credentialsCopied':False,'rawCapturesCopied':False}))
