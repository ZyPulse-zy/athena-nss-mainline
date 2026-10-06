"""Resolve copied entry-local imports before any new qualification is frozen."""
from pathlib import Path
import re

w = Path(__file__).resolve().parents[2]; r = w / 'work/v26-normal'; old = w / 'work/v20-five'
added = []
while True:
    missing = set()
    for p in r.glob('*.mjs'):
        for target in re.findall(r'''(?:from\s*|import\s*)['"](\./[^'"]+\.mjs)['"]''', p.read_text(encoding='utf8')):
            q = p.parent / target
            if not q.exists():
                missing.add(q.name)
    if not missing:
        break
    for name in sorted(missing):
        source = old / name
        assert source.exists(), name
        data = source.read_bytes().replace(b'work/v20-five', b'work/v26-normal').replace(rb'work\/v20-five\/', rb'work\/v26-normal\/')
        with (r / name).open('xb') as f:
            f.write(data)
        added.append(name)
print('Original local dependencies added: ' + ', '.join(added))
