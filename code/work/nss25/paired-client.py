"""Read-only natural WAN selection. Keep the selected UDP socket throughout."""
import importlib.util,json,socket,sys,time,types
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('nss20_qualified_paired',HERE.parent/'nss16/paired-client.py')
paired=importlib.util.module_from_spec(spec);spec.loader.exec_module(paired)
from traffic import CLOCK,CLOCK_NS,packet,load_config,save_result,watchdog

def select_udp(c,choice_path):
    ports=c['udpCandidatePorts'];assert isinstance(ports,list)and 1<=len(ports)<=8 and len(set(ports))==len(ports)
    assert all(type(p)is int and 1024<=p<=65535 and p not in c['tcpCandidatePorts']and p!=c['neighborSourcePort']for p in ports)
    owner=c['choiceOwner'];assert len(owner)==32 and all(x in'0123456789abcdef'for x in owner)
    choice=Path(choice_path);assert not choice.exists();sockets=[];selected=None;start=CLOCK();due=start+25;stop=watchdog(28)
    audit={'candidatePorts':ports,'packetsSent':0,'selectedSocketNoRebind':False,'rejectedSocketsClosed':0}
    try:
        for p in ports:
            s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);s.bind((c['clientAddress'],p));sockets.append(s)
        print('NSS20_UDP_CANDIDATES_STARTED',flush=True);next_send=CLOCK();seq=2000000
        while CLOCK()<due:
            if choice.exists():
                data=choice.read_bytes();assert len(data)<=2048;v=json.loads(data)
                assert v['owner']==owner and v['sourcePort']in ports and v['action']=='accept','UDP choice ownership or scope changed'
                selected=sockets[ports.index(v['sourcePort'])];c['udpSourcePort']=v['sourcePort'];audit['selectedSourcePort']=v['sourcePort'];audit['selectedSocketNoRebind']=True;return selected,audit
            if CLOCK()>=next_send:
                for s in sockets:s.sendto(packet(c['token'],seq,CLOCK_NS()),(c['serverAddress'],c['udpPort']));seq+=1;audit['packetsSent']+=1
                next_send=CLOCK()+.5
            time.sleep(.01)
        raise TimeoutError('Finite natural UDP selection deadline')
    finally:
        for s in sockets:
            if s is not selected:s.close();audit['rejectedSocketsClosed']+=1
        stop.cancel()

def run(c,choice,go):
    held,audit=select_udp(c,Path(choice).with_name(Path(choice).name+'-udp'))
    selection=paired.install(c,choice);real_factory=paired.base.socket.socket;given=False
    class HeldUdp:
        def bind(self,address):assert held.getsockname()==address,'Selected UDP rebound'
        def connect(self,target):assert target==(c['serverAddress'],c['udpPort']);held.connect(target)
        def __getattr__(self,key):return getattr(held,key)
    def factory(family=socket.AF_INET,type=socket.SOCK_STREAM,*args,**kwargs):
        nonlocal given
        if family==socket.AF_INET and type==socket.SOCK_DGRAM and not args and not kwargs and not given:given=True;return HeldUdp()
        return real_factory(family,type,*args,**kwargs)
    namespace=types.SimpleNamespace(**{name:getattr(socket,name)for name in dir(socket)});namespace.socket=factory;paired.base.socket=namespace
    try:r=paired.base.run(c,go);r['selection']=selection;r['udpSelection']=audit;return r
    finally:held.close()

if __name__=='__main__':
    c=load_config(sys.argv[1],'client');save_result(sys.argv[4],run(c,sys.argv[2],sys.argv[3]))
