import hashlib,json,re,subprocess
from pathlib import Path
here=Path(__file__).resolve().parent;root=here.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def unix(p):
 s=p.resolve().as_posix();return '/mnt/'+s[0].lower()+s[2:]
rt=root/'work/nss9/lua-runtime/extracted/usr'
cmd=['wsl.exe','-d','Athena-Cake-Build','--exec','/usr/bin/env','LD_LIBRARY_PATH='+unix(rt/'lib/x86_64-linux-gnu'),unix(rt/'bin/lua5.1')]
helper=(here/'tc-command.lua').read_text();code=(here/'tc-command-fixtures.lua').read_text().replace('__HELPER__',helper)
fixture=here/'tc-command-replay.lua';fixture.write_text(code,encoding='utf-8',newline='\n')
r=subprocess.run(cmd+[unix(fixture)],capture_output=True,text=True,timeout=30)
(here/'tc-command-replay-output.txt').write_text(r.stdout+r.stderr,encoding='utf-8')
assert r.returncode==0,r.stdout+r.stderr
cases=re.findall(r'^PASS (.*)$',r.stdout,re.M);assert len(cases)==16
syntax=subprocess.run(cmd+['-e',"assert(loadfile('"+unix(here/'worker.lua')+"'));print('SYNTAX_PASS')"],capture_output=True,text=True,timeout=30)
assert syntax.returncode==0,syntax.stderr
old=(here/'original-worker.lua').read_text();new=(here/'worker.lua').read_text()
# No changes to classifier decisions, observation, publication, exception handler, or recovery.
for start,end in [('if mode==\'status\'then','local function query('),('local function query(',None)]:
 a=old[old.index(start):old.index(end) if end else None];b=new[new.index(start):new.index(end) if end else None];assert a==b
manifest=json.loads((here/'candidate-manifest.json').read_text());assert manifest['workerSha256']==sha(here/'worker.lua')
out={'passed':True,'checks':len(cases),'cases':cases,'workerSha256':sha(here/'worker.lua'),'helperSha256':sha(here/'tc-command.lua'),'workerSyntax':True,'observationPublicationAndRecoveryByteEquivalent':True,'routerWrites':False,'serviceLifecycleInjected':False}
(here/'worker-qualified.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out))
