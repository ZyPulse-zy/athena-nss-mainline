from pathlib import Path
r=Path(__file__).resolve().parent;old=r.parent/'nss152'
files={'health-v3.mjs':'health.mjs','read-final-physical-v3.mjs':'read-final-physical.mjs','verify-all-endpoints.mjs':'verify-all-endpoints.mjs','verify-receivers.mjs':'verify-receivers.mjs','verify-downloaders.mjs':'verify-downloaders.mjs','calibrate-clock.mjs':'calibrate-clock.mjs','analyze.py':'analyze.py'}
for a,b in files.items():
    p=r/b;assert not p.exists();s=(old/a).read_text(encoding='utf-8')
    if b=='verify-all-endpoints.mjs':
        # All old 20 references remain byte-identical; append this round only.
        s=s.replace("root='work/nss152'", "root='work/nss153'")
        anchor='const hashes=loads.map('
        assert s.count(anchor)==1
        s=s.replace(anchor,"const current=JSON.parse(fs.readFileSync('work/nss153/load-latest-private.json'));assert.match(current.unit,/^nss153-[a-f0-9]{16}$/);assert.ok(!loads.some(x=>x.unit===current.unit));loads.push(current);\n"+anchor)
    else:
        s=s.replace('work/nss152','work/nss153').replace('run-v4/','run1/')
    if b=='calibrate-clock.mjs':s=s.replace('nss(?:151|152)', 'nss153')
    if b=='analyze.py':s=s.replace("read_text().splitlines()", "read_text(encoding='utf-8').splitlines()")
    p.write_text(s,encoding='utf-8',newline='')
print('Read-only complete health, physical roots, all 21 endpoints and descriptive metrics prepared.')
