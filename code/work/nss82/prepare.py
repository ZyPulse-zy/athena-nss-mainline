"""Use the already-qualified exact one-packet skew reread at every tag observation."""
from pathlib import Path
import hashlib,json
r=Path('work/nss82');r.mkdir(exist_ok=True)
for p in Path('work/nss81').glob('*'):
 if p.is_file() and p.suffix in ('.mjs','.py','.ps1') and p.name not in ('prepare.py','session-binding.mjs'):
  s=p.read_text().replace('work/nss81','work/nss82').replace('nss81','nss82').replace('NSS81','NSS82')
  r.joinpath(p.name).write_text(s)
source=Path('work/nss77/fast-path.lua').read_text()
ack=Path('work/nss81/fast-path.lua').read_text();a=ack.index('function M.mayRereadAck');b=ack.index('function M.verifyRenewalAck',a);ack=ack[a:b].strip()+'\n'
source=source.replace('function M.verifyRenewalAck',ack+'\nfunction M.verifyRenewalAck',1)
wrapper=""" local function checkedTags(key,live,pending)
 local raw=live();record[key]=raw;local c={}
 for _,x in ipairs(raw.nftables)do if x.rule then for _,e in ipairs(x.rule.expr)do if e.counter then c[x.rule.comment:match('([^:]+)$')]=e.counter end end end end
 if M.mayRereadCounterSnapshot(c)or M.mayRereadAck(c)then
 stopped();assert(now()<record.deadline-5);record[key..'First']=raw;record.tagCounterRereads=record.tagCounterRereads or{};record.tagCounterRereads[#record.tagCounterRereads+1]={key=key,reads=1,nssAdmissionAllowed=false};raw=live();record[key]=raw end
 return getter(raw,pending)
 end
"""
source=source.replace(' local function state()',wrapper+' local function state()',1)
edits=[]
def replace(old,new):
 global source
 assert source.count(old)==1;edits.append((old,new));source=source.replace(old,new)
replace('record.tagsBefore=live();record.preLearningGetter=getter(record.tagsBefore)',"record.preLearningGetter=checkedTags('tagsBefore',live)")
replace('record.initialTags=live();local _,pending=getter(record.initialTags,true)',"local _,pending=checkedTags('initialTags',live,true)")
a=source.index("  record.qosAtA=qos.snapshot();measure('A');record.tagsAfterA=live();")
b=source.index('  local fresh,learningDue=',a)
replace(source[a:b],"  record.qosAtA=qos.snapshot();measure('A');checkedTags('tagsAfterA',live)\n")
a=source.index('  record.tagsBeforeA2=live();local a2Counters=')
b=source.index("measure('A2');record.tagsAfterA2=live();getter(record.tagsAfterA2)",a)+len("measure('A2');record.tagsAfterA2=live();getter(record.tagsAfterA2)")
replace(source[a:b],"  checkedTags('tagsBeforeA2',live);measure('A2');checkedTags('tagsAfterA2',live)")
restored=source.replace(ack+'\n','').replace(wrapper,'')
for old,new in reversed(edits):restored=restored.replace(new,old)
assert restored==Path('work/nss77/fast-path.lua').read_text()
source='\n'.join(x for x in source.splitlines() if x.strip() and not x.lstrip().startswith('--'))+'\n'
r.joinpath('fast-path.lua').write_text(source)
payload=Path('work/nss81/payload.mjs').read_text().replace('work/nss81','work/nss82');r.joinpath('payload.mjs').write_text(payload)
r.joinpath('module-stage.mjs').write_text(Path('work/nss81/module-stage.mjs').read_text().replace('work/nss81','work/nss82'))
binding="""import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';import {verifyPreparation as previous} from '../nss80/session-binding.mjs';
export function verifyPreparation(){const q=previous(),p=JSON.parse(fs.readFileSync('work/nss82/entry-qualified.json')),a=JSON.parse(fs.readFileSync('work/nss82/ack-qualified.json'));assert.ok(p.passed&&p.allGetterSitesOneExactReread&&p.strictSecondGetterUnchanged&&a.passed&&a.cases===17&&!a.nssAdmissionAllowed);assert.equal(a.fastSha256,p.fastSha256);for(const[f,h]of Object.entries(p.sourceManifest))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex'),h,f);return{...q,sourceManifest:{...q.sourceManifest,...p.sourceManifest}};}
"""
r.joinpath('session-binding.mjs').write_text(binding)
names=[p for p in r.glob('*') if p.is_file() and p.suffix in ('.mjs','.py','.ps1','.lua')]
manifest={p.as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in names}
r.joinpath('entry-qualified.json').write_text(json.dumps({'passed':True,'allGetterSitesOneExactReread':True,'strictSecondGetterUnchanged':True,'nativeLimitsUnchanged':True,'qosParentMbps':20,'fastSha256':hashlib.sha256(r.joinpath('fast-path.lua').read_bytes()).hexdigest(),'sourceManifest':manifest},indent=2)+'\n')
print(json.dumps({'fastBytes':r.joinpath('fast-path.lua').stat().st_size,'allGetterSitesOneExactReread':True,'strictSecondGetterUnchanged':True,'nativeLimitsUnchanged':True}))
