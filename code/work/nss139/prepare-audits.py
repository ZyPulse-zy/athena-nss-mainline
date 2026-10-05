from pathlib import Path
import json
w=Path(__file__).resolve().parents[2];r=w/'work/nss139'
for name in ['health.mjs','read-final-physical.mjs']:
 b=(w/'work/nss138'/name).read_bytes();n=b.replace(b'nss138',b'nss139').replace(b'NSS138',b'NSS139');assert n.replace(b'nss139',b'nss138').replace(b'NSS139',b'NSS138')==b;(r/name).write_bytes(n)
errors=[{'operation':'preflight health helper','error':'Argument pre-class-lifecycle rejected by required v[0-9]+ label; no router call executed','subsequentOriginalFullStageAuditsPassed':True},{'operation':'post-trial physical audit output','error':'EEXIST on write-exclusive receipt path; preflight evidence remained exact, so final audit moved to new NSS139 directory','oldEvidenceOverwritten':False}]
(r/'local-audit-invocation-failures.json').write_text(json.dumps(errors,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'preparedReadOnlyFinalAudits':True,'originalOutputsPreserved':True}))
