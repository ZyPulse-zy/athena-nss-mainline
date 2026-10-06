"""Use the native state-node ownership derivation and exact baseline receipt name."""
from pathlib import Path
import json
r=Path(__file__).resolve().parent
def put(n,s):
    p=r/n;assert not p.exists(),n;p.write_text(s,encoding='utf-8',newline='')
for n in ['epoch-session','current-audit-diagnostic','crash-controller']:
    s=(r/(n+'.mjs')).read_text(encoding='utf-8').replace('./session-binding.mjs','./session-binding-v2.mjs').replace('work/nss152/run/continuity-private.json','work/nss152/run-v2/continuity-private.json')
    if n=='epoch-session':s=s.replace('work/nss152/current-audit-diagnostic.mjs','work/nss152/current-audit-diagnostic-v2.mjs')
    if n=='crash-controller':
        for a,b in [("out=root+'/run'","out=root+'/run-v2'"),('frozen-qualified-inputs','frozen-qualified-inputs-v2'),('entry-source-manifest.json','entry-source-manifest-v2.json'),("root+'/current-audit-diagnostic.mjs'","root+'/current-audit-diagnostic-v2.mjs'"),("root+'/epoch-session.mjs'","root+'/epoch-session-v2.mjs'"),('before-baseline-private','before-private')]:s=s.replace(a,b)
        s=s.replace("assert.match(ctx.plan.statePath,", "assert.match(ctx.plan.owner,/^[a-f0-9]{32}$/);ctx.statePath='/root/router-project/experiments/rp-nss25-state-'+ctx.plan.owner+'/ecm-state';assert.match(ctx.statePath,")
        s=s.replace('"lua - "+ctx.plan.statePath+', '"lua - "+ctx.statePath+')
    put(n+'-v2.mjs',s)
put('initial-static-refusal-private.json',json.dumps({'passed':False,'productionExecution':False,'reason':'Serialized plan has no statePath: native state-node setup derives it from owner; exact baseline receipt is before-private.json','correction':'Derive the same owned state path, use the actual baseline filename, preserve original controller source'},indent=2)+'\n')
print('State-node derivation and original baseline filename corrected before load.')
