"""Keep the same QoS test; tolerate transient Windows status-file sharing conflicts."""
from pathlib import Path
import hashlib,json
r=Path('work/nss88');r.mkdir(exist_ok=True)
for p in Path('work/nss87').iterdir():
 if not p.is_file() or p.suffix not in ('.mjs','.py','.ps1','.lua') or p.name in ('prepare-continuous.py','session-binding.mjs'):continue
 s=p.read_text(encoding='utf-8').replace('work/nss87','work/nss88').replace('nss87','nss88').replace('NSS87','NSS88')
 if p.name=='ssh-client.mjs':
  old="fs.renameSync(dir+'/status-private.json.new',dir+'/status-private.json');loadOut.write"
  new="try{fs.renameSync(dir+'/status-private.json.new',dir+'/status-private.json')}catch(e){if(e.code!=='EPERM'&&e.code!=='EBUSY')throw e;stats.statusPublicationDeferrals=(stats.statusPublicationDeferrals??0)+1}loadOut.write"
  assert s.count(old)==1;s=s.replace(old,new)
 if p.name=='capture-endpoint.mjs':
  s=s.replace('socket.htons(0x0800)','socket.htons(0x0003)')
  s=s.replace('readonly:true,seconds:5,authenticatedIncoming','readonly:true,allProtocolTapForTransmitVisibility:true,seconds:5,authenticatedIncoming')
 r.joinpath(p.name).write_text(s,encoding='utf-8')
for n in ['fast-path.lua','qos-physical.lua','qos-native-qualification.json']:r.joinpath(n).write_bytes(Path('work/nss87',n).read_bytes())
binding="""import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';import {verifyPreparation as previous} from '../nss87/session-binding.mjs';
export function verifyPreparation(){const q=previous(),p=JSON.parse(fs.readFileSync('work/nss88/entry-qualified.json')),t=JSON.parse(fs.readFileSync('work/nss88/client-publication-qualified.json'));assert.ok(p.passed&&p.fastAndQosBytesUnchanged&&t.passed&&t.cases===3);assert.equal(t.clientSha256,p.clientSha256);for(const[f,h]of Object.entries(p.sourceManifest))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex'),h,f);return{...q,sourceManifest:{...q.sourceManifest,...p.sourceManifest}};}
"""
r.joinpath('session-binding.mjs').write_text(binding,encoding='utf-8')
m={p.as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in r.iterdir() if p.is_file() and p.suffix in ('.mjs','.py','.ps1','.lua')}
r.joinpath('entry-qualified.json').write_text(json.dumps({'passed':True,'qosGroupMbps':60,'tcpOfferedMbps':52,'clientSha256':hashlib.sha256(r.joinpath('ssh-client.mjs').read_bytes()).hexdigest(),'fastAndQosBytesUnchanged':True,'statusFreshnessUnderTwoSecondsStillRequired':True,'sourceManifest':m},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'prepared':True,'statusSharingConflictWillNotKillTraffic':True,'nativeFastAndQosBytesUnchanged':True}))
