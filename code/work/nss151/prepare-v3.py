"""Bind the original capability inputs and correct one accidental old namespace alias."""
from pathlib import Path
import json,hashlib
r=Path(__file__).resolve().parent;w=r.parents[1]
def put(n,s):
 p=r/n;assert not p.exists(),n;p.write_text(s,encoding='utf-8',newline='')
for a,b in [('class-session-v2.mjs','class-session-v3.mjs'),('epoch-session-v2.mjs','epoch-session-v3.mjs')]:
 s=(r/a).read_text(encoding='utf-8').replace('./session-binding-v2.mjs','./session-binding-v3.mjs').replace('work/nss151/current-audit-diagnostic-v2.mjs','work/nss151/current-audit-diagnostic-v3.mjs').replace('work/nss49/current-audit-diagnostic-v2.mjs','work/nss49/current-audit-diagnostic.mjs').replace('work/nss151/run-v2/continuity-private.json','work/nss151/run-v3/continuity-private.json').replace('work/nss151/uplink-capacity-private.json','work/nss114/uplink-capacity-private.json')
 put(b,s)
put('current-audit-diagnostic-v3.mjs',(r/'current-audit-diagnostic-v2.mjs').read_text(encoding='utf-8').replace('./session-binding-v2.mjs','./session-binding-v3.mjs'))
put('run-v3.mjs',(r/'run-v2.mjs').read_text(encoding='utf-8').replace('./session-binding-v2.mjs','./session-binding-v3.mjs').replace("output=root+'/run-v2'","output=root+'/run-v3'").replace('frozen-qualified-inputs-v2','frozen-qualified-inputs-v3').replace('entry-source-manifest-v2.json','entry-source-manifest-v3.json').replace('current-audit-diagnostic-v2.mjs','current-audit-diagnostic-v3.mjs').replace('class-session-v2.mjs','class-session-v3.mjs').replace('epoch-session-v2.mjs','epoch-session-v3.mjs').replace('start-dallas.mjs','start-dallas-v3.mjs'))
put('start-dallas-v3.mjs',(r/'start-dallas.mjs').read_text(encoding='utf-8').replace("const unit='nss150-'","const unit='nss151-'"))
a=w/'work/nss138/uplink-capacity-private.json';b=w/'work/nss114/uplink-capacity-private.json'
assert json.loads(a.read_text(encoding='utf-8'))==json.loads(b.read_text(encoding='utf-8'))
put('capacity-alias-proof-private.json',json.dumps({'passed':True,'original138And114CapabilityDataSemanticEquality':True,'useSource':'work/nss114/uplink-capacity-private.json','sourceSha256':hashlib.sha256(b.read_bytes()).hexdigest(),'noCapacityValuesChanged':True},indent=2)+'\n')
put('runtime-v2-failure-private.json',json.dumps({'passed':False,'originalOutputsAnd1642Plus8BindingsPreserved':True,'reason':'Missing local uplink capability alias; an unintended nss49 diagnostic basename alias was also detected read-only before a checkpoint','checkpointCreated':False,'stageStarted':False,'ecmOpened':False,'endpointTrafficStarted':True,'correction':'Bind the two original private capability inputs; check all literal code dependencies before loading; use fresh unit prefix'},indent=2)+'\n')
print('Original capability inputs bound; no router state or capacity values changed.')
