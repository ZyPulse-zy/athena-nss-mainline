"""Prepare the required evening closure without opening another experiment."""
from pathlib import Path
r=Path(__file__).resolve().parent;out=r/'evening-20261006';out.mkdir()
for name in ['health','read-final-physical','verify-receivers','verify-downloaders']:
    s=(r/(name+'.mjs')).read_text(encoding='utf-8')
    s=s.replace("root='work/nss158'","root='work/nss158/evening-20261006'")
    s=s.replace("r='work/nss158'","r='work/nss158/evening-20261006'")
    s=s.replace("'work/nss158/receiver-closure","'work/nss158/evening-20261006/receiver-closure")
    s=s.replace("'work/nss158/download-receiver-closure","'work/nss158/evening-20261006/download-receiver-closure")
    with (r/('evening-'+name+'.mjs')).open('x',encoding='utf-8',newline='') as f:f.write(s)
s=(r/'verify-all-endpoints.mjs').read_text(encoding='utf-8')
assert s.count("root='work/nss158'")==1
s=s.replace("root='work/nss158'","root='work/nss158/evening-20261006'")
with (r/'evening-verify-all-endpoints.mjs').open('x',encoding='utf-8',newline='') as f:f.write(s)
print('Prepared exclusive evening closure directory; all original audit mechanisms unchanged; no connections/writes')
