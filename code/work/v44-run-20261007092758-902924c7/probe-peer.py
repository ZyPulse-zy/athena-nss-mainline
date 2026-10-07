"""Finite owned UDP discovery, no configuration changes."""
import json, socket, sys, time
c=json.loads(sys.argv[1]); token=bytes.fromhex(c['token'])
with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as s:
    s.bind((c['clientAddress'],c['udpSourcePort']))
    for n in range(30):
        s.sendto(token+b'\0'*96,(c['serverAddress'],c['udpPort']));time.sleep(.04)
print(json.dumps({'probeDatagrams':30,'configurationWrites':False}))
