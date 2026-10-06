from pathlib import Path
r=Path(__file__).resolve().parent
def put(n,s):
 p=r/n;assert not p.exists();p.write_text(s,encoding='utf-8',newline='')
put('epoch-driver-v5.mjs',(r/'epoch-driver-v4.mjs').read_text(encoding='utf-8').replace("'./session-binding-v4.mjs'","'./session-binding-v5.mjs'").replace('/run7/','/run9/').replace('/run8/','/run10/'))
put('pilot-supervisor-v5.mjs',(r/'pilot-supervisor-v4.mjs').read_text(encoding='utf-8').replace("'./session-binding-v4.mjs'","'./session-binding-v5.mjs'").replace("'./epoch-driver-v4.mjs'","'./epoch-driver-v5.mjs'").replace("?'/run7':'/run8'","?'/run9':'/run10'"))
put('session-binding-v5.mjs',(r/'session-binding-v4.mjs').read_text(encoding='utf-8').replace("'./session-binding-v3.mjs'","'./session-binding-v4.mjs'").replace('/entry-qualified-v4.json','/entry-qualified-v5.json'))
print('Identical qualified mechanism; fresh run9/run10 preserve failed matching evidence and original fixed budgets.')
