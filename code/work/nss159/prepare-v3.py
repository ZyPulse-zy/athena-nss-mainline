from pathlib import Path
r=Path('work/nss159')
def write(name,data):
    with (r/name).open('x',encoding='utf-8',newline='\n') as f:f.write(data)
s=(r/'current-audit-diagnostic-v2.mjs').read_text(encoding='utf-8')
write('current-audit-diagnostic-v3.mjs',s.replace("'./session-binding-v2.mjs'","'./session-binding-v3.mjs'"))
s=(r/'epoch-driver-v2.mjs').read_text(encoding='utf-8')
assert 'work/nss49/current-audit-diagnostic-v2.mjs' in s
s=s.replace('work/nss49/current-audit-diagnostic-v2.mjs','work/nss49/current-audit-diagnostic.mjs')
s=s.replace('work/nss159/current-audit-diagnostic-v2.mjs','work/nss159/current-audit-diagnostic-v3.mjs')
write('epoch-driver-v3.mjs',s.replace("'./session-binding-v2.mjs'","'./session-binding-v3.mjs'"))
s=(r/'pilot-supervisor-v2.mjs').read_text(encoding='utf-8')
s=s.replace('current-audit-diagnostic-v2.mjs','current-audit-diagnostic-v3.mjs').replace("'./epoch-driver-v2.mjs'","'./epoch-driver-v3.mjs'").replace("'./session-binding-v2.mjs'","'./session-binding-v3.mjs'")
write('pilot-supervisor-v3.mjs',s)
s=(r/'session-binding-v2.mjs').read_text(encoding='utf-8').replace("'./session-binding.mjs'","'./session-binding-v2.mjs'").replace('entry-qualified-v2.json','entry-qualified-v3.json')
write('session-binding-v3.mjs',s)
s=(r/'qualify-v3.mjs').read_text(encoding='utf-8')
s=s.replace("from './session-binding.mjs'","from './session-binding-v2.mjs'")
s=s.replace("'session-binding-v2.mjs','qualify-v3.mjs'","'session-binding-v2.mjs','qualify-v3.mjs','prepare-v3.py','current-audit-diagnostic-v3.mjs','epoch-driver-v3.mjs','pilot-supervisor-v3.mjs','session-binding-v3.mjs','qualify-v4.mjs'")
s=s.replace("root+'/epoch-driver-v2.mjs'","root+'/epoch-driver-v3.mjs'").replace(".replace(\"'./session-binding-v2.mjs'\"", ".replace(\"'./session-binding-v3.mjs'\"")
s=s.replace("replaceAll('current-audit-diagnostic-v2.mjs'","replaceAll('current-audit-diagnostic-v3.mjs'")
s=s.replace("root+'/policy-qualified-v2.json'","root+'/policy-qualified-v3.json'").replace("root+'/entry-qualified-v2.json'","root+'/entry-qualified-v3.json'").replace("import('./session-binding-v2.mjs')","import('./session-binding-v3.mjs')")
needle="const p=spawnSync(process.execPath,[root+'/policy-tests.mjs']"
assert needle in s
extra="""const literalSourceDependencies=[];
for(const name of names.filter(n=>n.endsWith('.mjs'))){const text=fs.readFileSync(root+'/'+name,'utf8');
 for(const m of text.matchAll(/(?:readFileSync|runNode|run)\\(\\s*['\"](work\\/[^'\"]+)['\"]/g)){
  if(!/\\.(?:mjs|lua|py|ps1)$/.test(m[1]))continue;
  assert.ok(m[1] in old.sourceManifest||names.includes(path.posix.relative(root,m[1])),'Unbound literal source '+m[1]);assert.ok(fs.existsSync(m[1]));literalSourceDependencies.push(m[1]);
 }
}
"""
s=s.replace(needle,extra+needle)
s=s.replace('fixturePolicyCases:model.cases','fixturePolicyCases:model.cases,staticLiteralSourceDependenciesActuallyChecked:[...new Set(literalSourceDependencies)],oldQualificationMissedLiteralDependencyPreserved:true')
write('qualify-v4.mjs',s)
print('New sources preserve old dependency failure; static literal source checks added')
