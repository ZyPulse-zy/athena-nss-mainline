"""Add only exclusive current pilot directories to the read-only endpoint audit."""
from pathlib import Path

root = Path(__file__).resolve().parent
source = (root / 'verify-all-endpoints.mjs').read_text(encoding='utf-8')
marker = "const partial=JSON.parse"
assert source.count(marker) == 1
addition = """const pilotDirs=fs.readdirSync(root,{withFileTypes:true}).filter(d=>d.isDirectory()&&/^pilot-(?:change|close)-\\d{14}-[a-f0-9]{16}$/.test(d.name)).map(d=>root+'/'+d.name).sort();
for(const d of pilotDirs){const file=d+'/load-reference-private.json';if(!fs.existsSync(file))continue;const x=JSON.parse(fs.readFileSync(file));assert.match(x.unit,/^nss157-[a-f0-9]{16}$/);assert.match(x.dir,/^work\\/nss157\\/load-\\d{14}-[a-f0-9]{16}$/);assert.ok(!loads.some(y=>y.unit===x.unit));loads.push(x);}
"""
result = source.replace(marker, addition + marker)
for name in ['endpoint-remote-raw-private', 'client-closure-raw-private', 'endpoint-client-closure']:
    assert result.count("save('" + name + "'") == 1
    result = result.replace("save('" + name + "'", "save('" + name + "-v2'")
target = root / 'verify-all-endpoints-v2.mjs'
with target.open('x', encoding='utf-8', newline='') as out:
    out.write(result)
print('Prepared exact owned pilot enumeration; audit not executed')
