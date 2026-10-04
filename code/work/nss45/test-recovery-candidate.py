"""Synthetic adoption/restart/interruption/foreign-writer replay and read counts."""
import hashlib,json,re,subprocess,shutil
from pathlib import Path
here=Path(__file__).resolve().parent;root=here.parents[1]
own=(root/'athena-nss-mainline/code/deployed-classifier/owned.lua').read_bytes()
seed=r'''
local input={boot='11111111-1111-1111-1111-111111111111',queues={},native={}}
for w=1,5 do for i,prefix in ipairs({'rpwan','rpifb'})do
 local dev=prefix..w;local h=string.format('%x:',0x8000+w*2+i)
 input.queues[dev]={handle=h,options={bandwidth=100000000,diffserv='diffserv4',nat=true}}
 local baseHead='filter protocol ip pref 40900 u32 chain 0'
 local fallback='filter protocol all pref 41900 matchall chain 0'
 input.native[dev]=baseHead..'\n'..baseHead..' fh 800: ht divisor 1\n'..baseHead..' fh 800::800 order 2048 key ht 800 bkt 0 terminal flowid not_in_hw\n  match 45000400/ff00fc00 at 0\n  match 00060000/00ff0000 at 8\n\taction order 1: skbedit priority '..h..'2 pass\n\t index '..(w*10+i*2)..' ref 1 bind 1\n\n'..fallback..'\n'..fallback..' handle 0x1\n  not_in_hw\n\taction order 1: skbedit priority '..h..'2 pass\n\t index '..(w*10+i*2+1)..' ref 1 bind 1\n\n'
 if w==5 then for slot=1,2 do
  local sport=50000+slot;local proto=17;local tuple={src='192.0.2.1',dst='198.51.100.5',sport=45818,dport=sport}
  if i==1 then tuple={src='198.51.100.5',dst='192.0.2.1',sport=sport,dport=45818}end
  local semantic=B.semantic(tuple,proto,h);local head='filter protocol ip pref '..(41000+slot)..' u32 chain 0';local fh=string.format('%x',2304+slot)
  local text=head..'\n'..head..' fh '..fh..': ht divisor 1\n'..head..' fh '..fh..'::800 order 2048 key ht '..fh..' bkt 0 terminal flowid not_in_hw\n'
  for _,k in ipairs(semantic.matches)do text=text..'  match '..k.value..'/'..k.mask..' at '..k.off..'\n'end
  text=text..'\taction order 1: skbedit priority '..semantic.priority..' pass\n\t index '..(100+slot)..' ref 1 bind 1\n\n'
  input.native[dev]=input.native[dev]..text
 end end
end end
'''
# New fixture data is synthetic; historical private rule inputs are not used.
base=(root/'work/nss23/backend-fixtures.lua').read_text()
first="local here=assert(arg[1]);local own=assert(dofile(here..'/owned.lua'));local B=assert(dofile(here..'/backend.lua'));local input=assert(dofile(here..'/backend-input-private.lua'))"
assert base.count(first)==1
body=base.replace(first,"local here=assert(arg[1]);local own=assert(dofile(here..'/owned.lua'));local B=assert(dofile(here..'/backend.lua'));\n"+seed)
body=body.replace('local stored,inject,operations,seq=nil,nil,0,1000;','local reads=0;local stored,inject,operations,seq=nil,nil,0,1000;')
body=body.replace('local function native(dev,h)','local function native(dev,h)\n reads=reads+1')
body=body.replace("queue=function(dev)local q=clone(cfg.queues[dev]);","queue=function(dev)reads=reads+1;local q=clone(cfg.queues[dev]);")
marker="io.write('BACKEND_FIXTURES_PASS '..#passed..'\\n');"
assert body.count(marker)==1
extra=r'''
-- All rules are empty after the original adoption/crash/unknown-writer cases.
worker=B.new(cfg,R,own);reads=0;local opsBefore=operations;worker.recover();local emptyReads=reads
yes(operations==opsBefore,'empty recovery never writes a native selector')
yes(emptyReads==EXPECTED_EMPTY_READS,'exact empty recovery read count')
-- Change a known object after the preinspection, before the first possible write.
worker.reconcile(snap(flow(70,56000,'RT',5)));local savedNative=R.native;local altered=false
R.native=function(dev,h)
 if dev=='rpwan5'and not altered then
  local out=savedNative(dev,h);dyn[dev][1].matches[4].value='cb007109';altered=true;return out
 end
 return savedNative(dev,h)
end
local beforeWrites=#writes;local recovered=pcall(worker.recover)
yes(not recovered and altered,'unknown writer appearing after initial inspection rejects completion')
yes(dyn.rpwan5[1]and dyn.rpwan5[1].matches[4].value=='cb007109','changed selector survives initial enumeration reuse')
for i=beforeWrites+1,#writes do yes(not writes[i]:find('dev rpwan5 ',1,true),'unknown upload selector never deleted')end
R.native=savedNative
io.write('RECOVERY_READS '..emptyReads..'\n')
'''
body=body.replace(marker,extra+'\n'+marker)
fixture=here/'recovery-fixtures.lua';fixture.write_text(body,encoding='utf-8',newline='\n')
def unix(p):
    s=p.resolve().as_posix();return '/mnt/'+s[0].lower()+s[2:]
rt=root/'work/nss9/lua-runtime/extracted/usr'
cmd=['wsl.exe','-d','Athena-Cake-Build','--exec','/usr/bin/env','LD_LIBRARY_PATH='+unix(rt/'lib/x86_64-linux-gnu'),unix(rt/'bin/lua5.1')]
results=[]
for method,name,expected in [('original','original-backend.lua',60),('candidate','candidate-backend.lua',40)]:
    stage=here/('recovery-'+method+'-replay');stage.mkdir(exist_ok=True)
    (stage/'owned.lua').write_bytes(own);shutil.copyfile(here/name,stage/'backend.lua')
    (stage/'fixture.lua').write_text(body.replace('EXPECTED_EMPTY_READS',str(expected)),encoding='utf-8',newline='\n')
    r=subprocess.run(cmd+[unix(stage/'fixture.lua'),unix(stage)],capture_output=True,text=True,timeout=30)
    (here/('recovery-'+method+'-output.txt')).write_text(r.stdout+r.stderr,encoding='utf-8')
    checks=re.findall(r'^PASS (.*)$',r.stdout,re.M)
    results.append({'method':method,'passed':r.returncode==0,'checks':len(checks),'cases':checks,'emptyReadonlyCalls':expected,'sourceSha256':hashlib.sha256((here/name).read_bytes()).hexdigest(),'error':r.stderr})
out={'passed':all(r['passed']for r in results),'results':results,'syntheticInput':True,'routerWrites':False,'installed':False,'ownUndoSha256':hashlib.sha256(own).hexdigest(),'recoveryReadCount':{'original':60,'candidate':40},'actualNativeTcOrServiceFaultsInjected':False,'scope':'Actual old/new backends and unchanged undo with synthetic tc/journal; including interruption and a writer appearing after initial inspection.'}
(here/'recovery-qualified.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps({**out,'results':[{k:v for k,v in r.items()if k!='cases'}for r in results]}));raise SystemExit(0 if out['passed']else 1)
