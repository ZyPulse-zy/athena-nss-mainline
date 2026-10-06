"""Readonly final audits include every old endpoint plus both new crash-test loads."""
from pathlib import Path
r=Path(__file__).resolve().parent;w=r.parents[1]
def put(n,s):
    p=r/n;assert not p.exists(),n;p.write_text(s,encoding='utf-8',newline='')
s=(w/'work/nss151/verify-all-endpoints.mjs').read_text(encoding='utf-8')
s=s.replace('147,149,150,151]', '147,149,150,151,152]').replace("root='work/nss151'", "root='work/nss152'")
a='const hashes=loads.map'
b="const firstCrash=JSON.parse(fs.readFileSync('work/nss152/load-v3-reference-private.json'));assert.match(firstCrash.unit,/^nss152-[a-f0-9]{16}$/);assert.ok(!loads.some(y=>y.unit===firstCrash.unit));loads.push(firstCrash);\nconst hashes=loads.map"
assert s.count(a)==1;s=s.replace(a,b)
put('verify-all-endpoints.mjs',s)
for n in ['verify-downloaders.mjs','verify-receivers.mjs']:
    put(n,(w/('work/nss151/'+n)).read_text(encoding='utf-8').replace('work/nss151/','work/nss152/'))
put('calibrate-clock.mjs',(w/'work/nss151/calibrate-clock.mjs').read_text(encoding='utf-8').replace(r'nss151\/',r'nss(?:151|152)\/'))
print('Final audit sources prepared; endpoint units and private references remain local.')
