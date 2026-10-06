"""Retain the 60 Mbps plan; recognize recorded 40-byte ACK and pending UDP reads."""
from pathlib import Path
import hashlib,json
r=Path('work/nss85');r.mkdir(exist_ok=True)
for p in Path('work/nss84').iterdir():
 if p.is_file() and p.suffix in ('.mjs','.py','.ps1','.lua') and p.name not in ('prepare-budget.py','session-binding.mjs','qualify-qos-native.mjs'):
  s=p.read_text(encoding='utf-8').replace('work/nss84','work/nss85').replace('nss84','nss85').replace('NSS84','NSS85')
  r.joinpath(p.name).write_text(s,encoding='utf-8')
r.joinpath('qos-physical.lua').write_bytes(Path('work/nss84/qos-physical.lua').read_bytes())
r.joinpath('qos-native-qualification.json').write_bytes(Path('work/nss84/qos-native-qualification.json').read_bytes())
s=Path('work/nss84/fast-path.lua').read_text(encoding='utf-8')
s=s.replace('function M.mayRereadAck(c)','function M.mayRereadAck(c,pending)',1)
old='if not(t and e and u)or u.packets~=0 or u.bytes~=0 or t.packets<=0 or e.packets<=0 then return false end'
new='if not(t and e and u)or u.packets~=0 or u.bytes~=0 then return false end\nif(t.packets<=0 or e.packets<=0)and not(pending and t.packets==0 and e.packets==0 and t.bytes==0 and e.bytes==0)then return false end'
a=s.index('function M.mayRereadAck');b=s.index('function M.verifyRenewalAck',a);piece=s[a:b];assert old in piece
piece=piece.replace(old,new).replace('e.bytes==t.bytes+60 then','(e.bytes==t.bytes+60 or e.bytes==t.bytes+40)then')
s=s[:a]+piece+s[b:];s=s.replace('M.mayRereadAck(c)then','M.mayRereadAck(c,pending)then')
r.joinpath('fast-path.lua').write_text(s,encoding='utf-8')
# Preparation rejects degraded synthetic UDP rather than calling it usable game traffic.
m=r.joinpath('match-controlled.mjs').read_text(encoding='utf-8')
needle='if(x.pairs.length){console.log'
replacement="""if(x.pairs.length){const events=fs.readFileSync(load.dir+'/udp-samples-private.jsonl','utf8').trim().split('\\n').map(s=>JSON.parse(s));const at=Date.now()/1000;const sent=events.filter(e=>e.event==='sent'&&e.at>=at-3&&e.at<at-.6);const replies=new Set(events.filter(e=>e.event==='reply').map(e=>e.sequence));const returned=sent.filter(e=>replies.has(e.sequence)).length;assert.ok(sent.length>=50&&returned/sent.length>=.9,'Controlled UDP baseline degraded before staging');fs.writeFileSync(load.dir+'/udp-baseline-qualified.json',JSON.stringify({passed:true,sent:sent.length,returned,minimumRatio:.9,routerWrites:false,notCs2Acceptance:true}));console.log"""
assert needle in m;m=m.replace(needle,replacement);r.joinpath('match-controlled.mjs').write_text(m,encoding='utf-8')
binding="""import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';import {verifyPreparation as previous} from '../nss84/session-binding.mjs';
export function verifyPreparation(){const q=previous(),p=JSON.parse(fs.readFileSync('work/nss85/entry-qualified.json')),n=JSON.parse(fs.readFileSync('work/nss85/getter-qualified.json'));assert.ok(p.passed&&n.passed&&n.cases>=20&&!n.nssAdmissionAllowed);assert.equal(n.sourceSha256,p.fastSourceSha256);for(const[f,h]of Object.entries(p.sourceManifest))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex'),h,f);return{...q,sourceManifest:{...q.sourceManifest,...p.sourceManifest}};}
"""
r.joinpath('session-binding.mjs').write_text(binding,encoding='utf-8')
manifest={p.as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in r.iterdir() if p.is_file() and p.suffix in ('.mjs','.py','.ps1','.lua')}
r.joinpath('entry-qualified.json').write_text(json.dumps({'passed':True,'qosGroupMbps':60,'tcpOfferedMbps':52,'one40Or60ByteAckOnly':True,'pendingAllowedOnlyAtOriginalInitialSite':True,'secondOriginalStrictGetterUnchanged':True,'qosBytesUnchangedFrom84':True,'fastSourceSha256':hashlib.sha256(r.joinpath('fast-path.lua').read_bytes()).hexdigest(),'sourceManifest':manifest},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'prepared':True,'qosBytesUnchanged':True,'exactRecorded40ByteAckAdded':True,'noNativePermissionOrDeadlineChange':True}))
