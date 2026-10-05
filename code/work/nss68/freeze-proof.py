"""Public sources allowlisted; exact NSS bindings and private runtime stay local."""
from pathlib import Path
import json,hashlib
R=Path('work/nss68');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
names=['deployment-binding.mjs','prepare.py','commit-publication.mjs','qualify-entry.mjs','cleanup-stage.mjs','health.mjs','publication-retain.mjs','verify-rollback.mjs','read-real-candidates.mjs','record-candidates.mjs','wait-ready-candidate.mjs','wait-publication-metadata.mjs','current-audit-diagnostic.mjs','module-stage.mjs','real-session.mjs','session-binding.mjs','audit-load.mjs','observe-retained.lua','observe-retained.mjs','client-watchdog.ps1','read-worker-recovery.mjs','summarize.py','freeze-proof.py']
D=R/'proof-v1/code';D.mkdir(parents=True,exist_ok=True);hashes={}
for name in names:
    p=R/name;dst=D/name
    if dst.exists():assert dst.read_bytes()==p.read_bytes()
    else:dst.write_bytes(p.read_bytes())
    hashes[p.as_posix()]=sha(p)
ctx=json.loads((R/'deployment-latest.json').read_text());C=Path(ctx['localDir'])
runtime=[R/'trial-private.json',R/'deployment-latest.json',R/'entry-qualified.json']+[C/n for n in ['undo.sh','install.sh','old-worker.lua','old-config.json','new-worker.lua','new-config.json','permanent-commit.json','commit-raw-private.json','commit-remote-private.json']]
P=R/'proof-v1/private-runtime';P.mkdir(exist_ok=True);actual={}
for p in runtime:
    dst=P/p.name
    if dst.exists():assert dst.read_bytes()==p.read_bytes()
    else:dst.write_bytes(p.read_bytes())
    actual[p.as_posix()]=sha(p)
proof={'sources':len(hashes),'sourceHashes':hashes,'candidateRetainedAtEnd':True,'privateConnectionConfigurationAndCapturesExcluded':True,'old63And67ProofsUntouched':True,'newFlowPermissionGranted':False,'role':'qualified-publication-retention-and-explicit-deployment-consumer-audit-stage-overlay'}
for file,data in [(R/'source-proof-v1.json',proof),(R/'runtime-proof-private.json',{'sourceHashes':actual,'originalActualInputBytesFrozen':True})]:
    text=json.dumps(data,ensure_ascii=False,indent=2)+'\n'
    if file.exists():assert file.read_text(encoding='utf-8')==text
    else:file.write_text(text,encoding='utf-8',newline='\n')
print(json.dumps({'frozenPublicSources':len(hashes),'actualPrivateInputsFrozen':len(actual),'nssAdmission':False}))
