"""Bind the existing real-session interface to the tested controlled factory."""
from pathlib import Path
import json
r=Path('work/nss148')
for name in ['real-session.mjs','current-audit-diagnostic.mjs']:
    b=(Path('work/nss140')/name).read_bytes()
    s=b.replace(b'nss140',b'nss148').replace(b'NSS140',b'NSS148')
    assert s.replace(b'nss148',b'nss140').replace(b'NSS148',b'NSS140')==b
    for f in ['declared-baseline.mjs','compact-default-queues.mjs','service-epoch.mjs','parse-ecm-any-wan.mjs','module-stage.mjs','uplink-tag-plan.mjs']:
        s=s.replace(("'./"+f+"'").encode(),("'../nss147/"+f+"'").encode())
    if name=='real-session.mjs':
        s=s.replace(b'work/nss148/uplink-capacity-private.json',b'work/nss140/uplink-capacity-private.json')
    with (r/name).open('xb') as stream:stream.write(s)
for name in ['read-real-candidates.mjs','record-candidates.mjs']:
    b=(Path('work/nss143')/name).read_bytes()
    s=b.replace(b'nss143',b'nss148').replace(b'NSS143',b'NSS148')
    assert s.replace(b'nss148',b'nss143').replace(b'NSS148',b'NSS143')==b
    s=s.replace(b"from'./candidate-adapter.mjs'",b"from'../nss143/candidate-adapter.mjs'")
    with (r/name).open('xb') as stream:stream.write(s)
for name in ['failed-wan-owner.lua','declared-baseline.mjs']:
    with (r/name).open('xb') as stream:stream.write((Path('work/nss147')/name).read_bytes())
print(json.dumps({'prepared':True,'sameTestedNss147Factory':True,'readerUsesQualified143CandidateAdapter':True,'defaultReadonly':True,'desktopOperated':False,'routerWrites':False}))
