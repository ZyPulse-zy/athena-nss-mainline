"""Keep negative neighbors outside the newly admitted five-tuple set."""
from pathlib import Path
import shutil,json,hashlib
g=Path(__file__).resolve().parent/'endpoint-gate';d=g/'failed-control-v2';d.mkdir()
for n in ['control_harness.py','control-harness.generated.c','control-host-run.log','control-host-build.log','predicate_test.c','ct_harness.py']:
 shutil.copyfile(g/n,d/n)
(d/'failure.json').write_text(json.dumps({'controlModelFailedCheck':33,'predicateNegativeNeighborFailed':True,'reason':'Adjacent fixture source ports made the +1 negative probe equal another intentionally whitelisted TCP tuple','nativeSourceUnchanged':True,'productionWrites':False},indent=2))
for n in ['control_harness.py','ct_harness.py','predicate_test.c']:
 p=g/n;s=p.read_text().replace('47778','47877').replace('47779','47977');p.write_text(s)
print('Corrected model-only source-port separation; native admission rules unchanged')
