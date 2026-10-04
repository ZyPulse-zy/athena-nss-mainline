"""Explicit curated NSS54–63 export. Raw connections, archives, HUD and modules stay local."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, json, hashlib, shutil
p=argparse.ArgumentParser();p.add_argument('workspace',type=Path)
workspace=p.parse_args().workspace.resolve();root=Path(__file__).resolve().parents[1]
def read(path):return json.loads((workspace/path).read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,obj):(root/path).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
current=root/'evidence/current-runtime.json';historical=root/'evidence/nss53-runtime.json'
if not historical.exists():
    assert json.loads(current.read_text())['round']=='NSS53';shutil.copyfile(current,historical)
assert json.loads(historical.read_text())['round']=='NSS53'
assert json.loads(current.read_text())['round'] in ('NSS53','NSS63')
manifest=json.loads((root/'source-manifest.json').read_text());existing={x['path']:x for x in manifest['sources']}
for n,version in [(n,1) for n in range(54,64)]+[(63,2)]:
    proof=read(f'work/nss{n}/source-proof-v{version}.json')
    assert proof['sources']==len(proof['sourceHashes']) and proof['notAdditionalProductionAdmission']
    for source,expected in proof['sourceHashes'].items():
        src=workspace/source;frozen=workspace/f'work/nss{n}/proof-v{version}/code'/src.name
        assert sha(src)==sha(frozen)==expected
        assert 'private' not in src.name and src.suffix in ('.mjs','.lua','.json','.py')
        dst=root/'code'/source;dst.parent.mkdir(parents=True,exist_ok=True);key=dst.relative_to(root).as_posix()
        if key in existing:assert existing[key]['sha256']==expected
        shutil.copyfile(frozen,dst)
        existing[key]={'path':key,'workspaceSource':source,'sha256':expected,'bytes':src.stat().st_size,'role':proof['role']}
    save(f'evidence/nss{n}-source-proof'+('-v2' if version==2 else '')+'.json',proof)
data=read('outputs/nss63-mainline-observations-v2.json')
assert data['productionTemporaryStages']==5 and data['actualNssOpenings']==1 and not data['completeForwardingABAThisTurn']
assert data['entry']['boundInputs']==241 and data['finalState']['protectedAudit']['passed']
save('evidence/nss63-mainline.json',data)
for dst,src in {
    'nss63-attempts':'work/nss63/attempts-v2-sanitized.json',
    'nss63-partial56':'work/nss63/partial56-metrics-sanitized.json',
    'nss63-client56':'work/nss63/client56-sanitized.json',
    'nss63-entry-binding':'work/nss63/entry-qualified.json',
    'nss63-steam-ended':'work/nss63/steam-ended-sanitized.json',
    'nss63-final-audit':'work/nss63/final-client-restored-audit.json',
    'nss63-final-cleanup':'work/nss63/final-client-restored-cleanup-audit.json'}.items():save(f'evidence/{dst}.json',read(src))
save('evidence/current-runtime.json',{
    'checkedAt':data['observedAt'],'round':'NSS63','deploymentReference':data['deploymentReference'],
    'classifierConfigSha256':data['classifierConfigSha256'],'audit':data['finalState']['protectedAudit'],
    'finalClosure':data['finalState']['closure'],'workerPid':data['finalState']['workerPid'],
    'naturalWorkerRestartObservedThisTurn':True,'classifierWorkerContinuousAfterCacheRetain':False,
    'permanentClassifierChangedThisTurn':False,'classifierReliabilityChangesRetained':3,'pureIpv4ParserCacheRetained':True,
    'experimentalConfigurationWritesThisTurn':True,'nssOpenedThisTurn':True,'temporaryStagesThisTurn':5,
    'historicalNss49FunctionABACompleted':True,'realForwardingABACompletedThisTurn':False,
    'partialABThisTurn':True,'realNssBClientHudCapturedThisTurn':True,'completePerformanceAndGameAcceptance':False,
    'qualifiedExperimentalEntry':'work/nss63/real-session.mjs','qualifiedExperimentalEntryBoundInputs':241,
    'entryPreparationQualified':True,'entryNotInstalledAsResidentClassifier':True,'entryFullHighLoadForwardingQualified':False,
    'latestEntryRefusedBeforeCheckpoint':True,'nssPermanentlyEnabled':False,
    'steamImmediateQueueEmpty':True,'steamNetworkBps':0,'cs2TestServerExited':True,'cs2HudRestored':True,
    'humanGameplayThisTurn':False,'upstreamSubmitted':False,'requiresLiveRevalidation':True,
    'historical53RuntimePreservedSha256':sha(historical)})
manifest.update({'generatedAt':datetime.now(timezone.utc).isoformat(),'sources':list(existing.values()),'lastAppendExport':'NSS63','privateDataExcluded':True})
save('source-manifest.json',manifest)
print(json.dumps({'exported':True,'latestRound':'NSS63','newCuratedSources':144,'totalCuratedSources':len(existing),'rawPrivateDataCopied':False}))
