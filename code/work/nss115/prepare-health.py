from pathlib import Path
r=Path('work/nss115');s=Path('work/nss110/health.mjs').read_text(encoding='utf-8').replace('nss110','nss115')
(r/'health.mjs').write_text(s,encoding='utf-8')
print('Prepared original native closure for new round')
