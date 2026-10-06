from pathlib import Path
r=Path(__file__).resolve().parent
def put(n,s):p=r/n;assert not p.exists();p.write_text(s,encoding='utf-8',newline='')
s=(r/'epoch-driver-v8.mjs').read_text(encoding='utf-8').replace("'./session-binding-v8.mjs'","'./session-binding-live.mjs'")
old="assert.ok(['work/nss157/run15/continuity-private.json','work/nss157/run15/successor-continuity-private.json','work/nss157/run16/continuity-private.json','work/nss157/run16/successor-continuity-private.json'].includes(continuityPath));"
assert s.count(old)==1
s=s.replace(old,"assert.match(continuityPath,/^work\\/nss157\\/pilot-(?:change|close)-\\d{14}-[a-f0-9]{16}\\/(?:successor-)?continuity-private\\.json$/);")
put('epoch-driver-live.mjs',s)
s=(r/'pilot-supervisor-v8.mjs').read_text(encoding='utf-8').replace("'./session-binding-v8.mjs'","'./session-binding-live.mjs'").replace("'./epoch-driver-v8.mjs'","'./epoch-driver-live.mjs'")
assert s.count("out=root+(scenario==='change'?'/run15':'/run16')")==1
s=s.replace("out=root+(scenario==='change'?'/run15':'/run16')","out=root+'/pilot-'+scenario+'-'+new Date().toISOString().replace(/\\D/g,'').slice(0,14)+'-'+crypto.randomBytes(8).toString('hex')")
s=s.replace("scenario,bindings:Object.keys(q.sourceManifest).length,desktopOperated:false","scenario,output:out,bindings:Object.keys(q.sourceManifest).length,desktopOperated:false")
put('pilot-supervisor-live.mjs',s)
put('session-binding-live.mjs',(r/'session-binding-v8.mjs').read_text(encoding='utf-8').replace("'./session-binding-v7.mjs'","'./session-binding-v8.mjs'").replace('/entry-qualified-v8.json','/entry-qualified-live.json'))
print('Each finite attempt now creates an exclusive UTC/random pilot directory; no old namespaces accepted or reused. Native/traffic limits unchanged.')
