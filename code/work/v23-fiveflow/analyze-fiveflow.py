"""Use only the completed five-flow pilot; keep prior pre-admission attempts visible."""
from pathlib import Path

r = Path(__file__).resolve().parent
s = (r / 'analyze-hardware.py').read_text(encoding='utf8')
old = "pilots=sorted(root.glob('pilot-aba-*'));assert len(pilots)==1;pilot=pilots[0]"
new = "pilots=sorted(root.glob('pilot-aba-*'));completed=[p for p in pilots if (p/'automatic-result.json').exists() and __import__('json').loads((p/'automatic-result.json').read_text())['passed']];assert len(completed)==1;pilot=completed[0]"
assert s.count(old) == 1
exec(compile(s.replace(old, new), str(r / 'analyze-hardware.py'), 'exec'), {'__file__': str(r / 'analyze-hardware.py'), '__name__': '__main__'})
