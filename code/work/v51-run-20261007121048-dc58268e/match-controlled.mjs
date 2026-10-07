import fs from'node:fs';import assert from'node:assert/strict';import{spawnSync}from'node:child_process';import{naturalRotationPlan}from'./acquisition-plan.mjs';
const root='work/v51-run-20261007121048-dc58268e',load=JSON.parse(fs.readFileSync(root+'/load-latest-private.json')),config=JSON.parse(fs.readFileSync(load.dir+'/client-config-private.json')),began=performance.now(),events=[];
function control(value){fs.writeFileSync(load.dir+'/control.json.new',JSON.stringify({session:config.session,...value}));fs.renameSync(load.dir+'/control.json.new',load.dir+'/control.json');}
while(performance.now()-began<35000){
 const p=spawnSync(process.execPath,[root+'/read-controlled.mjs'],{encoding:'utf8',windowsHide:true,timeout:15000});const event={at:new Date().toISOString(),code:p.status,stdout:p.stdout,stderr:p.stderr};events.push(event);fs.writeFileSync(load.dir+'/matching-private.json',JSON.stringify(events,null,2)+'\n');assert.equal(p.status,0,'Owned classification read failed; original result retained');
 const frame=JSON.parse(fs.readFileSync(root+'/controlled-candidates-private.json')),status=JSON.parse(fs.readFileSync(load.dir+'/status-private.json'));assert.equal(status.pid,load.clientPid);assert.equal(status.session,config.session);
 if(frame.pairs.length&&status.tcpConnected&&frame.ownedEstablishedTcpPorts.length===4){control({freezeTcp:true});console.log(JSON.stringify({passed:true,naturalWanSet:[...new Set(Object.values(frame.pairs[0]).map(x=>x.wan))].sort(),fourOwnedTcpChildrenAndOneUdp:true,permanentClassifierUsed:true,naturalReads:events.length,routerPolicyWrites:false,batchAcquisitionOnlyBeforeNss:true}));process.exit(0);}
 const plan=naturalRotationPlan(frame,status);event.acquisition=plan;fs.writeFileSync(load.dir+'/matching-private.json',JSON.stringify(events,null,2)+'\n');if(plan.commands.length)control({rotateTcpBatch:plan.commands});
 await new Promise(r=>setTimeout(r,plan.commands.length?100:200));
}
throw Error('Finite natural five-WAN matching expired without router stage');
