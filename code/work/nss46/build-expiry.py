"""Typed software expiry: withdraw data, recover precisely, then observe afresh."""
import hashlib,json
from pathlib import Path
here=Path(__file__).resolve().parent;root=here.parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
def replace(s,a,b):
    assert s.count(a)==1,a
    return s.replace(a,b)
policy=r'''
 if e.kind=='bounded-software-snapshot-expiry'then
  return e.limit==6 and e.mutationChildCleanupCompleted==true and
   type(e.sourceStartedAt)=='number'and e.sourceStartedAt>=0 and e.sourceStartedAt<math.huge and
   type(e.checkedAt)=='number'and e.checkedAt<math.huge and e.checkedAt>=e.sourceStartedAt+6
 end'''
proof={}
for name in ['worker.lua','guardian.lua']:
    raw=(root/'work/nss45'/('original-'+name)).read_bytes();s=raw.decode()
    needle=" if e.kind=='bounded-source-overflow'then return e.stream=='stdout'and e.limit==524288 end"
    s=replace(s,needle,needle+policy)
    if name=='worker.lua':
        s=replace(s,"checkFresh=function(s)permission();assert(s==snapshotInUse and now()<s.provenance.startedAtUptime+6,'Classifier snapshot stale before write')end,",r'''checkFresh=function(s)
  permission();assert(s==snapshotInUse,'Classifier snapshot identity changed')
  local at=now();local began=assert(s.provenance.startedAtUptime)
  if not(at<began+6)then error({kind='bounded-software-snapshot-expiry',limit=6,sourceStartedAt=began,checkedAt=at},0)end
 end,''')
        s=replace(s,"  permission();local backend=Backend.new(cfg,R,own);v.changes=backend.reconcile(snapshotInUse);v.snapshot=snapshotInUse",r'''  permission();local backend=Backend.new(cfg,R,own)
  local reconciled,changes=pcall(backend.reconcile,snapshotInUse)
  if reconciled then v.changes=changes;v.snapshot=snapshotInUse
  elseif type(changes)=='table'and changes.kind=='bounded-software-snapshot-expiry'and
   changes.limit==6 and changes.sourceStartedAt==snapshotInUse.provenance.startedAtUptime and
   type(changes.checkedAt)=='number'and changes.checkedAt>=changes.sourceStartedAt+6 then
   v.observationExpired=changes
  else error(changes,0)end''')
        # This function runs only after the original bounded mutation runner returned 0.
        helper=r'''
local function recoverSoftwareExpiry(snap,result)
 local expired=assert(result.observationExpired)
 assert(result.producer==producer and result.querySequence==snap.provenance.sequence)
 assert(expired.sourceStartedAt==snap.provenance.startedAtUptime and expired.checkedAt<=now())
 assert(result.snapshot==nil and result.changes==nil and not result.deferred)
 local detail={kind=expired.kind,limit=expired.limit,sourceStartedAt=expired.sourceStartedAt,checkedAt=expired.checkedAt,
  queryCleanupCompleted=true,mutationChildCleanupCompleted=true,baselineRecoveryComplete=false}
 assert(Overload.accept(detail),'Unqualified software expiry')
 publishClassification('degraded',nil,detail.kind,detail);publish('degraded',nil,detail.kind,detail)
 step('discard-observation-history')
 withMutation('recover');detail.baselineRecoveryComplete=true
 publishClassification('degraded',nil,detail.kind,detail);publish('degraded',nil,detail.kind,detail)
 return true
end
'''
        s=replace(s,'local overflowEpisode=false;local overflowRecovered=false;local overflowAttempts=0',helper+'\nlocal overflowEpisode=false;local overflowRecovered=false;local overflowAttempts=0')
        s=replace(s,'  overflowEpisode=false;overflowRecovered=false;snapshotInUse=snap','  overflowEpisode=false;overflowRecovered=false;snapshotInUse=snap;local softwareExpired=false')
        s=replace(s,'   if not result.deferred then snap=SoftwareRequest.merge(snap,result) else',"   if result.observationExpired then softwareExpired=recoverSoftwareExpiry(snap,result)\n   elseif not result.deferred then snap=SoftwareRequest.merge(snap,result) else")
        s=replace(s,"  if now()-auditAt>=30 and activeOwner()then withMutation('audit');auditAt=now()end\n  publish('running',snap)","  if not softwareExpired then\n   if now()-auditAt>=30 and activeOwner()then withMutation('audit');auditAt=now()end\n   publish('running',snap)\n  end")
    target=here/('stale-'+name);target.write_text(s,encoding='utf-8',newline='\n')
    proof[name]={'baseNss39Sha256':sha(raw),'staleCandidateSha256':sha(s.encode())}
out={'passed':True,'sources':proof,'sourceRowsLimit':2048,'softwareSourceDeadlineSeconds':6,'mutationRunnerSeconds':6,'guardianFreshnessSeconds':9,'installed':False,'nssPermitGranted':False,'unknownErrorsStayTerminal':True,'requiresExactOwnedRecovery':True,'scope':'Candidate typed software source expiry; no deadline extension. Expiry-only change relative to NSS39; row handling unchanged.'}
(here/'stale-candidate-manifest.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'built':True,'softwareDeadlineUnchanged':6,'installed':False}))
