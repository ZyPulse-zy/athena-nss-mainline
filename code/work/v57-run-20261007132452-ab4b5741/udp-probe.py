"""Twenty nonce-authenticated echoes, on the already owned fixed UDP tuple."""
import json,socket,sys,time
c=json.loads(sys.argv[1]);token=bytes.fromhex(c['token']);assert len(token)==32
base=c['probeBaseSequence'];sent=0;received=set();start=time.monotonic();end=start+1.1
with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as s:
    s.bind((c['clientAddress'],c['udpSourcePort']));s.settimeout(.005)
    while time.monotonic()<end:
        if sent<20 and time.monotonic()-start>=sent*.02:
            s.sendto(token+(base+sent).to_bytes(8,'big')+b'\0'*88,(c['serverAddress'],c['udpPort']));sent+=1
        try:b,peer=s.recvfrom(2048)
        except socket.timeout:continue
        if len(b)==128 and b[:32]==token and peer==(c['serverAddress'],c['udpPort']):
            seq=int.from_bytes(b[32:40],'big')
            if base<=seq<base+20:received.add(seq)
print(json.dumps({'mode':'python-unconnected','sent':sent,'received':len(received),'nonceVerified':True}))
