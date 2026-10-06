from pathlib import Path
r=Path(__file__).resolve().parent
def put(n,s):p=r/n;assert not p.exists();p.write_text(s,encoding='utf-8',newline='')
s=(r/'module-stage-v3.mjs').read_text(encoding='utf-8').replace("'./payload-v3.mjs'","'./payload-v4.mjs'").replace("'work/nss157/fast-path.lua'","'work/nss157/fast-path-v2.lua'");put('module-stage-v4.mjs',s)
put('epoch-driver-v7.mjs',(r/'epoch-driver-v6.mjs').read_text(encoding='utf-8').replace("'./session-binding-v6.mjs'","'./session-binding-v7.mjs'").replace("'./module-stage-v3.mjs'","'./module-stage-v4.mjs'").replace('/run11/','/run13/').replace('/run12/','/run14/'))
put('pilot-supervisor-v7.mjs',(r/'pilot-supervisor-v6.mjs').read_text(encoding='utf-8').replace("'./session-binding-v6.mjs'","'./session-binding-v7.mjs'").replace("'./epoch-driver-v6.mjs'","'./epoch-driver-v7.mjs'").replace("?'/run11':'/run12'","?'/run13':'/run14'"))
put('session-binding-v7.mjs',(r/'session-binding-v6.mjs').read_text(encoding='utf-8').replace("'./session-binding-v5.mjs'","'./session-binding-v6.mjs'").replace('/entry-qualified-v6.json','/entry-qualified-v7.json'))
print('Only native record alias corrected; fresh run13/run14 and original failed run11 preserved.')
