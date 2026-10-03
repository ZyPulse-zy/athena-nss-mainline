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

current=read('work/nss33/deployment-latest.json')
cfg=read(current['localDir']+'/config.json')
sources=[]
allowlist={
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
auditPath=current['localDir']+'/nss34-end-audit.json'
if not (workspace/auditPath).is_file(): auditPath=current['localDir']+'/nss34-begin-audit.json'
audit=read(auditPath)
checked=datetime.fromtimestamp((workspace/auditPath).stat().st_mtime,timezone.utc).isoformat()
pc=read('work/nss34/real-reader-qualified.json')
save('evidence/current-runtime.json',{
 'checkedAt':checked,'round':'NSS34','deploymentReference':'work/nss33/deployment-latest.json',
 'classifierConfigSha256':current['configHash'],'deployedTextSources':deployed,
 'audit':keys(audit,['passed','protectedConfigurationUnchanged','exactOwnedNativeAudit','selectors','queryAge','sequence','ecmClosedAndZero']),
 'applicationObservation':keys(pc,['observedAt','readonly','gameProcessRunning','steamProcessRunning','actualCs2RtCandidates','actualSteamBulkCandidates','sameWanCandidates','sourceAge','nssAdmissionAllowed']),
 'finalClosure':keys(read('work/nss34/final-closure.json'),['passed','observedAt','readonly','noActiveRootTransaction','noNssStagingDirectory','noExperimentStateNodeDirectory','noExperimentalGateOrQdiscModule']) if (workspace/'work/nss34/final-closure.json').is_file() else None,
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
print(json.dumps({'sourceFiles':len(sources),'codeBytes':sum(s['bytes'] for s in sources),'evidenceFiles':6,'credentialsCopied':False,'rawCapturesCopied':False}))
