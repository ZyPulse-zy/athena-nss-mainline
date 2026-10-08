// A finite, separate simulation fixture. The resident product never imports it.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import path from 'node:path';import crypto from 'node:crypto';
import {materialize,hash,read,save,namespacePattern} from '../resident-dev-20261007/materialize.mjs';
import {once,root} from './adapt.mjs';
export const fixtureLimits=Object.freeze({client:360,guard:390,server:450,firewall:360,sender:365,targetNss:190,mbps:32,offeredMbps:16,pps:50,packetBytes:128});
export function materializeFixture(runtime,cutoff){
 const q=materialize(runtime,cutoff);
 const replaceNumbers=s=>s.replace(/\b180\b/g,'360').replace(/\b210\b/g,'390').replace(/\b240\b/g,'440').replace(/\b250\b/g,'450').replaceAll('4min 10s','7min 30s');
 for(const name of ['start-dallas.mjs','native-client.mjs','owned-load-policy.mjs','client-watchdog.ps1','server.py','endpoint-firewall-guardian.py','close-endpoint.mjs','capture-client-closure.ps1','check-udp-path.mjs','download-server.py']){
  const file=runtime+'/'+name;let s=fs.readFileSync(file,'utf8');
  if(name==='native-client.mjs'){
   s=once(s,'assert.equal(c.seconds,180)','assert.equal(c.seconds,360)');
   s=once(s,'finish(),180000','finish(),360000');s=once(s,'timeout -k 1 185 python3','timeout -k 1 365 python3');
  }else if(name==='client-watchdog.ps1')s=once(s,'WaitForExit(210000)','WaitForExit(390000)');
  else s=replaceNumbers(s);
  if(name==='download-server.py')s=once(s,'signal.alarm(182)','signal.alarm(362)');
  if(['start-dallas.mjs','native-client.mjs','owned-load-policy.mjs'].includes(name))s=once(s,'{tcp:8,tcp2:8,tcp3:8,tcp4:8}','{tcp:4,tcp2:4,tcp3:4,tcp4:4}');
  if(name==='start-dallas.mjs')s=once(s,'tcpTargetMbps:config.mbps','tcpTargetMbps:Object.values(config.tcpRates).reduce((a,b)=>a+b,0),tcpCeilingMbps:config.mbps');
  fs.writeFileSync(file,s);q.sourceManifest[file]=hash(Buffer.from(s));
 }
 q.sourceManifest[root+'/fixture-materialize.mjs']=hash(fs.readFileSync(root+'/fixture-materialize.mjs'));
 q.finiteSimulationLimits=fixtureLimits;fs.writeFileSync(runtime+'/entry-qualified.json',JSON.stringify(q,null,2)+'\n');
 return q;
}
export function requireOwnedUpload(config,status,load,at=Date.now()/1000){
 assert.equal(config.seconds,fixtureLimits.client);assert.equal(config.mbps,32);assert.equal(config.pps,50);
 assert.equal(config.bulkDirection,'download');assert.deepEqual(config.tcpRates,{tcp:4,tcp2:4,tcp3:4,tcp4:4});
 assert.equal(status.pid,load.clientPid);assert.equal(status.session,config.session);
 assert.deepEqual(status.perTcpMbps,config.tcpRates);assert.ok(status.tcpBytes>0);
 assert.equal(status.tcpMetric,'client-observed stdout download bytes');assert.equal(status.bulkTransport,'owned native OpenSSH download');
 assert.equal(status.pacerDebtCatchupAllowed,false);assert.equal(status.maximumCombinedPacerCreditBytes,65536);
 assert.ok(status.tcpChildren.length===4&&status.tcpChildren.every(x=>x.connected));
 assert.ok(at-status.at>=0&&at-status.at<2);assert.ok(status.elapsed>=0&&status.elapsed<110);
 return{remainingSeconds:fixtureLimits.client-status.elapsed,finiteIndependentSimulationDeadline:true};
}
export function stopFixture(root){
 assert.match(root,namespacePattern);const q=read(root+'/entry-qualified.json');assert.equal(q.finiteSimulationLimits.client,fixtureLimits.client);
 const pointer=root+'/load-latest-private.json';
 if(!fs.existsSync(pointer)){if(!fs.existsSync(root+'/stop-request.json'))save(root+'/stop-request.json',{stopOwnedTraffic:true});return{requested:true,beforeClientLaunch:true};}
 const load=read(pointer);assert.equal(path.dirname(load.dir),root);assert.ok(load.dir.startsWith(root+'/load-'));
 const config=read(load.dir+'/client-config-private.json');assert.equal(config.seconds,360);assert.equal(config.mbps,32);assert.deepEqual(config.tcpRates,{tcp:4,tcp2:4,tcp3:4,tcp4:4});assert.match(config.session,/^[a-f0-9]{16}$/);
 if(fs.existsSync(load.dir+'/result-private.json'))return{requested:true,clientControlWritten:false,clientAlreadyEnded:true};
 const status=read(load.dir+'/status-private.json');assert.equal(status.pid,load.clientPid);assert.equal(status.session,config.session);
 const target=load.dir+'/control.json',tmp=target+'.stop-'+crypto.randomBytes(4).toString('hex');save(tmp,{session:config.session,stop:true});fs.renameSync(tmp,target);
 if(!fs.existsSync(root+'/stop-request.json'))save(root+'/stop-request.json',{requestedAt:new Date().toISOString(),stopOwnedTraffic:true});
 return{requested:true,clientControlWritten:true,routerWrites:false,forceKillController:false};
}
