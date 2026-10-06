from pathlib import Path
import json
r = Path(__file__).resolve().parent
s = (r/'qualify-v5.mjs').read_text(encoding='utf-8')
assert s.count("'qualify-v5.mjs','health.mjs'") == 1
s = s.replace("'qualify-v5.mjs','health.mjs'", "'qualify-v5.mjs','prepare-qualification-v6.py','qualify-v6.mjs'")
p=r/'qualify-v6.mjs';assert not p.exists();p.write_text(s,encoding='utf-8',newline='')
p=r/'qualification-v5-failure.json';assert not p.exists();p.write_text(json.dumps({'passed':False,'phase':'local dependency binding before production','error':'Unbound work/nss109/failover-baseline.mjs','routerConnected':False,'productionWrites':False,'repair':'Do not conflate separately executed operational final-health audit with NSS production entry dependencies; every actual entry dependency remains bound'},indent=2)+'\n',encoding='utf-8')
print('Operational health script excluded from production entry, original binding failure retained.')
