"""Keep the row cap; type only a completed, bounded observation overload."""
import hashlib,json
from pathlib import Path
here=Path(__file__).resolve().parent;root=here.parents[1]
dep=json.loads((root/'work/nss39/deployment-latest.json').read_text(encoding='utf-8-sig'))
cfg=json.loads((root/dep['localDir']/'config.json').read_text(encoding='utf-8-sig'))
assert cfg['source']['maxSourceRows']==2048 and cfg['source']['maxSourceBytes']==524288
sha=lambda b:hashlib.sha256(b).hexdigest()
changes={}
def replace(s,a,b):
    assert s.count(a)==1,a
    return s.replace(a,b)
for name in ['worker.lua','guardian.lua','conntrack-source.lua']:
    original=(root/'athena-nss-mainline/code/deployed-classifier'/name).read_bytes()
    assert sha(original)==cfg['files'][name]
    (here/('original-'+name)).write_bytes(original)
    s=original.decode('utf-8')
    if name in ['worker.lua','guardian.lua']:
        needle=" if e.kind=='bounded-source-overflow'then return e.stream=='stdout'and e.limit==524288 end"
        s=replace(s,needle,needle+"\n if e.kind=='bounded-source-row-overflow'then return e.limit==2048 and e.observedRows==2049 end")
    if name=='worker.lua':
        s=replace(s,"return{rawStatus=0,stdout=streams[1].body,stderr=streams[2].body}","return{rawStatus=0,stdout=streams[1].body,stderr=streams[2].body,queryCleanupCompleted=true}")
        s=replace(s,"local detail={kind=snap.kind,stream=snap.stream,limit=snap.limit,reason=snap.reason,exitCode=snap.exitCode,queryCleanupCompleted=true,attempts=overflowAttempts,baselineRecoveryComplete=overflowRecovered}","local detail={kind=snap.kind,stream=snap.stream,limit=snap.limit,observedRows=snap.observedRows,reason=snap.reason,exitCode=snap.exitCode,queryCleanupCompleted=true,attempts=overflowAttempts,baselineRecoveryComplete=overflowRecovered}")
    if name=='conntrack-source.lua':
        s=replace(s,"rawRows=rawRows+1;assert(rawRows<=o.maxSourceRows,'Source rows exceed bound')","rawRows=rawRows+1;if rawRows>o.maxSourceRows then error({kind='bounded-source-row-overflow',limit=o.maxSourceRows,observedRows=rawRows},0)end")
        s=replace(s," local rows,summary=M.normalize(o,p,answer.stdout,answer.stderr,boot,r.now())"," local normalized,rows,summary=pcall(M.normalize,o,p,answer.stdout,answer.stderr,boot,r.now())\n if not normalized then\n  -- Only the existing query implementation can attest successful child reaping.\n  if type(rows)=='table'and rows.kind=='bounded-source-row-overflow'and\n   rows.limit==o.maxSourceRows and rows.observedRows==o.maxSourceRows+1 and\n   answer.queryCleanupCompleted==true then rows.queryCleanupCompleted=true end\n  error(rows,0)\n end")
    candidate=s.encode();(here/name).write_bytes(candidate)
    changes[name]={'oldSha256':sha(original),'candidateSha256':sha(candidate)}
out={'passed':True,'changedSources':changes,'sourceRowsLimit':2048,'sourceBytesLimit':524288,'deployed':False,'classifierPolicyChanged':False,'nssAdmissionChanged':False,'deadlinesChanged':False,'scope':'Only type a row overload after the original query has reaped; existing degraded withdrawal and exact recovery remain required.'}
(here/'row-candidate-manifest.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'built':True,'sourceChanges':3,'rowCapUnchanged':2048,'installed':False}))
