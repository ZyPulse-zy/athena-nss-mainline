"""Append an explicit sanitized export. Historical exports/runtime are preserved."""
import argparse,hashlib,json,shutil
from pathlib import Path
from datetime import datetime,timezone
p=argparse.ArgumentParser();p.add_argument('workspace',type=Path);args=p.parse_args();workspace=args.workspace.resolve();root=Path(__file__).resolve().parents[1]
def read(path):return json.loads((workspace/path).read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,value):(root/path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
previous=root/'evidence/current-runtime.json';historical=root/'evidence/nss49-runtime.json'
if not historical.exists():
    assert json.loads(previous.read_text())['round']=='NSS49';shutil.copyfile(previous,historical)
manifest=json.loads((root/'source-manifest.json').read_text());existing={x['path']:x for x in manifest['sources']}
for round in ['nss50','nss51','nss52']:
    proof=read(f'work/{round}/source-proof-v1.json');assert proof['notAdditionalProductionAdmission']and proof['privateConnectionAndCapturesExcluded']
    for source,expected in proof['sourceHashes'].items():
        file=workspace/source;frozen=workspace/'work'/round/'proof-v1/code'/file.name;assert sha(file)==sha(frozen)==expected
        assert 'private'not in file.name and file.suffix in ('.lua','.mjs','.py','.js','.json')
        dst=root/'code'/source;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(frozen,dst)
        path=dst.relative_to(root).as_posix();existing[path]={'path':path,'workspaceSource':source,'sha256':expected,'bytes':file.stat().st_size,'role':'uninstalled-readonly-candidate'if round=='nss52'else'experimental-entry-observer-or-test'}
    save(f'evidence/{round}-source-proof.json',proof)
data=read('outputs/nss52-mainline-observations.json');assert data['reportVerification']['sourceValidated']and not data['ecmOpenedThisTurn']
save('evidence/nss52-mainline.json',data)
save('evidence/nss50-mainline.json',read('outputs/nss50-mainline-observations.json'))
save('evidence/nss51-mainline.json',read('outputs/nss51-mainline-observations.json'))
save('evidence/nss52-phase-qualification.json',read('work/nss52/phase-qualified-sanitized.json'))
save('evidence/nss50-service-epoch-tests.json',read('work/nss50/service-epoch-tests.json'))
save('evidence/nss50-client-software.json',read('work/nss50/client-reviewed-sanitized.json'))
save('evidence/nss50-partial-software.json',read('work/nss50/partial-a-sanitized.json'))
save('evidence/nss51-phase-timing.json',read('work/nss52/trace-summary-v2-sanitized.json'))
owned=read('work/nss51/final-post-game-audit.json');closure=read('work/nss50/final-post-game-cleanup-audit.json')
save('evidence/current-runtime.json',{'checkedAt':closure['observedAt'],'round':'NSS52','deploymentReference':data['deploymentReference'],'classifierConfigSha256':data['classifierConfigSha256'],'audit':owned,'finalClosure':closure,'classifierWorkerContinuousAfterCacheRetain':data['finalState']['sameCacheRetainedWorker'],'historicalNss49FunctionABACompleted':True,'historicalNss46SoftwareExpiryAndCrashRecoveryPassed':True,'classifierReliabilityChangesRetained':3,'pureIpv4ParserCacheRetained':True,'experimentalConfigurationWritesThisTurn':True,'nssOpenedThisTurn':False,'realForwardingABACompletedThisTurn':False,'completePerformanceAndGameAcceptance':False,'nssPermanentlyEnabled':False,'qualifiedExperimentalEntry':'work/nss51/real-session.mjs','qualifiedExperimentalEntryBoundInputs':140,'uninstalledNextCandidate':'work/nss52/core-guard-phase.lua','candidateNotProductionBound':True,'clientTestServerExited':True,'hudRestored':True,'steamDownloadCompleted':True,'upstreamSubmitted':False,'requiresLiveRevalidation':True})
manifest.update({'generatedAt':datetime.now(timezone.utc).isoformat(),'sources':list(existing.values()),'lastAppendExport':'NSS50–NSS52','privateDataExcluded':True});save('source-manifest.json',manifest)
print(json.dumps({'exported':True,'latestRound':'NSS52','historical49RuntimePreserved':True,'totalCuratedSources':len(existing),'rawCapturesOrCredentialsCopied':False}))
