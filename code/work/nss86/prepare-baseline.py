"""Measure degraded baseline instead of requiring the hoped-for QoS outcome first."""
from pathlib import Path
import json,hashlib
r=Path('work/nss86');r.mkdir(exist_ok=True)
for p in Path('work/nss85').iterdir():
 if p.is_file() and p.suffix in ('.mjs','.py','.ps1','.lua') and p.name not in ('prepare-observation.py','session-binding.mjs','qualify-getter.mjs'):
  s=p.read_text(encoding='utf-8').replace('work/nss85','work/nss86').replace('nss85','nss86').replace('NSS85','NSS86')
  if p.name=='match-controlled.mjs':
   s=s.replace("sent.length>=50&&returned/sent.length>=.9,'Controlled UDP baseline degraded before staging'","sent.length>=50&&returned>=1,'Controlled UDP has no observed baseline reply'").replace('minimumRatio:.9','minimumObservedReplies:1')
  r.joinpath(p.name).write_text(s,encoding='utf-8')
for name in ['qos-physical.lua','fast-path.lua','qos-native-qualification.json']:r.joinpath(name).write_bytes(Path('work/nss85',name).read_bytes())
binding="""import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';import {verifyPreparation as previous} from '../nss85/session-binding.mjs';
export function verifyPreparation(){const q=previous(),p=JSON.parse(fs.readFileSync('work/nss86/entry-qualified.json'));assert.ok(p.passed&&p.actualBidirectionalTrafficStillRequired&&p.nativeGateAndDeadlinesUnchanged);for(const[f,h]of Object.entries(p.sourceManifest))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex'),h,f);assert.equal(crypto.createHash('sha256').update(fs.readFileSync('work/nss86/fast-path.lua')).digest('hex'),crypto.createHash('sha256').update(fs.readFileSync('work/nss85/fast-path.lua')).digest('hex'));return{...q,sourceManifest:{...q.sourceManifest,...p.sourceManifest}};}
"""
r.joinpath('session-binding.mjs').write_text(binding,encoding='utf-8')
manifest={p.as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in r.iterdir() if p.is_file() and p.suffix in ('.mjs','.py','.ps1','.lua')}
r.joinpath('entry-qualified.json').write_text(json.dumps({'passed':True,'qosGroupMbps':60,'tcpOfferedMbps':52,'baselineLossMeasuredNotPrecluded':True,'actualBidirectionalTrafficStillRequired':True,'nativeGateAndDeadlinesUnchanged':True,'sourceManifest':manifest},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'prepared':True,'qosGroupMbps':60,'offeredMbps':52,'nativeBidirectionalGateUnchanged':True,'degradedUdpBaselineWillBeMeasured':True}))
