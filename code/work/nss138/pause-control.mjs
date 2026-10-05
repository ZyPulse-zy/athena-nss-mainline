import fs from'node:fs';import assert from'node:assert/strict';
import{connectRouter}from'../nss27/connect-router.mjs';
import{encode,receipt}from'../nss11/v7-observe-repair/observe2/transport.mjs';

export function setApplicationPause(load,paused,proofDir){
 assert.equal(typeof paused,'boolean');const config=JSON.parse(fs.readFileSync(load.dir+'/client-config-private.json'));
 const status=JSON.parse(fs.readFileSync(load.dir+'/status-private.json'));
 assert.equal(status.pid,load.clientPid);assert.equal(status.session,config.session);assert.ok(status.tcpConnected&&Date.now()/1000-status.at<2);
 const path=load.dir+'/control.json';const before=fs.existsSync(path)?JSON.parse(fs.readFileSync(path)):{session:config.session};assert.equal(before.session,config.session);
 const next={...before,pauseTcp:paused};fs.writeFileSync(path+'.new',JSON.stringify(next));fs.renameSync(path+'.new',path);
 const r={at:new Date().toISOString(),paused,applicationPayloadOnly:true,sameTcpSocketRequested:true,udpUnchanged:true,clientPid:status.pid,tcpSourcePort:status.tcpSourcePort,udpSourcePort:status.udpSourcePort,before,after:next,clientIndependentDeadlineSeconds:210};
 fs.writeFileSync(proofDir+'/'+(paused?'application-pause':'application-resume')+'-private.json',JSON.stringify(r,null,2)+'\n',{flag:'wx'});return r;
}
export async function pauseAfterOwnedAcceleration(load,context,c){
 assert.ok(c&&typeof c.run==='function');const due=performance.now()+45000,reads=[];
 const code=fs.readFileSync('work/nss138/watcher-read.lua','utf8');
 try{
  while(performance.now()<due){const e=encode("lua - <<'NSS138_OWNED_PAUSE_READ'\n"+code+"\nNSS138_OWNED_PAUSE_READ\n");const raw=receipt(await c.run(e.command),e);assert.equal(raw.code,0,raw.stderr);const v=JSON.parse(raw.stdout);reads.push(v);
   if(v.count===2&&v.stop===0&&v.stopAfter===0){assert.equal(v.hash,context.plan.frozenHash);assert.equal(v.tcp,'Y');assert.equal(v.udp,'Y');const r=setApplicationPause(load,true,context.dir);fs.writeFileSync(context.dir+'/pause-trigger-private.json',JSON.stringify({passed:true,readOnlyRouterWatcher:true,readings:reads,trigger:v,application:r},null,2)+'\n',{flag:'wx'});return r;}
   assert.ok(v.count>=0&&v.count<=2,'Unexpected pretrigger ECM scope');if(v.count>0)assert.equal(v.hash,context.plan.frozenHash);await new Promise(r=>setTimeout(r,250));
  }throw Error('Owned accelerated pair never reached pause trigger');
 }catch(e){fs.writeFileSync(context.dir+'/pause-watcher-error-private.json',JSON.stringify({error:String(e),readings:reads},null,2)+'\n',{flag:'wx'});throw e;}finally{c.close()}
}
