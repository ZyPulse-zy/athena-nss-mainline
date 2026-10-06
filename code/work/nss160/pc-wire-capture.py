"""Existing Npcap, one non-promiscuous adapter, socket-local filter, finite read."""
import ctypes as C,json,os,pathlib,sys,time
exec(pathlib.Path(__file__).with_name('packet-parser.py').read_text(encoding='utf-8'))
class Timeval(C.Structure):_fields_=[('sec',C.c_long),('usec',C.c_long)]
class Header(C.Structure):_fields_=[('ts',Timeval),('caplen',C.c_uint32),('length',C.c_uint32)]
class Filter(C.Structure):_fields_=[('length',C.c_uint),('insns',C.c_void_p)]
class Stats(C.Structure):_fields_=[(n,C.c_uint) for n in ('recv','drop','ifdrop','capt','sent','netdrop')]
def capture(c):
    assert os.name=='nt' and C.sizeof(Header)==16
    seconds=c['seconds'];assert 1<=seconds<=130
    token=bytes.fromhex(c['token']);assert len(token)==32 and c['serverAddress']=='172.93.163.251' and c['udpPort']==45818
    device=c['device'];assert device.startswith('\\Device\\NPF_{') and device.endswith('}')
    dll=pathlib.Path('C:/Windows/System32/Npcap/wpcap.dll');assert dll.is_file()
    os.add_dll_directory(str(dll.parent));lib=C.CDLL(str(dll))
    signatures={'pcap_create':(C.c_void_p,[C.c_char_p,C.c_char_p]),'pcap_set_snaplen':(C.c_int,[C.c_void_p,C.c_int]),'pcap_set_promisc':(C.c_int,[C.c_void_p,C.c_int]),'pcap_set_timeout':(C.c_int,[C.c_void_p,C.c_int]),'pcap_set_buffer_size':(C.c_int,[C.c_void_p,C.c_int]),'pcap_activate':(C.c_int,[C.c_void_p]),'pcap_datalink':(C.c_int,[C.c_void_p]),'pcap_compile':(C.c_int,[C.c_void_p,C.POINTER(Filter),C.c_char_p,C.c_int,C.c_uint]),'pcap_setfilter':(C.c_int,[C.c_void_p,C.POINTER(Filter)]),'pcap_freecode':(None,[C.POINTER(Filter)]),'pcap_setnonblock':(C.c_int,[C.c_void_p,C.c_int,C.c_char_p]),'pcap_next_ex':(C.c_int,[C.c_void_p,C.POINTER(C.POINTER(Header)),C.POINTER(C.POINTER(C.c_ubyte))]),'pcap_stats':(C.c_int,[C.c_void_p,C.POINTER(Stats)]),'pcap_geterr':(C.c_char_p,[C.c_void_p]),'pcap_close':(None,[C.c_void_p])}
    for n,(restype,args) in signatures.items():getattr(lib,n).restype=restype;getattr(lib,n).argtypes=args
    err=C.create_string_buffer(256);h=lib.pcap_create(device.encode('ascii'),err);assert h,err.value.decode(errors='replace')
    rows=[];started=time.time();mon=time.monotonic()
    try:
        for name,value in [('pcap_set_snaplen',256),('pcap_set_promisc',0),('pcap_set_timeout',20),('pcap_set_buffer_size',1048576)]:assert getattr(lib,name)(h,value)==0
        assert lib.pcap_activate(h)==0,lib.pcap_geterr(h).decode(errors='replace')
        assert lib.pcap_datalink(h)==1,'Unsupported datalink'
        f=Filter();expression=b'ip and udp and host 172.93.163.251 and port 45818'
        assert lib.pcap_compile(h,C.byref(f),expression,1,0xffffffff)==0
        try:assert lib.pcap_setfilter(h,C.byref(f))==0
        finally:lib.pcap_freecode(C.byref(f))
        assert lib.pcap_setnonblock(h,1,err)==0
        print(json.dumps({'ready':True,'pid':os.getpid(),'startedAt':started,'nonPromiscuous':True,'socketLocalFilter':True,'independentInProcessDeadlineSeconds':seconds}),flush=True)
        ph=C.POINTER(Header)();pb=C.POINTER(C.c_ubyte)()
        while time.monotonic()-mon<seconds:
            code=lib.pcap_next_ex(h,C.byref(ph),C.byref(pb))
            if code==0:time.sleep(.002);continue
            assert code==1,lib.pcap_geterr(h).decode(errors='replace')
            header=ph.contents;assert header.caplen<=256 and 0<=header.ts.usec<1000000
            parsed=parse_ethernet(C.string_at(pb,header.caplen),token,c['serverAddress'],c['udpPort'])
            if parsed:
                assert len(rows)<10000
                rows.append([parsed[0],parsed[1],round(header.ts.sec+header.ts.usec/1000000,6)])
        stats=Stats();assert lib.pcap_stats(h,C.byref(stats))==0
        out={'passed':stats.drop==stats.ifdrop==0,'rows':rows,'seconds':time.monotonic()-mon,'pcapReceived':stats.recv,'pcapDropped':stats.drop,'interfaceDropped':stats.ifdrop,'filterApplied':True,'nonPromiscuous':True,'driverChanged':False,'startedAt':started,'finishedAt':time.time(),'probeIsNotPhysicalWireProof':True}
        encoded=json.dumps(out,separators=(',',':'));assert len(encoded.encode())<=1048576
        print(encoded,flush=True);return out
    finally:lib.pcap_close(h)
if __name__=='__main__':capture(json.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8')))
