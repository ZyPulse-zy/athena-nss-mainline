"""Freeze only reviewed public source; full actual runtime inputs stay private."""
from pathlib import Path
import json,hashlib
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
common=['health.mjs','publication-trial.mjs','verify-rollback.mjs','cleanup-stage.mjs','observe-restored.lua',
 'observe-restored.mjs','observe-trial.lua','observe-trial.mjs','client-watchdog.ps1']
for number in (66,67):
 root=Path(f'work/nss{number}');names=common+(['bounded-load.mjs']if number==66 else['audit-load.mjs','summarize.py','freeze-proof.py'])
 dst=root/'proof-v1/code';dst.mkdir(parents=True,exist_ok=True);hashes={}
 for name in names:
  src=root/name;out=dst/name
  if out.exists():assert out.read_bytes()==src.read_bytes(),'Frozen source changed'
  else:out.write_bytes(src.read_bytes())
  hashes[src.as_posix()]=sha(src)
 proof={'sources':len(hashes),'sourceHashes':hashes,'privateConnectionAndCapturesExcluded':True,
  'notAdditionalProductionAdmission':True,'publicationCandidateInstalledDuringTrial':True,'candidateRetainedAtEnd':False,
  'productionNssEntryUnchanged':True,'role':'single-publication-boundary-real-download-trial-and-independent-natural-undo',
  'observerRuntimeOwnerPassedAsArgumentNotHardcoded':True,'original64And65ProofsUntouched':True}
 encoded=json.dumps(proof,ensure_ascii=False,indent=2)+'\n';p=root/'source-proof-v1.json'
 if p.exists():assert p.read_text(encoding='utf-8')==encoded
 else:p.write_text(encoded,encoding='utf-8',newline='\n')
 ctx=json.loads((root/'trial-private.json').read_text());runtime=[root/'trial-private.json']
 runtime.extend(Path(ctx['localDir'])/n for n in ['undo.sh','install.sh','new-worker.lua','new-config.json','old-worker.lua','old-config.json'])
 private=root/'proof-v1/private-runtime';private.mkdir(exist_ok=True);actual={}
 for src in runtime:
  out=private/src.name
  if out.exists():assert out.read_bytes()==src.read_bytes()
  else:out.write_bytes(src.read_bytes())
  actual[src.as_posix()]=sha(src)
 text=json.dumps({'sourceHashes':actual,'originalActualInputBytesFrozen':True},indent=2)+'\n'
 p=root/'runtime-proof-private.json'
 if p.exists():assert p.read_text()==text
 else:p.write_text(text,encoding='utf-8',newline='\n')
 print(json.dumps({'round':f'NSS{number}','frozenPublicSources':len(hashes),'actualPrivateInputsFrozen':len(actual),'nssPermissionAdded':False}))
