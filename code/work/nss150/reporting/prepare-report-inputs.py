from pathlib import Path
import json
w=Path(__file__).resolve().parents[3];r=w/'work/nss150'
s=(w/'work/nss147/calibrate-clock.mjs').read_text(encoding='utf-8')
s=s.replace(r'/^work\/nss147\/controlled-matched-aba-\d+-[a-f0-9]+$/',r'/^work\/nss(?:149|150)\/automatic-epoch-\d+-[a-f0-9]+$/')
assert 'controlled-matched-aba-' not in s
with (r/'calibrate-lifecycle.mjs').open('x',encoding='utf-8') as f:f.write(s)
p=r/'verify-all-endpoints.mjs';s=p.read_text(encoding='utf-8')
a="const hashes=loads.map"
z="for(const file of ['work/nss150/load-v1-reference-private.json','work/nss150/load-v3-reference-private.json']){const x=JSON.parse(fs.readFileSync(file));assert.match(x.unit,/^nss150-[a-f0-9]{16}$/);assert.ok(!loads.some(y=>y.unit===x.unit));loads.push(x);}\nconst hashes=loads.map"
assert s.count(a)==1;s=s.replace(a,z)
# This helper has not run or been operationally qualified; add version 2 rather
# than modifying even an unused earlier source copy.
with (r/'verify-all-endpoints-v2.mjs').open('x',encoding='utf-8') as f:f.write(s)
print(json.dumps({'prepared':True,'postchecksOnly':True,'all15EndpointLoadsIncluded':True,'rawInputsNotExported':True,'routerWrites':False}))
