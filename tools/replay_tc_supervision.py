"""Replay the exact tc supervisor using deterministic child/pipe/time models."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--wsl-runtime',type=Path,required=True);p.add_argument('--wsl-distro',default='Athena-Cake-Build');a=p.parse_args()
root=Path(__file__).resolve().parents[1];source=root/'code/work/nss39';local=root/'.local/nss39-replay';local.mkdir(parents=True,exist_ok=True)
helper=(source/'tc-command.lua').read_text();code=(source/'tc-command-fixtures.lua').read_text().replace('__HELPER__',helper);file=local/'tc-command-replay.lua';file.write_text(code,encoding='utf-8',newline='\n')
def unix(p):
 s=p.resolve().as_posix();return '/mnt/'+s[0].lower()+s[2:]
rt=a.wsl_runtime.resolve();cmd=['wsl.exe','-d',a.wsl_distro,'--exec','/usr/bin/env','LD_LIBRARY_PATH='+unix(rt/'lib/x86_64-linux-gnu'),unix(rt/'bin/lua5.1')]
r=subprocess.run(cmd+[unix(file)],capture_output=True,text=True,timeout=30);cases=re.findall(r'^PASS (.*)$',r.stdout,re.M)
out={'passed':r.returncode==0 and len(cases)==16,'checks':len(cases),'cases':cases,'helperSha256':hashlib.sha256((source/'tc-command.lua').read_bytes()).hexdigest(),'routerAccess':False,'trafficGenerated':False,'productionFaultInjected':False,'error':r.stderr}
(local/'result.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');assert out['passed'],r.stdout+r.stderr;print(json.dumps(out))
