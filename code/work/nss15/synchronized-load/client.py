"""Keep the discovery sockets alive through endpoint authorization and measurement."""
import json, os, select, socket, sys, threading, time
from pathlib import Path
from traffic import (CLOCK, CLOCK_NS, CLOCK_INFO, ProbeMetrics, TCP_ACK, UDP_SIZE,
                     bounded_error, decode_packet, load_config, packet, receive_exact,
                     request, save_result, transfer, watchdog, integer)

def run(c, go_path):
    assert sys.platform=='win32'
    go=Path(go_path);assert not go.exists()
    udp_seconds=integer(c.get('udpMeasurementSeconds',c['durationSeconds']),1,c['durationSeconds'],'udpMeasurementSeconds')
    started=CLOCK();hard_due=started+75;stop=watchdog(78)
    r={'scope':'held Windows LAN sockets; synthetic only','clockInfo':CLOCK_INFO,
       'udp':None,'tcp':None,'errors':[],'warmupUdpSent':0,'configurationWrites':False}
    udp=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);tcp=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    threads=[]
    try:
        udp.bind((c['clientAddress'],c['udpSourcePort']));tcp.bind((c['clientAddress'],c['tcpSourcePort']))
        udp.connect((c['serverAddress'],c['udpPort']));udp.setblocking(False)
        tcp.settimeout(60);tcp.setsockopt(socket.IPPROTO_IP,socket.IP_TOS,0);udp.setsockopt(socket.IPPROTO_IP,socket.IP_TOS,0)
        def stream():
            try:
                tcp.connect((c['serverAddress'],c['tcpPort']))
                tcp.settimeout(.2);connected=CLOCK()
                print('NSS15_TCP_CONNECTED_WAITING_GO',flush=True)
                while CLOCK()<hard_due and not go.exists():time.sleep(.01)
                if not go.exists():raise TimeoutError('TCP measurement start deadline')
                request_started=CLOCK()
                requested_duration=c.get('tcpDurationSeconds',c['durationSeconds'])
                assert isinstance(requested_duration,int) and 1<=requested_duration<=c['durationSeconds']
                tcp.sendall(request(c['token'],c['tcpMode'],c['tcpMaxBytes'],requested_duration,c['tcpTargetMbps']))
                header=receive_exact(tcp,TCP_ACK.size,min(hard_due,request_started+2));magic,size,duration,mbps=TCP_ACK.unpack(header)
                assert magic==b'NSS12OK!' and 1<=size<=c['tcpMaxBytes'] and 1<=duration<=c['durationSeconds'] and 1<=mbps<=c['tcpTargetMbps']
                r['tcp']=transfer(tcp,c['tcpMode']=='upload',size,min(hard_due,CLOCK()+duration),mbps)
                r['tcp'].update({'mode':c['tcpMode'],'requestStartedElapsedSeconds':request_started-started,'connectedElapsedSeconds':connected-started,'completedElapsedSeconds':CLOCK()-started,'reconnects':0,'sourcePort':c['tcpSourcePort']})
            except (OSError,TimeoutError,ConnectionError,AssertionError,ValueError) as exc:
                r['errors'].append(bounded_error(exc));r['tcp']={'bytes':0,'success':False,'reconnects':0}
            finally:tcp.close()
        def echo():
            seq=1000000;next_send=CLOCK();warmup_received=0
            while CLOCK()<hard_due and not go.exists():
                if CLOCK()>=next_send:
                    r['warmupUdpSent']+=int(udp.send(packet(c['token'],seq,CLOCK_NS()))==UDP_SIZE);seq+=1;next_send=CLOCK()+.25
                if select.select([udp],[],[],.02)[0]:
                    if decode_packet(udp.recv(2048),c['token']) is not None:warmup_received+=1
            if not go.exists():r['errors'].append({'type':'StartDeadline'});return
            neighbor=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            try:
                neighbor.bind((c['clientAddress'],integer(c.get('neighborSourcePort',54374),1024,65535,'neighborSourcePort')));neighbor.setsockopt(socket.IPPROTO_IP,socket.IP_TOS,0)
                for _ in range(6):neighbor.sendto(bytes(UDP_SIZE),(c['serverAddress'],c['udpPort']))
                r['neighborInvalidNoncePacketsSent']=6
            finally:neighbor.close()
            phase_ns=CLOCK_NS();phase=phase_ns/1e9;due=phase+udp_seconds;next_send=phase;metrics=ProbeMetrics();seq=attempts=0;ignored_warmup=0
            while CLOCK()<min(hard_due,due+1):
                now=CLOCK()
                if now<due and now>=next_send and attempts<c['udpMaxPackets']:
                    stamp=CLOCK_NS();n=udp.send(packet(c['token'],seq,stamp));attempts+=1
                    if n==UDP_SIZE:metrics.sent_packet(seq,stamp,(stamp-phase_ns)/1e9)
                    seq+=1;next_send+=1/c['udpPps']
                    if next_send<now:next_send=now+1/c['udpPps']
                waiting=min(.02,max(0,next_send-CLOCK())) if now<due and attempts<c['udpMaxPackets'] else .02
                if select.select([udp],[],[],waiting)[0]:
                    data=udp.recv(2048);decoded=decode_packet(data,c['token']);stamp=CLOCK_NS()
                    if decoded is not None and decoded[0]>=1000000:ignored_warmup+=1;continue
                    metrics.echo(data,c['token'],(stamp-phase_ns)/1e9,stamp)
            r['udp']=metrics.summary();r['udp'].update({'targetPps':c['udpPps'],'payloadBytes':UDP_SIZE,'sourcePort':c['udpSourcePort'],'phaseStartedElapsedSeconds':phase-started,'warmupReplies':warmup_received+ignored_warmup})
        threads=[threading.Thread(target=echo,daemon=True),threading.Thread(target=stream,daemon=True)]
        for t in threads:t.start()
        print('NSS14_HELD_SOCKETS_STARTED',flush=True)
        for t in threads:t.join(max(0,hard_due-CLOCK()))
        if any(t.is_alive() for t in threads):raise TimeoutError('Held client deadline')
        r['elapsedSeconds']=CLOCK()-started;return r
    finally:
        udp.close();tcp.close()
        if not any(t.is_alive() for t in threads):stop.cancel()

if __name__=='__main__':
    c=load_config(sys.argv[1],'client');save_result(sys.argv[3],run(c,sys.argv[2]))
