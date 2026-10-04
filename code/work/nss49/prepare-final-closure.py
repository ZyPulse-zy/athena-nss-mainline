from pathlib import Path

base=Path('work/nss49')
original=(base/'final-closure.mjs').read_bytes()
target=base/'final-cleanup-audit.mjs'
assert not target.exists()
target.write_bytes(original.replace(b"'work/nss49/final-closure.json'",b"'work/nss49/final-cleanup-audit.json'"))
(base/'second-attempt-readiness-private.json').write_bytes((base/'real-session-readiness.json').read_bytes())
