from pathlib import Path
r=Path('work/nss159')
def write(name,data):
    with (r/name).open('x',encoding='utf-8',newline='\n') as f:f.write(data)
write('close-endpoint-v2.mjs',(r/'close-endpoint.mjs').read_text(encoding='utf-8').replace('^nss157-','^nss159-'))
write('current-audit-diagnostic-v4.mjs',(r/'current-audit-diagnostic-v3.mjs').read_text(encoding='utf-8').replace("'./session-binding-v3.mjs'","'./session-binding-v4.mjs'"))
write('epoch-driver-v4.mjs',(r/'epoch-driver-v3.mjs').read_text(encoding='utf-8').replace('current-audit-diagnostic-v3.mjs','current-audit-diagnostic-v4.mjs').replace("'./session-binding-v3.mjs'","'./session-binding-v4.mjs'"))
write('pilot-supervisor-v4.mjs',(r/'pilot-supervisor-v3.mjs').read_text(encoding='utf-8').replace('current-audit-diagnostic-v3.mjs','current-audit-diagnostic-v4.mjs').replace("'./epoch-driver-v3.mjs'","'./epoch-driver-v4.mjs'").replace("'./session-binding-v3.mjs'","'./session-binding-v4.mjs'").replace('work/nss159/close-endpoint.mjs','work/nss159/close-endpoint-v2.mjs'))
write('session-binding-v4.mjs',(r/'session-binding-v3.mjs').read_text(encoding='utf-8').replace("'./session-binding-v2.mjs'","'./session-binding-v3.mjs'").replace('entry-qualified-v3.json','entry-qualified-v4.json'))
s=(r/'qualify-v4.mjs').read_text(encoding='utf-8')
s=s.replace("from './session-binding-v2.mjs'","from './session-binding-v3.mjs'")
s=s.replace("'session-binding-v3.mjs','qualify-v4.mjs'","'session-binding-v3.mjs','qualify-v4.mjs','prepare-v4.py','close-endpoint-v2.mjs','current-audit-diagnostic-v4.mjs','epoch-driver-v4.mjs','pilot-supervisor-v4.mjs','session-binding-v4.mjs','qualify-v5.mjs'")
s=s.replace("root+'/epoch-driver-v3.mjs'","root+'/epoch-driver-v4.mjs'").replace(".replace(\"'./session-binding-v3.mjs'\"", ".replace(\"'./session-binding-v4.mjs'\"").replace("replaceAll('current-audit-diagnostic-v3.mjs'","replaceAll('current-audit-diagnostic-v4.mjs'")
s=s.replace("root+'/policy-qualified-v3.json'","root+'/policy-qualified-v4.json'").replace("root+'/entry-qualified-v3.json'","root+'/entry-qualified-v4.json'").replace("import('./session-binding-v3.mjs')","import('./session-binding-v4.mjs')")
needle='const q={passed:true'
check="""assert.ok(fs.readFileSync(root+'/current-audit-diagnostic-v4.mjs','utf8').includes('nss159\\\\/'));
assert.ok(fs.readFileSync(root+'/close-endpoint-v2.mjs','utf8').includes('^nss159-'));
assert.ok(!fs.readFileSync(root+'/epoch-driver-v4.mjs','utf8').includes('work/nss49/current-audit-diagnostic-v'));
"""
assert needle in s;s=s.replace(needle,check+needle)
write('qualify-v5.mjs',s)
print('Bound exact endpoint unit namespace; historic original sources retained')
