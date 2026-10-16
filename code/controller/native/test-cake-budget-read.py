#!/usr/bin/env python3
"""Execute the actual decoder with synthetic netlink frames and no live socket."""
import json,os,pathlib,subprocess,tempfile
root=pathlib.Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix='cake-budget-model-') as folder:
    output=pathlib.Path(folder)/'test-budget'
    flags=['-std=c11','-O2','-Wall','-Wextra','-Werror']
    if os.getenv('ATHENA_TEST_SANITIZERS')=='1':
        flags+=['-fsanitize=address,undefined','-fno-omit-frame-pointer']
    subprocess.run([os.getenv('CC','gcc'),*flags,str(root/'test-cake-budget-read.c'),'-o',str(output)],check=True)
    result=subprocess.run([str(output)],text=True,capture_output=True,timeout=15,check=True)
    report=json.loads(result.stdout);assert report['passed'] and not report['liveSocketOpened']
    print(json.dumps(report))
