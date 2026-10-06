"""Carry the exact declared-baseline helper required by the new audit namespace."""
from pathlib import Path
import json

root = Path(__file__).resolve().parent
with (root / 'declared-baseline.mjs').open('xb') as f:
    f.write((root.parent / 'nss157/declared-baseline.mjs').read_bytes())
source = (root / 'qualify-entry-v2.mjs').read_text(encoding='utf-8')
old = "'prepare-qualification-v2.py','qualify-entry-v2.mjs'];"
assert source.count(old) == 1
source = source.replace(old, "'prepare-qualification-v2.py','qualify-entry-v2.mjs','declared-baseline.mjs','prepare-qualification-v3.py','qualify-entry-v3.mjs'];")
with (root / 'qualify-entry-v3.mjs').open('x', encoding='utf-8', newline='') as f:
    f.write(source)
failure = {'passed':False,'source':'work/nss158/qualify-entry-v2.mjs',
           'error':'Unbound literal work/nss158/declared-baseline.mjs',
           'cause':'New audit namespace referenced an existing byte-identical declared-baseline helper that had not been copied',
           'originalSourcePreserved':True,'refusedBeforeRouterConnect':True,'productionWrites':False}
with (root / 'qualification-v2-failure.json').open('x', encoding='utf-8') as f:
    json.dump(failure, f, indent=2);f.write('\n')
print('Bound exact required baseline helper; no baseline policy changed')
