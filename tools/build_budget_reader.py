#!/usr/bin/env python3
"""Build only the read-only userspace CAKE snapshot helper; never connect/deploy."""
import argparse,hashlib,json,pathlib,subprocess
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--cc',required=True);p.add_argument('--output',type=pathlib.Path,required=True)
a=p.parse_args();root=pathlib.Path(__file__).resolve().parents[1]
source=root/'code/controller/native/cake_budget_read.c';a.output.parent.mkdir(parents=True,exist_ok=True)
subprocess.run([a.cc,'-std=c11','-O2','-Wall','-Wextra','-Werror','-D_FORTIFY_SOURCE=2','-fstack-protector-strong',str(source),'-Wl,-z,relro,-z,now','-o',str(a.output)],check=True)
data=a.output.read_bytes();assert data[:4]==b'\x7fELF'
print(json.dumps({'built':True,'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'binarySha256':hashlib.sha256(data).hexdigest(),'elfMachine':int.from_bytes(data[18:20],'little'),'deployed':False}))
