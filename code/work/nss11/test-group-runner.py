import subprocess,time,json,os,pathlib,tempfile,signal,hashlib
root=pathlib.Path(__file__).parent
runner=str(root/'group-runner-host')
results=[]
def test(name,args,expect,signal_after=None,pidfile=None):
    begin=time.monotonic();p=subprocess.Popen([runner,*args],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    if signal_after is not None:
        time.sleep(signal_after);p.send_signal(signal.SIGTERM)
    out,err=p.communicate(timeout=8)
    elapsed=time.monotonic()-begin
    gone=[]
    if pidfile:
        for v in pathlib.Path(pidfile).read_text().split():
            gone.append(not pathlib.Path('/proc/'+v).exists())
    ok=p.returncode==expect and elapsed<7 and all(gone)
    results.append(dict(name=name,code=p.returncode,expect=expect,elapsed=round(elapsed,3),descendantsGone=gone,ok=ok,stdout=out,stderr=err))
    assert ok,results[-1]
with tempfile.TemporaryDirectory(prefix='nss11-runner-') as d:
    test('exit-zero',['1','/bin/sh','-c','exit 0'],0)
    test('exit-nonzero',['1','/bin/sh','-c','exit 7'],7)
    test('invalid-bound',['7','/bin/true'],2)
    file=d+'/timed.pid'
    test('timeout-reaps-child',['1','/bin/sh','-c',f'echo $$ > {file}; sleep 30 & echo $! >> {file}; wait'],124,pidfile=file)
    file=d+'/stray.pid'
    test('normal-exit-reaps-background',['2','/bin/sh','-c',f'sleep 30 & echo $! > {file}; exit 0'],0,pidfile=file)
    file=d+'/term.pid'
    test('term-cancels-before-outer-kill',['6','/bin/sh','-c',f'echo $$ > {file}; sleep 30 & echo $! >> {file}; wait'],143,signal_after=.4,pidfile=file)
    file=d+'/ignore.pid'
    test('term-ignoring-descendant',['1','/bin/sh','-c',f'trap "" TERM; echo $$ > {file}; sleep 30 & echo $! >> {file}; wait'],124,pidfile=file)
payload=dict(allPassed=True,tests=results,sha256={n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in ['group-runner.c','group-runner-host','group-runner-aarch64']})
(root/'group-runner-test.json').write_text(json.dumps(payload,indent=2)+'\n')
print(json.dumps(payload))
