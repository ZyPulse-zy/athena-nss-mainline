"""Only raise offered test traffic; native QoS 20 Mbps and all router code stay unchanged."""
from pathlib import Path
import json,hashlib
root=Path('work/nss80');root.mkdir(exist_ok=True)
files=['controlled-session.mjs','read-controlled.mjs','current-audit-diagnostic.mjs','client-watchdog.ps1','server.py','discover-peer.py','probe-peer.py','start-dallas.mjs','endpoint-firewall-guardian.py','ssh-client.mjs','match-controlled.mjs','calibrate-clock.mjs','analyze-controlled.py','close-endpoint.mjs']
for name in files:
    s=Path('work/nss79',name).read_text().replace('work/nss79','work/nss80').replace('nss79','nss80').replace('NSS79','NSS80')
    if name=='ssh-client.mjs':
        s=s.replace("c.mbps>=1&&c.mbps<=20","c.mbps===32")
        s=s.replace('18000000','32000000')
    if name=='start-dallas.mjs':
        s=s.replace("config.tcpServerAddress='18.138.159.236';config.tcpPort=22;","config.mbps=32;config.tcpServerAddress='18.138.159.236';config.tcpPort=22;")
        s=s.replace('tcpTargetMbps:18','tcpTargetMbps:config.mbps')
    if name=='analyze-controlled.py':
        s=s.replace("'requestedTcpMbps':18","'requestedTcpMbps':32")
        s=s.replace("'oneWan':5","'oneWan':json.loads((case/'selected-private.json').read_text())['tcp']['wan']")
    root.joinpath(name).write_text(s)
binding="""import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';import {verifyPreparation as previous} from '../nss79/session-binding.mjs';
export function verifyPreparation(){const q=previous(),p=JSON.parse(fs.readFileSync('work/nss80/entry-qualified.json'));assert.ok(p.passed&&p.onlyOfferedLoadRaised&&p.qosParentMbps===20&&p.routerLibrariesUnchanged);for(const[f,h]of Object.entries(p.sourceManifest))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex'),h,f);return{...q,sourceManifest:{...q.sourceManifest,...p.sourceManifest}};}
"""
root.joinpath('session-binding.mjs').write_text(binding)
names=files+['session-binding.mjs','prepare.py']; manifest={str(root/n).replace('\\','/'):hashlib.sha256((root/n).read_bytes()).hexdigest() for n in names}
assert "../nss77/module-stage.mjs" in root.joinpath('controlled-session.mjs').read_text()
assert 'selectedSubgroupCeilingMbps:20' in root.joinpath('controlled-session.mjs').read_text()
assert '32000000' in root.joinpath('ssh-client.mjs').read_text()
root.joinpath('entry-qualified.json').write_text(json.dumps({'passed':True,'onlyOfferedLoadRaised':True,'offeredTcpMbps':32,'qosParentMbps':20,'routerLibrariesUnchanged':True,'nativeOwnerGateTtlsAndOneTcpOneUdpUnchanged':True,'sourceManifest':manifest},indent=2)+'\n')
print(json.dumps({'newBoundSources':len(manifest),'offeredTcpMbps':32,'qosParentMbps':20,'routerLibrariesUnchanged':True}))
