"""Bounded natural-WAN selection, wrapping the unchanged synchronized client."""
import errno,importlib.util,json,select,socket,sys,time,types
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'nss15/synchronized-load'))
from traffic import CLOCK,load_config,save_result
spec=importlib.util.spec_from_file_location('nss16_synchronized_client',HERE.parent/'nss15/synchronized-load/client.py')
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)

def install(c,choice_path,phase_seconds=32):
    ports=c.get('tcpCandidatePorts');assert isinstance(ports,list) and 1<=len(ports)<=8
    assert len(set(ports))==len(ports)and all(type(p)is int and 1024<=p<=65535 and p!=c['udpSourcePort']for p in ports)
    owner=c.get('choiceOwner');assert isinstance(owner,str)and len(owner)==32 and all(x in'0123456789abcdef'for x in owner)
    choice=Path(choice_path);assert not choice.exists();real=socket.socket;deadline=CLOCK()+phase_seconds
    audit={'candidatePorts':[],'rejectedSocketsClosed':0,'selectedSourcePort':None,'selectedSocketNoReconnect':False}
    class ProbeSocket:
        def __init__(self):self.address=None;self.timeout=None;self.options=[];self.sock=None;self.closed=False
        def bind(self,address):assert self.address is None;self.address=address
        def settimeout(self,value):self.timeout=value;self.sock and self.sock.settimeout(value)
        def setsockopt(self,*args):self.options.append(args);self.sock and self.sock.setsockopt(*args)
        def connect(self,target):
            assert self.address and self.sock is None
            if c.get('tcpStartPath'):
                start=Path(c['tcpStartPath']);print('NSS16_TCP_WAITING_ENDPOINT_READY',flush=True)
                while CLOCK()<deadline and not start.exists():time.sleep(.01)
                assert start.exists()and start.read_text()==owner+'\n','Endpoint readiness deadline/owner'
            for index,port in enumerate(ports,1):
                s=real(socket.AF_INET,socket.SOCK_STREAM);self.sock=s;s.bind((self.address[0],port))
                for args in self.options:s.setsockopt(*args)
                s.setblocking(False);result=s.connect_ex(target);assert result in(0,errno.EINPROGRESS,errno.EWOULDBLOCK,errno.EALREADY,10035,10036,10037)
                audit['candidatePorts'].append(port);print('NSS16_TCP_CANDIDATE '+json.dumps({'index':index,'sourcePort':port}),flush=True)
                action=None;candidate_choice=choice.with_name(choice.name+'.'+str(index))
                while CLOCK()<deadline:
                    if candidate_choice.exists():
                        body=candidate_choice.read_bytes();assert len(body)<=2048;v=json.loads(body)
                        assert v['owner']==owner and v['action']in('accept','continue')
                        assert v['index']==index and v['sourcePort']==port,'Candidate decision identity changed';action=v['action'];break
                    time.sleep(.01)
                if action!='accept':
                    s.close();self.sock=None;audit['rejectedSocketsClosed']+=1
                    if action is None:raise TimeoutError('Finite candidate selection deadline')
                    continue
                audit['selectedSourcePort']=port;c['tcpSourcePort']=port
                print('NSS16_TCP_SELECTED '+json.dumps({'index':index,'sourcePort':port}),flush=True)
                connected_start=CLOCK();next_log=connected_start+5
                while CLOCK()<deadline+22:
                    if select.select([], [s], [s], .05)[1:]==([],[]):
                        if CLOCK()>=next_log:print('NSS16_TCP_CONNECT_PENDING '+json.dumps({'sourcePort':port,'waitedSeconds':CLOCK()-connected_start}),flush=True);next_log=CLOCK()+5
                        continue
                    error=s.getsockopt(socket.SOL_SOCKET,socket.SO_ERROR)
                    if error:print('NSS16_TCP_CONNECT_ERROR '+json.dumps({'sourcePort':port,'errno':error}),flush=True);raise OSError(error,'Selected TCP connection failed')
                    s.settimeout(self.timeout);audit['selectedSocketNoReconnect']=True;return
                raise TimeoutError('Held selected TCP deadline')
            raise TimeoutError('No natural same-WAN candidate within bound')
        def sendall(self,*args):return self.sock.sendall(*args)
        def recv(self,*args):return self.sock.recv(*args)
        def send(self,*args):return self.sock.send(*args)
        def close(self):
            if self.sock:self.sock.close();self.sock=None
            self.closed=True
    def factory(family=socket.AF_INET,type=socket.SOCK_STREAM,*args,**kwargs):
        return ProbeSocket()if family==socket.AF_INET and type==socket.SOCK_STREAM and not args and not kwargs else real(family,type,*args,**kwargs)
    namespace=types.SimpleNamespace(**{name:getattr(socket,name)for name in dir(socket)});namespace.socket=factory;base.socket=namespace
    return audit

def run(c,choice,go):
    audit=install(c,choice);r=base.run(c,go);r['selection']=audit;return r

if __name__=='__main__':
    c=load_config(sys.argv[1],'client');save_result(sys.argv[4],run(c,sys.argv[2],sys.argv[3]))
