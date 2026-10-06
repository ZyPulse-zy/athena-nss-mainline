"""Finite synthetic workload primitives. Imports never open a socket."""
import hmac
import ipaddress
import json
import math
import os
import socket
import statistics
import struct
import threading
import time
from pathlib import Path

MAX_DURATION = 120
MAX_SERVER_DURATION = 180
MAX_TCP_BYTES = 4 * 1024**3
MAX_TCP_MBPS = 1000
MAX_UDP_PPS = 50
MAX_UDP_SERVER_PPS = 100
MAX_UDP_PACKETS = MAX_DURATION * MAX_UDP_PPS
CHUNK = 65536
UDP_SIZE = 128
TCP_REQUEST = struct.Struct('!8s16scQHH')
TCP_ACK = struct.Struct('!8sQHH')
CLOCK = time.perf_counter
CLOCK_NS = time.perf_counter_ns
_CLOCK_INFO = time.get_clock_info('perf_counter')
CLOCK_INFO = {'name': 'perf_counter/perf_counter_ns',
              'implementation': _CLOCK_INFO.implementation,
              'monotonic': _CLOCK_INFO.monotonic, 'adjustable': _CLOCK_INFO.adjustable,
              'resolutionSeconds': _CLOCK_INFO.resolution}
if not _CLOCK_INFO.monotonic:
    raise RuntimeError('Finite workload requires a monotonic clock')


def integer(value, low, high, field):
    if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
        raise ValueError('Invalid ' + field)
    return value


def ipv4(value, field, lan=False, bind=False):
    try:
        ip = ipaddress.IPv4Address(value)
    except (ValueError, TypeError):
        raise ValueError('Invalid ' + field) from None
    if ip.is_multicast or ip.is_reserved or ip.is_loopback or ip.is_link_local:
        raise ValueError('Invalid ' + field)
    if ip.is_unspecified and not bind:
        raise ValueError('Invalid ' + field)
    if lan and (not ip.is_private or ip.is_unspecified):
        raise ValueError('Client must bind an explicit LAN IPv4 address')
    return str(ip)


def token(value):
    if not isinstance(value, str) or len(value) != 32:
        raise ValueError('A private 16-byte token is required')
    try:
        raw = bytes.fromhex(value)
    except ValueError:
        raise ValueError('Invalid private token') from None
    if len(raw) != 16 or raw == bytes(16):
        raise ValueError('Invalid private token')
    return raw


def config(raw, role):
    if not isinstance(raw, dict):
        raise ValueError('Configuration must be an object')
    c = dict(raw)
    c['localSelfTest'] = c.get('localSelfTest', False)
    if not isinstance(c['localSelfTest'], bool):
        raise ValueError('localSelfTest must be boolean')
    c['token'] = token(c.pop('tokenHex', None))
    c['durationSeconds'] = integer(c.get('durationSeconds'), 1,
                                 MAX_SERVER_DURATION if role == 'server' else MAX_DURATION,
                                 'durationSeconds')
    c['tcpMaxBytes'] = integer(c.get('tcpMaxBytes'), 1, MAX_TCP_BYTES, 'tcpMaxBytes')
    for key in ('tcpPort', 'udpPort'):
        c[key] = integer(c.get(key), 1024, 65535, key)
    if c['tcpPort'] == c['udpPort']:
        raise ValueError('Use distinct task-local ports')
    if role == 'server':
        if c['localSelfTest']:
            if c.get('bindAddress') != '127.0.0.1' or c.get('authorizedPeers') != ['127.0.0.1']:
                raise ValueError('Local self-test must bind and authorize loopback only')
        else:
            c['bindAddress'] = ipv4(c.get('bindAddress'), 'bindAddress', bind=True)
        peers = c.get('authorizedPeers')
        if not isinstance(peers, list) or not 1 <= len(peers) <= 5:
            raise ValueError('One to five explicit authorized peer IPv4 addresses are required')
        c['authorizedPeers'] = frozenset(peers if c['localSelfTest'] else
                                       (ipv4(p, 'authorizedPeers') for p in peers))
        if len(c['authorizedPeers']) != len(peers):
            raise ValueError('Duplicate authorized peer')
        c['tcpMaxMbps'] = integer(c.get('tcpMaxMbps'), 1, MAX_TCP_MBPS, 'tcpMaxMbps')
        c['udpMaxPps'] = integer(c.get('udpMaxPps'), 1, MAX_UDP_SERVER_PPS, 'udpMaxPps')
    elif role == 'client':
        if c['localSelfTest']:
            if c.get('clientAddress') != '127.0.0.1' or c.get('serverAddress') != '127.0.0.1':
                raise ValueError('Local self-test endpoints must both be loopback')
        else:
            c['clientAddress'] = ipv4(c.get('clientAddress'), 'clientAddress', lan=True)
            c['serverAddress'] = ipv4(c.get('serverAddress'), 'serverAddress')
        for key in ('tcpSourcePort', 'udpSourcePort'):
            c[key] = integer(c.get(key), 1024, 65535, key)
        if c['tcpSourcePort'] == c['udpSourcePort']:
            raise ValueError('Use distinct source ports')
        if c.get('tcpMode') not in ('download', 'upload'):
            raise ValueError('Invalid tcpMode')
        c['tcpTargetMbps'] = integer(c.get('tcpTargetMbps'), 1, MAX_TCP_MBPS, 'tcpTargetMbps')
        c['udpPps'] = integer(c.get('udpPps'), 1, MAX_UDP_PPS, 'udpPps')
    else:
        raise ValueError('Invalid role')
    c['udpMaxPackets'] = integer(c.get('udpMaxPackets'), 1,
                                 MAX_SERVER_DURATION * MAX_UDP_SERVER_PPS if role == 'server' else MAX_UDP_PACKETS,
                                 'udpMaxPackets')
    return c


def load_config(path, role):
    return config(json.loads(Path(path).read_text(encoding='utf-8')), role)


def packet(tok, sequence, stamp):
    return tok + struct.pack('!QQ', sequence, stamp) + bytes(96)


def decode_packet(data, tok):
    if len(data) != UDP_SIZE or not hmac.compare_digest(data[:16], tok) or data[32:] != bytes(96):
        return None
    return struct.unpack('!QQ', data[16:32])


def request(tok, mode, max_bytes, duration, mbps):
    return TCP_REQUEST.pack(b'NSS12TCP', tok, b'D' if mode == 'download' else b'U', max_bytes, duration, mbps)


def decode_request(data, tok):
    if len(data) != TCP_REQUEST.size:
        return None
    magic, supplied, mode, size, duration, mbps = TCP_REQUEST.unpack(data)
    if magic != b'NSS12TCP' or not hmac.compare_digest(supplied, tok) or mode not in (b'D', b'U'):
        return None
    if not 1 <= size <= MAX_TCP_BYTES or not 1 <= duration <= MAX_DURATION or not 1 <= mbps <= MAX_TCP_MBPS:
        return None
    return ('download' if mode == b'D' else 'upload', size, duration, mbps)


def receive_exact(sock, count, deadline, clock=CLOCK):
    data = bytearray()
    while len(data) < count:
        if clock() >= deadline:
            raise TimeoutError('Finite handshake expired')
        try:
            part = sock.recv(count - len(data))
        except socket.timeout:
            continue
        if not part:
            raise ConnectionError('Incomplete handshake')
        data.extend(part)
    return bytes(data)


def pace(total, start, mbps, deadline, clock=CLOCK, sleep=time.sleep):
    due = start + total / (mbps * 1_000_000 / 8)
    while clock() < min(due, deadline):
        sleep(max(0, min(.05, min(due, deadline) - clock())))


def transfer(sock, sending, max_bytes, deadline, mbps, clock=CLOCK, sleep=time.sleep):
    """At most one chunk of memory; bytes and time are independent upper bounds."""
    total = 0
    start = clock()
    block = bytes(CHUNK) if sending else None
    end_reason = 'deadline'
    while clock() < deadline and total < max_bytes:
        amount = min(CHUNK, max_bytes - total)
        try:
            if sending:
                n = sock.send(memoryview(block)[:amount])
            else:
                n = len(sock.recv(amount))  # Discard payload; never write TCP data to disk.
        except socket.timeout:
            continue
        except OSError as exc:
            elapsed = max(0, clock() - start)
            return {'bytes': total, 'elapsedSeconds': elapsed,
                    'averageMbps': total * 8 / elapsed / 1_000_000 if elapsed else None,
                    'endReason': 'socket-error', 'error': bounded_error(exc), 'payloadSaved': False}
        if not n:
            end_reason = 'peer-closed'
            break
        total += n
        pace(total, start, mbps, deadline, clock, sleep)
    if total == max_bytes:
        end_reason = 'max-bytes'
    elapsed = max(0, clock() - start)
    return {'bytes': total, 'elapsedSeconds': elapsed,
            'averageMbps': total * 8 / elapsed / 1_000_000 if elapsed else None,
            'endReason': end_reason, 'payloadSaved': False}


class EchoAdmission:
    """Allow only the configured peers, then pin one authenticated UDP peer endpoint."""
    def __init__(self, tok, peers, max_packets, pps, deadline, start):
        self.tok, self.peers = tok, peers
        self.max_packets, self.pps, self.deadline = max_packets, pps, deadline
        self.bucket, self.quota, self.pinned = start, pps, None
        self.accepted, self.rejected = 0, 0

    def admit(self, data, peer, now):
        valid = decode_packet(data, self.tok)
        if (now >= self.deadline or peer[0] not in self.peers or valid is None or
                self.accepted >= self.max_packets or (self.pinned is not None and peer != self.pinned)):
            self.rejected += 1
            return False
        if now - self.bucket >= 1:
            self.bucket, self.quota = now, self.pps
        if self.quota <= 0:
            self.rejected += 1
            return False
        self.pinned = peer
        self.quota -= 1
        self.accepted += 1
        return True


class ProbeMetrics:
    def __init__(self):
        self.sent, self.received = {}, {}
        self.duplicates = self.invalid = self.reordered = 0
        self.last_arrival_seq = -1

    def sent_packet(self, seq, stamp, elapsed):
        self.sent[seq] = (stamp, elapsed)

    def echo(self, data, tok, elapsed, received_stamp_ns=None):
        decoded = decode_packet(data, tok)
        if decoded is None:
            self.invalid += 1
            return
        seq, stamp = decoded
        expected = self.sent.get(seq)
        if (expected is None or stamp != expected[0] or elapsed < expected[1] or
                (received_stamp_ns is not None and received_stamp_ns < stamp)):
            self.invalid += 1
            return
        if seq in self.received:
            self.duplicates += 1
            return
        if seq < self.last_arrival_seq:
            self.reordered += 1
        self.last_arrival_seq = max(seq, self.last_arrival_seq)
        rtt_ms = ((received_stamp_ns - stamp) / 1_000_000 if received_stamp_ns is not None
                  else (elapsed - expected[1]) * 1000)
        self.received[seq] = {'seq': seq, 'elapsedSeconds': elapsed, 'rttMs': rtt_ms}

    def summary(self):
        # Jitter estimate uses reception order, including any reordered valid echoes.
        rows = sorted(self.received.values(), key=lambda row: row['elapsedSeconds'])
        rtts = sorted(row['rttMs'] for row in rows)
        def percentile(p):
            return rtts[min(len(rtts) - 1, math.ceil(p * len(rtts)) - 1)] if rtts else None
        jitter = 0.0 if len(rows) >= 2 else None
        for previous, current in zip(rows, rows[1:]):
            jitter += (abs(current['rttMs'] - previous['rttMs']) - jitter) / 16
        missing = sorted(set(self.sent) - set(self.received))
        return {'sent': len(self.sent), 'received': len(rows), 'missingWithinDrain': len(missing),
                'probeLossPercent': 100 * len(missing) / len(self.sent) if self.sent else None,
                'rttMedianMs': statistics.median(rtts) if rtts else None,
                'rttP95Ms': percentile(.95), 'rttP99Ms': percentile(.99),
                'rttMaxMs': max(rtts) if rtts else None,
                'rttVariationEwmaMs': jitter, 'duplicates': self.duplicates,
                'reordered': self.reordered, 'invalid': self.invalid,
                'samples': rows, 'missingSequences': missing,
                'note': 'Synthetic echo RTT and RTT variation; no one-way IPDV or CS2 loss claim.'}


def watchdog(seconds):
    """Process hard stop also works on Windows; external controller still owns rollback."""
    t = threading.Timer(seconds, lambda: os._exit(124))
    t.daemon = True
    t.start()
    return t


def save_result(path, value):
    p = Path(path)
    if p.exists() or p.with_suffix(p.suffix + '.new').exists():
        raise ValueError('Refusing to overwrite result or staging evidence')
    staging = p.with_suffix(p.suffix + '.new')
    with staging.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, indent=2)
        f.write('\n')
    # Publish without replacing an unknown existing result, even if it appeared meanwhile.
    os.link(staging, p)
    staging.unlink()


def bounded_error(exc):
    # Do not emit an exception string which might contain private endpoint/config data.
    return {'type': type(exc).__name__, 'errno': getattr(exc, 'errno', None)}
