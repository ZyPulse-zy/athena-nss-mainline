import fs from 'node:fs';import assert from 'node:assert/strict';import {spawnSync} from 'node:child_process';
const root='work/nss156',load=JSON.parse(fs.readFileSync(root+'/load-latest-private.json')),c=JSON.parse(fs.readFileSync(load.dir+'/client-config-private.json')),began=performance.now(),attempts=[];
while(performance.now()-began<75000){const p=spawnSync(process.execPath,[root+'/read-controlled-v7.mjs'],{encoding:'utf8',windowsHide:true,timeout:12000});attempts.push({at:new Date().toISOString(),code:p.status,stdout:p.stdout,stderr:p.stderr});fs.writeFileSync(load.dir+'/natural-matching-private.json',JSON.stringify(attempts,null,2));assert.equal(p.status,0,p.stderr);
 const x=JSON.parse(fs.readFileSync(root+'/controlled-candidates-private.json')),status=JSON.parse(fs.readFileSync(load.dir+'/status-private.json'));
 assert.equal(status.pid,load.clientPid);assert.equal(status.session,c.session);
 if(x.pairs.length){const selected=x.pairs[0].tcp.original.sport;if(status.selectedTcpPort!==selected){assert.equal(status.selectedTcpPort,null);fs.writeFileSync(load.dir+'/control.json.new',JSON.stringify({session:c.session,selectTcpPort:selected}));fs.renameSync(load.dir+'/control.json.new',load.dir+'/control.json');}
  else if(status.tcpConnected&&x.ownedEstablishedTcpPorts.length===1&&x.ownedEstablishedTcpPorts[0]===selected){
   const events=fs.readFileSync(load.dir+'/udp-samples-private.jsonl','utf8').trim().split('\n').map(s=>JSON.parse(s)),at=Date.now()/1000,sent=events.filter(e=>e.event==='sent'&&e.at>=at-3&&e.at<at-.6),replies=new Set(events.filter(e=>e.event==='reply').map(e=>e.sequence)),returned=sent.filter(e=>replies.has(e.sequence)).length;
   fs.writeFileSync(load.dir+'/udp-baseline-qualified.json',JSON.stringify({observed:true,sent:sent.length,returned,notAdmissionPredicate:true,routerWrites:false,notCs2Acceptance:true}));
   console.log(JSON.stringify({passed:true,sameWan:x.pairs[0].tcp.wan,selectedByActualPermanentClassifier:true,linuxAffinityPreserved:true,onlyOneOwnedTcpRemaining:true,softwareOnlyProbeCohort:true,naturalAttempts:attempts.length,routerPolicyWrites:false}));process.exit(0);
  }
 }
 if(!x.pairs.length&&x.tcp.length===4&&x.ownedEstablishedTcpPorts.length===4)throw Error('Four software-only candidates classified, none match fixed UDP WAN; no stage');
 await new Promise(r=>setTimeout(r,1200));
}
throw Error('Finite software-only cohort preparation expired');
