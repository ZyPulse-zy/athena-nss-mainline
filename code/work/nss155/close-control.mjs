import fs from 'node:fs';
import assert from 'node:assert/strict';
import {connectRouter} from '../nss27/connect-router.mjs';
import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
import {validateAcceleratedState} from '../nss140/parse-ecm-any-wan.mjs';
const read=(dir,n)=>JSON.parse(fs.readFileSync(dir+'/'+n+'.json'));
// Independent read-only observer closes only the explicitly owned application
// socket. It never changes a router gate, CT, mark, tag, route, or guardian.
export async function createCloseControl(ctx,selected,load,config){
 assert.equal(ctx.receipt.rollbackBeforeFirstWrite,true);
 assert.equal(read(ctx.dir,'stage-detached-private').identity.ppid,1);
 const cp=read(ctx.dir,'stage-checkpoint-verified');assert.equal(cp.gzipVerified,true);
 const c=await connectRouter();
 const task=(async()=>{
  const save=(n,v)=>fs.writeFileSync(ctx.dir+'/'+n+'.json',JSON.stringify(v,null,2)+'\n',{flag:'wx'});
  let proof,raw;
  try{
   const path='/root/router-project/experiments/rp-nss25-state-'+ctx.plan.owner+'/ecm-state';
   assert.match(path,/^\/root\/router-project\/experiments\/rp-nss25-state-[a-f0-9]{32}\/ecm-state$/);
   const e=encode("lua - "+path+" <<'NSS155_OWNED_CLOSE'\n"+fs.readFileSync('work/nss155/crash-read.lua','utf8')+"\nNSS155_OWNED_CLOSE\n");
   const due=performance.now()+45000;
   while(performance.now()<due){
    const r=receipt(await c.run(e.command),e);assert.equal(r.code,0,r.stderr);raw=JSON.parse(r.stdout);
    if(raw.count===2){
     assert.equal(raw.frozen_record_sha256,ctx.plan.frozenHash);
     assert.equal(raw.tcp_permit,'Y');assert.equal(raw.game_permit,'Y');
     for(const slot of ['tcp','game'])assert.ok(raw[slot+'_pinned_state'].includes('pinned=1 current_hash_matches=1'));
     proof=validateAcceleratedState(raw.state,selected);break;
    }
    await new Promise(r=>setTimeout(r,150));
   }
   assert.ok(proof,'Exact accelerated pair not observed; application close withheld');
   const before=read(load.dir,'status-private');assert.equal(before.session,config.session);assert.equal(before.pid,load.clientPid);
   assert.equal(before.tcpConnected,true);assert.equal(before.tcpSourcePort,selected.tcp.original.sport);
   assert.equal(before.udpSourcePort,selected.udp.original.sport);assert.ok(Date.now()/1000-before.at<2);
   save('before-owned-close-private',{raw,proof,client:before,checkpointDownloadedBeforeFirstWrite:true,independentRollbackVerified:true});
   const requestedAt=Date.now()/1000;
   fs.writeFileSync(load.dir+'/control.json.new',JSON.stringify({session:config.session,closeTcp:true}));
   fs.renameSync(load.dir+'/control.json.new',load.dir+'/control.json');
   let after;const until=performance.now()+10000;
   while(performance.now()<until){
    after=read(load.dir,'status-private');assert.equal(after.session,config.session);assert.equal(after.pid,load.clientPid);
    if(!after.tcpConnected&&after.tcpClosingRequested&&after.tcpClosedAt>=requestedAt&&after.udpReceived>before.udpReceived+10)break;
    await new Promise(r=>setTimeout(r,100));
   }
   assert.equal(after.tcpConnected,false);assert.equal(after.tcpClosingRequested,true);assert.ok(after.tcpClosedAt>=requestedAt);
   assert.equal(after.udpSourcePort,before.udpSourcePort);assert.ok(after.udpReceived>before.udpReceived+10);assert.deepEqual(after.errors,[]);
   const result={passed:true,requestedAt,actualCloseAt:after.tcpClosedAt,ownClientPid:load.clientPid,
    originalTcpPort:before.tcpSourcePort,udpPort:after.udpSourcePort,udpContinued:true,udpRepliesAfterClose:after.udpReceived-before.udpReceived,
    ecmbeforeClose:2,routerWrites:false,clearConntrack:false,ctExitClaimed:false};
   save('owned-tcp-close-private',result);return result;
  }finally{c.close()}
 })();
 // Preserve failures without an unhandled rejection while the epoch driver is
 // finishing its independently guarded restoration.
 return {task:task.then(result=>({passed:true,result}),error=>({passed:false,error:String(error)}))};
}
