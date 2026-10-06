"""Private finite TCP source/sink and UDP echo. No service or firewall setup."""
import argparse
import json
import socket
import threading
import time
from traffic import (CLOCK, CLOCK_INFO, EchoAdmission, TCP_ACK, TCP_REQUEST, UDP_SIZE, bounded_error,
                     decode_packet, decode_request, load_config, receive_exact, save_result, transfer, watchdog)


def run(c):
    started = CLOCK()
    deadline = started + c['durationSeconds']
    hard_stop = watchdog(c['durationSeconds'] + 3)
    results = {'scope': 'local-self-test' if c['localSelfTest'] else 'synthetic external endpoint only',
               'localSelfTest': c['localSelfTest'], 'clockInfo': CLOCK_INFO,
               'tcp': None, 'udp': None, 'errors': []}
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    threads = []
    try:
        udp.bind((c['bindAddress'], c['udpPort']))
        tcp.bind((c['bindAddress'], c['tcpPort']))
        udp.settimeout(.2)
        tcp.settimeout(.2)
        udp.setsockopt(socket.IPPROTO_IP, socket.IP_TOS, 0)
        tcp.setsockopt(socket.IPPROTO_IP, socket.IP_TOS, 0)
        tcp.listen(2)
        admission = EchoAdmission(c['token'], c['authorizedPeers'], c['udpMaxPackets'],
                                  c['udpMaxPps'], deadline, started)

        def echo():
            wire_bytes, echoed, trace_count = 0, 0, 0
            try:
                while CLOCK() < deadline and admission.accepted < c['udpMaxPackets']:
                    try:
                        data, peer = udp.recvfrom(2048)
                    except socket.timeout:
                        continue
                    accepted = admission.admit(data, peer, CLOCK())
                    if c.get('traceUdp', False) and trace_count < 6:
                        trace_count += 1
                        print('NSS16_UDP_DIAGNOSTIC ' + json.dumps({'peerAddress': peer[0], 'peerPort': peer[1], 'nonceValid': decode_packet(data, c['token']) is not None, 'peerAuthorized': peer[0] in c['authorizedPeers'], 'admitted': accepted, 'serverElapsedSeconds': CLOCK()-started}), flush=True)
                    if accepted:
                        udp.sendto(data, peer)
                        echoed += 1
                        wire_bytes += len(data)
            except OSError as exc:
                results['errors'].append(bounded_error(exc))
            results['udp'] = {'echoed': echoed, 'rejected': admission.rejected,
                              'payloadBytesEachDirection': wire_bytes,
                              'payloadByteCeilingEachDirection': c['udpMaxPackets'] * UDP_SIZE,
                              'peerPinned': admission.pinned is not None,
                              'authenticatedPeerAddress': admission.pinned[0] if admission.pinned else None,
                              'authenticatedPeerPort': admission.pinned[1] if admission.pinned else None}

        def stream():
            rejected = 0
            while CLOCK() < deadline and rejected < 32:
                try:
                    conn, peer = tcp.accept()
                except socket.timeout:
                    continue
                try:
                    conn.settimeout(.2)
                    if peer[0] not in c['authorizedPeers']:
                        rejected += 1
                        continue
                    # Same socket may wait for controller GO; authorization and nonce still apply.
                    # The server's independent absolute deadline bounds this wait.
                    header = receive_exact(conn, TCP_REQUEST.size, deadline)
                    decoded = decode_request(header, c['token'])
                    if decoded is None:
                        rejected += 1
                        continue
                    mode, wanted_bytes, wanted_duration, wanted_mbps = decoded
                    size = min(wanted_bytes, c['tcpMaxBytes'])
                    mbps = min(wanted_mbps, c['tcpMaxMbps'])
                    duration = min(wanted_duration, max(0, int(deadline - CLOCK())))
                    if duration < 1:
                        break
                    conn.sendall(TCP_ACK.pack(b'NSS12OK!', size, duration, mbps))
                    active_deadline = min(deadline, CLOCK() + duration)
                    results['tcp'] = transfer(conn, mode == 'download', size, active_deadline,
                                              mbps)
                    results['tcp'].update({'mode': mode, 'authenticatedSessions': 1, 'authenticatedPeerAddress': peer[0], 'authenticatedPeerPort': peer[1],
                                           'rejectedConnections': rejected, 'maxBytes': size,
                                           'negotiatedMbps': mbps})
                    return  # Exactly one authenticated TCP session; never restart it.
                except (OSError, TimeoutError, ConnectionError) as exc:
                    results['errors'].append(bounded_error(exc))
                    rejected += 1
                finally:
                    conn.close()
            if results['tcp'] is None:
                results['tcp'] = {'authenticatedSessions': 0, 'rejectedConnections': rejected,
                                  'bytes': 0, 'payloadSaved': False}

        threads = [threading.Thread(target=echo, daemon=True), threading.Thread(target=stream, daemon=True)]
        for worker in threads:
            worker.start()
        print('NSS12_SYNTHETIC_READY', flush=True)
        for worker in threads:
            worker.join(max(0, deadline + .5 - CLOCK()))
        if any(worker.is_alive() for worker in threads):
            raise TimeoutError('Worker failed finite exit')
        results.update({'durationCeilingSeconds': c['durationSeconds'],
                        'elapsedSeconds': CLOCK() - started,
                        'udpPayloadSize': UDP_SIZE, 'hardStopSeconds': c['durationSeconds'] + 3,
                        'productionChanges': False})
        return results
    finally:
        udp.close()
        tcp.close()
        if not any(worker.is_alive() for worker in threads):
            hard_stop.cancel()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('config')
    parser.add_argument('output')
    parser.add_argument('--local-self-test', action='store_true')
    args = parser.parse_args()
    try:
        c = load_config(args.config, 'server')
        if c['localSelfTest'] != args.local_self_test:
            raise ValueError('Explicit local-self-test flag and config must agree')
        result = run(c)
        save_result(args.output, result)
        print(json.dumps({k: v for k, v in result.items() if k != 'samples'}))
    except Exception as exc:
        print(json.dumps({'success': False, 'error': bounded_error(exc)}))
        raise SystemExit(1)
