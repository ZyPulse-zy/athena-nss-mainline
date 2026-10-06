from pathlib import Path
import json
r=Path(__file__).resolve().parent;old=r.parent/'nss154'
helpers=['health.mjs','read-final-physical.mjs','verify-all-endpoints.mjs','verify-receivers.mjs','verify-downloaders.mjs','calibrate-clock.mjs','analyze.py']
first=json.loads((r/'run1/load-reference-private.json').read_text());first['unit']=json.loads((r.parents[1]/first['dir']/'server-deadline-private.json').read_text())['unit']
(r/'load-v1-reference-private.json').write_text(json.dumps(first,indent=2)+'\n',encoding='utf-8')
for name in helpers:
    p=r/name;assert not p.exists();s=(old/name).read_text(encoding='utf-8').replace("root='work/nss154'","root='work/nss155'").replace("r='work/nss154'","r='work/nss155'")
    if name=='verify-all-endpoints.mjs':
        anchor='const hashes=loads.map(s=>';assert s.count(anchor)==1
        s=s.replace(anchor,"for(const file of ['work/nss155/load-v1-reference-private.json','work/nss155/load-latest-private.json']){const x=JSON.parse(fs.readFileSync(file));assert.match(x.unit,/^nss155-[a-f0-9]{16}$/);assert.ok(!loads.some(y=>y.unit===x.unit));loads.push(x);}\n"+anchor)
    p.write_text(s,encoding='utf-8',newline='')
print('Post-run health reads ready; both finite owned loads preserved separately. No runtime source modified.')
