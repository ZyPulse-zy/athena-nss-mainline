import pathlib,struct,json
exec(pathlib.Path(__file__).with_name('packet-parser.py').read_text(encoding='utf-8'))
token=b'z'*32;server='172.93.163.251';b=bytearray(156);b[0]=0x45;b[9]=17;struct.pack_into('!H',b,2,156);b[12:16]=ipaddress.IPv4Address(server).packed;b[16:20]=ipaddress.IPv4Address('192.168.237.207').packed;struct.pack_into('!HHH',b,20,45818,59001,136);b[28:60]=token;struct.pack_into('!Q',b,60,7)
assert parse_ip(b,token,server)==(7,'down');ether=b'\0'*12+b'\x08\x00'+b;assert parse_ethernet(ether,token,server)==(7,'down')
vlan=b'\0'*12+b'\x81\x00\0\x01\x08\x00'+b;assert parse_ethernet(vlan,token,server)==(7,'down')
cases=3
for offset,value in [(0,0x65),(9,6),(2,1),(24,1),(28,0),(60,1),(6,1)]:
    x=bytearray(b);x[offset]=value;assert parse_ip(x,token,server) is None;cases+=1
assert parse_ip(b[:155],token,server) is None;assert parse_ip(b,b'y'*32,server) is None;assert parse_ethernet(b'\0'*18,token,server) is None
print(json.dumps({'passed':True,'cases':cases+3,'noSocketOpened':True}))
