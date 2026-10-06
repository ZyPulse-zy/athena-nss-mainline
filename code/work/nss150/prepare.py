from pathlib import Path
import json,hashlib
r=Path('work/nss150');old=Path('work/nss149')
p=json.loads((old/'entry-qualified.json').read_text(encoding='utf-8'))
names=['controlled-session.mjs','current-audit-diagnostic.mjs','read-controlled.mjs',
       'start-dallas.mjs','ssh-client.mjs','download-server.py','server.py',
       'endpoint-firewall-guardian.py','client-watchdog.ps1','discover-peer.py',
       'probe-peer.py','match-controlled.mjs','close-endpoint.mjs','health.mjs',
       'read-final-physical.mjs','verify-old-endpoints.mjs','verify-downloaders.mjs',
       'verify-all-endpoints.mjs','verify-receivers.mjs','run.mjs','lifecycle-policy.mjs','policy-models.mjs']
for name in names:
    src=old/name;b=src.read_bytes();assert hashlib.sha256(b).hexdigest()==p['sourceManifest'][src.as_posix()]
    s=b.replace(b'nss149',b'nss150').replace(b'NSS149',b'NSS150')
    if name=='controlled-session.mjs':
        s=s.replace(b"from './module-stage.mjs'",b"from '../nss149/module-stage.mjs'")
    if name=='lifecycle-policy.mjs':
        a=b"status.elapsed<80,'Insufficient fixed client lifetime for a new owner'"
        z=b"status.elapsed<110,'Insufficient fixed client lifetime for a new owner'"
        assert s.count(a)==1;s=s.replace(a,z)
    if name=='policy-models.mjs':
        s=s.replace(b"['expired-client',{elapsed:81}]",b"['expired-client',{elapsed:111}]")
        needle=b"requireOwnedLifetime(config,status,load,100);cases.push({case:'owned-fresh-client-accepts',passed:true,modelOnly:true});"
        assert s.count(needle)==1
        s=s.replace(needle,needle+b"\nrequireOwnedLifetime(config,{...status,elapsed:90},load,100);cases.push({case:'fresh-client-with-90-seconds-remaining-accepts',passed:true,modelOnly:true});")
    with (r/name).open('xb') as f:f.write(s)
print(json.dumps({'prepared':True,'changedVariable':'client admission preparation margin only',
  'clientHardSeconds':180,'sourceSeconds':6,'nativeHardSeconds':27,'ownerHardSeconds':100,
  'tested149FactoryReusedExactly':True,'routerWrites':False}))
