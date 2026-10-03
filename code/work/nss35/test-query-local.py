import argparse,hashlib,json,re,subprocess
from pathlib import Path
root=Path(__file__).resolve().parent
def unix(p):
 s=p.resolve().as_posix();return '/mnt/'+s[0].lower()+s[2:]
parser=argparse.ArgumentParser();parser.add_argument('--wsl-runtime',type=Path);args=parser.parse_args()
rt=args.wsl_runtime or root.parent/'nss9/lua-runtime/extracted/usr'
cmd=['wsl.exe','-d','Athena-Cake-Build','--exec','/usr/bin/env','LD_LIBRARY_PATH='+unix(rt/'lib/x86_64-linux-gnu'),unix(rt/'bin/lua5.1'),unix(root/'query-local-fixtures.lua'),unix(root)]
r=subprocess.run(cmd,capture_output=True,text=True,timeout=30)
cases=re.findall(r'^PASS (.*)$',r.stdout,re.M)
out={'passed':r.returncode==0,'checks':len(cases),'cases':cases,'querySha256':hashlib.sha256((root/'address-query.lua').read_bytes()).hexdigest(),'scope':'Actual address collector and recovery policy with mocked process, pipe and time APIs. Tests unsafe child states without killing any real process.','routerWrites':False,'stderr':r.stderr}
(root/'query-local-qualified.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out));raise SystemExit(r.returncode)
