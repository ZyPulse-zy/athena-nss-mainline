from pathlib import Path
import json
r=Path(__file__).resolve().parent;old=r.parent/'nss155'
for name in ['health.mjs','read-final-physical.mjs','verify-receivers.mjs','verify-downloaders.mjs','calibrate-clock.mjs','analyze.py']:
    p=r/name;assert not p.exists();s=(old/name).read_text(encoding='utf-8').replace("root='work/nss155'","root='work/nss156'").replace("r='work/nss155'","r='work/nss156'")
    s=s.replace('work/nss155/receiver-closure','work/nss156/receiver-closure').replace('work/nss155/download-receiver-closure','work/nss156/download-receiver-closure')
    p.write_text(s,encoding='utf-8',newline='')
refs=[]
for n in ['run1','run2','run3','run4','run5','run6','run7']:
    source=r/n/'load-reference-private.json';x=json.loads(source.read_text(encoding='utf-8'));launch=json.loads((r.parents[1]/x['dir']/'launch-receipt.json').read_text(encoding='utf-8'));x['unit']=launch['unit']
    p=r/f'load-{n}-reference-private.json';assert not p.exists();p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8');refs.append('work/nss156/'+p.name)
s=(old/'verify-all-endpoints.mjs').read_text(encoding='utf-8').replace("root='work/nss155'","root='work/nss156'")
anchor='const hashes=loads.map(s=>';assert s.count(anchor)==1
s=s.replace(anchor,"for(const file of "+json.dumps(refs)+"){const x=JSON.parse(fs.readFileSync(file));assert.match(x.unit,/^nss156-[a-f0-9]{16}$/);assert.ok(!loads.some(y=>y.unit===x.unit));loads.push(x);}\n"+anchor)
p=r/'verify-all-endpoints.mjs';assert not p.exists();p.write_text(s,encoding='utf-8',newline='')
print('Output namespace checked; original 27 owned endpoints plus seven NSS156 loads only.')
