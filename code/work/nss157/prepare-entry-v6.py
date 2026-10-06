from pathlib import Path
r=Path(__file__).resolve().parent
def put(n,s):
 p=r/n;assert not p.exists();p.write_text(s,encoding='utf-8',newline='')
s=(r/'module-stage-v2.mjs').read_text(encoding='utf-8');assert s.count("'work/nss157/classifier-current-full.lua'")==1;put('module-stage-v3.mjs',s.replace("'work/nss157/classifier-current-full.lua'","'work/nss157/classifier-complete-wait.lua'"))
put('epoch-driver-v6.mjs',(r/'epoch-driver-v5.mjs').read_text(encoding='utf-8').replace("'./session-binding-v5.mjs'","'./session-binding-v6.mjs'").replace("'./module-stage-v2.mjs'","'./module-stage-v3.mjs'").replace('/run9/','/run11/').replace('/run10/','/run12/'))
put('pilot-supervisor-v6.mjs',(r/'pilot-supervisor-v5.mjs').read_text(encoding='utf-8').replace("'./session-binding-v5.mjs'","'./session-binding-v6.mjs'").replace("'./epoch-driver-v5.mjs'","'./epoch-driver-v6.mjs'").replace("?'/run9':'/run10'","?'/run11':'/run12'"))
put('session-binding-v6.mjs',(r/'session-binding-v5.mjs').read_text(encoding='utf-8').replace("'./session-binding-v4.mjs'","'./session-binding-v5.mjs'").replace('/entry-qualified-v5.json','/entry-qualified-v6.json'))
print('Bounded source-publication wait only; new run11/run12, fresh independent checkpoint each epoch.')
