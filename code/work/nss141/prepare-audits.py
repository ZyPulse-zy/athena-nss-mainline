"""New read-only round; do not overwrite the last published operational evidence."""
from pathlib import Path
import json
w=Path(__file__).resolve().parents[2];r=w/'work/nss141';r.mkdir(exist_ok=True)
for name in ['health.mjs','read-final-physical.mjs','verify-receivers.mjs']:
 source=(w/'work/nss139'/name).read_bytes();b=source.replace(b'nss139',b'nss141').replace(b'NSS139',b'NSS141')
 assert b.replace(b'nss141',b'nss139').replace(b'NSS141',b'NSS139')==source
 target=r/name;assert not target.exists();target.write_bytes(b)
print(json.dumps({'prepared':True,'routerWrites':False,'namespaceOnly':True}))
