"""Real local socketpair protocol tests; not router/NSS factory models."""
from pathlib import Path
import importlib.util,socket,threading,time,json
r=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('receiver',r/'receiver.py');lib=importlib.util.module_from_spec(spec);spec.loader.exec_module(lib)
token=b'A'*32;results=[]
def run(key,fragmented=False,body=b'',capacity=4096):
    a,b=socket.socketpair();a.settimeout(1);b.settimeout(1);used=0;result={}
    def reserve(n):
        nonlocal used
        assert used+n<=capacity;used+=n
    def server():
        try:result.update(lib.receive_upload(a,token,time.monotonic()+1,reserve))
        except (OSError,TimeoutError,AssertionError) as e:result['refused']=type(e).__name__
        finally:a.close()
    thread=threading.Thread(target=server);thread.start()
    if fragmented:
        for p in [key[:7],key[7:19],key[19:]]:b.sendall(p);time.sleep(.005)
    else:b.sendall(key)
    if len(key)<32:b.shutdown(socket.SHUT_WR)
    pending=b''
    try:
        line=b''
        while not line.endswith(b'\n'):
            part=b.recv(1)
            if not part:break
            line+=part
        if key==token:
            assert json.loads(line)=={'ready':True};b.sendall(body);b.shutdown(socket.SHUT_WR)
            while True:
                part=b.recv(4096)
                if not part:break
                pending+=part
    finally:b.close();thread.join(2);assert not thread.is_alive()
    return result,[json.loads(x) for x in pending.splitlines()],used
good,acks,count=run(token,True,b'Z'*1024);assert good=={'authenticated':True,'received':1024} and acks[-1]['received']==1024 and count==1024;results.append('fragmented_nonce_authorized_exact_bytes')
bad,acks,count=run(b'B'*32);assert bad=={'authenticated':False,'received':0} and not acks and count==0;results.append('wrong_nonce_no_ready_no_payload')
short,acks,count=run(token[:10]);assert short=={'authenticated':False,'received':0} and count==0;results.append('short_nonce_eof_no_ready')
limit,acks,count=run(token,False,b'Z'*2048,1024);assert limit.get('refused')=='AssertionError' and count==0;results.append('receiver_byte_ceiling_refused')
proof={'passed':True,'localSocketpairCases':results,'caseCount':len(results),'routerOrNssExecution':False,'fullFactoryModel':False};(r/'receiver-model-qualified.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print(json.dumps(proof))
