"""Immutable allowlist for latest native candidate and sanitized-only source proof."""
from pathlib import Path
import hashlib,json
root=Path('work/nss64');names=[
 'health.mjs','profile.lua','run-profile.mjs','json-project.lua','project-fixtures.lua','compare-project.mjs',
 'flow-json.lua','flow-json-stream.lua','json-project-fast.lua','compare-encoding.mjs',
 'observe-pipeline.lua','observe-pipeline.mjs','encoding-scale.mjs','build-candidate.mjs','compile-candidate.mjs',
 'candidate-worker.lua','candidate-worker-manifest.json','summarize.py','freeze-proof.py','compile-qualified.json']
hashes={};dst=root/'proof-v1/code';dst.mkdir(parents=True,exist_ok=True)
for name in names:
 p=root/name;data=p.read_bytes();assert p.is_file()and 'private'not in name
 frozen=dst/name
 if frozen.exists():assert frozen.read_bytes()==data,'Cannot overwrite frozen '+name
 else:frozen.write_bytes(data)
 hashes[p.as_posix()]=hashlib.sha256(data).hexdigest()
proof={'sources':len(hashes),'sourceHashes':hashes,'privateConnectionAndCapturesExcluded':True,
 'notAdditionalProductionAdmission':True,'candidateInstalled':False,'productionEntryUnchanged':True,
 'role':'readonly-publication-latency-and-complete-encoding-candidate-latest-native-contract-and-exact-compile',
 'earlierSameRoundWrapperRevisionsNotClaimedByteIdentical':True,'original63ProofsUntouched':True}
p=root/'source-proof-v1.json';encoded=json.dumps(proof,ensure_ascii=False,indent=2)+'\n'
if p.exists():assert p.read_text(encoding='utf-8')==encoded
else:p.write_text(encoded,encoding='utf-8',newline='\n')
print(json.dumps({'passed':True,'frozenSources':len(hashes),'candidateInstalled':False,'additionalProductionAdmission':False}))
