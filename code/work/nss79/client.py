"""One held TCP download and one low-rate UDP socket, finite and fully measured."""
from pathlib import Path
import json, os, socket, struct, sys, threading, time

config_path = Path(sys.argv[1]).resolve(); c = json.loads(config_path.read_text())
assert 1 <= c['mbps'] <= 20 and 10 <= c['seconds'] <= 180 and 1 <= c['pps'] <= 50
directory = config_path.parent; token = bytes.fromhex(c['token']); assert len(token) == 32
started = time.monotonic(); deadline = started + c['seconds']; stopped = threading.Event()
stats = {'pid': os.getpid(), 'session': c['session'], 'startedAt': time.time(), 'tcpBytes': 0,
         'udpSent': 0, 'udpReceived': 0, 'udpSourcePort': c['udpSourcePort'], 'tcpSourcePort': c['tcpSourcePort'], 'tcpConnected': False, 'tcpAttempts': [], 'errors': []}
lock = threading.Lock()

def tcp():
    for candidate in range(c['tcpSourcePort'],c['tcpSourcePort']+8):
        stats['tcpSourcePort']=candidate
        try:
            with socket.socket() as sock:
                sock.settimeout(3); sock.bind((c['clientAddress'], candidate))
                sock.connect((c['serverAddress'], c['tcpPort'])); sock.sendall(token)
                stats['tcpAttempts'].append({'sourcePort':candidate,'connected':True})
                stats['tcpConnected'] = True; sock.settimeout(.5)
                while time.monotonic() < deadline and not stopped.is_set() and stats['tcpBytes'] < 450*1024*1024:
                    try: data = sock.recv(65536)
                    except socket.timeout: continue
                    if not data: break
                    with lock: stats['tcpBytes'] += len(data)
                return
        except Exception as e:
            stats['tcpAttempts'].append({'sourcePort':candidate,'connected':False,'error':str(e)})
            if stats['tcpConnected']:stats['errors'].append('TCP: '+str(e));stopped.set();return
        if time.monotonic()>=deadline or stopped.is_set():return
    stats['errors'].append('TCP: no authenticated endpoint within eight natural candidates'); stopped.set()

def udp():
    sock = None; port = None; sequence = 0; next_send = time.monotonic(); seen = set()
    try:
        with (directory/'udp-samples-private.jsonl').open('w') as output:
            while time.monotonic() < deadline and not stopped.is_set():
                control = directory/'control.json'
                if control.exists():
                    update = json.loads(control.read_text())
                    assert update['session'] == c['session']
                    if update.get('stop'): stopped.set(); break
                    desired = update.get('udpSourcePort', c['udpSourcePort'])
                else: desired = c['udpSourcePort']
                assert c['udpSourcePort'] <= desired < c['udpSourcePort']+12
                if port != desired:
                    if sock: sock.close()
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.bind((c['clientAddress'], desired)); sock.connect((c['serverAddress'], c['udpPort']))
                    sock.settimeout(.004); port = desired; stats['udpSourcePort'] = port
                now = time.monotonic()
                if now >= next_send:
                    packet = token+struct.pack('!Qd', sequence, now)+b'\0'*80
                    sock.send(packet); stats['udpSent'] += 1
                    output.write(json.dumps({'event':'sent','at':time.time(),'sequence':sequence,'sourcePort':port})+'\n')
                    sequence += 1; next_send = now + 1/c['pps']
                try:
                    data = sock.recv(2048)
                    if len(data) == 128 and data[:32] == token:
                        seq, sent_at = struct.unpack('!Qd', data[32:48])
                        if seq not in seen:
                            seen.add(seq); stats['udpReceived'] += 1
                            output.write(json.dumps({'event':'reply','at':time.time(),'sequence':seq,'sourcePort':port,'rttMs':(time.monotonic()-sent_at)*1000})+'\n')
                except (socket.timeout, ConnectionResetError): pass
                output.flush()
    except Exception as e: stats['errors'].append('UDP: '+str(e)); stopped.set()
    finally:
        if sock: sock.close()

threads = [threading.Thread(target=tcp), threading.Thread(target=udp)]
for thread in threads: thread.start()
with (directory/'load-samples-private.jsonl').open('w') as output:
    while any(t.is_alive() for t in threads):
        current = {**stats, 'at': time.time(), 'elapsed': time.monotonic()-started}
        tmp = directory/'status-private.json.new'; tmp.write_text(json.dumps(current)); os.replace(tmp, directory/'status-private.json')
        output.write(json.dumps(current)+'\n'); output.flush(); time.sleep(.25)
for thread in threads: thread.join()
stats['finishedAt'] = time.time(); stats['seconds'] = time.monotonic()-started
(directory/'result-private.json').write_text(json.dumps(stats, indent=2))
print(json.dumps({k:v for k,v in stats.items() if k!='session'}), flush=True)
