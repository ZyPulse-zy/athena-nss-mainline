"""Reuse the exact closure checks with fresh output paths for NSS158."""
from pathlib import Path

root = Path(__file__).resolve().parent
prior = root.parent / 'nss157'

def put(name, text):
    with (root / name).open('x', encoding='utf-8', newline='') as f:
        f.write(text)

for name in ['health.mjs','read-final-physical.mjs','verify-receivers.mjs','verify-downloaders.mjs']:
    put(name, (prior/name).read_text(encoding='utf-8').replace('work/nss157', 'work/nss158'))
clock = (prior/'calibrate-clock.mjs').read_text(encoding='utf-8')
assert clock.count('work\\/nss157') == 1
put('calibrate-clock.mjs', clock.replace('work\\/nss157', 'work\\/nss158'))
endpoints = (prior/'verify-all-endpoints-v3.mjs').read_text(encoding='utf-8')
assert endpoints.count("root='work/nss157'") == 1
endpoints = endpoints.replace("root='work/nss157'", "root='work/nss158'")
assert endpoints.count('const pilotDirs=fs.readdirSync(root,') == 1
assert endpoints.count(".map(d=>root+'/'+d.name).sort();") == 1
endpoints = endpoints.replace('const pilotDirs=fs.readdirSync(root,', "const pilotRoot='work/nss157';const pilotDirs=fs.readdirSync(pilotRoot,")
endpoints = endpoints.replace(".map(d=>root+'/'+d.name).sort();", ".map(d=>pilotRoot+'/'+d.name).sort();")
put('verify-all-endpoints.mjs', endpoints.replace("-v3'", "-v1'"))
print('Prepared fresh complete health/physical/owned endpoint/receiver checks')
