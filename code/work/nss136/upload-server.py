"""Owned SSH stdin receiver. No file creation or persistent server configuration."""
import os,time,select,json
end=time.monotonic()+180;total=0;last=0
while time.monotonic()<end and total<1024*1024*1024:
 ready=select.select([0],[],[],min(.05,max(0,end-time.monotonic())))[0]
 if ready:
  b=os.read(0,65536)
  if not b:break
  total+=len(b)
  if total>1024*1024*1024:raise RuntimeError('Receiver byte ceiling exceeded')
 now=time.monotonic()
 if now-last>=.2:
  os.write(1,(json.dumps({'received':total},separators=(',',':'))+'\n').encode());last=now
os.write(1,(json.dumps({'received':total},separators=(',',':'))+'\n').encode())
