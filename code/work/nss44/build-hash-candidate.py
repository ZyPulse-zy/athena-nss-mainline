"""Uninstalled candidate. Publication, lifecycle, classifier rules and bounds unchanged."""
from pathlib import Path
import hashlib,json
r=Path('work/nss44');source=Path('work/nss39/worker.lua').read_text(encoding='utf-8');helper=(r/'hash-batch.lua').read_text(encoding='utf-8')
a=source.index('for name,h in pairs(cfg.files)do');b=source.index('local own=assert(dofile',a)
old=source[a:b]
assert old.count('direct(')==1 and old.count('Payload bytes changed')==1
new='local PayloadHash=(function()\n'+helper+'\nend)()\nlocal payloadHashCommand,payloadHashCap=PayloadHash.command(base,cfg.files)\nPayloadHash.verify(base,cfg.files,direct(payloadHashCommand,payloadHashCap))\n'
candidate=source[:a]+new+source[b:]
(r/'candidate-worker.lua').write_text(candidate,encoding='utf-8',newline='\n')
sha=lambda s:hashlib.sha256(s.encode()).hexdigest()
(r/'candidate-hash-manifest.json').write_text(json.dumps({'installed':False,'candidateOnly':True,'oldWorkerSha256':sha(source),'candidateWorkerSha256':sha(candidate),'helperSha256':sha(helper),
 'onlyChange':'Batch payload checksums; every payload checked each worker invocation. Config checksum remains first and separate.',
 'publicationLifecycleRuleAndDeadlineByteEquivalent':source[b:]==candidate[candidate.index('local own=assert(dofile'):],
 'hashesCached':False,'externalProcessCountPerPayloadVerification':'number of payloads -> one','routerWrites':False},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'built':True,'installed':False,'candidateWorkerSha256':sha(candidate),'publicationLifecycleRuleAndDeadlineByteEquivalent':True}))
