"""AF_PACKET read-only socket; kernel filter attached before reception is enabled."""
import ctypes as C,json,signal,socket,struct,sys,time
class Insn(C.Structure):_fields_=[('code',C.c_ushort),('jt',C.c_ubyte),('jf',C.c_ubyte),('k',C.c_uint)]
class Program(C.Structure):_fields_=[('length',C.c_ushort),('filter',C.POINTER(Insn))]
class Address(C.Structure):_fields_=[('family',C.c_ushort),('protocol',C.c_ushort),('ifindex',C.c_int),('hatype',C.c_ushort),('pkttype',C.c_ubyte),('halen',C.c_ubyte),('addr',C.c_ubyte*8)]
def capture(c):
    seconds=c['seconds'];assert 1<=seconds<=130
    token=bytes.fromhex(c['token']);assert len(token)==32 and c['serverAddress']=='172.93.163.251' and c['udpPort']==45818
    server=int.from_bytes(socket.inet_aton(c['serverAddress']),'big');port=c['udpPort']
    instructions=[(0x30,0,0,0),(0x15,0,11,0x45),(0x30,0,0,9),(0x15,0,9,17),(0x20,0,0,12),(0x15,2,0,server),(0x20,0,0,16),(0x15,0,5,server),(0x28,0,0,20),(0x15,2,0,port),(0x28,0,0,22),(0x15,0,1,port),(0x06,0,0,156),(0x06,0,0,0)]
    code=(Insn*len(instructions))(*(Insn(*x) for x in instructions));prog=Program(len(instructions),code)
    libc=C.CDLL(None,use_errno=True);libc.bind.argtypes=[C.c_int,C.c_void_p,C.c_uint];libc.setsockopt.argtypes=[C.c_int,C.c_int,C.c_int,C.c_void_p,C.c_uint]
    s=socket.socket(socket.AF_PACKET,socket.SOCK_DGRAM,0)
    try:
        s.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,262144)
        assert libc.setsockopt(s.fileno(),socket.SOL_SOCKET,26,C.byref(prog),C.sizeof(prog))==0,C.get_errno()
        a=Address(family=socket.AF_PACKET,protocol=socket.htons(3));assert libc.bind(s.fileno(),C.byref(a),C.sizeof(a))==0,C.get_errno()
        s.settimeout(.1);signal.alarm(seconds+2);start=time.monotonic();rows=[]
        print(json.dumps({'ready':True,'socketFilterBeforeBind':True,'seconds':seconds}),flush=True)
        while time.monotonic()-start<seconds:
            try:b,a=s.recvfrom(256)
            except socket.timeout:continue
            if len(b)!=156 or b[28:60]!=token:continue
            seq=struct.unpack_from('!Q',b,60)[0]
            if seq>=10000:raise AssertionError('Sequence ceiling exceeded')
            parsed=parse_ip(b,token,c['serverAddress'],port)
            if parsed:
                assert len(rows)<10000;rows.append([parsed[0],parsed[1],round(time.time(),6),a[0],a[2]])
        packets,drops=struct.unpack('II',s.getsockopt(263,6,8));out={'passed':drops==0,'seconds':time.monotonic()-start,'rows':rows,'socketPackets':packets,'socketDrops':drops,'socketFilterBeforeBind':True,'routerWrites':False}
        encoded=json.dumps(out,separators=(',',':'));assert len(encoded.encode())<=1048576;print(encoded,flush=True);return out
    finally:s.close()
if __name__=='__main__':capture(json.loads(sys.argv[1]))
