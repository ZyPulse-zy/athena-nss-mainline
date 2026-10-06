"""Correct only escaped audit namespace and use fresh output/binding paths."""
from pathlib import Path
import json,hashlib
r=Path(__file__).resolve().parent
def write(name,text):
 p=r/name;assert not p.exists(),name;p.write_text(text,encoding='utf-8',newline='')
a=(r/'current-audit-diagnostic.mjs').read_text().replace(r'work\/nss150',r'work\/nss151').replace('./session-binding.mjs','./session-binding-v2.mjs')
assert r'/^work\/nss151\/'in a and r'/^work\/nss150\/'not in a
write('current-audit-diagnostic-v2.mjs',a)
for old,new in [('class-session.mjs','class-session-v2.mjs'),('epoch-session.mjs','epoch-session-v2.mjs')]:
 s=(r/old).read_text().replace('./session-binding.mjs','./session-binding-v2.mjs').replace('current-audit-diagnostic.mjs','current-audit-diagnostic-v2.mjs').replace('work/nss151/run/continuity-private.json','work/nss151/run-v2/continuity-private.json')
 write(new,s)
s=(r/'run.mjs').read_text().replace('./session-binding.mjs','./session-binding-v2.mjs').replace("output=root+'/run'","output=root+'/run-v2'").replace("root+'/frozen-qualified-inputs'","root+'/frozen-qualified-inputs-v2'").replace('entry-source-manifest.json','entry-source-manifest-v2.json').replace('current-audit-diagnostic.mjs','current-audit-diagnostic-v2.mjs').replace('class-session.mjs','class-session-v2.mjs').replace('epoch-session.mjs','epoch-session-v2.mjs')
write('run-v2.mjs',s)
write('qualification-v2/live-preflight-failure-private.json',json.dumps({'passed':False,'originalSourceInputsAndOutputPreserved':True,'reason':'Escaped audit path regex retained nss150 while plain path strings correctly changed to nss151','routerConnected':False,'endpointTrafficStarted':False,'checkpointCreated':False,'ecmOpened':False,'correction':'Only escaped case namespace and new versioned source/output/bindings'},indent=2)+'\n')
print('Namespace rejection preserved; new versioned sources prepared.')
