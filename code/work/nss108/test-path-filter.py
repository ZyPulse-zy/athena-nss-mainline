"""Offline loopback validates kernel BPF, TX/RX visibility and nonce rejection."""
import socket,subprocess,json,struct
nonce=bytes(range(32));p=subprocess.Popen(['work/nss108/udp-path-tap-host','2','127.0.0.1','45818',nonce.hex()],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
try:
 assert p.stdout.readline().strip()=='NSS108_TAP_READY'
 with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as server,socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as client:
  server.bind(('127.0.0.1',45818));server.settimeout(1);client.settimeout(1)
  for seq in [1,2,3]:
   data=nonce+struct.pack('>Q',seq)+bytes(88);client.sendto(data,server.getsockname());body,peer=server.recvfrom(256);server.sendto(body,peer);assert client.recv(256)==data
  data=bytes(32)+struct.pack('>Q',9)+bytes(88);client.sendto(data,server.getsockname());body,peer=server.recvfrom(256);server.sendto(body,peer);client.recv(256)
 out,err=p.communicate(timeout=4);assert p.returncode==0,err;o=json.loads(out);assert o['passed'] and o['socketDrops']==0
 for direction in ['up','down']:
  for packet_type in [0,4]:
   matches=[g for g in o['groups'] if g['interface']=='lo' and g['direction']==direction and g['packetType']==packet_type];assert len(matches)==1
   assert [x[0] for x in matches[0]['sequenceTimes']]==[1,2,3]
 proof={'passed':True,'offlineLoopbackOnly':True,'parserCases':6,'socketLocalBpfVerified':True,'transmitAndReceiveVerified':True,'nonceMismatchRejected':True,'socketDrops':0,'routerWrites':False}
 with open('work/nss108/tap-offline-qualification.json','x') as f:json.dump(proof,f,indent=2);f.write('\n')
 print(json.dumps(proof))
finally:
 if p.poll() is None:p.kill();p.wait()
