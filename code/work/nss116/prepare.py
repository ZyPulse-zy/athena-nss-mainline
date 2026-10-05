from pathlib import Path
import json
r=Path('work/nss116');r.mkdir(exist_ok=True)
names=['controlled-session.mjs','current-audit-diagnostic.mjs','match-controlled.mjs','run.mjs','start-dallas.mjs','read-controlled.mjs','close-endpoint.mjs','ssh-client.mjs','server.py','discover-peer.py','probe-peer.py','endpoint-firewall-guardian.py','client-watchdog.ps1','failed-wan-owner.lua','declared-baseline.mjs','service-epoch.mjs','module-stage.mjs','payload.mjs','pack-lua.mjs','pack-guardian.mjs','compact-default-queues.mjs','uplink-tag-plan.mjs','parse-ecm-any-wan.mjs','fast-path.lua','module-stage-guardian.lua','qos-physical.lua','tag-normalizer.lua']
for name in names:
 s=(Path('work/nss114')/name).read_bytes();v=s.replace(b'nss114',b'nss116').replace(b'NSS114',b'NSS116');assert v.replace(b'nss116',b'nss114').replace(b'NSS116',b'NSS114')==s
 if name=='start-dallas.mjs':v=v.replace(b'config.mbps=48;',b"config.mbps=48;config.bulkDirection='upload';")
 (r/name).write_bytes(v)
for name in ['qos-native-qualification.json','normalizer-qualification.json','uplink-capacity-private.json']:(r/name).write_bytes((Path('work/nss114')/name).read_bytes())
p=r/'ssh-client.mjs';s=p.read_text(encoding='utf-8')
s=s.replace("import ssh2 from ","import{uploadAck}from'./upload-ack.mjs';\nimport ssh2 from ")
s=s.replace('let ended=false,sock,udpTimer,statusTimer,hardTimer,seq=0,client;', 'let ended=false,sock,udpTimer,statusTimer,hardTimer,seq=0,client,uploadTimer;')
s=s.replace('clearInterval(udpTimer);clearInterval(statusTimer);', 'clearInterval(udpTimer);clearInterval(uploadTimer);clearInterval(statusTimer);')
s=s.replace("bulkTransport:'owned authenticated SSH TCP'", "bulkTransport:'owned authenticated SSH TCP upload',tcpMetric:'server-confirmed received bytes'")
begin=s.index('const py=');end=s.index('function connectTcp(port)',begin)
s=s[:begin]+"assert.equal(c.bulkDirection,'upload');const py=fs.readFileSync(new URL('./upload-server.py',import.meta.url),'utf8');\n"+s[end:]
s=s.replace('const old=client;client=new ssh2.Client();old?.destroy();', 'const old=client;clearInterval(uploadTimer);client=new ssh2.Client();old?.destroy();')
old="stream.on('data',b=>{if(current!==client)return;stats.tcpBytes+=b.length;if(stats.tcpBytes>1024*1024*1024)stop('Byte ceiling reached')});"
assert s.count(old)==1
new="""let pending='',acknowledged=0,submitted=0,blocked=false;const deliveredBase=stats.tcpBytes,begin=performance.now();
stream.on('data',b=>{if(current!==client)return;try{pending+=b.toString('utf8');assert.ok(pending.length<=8192,'Remote counter buffer overflow');let at;while((at=pending.indexOf('\\n'))>=0){const line=pending.slice(0,at);pending=pending.slice(at+1);acknowledged=uploadAck(acknowledged,line);stats.tcpBytes=deliveredBase+acknowledged;assert.ok(stats.tcpBytes<=1024*1024*1024,'Global delivery ceiling reached');}}catch(e){stop('Remote delivery counter: '+String(e));}});
stream.on('drain',()=>{if(current===client)blocked=false});const block=Buffer.alloc(16384);
uploadTimer=setInterval(()=>{if(current!==client||ended||blocked)return;const target=(performance.now()-begin)/1000*48000000/8;try{for(let i=0;i<4&&submitted<target;i++){assert.ok(submitted+block.length<=1024*1024*1024,'Submission ceiling reached');submitted+=block.length;if(!stream.write(block)){blocked=true;break}}}catch(e){stop('Upload: '+String(e));}},5);"""
s=s.replace(old,new);p.write_text(s,encoding='utf-8')
print(json.dumps({'prepared':True,'onlyBulkLoadDirectionChanged':True,'queueRatesChanged':False,'routerPayloadChanged':False,'productionWrites':False}))
