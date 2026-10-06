"""Read only, bounded capture of authenticated test datagrams at our endpoint."""
import json, socket, struct, sys, time
token = bytes.fromhex(sys.argv[1]); assert len(token) == 32
s = socket.socket(socket.AF_PACKET, socket.SOCK_DGRAM, socket.htons(0x0800))
s.settimeout(.2); end = time.monotonic()+5; rows=[]
print('NSS85_PASSIVE_READY', flush=True)
while time.monotonic()<end:
    try: data, address=s.recvfrom(2048)
    except socket.timeout: continue
    if len(data)<28 or data[0]>>4!=4 or data[9]!=17: continue
    ihl=(data[0]&15)*4
    if len(data)<ihl+8+32 or struct.unpack('!H',data[ihl+2:ihl+4])[0]!=45818: continue
    if data[ihl+8:ihl+40]!=token: continue
    rows.append({'sourceAddress':socket.inet_ntoa(data[12:16]),'sourcePort':struct.unpack('!H',data[ihl:ihl+2])[0], 'destinationAddress':socket.inet_ntoa(data[16:20]), 'nonceVerified':True})
    if len(rows)>=16: break
print(json.dumps({'authenticatedRows':rows, 'firewallWrites':False}), flush=True)
