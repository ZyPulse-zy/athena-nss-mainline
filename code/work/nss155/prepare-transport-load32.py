from pathlib import Path
r=Path(__file__).resolve().parent;p=r/'transport-load32-diagnostic.mjs';assert not p.exists()
s=(r/'transport-reopen-diagnostic.mjs').read_text(encoding='utf-8')
s=s.replace("import {connectRouter}","import {createPacer} from './bounded-pacer.mjs';\nimport {connectRouter}")
s=s.replace("root+'/transport-diagnostic-'","root+'/transport-load32-diagnostic-'")
s=s.replace("let timer,stream;","let timer,stream,blocked=false;const samples=[];")
old="timer=setInterval(()=>{if(r.submitted<2*1024*1024&&ch.writable){ch.write(Buffer.alloc(16384));r.submitted+=16384;}},50);";assert s.count(old)==1
new="ch.on('drain',()=>{blocked=false});const pacer=createPacer(performance.now(),32000000/8);timer=setInterval(()=>{for(let i=0;i<4&&r.submitted<32*1024*1024&&pacer.next(performance.now(),blocked);i++){r.submitted+=16384;if(!ch.write(Buffer.alloc(16384))){blocked=true;break}}},5);"
s=s.replace(old,new).replace("await new Promise(x=>setTimeout(x,6500));clearInterval(timer);","const sampleTimer=setInterval(()=>samples.push({at:Date.now()/1000,submitted:r.submitted,acknowledged:r.acknowledged,blocked,socketRead:sock.bytesRead,socketWritten:sock.bytesWritten}),250);await new Promise(x=>setTimeout(x,6500));clearInterval(timer);clearInterval(sampleTimer);r.samples=samples;")
s=s.replace('offeredTcpMbps:2.62144','offeredTcpMbps:32');p.write_text(s,encoding='utf-8',newline='')
print('Same finite two-connection software diagnostic, offered rate alone raised to the existing32Mbps pacer cap.')
