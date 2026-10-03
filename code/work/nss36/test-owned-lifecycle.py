"""Existing rule adoption and crash recovery, exact deployed pure reconciler with mocked tc."""
import hashlib,json,re,shutil,subprocess
from pathlib import Path
here=Path(__file__).resolve().parent;root=here.parents[1];stage=here/'owned-fixtures-private';stage.mkdir(exist_ok=True)
dep=json.loads((root/'work/nss35/deployment-latest.json').read_text());cfg=json.loads((root/dep['localDir']/'config.json').read_text());hashes={}
for name in ['owned.lua','backend.lua']:
 src=root/'athena-nss-mainline/code/deployed-classifier'/name;digest=hashlib.sha256(src.read_bytes()).hexdigest();assert digest==cfg['files'][name];hashes[name]=digest;shutil.copyfile(src,stage/name)
for name in ['backend-fixtures.lua','backend-input-private.lua']:shutil.copyfile(root/'work/nss23'/name,stage/name)
def unix(p):
 s=p.resolve().as_posix();return '/mnt/'+s[0].lower()+s[2:]
rt=root/'work/nss9/lua-runtime/extracted/usr'
r=subprocess.run(['wsl.exe','-d','Athena-Cake-Build','--exec','/usr/bin/env','LD_LIBRARY_PATH='+unix(rt/'lib/x86_64-linux-gnu'),unix(rt/'bin/lua5.1'),unix(stage/'backend-fixtures.lua'),unix(stage)],capture_output=True,text=True,timeout=30)
(here/'owned-lifecycle-output.txt').write_text(r.stdout+r.stderr,encoding='utf-8');cases=re.findall(r'^PASS (.*)$',r.stdout,re.M)
out={'passed':r.returncode==0,'checks':len(cases),'cases':cases,'sourceSha256':hashes,'configurationSha256':dep['configHash'],'routerWrites':False,'actualTcWrites':False,'scope':'Exact deployed ownership and reconciler modules; historical private rule fixture and simulated tc/journal operations. No production restart, crash or broad cleanup.','error':r.stderr}
(here/'owned-lifecycle-qualified.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out));raise SystemExit(r.returncode)
