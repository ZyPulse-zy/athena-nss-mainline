import fs from'node:fs';import assert from'node:assert/strict';
const root='work/v39-five-sim',load=JSON.parse(fs.readFileSync(root+'/load-latest-private.json')),limit=performance.now()+32000;
while(performance.now()<limit){
 const path=load.dir+'/status-private.json';
 if(fs.existsSync(path)){
  const s=JSON.parse(fs.readFileSync(path));assert.equal(s.pid,load.clientPid);assert.ok(s.errors.length===0,'Owned fixture connection failed before NSS');
  assert.equal(s.tcpChildren.length,4);assert.ok(s.elapsed<50,'Fixed session restoration margin already consumed');
  if(s.tcpChildren.every(x=>x.connected&&Number.isInteger(x.ownerPid)&&x.bytes>0)&&Date.now()/1000-s.at<2){console.log(JSON.stringify({passed:true,fourOwnedSshChildrenReady:true,clientElapsedSeconds:s.elapsed,routerWrites:false}));process.exit(0);}
 }
 if(fs.existsSync(load.dir+'/result-private.json'))throw Error('Owned fixture exited before all handshakes completed');
 await new Promise(r=>setTimeout(r,100));
}
throw Error('Four owned SSH fixture handshakes exceeded readiness bound');
