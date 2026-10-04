"""Explicit NSS65 export. No actual owner/config/checkpoint or raw observer export."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,shutil
p=argparse.ArgumentParser();p.add_argument('workspace',type=Path);workspace=p.parse_args().workspace.resolve()
root=Path(__file__).resolve().parents[1]
def read(path):return json.loads((workspace/path).read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,o):(root/path).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
current=root/'evidence/current-runtime.json';history=root/'evidence/nss64-runtime.json'
if not history.exists():
 assert json.loads(current.read_text())['round']=='NSS64';shutil.copyfile(current,history)
assert json.loads(history.read_text())['round']=='NSS64'
assert json.loads(current.read_text())['round']in ('NSS64','NSS65')
proof=read('work/nss65/source-proof-v1.json')
assert proof['notAdditionalProductionAdmission']and proof['publicationCandidateInstalledDuringTrial']and not proof['candidateRetainedAtEnd']
manifest=json.loads((root/'source-manifest.json').read_text());items={v['path']:v for v in manifest['sources']}
for source,expected in proof['sourceHashes'].items():
 src=workspace/source;frozen=workspace/'work/nss65/proof-v1/code'/src.name
 assert sha(src)==sha(frozen)==expected and 'private'not in src.name and src.suffix in ('.mjs','.lua','.py')
 dst=root/'code'/source;dst.parent.mkdir(parents=True,exist_ok=True);key=dst.relative_to(root).as_posix()
 if key in items:assert items[key]['sha256']==expected
 shutil.copyfile(frozen,dst);items[key]={'path':key,'workspaceSource':source,'sha256':expected,'bytes':src.stat().st_size,'role':proof['role']}
save('evidence/nss65-source-proof.json',proof)
data=read('outputs/nss65-mainline-observations.json');audit=data['finalState']['protectedAudit']
assert data['routerConfigurationWrites']and data['publicationCandidateActuallyInstalled']and not data['candidateRetainedAtEnd']
assert data['rollback']['automaticExpiryWithoutControllerRollback']and not data['nssOpenedThisTurn']and audit['passed']
save('evidence/nss65-mainline.json',data)
save('evidence/nss65-pipeline.json',read('work/nss65/pipeline-sanitized.json'))
save('evidence/nss65-final-audit.json',read('work/nss65/final-health.json'))
save('evidence/current-runtime.json',{'round':'NSS65','checkedAt':data['observedAt'],'deploymentReference':data['deploymentReference'],
 'classifierConfigSha256':data['classifierConfigSha256'],
 'audit':{**audit,'protectedConfigurationUnchanged':audit['configurationMatches'],'exactOwnedNativeAudit':audit['originalFullLockedAudit'],'ecmClosedAndZero':audit['ecmStoppedAndZero']},
 'finalClosure':{'passed':all(audit[k]for k in ['noActiveTransaction','noStaging','noExperimentState','noExperimentalModule'])},
 'workerPid':audit['workerPid'],'guardianPid':audit['guardianPid'],'sameWorkerGuardianAndProducerSinceOpening':False,
 'expectedClassifierRestartForTrialAndRestore':True,'naturalWorkerRestartObservedThisTurn':False,
 'permanentClassifierChangedThisTurn':False,'experimentalConfigurationWritesThisTurn':True,'nssOpenedThisTurn':False,
 'qualifiedExperimentalEntry':'work/nss63/real-session.mjs','qualifiedExperimentalEntryBoundInputs':241,
 'entryPreparationQualified':True,'entryFullHighLoadForwardingQualified':False,'candidateEntryBindingCreated':False,
 'publicationCandidateInstalledDuringTrial':True,'publicationCandidateInstalled':False,
 'candidateWorkerSha256':data['candidateWorkerSha256'],'independentNatural180SecondUndoVerified':True,
 'nssPermanentlyEnabled':False,'completePerformanceAndGameAcceptance':False,'gameGuiOrNewDownloadPerformedThisTurn':False,
 'historical64RuntimePreservedSha256':sha(history),'historical63RuntimePreservedSha256':sha(root/'evidence/nss63-runtime.json'),'requiresLiveRevalidation':True})
manifest.update({'sources':list(items.values()),'lastAppendExport':'NSS65','privateDataExcluded':True,'generatedAt':datetime.now(timezone.utc).isoformat()})
save('source-manifest.json',manifest)
print(json.dumps({'exported':True,'round':'NSS65','newCuratedSources':proof['sources'],'totalCuratedSources':len(items),'rawPrivateDataCopied':False}))
