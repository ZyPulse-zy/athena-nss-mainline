"""Append NSS53 explicit readable sources and sanitized facts; preserve historical bytes."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, json, hashlib, shutil
p=argparse.ArgumentParser();p.add_argument('workspace',type=Path)
workspace=p.parse_args().workspace.resolve();root=Path(__file__).resolve().parents[1]
def read(path):return json.loads((workspace/path).read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,obj):(root/path).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
previous=root/'evidence/current-runtime.json';historical=root/'evidence/nss52-runtime.json'
if not historical.exists():
    assert json.loads(previous.read_text())['round']=='NSS52'
    shutil.copyfile(previous,historical)
assert json.loads(historical.read_text())['round']=='NSS52'
assert json.loads(previous.read_text())['round'] in ('NSS52','NSS53')
old=json.loads((root/'source-manifest.json').read_text())
existing={item['path']:item for item in old['sources']}
proof=read('work/nss53/source-proof-v1.json')
assert proof['sources']==len(proof['sourceHashes'])==24
assert proof['privateConnectionAndCapturesExcluded'] and proof['notAdditionalProductionAdmission']
for source,expected in proof['sourceHashes'].items():
    file=workspace/source;frozen=workspace/'work/nss53/proof-v1/code'/file.name
    assert sha(file)==sha(frozen)==expected
    assert 'private' not in file.name and file.suffix in ('.lua','.mjs','.json','.py')
    dst=root/'code'/source;dst.parent.mkdir(parents=True,exist_ok=True)
    path=dst.relative_to(root).as_posix()
    if path in existing:assert existing[path]['sha256']==expected
    shutil.copyfile(frozen,dst)
    existing[path]={'path':path,'workspaceSource':source,'sha256':expected,'bytes':file.stat().st_size,
                    'role':'experimental-entry-readonly-diagnostic-or-test-not-resident'}
data=read('outputs/nss53-mainline-observations.json')
assert data['phaseDiscovery']['actualPasses']==data['phaseDiscovery']['actualAttempts']==6
assert not data['routerConfigurationWrites'] and not data['ecmOpenedThisTurn']
assert data['entry']['boundInputs']==159 and data['finalState']['protectedAudit']['passed']
assert data['reportVerification']['sourceValidated'] and data['steamLoad']['pausedConfirmed']
save('evidence/nss53-mainline.json',data)
save('evidence/nss53-source-proof.json',proof)
for name in ['phase-load','diagnostics','entry-binding','steam-load']:
    save(f'evidence/nss53-{name}.json',read(f'work/nss53/{name}-sanitized.json'))
save('evidence/nss53-initial-audit.json',read('work/nss53/initial-prewrite-audit.json'))
save('evidence/current-runtime.json',{
    'checkedAt':data['observedAt'],'round':'NSS53',
    'deploymentReference':data['deploymentReference'],'classifierConfigSha256':data['classifierConfigSha256'],
    'audit':data['finalState']['protectedAudit'],'finalClosure':data['finalState']['closure'],
    'classifierWorkerContinuousAfterCacheRetain':data['finalState']['sameCacheRetainedWorkerAndGuardianAndProducer'],
    'historicalNss49FunctionABACompleted':True,'historicalNss46SoftwareExpiryAndCrashRecoveryPassed':True,
    'classifierReliabilityChangesRetained':3,'pureIpv4ParserCacheRetained':True,
    'experimentalConfigurationWritesThisTurn':False,'nssOpenedThisTurn':False,
    'realForwardingABACompletedThisTurn':False,'completePerformanceAndGameAcceptance':False,
    'nssPermanentlyEnabled':False,'qualifiedExperimentalEntry':'work/nss53/real-session.mjs',
    'qualifiedExperimentalEntryBoundInputs':159,'entryPreparationQualified':True,
    'entryNotInstalledAsResidentClassifier':True,'entryFullHighLoadForwardingQualified':False,
    'phaseDiscoveryActualLoadAttempts':6,'phaseDiscoveryActualLoadPassed':6,
    'steamDownloadPaused':True,'noCs2GuiActionsThisTurn':True,'actualGameCandidatesLastObservation':0,
    'upstreamSubmitted':False,'requiresLiveRevalidation':True,
    'historical52RuntimePreservedSha256':sha(historical)})
old.update({'generatedAt':datetime.now(timezone.utc).isoformat(),'sources':list(existing.values()),
            'lastAppendExport':'NSS53','privateDataExcluded':True})
save('source-manifest.json',old)
print(json.dumps({'exported':True,'latestRound':'NSS53','historical52RuntimePreserved':True,
                  'totalCuratedSources':len(existing),'rawPrivateDataCopied':False}))
