"""Inspect JS imports only in JS, rather than generator replacement strings."""
from pathlib import Path
import json

root = Path(__file__).resolve().parent
source = (root / 'qualify-entry.mjs').read_text(encoding='utf-8')
old = "'pilot-supervisor.mjs','qualify-entry.mjs'];"
assert source.count(old) == 1
source = source.replace(old, "'pilot-supervisor.mjs','qualify-entry.mjs','prepare-qualification-v2.py','qualify-entry-v2.mjs'];")
assert source.count(' for(const m of text.matchAll(') == 2
source = source.replace(' for(const m of text.matchAll(', " if(name.endsWith('.mjs'))for(const m of text.matchAll(")
with (root / 'qualify-entry-v2.mjs').open('x', encoding='utf-8', newline='') as f:
    f.write(source)
failure = {'passed':False,'source':'work/nss158/qualify-entry.mjs',
           'error':'Unbound import work/nss158/payload-v4.mjs',
           'cause':'JavaScript import regex scanned a Python generator replacement string',
           'originalSourcePreserved':True,'refusedBeforeRouterConnect':True,'productionWrites':False}
with (root / 'qualification-v1-failure.json').open('x', encoding='utf-8') as f:
    json.dump(failure, f, indent=2);f.write('\n')
print('Prepared language-specific import validation; old refusal retained')
