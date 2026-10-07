"""Readonly, bounded endpoint metadata capture; no listener or firewall changes."""
import ctypes, json, socket, struct, sys, time

c = json.loads(sys.argv[1])
assert c['serverAddress'] == '172.93.163.251'
assert c['tcpPort'] == 45817 and c['udpPort'] == 45818
token = bytes.fromhex(c['token'])
assert len(token) == 32

class Filter(ctypes.Structure):
    _fields_ = [('code', ctypes.c_ushort), ('jt', ctypes.c_ubyte),
                ('jf', ctypes.c_ubyte), ('k', ctypes.c_uint)]

class Program(ctypes.Structure):
    _fields_ = [('length', ctypes.c_ushort), ('filter', ctypes.POINTER(Filter))]

destination = struct.unpack('!I', socket.inet_aton(c['serverAddress']))[0]
instructions = [(0x20, 0, 0, 16), (0x15, 0, 7, destination),
                (0x30, 0, 0, 9), (0x15, 1, 0, 6), (0x15, 0, 4, 17),
                (0xb1, 0, 0, 0), (0x48, 0, 0, 2),
                (0x15, 2, 0, 45817), (0x15, 1, 0, 45818),
                (0x06, 0, 0, 0), (0x06, 0, 0, 192)]
filters = (Filter * len(instructions))(*(Filter(*x) for x in instructions))
program = Program(len(instructions), filters)
libc = ctypes.CDLL(None, use_errno=True)

with socket.socket(socket.AF_PACKET, socket.SOCK_DGRAM, socket.htons(0x0800)) as s:
    # Install a two-port / destination kernel filter before receiving any packets.
    if libc.setsockopt(s.fileno(), socket.SOL_SOCKET, 26,
                       ctypes.byref(program), ctypes.sizeof(program)) != 0:
        raise OSError(ctypes.get_errno(), 'Unable to attach bounded capture filter')
    s.settimeout(.2)
    end = time.monotonic() + 10
    rows = []
    print('OWNED_PEER_CAPTURE_READY', flush=True)
    while time.monotonic() < end and len(rows) < 64:
        try:
            data, address = s.recvfrom(192)
        except socket.timeout:
            continue
        if len(data) < 28 or data[0] >> 4 != 4:
            continue
        ihl = (data[0] & 15) * 4
        if len(data) < ihl + 8 or data[16:20] != socket.inet_aton(c['serverAddress']):
            continue
        proto = data[9]
        sport, dport = struct.unpack('!HH', data[ihl:ihl+4])
        row = {'at': time.time(), 'sourceAddress': socket.inet_ntoa(data[12:16]),
               'sourcePort': sport, 'destinationPort': dport}
        if proto == 17 and dport == 45818 and data[ihl+8:ihl+40] == token:
            row.update(protocol='udp', nonceVerified=True)
        elif proto == 6 and dport == 45817 and len(data) >= ihl+20 and data[ihl+13] & 2:
            row.update(protocol='tcp', syn=True, nonceVerified=False,
                       correlationOnly=True)
        else:
            continue
        rows.append(row)
    print(json.dumps({'rows': rows, 'readonly': True, 'firewallWrites': False,
                      'kernelFilterBeforeReceive': True,
                      'captureCeilingSeconds': 10, 'rowCeiling': 64}), flush=True)
