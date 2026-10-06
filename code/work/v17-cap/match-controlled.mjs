import fs from 'node:fs';import assert from 'node:assert/strict';import {spawnSync}from'node:child_process';
const root='work/v17-cap',load=JSON.parse(fs.readFileSync(root+'/load-latest-private.json')),config=JSON.parse(fs.readFileSync(load.dir+'/client-config-private.json')),began=performance.now(),events=[];
while(performance.now()-began<60000){
 const p=spawnSync(process.execPath,[root+'/read-controlled.mjs'],{encoding:'utf8',windowsHide:true,timeout:15000});events.push({at:new Date().toISOString(),code:p.status,stdout:p.stdout,stderr:p.stderr});fs.writeFileSync(load.dir+'/matching-private.json',JSON.stringify(events,null,2)+'\n');assert.equal(p.status,0,'Owned classification read failed; original result retained');
 const frame=JSON.parse(fs.readFileSync(root+'/controlled-candidates-private.json')),status=JSON.parse(fs.readFileSync(load.dir+'/status-private.json'));
 assert.equal(status.pid,load.clientPid);assert.equal(status.session,config.session);
 if(frame.pairs.length&&status.tcpConnected&&status.tcpBytes>0&&frame.ownedEstablishedTcpPorts.length===2){
  console.log(JSON.stringify({passed:true,naturalWanSet:[...new Set(Object.values(frame.pairs[0]).map(x=>x.wan))],twoOwnedTcpChildrenAndOneUdp:true,permanentClassifierUsed:true,naturalAttempts:events.length,routerPolicyWrites:false}));process.exit(0);
 }
 if(frame.tcp.length===2&&frame.udp.length===1&&status.tcpConnected){
  const slot=status.tcpChildren.find(x=>x.slot==='tcp2');assert.ok(slot.attempt<8,'Eight fixed-UDP second TCP candidates exhausted');
  fs.writeFileSync(load.dir+'/control.json.new',JSON.stringify({session:config.session,rotateTcp:{slot:'tcp2',attempt:slot.attempt+1}}));fs.renameSync(load.dir+'/control.json.new',load.dir+'/control.json');
 }
 await new Promise(r=>setTimeout(r,800));
}
throw Error('Finite natural matching expired without router stage');
