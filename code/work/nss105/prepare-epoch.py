"""Split startup observation from the validated pre-learning measurement epoch."""
from pathlib import Path
import json,hashlib
r=Path('work/nss105');old=Path('work/nss100');checks=[]
proof=json.loads((old/'entry-qualified.json').read_text())
for f in [Path(k).name for k in proof['sourceManifest']]:
 if f in ('prepare-rate.py','session-binding.mjs','run.mjs','qualify-qos-native.mjs'):continue
 dst=r/f;assert not dst.exists(),str(dst)
 if f in ('qos-physical.lua','module-stage-guardian.lua','tag-counter-audit.lua'):
  dst.write_bytes((old/f).read_bytes());checks.append({'file':f,'byteIdentical':True});continue
 s=(old/f).read_text(encoding='utf-8');v=s.replace('nss100','nss105').replace('NSS100','NSS105')
 assert v.replace('nss105','nss100').replace('NSS105','NSS100')==s
 dst.write_text(v,encoding='utf-8');checks.append({'file':f,'onlyNamespaceChanged':True})
f=r/'fast-path.lua';s=f.read_text(encoding='utf-8')
prefix="""function M.tagEpoch(b,c)
 local d={}
 for k,v in pairs(b)do
  local w=assert(c[k],'Epoch counter missing');d[k]={}
  for _,u in ipairs({'packets','bytes'})do local a,z=v[u],w[u];assert(type(a)=='number'and type(z)=='number'and a>=0 and z>=a and a%1==0 and z%1==0 and z<=9007199254740991,'Epoch counter regressed');d[k][u]=z-a end
  if k:match('_unexpected$')or k:match('_neighbor_nonzero$')then assert(v.packets==0 and v.bytes==0 or k=='tcp_post_down_unexpected'and v.packets==1 and v.bytes==1500,'Startup tag mismatch exceeds observed boundary')end
 end
 for k in pairs(c)do assert(b[k],'Epoch counter added')end
 return d
end
"""
assert s.count('function M.verifyRenewalAck')==1;s=s.replace('function M.verifyRenewalAck',prefix+'function M.verifyRenewalAck')
s=s.replace('local session;local loaded=false','local session;local loaded=false;local tagBase')
a='local c=counters(raw);local a=M.tagCounterAudit(c,pending)';b='local c=M.tagEpoch(tagBase,counters(raw));local a=M.tagCounterAudit(c,pending)'
assert s.count(a)==1;s=s.replace(a,b)
a='local next=counters(raw);a=M.tagCounterAudit(next,pending,c)';b='local next=M.tagEpoch(tagBase,counters(raw));a=M.tagCounterAudit(next,pending,c)'
assert s.count(a)==1;s=s.replace(a,b)
a='  repeat\n   stopped();local _,pending=checkedTags(\'initialTags\',live,true)'
b="""  record.startupTags=live();tagBase=counters(record.startupTags);M.tagEpoch(tagBase,tagBase)
  record.tagMeasurementEpoch={baselineAt=now(),warmupSeconds=0.1,contract='absolute-raw-retained-zero-new-wrong-tag',baselineCounters=tagBase,nssAdmissionAllowed=false}
  pause(0.1);stopped();assert(now()<getterUntil,'Startup epoch exceeded getter deadline')
  repeat
   stopped();local _,pending=checkedTags('initialTags',live,true)"""
assert s.count(a)==1;s=s.replace(a,b)
# Remove two explanatory comments to remain inside the existing staged payload cap.
s=s.replace('    stopped() -- ECM remains closed; fresh admission is checked after the core phase.','    stopped()').replace('   record.lastAdmissionProbe=nil -- avoid repeated table references in native jsonc','   record.lastAdmissionProbe=nil')
f.write_text(s,encoding='utf-8')
for name in ('long-window-qualification.json','qos-native-qualification.json'):(r/name).write_bytes((old/name).read_bytes())
(r/'run.mjs').write_text((old/'run.mjs').read_text(encoding='utf-8').replace('nss100','nss105').replace('NSS100 20 second phases / QoS30 / offered48','NSS105 startup measurement epoch / 20 second phases / QoS30 / offered48'),encoding='utf-8')
binding="""import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';import {verifyPreparation as previous} from '../nss100/session-binding.mjs';
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
export function verifyPreparation(){const q=previous(),p=JSON.parse(fs.readFileSync('work/nss105/entry-qualified.json')),t=JSON.parse(fs.readFileSync('work/nss105/startup-epoch-qualification.json'));assert.ok(p.passed&&p.onlyStartupMeasurementChanged&&t.passed&&t.checks.length>=16);assert.equal(t.sourceSha256,hash(fs.readFileSync('work/nss105/fast-path.lua')));for(const name of ['qos-physical.lua','module-stage-guardian.lua','tag-counter-audit.lua'])assert.equal(hash(fs.readFileSync('work/nss105/'+name)),hash(fs.readFileSync('work/nss100/'+name)));for(const[f,h]of Object.entries(p.sourceManifest))assert.equal(hash(fs.readFileSync(f)),h,f);return{...q,sourceManifest:{...q.sourceManifest,...p.sourceManifest}};}
"""
(r/'session-binding.mjs').write_text(binding,encoding='utf-8')
(r/'prepare-receipt.json').write_text(json.dumps({'checks':checks,'onlyStartupMeasurementChanged':True,'rawStartupRetained':True,'zeroNewUnexpectedRequired':True,'nativeSourceUnchanged':True,'phaseSeconds':20,'nativeSessionSeconds':27,'ownerSeconds':100,'classifierSeconds':6,'qosMbps':30,'offeredMbps':48},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'prepared':True,'additionalFastBytes':len(f.read_bytes())-len((old/'fast-path.lua').read_bytes()),'routerWrites':False}))
