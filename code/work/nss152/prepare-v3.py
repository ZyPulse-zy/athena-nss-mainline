"""Close every executable namespace edge before the single crash test."""
from pathlib import Path
import json
r=Path(__file__).resolve().parent
def put(n,s):
    p=r/n;assert not p.exists(),n;p.write_text(s,encoding='utf-8',newline='')
for n in ['read-controlled','match-controlled','health','read-final-physical','start-dallas','epoch-session','current-audit-diagnostic','crash-controller']:
    source=n+('-v2.mjs' if n in ['epoch-session','current-audit-diagnostic','crash-controller'] else '.mjs')
    s=(r/source).read_text(encoding='utf-8').replace("'work/nss151'", "'work/nss152'").replace('NSS151_PASSIVE_READY','NSS152_PASSIVE_READY').replace('./session-binding-v2.mjs','./session-binding-v3.mjs').replace('work/nss152/run-v2/continuity-private.json','work/nss152/run-v3/continuity-private.json')
    if n=='match-controlled':s=s.replace('work/nss152/read-controlled.mjs','work/nss152/read-controlled-v3.mjs')
    if n=='epoch-session':s=s.replace("observationRoot+'/read-controlled.mjs'","observationRoot+'/read-controlled-v3.mjs'").replace('work/nss152/current-audit-diagnostic-v2.mjs','work/nss152/current-audit-diagnostic-v3.mjs')
    if n=='crash-controller':
        for a,b in [("out=root+'/run-v2'","out=root+'/run-v3'"),('frozen-qualified-inputs-v2','frozen-qualified-inputs-v3'),('entry-source-manifest-v2.json','entry-source-manifest-v3.json'),("root+'/start-dallas.mjs'","root+'/start-dallas-v3.mjs'"),("root+'/match-controlled.mjs'","root+'/match-controlled-v3.mjs'"),("root+'/epoch-session-v2.mjs'","root+'/epoch-session-v3.mjs'"),("root+'/current-audit-diagnostic-v2.mjs'","root+'/current-audit-diagnostic-v3.mjs'")]:s=s.replace(a,b)
    put(n+'-v3.mjs',s)
put('namespace-preflight-refusal-private.json',json.dumps({'passed':False,'productionExecution':False,'reason':'Launcher passive-ready marker and bare root/observationRoot still referenced NSS151; discovered before connecting endpoints','correction':'Version every affected helper and bind all executable namespaces; original sources kept'},indent=2)+'\n')
print('All new executable namespaces closed before background traffic.')
