"""Run NSS36 admission differential replay from only the curated repository."""
import argparse,json,shutil,subprocess,sys
from pathlib import Path
repo=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description='212 offline checks; no router or network IO.')
p.add_argument('--wsl-runtime',required=True,type=Path)
args=p.parse_args()
stage=repo/'.local/nss36-replay'
files=['work/nss36/test-admission.py','work/nss36/classifier.lua','work/nss36/fast-path.lua','work/nss33/classifier.lua','work/nss23/consumer-fixtures.lua','work/nss27/renewal-consumer-fixtures.lua']
for name in files:
    src=repo/'code'/name; dst=stage/name
    dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
run=subprocess.run([sys.executable,str(stage/'work/nss36/test-admission.py'),'--wsl-runtime',str(args.wsl_runtime.resolve()),'--timing',str(repo/'evidence/nss33-admission-timing.json')],capture_output=True,text=True,timeout=40)
if run.returncode:
    print(run.stderr);print(run.stdout);raise SystemExit(run.returncode)
result=json.loads((stage/'work/nss36/admission-qualified.json').read_text())
assert result['passed'] and result['checks']==212 and result['differentialAdmissionCases']==108
print(json.dumps({k:v for k,v in result.items() if k not in ('cases','error')}))
