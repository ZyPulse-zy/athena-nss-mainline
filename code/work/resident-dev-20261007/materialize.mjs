import{patchFinalDriver,patchFinalStage}from'./final-selection.mjs';
import{patchSelectedAcquisition}from'./selected-acquisition.mjs';
import{patchAcquisitionOrder}from'./acquisition-order.mjs';
import{patchUdpDiscovery}from'./udp-discovery.mjs';
import{patchEligibleReader,patchEligibleMatcher}from'./eligible-selection.mjs';
import{patchFullReader}from'./full-classification.mjs';
import{patchControlledReader,patchNaturalAcquisition,patchMatcher}from'./route-acquisition.mjs';
import{patchResidentWindow}from'./resident-window.mjs';
import{compactSshOptions}from'./ssh-options.mjs';
import{instrumentNativeClient}from'./ssh-phase.mjs';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {verifyPreparation as inherited} from '../v42-counter-window/session-binding.mjs';

export const entryRoot='work/resident-dev-20261007';
export const sourceRoot='work/v42-counter-window';
export const threeRoot='work/v20-five';
const planeNames=new Set(['candidate-policy.mjs','class-leaf-map.mjs','classified-tags.lua','classifier.lua','epoch-driver.mjs','fast-path.lua','guardian-plan.mjs','module-stage-guardian.lua','module-stage.mjs','parse-ecm.mjs','payload.mjs','qos-physical.lua','tag-normalizer.lua','wan-scope.lua','wan-tag-plan.mjs','qos-native-qualified.json','normalizer-qualified.json','native-qualified.json']);
export const limits=Object.freeze({source:6,kernel:120,kernelMaximum:120,owner:180,client:180,clientGuard:210,server:250,phase:90,tcpMbps:32,downMbps:18,upMbps:60,perWanUpMbps:12,credit:65536,exec:9000,raw:65536,bundle:73728,record:1048576});
export const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
export const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
export const save=(p,v)=>fs.writeFileSync(p,JSON.stringify(v,null,2)+'\n',{flag:'wx'});
export const namespacePattern=/^work\/resident-rc1-run-\d{14}-[a-f0-9]{8}$/;
const oncePilot=(s,a,b)=>{assert.equal(s.split(a).length,2,a);return s.replace(a,b);};
const skipped=new Set(['prepare.py','qualify-entry.mjs','session-binding.mjs','analyze-v41-window.py','v41-aligned-window.json']);
export function inspection(){
 const base=inherited();assert.equal(Object.keys(base.sourceManifest).length,3354);
 const hardware=read('athena-nss-mainline/evidence/v42-five-wan-hardware.json');
 assert.ok(hardware.passed&&hardware.fiveWanBoundedHardwareAcceptance);assert.equal(hardware.renewals,20);
 const q=read(sourceRoot+'/entry-qualified.json');
 for(const name of ['fast-path.lua','classifier.lua','classified-tags.lua','module-stage-guardian.lua','qos-physical.lua','wan-scope.lua','tag-normalizer.lua'])assert.equal(hash(fs.readFileSync(sourceRoot+'/'+name)),q.sourceManifest[sourceRoot+'/'+name],name);
 return {passed:true,inheritedBindings:3354,mode:'inspect',routerWrites:false,trafficGenerated:false,desktopOperated:false,liveNetworkAudited:false,hardwareBasis:'v20-three-flow-and-v42-five-wan',simulatedGamePackets:true,boundedResidentCandidate:true,permanentNssDeployment:false,limits};
}
export function materialize(runtimeRoot,cutoff){
 assert.match(runtimeRoot,namespacePattern);assert.ok(Number.isFinite(cutoff)&&cutoff>Date.now()+300000&&cutoff<=Date.now()+900000,'Fresh cutoff must retain restoration margin within fifteen minutes');
 const base=inherited(),q=read(sourceRoot+'/entry-qualified.json');inspection();
 assert.ok(!fs.existsSync(runtimeRoot),'Fresh namespace required');fs.mkdirSync(runtimeRoot);
 const originHashes={},generatedHashes={},rebase=s=>s.replaceAll('work\\/v42-counter-window\\/',runtimeRoot.replaceAll('/','\\/')+'\\/').replaceAll(sourceRoot,runtimeRoot).replaceAll('work\\/v20-five\\/',runtimeRoot.replaceAll('/','\\/')+'\\/').replaceAll(threeRoot,runtimeRoot).replaceAll('v42-counter-window-',runtimeRoot.slice(5)+'-').replaceAll('v42-final',runtimeRoot.slice(5)+'-final');
 for(const [origin,digest] of Object.entries(q.sourceManifest)){
  const name=path.basename(origin);if(skipped.has(name))continue;
  let original=fs.readFileSync(origin);assert.equal(hash(original),digest,origin);originHashes[origin]=digest;
  if(planeNames.has(name)){const origin3=threeRoot+'/'+name,q3=read(threeRoot+'/entry-qualified.json');assert.equal(q3.passed,true);original=fs.readFileSync(origin3);assert.equal(hash(original),q3.sourceManifest[origin3],origin3);originHashes[origin3]=hash(original);}
  let bytes=['.json','.lua'].includes(path.extname(name))?original:Buffer.from(rebase(original.toString('utf8')));
  if(name==='fast-path.lua'){bytes=Buffer.from(patchResidentWindow(bytes.toString()));}
  if(name==='epoch-driver.mjs'){let s=bytes.toString();
   s="import{findExistingSelection}from'../resident-dev-20261007/record-classification.mjs';\n"+s;
   assert.equal(s.split('const preauditSelected=pair[0];let selected;').length,2);s=s.replace('const preauditSelected=pair[0];let selected;','let preauditSelected,selected;');
   const initial="assert.deepEqual(preauditSelected,continuity.selected,'Automatic successor changed original CT/socket pair');";assert.equal(s.split(initial).length,2);s=s.replace(initial,"preauditSelected=findExistingSelection(pair,continuity.selected);assert.ok(preauditSelected,'Original admitted CT/socket triple is no longer eligible');");
  s=s.replace('p.seconds>=60&&p.seconds<=61.5&&p.sampleCount>=118','p.seconds>=90&&p.seconds<=91.5&&p.sampleCount>=178');bytes=Buffer.from(s);}
  if(name==='epoch-driver.mjs')bytes=Buffer.from(patchFinalDriver(bytes.toString()));
  if(name==='module-stage.mjs')bytes=Buffer.from(patchFinalStage(bytes.toString()));
  if(name==='native-client.mjs'){
   let s=bytes.toString('utf8');const serial="stamp();for(const slot of ['tcp','tcp2','tcp3','tcp4']){if(ended)break;await startTcp(slot,1);while(!ended&&!stats.tcpChildren.find(x=>x.slot===slot).connected){if((performance.now()-began)/1000>=30){finish('Finite initial TCP acquisition window ended');break;}await new Promise(r=>setTimeout(r,25));}}";
   assert.equal(s.split(serial).length,2,'Original serial initial SSH startup must match');
   s="import{launchInitialFour}from'../resident-dev-20261007/fixture-startup.mjs';\n"+s.replace(serial,"stamp();await launchInitialFour(startTcp,()=>ended);");
   assert.equal(s.split('s.attempt=attempt;s.connected=false;').length,2);s=s.replace('s.attempt=attempt;s.connected=false;','s.attempt=attempt;s.connected=false;s.bytes=0;');s=instrumentNativeClient(s);s="import{compactSshOptions}from'../resident-dev-20261007/ssh-options.mjs';\n"+s;s=s.replace("spawn(sshExe,['-v','-o'","spawn(sshExe,['-v',...compactSshOptions,'-o'");bytes=Buffer.from(s);
  }
  if(name==='wait-four-ssh.mjs'){
   let s=bytes.toString('utf8');const prior="s.tcpChildren.every(x=>x.connected&&Number.isInteger(x.ownerPid)&&x.bytes>0)&&Date.now()/1000-s.at<2";
   assert.equal(s.split(prior).length,2);
   s="import{fourOwnedPidsReady}from'../resident-dev-20261007/fixture-startup.mjs';\n"+s.replace(prior,"fourOwnedPidsReady(s,Date.now()/1000)").replace('fourOwnedSshChildrenReady:true','fourOwnedSshPidsPublished:true,payloadAndClassificationStillRequired:true').replace('all handshakes completed','four owned child PIDs were published').replace('fixture handshakes exceeded readiness bound','fixture PID publication exceeded readiness bound');
   bytes=Buffer.from(s);
  }
  if(name==='start-dallas.mjs'){let s=bytes.toString();const needle="const literal=x=>";assert.equal(s.split(needle).length,2);s=s.replace(needle,"fs.writeFileSync(root+'/endpoint-setup-private.json',JSON.stringify({dir,unit,clientLaunchNotRequested:true})+'\\n',{flag:'wx'});const udpProof=spawnSync(process.execPath,[root+'/check-udp-path.mjs',dir],{encoding:'utf8',windowsHide:true,timeout:13000,maxBuffer:65536});save('udp-path-command-private',{code:udpProof.status,stdout:udpProof.stdout,stderr:udpProof.stderr});assert.equal(udpProof.status,0,'UDP echo preflight refused before client; original output retained');\n"+needle);bytes=Buffer.from(s);}
  if(name==='start-dallas.mjs'){let s=bytes.toString();const late="fs.writeFileSync(root+'/endpoint-setup-private.json',JSON.stringify({dir,unit,clientLaunchNotRequested:true})+'\\n',{flag:'wx'});",server="await ssh('systemd-run --unit='+unit",fw="const raw=await ssh('python3 -B -E -s -u -',guardian+";assert.equal(s.split(late).length,2);assert.equal(s.split(server).length,2);assert.equal(s.split(fw).length,2);s=s.replace(late,'').replace(server,"save('server-launch-intent-private',{at:new Date().toISOString(),unit,serverConfig:conf,sourceSha256:hash(serverSource),independentOsDeadlineSeconds:250});fs.writeFileSync(root+'/endpoint-setup-private.json',JSON.stringify({dir,unit,clientLaunchNotRequested:true})+'\\n',{flag:'wx'});"+server).replace(fw,"save('firewall-launch-intent-private',{at:new Date().toISOString(),independentExpirySeconds:180});"+fw);bytes=Buffer.from(s);}
  if(name==='start-dallas.mjs')bytes=Buffer.from(patchUdpDiscovery(bytes.toString()));
  if(name==='start-dallas.mjs'){
   let s=bytes.toString();s="import{preferredPort}from'../resident-dev-20261007/udp-seed.mjs';\n"+oncePilot(s,'const seededUdpPort=59000+crypto.randomInt(800);','const seededUdpPort=preferredPort();');bytes=Buffer.from(s);
  }
  if(name==='persistent-ssh.mjs'){bytes=fs.readFileSync(entryRoot+'/persistent-ssh.mjs');}
  if(name==='read-controlled.mjs'){bytes=Buffer.from(patchEligibleReader(patchFullReader(patchControlledReader(bytes.toString()))));}
  if(name==='acquisition-plan.mjs'){bytes=Buffer.from(patchNaturalAcquisition(bytes.toString()));}
  if(name==='match-controlled.mjs'){bytes=Buffer.from(patchSelectedAcquisition(patchAcquisitionOrder(patchEligibleMatcher(patchMatcher(bytes.toString())))));}
  if(name==='pilot-supervisor.mjs'){
   let s=bytes.toString('utf8');assert.equal(s.split('2026-10-07T10:00:00Z').length,2);
   s=s.replace('2026-10-07T10:00:00Z',new Date(cutoff).toISOString());
   s=oncePilot(s,'assert.ok(selected&&new Set(Object.values(selected).map(f=>f.wan)).size===5);','assert.ok(selected&&Object.keys(selected).length===3&&selected.tcp.wan!==selected.tcp2.wan);');
   s=s.replaceAll('fiveExactFlows:true','threeEligibleExactFlows:true').replaceAll('fiveExactFlowMultiWanFunctionalAcceptance:true','threeEligibleFlowMultiWanResidentTrial:true');
   s=s.replace('lifetime.remainingSeconds>=130','lifetime.remainingSeconds>=160').replace('record.phases[0].seconds>=60','record.phases[0].seconds>=90').replaceAll('oneSixtySecondSessionCompleted','oneNinetySecondResidentTrialCompleted').replaceAll('sixtySecondHardwareSessionCompleted','ninetySecondResidentTrialCompleted').replace('nativeSessionCapSeconds:120','nativeSessionCapSeconds:120,routerDetachedClassLeaseController:true,originalKernelMaximumKept:true').replace('oneSixtySecondSessionCompleted','oneNinetySecondResidentTrialCompleted');
   s=s.replace("const read=(d,n)=>", "const checkStop=()=>assert.ok(!fs.existsSync(root+'/stop-request.json'),'Operator requested stop before next admission');\nconst read=(d,n)=>");
   for(const needle of ["save('load-reference-private',await run", "await run(root+'/match-controlled.mjs');", "const trial=await runEpoch"]){assert.equal(s.split(needle).length,2,needle);s=s.replace(needle,'checkStop();'+needle);}
   bytes=Buffer.from(s);
  }
  if(name!=='persistent-ssh.mjs'&&path.extname(name)==='.mjs'&&/spawn(?:Sync)?\('ssh',\[/.test(bytes.toString())){let s=bytes.toString();s="import{compactSshOptions}from'../resident-dev-20261007/ssh-options.mjs';\n"+s;s=s.replaceAll("spawn('ssh',[","spawn('ssh',[...compactSshOptions,").replaceAll("spawnSync('ssh',[","spawnSync('ssh',[...compactSshOptions,");bytes=Buffer.from(s);}
  if(path.extname(name)==='.mjs')bytes=Buffer.from(bytes.toString().replaceAll('../nss68/deployment-binding.mjs','../resident-dev-20261007/deployment-binding.mjs').replaceAll('../nss122/wait-publication-metadata.mjs','../resident-dev-20261007/wait-publication-metadata.mjs'));
  if(name==='current-audit-diagnostic.mjs'){
   let s=bytes.toString().replaceAll('\r\n','\n');s=oncePilot(s,"['prewrite','recovery'].includes(purpose)","['prewrite','recovery','final'].includes(purpose)");
   s=oncePilot(s,"if(purpose==='prewrite'){\n  assert.ok(!fs.existsSync(refPath)","if(purpose!=='recovery'){\n  assert.ok(!fs.existsSync(refPath)");
   s=oncePilot(s,'hint=await waitReady(c,ctx,label);',"if(purpose==='prewrite')hint=await waitReady(c,ctx,label);");bytes=Buffer.from(s);
  }
  if(name==='read-final-health.mjs')bytes=Buffer.from(oncePilot(bytes.toString(),"-final','prewrite',dir","-final','final',dir"));
  fs.writeFileSync(runtimeRoot+'/'+name,bytes,{flag:'wx'});generatedHashes[runtimeRoot+'/'+name]=hash(bytes);
 }
 const recheck=fs.readFileSync(entryRoot+'/recheck-endpoint-readonly.mjs','utf8').replaceAll('__RUNTIME__',runtimeRoot);fs.writeFileSync(runtimeRoot+'/recheck-endpoint-readonly.mjs',recheck,{flag:'wx'});generatedHashes[runtimeRoot+'/recheck-endpoint-readonly.mjs']=hash(Buffer.from(recheck));
 for(const name of ['udp-probe.py','udp-probe.mjs','check-udp-path.mjs','recheck-partial-endpoint.mjs','capture-no-client-closure.ps1']){const source=fs.readFileSync(entryRoot+'/'+name,'utf8').replaceAll('__RUNTIME__',runtimeRoot);fs.writeFileSync(runtimeRoot+'/'+name,source,{flag:'wx'});generatedHashes[runtimeRoot+'/'+name]=hash(Buffer.from(source));}
 const binding=`import fs from'node:fs';import crypto from'node:crypto';import assert from'node:assert/strict';import{verifyPreparation as inherited}from'../v42-counter-window/session-binding.mjs';\nexport function verifyPreparation(){const old=inherited(),q=JSON.parse(fs.readFileSync('${runtimeRoot}/entry-qualified.json'));assert.ok(q.passed&&!q.hardwareExecuted);for(const[f,h]of Object.entries(q.sourceManifest))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex'),h,f);return{...old,sourceManifest:{...old.sourceManifest,...q.sourceManifest},externalSourceBindings:old.externalSourceBindings};}\n`;
 fs.writeFileSync(runtimeRoot+'/session-binding.mjs',binding,{flag:'wx'});generatedHashes[runtimeRoot+'/session-binding.mjs']=hash(Buffer.from(binding));
 for(const name of ['final-selection.mjs','selected-acquisition.mjs','acquisition-order.mjs','record-classification.mjs','udp-discovery.mjs','eligible-selection.mjs','full-classification.mjs','prepare.mjs','entry.mjs','materialize.mjs','check-model.mjs','platform-preflight.mjs','fixture-startup.mjs','ssh-phase.mjs','ssh-options.mjs','recheck-endpoint-readonly.mjs','udp-probe.py','udp-probe.mjs','check-udp-path.mjs','recheck-partial-endpoint.mjs','capture-no-client-closure.ps1','persistent-ssh.mjs','resident-window.mjs','route-acquisition.mjs','check-route-acquisition.mjs'])generatedHashes[entryRoot+'/'+name]=hash(fs.readFileSync(entryRoot+'/'+name));
 for(const name of ['classifier-core.lua','classifier-build.json','build-classifier.mjs','deployment-binding.mjs','classifier-tests-latest.json','core-deployment-plan.mjs','core-remote.mjs','core-workflow.mjs','deploy-core.mjs','test-core-plan.mjs','test-deployment-binding.mjs','lua-local.mjs','deployment-plan-tests-latest.json','wait-ready-candidate.mjs','wait-publication-metadata.mjs','udp-seed.mjs','udp-preferred-port.json','learning-alignment.mjs','test-learning-alignment.mjs'])generatedHashes[entryRoot+'/'+name]=hash(fs.readFileSync(entryRoot+'/'+name));
 for(const [p,digest] of Object.entries(generatedHashes)){
  assert.equal(hash(fs.readFileSync(p)),digest,p);
  if(p.endsWith('.mjs')){const r=spawnSync(process.execPath,['--check',p],{encoding:'utf8',windowsHide:true});assert.equal(r.status,0,r.stderr);}
 }
 for(const name of ['classifier.lua','classified-tags.lua','module-stage-guardian.lua','qos-physical.lua','wan-scope.lua','tag-normalizer.lua'])assert.deepEqual(fs.readFileSync(runtimeRoot+'/'+name),fs.readFileSync(threeRoot+'/'+name),name);assert.equal(fs.readFileSync(runtimeRoot+'/fast-path.lua','utf8'),patchResidentWindow(fs.readFileSync(threeRoot+'/fast-path.lua','utf8')));
 const result={passed:true,hardwareExecuted:false,sourceManifest:generatedHashes,inheritedBindings:Object.keys(base.sourceManifest).length,actualBindings:Object.keys({...base.sourceManifest,...generatedHashes}).length,originHashes,dataPlaneByteExact:false,residentLifetimeOnlyChange:false,closedLearningRaceCorrection:true,threeFlowDataPlaneReused:true,unqualifiedFlowsStaySoftware:true,sixCoreLuaSourcesByteExact:true,nativeGateByteExact:true,rtAndQosPolicyUnchanged:true,tcpBulkShapeCorrection:true,limits,cutoff:new Date(cutoff).toISOString(),singleExplicitSession:true};
 save(runtimeRoot+'/entry-qualified.json',result);return result;
}
export function stopRequest(root){
 assert.match(root,namespacePattern);assert.ok(fs.existsSync(root+'/entry-qualified.json'));
 if(!fs.existsSync(root+'/stop-request.json'))save(root+'/stop-request.json',{requestedAt:new Date().toISOString(),stopOwnedTraffic:true,independentRestorationStillRequired:true});
 const pointer=root+'/load-latest-private.json';if(!fs.existsSync(pointer))return {requested:true,clientControlWritten:false,beforeClientLaunch:true};
 const load=read(pointer);assert.ok(load.dir.startsWith(root+'/load-'));assert.equal(path.dirname(load.dir),root);
 const config=read(load.dir+'/client-config-private.json');assert.equal(config.seconds,limits.client);assert.equal(config.mbps,limits.tcpMbps);assert.match(config.session,/^[a-f0-9]{16}$/);
 if(fs.existsSync(load.dir+'/result-private.json'))return {requested:true,clientControlWritten:false,clientAlreadyEnded:true};
 const status=read(load.dir+'/status-private.json');assert.equal(status.pid,load.clientPid);assert.equal(status.session,config.session);
 const target=load.dir+'/control.json',tmp=target+'.stop-'+crypto.randomBytes(4).toString('hex');save(tmp,{session:config.session,stop:true});fs.renameSync(tmp,target);
 return {requested:true,clientControlWritten:true,routerWrites:false,forceKillController:false,restorationConfirmed:false};
}
