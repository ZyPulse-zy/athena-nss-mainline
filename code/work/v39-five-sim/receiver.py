"""Bounded nonce authentication and TCP-upload receiver, also used offline."""
import socket,time,select,json,hmac
def authenticate_upload(conn,token,deadline):
    assert isinstance(token,bytes) and len(token)==32
    key=b''
    while len(key)<32 and time.monotonic()<deadline:
        conn.settimeout(min(2,max(.001,deadline-time.monotonic())))
        part=conn.recv(32-len(key))
        if not part:return False
        key+=part
    return len(key)==32 and hmac.compare_digest(key,token)
def receive_upload(conn,token,deadline,reserve):
    if not authenticate_upload(conn,token,min(deadline,time.monotonic()+2)):return {'authenticated':False,'received':0}
    conn.sendall(b'{"ready":true}\n');received=0;last=0
    while time.monotonic()<deadline:
        ready=select.select([conn],[],[],min(.05,max(0,deadline-time.monotonic())))[0]
        if ready:
            b=conn.recv(65536)
            if not b:break
            reserve(len(b));received+=len(b)
        now=time.monotonic()
        if now-last>=.2:
            conn.sendall((json.dumps({'received':received},separators=(',',':'))+'\n').encode());last=now
    conn.sendall((json.dumps({'received':received},separators=(',',':'))+'\n').encode())
    return {'authenticated':True,'received':received}
