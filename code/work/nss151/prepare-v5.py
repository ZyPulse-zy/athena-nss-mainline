"""Give every readonly preflight a unique evidence label, preserving prior attempts."""
from pathlib import Path
import json
r = Path(__file__).resolve().parent
def put(n,s):
    p=r/n
    assert not p.exists(),n
    p.write_text(s,encoding='utf-8',newline='')
for n in ['class-session','epoch-session','current-audit-diagnostic','run']:
    s=(r/(n+'-v4.mjs')).read_text(encoding='utf-8')
    s=s.replace('./session-binding-v4.mjs','./session-binding-v5.mjs')
    for a,b in [('work/nss151/current-audit-diagnostic-v4.mjs','work/nss151/current-audit-diagnostic-v5.mjs'),('work/nss151/run-v4/continuity-private.json','work/nss151/run-v5/continuity-private.json')]:
        s=s.replace(a,b)
    if n=='run':
        for a,b in [("output=root+'/run-v4'","output=root+'/run-v5'"),('frozen-qualified-inputs-v4','frozen-qualified-inputs-v5'),('entry-source-manifest-v4.json','entry-source-manifest-v5.json'),("root+'/current-audit-diagnostic-v4.mjs'","root+'/current-audit-diagnostic-v5.mjs'"),("root+'/class-session-v4.mjs'","root+'/class-session-v5.mjs'"),("root+'/epoch-session-v4.mjs'","root+'/epoch-session-v5.mjs'"),("['class-transition-preflight','prewrite',pre]","[pre.split('/').at(-1)+'-preflight','prewrite',pre]")]:
            s=s.replace(a,b)
    put(n+'-v5.mjs',s)
put('runtime-v4-failure-private.json',json.dumps({'passed':False,'reason':'Readonly preflight reused a write-exclusive evidence label from v2; EEXIST refused before endpoint load or checkpoint','checkpointCreated':False,'stageStarted':False,'ecmOpened':False,'correction':'Label each audit with its unique case directory; preserve existing files'},indent=2)+'\n')
print('Unique readonly preflight labels prepared; all old evidence retained.')
