"""Read-only router localization with one naturally matched owned TCP/UDP pair."""
from pathlib import Path
import json,hashlib
r=Path('work/nss93');r.mkdir(exist_ok=True)
names=['start-dallas.mjs','ssh-client.mjs','server.py','discover-peer.py','probe-peer.py','endpoint-firewall-guardian.py','client-watchdog.ps1','read-controlled.mjs','match-controlled.mjs','close-endpoint.mjs']
for name in names:
 s=Path('work/nss89',name).read_text(encoding='utf-8').replace('work/nss89','work/nss93').replace('nss89','nss93').replace('NSS89','NSS93')
 if name=='ssh-client.mjs':
  s=s.replace("const udpOut=fs.createWriteStream(dir+'/udp-samples-private.jsonl'),loadOut=fs.createWriteStream(dir+'/load-samples-private.jsonl');","const phaseOut=fs.createWriteStream(dir+'/sender-phases-private.jsonl');const udpOut=fs.createWriteStream(dir+'/udp-samples-private.jsonl'),loadOut=fs.createWriteStream(dir+'/load-samples-private.jsonl');")
  s=s.replace('udpOut.end();loadOut.end();','udpOut.end();loadOut.end();phaseOut.end();')
  a=s.index('const py=');b=s.index('function connectTcp(',a)
  py="""import os,time,json,sys
end=time.monotonic()+180
start=time.monotonic();total=0;budget=0.;last=start;phase=-1;block=b'\\0'*16384
while time.monotonic()<end and total<1024*1024*1024:
 now=time.monotonic();index=int((now-start)//25);rate=52000000 if index%2==0 else 32000000
 if index!=phase:
  phase=index;sys.stderr.write('NSS93_PHASE '+json.dumps({'phase':index,'mbps':rate/1e6,'elapsed':now-start,'at':time.time(),'total':total})+'\\n');sys.stderr.flush()
 budget+=(now-last)*rate/8;last=now
 if total>=budget:time.sleep(.002);continue
 n=os.write(1,block);total+=n
"""
  s=s[:a]+'const py='+json.dumps(py)+';\n'+s[b:]
  old="let error='';stream.stderr.on('data',b=>{if(error.length<2048)error+=b.toString()});"
  new="let error='',phaseBuffer='';stream.stderr.on('data',b=>{if(current!==client)return;const text=b.toString();if(error.length<2048)error+=text;phaseBuffer+=text;let newline;while((newline=phaseBuffer.indexOf('\\n'))>=0){const line=phaseBuffer.slice(0,newline);phaseBuffer=phaseBuffer.slice(newline+1);if(line.startsWith('NSS93_PHASE '))phaseOut.write(JSON.stringify({...JSON.parse(line.slice(12)),receivedAt:Date.now()/1000,tcpSourcePort:port})+'\\n')}});"
  assert s.count(old)==1;s=s.replace(old,new)
 r.joinpath(name).write_text(s,encoding='utf-8')
manifest={p.as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in r.iterdir()if p.is_file()and p.suffix in ['.mjs','.py','.ps1']}
r.joinpath('diagnostic-source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'prepared':True,'routerMutations':False,'offeredTcpAlternatesMbps':[52,32],'phaseSeconds':25,'exactOneTcpAndUdp':True,'allPreviousInputsUntouched':True}))
