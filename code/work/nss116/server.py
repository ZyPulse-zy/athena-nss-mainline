"""Finite, nonce-authenticated TCP sender and equal-size UDP echo. No files or firewall writes."""
import json, signal, socket, sys, threading, time

c = json.loads(sys.argv[1])
assert 1 <= c['mbps'] <= 20 and 20 <= c['seconds'] <= 240
token = bytes.fromhex(c['token']); assert len(token) == 32
signal.alarm(c['seconds'] + 2)
deadline = time.monotonic() + c['seconds']
stats = {'tcpBytes': 0, 'udpEchoed': 0, 'udpIgnored': 0, 'authenticatedTcpSessions': 0}

def tcp():
    listener = socket.socket(); listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(('0.0.0.0', c['tcpPort'])); listener.listen(2); listener.settimeout(.5)
    try:
        while time.monotonic() < deadline:
            try: conn, peer = listener.accept()
            except socket.timeout: continue
            with conn:
                conn.settimeout(2); key = b''
                try:
                    while len(key) < 32:
                        part = conn.recv(32-len(key))
                        if not part: break
                        key += part
                    if key != token: continue
                    stats['authenticatedTcpSessions'] += 1
                    started = time.monotonic(); total = 0; block = b'\0' * 16384
                    while time.monotonic() < deadline and stats['tcpBytes'] < 512*1024*1024:
                        ahead = total*8/(c['mbps']*1e6)-(time.monotonic()-started)
                        if ahead > 0: time.sleep(min(ahead, .02)); continue
                        conn.sendall(block); total += len(block); stats['tcpBytes'] += len(block)
                except (OSError, TimeoutError): pass
    finally: listener.close()

def udp():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', c['udpPort'])); sock.settimeout(.2)
    bucket = time.monotonic(); quota = 100
    try:
        while time.monotonic() < deadline:
            try: data, peer = sock.recvfrom(2048)
            except socket.timeout: continue
            at = time.monotonic()
            if at-bucket >= 1: bucket = at; quota = 100
            if len(data) != 128 or data[:32] != token or quota <= 0:
                stats['udpIgnored'] += 1; continue
            quota -= 1; sock.sendto(data, peer); stats['udpEchoed'] += 1
    finally: sock.close()

threads = [threading.Thread(target=tcp), threading.Thread(target=udp)]
for thread in threads: thread.start()
print('CONTROLLED_ENDPOINT_READY', flush=True)
for thread in threads: thread.join()
print(json.dumps(stats), flush=True)
