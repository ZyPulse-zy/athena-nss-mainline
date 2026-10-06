// Small software-only stimulus: two finite authenticated SSH stdin receivers.
// No UDP endpoint, router configuration, NSS gate, mark, or policy writes.
import fs from 'node:fs';import net from 'node:net';import assert from 'node:assert/strict';import crypto from 'node:crypto';import {spawnSync} from 'node:child_process';
import ssh2 from 'file:///C:/Users/lishu/Documents/Codex/2026-09-11/ax6600-re-cs-02-jdcos-4/work/runtime/node_modules/ssh2/lib/index.js';
import {connectRouter} from '../nss27/connect-router.mjs';import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
const root='work/nss155',load=JSON.parse(fs.readFileSync(root+'/load-latest-private.json')),cfg=JSON.parse(fs.readFileSync(load.dir+'/client-config-private.json'));
assert.equal(cfg.tcpServerAddress,'18.138.159.236');assert.equal(cfg.clientAddress,'192.168.237.207');const out=root+'/transport-diagnostic-'+new Date().toISOString().replace(/\D/g,'').slice(0,14);fs.mkdirSync(out);
const save=(n,x)=>fs.writeFileSync(out+'/'+n+'.json',JSON.stringify(x,null,2)+'\n',{flag:'wx'});
const ports=Array.from({length:8},(_,i)=>cfg.tcpSourcePort+i);
const available=spawnSync('powershell.exe',['-NoProfile','-NonInteractive','-Command',"@("+ports.join(',')+") | Where-Object {@(Get-NetTCPConnection -LocalPort $_ -ErrorAction SilentlyContinue).Count -eq 0} | ConvertTo-Json -Compress"],{encoding:'utf8',windowsHide:true,timeout:12000});assert.equal(available.status,0);const free=JSON.parse(available.stdout);assert.ok(Array.isArray(free)&&free.length>=2);
const pinsRaw=spawnSync('ssh-keygen',['-F',cfg.tcpServerAddress],{encoding:'utf8',windowsHide:true});assert.equal(pinsRaw.status,0);
const pins=pinsRaw.stdout.split(/\r?\n/).filter(x=>x&&!x.startsWith('#')).map(x=>crypto.createHash('sha256').update(Buffer.from(x.trim().split(/\s+/)[2],'base64')).digest('hex'));
const quote=x=>"'"+x.replaceAll("'","'\\''")+"'",source=fs.readFileSync(root+'/upload-server.py','utf8');
const c=await connectRouter(),results=[];let client;const hard=setTimeout(()=>{client?.destroy();c.close();process.exit(2)},28000);
try{
 for(const port of free.slice(0,2)){
  const r={port,events:[],submitted:0,acknowledged:0,packets:0,errors:[]};client=new ssh2.Client();const sock=net.connect({host:cfg.tcpServerAddress,port:22,localAddress:cfg.clientAddress,localPort:port});let timer,stream;
  client.on('error',e=>r.errors.push(e.message));client.on('ready',()=>{r.events.push({event:'ready',at:Date.now()/1000});client.exec('timeout -k 1 12 python3 -u -c '+quote(source),(error,ch)=>{if(error){r.errors.push(error.message);return}stream=ch;let pending='';ch.on('data',b=>{pending+=b.toString();assert.ok(pending.length<8192);let i;while((i=pending.indexOf('\n'))>=0){const s=pending.slice(0,i);pending=pending.slice(i+1);r.acknowledged=JSON.parse(s).received;r.packets++;}});ch.on('close',code=>r.events.push({event:'stream-close',code,at:Date.now()/1000}));timer=setInterval(()=>{if(r.submitted<2*1024*1024&&ch.writable){ch.write(Buffer.alloc(16384));r.submitted+=16384;}},50);});});
  client.connect({sock,username:'ubuntu',privateKey:fs.readFileSync(cfg.sshKeyPath),hostHash:'sha256',hostVerifier:h=>pins.includes(h),readyTimeout:6000,keepaliveInterval:2000});
  await new Promise(x=>setTimeout(x,6500));clearInterval(timer);
  r.socket={bytesRead:sock.bytesRead,bytesWritten:sock.bytesWritten,destroyed:sock.destroyed};r.stream=stream?{writable:stream.writable,writableLength:stream.writableLength,readableLength:stream.readableLength}:null;
  const e=encode('conntrack -L -f ipv4 -p tcp -s '+cfg.clientAddress+' -d '+cfg.tcpServerAddress+' --sport '+port+' --dport 22 -o extended,id');
  const raw=receipt(await c.run(e.command),e);save('ct-'+port+'-private',raw);assert.equal(raw.code,0);r.ctStates=raw.stdout.trim().split(/\r?\n/).filter(Boolean).map(s=>({state:s.match(/\b(ESTABLISHED|SYN_SENT|SYN_RECV|TIME_WAIT|CLOSE_WAIT|FIN_WAIT|CLOSE|LAST_ACK)\b/)?.[1]??'UNKNOWN',wan:Number(s.match(/\bmark=(\d+)/)?.[1]??0)>>>16&255}));
  client.end();await new Promise(x=>setTimeout(x,200));client.destroy();results.push(r);save('connection-'+results.length+'-private',r);
 }
 const result={readonlyRouter:true,productionConfigurationWrites:false,nssEnabled:false,offeredTcpMbps:2.62144,totalSubmittedBytes:results.reduce((a,r)=>a+r.submitted,0),twoSequentialConnections:results.map(r=>({received:r.acknowledged,submitted:r.submitted,errors:r.errors,states:r.ctStates,socket:r.socket,stream:r.stream})),rootCauseProven:false};
 save('summary',result);console.log(JSON.stringify(result));
}finally{clearTimeout(hard);client?.destroy();c.close()}
