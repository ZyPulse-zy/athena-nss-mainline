"""Prepare readonly final audits, preserving the exact preceding helper sources."""
from pathlib import Path
r=Path(__file__).resolve().parent; w=r.parents[1]
def put(n,s):
    p=r/n; assert not p.exists(),n
    p.write_text(s,encoding='utf-8',newline='')
s=(w/'work/nss150/verify-all-endpoints-v3.mjs').read_text(encoding='utf-8')
s=s.replace('147,149,150]', '147,149,150,151]').replace("root='work/nss150'", "root='work/nss151'")
s=s.replace("'work/nss150/load-v4-reference-private.json']", "'work/nss150/load-v4-reference-private.json','work/nss151/load-v2-reference-private.json']")
put('verify-all-endpoints.mjs',s)
for n in ['verify-downloaders.mjs','verify-receivers.mjs']:
    put(n,(w/('work/nss150/'+n)).read_text(encoding='utf-8').replace('work/nss150/', 'work/nss151/').replace("work/nss151/download-server.py", "work/nss150/download-server.py"))
s=(w/'work/nss150/calibrate-lifecycle.mjs').read_text(encoding='utf-8')
s=s.replace(r'nss(?:149|150)', 'nss151').replace('automatic-epoch', '(?:automatic-epoch|controlled-class)')
put('calibrate-clock.mjs',s)
print('Final physical, endpoint/client, receiver and clock audits prepared without executing them.')
