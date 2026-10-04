"""Explicit export of NSS66/67 sources and already sanitized measured evidence."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,shutil
p=argparse.ArgumentParser();p.add_argument('workspace',type=Path);workspace=p.parse_args().workspace.resolve()
root=Path(__file__).resolve().parents[1]
def read(p):return json.loads((workspace/p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,o):(root/p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
current=root/'evidence/current-runtime.json';history=root/'evidence/nss65-runtime.json'
if not history.exists():
 assert json.loads(current.read_text())['round']=='NSS65';shutil.copyfile(current,history)
assert json.loads(history.read_text())['round']=='NSS65'
assert json.loads(current.read_text())['round']in ('NSS65','NSS67')
manifest=json.loads((root/'source-manifest.json').read_text());items={x['path']:x for x in manifest['sources']}
summaries={};total_new=0
for number in (66,67):
 proof=read(f'work/nss{number}/source-proof-v1.json')
 assert proof['sources']==len(proof['sourceHashes'])and proof['notAdditionalProductionAdmission']and not proof['candidateRetainedAtEnd']
 for source,expected in proof['sourceHashes'].items():
  src=workspace/source;frozen=workspace/f'work/nss{number}/proof-v1/code'/src.name
  assert sha(src)==sha(frozen)==expected and 'private'not in src.name and src.suffix in ('.mjs','.lua','.py','.ps1')
  dst=root/'code'/source;dst.parent.mkdir(parents=True,exist_ok=True);key=dst.relative_to(root).as_posix()
  if key in items:assert items[key]['sha256']==expected
  else:total_new+=1
  shutil.copyfile(frozen,dst);items[key]={'path':key,'workspaceSource':source,'sha256':expected,'bytes':src.stat().st_size,'role':proof['role']}
 data=read(f'outputs/nss{number}-mainline-observations.json');audit=data['finalState']['protectedAudit']
 assert data['publicationCandidateActuallyInstalled']and data['rollback']['automaticExpiryWithoutControllerRollback']
 assert not data['candidateRetainedAtEnd']and not data['nssOpenedThisTurn']and audit['passed']
 save(f'evidence/nss{number}-source-proof.json',proof);save(f'evidence/nss{number}-mainline.json',data)
 save(f'evidence/nss{number}-pipeline.json',read(f'work/nss{number}/pipeline-sanitized.json'))
 save(f'evidence/nss{number}-final-audit.json',audit);summaries[number]=data
data=summaries[67];audit=data['finalState']['protectedAudit']
def runtime(data):
 a=data['finalState']['protectedAudit']
 return {'round':data['round'],'checkedAt':data['observedAt'],'deploymentReference':data['deploymentReference'],
  'classifierConfigSha256':data['classifierConfigSha256'],
  'audit':{**a,'protectedConfigurationUnchanged':a['configurationMatches'],'exactOwnedNativeAudit':a['originalFullLockedAudit'],'ecmClosedAndZero':a['ecmStoppedAndZero']},
  'finalClosure':{'passed':all(a[k]for k in ['noActiveTransaction','noStaging','noExperimentState','noExperimentalModule'])},
  'workerPid':a['workerPid'],'guardianPid':a['guardianPid'],'sameWorkerGuardianAndProducerSinceOpening':False,
  'expectedClassifierRestartForTrialAndRestore':True,'naturalWorkerRestartObservedThisTurn':False,
  'permanentClassifierChangedThisTurn':False,'experimentalConfigurationWritesThisTurn':True,'nssOpenedThisTurn':False,
  'qualifiedExperimentalEntry':'work/nss63/real-session.mjs','qualifiedExperimentalEntryBoundInputs':241,
  'entryPreparationQualified':True,'entryFullHighLoadForwardingQualified':False,'candidateEntryBindingCreated':False,
  'publicationCandidateInstalledDuringTrial':True,'publicationCandidateInstalled':False,'candidateWorkerSha256':data['candidateWorkerSha256'],
  'independentNatural180SecondUndoVerified':True,'nssPermanentlyEnabled':False,'completePerformanceAndGameAcceptance':False,
  'steamDownloadControlledThisTurn':True,'gameStartedThisTurn':False,'realHumanMetricsAvailable':False,
  'above300MbpsPublicationActuallyObserved':data['conclusions']['testedAbove300MbpsPublicationWindowSupported'],
  'clientDownloadFinallyPausedOrCompleted':True,'requiresLiveRevalidation':True}
save('evidence/nss66-runtime.json',runtime(summaries[66]))
latest=runtime(data);latest['historical65RuntimePreservedSha256']=sha(history)
latest['historical64RuntimePreservedSha256']=sha(root/'evidence/nss64-runtime.json')
latest['historical63RuntimePreservedSha256']=sha(root/'evidence/nss63-runtime.json')
save('evidence/current-runtime.json',latest)
manifest.update({'sources':list(items.values()),'lastAppendExport':'NSS67','privateDataExcluded':True,'generatedAt':datetime.now(timezone.utc).isoformat()})
save('source-manifest.json',manifest)
print(json.dumps({'exported':True,'rounds':['NSS66','NSS67'],'newCuratedSources':total_new,'totalCuratedSources':len(items),'rawPrivateDataCopied':False}))
