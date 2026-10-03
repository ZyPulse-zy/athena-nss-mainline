"""Run the NSS38 traced candidate from curated sources only; no router access."""
import argparse,json,shutil,subprocess,sys
from pathlib import Path
repo=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--wsl-runtime',required=True,type=Path);a=p.parse_args()
stage=repo/'.local/nss38-replay'
files=['work/nss38/test-adapter-differential.py','work/nss38/adapter-differential.lua','work/nss38/test-admission.py','work/nss38/candidate-traced-classifier.lua','work/nss38/candidate-traced-fast-path.lua','work/nss37/classifier.lua','work/nss33/classifier.lua','work/nss23/consumer-fixtures.lua','work/nss27/renewal-consumer-fixtures.lua']
for name in files:
    dst=stage/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(repo/'code'/name,dst)
for name,extra in [('test-adapter-differential.py',[]),('test-admission.py',['--timing',str(repo/'evidence/nss33-admission-timing.json')])]:
    r=subprocess.run([sys.executable,str(stage/'work/nss38'/name),'--traced','--wsl-runtime',str(a.wsl_runtime.resolve()),*extra],capture_output=True,text=True,timeout=40)
    if r.returncode:print(r.stdout);print(r.stderr);raise SystemExit(r.returncode)
diff=json.loads((stage/'work/nss38/traced-adapter-differential-qualified.json').read_text())
admit=json.loads((stage/'work/nss38/traced-admission-qualified.json').read_text())
assert diff['passed'] and diff['differentialCases']==1470 and diff['inspectionCountChecks']==5
assert admit['passed'] and admit['checks']==230
proof=json.loads((repo/'evidence/nss38-mainline.json').read_text())['candidate']['trace']
assert diff['newSha256']==admit['adapterSha256']==proof['adapterSha256']
assert admit['fastSourceSha256']==proof['fastSha256']
print(json.dumps({'passed':True,'decisionCases':1470,'inspectionCountChecks':5,'admissionAndDiagnosticChecks':230,'routerAccess':False,'scope':'Synthetic IO, identities, time and serialization; native firmware admission not qualified.'}))
