"""Give unchanged read-only closure tools exclusive fresh output paths."""
from pathlib import Path
r=Path(__file__).resolve().parent
for name in ['read-final-physical','verify-receivers','verify-downloaders']:
    s=(r/(name+'.mjs')).read_text(encoding='utf-8')
    if name=='read-final-physical':
        for old in ['physical-final-raw-private','physical-final','final-failed-wan-owner-private']:
            s=s.replace('/'+old+'.json','/v2-'+old+'.json')
    else:
        old='download-receiver-closure' if name=='verify-downloaders' else 'receiver-closure'
        s=s.replace('/'+old,'/v2-'+old)
    with (r/(name+'-v2.mjs')).open('x',encoding='utf-8',newline='') as f:f.write(s)
s=(r/'verify-all-endpoints.mjs').read_text(encoding='utf-8')
assert s.count("-v1'")==3
s=s.replace("-v1'","-v2'")
with (r/'verify-all-endpoints-v2.mjs').open('x',encoding='utf-8',newline='') as f:f.write(s)
print('Exclusive fresh outputs only; no audit or production policy changed')
