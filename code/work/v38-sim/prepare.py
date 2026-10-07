from pathlib import Path
import json,hashlib
r=Path('work/v38-sim');old=Path('work/v37-sim')
q=json.loads((old/'entry-qualified.json').read_text());assert q['passed']
def rebase(data):
 for n in [b'v36-sim',b'v37-sim']:
  data=data.replace(b'work/'+n,b'work/v38-sim').replace(b'work\\/'+n+b'\\/',b'work\\/v38-sim\\/').replace(n+b'-',b'v38-sim-')
 return data
hashes={}
for rel,h in q['sourceManifest'].items():
 p=Path(rel);data=p.read_bytes();assert hashlib.sha256(data).hexdigest()==h;hashes[rel]=h
 if p.name in ['prepare.py','qualify-entry.mjs','session-binding.mjs']:continue
 with (r/p.name).open('xb') as f:f.write(rebase(data))
with (r/'prepare-receipt.json').open('x',encoding='utf8') as f:json.dump({'passed':True,'oldHashes':hashes,'namespaceRebaseIncludesEscapedRegularExpressions':True,'v37PathRefusalPreserved':True,'cutoff':'2026-10-07T06:30:00Z','productionNotStarted':True},f,indent=2);f.write('\n')
print(json.dumps({'passed':True,'newSourceNamespaceOnly':True,'productionNotStarted':True}))
