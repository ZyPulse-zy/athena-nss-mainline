// A single ordinary TCP connection attempt and 30 nonce UDP packets, no load.
import fs from 'node:fs';
import net from 'node:net';
import dgram from 'node:dgram';
import assert from 'node:assert/strict';
const file=process.argv[2], c=JSON.parse(fs.readFileSync(file)), out=file.replace('config-private.json','client-result-private.json');
assert.equal(c.clientAddress,'192.168.237.207');assert.equal(c.serverAddress,'172.93.163.251');
assert.equal(c.tcpPort,45817);assert.equal(c.udpPort,45818);
assert.ok(c.tcpSourcePort>=57000&&c.tcpSourcePort<58800);assert.ok(c.udpSourcePort>=59000&&c.udpSourcePort<59800);
const token=Buffer.from(c.token,'hex');assert.equal(token.length,32);
const started=performance.now(), result={pid:process.pid,startedAt:Date.now()/1000,tcpSourcePort:c.tcpSourcePort,udpSourcePort:c.udpSourcePort,tcpConnected:false,tcpPayloadBytes:0,udpSent:0,errors:[]};
const udp=dgram.createSocket('udp4');let tcp,finished=false,count=0,periodic;
function finish(){if(finished)return;finished=true;clearInterval(periodic);tcp?.destroy();try{udp.close()}catch{}result.seconds=(performance.now()-started)/1000;result.finishedAt=Date.now()/1000;fs.writeFileSync(out,JSON.stringify(result,null,2)+'\n',{flag:'wx'});}
const deadline=setTimeout(finish,8000);
udp.on('error',e=>result.errors.push('udp:'+e.code));
udp.bind(c.udpSourcePort,c.clientAddress,()=>{
 periodic=setInterval(()=>{if(finished||count>=30){clearInterval(periodic);return;}udp.send(Buffer.concat([token,Buffer.alloc(96)]),c.udpPort,c.serverAddress,e=>{if(e)result.errors.push('udpSend:'+e.code);else result.udpSent++});count++;},20);
 tcp=net.connect({host:c.serverAddress,port:c.tcpPort,localAddress:c.clientAddress,localPort:c.tcpSourcePort});
 tcp.on('connect',()=>{result.tcpConnected=true;result.tcpConnectedAt=Date.now()/1000;tcp.end();});
 tcp.on('data',b=>{result.tcpPayloadBytes+=b.length;tcp.destroy();});
 tcp.on('error',e=>result.errors.push('tcp:'+e.code));
});
process.once('exit',()=>{clearTimeout(deadline);tcp?.destroy();});
