// Bounded public speed-test GETs. Payloads are discarded, never saved or executed.
// No proxy/DNS/routing/configuration changes. Each native curl has its own timeout.
import fs from 'node:fs';import assert from 'node:assert/strict';import {spawn}from'node:child_process';
const cfgPath=process.argv[3],mode=process.argv[2];assert.ok(['parent','worker'].includes(mode));
const cfg=JSON.parse(fs.readFileSync(cfgPath));
assert.equal(cfg.endpoint,'https://speed.cloudflare.com/__down');assert.match(cfg.output,/^work\/nss66\/[a-z0-9-]+\.json$/);
assert.ok(Number.isInteger(cfg.seconds)&&cfg.seconds>=8&&cfg.seconds<=240);
assert.ok(Number.isInteger(cfg.parallel)&&cfg.parallel>=1&&cfg.parallel<=16);
assert.ok(Number.isSafeInteger(cfg.maximumAllocatedBytes)&&cfg.maximumAllocatedBytes>=10000000&&cfg.maximumAllocatedBytes<=12000000000);
assert.equal(process.platform,'win32');
if(mode==='parent'){
 const start=Date.now(),child=spawn(process.execPath,[process.argv[1],'worker',cfgPath],{windowsHide:true,stdio:['ignore','pipe','pipe','ipc']});
 let stderr='';child.stdout.on('data',b=>process.stdout.write(b));child.stderr.on('data',b=>{stderr=(stderr+b).slice(-1024)});
 const requestStop=setTimeout(()=>{if(child.connected)child.send({stop:true})},cfg.seconds*1000);
 const hard=setTimeout(()=>child.kill(),(cfg.seconds+3)*1000);
 child.on('exit',(code,signal)=>{
  clearTimeout(hard);clearTimeout(requestStop);
  const proof={boundedParentExited:true,startedAt:new Date(start).toISOString(),finishedAt:new Date().toISOString(),workerExitCode:code,workerSignal:signal,
   independentNativeRequestTimeoutSeconds:20,parentHardDeadlineSeconds:cfg.seconds+3,routerWrites:false,payloadSaved:false};
  fs.writeFileSync(cfg.output.replace('.json','-watchdog.json'),JSON.stringify(proof,null,2)+'\n',{flag:'wx'});
  if(code!==0){console.error(stderr||'Bounded download worker failed');process.exitCode=1;}
 });
}else{
 const startedAt=Date.now(),deadline=startedAt+cfg.seconds*1000,chunk=10000000,active=new Set(),requests=[];
 let allocated=0,received=0,stopping=false;
 function stop(){if(stopping)return;stopping=true;for(const p of active)p.kill();}
 process.on('message',m=>{if(m?.stop)stop()});
 const timer=setTimeout(stop,cfg.seconds*1000);
 function launch(){
  if(stopping||Date.now()>=deadline)return;
  const bytes=Math.min(chunk,cfg.maximumAllocatedBytes-allocated);if(bytes<=0)return;allocated+=bytes;
  const start=Date.now();
  const p=spawn('C:/Windows/System32/curl.exe',['--ipv4','--http1.1','--silent','--show-error','--connect-timeout','5','--max-time','20',
   '--output','NUL','--write-out','%{http_code} %{size_download} %{time_total}',cfg.endpoint+'?bytes='+bytes],{windowsHide:true,stdio:['ignore','pipe','pipe']});
  active.add(p);let output='',error='';p.stdout.on('data',b=>output=(output+b).slice(-512));p.stderr.on('data',b=>error=(error+b).slice(-512));
  p.on('exit',(code,signal)=>{
   active.delete(p);const v=output.trim().match(/^(\d{3}) (\d+) ([\d.]+)$/);
   const size=v?Number(v[2]):0;received+=size;
   if(v&&Number(v[1])>=400){process.exitCode=1;stop();}
   requests.push({startedElapsedSeconds:(start-startedAt)/1000,finishedElapsedSeconds:(Date.now()-startedAt)/1000,
    allocatedBytes:bytes,receivedBytes:size,httpStatus:v?Number(v[1]):null,exitCode:code,signal,stopWasRequested:stopping,
    boundedErrorType:error?'curl-request-error':null});
   fs.writeFileSync(cfg.output,JSON.stringify({startedAt:new Date(startedAt).toISOString(),updatedAt:new Date().toISOString(),
    parallel:cfg.parallel,seconds:cfg.seconds,maximumAllocatedBytes:cfg.maximumAllocatedBytes,allocatedBytes:allocated,receivedBytes:received,
    activeRequests:active.size,stopRequested:stopping,requests,payloadSaved:false,payloadExecuted:false,
    ecmOpened:false,steamTraffic:false,proxyDnsOrRouterSettingsChanged:false},null,2)+'\n');
   if(!stopping&&Date.now()<deadline&&allocated<cfg.maximumAllocatedBytes)launch();
   if(active.size===0){clearTimeout(timer);process.disconnect?.();}
  });
 }
 for(let i=0;i<cfg.parallel;i++)launch();
 console.log(JSON.stringify({boundedDownloadStarted:true,parallel:cfg.parallel,hardSeconds:cfg.seconds,maxAllocatedBytes:cfg.maximumAllocatedBytes,payloadSaved:false,steamTraffic:false}));
}
