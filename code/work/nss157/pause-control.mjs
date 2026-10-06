import fs from 'node:fs';import assert from 'node:assert/strict';import {connectRouter} from '../nss27/connect-router.mjs';import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';import {validateAcceleratedState} from '../nss140/parse-ecm-any-wan.mjs';import {setApplicationPause} from '../nss151/pause-control.mjs';
export {setApplicationPause};const read=(d,n)=>JSON.parse(fs.readFileSync(d+'/'+n+'.json'));
export async function createPauseControl(ctx,selected,load,config){
 assert.equal(ctx.receipt.rollbackBeforeFirstWrite,true);assert.equal(read(ctx.dir,'stage-detached-private').identity.ppid,1);assert.equal(read(ctx.dir,'stage-checkpoint-verified').gzipVerified,true);
 const c=await connectRouter();const task=(async()=>{try{
  const path='/root/router-project/experiments/rp-nss25-state-'+ctx.plan.owner+'/ecm-state';assert.match(path,/^\/root\/router-project\/experiments\/rp-nss25-state-[a-f0-9]{32}\/ecm-state$/);
  const e=encode("lua - "+path+" <<'NSS157_OWNED_PAUSE'\n"+fs.readFileSync('work/nss157/crash-read.lua','utf8')+"\nNSS157_OWNED_PAUSE\n"),due=performance.now()+45000;let proof,raw;
  while(performance.now()<due){const r=receipt(await c.run(e.command),e);assert.equal(r.code,0,r.stderr);raw=JSON.parse(r.stdout);if(raw.count===2){assert.equal(raw.frozen_record_sha256,ctx.plan.frozenHash);assert.equal(raw.tcp_permit,'Y');assert.equal(raw.game_permit,'Y');proof=validateAcceleratedState(raw.state,selected);break}await new Promise(r=>setTimeout(r,150))}
  assert.ok(proof,'Pause withheld until exact acceleration proved');const before=read(load.dir,'status-private');assert.equal(before.pid,load.clientPid);assert.equal(before.session,config.session);assert.equal(before.tcpSourcePort,selected.tcp.original.sport);assert.equal(before.udpSourcePort,selected.udp.original.sport);
  fs.writeFileSync(ctx.dir+'/before-owned-pause-private.json',JSON.stringify({raw,proof,before},null,2)+'\n',{flag:'wx'});setApplicationPause(load,true,ctx.dir);
  let after;const until=performance.now()+10000;while(performance.now()<until){after=read(load.dir,'status-private');if(after.tcpPaused&&after.udpReceived>before.udpReceived+10)break;await new Promise(r=>setTimeout(r,100))}
  assert.equal(after.tcpPaused,true);assert.equal(after.tcpConnected,true);assert.equal(after.tcpSourcePort,before.tcpSourcePort);assert.equal(after.udpSourcePort,before.udpSourcePort);assert.ok(after.udpReceived>before.udpReceived+10);assert.deepEqual(after.errors,[]);
  const result={passed:true,ecmBeforePause:2,ownedApplicationPayloadPaused:true,sameTcpSocketRequested:true,udpContinued:true,routerWrites:false,ctExitClaimed:false};fs.writeFileSync(ctx.dir+'/owned-pause-trigger.json',JSON.stringify(result,null,2)+'\n',{flag:'wx'});return result;
 }finally{c.close()}})();return{task:task.then(result=>({passed:true,result}),error=>({passed:false,error:String(error)}))};
}
