"""Replay NSS35 classifier failure recovery without router access."""
import argparse,json,shutil,subprocess,sys,tempfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--wsl-runtime',type=Path,required=True);a=p.parse_args()
root=Path(__file__).resolve().parents[1];local=root/'.local';local.mkdir(exist_ok=True)
source=root/'code/work/nss35'
names=['worker.lua','guardian.lua','conntrack-source.lua','observation-policy.lua','address-query.lua','query-local-fixtures.lua','test-query-local.py','test-recovery.py']
results=[]
with tempfile.TemporaryDirectory(prefix='classifier-recovery-',dir=local)as d:
 stage=Path(d)
 for name in names:shutil.copyfile(source/name,stage/name)
 for script,result in [('test-recovery.py','recovery-qualified.json'),('test-query-local.py','query-local-qualified.json')]:
  run=subprocess.run([sys.executable,str(stage/script),'--wsl-runtime',str(a.wsl_runtime.resolve())],capture_output=True,text=True,timeout=45)
  if run.returncode:raise RuntimeError(run.stdout+'\n'+run.stderr)
  results.append(json.loads((stage/result).read_text(encoding='utf-8')))
out={'passed':all(r['passed']for r in results),'checks':sum(r['checks']for r in results),'parts':results,'routerAccess':False,'trafficGenerated':False,'productionFaultInjected':False}
(local/'classifier-recovery-replay.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
assert out['passed']and out['checks']==57
print(json.dumps({'passed':True,'checks':out['checks'],'routerAccess':False,'trafficGenerated':False}))
