"""Finite RAM-only sender over the existing authenticated SSH session."""
import os, signal, time
RATE=32_000_000/8
CREDIT=65536
BLOCK=16384
MAX_BYTES=1024*1024*1024
signal.alarm(182)
end=time.monotonic()+180
last=time.monotonic();credit=BLOCK;total=0;block=b'\0'*BLOCK
while time.monotonic()<end and total<MAX_BYTES:
    now=time.monotonic()
    credit=min(CREDIT,credit+max(0,now-last)*RATE);last=now
    if credit<BLOCK:
        time.sleep(min(.02,(BLOCK-credit)/RATE));continue
    sent=os.write(1,block)
    if sent<=0:break
    total+=sent;credit-=sent
