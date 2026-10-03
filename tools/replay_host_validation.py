"""Replay NSS42 WAN validation and diagnostics without private state or router IO."""
import argparse, ast, hashlib, json, re, shutil, subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--node',type=Path,required=True);p.add_argument('--wsl-runtime',type=Path,required=True);p.add_argument('--wsl-distro',default='Athena-Cake-Build');a=p.parse_args()
root=Path(__file__).resolve().parents[1];source=root/'code/work/nss42';local=root/'.local/nss42-replay';local.mkdir(parents=True,exist_ok=True)
for relative in ['work/nss42/parse-ecm-any-wan.mjs','work/nss12/forward-tag-trial/model.mjs']:
    dest=local/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/'code'/relative,dest)
test=(source/'test-parser.mjs').read_text(encoding='utf-8')
start=test.index('function selection(wan)');end=test.index('const out={passed:true,checks:cases.length')
body=test[start:end];assert 'record.' not in body and 'readFileSync' not in body
runner=local/'work/nss42/runner.mjs';runner.write_text("import assert from 'node:assert/strict';import {validateAcceleratedState} from './parse-ecm-any-wan.mjs';const cases=[];\n"+body+"\nassert.equal(cases.length,42);console.log(JSON.stringify({passed:true,checks:cases.length,actualHardwareStateRead:false,routerAccess:false}));\n",encoding='utf-8',newline='\n')
r=subprocess.run([str(a.node.resolve()),str(runner.resolve())],cwd=local,capture_output=True,text=True,timeout=30);assert r.returncode==0,r.stderr
wan=json.loads(r.stdout);assert wan['passed'] and wan['checks']==42
tree=ast.parse((source/'test-publication-wait.py').read_text(encoding='utf-8'))
values=[ast.literal_eval(node.value) for node in tree.body if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='fixtures' for t in node.targets)]
assert len(values)==1 and isinstance(values[0],str)
lua=local/'publication-diagnostics.lua';lua.write_text(values[0].replace('__SOURCE__',(source/'publication-wait.lua').read_text(encoding='utf-8')),encoding='utf-8',newline='\n')
def unix(path):
    s=path.resolve().as_posix();return '/mnt/'+s[0].lower()+s[2:]
rt=a.wsl_runtime.resolve();cmd=['wsl.exe','-d',a.wsl_distro,'--exec','/usr/bin/env','LD_LIBRARY_PATH='+unix(rt/'lib/x86_64-linux-gnu'),unix(rt/'bin/lua5.1'),unix(lua)]
r=subprocess.run(cmd,capture_output=True,text=True,timeout=30);cases=re.findall(r'^PASS (.*)$',r.stdout,re.M);assert r.returncode==0 and len(cases)==23,r.stdout+r.stderr
out={'passed':True,'wanChecks':42,'diagnosticChecks':23,'checks':65,'scope':'Re-execution of existing synthetic NSS42 cases; not 65 additional distinct cases. The one frozen actual-state replay is deliberately omitted.','routerAccess':False,'privateHardwareStateRead':False,'trafficGenerated':False,'parserSha256':hashlib.sha256((source/'parse-ecm-any-wan.mjs').read_bytes()).hexdigest(),'plannerSha256':hashlib.sha256((source/'publication-wait.lua').read_bytes()).hexdigest()}
(local/'result.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out))
