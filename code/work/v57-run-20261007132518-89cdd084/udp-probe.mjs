import dgram from 'node:dgram';
import assert from 'node:assert/strict';
const c=JSON.parse(process.argv[2]),mode=process.argv[3];assert.ok(['connected','unconnected'].includes(mode));
const token=Buffer.from(c.token,'hex'),base=c.probeBaseSequence;assert.equal(token.length,32);assert.ok(Number.isInteger(base));
const sock=dgram.createSocket('udp4'),seen=new Set();let sent=0,timer,ended=false;
sock.on('error',e=>{console.error(String(e));process.exitCode=1;finish();});
sock.on('message',(b,peer)=>{if(b.length===128&&b.subarray(0,32).equals(token)&&peer.address===c.serverAddress&&peer.port===c.udpPort){const seq=Number(b.readBigUInt64BE(32));if(seq>=base&&seq<base+20)seen.add(seq);}});
function finish(){if(ended)return;ended=true;clearInterval(timer);try{sock.close();}catch{}console.log(JSON.stringify({mode:'node-'+mode,sent,received:seen.size,nonceVerified:true}));}
function begin(){if(ended)return;timer=setInterval(()=>{if(sent>=20){clearInterval(timer);return;}const b=Buffer.alloc(128);token.copy(b);b.writeBigUInt64BE(BigInt(base+sent),32);if(mode==='connected')sock.send(b);else sock.send(b,c.udpPort,c.serverAddress);sent++;},20);setTimeout(finish,1100);}
sock.bind(c.udpSourcePort,c.clientAddress,()=>{if(mode==='connected')sock.connect(c.udpPort,c.serverAddress,begin);else begin();});
