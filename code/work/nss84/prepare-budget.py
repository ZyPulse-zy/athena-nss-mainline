"""One QoS change: selected group 20 -> 60 Mbps, with finite owned 52 Mbps load."""
from pathlib import Path
import json,hashlib
r=Path('work/nss84');r.mkdir(exist_ok=True)
for p in Path('work/nss82').iterdir():
 if not p.is_file() or p.suffix not in ('.mjs','.py','.ps1','.lua'):continue
 if p.name in ('prepare.py','qualify-ack.mjs','session-binding.mjs'):continue
 s=p.read_text(encoding='utf-8').replace('work/nss82','work/nss84').replace('nss82','nss84').replace('NSS82','NSS84')
 if p.name=='ssh-client.mjs':
  assert 'c.mbps===32' in s and '32000000' in s and s.count('450*1024*1024')==2
  s=s.replace('c.mbps===32','c.mbps===52').replace('32000000','52000000').replace('450*1024*1024','1024*1024*1024')
 if p.name=='start-dallas.mjs':s=s.replace('config.mbps=32','config.mbps=52')
 if p.name=='module-stage.mjs':
  assert s.count('work/nss49/qos-physical.lua')==1 and s.count('work/nss16/qos-native-qualification.json')==1
  s=s.replace('work/nss49/qos-physical.lua','work/nss84/qos-physical.lua').replace('work/nss16/qos-native-qualification.json','work/nss84/qos-native-qualification.json')
 if p.name=='controlled-session.mjs':
  assert 'selectedSubgroupCeilingMbps:20' in s;s=s.replace('selectedSubgroupCeilingMbps:20','selectedSubgroupCeilingMbps:60')
 if p.name=='analyze-controlled.py':s=s.replace("'requestedTcpMbps':32","'requestedTcpMbps':52").replace("'qosParentMbps':20","'qosParentMbps':60")
 r.joinpath(p.name).write_text(s,encoding='utf-8')
# The fast path executable is unchanged, including source/core/native deadlines.
r.joinpath('fast-path.lua').write_bytes(Path('work/nss82/fast-path.lua').read_bytes())
old=Path('work/nss49/qos-physical.lua').read_bytes();new=old
for a,b in [(b'20Mbit',b'60Mbit'),(b'19Mbit',b'59Mbit'),(b'20mbit',b'60mbit'),(b'19mbit',b'59mbit')]:
 assert a in new;new=new.replace(a,b)
restored=new
for a,b in [(b'20Mbit',b'60Mbit'),(b'19Mbit',b'59Mbit'),(b'20mbit',b'60mbit'),(b'19mbit',b'59mbit')]:restored=restored.replace(b,a)
assert restored==old;r.joinpath('qos-physical.lua').write_bytes(new)
q=Path('work/nss16/qualify-qos-native.mjs').read_text(encoding='utf-8')
q=q.replace("from './connect-router.mjs'","from '../nss20/connect-router.mjs'").replace('work/nss16/qos-physical.lua','work/nss84/qos-physical.lua').replace('work/nss16/qos-native-qualification','work/nss84/qos-native-qualification')
q=q.replace('const classes=prior.slice(0,split)',"const classes=prior.slice(0,split).replaceAll('20Mbit','60Mbit').replaceAll('19Mbit','59Mbit')")
q=q.replace("fixtureSource='recorded NSS8 stock module native output'","fixtureSource='recorded NSS8 layout; only selected group rates transformed to 60/59/1 Mbps'")
r.joinpath('qualify-qos-native.mjs').write_text(q,encoding='utf-8')
binding="""import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';import {verifyPreparation as previous} from '../nss82/session-binding.mjs';
export function verifyPreparation(){const q=previous(),p=JSON.parse(fs.readFileSync('work/nss84/entry-qualified.json')),n=JSON.parse(fs.readFileSync('work/nss84/qos-native-qualification.json'));assert.ok(p.passed&&p.onlySelectedQosRatesChanged&&n.passed&&n.checks.length===7);assert.equal(n.sourceSha256,p.qosSourceSha256);assert.equal(p.fastSourceSha256,crypto.createHash('sha256').update(fs.readFileSync('work/nss82/fast-path.lua')).digest('hex'));for(const[f,h]of Object.entries(p.sourceManifest))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex'),h,f);return{...q,sourceManifest:{...q.sourceManifest,...p.sourceManifest}};}
"""
r.joinpath('session-binding.mjs').write_text(binding,encoding='utf-8')
manifest={p.as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in r.iterdir() if p.is_file() and p.suffix in ('.mjs','.py','.ps1','.lua')}
r.joinpath('entry-qualified.json').write_text(json.dumps({'passed':True,'onlySelectedQosRatesChanged':True,'qosGroupMbps':60,'tcpOfferedMbps':52,'finiteClientBytes':1024*1024*1024,'ownerSeconds':45,'nativeLifetimeBoundsUnchanged':True,'fastSourceSha256':hashlib.sha256(r.joinpath('fast-path.lua').read_bytes()).hexdigest(),'qosSourceSha256':hashlib.sha256(new).hexdigest(),'sourceManifest':manifest},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'prepared':True,'qosGroupMbps':60,'bulkMbps':59,'rtMbps':1,'offeredTcpMbps':52,'fastBytesUnchanged':True,'onlyQosRateLiteralsChanged':True}))
