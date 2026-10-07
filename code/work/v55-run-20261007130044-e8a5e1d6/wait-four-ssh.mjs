import{fourOwnedPidsReady}from'../v55-resident-trial/fixture-startup.mjs';
import fs from'node:fs';import assert from'node:assert/strict';
const root='work/v55-run-20261007130044-e8a5e1d6',load=JSON.parse(fs.readFileSync(root+'/load-latest-private.json')),limit=performance.now()+32000;
while(performance.now()<limit){
 const path=load.dir+'/status-private.json';
 if(fs.existsSync(path)){
  const s=JSON.parse(fs.readFileSync(path));assert.equal(s.pid,load.clientPid);assert.ok(s.errors.length===0,'Owned fixture connection failed before NSS');
  assert.equal(s.tcpChildren.length,4);assert.ok(s.elapsed<50,'Fixed session restoration margin already consumed');
  if(fourOwnedPidsReady(s,Date.now()/1000)){console.log(JSON.stringify({passed:true,fourOwnedSshPidsPublished:true,payloadAndClassificationStillRequired:true,clientElapsedSeconds:s.elapsed,routerWrites:false}));process.exit(0);}
 }
 if(fs.existsSync(load.dir+'/result-private.json'))throw Error('Owned fixture exited before four owned child PIDs were published');
 await new Promise(r=>setTimeout(r,100));
}
throw Error('Four owned SSH fixture PID publication exceeded readiness bound');
