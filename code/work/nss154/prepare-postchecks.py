from pathlib import Path
r=Path(__file__).resolve().parent;old=r.parent/'nss153'
names=['health.mjs','read-final-physical.mjs','verify-all-endpoints.mjs','verify-receivers.mjs','verify-downloaders.mjs','calibrate-clock.mjs','analyze.py']
for name in names:
    p=r/name;assert not p.exists();s=(old/name).read_text(encoding='utf-8')
    if name=='verify-all-endpoints.mjs':
        s=s.replace("root='work/nss153'","root='work/nss154'")
        anchor='const hashes=loads.map(';assert s.count(anchor)==1
        s=s.replace(anchor,"const thisRound=JSON.parse(fs.readFileSync('work/nss154/load-latest-private.json'));assert.match(thisRound.unit,/^nss154-[a-f0-9]{16}$/);assert.ok(!loads.some(x=>x.unit===thisRound.unit));loads.push(thisRound);\n"+anchor)
    else:s=s.replace('work/nss153','work/nss154').replace('nss153\\/','nss154\\/')
    p.write_text(s,encoding='utf-8',newline='')
print('Read-only closure prepared for the new supervisor restart test.')
