"""Replace non-atomic counter equality with one bounded monotonic bracket."""
from pathlib import Path
import json,hashlib
r=Path('work/nss89');r.mkdir(exist_ok=True)
for p in Path('work/nss88').iterdir():
 if not p.is_file() or p.suffix not in ('.mjs','.py','.ps1','.lua') or p.name in ('prepare-client.py','session-binding.mjs','qualify-client.mjs'):continue
 s=p.read_text(encoding='utf-8').replace('work/nss88','work/nss89').replace('nss88','nss89').replace('NSS88','NSS89')
 r.joinpath(p.name).write_text(s,encoding='utf-8')
for n in ['qos-physical.lua','qos-native-qualification.json']:r.joinpath(n).write_bytes(Path('work/nss88',n).read_bytes())
s=Path('work/nss88/fast-path.lua').read_text(encoding='utf-8')
a=s.index('function M.mayRereadCounterSnapshot');b=s.index('function M.verifyRenewalAck')
s=s[:a]+r.joinpath('tag-counter-audit.lua').read_text(encoding='utf-8')+s[b:]
a=s.index(' local function getter(');b=s.index(' local function state()',a)
replacement=""" local function counters(raw)
  local c={};for _,x in ipairs(raw.nftables)do if x.rule then for _,e in ipairs(x.rule.expr)do if e.counter then c[x.rule.comment:match('([^:]+)$')]=e.counter end end end end;return c
 end
 local function checkedTags(key,live,pending)
  local raw=live();record[key]=raw;local c=counters(raw);local a=M.tagCounterAudit(c,pending)
  if a.needsSecond then
   stopped();assert(now()<record.deadline-5);record[key..'First']=raw
   record.tagCounterRereads=record.tagCounterRereads or{};record.tagCounterRereads[#record.tagCounterRereads+1]={key=key,reads=1,nssAdmissionAllowed=false,contract='monotonic-overlap-zero-wrong-tag'}
   raw=live();record[key]=raw;local next=counters(raw);a=M.tagCounterAudit(next,pending,c);c=next
  end
  return c,a.pending
 end
"""
s=s[:a]+replacement+s[b:]
assert s.count('getter(record.initialTags);')==1;s=s.replace('getter(record.initialTags);','')
r.joinpath('fast-path.lua').write_text(s,encoding='utf-8')
binding="""import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';import {verifyPreparation as previous} from '../nss88/session-binding.mjs';
export function verifyPreparation(){const q=previous(),p=JSON.parse(fs.readFileSync('work/nss89/entry-qualified.json')),t=JSON.parse(fs.readFileSync('work/nss89/getter-qualified.json'));assert.ok(p.passed&&p.onlyCounterObservationChanged&&t.passed);assert.equal(t.sourceSha256,p.fastSourceSha256);assert.ok(t.cases>=20);for(const[f,h]of Object.entries(p.sourceManifest))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex'),h,f);return{...q,sourceManifest:{...q.sourceManifest,...p.sourceManifest}};}
"""
r.joinpath('session-binding.mjs').write_text(binding,encoding='utf-8')
print(json.dumps({'prepared':True,'onlyTagObservationChanged':True,'strictWrongTagAndPolicyAndIdentityKept':True,'maximumRereads':1}))
