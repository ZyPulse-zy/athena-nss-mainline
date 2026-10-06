import fs from 'node:fs';import assert from 'node:assert/strict';import {spawnSync} from 'node:child_process';import {nextPort} from './download-policy.mjs';
const root='work/v12',load=JSON.parse(fs.readFileSync(root+'/load-latest-private.json')),c=JSON.parse(fs.readFileSync(load.dir+'/client-config-private.json')),began=performance.now(),attempts=[];
let requested=null;
while(performance.now()-began<75000){
 const p=spawnSync(process.execPath,[root+'/read-controlled.mjs'],{encoding:'utf8',windowsHide:true,timeout:15000});attempts.push({at:new Date().toISOString(),code:p.status,stdout:p.stdout,stderr:p.stderr});fs.writeFileSync(load.dir+'/natural-matching-private.json',JSON.stringify(attempts,null,2));assert.equal(p.status,0,p.stderr);
 const x=JSON.parse(fs.readFileSync(root+'/controlled-candidates-private.json')),status=JSON.parse(fs.readFileSync(load.dir+'/status-private.json'));
 assert.equal(status.pid,load.clientPid);assert.equal(status.session,c.session);assert.equal(status.onlyOneRemoteSenderAtATime,true);
 const write=v=>{fs.writeFileSync(load.dir+'/control.json.new',JSON.stringify({session:c.session,...v}));fs.renameSync(load.dir+'/control.json.new',load.dir+'/control.json');};
 if(x.pairs.length){const selected=x.pairs[0].tcp.original.sport;
  if(status.selectedTcpPort!==selected){assert.equal(status.selectedTcpPort,null);write({selectTcpPort:selected});}
  else if(status.tcpConnected&&x.ownedEstablishedTcpPorts.length===1&&x.ownedEstablishedTcpPorts[0]===selected){
   const events=fs.readFileSync(load.dir+'/udp-samples-private.jsonl','utf8').trim().split('\n').map(s=>JSON.parse(s)),at=Date.now()/1000,sent=events.filter(e=>e.event==='sent'&&e.at>=at-3&&e.at<at-.6),replies=new Set(events.filter(e=>e.event==='reply').map(e=>e.sequence));
   fs.writeFileSync(load.dir+'/udp-baseline-qualified.json',JSON.stringify({observed:true,sent:sent.length,returned:sent.filter(e=>replies.has(e.sequence)).length,notAdmissionPredicate:true,routerWrites:false,notCs2Acceptance:true}));
   console.log(JSON.stringify({passed:true,sameWan:x.pairs[0].tcp.wan,selectedByActualPermanentClassifier:true,linuxAffinityPreserved:true,onlyOneOwnedTcpRemaining:true,naturalAttempts:attempts.length,confirmedOldSendersClosed:status.confirmedOldSendersClosed,routerPolicyWrites:false}));process.exit(0);
  }
 }else if(x.tcp.length===1&&x.udp.length===1&&x.ownedEstablishedTcpPorts.length===1&&status.tcpConnected&&status.tcpSourcePort!==requested){
  if(status.tcpSourcePort>=c.tcpSourcePort+7)throw Error('Eight acknowledged software senders exhausted without fixed UDP WAN; no stage');
  const next=nextPort(c.tcpSourcePort,status.tcpSourcePort,status.selectedTcpPort);requested=status.tcpSourcePort;write({tcpSourcePort:next});
 }
 await new Promise(r=>setTimeout(r,1200));
}
throw Error('Finite software-only download matching expired');
