"""Only decode the owned fixed-size UDP nonce/sequence; retain no other payload."""
import ipaddress,struct
def parse_ip(b,token,server,port=45818):
    if len(token)!=32 or len(b)<68 or b[0]>>4!=4:return None
    ihl=(b[0]&15)*4
    if ihl<20 or len(b)<ihl+136 or b[9]!=17:return None
    total=struct.unpack_from('!H',b,2)[0]
    if total!=ihl+136 or len(b)<total or struct.unpack_from('!H',b,6)[0]&0x3fff:return None
    sp,dp,size=struct.unpack_from('!HHH',b,ihl)
    if size!=136:return None
    src,dst=str(ipaddress.IPv4Address(bytes(b[12:16]))),str(ipaddress.IPv4Address(bytes(b[16:20])))
    direction='down' if src==server and sp==port else 'up' if dst==server and dp==port else None
    data=b[ihl+8:ihl+136]
    if direction is None or data[:32]!=token:return None
    seq=struct.unpack_from('!Q',data,32)[0]
    if seq>=10000:return None
    return seq,direction
def parse_ethernet(b,token,server,port=45818):
    if len(b)<14:return None
    kind=struct.unpack_from('!H',b,12)[0];at=14
    for _ in range(2):
        if kind not in (0x8100,0x88a8):break
        if len(b)<at+4:return None
        kind=struct.unpack_from('!H',b,at+2)[0];at+=4
    return parse_ip(b[at:],token,server,port) if kind==0x0800 else None
