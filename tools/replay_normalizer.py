"""Replay the exact NSS37 normalizer differential suite without private captures or router IO."""
import argparse,json,shutil,subprocess,sys,tempfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--wsl-runtime',type=Path,required=True);a=p.parse_args()
root=Path(__file__).resolve().parents[1];local=root/'.local';local.mkdir(exist_ok=True)
source=root/'code/work/nss37'
with tempfile.TemporaryDirectory(prefix='normalizer-',dir=local)as d:
 stage=Path(d)
 for name in ['conntrack-source.lua','original-conntrack-source.lua','test-normalizer.py']:
  shutil.copyfile(source/name,stage/name)
 run=subprocess.run([sys.executable,str(stage/'test-normalizer.py'),'--wsl-runtime',str(a.wsl_runtime.resolve())],capture_output=True,text=True,timeout=50)
 if run.returncode:raise RuntimeError(run.stdout+'\n'+run.stderr)
 result=json.loads((stage/'normalizer-qualified.json').read_text(encoding='utf-8'))
 assert result['passed'] and result['checks']==9085 and not result['capturedTextReplayed']
 result.update(routerAccess=False,privateCaptureRead=False)
 (local/'normalizer-replay.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'passed':True,'checks':result['checks'],'routerAccess':False,'trafficGenerated':False,'privateCaptureRead':False}))
