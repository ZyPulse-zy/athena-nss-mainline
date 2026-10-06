import fs from 'node:fs';import path from 'node:path';import net from 'node:net';import dgram from 'node:dgram';import assert from 'node:assert/strict';
import {nextPendingPort} from './pending-policy.mjs';
import {createPacer} from './bounded-pacer.mjs';import {uploadAck} from './upload-ack.mjs';
const configPath=path.resolve(process.argv[2]),c=JSON.parse(fs.readFileSync(configPath)),dir=path.dirname(configPath);
assert.equal(c.mbps,32);assert.equal(c.seconds,180);assert.equal(c.pps,50);assert.equal(c.bulkDirection,'upload');assert.equal(c.tcpPort,45817);assert.equal(c.udpPort,45818);assert.equal(c.serverAddress,'172.93.163.251');assert.equal(c.tcpServerAddress,c.serverAddress);
const token=Buffer.from(c.token,'hex');assert.equal(token.length,32);const started=performance.now();
const stats={pid:process.pid,session:c.session,startedAt:Date.now()/1000,tcpBytes:0,tcpSubmitted:0,tcpSourcePort:c.tcpSourcePort,udpSourcePort:c.udpSourcePort,udpSent:0,udpReceived:0,tcpConnected:false,errors:[],bulkTransport:'nonce authenticated raw TCP upload',tcpMetric:'server-confirmed received bytes',pacerDebtCatchupAllowed:false,maximumPacerCreditBytes:65536,tcpPaused:false};
const udpOut=fs.createWriteStream(dir+'/udp-samples-private.jsonl'),loadOut=fs.createWriteStream(dir+'/load-samples-private.jsonl');let ended=false,client,sock,uploadTimer,pendingTimer,udpTimer,statusTimer,seq=0;const seen=new Set();
function stamp(){if(ended)return;const x={...stats,at:Date.now()/1000,elapsed:(performance.now()-started)/1000};fs.writeFileSync(dir+'/status-private.json.new',JSON.stringify(x));try{fs.renameSync(dir+'/status-private.json.new',dir+'/status-private.json')}catch(e){if(e.code!=='EPERM'&&e.code!=='EBUSY')throw e;stats.statusPublicationDeferrals=(stats.statusPublicationDeferrals??0)+1}loadOut.write(JSON.stringify(x)+'\n')}
function stop(reason){if(ended)return;ended=true;clearTimeout(pendingTimer);clearInterval(uploadTimer);clearInterval(udpTimer);clearInterval(statusTimer);clearTimeout(hard);if(reason)stats.errors.push(reason);sock?.close();client?.destroy();fs.writeFileSync(dir+'/result-private.json',JSON.stringify({...stats,finishedAt:Date.now()/1000,seconds:(performance.now()-started)/1000},null,2));udpOut.end();loadOut.end();setTimeout(()=>process.exit(stats.errors.length?1:0),50)}
function closeOwnedTcp(){assert.ok(client&&stats.tcpConnected);clearInterval(uploadTimer);stats.tcpClosingRequested=true;stats.tcpCloseRequestedAt=Date.now()/1000;client.end();loadOut.write(JSON.stringify({event:'tcp-owned-close-requested',at:stats.tcpCloseRequestedAt,sourcePort:stats.tcpSourcePort,udpSourcePort:stats.udpSourcePort})+'\n')}
function connectTcp(port){
 assert.ok(Number.isInteger(port)&&port>=c.tcpSourcePort&&port<c.tcpSourcePort+8);const old=client;clearTimeout(pendingTimer);clearInterval(uploadTimer);client=net.connect({host:c.serverAddress,port:c.tcpPort,localAddress:c.clientAddress,localPort:port});old?.destroy();const current=client;stats.tcpSourcePort=port;stats.tcpConnected=false;stats.tcpClosingRequested=false;
 const base=stats.tcpBytes;let pending='',acknowledged=0,submitted=0,blocked=false,authenticated=false;
 const attemptedAt=performance.now();
 function retryPending(reason,failed){if(current!==client||ended)return;if(authenticated){stop('TCP: '+reason);return}
  const attempt={port,reason,at:Date.now()/1000,elapsedMs:performance.now()-attemptedAt,nonceAccepted:false};
  stats.pendingTcpAttempts=(stats.pendingTcpAttempts??[]);stats.pendingTcpAttempts.push(attempt);loadOut.write(JSON.stringify({event:'pending-tcp-refused',...attempt})+'\n');
  try{const next=nextPendingPort({start:c.tcpSourcePort,port,authenticated,elapsedMs:attempt.elapsedMs,failed});assert.ok(next!==null);connectTcp(next)}catch(e){stop(String(e))}
 }
 pendingTimer=setTimeout(()=>retryPending('Pending TCP nonce not accepted within original matching slice',false),5500);
 current.on('connect',()=>current.write(token));current.on('error',e=>retryPending(e.message,true));
 current.on('close',()=>{if(current!==client||ended)return;stats.tcpConnected=false;stats.tcpClosedAt=Date.now()/1000;if(stats.tcpClosingRequested)loadOut.write(JSON.stringify({event:'tcp-owned-closed',at:stats.tcpClosedAt,sourcePort:port,udpSourcePort:stats.udpSourcePort})+'\n');else retryPending('Unexpected raw TCP close',true)});
 current.on('drain',()=>{if(current===client)blocked=false});
 current.on('data',b=>{if(current!==client||ended)return;try{
  pending+=b.toString();assert.ok(pending.length<=8192);let at;
  while((at=pending.indexOf('\n'))>=0){const line=pending.slice(0,at);pending=pending.slice(at+1);const x=JSON.parse(line);
   if(!authenticated){assert.deepEqual(x,{ready:true});authenticated=true;clearTimeout(pendingTimer);stats.tcpConnected=true;stats.remoteNonceAccepted=true;const pacer=createPacer(performance.now(),32000000/8);uploadTimer=setInterval(()=>{if(current!==client||ended||stats.tcpClosingRequested)return;try{for(let i=0;i<4&&pacer.next(performance.now(),blocked||stats.tcpPaused);i++){assert.ok(stats.tcpSubmitted+16384<=512*1024*1024);submitted+=16384;stats.tcpSubmitted+=16384;if(!current.write(Buffer.alloc(16384))){blocked=true;break}}}catch(e){stop(String(e))}},5);
   }else{acknowledged=uploadAck(acknowledged,line);assert.ok(acknowledged<=submitted);stats.tcpBytes=base+acknowledged;assert.ok(stats.tcpBytes<=512*1024*1024)}
  }
 }catch(e){stop('Authenticated counter: '+String(e))}});
}
sock=dgram.createSocket('udp4');sock.on('error',e=>stop('UDP: '+e.message));sock.on('message',b=>{if(b.length!==128||!b.subarray(0,32).equals(token))return;const number=Number(b.readBigUInt64BE(32));if(seen.has(number))return;seen.add(number);stats.udpReceived++;udpOut.write(JSON.stringify({event:'reply',sequence:number,at:Date.now()/1000,sourcePort:stats.udpSourcePort,rttMs:performance.now()-b.readDoubleBE(40)})+'\n')});sock.bind(c.udpSourcePort,c.clientAddress,()=>sock.connect(c.udpPort,c.serverAddress));
udpTimer=setInterval(()=>{if(ended)return;try{
 const file=dir+'/control.json';if(fs.existsSync(file)){const x=JSON.parse(fs.readFileSync(file));assert.equal(x.session,c.session);if(x.stop){stop();return}if(x.closeTcp!==undefined){assert.equal(typeof x.closeTcp,'boolean');if(x.closeTcp&&stats.tcpConnected&&!stats.tcpClosingRequested)closeOwnedTcp()}if(x.pauseTcp!==undefined){assert.equal(typeof x.pauseTcp,'boolean');stats.tcpPaused=x.pauseTcp}assert.equal(x.udpSourcePort??stats.udpSourcePort,c.udpSourcePort);if(x.tcpSourcePort!==undefined&&x.tcpSourcePort>stats.tcpSourcePort)connectTcp(x.tcpSourcePort)}
 const b=Buffer.alloc(128);token.copy(b);b.writeBigUInt64BE(BigInt(seq),32);b.writeDoubleBE(performance.now(),40);sock.send(b,e=>{if(e&&!ended)stop(String(e))});stats.udpSent++;udpOut.write(JSON.stringify({event:'sent',sequence:seq++,at:Date.now()/1000,sourcePort:stats.udpSourcePort})+'\n');
 }catch(e){stop(String(e))}},20);
statusTimer=setInterval(stamp,250);const hard=setTimeout(()=>stop(),180000);stamp();connectTcp(c.tcpSourcePort);
