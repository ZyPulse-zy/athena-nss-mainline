"""One bounded owned sender; acknowledge STOP before a successor can start."""
import os,sys,time,signal,select,json
RATE=4_000_000
CREDIT=65536
BLOCK=16384
MAX_BYTES=1024*1024*1024
signal.alarm(182)
start=time.monotonic();end=start+180;last=start;credit=BLOCK;total=0
print(json.dumps({'event':'ready','rateBytesPerSecond':RATE,'creditBytes':CREDIT,'maximumSeconds':180}),file=sys.stderr,flush=True)
reason='deadline';block=b'\0'*BLOCK
while time.monotonic()<end and total<MAX_BYTES:
    if select.select([sys.stdin],[],[],0)[0]:
        command=sys.stdin.readline(32)
        if command=='':reason='controller-eof';break
        if command!='STOP\n':raise ValueError('Only exact owned STOP is accepted')
        reason='owned-stop';break
    now=time.monotonic();credit=min(CREDIT,credit+max(0,now-last)*RATE);last=now
    if credit<BLOCK:
        time.sleep(min(.02,(BLOCK-credit)/RATE));continue
    sent=os.write(1,block)
    if sent<=0:raise OSError('No write progress')
    total+=sent;credit-=sent
print(json.dumps({'event':'closed','reason':reason,'bytes':total,'seconds':time.monotonic()-start,'serverStopped':True}),file=sys.stderr,flush=True)
