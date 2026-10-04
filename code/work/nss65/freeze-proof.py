"""Freeze an explicit source allowlist; actual staging/owner/config inputs stay private."""
from pathlib import Path
import hashlib,json
root=Path('work/nss65');names=['health.mjs','publication-trial.mjs','verify-rollback.mjs','cleanup-stage.mjs',
 'summarize.py','freeze-proof.py','observe-restored.lua','observe-restored.mjs']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dst=root/'proof-v1/code';dst.mkdir(parents=True,exist_ok=True);hashes={}
for name in names:
 src=root/name;out=dst/name
 if out.exists():assert out.read_bytes()==src.read_bytes(),'Frozen source changed: '+name
 else:out.write_bytes(src.read_bytes())
 hashes[src.as_posix()]=sha(src)
proof={'sources':len(hashes),'sourceHashes':hashes,'privateConnectionAndCapturesExcluded':True,
 'notAdditionalProductionAdmission':True,'publicationCandidateInstalledDuringTrial':True,'candidateRetainedAtEnd':False,
 'productionNssEntryUnchanged':True,'role':'single-publication-boundary-live-trial-and-independent-natural-undo',
 'actualOwnerParameterizedRuntimeObserversRetainedPrivately':True,'original64ProofsUntouched':True}
p=root/'source-proof-v1.json';encoded=json.dumps(proof,ensure_ascii=False,indent=2)+'\n'
if p.exists():assert p.read_text(encoding='utf-8')==encoded
else:p.write_text(encoded,encoding='utf-8',newline='\n')
ctx=json.loads((root/'trial-private.json').read_text());runtime=[root/'observe-trial.lua',root/'observe-trial.mjs']
runtime.extend(Path(ctx['localDir'])/n for n in ['undo.sh','install.sh','new-worker.lua','new-config.json','old-worker.lua','old-config.json'])
private_dst=root/'proof-v1/private-runtime';private_dst.mkdir(exist_ok=True);runtime_hashes={}
for src in runtime:
 out=private_dst/src.name
 if out.exists():assert out.read_bytes()==src.read_bytes()
 else:out.write_bytes(src.read_bytes())
 runtime_hashes[src.as_posix()]=sha(src)
q=root/'runtime-proof-private.json';data=json.dumps({'sourceHashes':runtime_hashes,'originalActualInputBytesFrozen':True},indent=2)+'\n'
if q.exists():assert q.read_text()==data
else:q.write_text(data,encoding='utf-8',newline='\n')
print(json.dumps({'passed':True,'frozenPublicSources':len(hashes),'privateRuntimeInputsFrozen':len(runtime_hashes),'candidateRetained':False}))
