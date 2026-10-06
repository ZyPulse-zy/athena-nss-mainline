"""Finite nonce-authenticated four-slot raw download; no SSH data channels."""
import hmac,json,select,signal,socket,sys,threading,time

class DownloadBudget:
    def __init__(self):
        self.lock=threading.Lock();self.active=set();self.sessions=0;self.bytes=0
    def claim(self,slot):
        with self.lock:
            assert slot in range(4) and slot not in self.active and len(self.active)<4 and self.sessions<32
            self.active.add(slot);self.sessions+=1
    def release(self,slot):
        with self.lock:self.active.discard(slot)
    def reserve(self,n):
        with self.lock:
            assert 0<n<=16384 and self.bytes+n<=1024*1024*1024
            self.bytes+=n

def send_raw_download(conn,token,deadline,budget):
    conn.settimeout(2);key=b'';slot=None;claimed=False
    try:
        auth_deadline=min(deadline,time.monotonic()+2)
        while len(key)<33 and time.monotonic()<auth_deadline:
            part=conn.recv(33-len(key))
            if not part:return False
            key+=part
        if len(key)!=33 or not hmac.compare_digest(key[:32],token) or key[32] not in range(4):return False
        slot=key[32];budget.claim(slot);claimed=True
        ready={'ready':True,'schema':'owned-four-raw-download-v1','slot':slot,'mbps':8,'creditBytes':16384,'combinedMbps':32,'combinedCreditBytes':65536}
        conn.sendall((json.dumps(ready,separators=(',',':'))+'\n').encode())
        block=b'\0'*16384;credit=16384;last=time.monotonic();command=b''
        while time.monotonic()<deadline:
            if select.select([conn],[],[],0)[0]:
                part=conn.recv(16)
                if not part:break
                command+=part
                assert len(command)<=5 and b'STOP\n'.startswith(command)
                if command==b'STOP\n':break
            now=time.monotonic();credit=min(16384,credit+max(0,now-last)*1_000_000);last=now
            if credit<16384:
                time.sleep(min(.02,(16384-credit)/1_000_000));continue
            budget.reserve(len(block));conn.sendall(block);credit-=len(block)
        return True
    finally:
        if claimed:budget.release(slot)

def main():
    c=json.loads(sys.argv[1]);assert c['mbps']==32 and c['seconds']==240 and c['tcpPort']==45817 and c['udpPort']==45818
    token=bytes.fromhex(c['token']);assert len(token)==32
    signal.alarm(242);deadline=time.monotonic()+240;budget=DownloadBudget();threads=[]
    def tcp():
        listener=socket.socket();listener.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1);listener.bind(('0.0.0.0',45817));listener.listen(8);listener.settimeout(.2);accepted=0
        def child(conn):
            with conn:
                try:send_raw_download(conn,token,deadline,budget)
                except (OSError,TimeoutError,AssertionError):pass
        try:
            while time.monotonic()<deadline and accepted<40:
                try:conn,peer=listener.accept()
                except socket.timeout:continue
                accepted+=1;t=threading.Thread(target=child,args=(conn,));threads.append(t);t.start()
        finally:listener.close()
    def udp():
        sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);sock.bind(('0.0.0.0',45818));sock.settimeout(.2);at=time.monotonic();quota=100
        try:
            while time.monotonic()<deadline:
                try:data,peer=sock.recvfrom(2048)
                except socket.timeout:continue
                now=time.monotonic()
                if now-at>=1:at=now;quota=100
                if len(data)!=128 or data[:32]!=token or quota<=0:continue
                quota-=1;sock.sendto(data,peer)
        finally:sock.close()
    owners=[threading.Thread(target=tcp),threading.Thread(target=udp)]
    for t in owners:t.start()
    print('CONTROLLED_ENDPOINT_READY',flush=True)
    for t in owners:t.join()
    for t in threads:t.join()
    print(json.dumps({'tcpBytesReserved':budget.bytes,'authenticatedSessions':budget.sessions,'activeSlots':len(budget.active)}),flush=True)

if __name__=='__main__':main()
