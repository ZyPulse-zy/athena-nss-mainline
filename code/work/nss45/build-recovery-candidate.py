"""Reuse only the initial attested state for the first readonly undo inspection."""
import hashlib,json
from pathlib import Path
here=Path(__file__).resolve().parent;root=here.parents[1]
old=(root/'athena-nss-mainline/code/deployed-classifier/backend.lua').read_bytes()
dep=json.loads((root/'work/nss39/deployment-latest.json').read_text(encoding='utf-8-sig'))
cfg=json.loads((root/dep['localDir']/'config.json').read_text(encoding='utf-8-sig'))
sha=lambda b:hashlib.sha256(b).hexdigest();assert sha(old)==cfg['files']['backend.lua']
(here/'original-backend.lua').write_bytes(old)
s=old.decode();a="   local l=J.wans[tostring(w)];inspect(w)\n   local r=own.undo(C[w],l,{context={lockDelegated=true,workerStopped=true,transactionId=owner,boot=boot,deadline=1},\n    readBoot=R.boot,readRoot=function(dev)return R.queue(dev).handle end,\n    readNative=R.native,write=function(cmd)assert(cmd:sub(1,3)=='tc ');R.batch({cmd:sub(4)})end})"
b="""   local l=J.wans[tostring(w)];local initial=inspect(w)
   -- inspect(w) has already attested both full roots and parsed native state.
   -- Reuse it once for undo's initial enumeration only. Every write still has
   -- undo's original fresh prewrite and postwrite reads. Never cache after a write.
   local rootUsed,nativeUsed,wrote={},{},false
   local r=own.undo(C[w],l,{context={lockDelegated=true,workerStopped=true,transactionId=owner,boot=boot,deadline=1},
    readBoot=R.boot,readRoot=function(dev)
     if not wrote and not rootUsed[dev]then rootUsed[dev]=true;return assert(initial[dev]).handle end
     return R.queue(dev).handle
    end,
    readNative=function(dev,h)
     if not wrote and not nativeUsed[dev]then
      nativeUsed[dev]=true;assert(rootUsed[dev]and initial[dev].handle==h);return initial[dev].text
     end
     return R.native(dev,h)
    end,
    write=function(cmd)assert(cmd:sub(1,3)=='tc ');wrote=true;R.batch({cmd:sub(4)})end})"""
assert s.count(a)==1;s=s.replace(a,b)
(here/'candidate-backend.lua').write_text(s,encoding='utf-8',newline='\n')
out={'passed':True,'oldSha256':sha(old),'candidateSha256':sha(s.encode()),'onlyInitialRecoveryEnumerationChanged':True,'ownUndoUnchanged':True,'prewriteAndPostwriteReadsRetained':True,'cacheLifetime':'One initial inspection inside one WAN recovery; disabled after first actual write','deadlinesChanged':False,'installed':False}
(here/'recovery-candidate-manifest.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'built':True,'onlyBackendRecoveryChanged':True,'installed':False}))
