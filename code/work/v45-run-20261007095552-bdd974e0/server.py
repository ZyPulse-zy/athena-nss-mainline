"""Finite raw-upload endpoint; receiver.py is concatenated by the launcher."""
import json,signal,socket,sys,threading,time
c=json.loads(sys.argv[1]);assert c['mbps']==32 and c['seconds']==240
assert c['tcpPort']==45817 and c['udpPort']==45818
token=bytes.fromhex(c['token']);assert len(token)==32
signal.alarm(c['seconds']+2);deadline=time.monotonic()+c['seconds']
stats={'tcpBytes':0,'udpEchoed':0,'udpIgnored':0,'authenticatedTcpSessions':0}
def reserve(n):
    assert 0<n<=65536 and stats['tcpBytes']+n<=512*1024*1024,'Global byte ceiling exceeded'
    stats['tcpBytes']+=n
def tcp():
    listener=socket.socket();listener.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1);listener.bind(('0.0.0.0',c['tcpPort']));listener.listen(2);listener.settimeout(.5)
    try:
        while time.monotonic()<deadline:
            try:conn,peer=listener.accept()
            except socket.timeout:continue
            with conn:
                try:
                    result=receive_upload(conn,token,deadline,reserve)
                    if result['authenticated']:stats['authenticatedTcpSessions']+=1
                except (OSError,TimeoutError,AssertionError):pass
    finally:listener.close()
def udp():
    sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);sock.bind(('0.0.0.0',c['udpPort']));sock.settimeout(.2);bucket=time.monotonic();quota=100
    try:
        while time.monotonic()<deadline:
            try:data,peer=sock.recvfrom(2048)
            except socket.timeout:continue
            at=time.monotonic()
            if at-bucket>=1:bucket=at;quota=100
            if len(data)!=128 or data[:32]!=token or quota<=0:stats['udpIgnored']+=1;continue
            quota-=1;sock.sendto(data,peer);stats['udpEchoed']+=1
    finally:sock.close()
threads=[threading.Thread(target=tcp),threading.Thread(target=udp)]
for t in threads:t.start()
print('CONTROLLED_ENDPOINT_READY',flush=True)
for t in threads:t.join()
print(json.dumps(stats),flush=True)
