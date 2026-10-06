"""Exercise the actual sender with local socket pairs, never production endpoints."""
from pathlib import Path
import importlib.util,json,socket,threading,time
r=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('raw_sender',r/'raw-server.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
token=b'm'*32;budget=m.DownloadBudget();checks=0;errors=[]
def start(key,slot):
    a,b=socket.socketpair();b.settimeout(2)
    def serve():
        with a:
            try:m.send_raw_download(a,token,time.monotonic()+2,budget)
            except AssertionError:errors.append('rejected')
    t=threading.Thread(target=serve);t.start();b.sendall(key+bytes([slot]));return b,t
clients=[]
for i in range(4):
    b,t=start(token,i);buf=b''
    while b'\n' not in buf:buf+=b.recv(4096)
    at=buf.index(b'\n');v=json.loads(buf[:at]);assert v['ready'] and v['slot']==i and v['creditBytes']==16384 and v['combinedCreditBytes']==65536;checks+=1
    clients.append((b,t))
assert budget.active=={0,1,2,3} and budget.sessions==4;checks+=1
bad,t=start(b'x'*32,0);assert bad.recv(1)==b'';bad.close();t.join();assert budget.sessions==4;checks+=1
dup,t=start(token,0);assert dup.recv(1)==b'';dup.close();t.join();assert errors==['rejected'] and budget.sessions==4;checks+=1
for b,t in clients:
    b.sendall(b'STOP\n')
    while b.recv(65536):pass
    b.close();t.join()
assert not budget.active;checks+=1
b,t=start(token,0);buf=b''
while b'\n' not in buf:buf+=b.recv(4096)
assert json.loads(buf.split(b'\n',1)[0])['slot']==0 and budget.sessions==5;checks+=1
b.sendall(b'STOP\n')
while b.recv(65536):pass
b.close();t.join();assert not budget.active and budget.bytes<1024*1024*1024;checks+=1
print(json.dumps({'passed':True,'checks':checks,'actualSenderLocalSocketsExercised':True,'fourConcurrentSlots':True,'nonceAndDuplicateRefusal':True,'oldSlotReleasedBeforeReuse':True,'productionWrites':False,'routerTraffic':False}))
