"""Freeze an explicit readable-source allowlist. Do not copy raw runtime data."""
from pathlib import Path
import json, hashlib, shutil
root=Path('work/nss53')
names=['selection-diagnostic.lua','build-candidate.mjs','classifier.lua','classifier-delta.json',
       'core-guard-phase.lua','candidate-summary.json','test-diagnostics.mjs',
       'test-ready-readonly.mjs','test-ready-steam-load.mjs','trace-readonly.mjs',
       'build-entry.mjs','qualification.mjs','session-binding.mjs','module-stage.mjs',
       'real-session.mjs','qualify-entry.mjs','phase-qualified.json','entry-qualified.json',
       'current-audit-diagnostic.mjs','cleanup-audit.mjs','diagnostic-qualified.json',
       'ready-readonly-qualified.json','summarize.py','freeze-safe-sources.py']
assert len(names)==len(set(names))==24
out=root/'proof-v1/code'
assert not out.exists()
out.mkdir(parents=True)
hashes={}
for name in names:
    file=root/name
    assert 'private' not in name and file.suffix in ('.lua','.mjs','.json','.py')
    file.read_text(encoding='utf-8')
    hashes[file.as_posix()]=hashlib.sha256(file.read_bytes()).hexdigest()
    shutil.copyfile(file,out/name)
proof={'round':'NSS53','sources':len(hashes),'sourceHashes':hashes,
       'privateConnectionAndCapturesExcluded':True,'notAdditionalProductionAdmission':True,
       'candidateAndExperimentalEntryNotResidentClassifier':True,
       'sameCurrentSourceBindingVerifiedSeparately':True}
(root/'source-proof-v1.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'frozen':True,'sources':len(hashes),'rawPrivateEvidenceCopied':False}))
