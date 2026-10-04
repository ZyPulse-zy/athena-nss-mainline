"""Offline candidate checks, without router access or production entry qualification."""
from pathlib import Path
import subprocess,json,re,hashlib
r=Path('work/nss44');root=Path.cwd();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=(r/'wait-ready-candidate.mjs').read_text()
start=source.index("assert(s.publication=='before-software-baseline')");end=source.index('assert(s.configSha256==',start)
guard=source[start:end]
assert "ram..'/snapshot.json'" not in source and source.count("ram..'/classification.json'")==2
assert "start+5" in source and "group-runner 6" in source and '100000000' in source
assert "work/nss42/publication-wait.lua" in source
audit=(r/'candidate-audit-readonly.mjs').read_text();original=Path('work/nss42/current-audit-diagnostic.mjs').read_text()
assert audit[audit.index(' const code=render('):].replace('work/nss44','work/nss42')==original[original.index(' const code=render('):]
worker=(r/'candidate-worker.lua').read_text();old=Path('work/nss39/worker.lua').read_text()
assert worker[worker.index('local own=assert(dofile'):]==old[old.index('local own=assert(dofile'):]
assert "direct('/usr/bin/sha256sum '..base..'/config.json'" in worker
helper=(r/'hash-batch.lua').read_text()
fixture="""local M=(function()\n"""+helper+"""\nend)()
local passed={};local function check(label,good,fn)local ok=pcall(fn);assert(ok==good,label);passed[#passed+1]=label end
local base='/root/router-project/classifier/nss44-fixture';local a=string.rep('a',64);local b=string.rep('b',64);local files={['a.lua']=a,['b.lua']=b}
local lineA=a..'  '..base..'/a.lua\\n';local lineB=b..'  '..base..'/b.lua\\n'
check('batch command has all paths',true,function()local c,cap=M.command(base,files);assert(c=='/usr/bin/sha256sum '..base..'/a.lua '..base..'/b.lua'and cap==16384)end)
check('expected hashes accepted',true,function()assert(M.verify(base,files,lineA..lineB)==2)end)
check('unordered hashes accepted',true,function()assert(M.verify(base,files,lineB..lineA)==2)end)
check('missing digest rejected',false,function()M.verify(base,files,lineA)end)
check('duplicate digest rejected',false,function()M.verify(base,files,lineA..lineA..lineB)end)
check('foreign base rejected',false,function()M.verify(base,files,a..'  /another/a.lua\\n'..lineB)end)
check('unknown path rejected',false,function()M.verify(base,files,lineA..lineB..a..'  '..base..'/unknown.lua\\n')end)
check('changed payload rejected',false,function()M.verify(base,files,b..'  '..base..'/a.lua\\n'..lineB)end)
check('malformed output rejected',false,function()M.verify(base,files,'not-a-checksum\\n')end)
check('empty output rejected',false,function()M.verify(base,files,'')end)
for _,name in ipairs({'../a.lua','/a.lua','a;echo','a$(echo)','a file.lua'})do check('unsafe filename '..name,false,function()M.command(base,{[name]=a})end)end
check('short digest rejected',false,function()M.command(base,{['a.lua']=a:sub(2)})end)
check('nonhex digest rejected',false,function()M.command(base,{['a.lua']=string.rep('g',64)})end)
check('empty payload list rejected',false,function()M.command(base,{})end)
check('oversized payload list rejected',false,function()local f={};for i=1,65 do f['file'..i..'.lua']=a end;M.command(base,f)end)
check('unknown base rejected',false,function()M.command('/root/other',files)end)
check('malformed files rejected',false,function()M.command(base,'files')end)
local function project(s)\n"""+guard+"""\nreturn true end
local function valid()return{publication='before-software-baseline',snapshot={flows={{},{}},provenance={sequence=10},admissionProjection={version=1,scope='bulk-and-admitted-rt',sourceSequence=10,candidateFlowCount=2,completeInputFlowCount=10}}}end
check('classification projection accepted',true,function()assert(project(valid()))end)
check('postbaseline publication rejected',false,function()local s=valid();s.publication='after-software-baseline';project(s)end)
check('wrong projection version rejected',false,function()local s=valid();s.snapshot.admissionProjection.version=2;project(s)end)
check('wrong projection scope rejected',false,function()local s=valid();s.snapshot.admissionProjection.scope='all';project(s)end)
check('wrong projection sequence rejected',false,function()local s=valid();s.snapshot.admissionProjection.sourceSequence=11;project(s)end)
check('wrong candidate count rejected',false,function()local s=valid();s.snapshot.admissionProjection.candidateFlowCount=3;project(s)end)
check('invalid complete count rejected',false,function()local s=valid();s.snapshot.admissionProjection.completeInputFlowCount=1;project(s)end)
check('missing projection rejected',false,function()local s=valid();s.snapshot.admissionProjection=nil;project(s)end)
check('missing provenance rejected',false,function()local s=valid();s.snapshot.provenance=nil;project(s)end)
for _,name in ipairs(passed)do io.write('PASS '..name..'\\n')end
"""
p=r/'candidate-fixtures.lua';p.write_text(fixture,encoding='utf-8')
def unix(p):s=p.resolve().as_posix();return '/mnt/'+s[0].lower()+s[2:]
rt=root/'work/nss9/lua-runtime/extracted/usr'
cmd=['wsl.exe','-d','Athena-Cake-Build','--exec','/usr/bin/env','LD_LIBRARY_PATH='+unix(rt/'lib/x86_64-linux-gnu'),unix(rt/'bin/lua5.1')]
run=subprocess.run(cmd+[unix(p)],capture_output=True,text=True,timeout=30);assert run.returncode==0,run.stdout+run.stderr
cases=re.findall(r'^PASS (.+)$',run.stdout,re.M);assert len(cases)==30,len(cases)
syntax=subprocess.run(cmd+['-e',"assert(loadfile('"+unix(r/'candidate-worker.lua')+"'))"],capture_output=True,text=True,timeout=30);assert syntax.returncode==0,syntax.stderr
out={'passed':True,'checks':30,'cases':cases,'routerAccess':False,'candidateInstalled':False,'productionEntryQualified':False,
 'schedulingLibraryUnchanged':True,'originalCompleteLockedAuditUnchanged':True,'publicationLifecycleRuleAndDeadlineByteEquivalent':True,
 'scope':'Checksum and projection guards plus static source equivalence; not full lifecycle or native high-load proof',
 'sourceHashes':{str(p).replace('\\','/'):sha(p) for p in (r/'hash-batch.lua',r/'candidate-worker.lua',r/'wait-ready-candidate.mjs',r/'candidate-audit-readonly.mjs',r/'test_candidates.py',Path('work/nss42/publication-wait.lua'))}}
(r/'candidate-local-qualified.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps({'passed':True,'checks':30,'routerAccess':False,'candidateInstalled':False,'productionEntryQualified':False}))
