"""Extend the observation, not classification freshness or flow scope."""
from pathlib import Path
import hashlib,json
r=Path('work/nss99');prior=Path('work/nss97')
p=json.loads((prior/'entry-qualified.json').read_text());checks=[]
def once(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
for f in [Path(x).name for x in p['sourceManifest']]:
 if f in ('prepare-saturation.py','qualify-qos-native.mjs','session-binding.mjs','run.mjs'):continue
 src=prior/f;dst=r/f;assert not dst.exists(),str(dst)
 if f in ('qos-physical.lua','tag-counter-audit.lua'):
  dst.write_bytes(src.read_bytes());checks.append({'file':f,'byteIdentical':True});continue
 s=src.read_text(encoding='utf-8');v=s.replace('nss97','nss99').replace('NSS97','NSS99')
 changes=[]
 if f=='fast-path.lua':
  for a,b in [("name=='A'and 26 or name=='B'and 13 or 8","name=='A'and 78 or name=='B'and 55 or 28"),('requestedSeconds=5','requestedSeconds=20'),('s.uptime-start>=5','s.uptime-start>=20'),('p.seconds>=5 and p.seconds<=6.5','p.seconds>=20 and p.seconds<=21.5'),('deadline-32','deadline-84'),('record.deadline-32','record.deadline-84'),('record.deadline-15','record.deadline-56'),('now()+12,record.deadline-8','now()+27,record.deadline-28'),('session/1000-now()>=9','session/1000-now()>=26'),('minimumStableSeconds=5','minimumStableSeconds=20')]:
   # deadline-32 also occurs as a record field; replace the two sites together.
   if a=='deadline-32':assert v.count(a)==2;v=v.replace(a,b);changes.append([a,b]);continue
   if a=='record.deadline-32':continue
   v=once(v,a,b);changes.append([a,b])
 if f=='module-stage.mjs':
  v=once(v,"fs.readFileSync('work/nss49/module-stage-guardian.lua'","fs.readFileSync('work/nss99/module-stage-guardian.lua'")
 if f=='controlled-session.mjs':
  v=once(v,'i<26','i<60');v=once(v,'p.seconds>=5&&p.seconds<=6.5&&p.sampleCount>=8','p.seconds>=20&&p.seconds<=21.5&&p.sampleCount>=38')
 dst.write_text(v,encoding='utf-8');checks.append({'file':f,'changes':changes,'namespaceUpdated':f not in ('fast-path.lua',)})
g=(Path('work/nss49/module-stage-guardian.lua')).read_text(encoding='utf-8')
(r/'module-stage-guardian.lua').write_text(once(g,'deadline=now()+45','deadline=now()+100'),encoding='utf-8')
# Previous exact native-option qualification is consumed, not replayed.
(r/'qos-native-qualification.json').write_bytes((prior/'qos-native-qualification.json').read_bytes())
binding="""import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';import {verifyPreparation as previous} from '../nss97/session-binding.mjs';
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
export function verifyPreparation(){const q=previous(),p=JSON.parse(fs.readFileSync('work/nss99/entry-qualified.json')),t=JSON.parse(fs.readFileSync('work/nss99/long-window-qualification.json'));assert.ok(p.passed&&p.onlyObservationTimingChanged&&p.tcpOfferedMbps===48&&p.qosGroupMbps===40&&t.passed&&t.checks.length>=8);assert.equal(t.sourceSha256,hash(fs.readFileSync('work/nss99/fast-path.lua')));assert.equal(t.guardianSha256,hash(fs.readFileSync('work/nss99/module-stage-guardian.lua')));assert.equal(t.nativeSourceSha256,hash(fs.readFileSync('work/nss27/endpoint-gate/rp_ecm_gate_lab_ct.c')));for(const[f,h]of Object.entries(p.sourceManifest))assert.equal(hash(fs.readFileSync(f)),h,f);return{...q,sourceManifest:{...q.sourceManifest,...p.sourceManifest}};}
"""
(r/'session-binding.mjs').write_text(binding,encoding='utf-8')
driver=(prior/'run.mjs').read_text(encoding='utf-8').replace('nss97','nss99').replace('NSS97 selected QoS40 / offered48','NSS99 20 second phases / QoS40 / offered48').replace("['aba'],110","['aba'],145")
(r/'run.mjs').write_text(driver,encoding='utf-8')
m={f.as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in r.iterdir() if f.is_file() and f.suffix in ('.mjs','.py','.ps1','.lua')}
(r/'entry-qualified.json').write_text(json.dumps({'passed':True,'onlyObservationTimingChanged':True,'tcpOfferedMbps':48,'qosGroupMbps':40,'phaseSeconds':20,'fixedNativeSessionSeconds':27,'detachedOwnerSeconds':100,'classifierFreshnessSeconds':6,'checks':checks,'sourceManifest':m},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'prepared':True,'files':len(m),'phaseSeconds':20,'fixedNativeSessionSeconds':27,'detachedOwnerSeconds':100,'classifierFreshnessSeconds':6,'qosBytesUnchanged':True,'routerWrites':False}))
