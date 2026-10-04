"""Explicit NSS64 export. Preserve historical runtime bytes and private material."""
from pathlib import Path
from datetime import datetime, timezone
import argparse,json,hashlib,shutil
p=argparse.ArgumentParser();p.add_argument('workspace',type=Path);workspace=p.parse_args().workspace.resolve()
root=Path(__file__).resolve().parents[1]
def read(path):return json.loads((workspace/path).read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,obj):(root/path).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
current=root/'evidence/current-runtime.json';old=root/'evidence/nss63-runtime.json'
if not old.exists():
 assert json.loads(current.read_text())['round']=='NSS63';shutil.copyfile(current,old)
assert json.loads(old.read_text())['round']=='NSS63'
assert json.loads(current.read_text())['round'] in ('NSS63','NSS64')
proof=read('work/nss64/source-proof-v1.json');assert proof['notAdditionalProductionAdmission'] and not proof['candidateInstalled']
manifest=json.loads((root/'source-manifest.json').read_text());items={x['path']:x for x in manifest['sources']}
for source,expected in proof['sourceHashes'].items():
 src=workspace/source;frozen=workspace/'work/nss64/proof-v1/code'/src.name
 assert sha(src)==sha(frozen)==expected and 'private'not in src.name and src.suffix in ('.mjs','.lua','.json','.py')
 dst=root/'code'/source;dst.parent.mkdir(parents=True,exist_ok=True);key=dst.relative_to(root).as_posix()
 if key in items:assert items[key]['sha256']==expected
 shutil.copyfile(frozen,dst);items[key]={'path':key,'workspaceSource':source,'sha256':expected,'bytes':src.stat().st_size,'role':proof['role']}
save('evidence/nss64-source-proof.json',proof)
data=read('outputs/nss64-mainline-observations.json')
assert not data['routerConfigurationWrites'] and not data['ecmOpenedThisTurn'] and data['finalState']['protectedAudit']['passed']
save('evidence/nss64-mainline.json',data)
for dest,src in {
 'nss64-encoding':'work/nss64/encoding-corrected.json','nss64-scale':'work/nss64/scale1-scale.json',
 'nss64-pipeline':'work/nss64/pipeline-sanitized.json','nss64-latency':'work/nss64/historical63-latency-sanitized.json',
 'nss64-compile':'work/nss64/compile-qualified.json','nss64-final-audit':'work/nss64/final-health.json'}.items():save('evidence/'+dest+'.json',read(src))
audit=data['finalState']['protectedAudit']
save('evidence/current-runtime.json',{
 'round':'NSS64','checkedAt':data['observedAt'],'deploymentReference':data['deploymentReference'],
 'classifierConfigSha256':data['classifierConfigSha256'],
 'audit':{**audit,'protectedConfigurationUnchanged':audit['configurationMatches'],
  'exactOwnedNativeAudit':audit['originalFullLockedAudit'],'ecmClosedAndZero':audit['ecmStoppedAndZero']},
 'finalClosure':{'passed':all(audit[k]for k in ['noActiveTransaction','noStaging','noExperimentState','noExperimentalModule'])},
 'workerPid':audit['workerPid'],'guardianPid':audit['guardianPid'],'sameWorkerGuardianAndProducerSinceOpening':True,
 'permanentClassifierChangedThisTurn':False,'experimentalConfigurationWritesThisTurn':False,'nssOpenedThisTurn':False,
 'naturalWorkerRestartObservedThisTurn':False,'qualifiedExperimentalEntry':'work/nss63/real-session.mjs',
 'qualifiedExperimentalEntryBoundInputs':241,'entryPreparationQualified':True,'entryFullHighLoadForwardingQualified':False,
 'publicationCandidateInstalled':False,'candidateWorkerSha256':data['candidateWorker']['candidateWorkerSha256'],
 'candidateCompiledInTargetRamOnly':True,'nssPermanentlyEnabled':False,'completePerformanceAndGameAcceptance':False,
 'gameGuiOrNewDownloadPerformedThisTurn':False,'historical63RuntimePreservedSha256':sha(old),'requiresLiveRevalidation':True})
manifest.update({'sources':list(items.values()),'lastAppendExport':'NSS64','privateDataExcluded':True,'generatedAt':datetime.now(timezone.utc).isoformat()})
save('source-manifest.json',manifest)
print(json.dumps({'exported':True,'round':'NSS64','newCuratedSources':proof['sources'],'totalCuratedSources':len(items),'rawPrivateDataCopied':False}))
