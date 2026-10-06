from pathlib import Path
r=Path(__file__).resolve().parent;old=r.parent/'nss156'
for dst,src in [('calibrate-clock.mjs','calibrate-clock-v2.mjs'),('analyze.py','analyze.py'),('read-final-physical.mjs','read-final-physical.mjs'),('verify-receivers.mjs','verify-receivers.mjs'),('verify-downloaders.mjs','verify-downloaders.mjs')]:
 s=(old/src).read_text(encoding='utf-8').replace('work/nss156','work/nss157').replace('work\\/nss156','work\\/nss157')
 p=r/dst;assert not p.exists();p.write_text(s,encoding='utf-8',newline='')
s=(old/'verify-all-endpoints.mjs').read_text(encoding='utf-8').replace("root='work/nss156'","root='work/nss157'")
a=s.index('const hashes=loads.map(')
extra="""const cases=[1,7,9,11,13,15,16];for(const n of cases){const file=`work/nss157/run${n}/load-reference-private.json`;if(!fs.existsSync(file))continue;const x=JSON.parse(fs.readFileSync(file));assert.match(x.unit,/^nss157-[a-f0-9]{16}$/);assert.ok(!loads.some(y=>y.unit===x.unit));loads.push(x);}
const partial=JSON.parse(fs.readFileSync('work/nss157/load-20261006090018-a34f1395f4a87e1b/server-deadline-private.json'));assert.match(partial.unit,/^nss157-[a-f0-9]{16}$/);assert.equal(JSON.parse(fs.readFileSync('work/nss157/load-20261006090018-a34f1395f4a87e1b/partial-cleanup.json')).passed,true);
"""
s=s[:a]+extra+s[a:]
s=s.replace('loads.map(s=>s.unit)',"[...loads.map(s=>s.unit),partial.unit]")
s=s.replace('const paths=loads.map(s=>s.dir.replaceAll',"const paths=[...loads,{dir:'work/nss157/load-20261006090018-a34f1395f4a87e1b'}].map(s=>s.dir.replaceAll")
p=r/'verify-all-endpoints.mjs';assert not p.exists();p.write_text(s,encoding='utf-8',newline='')
print('Fresh NSS157 postchecks prepared; all successful current load references plus independently closed partial unit included.')
