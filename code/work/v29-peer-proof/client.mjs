// One authenticated, bounded TCP download plus fixed nonce UDP; no NSS actions.
import fs from 'node:fs';import net from 'node:net';import dgram from 'node:dgram';import assert from 'node:assert/strict';
import {validateReady} from '../v27-raw/raw-policy.mjs';
const file=process.argv[2],c=JSON.parse(fs.readFileSync(file)),dir=file.slice(0,file.lastIndexOf('/'));
assert.equal(c.serverAddress,'172.93.163.251');assert.equal(c.clientAddress,'192.168.237.207');assert.equal(c.tcpPort,45817);assert.equal(c.udpPort,45818);assert.equal(c.seconds,25);
const token=Buffer.from(c.token,'hex');assert.equal(token.length,32);
const started=performance.now(),result={pid:process.pid,startedAt:Date.now()/1000,tcpConnected:false,tcpAuthenticatedReady:false,tcpBytes:0,udpSent:0,udpReceived:0,errors:[],tcpMbpsLimit:8,hardLifetimeSeconds:25};
const udp=dgram.createSocket('udp4'),tcp=new net.Socket();let finished=false,ready=false,pending=Buffer.alloc(0),seq=0,periodic;
const save=()=>fs.writeFileSync(dir+'/client-status-private.json',JSON.stringify({...result,at:Date.now()/1000,elapsed:(performance.now()-started)/1000})+'\n');
function finish(error){if(finished)return;finished=true;clearInterval(periodic);clearTimeout(first);clearTimeout(hard);if(error)result.errors.push(String(error));tcp.destroy();try{udp.close()}catch{}result.seconds=(performance.now()-started)/1000;result.finishedAt=Date.now()/1000;save();fs.writeFileSync(dir+'/client-result-private.json',JSON.stringify(result,null,2)+'\n',{flag:'wx'});}
const hard=setTimeout(()=>finish(),25000),first=setTimeout(()=>finish('Original eight-second first payload deadline'),8000);
udp.on('error',e=>finish('udp:'+e.code));udp.on('message',b=>{if(b.length===128&&b.subarray(0,32).equals(token))result.udpReceived++;});
tcp.on('connect',()=>{result.tcpConnected=true;tcp.write(Buffer.concat([token,Buffer.from([0])]));});
tcp.on('data',b=>{try{if(!ready){pending=Buffer.concat([pending,b]);const at=pending.indexOf(10);if(at<0){assert.ok(pending.length<=512);return;}assert.ok(at<=512);validateReady(JSON.parse(pending.subarray(0,at).toString()),'tcp');ready=true;result.tcpAuthenticatedReady=true;b=pending.subarray(at+1);pending=Buffer.alloc(0);}if(b.length){clearTimeout(first);result.tcpBytes+=b.length;result.firstPayloadAt??=Date.now()/1000;assert.ok(result.tcpBytes<=32*1024*1024);save();}}catch(e){finish(e);}});
tcp.on('error',e=>finish('tcp:'+e.code));tcp.on('close',()=>{if(!finished)finish('Unexpected authenticated TCP close');});
udp.bind(c.udpSourcePort,c.clientAddress,()=>{
 periodic=setInterval(()=>{if(finished)return;const payload=Buffer.alloc(128);token.copy(payload);payload.writeBigUInt64BE(BigInt(seq++),32);udp.send(payload,c.udpPort,c.serverAddress,e=>{if(e&&!finished)finish(e)});result.udpSent++;save();},20);
 tcp.connect({host:c.serverAddress,port:c.tcpPort,localAddress:c.clientAddress,localPort:c.tcpSourcePort});
});save();
