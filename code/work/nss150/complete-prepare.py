from pathlib import Path
import json,hashlib
r=Path('work/nss150');old=Path('work/nss149')
p=json.loads((old/'entry-qualified.json').read_text(encoding='utf-8'))
for name in ['run.mjs','lifecycle-policy.mjs','policy-models.mjs','verify-receivers.mjs']:
    src=old/name;b=src.read_bytes();assert hashlib.sha256(b).hexdigest()==p['sourceManifest'][src.as_posix()]
    s=b.replace(b'nss149',b'nss150').replace(b'NSS149',b'NSS150')
    if name=='lifecycle-policy.mjs':
        a=b"status.elapsed<80,'Insufficient fixed client lifetime for a new owner'"
        z=b"status.elapsed<110,'Insufficient fixed client lifetime for a new owner'"
        assert s.count(a)==1;s=s.replace(a,z)
    if name=='policy-models.mjs':
        s=s.replace(b"['expired-client',{elapsed:81}]",b"['expired-client',{elapsed:111}]")
        a=b"requireOwnedLifetime(config,status,load,100);cases.push({case:'owned-fresh-client-accepts',passed:true,modelOnly:true});"
        assert s.count(a)==1;s=s.replace(a,a+b"\nrequireOwnedLifetime(config,{...status,elapsed:90},load,100);cases.push({case:'fresh-client-with-90-seconds-remaining-accepts',passed:true,modelOnly:true});")
    with (r/name).open('xb') as f:f.write(s)
print(json.dumps({'prepared':True,'firstPartialPreparationPreserved':True,'operationalFactoryNotChanged':True,'routerWrites':False}))
