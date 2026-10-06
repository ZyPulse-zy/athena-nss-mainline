import fs from'node:fs';import assert from'node:assert/strict';import{spawnSync}from'node:child_process';
const root='work/v27-raw',load=JSON.parse(fs.readFileSync(root+'/load-latest-private.json')),config=JSON.parse(fs.readFileSync(load.dir+'/client-config-private.json')),began=performance.now(),events=[];
while(performance.now()-began<60000){
 const p=spawnSync(process.execPath,[root+'/read-controlled.mjs'],{encoding:'utf8',windowsHide:true,timeout:15000});events.push({at:new Date().toISOString(),code:p.status,stdout:p.stdout,stderr:p.stderr});fs.writeFileSync(load.dir+'/matching-private.json',JSON.stringify(events,null,2)+'\n');assert.equal(p.status,0,'Owned classification read failed; original result retained');
 const frame=JSON.parse(fs.readFileSync(root+'/controlled-candidates-private.json')),status=JSON.parse(fs.readFileSync(load.dir+'/status-private.json'));assert.equal(status.pid,load.clientPid);assert.equal(status.session,config.session);
 if(frame.pairs.length&&status.tcpConnected&&frame.ownedEstablishedTcpPorts.length===4){console.log(JSON.stringify({passed:true,naturalWanSet:[...new Set(Object.values(frame.pairs[0]).map(x=>x.wan))].sort(),fourOwnedTcpChildrenAndOneUdp:true,permanentClassifierUsed:true,naturalAttempts:events.length,routerPolicyWrites:false}));process.exit(0);}
 if(frame.tcp.length===4&&frame.udp.length===1&&status.tcpConnected){
  const seen=new Set([frame.udp[0].identity.wan]);let duplicate;
  for(const slot of ['tcp','tcp2','tcp3','tcp4']){const t=frame.tcp.find(f=>status.tcpChildren.some(c=>c.slot===slot)&&frame.ownedTcpSlots?.[slot]===f.identity.original.sport);if(!t)continue;if(seen.has(t.identity.wan)){duplicate=slot;break;}seen.add(t.identity.wan);}
  assert.ok(duplicate,'Incomplete owned socket-to-slot mapping');const slot=status.tcpChildren.find(x=>x.slot===duplicate);assert.ok(slot.attempt<8,'Eight natural candidates for an owned TCP slot exhausted');
  fs.writeFileSync(load.dir+'/control.json.new',JSON.stringify({session:config.session,rotateTcp:{slot:duplicate,attempt:slot.attempt+1}}));fs.renameSync(load.dir+'/control.json.new',load.dir+'/control.json');
 }
 await new Promise(r=>setTimeout(r,800));
}
throw Error('Finite natural five-WAN matching expired without router stage');
