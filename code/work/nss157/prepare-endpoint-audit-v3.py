"""Resolve startup summaries to the same owned directory's OS deadline receipt."""
from pathlib import Path
import json

root = Path(__file__).resolve().parent
source = (root / 'verify-all-endpoints-v2.mjs').read_text(encoding='utf-8')
helper = """function ownedReference(x){assert.equal(x.started,true);assert.match(x.dir,/^work\\/nss157\\/load-\\d{14}-[a-f0-9]{16}$/);const s=JSON.parse(fs.readFileSync(x.dir+'/server-deadline-private.json'));assert.match(s.unit,/^nss157-[a-f0-9]{16}$/);assert.equal(s.verifiedBeforeClientTraffic,true);assert.equal(s.independentOsDeadlineSeconds,250);if(x.unit!==undefined)assert.equal(x.unit,s.unit);return{...x,unit:s.unit};}
"""
assert source.count('const cases=') == 1
source = source.replace('const cases=', helper + 'const cases=')
lines = source.splitlines(keepends=True)
changed = 0
for index, line in enumerate(lines):
    if line.startswith('const cases=') or line.startswith('for(const d of pilotDirs)'):
        assert line.count('const x=JSON.parse(fs.readFileSync(file));') == 1
        lines[index] = line.replace('const x=JSON.parse(fs.readFileSync(file));', 'const x=ownedReference(JSON.parse(fs.readFileSync(file)));')
        changed += 1
assert changed == 2
source = ''.join(lines)
extra = """const abaRoot='work/nss158';const abaDirs=fs.readdirSync(abaRoot,{withFileTypes:true}).filter(d=>d.isDirectory()&&/^pilot-aba-\\d{14}-[a-f0-9]{16}$/.test(d.name)).map(d=>abaRoot+'/'+d.name).sort();for(const d of abaDirs){const file=d+'/load-reference-private.json';if(!fs.existsSync(file))continue;const x=ownedReference(JSON.parse(fs.readFileSync(file)));assert.ok(!loads.some(y=>y.unit===x.unit));loads.push(x);}
"""
assert source.count('const partial=') == 1
source = source.replace('const partial=', extra + 'const partial=')
source = source.replace("-v2'", "-v3'")
with (root / 'verify-all-endpoints-v3.mjs').open('x', encoding='utf-8', newline='') as f:
    f.write(source)
failure = {'passed':False,'source':'work/nss157/verify-all-endpoints-v2.mjs',
           'error':'AssertionError: string argument undefined at x.unit',
           'cause':'Harness stored startup summary, while the OS-owned unit is in its same directory deadline receipt',
           'refusedBeforeRemoteConnect':True,'originalSourcePreserved':True,'remoteWrites':False}
with (root / 'endpoint-audit-v2-failure.json').open('x', encoding='utf-8') as f:
    json.dump(failure, f, indent=2);f.write('\n')
print('Prepared exact owned receipt mapping and finite ABA fixture enumeration')
