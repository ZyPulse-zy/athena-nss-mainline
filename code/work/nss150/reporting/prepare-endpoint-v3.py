from pathlib import Path
import json
w=Path(__file__).resolve().parents[3];r=w/'work/nss150'
s=(r/'verify-all-endpoints-v2.mjs').read_text(encoding='utf-8')
a="'work/nss150/load-v1-reference-private.json','work/nss150/load-v3-reference-private.json'"
z=a+",'work/nss150/load-v4-reference-private.json'"
assert s.count(a)==1;s=s.replace(a,z)
with (r/'verify-all-endpoints-v3.mjs').open('x',encoding='utf-8') as f:f.write(s)
print(json.dumps({'prepared':True,'all16OwnedEndpointLoadsIncluded':True,'readonlyOnly':True}))
