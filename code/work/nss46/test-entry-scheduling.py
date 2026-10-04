"""Actual scheduling guard and unchanged planner; native audit stays mandatory."""
from pathlib import Path
import hashlib,json,re,subprocess
root=Path.cwd();here=root/'work/nss46';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=(here/'wait-ready-candidate.mjs').read_text();a=s.index("assert(s.publication=='before-software-baseline')");b=s.index('assert(s.configSha256==',a);guard=s[a:b]
assert "ram..'/snapshot.json'"not in s and 'start+5'in s and 'group-runner 6'in s and 'nssAdmissionAllowed=false'in s
assert (here/'publication-wait.lua').read_bytes()==(root/'work/nss42/publication-wait.lua').read_bytes()
audit=(here/'current-audit-diagnostic.mjs').read_text();old=(root/'work/nss44/candidate-audit-readonly.mjs').read_text()
assert audit[audit.index(' const code=render('):].replace('work/nss46','work/nss44')==old[old.index(' const code=render('):]
assert (here/'audit-renderer.mjs').read_bytes()==(root/'work/nss45/audit-renderer.mjs').read_bytes()
fixture=r'''local cases={};local function check(name,expected,fn)local ok=pcall(fn);assert(ok==expected,name);cases[#cases+1]=name end
local function project(s)
'''+guard+r'''
return true end
local function valid()return{publication='before-software-baseline',snapshot={flows={{},{}},provenance={sequence=10},admissionProjection={version=1,scope='bulk-and-admitted-rt',sourceSequence=10,candidateFlowCount=2,completeInputFlowCount=10}}}end
check('correct projection',true,function()project(valid())end)
check('postbaseline refused',false,function()local s=valid();s.publication='after-software-baseline';project(s)end)
for _,change in ipairs({{version=2},{scope='all'},{sourceSequence=11},{candidateFlowCount=3},{completeInputFlowCount=1}})do check('changed projection '..#cases,false,function()local s=valid();for k,v in pairs(change)do s.snapshot.admissionProjection[k]=v end;project(s)end)end
check('missing projection',false,function()local s=valid();s.snapshot.admissionProjection=nil;project(s)end)
check('missing provenance',false,function()local s=valid();s.snapshot.provenance=nil;project(s)end)
for _,name in ipairs(cases)do print('PASS '..name)end;print('COMPLETE '..#cases)
'''
(here/'entry-scheduling-fixtures.lua').write_text(fixture,encoding='utf-8',newline='\n')
unix=lambda p:'/mnt/'+p.resolve().as_posix()[0].lower()+p.resolve().as_posix()[2:]
rt=root/'work/nss9/lua-runtime/extracted/usr'
r=subprocess.run(['wsl.exe','-d','Athena-Cake-Build','--exec','/usr/bin/env','LD_LIBRARY_PATH='+unix(rt/'lib/x86_64-linux-gnu'),unix(rt/'bin/lua5.1'),unix(here/'entry-scheduling-fixtures.lua')],capture_output=True,text=True);assert r.returncode==0,r.stderr
cases=re.findall(r'^PASS (.*)$',r.stdout,re.M);assert len(cases)==9
p=(root/'work/nss42/test-publication-wait.py').read_text().replace('work/nss42','work/nss46');(here/'test-publication-wait.py').write_text(p,encoding='utf-8',newline='\n')
r=subprocess.run(['C:/Users/lishu/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe','-B','-X','utf8',str(here/'test-publication-wait.py')],capture_output=True,text=True);assert r.returncode==0,r.stderr
planner=json.loads((here/'publication-wait-qualified.json').read_text());assert planner['passed']and planner['checks']==23
out={'passed':True,'checks':32,'projectionCases':9,'plannerCases':23,'originalCompleteLockedAuditUnchanged':True,'schedulingDoesNotGrantNss':True,'sourceAndOwnerDeadlinesUnchanged':True,'routerWrites':False,'testedSourceManifest':{'work/nss46/'+n:sha(here/n)for n in ['wait-ready-candidate.mjs','current-audit-diagnostic.mjs','publication-wait.lua','audit-renderer.mjs','test-entry-scheduling.py','test-publication-wait.py']}}
(here/'entry-scheduling-qualified.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in out.items()if k!='testedSourceManifest'}))
