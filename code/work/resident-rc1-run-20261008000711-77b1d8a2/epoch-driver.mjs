import{pinNormalOwnership}from'../resident-normal-dev-20261008/normal-policy.mjs';
import{choosePreparationPair}from'../resident-dev-20261007/final-selection.mjs';
import{findExistingSelection}from'../resident-dev-20261007/record-classification.mjs';
import{mapClassifiedPair}from'./class-leaf-map.mjs';
import {auditScopedBaseline} from '../nss160/declared-baseline.mjs';
import {verifyPreparation} from './session-binding.mjs';
import {verifyEpochServices} from '../nss140/service-epoch.mjs';



import {validateAcceleratedState} from './parse-ecm.mjs';
// Bounded owned TCP/UDP pair. Actual permanent classifier and exact native gate.
// Exact single-WAN pair only after native renewal, expiry, acceleration and cleanup qualify.
// Identical queue budget and common observer across A/B/A2. Real offered load and
// game telemetry still need review before any performance conclusion.
import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';import {spawnSync} from 'node:child_process';
import {beginStage,uploadStage,readStage,waitStageUndo} from './module-stage.mjs';
import {connectRouter} from '../nss27/connect-router.mjs';import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
import {readBaseline,auditBaseline} from '../nss15/baseline.mjs';import {packetTemplate} from './wan-tag-plan.mjs';
import {canonicalSelection} from '../nss27/flow-selection.mjs';
import{compactDefaultQueues}from'../nss140/compact-default-queues.mjs';
export async function runEpoch(continuityPath,onDetached,expectedExit=false){
const mode='lifecycle';assert.equal(expectedExit,false);assert.equal(typeof onDetached,'function');
const root='work/nss49', observationRoot='work/resident-rc1-run-20261008000711-77b1d8a2',hash=b=>crypto.createHash('sha256').update(b).digest('hex');
function runNode(file,args=[]){const p=spawnSync(process.execPath,[file,...args],{encoding:'utf8',windowsHide:true,timeout:30000});assert.equal(p.status,0,p.stderr);return p.stdout.trim();}
const preflight=JSON.parse(fs.readFileSync(root+'/mainline-preflight-qualified.json'));assert.equal(preflight.passed,true);assert.equal(preflight.phasedIntegration,true);
verifyPreparation();
const proof=JSON.parse(fs.readFileSync('work/nss27/wan-scope-qualified.json'));assert.equal(proof.passed,true);assert.equal(proof.sourceSha256,hash(fs.readFileSync(root+'/wan-scope.lua')));
runNode(observationRoot+'/read-controlled.mjs');
const candidates=JSON.parse(fs.readFileSync(observationRoot+'/controlled-candidates-private.json'));
const pair=candidates.pairs;
const observed={observedAt:new Date().toISOString(),mode,actualGameCandidates:candidates.udp.length,actualBulkCandidates:candidates.tcp.length,distinctWanPairs:pair.length,routerWrites:false,trafficGenerated:false,openFrontend:false};
if(!pair.length||mode==='inspect'){
 observed.status=pair.length?'TWO_WAN_CONTROLLED_PAIR_VISIBLE_NOT_STARTED':'WAITING_FOR_CONTROLLED_OWNED_PAIR';
 observed.nssPermissionGranted=false;fs.writeFileSync(observationRoot+'/real-session-readiness.json',JSON.stringify(observed,null,2)+'\n');console.log(JSON.stringify(observed));
}else{
 const convert=canonicalSelection;
 let preauditSelected,selected;
  assert.match(continuityPath,/^work\/resident-rc1-run-20261008000711-77b1d8a2\/pilot-aba-\d{14}-[a-f0-9]{16}\/continuity-private\.json$/);
  const continuity=JSON.parse(fs.readFileSync(continuityPath));
  preauditSelected=choosePreparationPair(candidates,continuity.selected.udp);
 verifyPreparation();
 const dir='work/resident-rc1-run-20261008000711-77b1d8a2/session-'+new Date().toISOString().replace(/\D/g,'').slice(0,14)+'-'+crypto.randomBytes(4).toString('hex');fs.mkdirSync(dir);
 const save=(n,v)=>fs.writeFileSync(dir+'/'+n+'.json',(n==='last-record-private'?JSON.stringify(v):JSON.stringify(v,null,2))+'\n');
 // Record owned preparation candidates; final TCP identities freeze before owner creation.
 save('selected-preaudit-private',preauditSelected);
 save('normal-owner-preaudit-private',{candidates,pc:JSON.parse(fs.readFileSync(observationRoot+'/controlled-pc-raw-private.json'))});
 const preauditQualification=verifyPreparation();save('external-source-hashes-preaudit-private',preauditQualification.externalSourceBindings??[]);const preauditManifest={...preauditQualification.sourceManifest};save('source-manifest-preaudit',preauditManifest);
 fs.mkdirSync(dir+'/frozen');for(const [file,digest] of Object.entries(preauditManifest)){assert.equal(hash(fs.readFileSync(file)),digest);const dst=dir+'/frozen/'+file;fs.mkdirSync(dst.slice(0,dst.lastIndexOf('/')),{recursive:true});fs.copyFileSync(file,dst);}
 let c,context,before,completed=false;const failures=[];
 try{
  // Validate the exact current source set, never a historical passing receipt alone.
  for(const [source,proof,key] of [['fast-path.lua','aba-qualified.json','sourceSha256'],['classifier.lua','consumer-qualified.json','adapterSha256']]){const p=JSON.parse(fs.readFileSync(root+'/'+proof));assert.equal(p.passed,true);assert.equal(p[key],hash(fs.readFileSync(root+'/'+source)));}
  runNode('work/resident-rc1-run-20261008000711-77b1d8a2/current-audit-diagnostic.mjs',[dir.split('/').at(-1)+'-before','prewrite',dir]);
  c=await connectRouter();before=await readBaseline(c,dir,'before');verifyEpochServices(JSON.parse(fs.readFileSync(dir+'/service-epoch-private.json')).services,before.services);auditScopedBaseline(JSON.parse(fs.readFileSync(dir+'/prewrite-baseline-private.json')),before);
  // Choose current actual owned BULK candidates after the whole protected audit.
  // Final TCP selection remains confined to verified WANs before detached staging.
  runNode(observationRoot+'/read-controlled.mjs');
  const selectionFrame=JSON.parse(fs.readFileSync(observationRoot+'/controlled-candidates-private.json'));
  assert.equal(selectionFrame.producer,candidates.producer);
  selected=choosePreparationPair(selectionFrame,preauditSelected.udp);
  save('persistent-selection-private',{passed:true,producer:selectionFrame.producer,initialSequence:candidates.sourceSequence,currentSequence:selectionFrame.sourceSequence,selected});
  const source=fs.readFileSync(root+'/read-prerequisites.lua','utf8');const prerequisites=[];
  for(const slot of ['tcp','udp','tcp2']){const f=selected[slot];if(prerequisites.some(q=>q.wan===f.wan))continue;const e=encode("/usr/bin/lua - "+f.wan+" <<'NSS27_REAL_PREREQUISITES'\n"+source+"\nNSS27_REAL_PREREQUISITES\n");const raw=receipt(await c.run(e.command),e);assert.equal(raw.code,0,raw.stderr);const q=JSON.parse(raw.stdout);save('prerequisites-'+slot+'-private',q);assert.equal(q.wan,f.wan);assert.equal(q.status['ipv4-address'][0].address,f.reply.dst);assert.equal(q.status.l3_device,'rpwan'+f.wan);prerequisites.push(q);}
  const bulkScope=[selected.tcp.wan,selected.tcp2.wan];const originalUdp=structuredClone(selected.udp);
  const wan=prerequisites[0];assert.equal(prerequisites[1].boot,wan.boot);assert.equal(prerequisites[1].stateMajor,wan.stateMajor);
  const pin=JSON.parse(fs.readFileSync('work/nss16/qos-capacity-private.json'));const up=JSON.parse(fs.readFileSync('work/nss140/uplink-capacity-private.json'));assert.equal(up.boot,wan.boot);assert.equal(up.device,'wan');assert.equal(up.ifindex,6);assert.equal(pin.boot.trim(),wan.boot);
  const owner=crypto.randomBytes(16).toString('hex');
  const makeInput=(selected,selectionFrame,freeze=false)=>{
  assert.deepEqual(pinNormalOwnership(selectionFrame,selected).udp,continuity.pinnedUdpOwner,'Original UDP process instance changed');
  if(freeze)save('normal-owner-final-private',{selected,owners:pinNormalOwnership(selectionFrame,selected),sourceSequence:selectionFrame.sourceSequence,producer:selectionFrame.producer});
  const frozen=Buffer.from(JSON.stringify({schema:'nss150-controlled-owned-pair-v1',selected,sourceSequence:selectionFrame.sourceSequence,producer:selectionFrame.producer,pcEvidenceSha256:hash(fs.readFileSync(observationRoot+'/controlled-pc-raw-private.json'))}));
  if(freeze){fs.writeFileSync(dir+'/frozen-private.json',frozen,{flag:'wx'});save('selected-private',selected);}
  const values={register_gate:1,diagnostic_only:0};
  for(const [slot,name] of [['tcp','tcp'],['udp','game'],['tcp2','tcp2']]){const f=selected[slot];assert.equal(f.zone,0);assert.ok(Number.isSafeInteger(f.id)&&f.id>0&&f.id<=0xffffffff);assert.equal(f.original.src,'192.168.237.207');assert.equal((f.mark&0xff0000)>>>16,f.wan);assert.equal(f.mark&0x2000,0);
   Object.assign(values,{[name+'_ct_id_raw']:((f.id>>>24)|((f.id>>>8)&0xff00)|((f.id<<8)&0xff0000)|(f.id<<24))>>>0,[name+'_server']:f.original.dst,[name+'_source_port']:f.original.sport,[name+'_server_port']:f.original.dport,[name+'_ct_mark']:f.mark,[name+'_nat_address']:f.reply.dst,[name+'_nat_port']:f.reply.dport});}
  values.frozen_record_sha256=hash(frozen);
  const insmodArguments=Object.entries(values).map(([k,v])=>{assert.match(k,/^[a-z0-9_]+$/);assert.match(String(v),/^[a-f0-9.]+$/);return k+'='+v;}).join(' ');
  const unusedPort=selected.udp.original.sport===59999?59998:59999;
  const classified=mapClassifiedPair(selectionFrame,selected);assert.equal(classified.decisions[0].class,'BULK');assert.equal(classified.decisions[1].class,'RT');assert.equal(classified.decisions[2].class,'BULK');
  save(freeze?'post-checkpoint-class-leaf-map-proof':'initial-class-leaf-map-proof',{passed:true,mappingByActualClass:true,sourceSequence:classified.sourceSequence,sourceAge:classified.sourceAge,producer:classified.producer,nssAdmissionAllowed:false,originalDetachedClassLeaseAndKernelPinStillRequired:true,decisions:classified.decisions.map(({slot,class:category,protocol,upTag,downTag,validUntilUptime})=>({slot,class:category,protocol,upTag,downTag,validUntilUptime}))});
  const template=packetTemplate(classified,owner,unusedPort);
  template.expected.nftables=template.expected.nftables.filter(x=>x.chain?.name!=='forward'&&x.rule?.chain!=='forward');
  const tagPlan={table:template.expected.nftables[0].table.name,owner,mode:'rt',expected:template.expected,wanLeafAssignments:template.wanLeafAssignments};
  return {mode:'stage',openFrontend:true,wanPrerequisites:{boot:wan.boot,members:prerequisites.map(q=>({w:q.wan,pid:q.auth.pid,start:q.auth.start,failure:q.auth.failure,index:q.mode[0].ifindex,mac:q.mode[0].address,link:q.mode[0].link,ip:q.status['ipv4-address'][0].address}))},stateMajor:wan.stateMajor,frozenHash:hash(frozen),insmodArguments,autoClassified:true,selected,tagPlan,qosStaged:true,qosDevice:'lan4',qosTc:pin.tc,qosModule:pin.qdiscModule,qosBaseline:compactDefaultQueues(pin.interfaces.lan4.qdiscs),qosBoot:wan.boot,uplinkDevice:'wan',uplinkIfindex:6,uplinkPhysicalAeId:5,uplinkBaseline:compactDefaultQueues(up.defaultQueues)};
  };
  // Refresh real application ownership before any checkpoint or staging operation.
  runNode(observationRoot+'/read-controlled.mjs');const fresh=JSON.parse(fs.readFileSync(observationRoot+'/controlled-candidates-private.json'));
  assert.equal(fresh.producer,candidates.producer);assert.ok(fresh.sourceSequence>=candidates.sourceSequence);
  selected=choosePreparationPair(fresh,originalUdp,bulkScope);
  const manifest={...verifyPreparation().sourceManifest};for(const file of ['work/nss39/pair-policy.mjs','work/nss49/real-session.mjs','work/nss49/session-binding.mjs','work/nss49/read-real-candidates.mjs','work/nss49/record-candidates.mjs','work/nss49/current-audit-diagnostic.mjs','work/nss49/audit-renderer.mjs','work/nss27/flow-selection.mjs'])manifest[file]=hash(fs.readFileSync(file));save('source-manifest',manifest);
  context=await beginStage(makeInput(selected,fresh),dir,async provisional=>{
   // Syntax and the downloaded checkpoint are complete. Select the TCP now,
   // before the independent stage begins; an existing gate is never retargeted.
   verifyPreparation();runNode(observationRoot+'/read-controlled.mjs');
   const frame=JSON.parse(fs.readFileSync(observationRoot+'/controlled-candidates-private.json'));
   assert.equal(frame.producer,selectionFrame.producer);assert.ok(frame.sourceSequence>=selectionFrame.sourceSequence);selected=choosePreparationPair(frame,originalUdp,bulkScope);
   const refined=makeInput(selected,frame,true);
   refined.classifierOwner=provisional.classifierOwner;
   save('post-checkpoint-controlled-receipt-private',frame);
   return refined;
  });
  await onDetached(context);await uploadStage(context);let latest;
  for(let i=0;i<115;i++){const s=await readStage(c,context);if(s.record){latest=s.record;save('last-record-private',latest);}if(!s.directoryPresent)break;await new Promise(r=>setTimeout(r,1700));}
  await waitStageUndo(context);assert.ok(latest,'No bounded-owner receipt');assert.equal(latest.error,undefined,latest.error);
  for(const key of ['automaticLifecycleEpochCompleted','unchangedQoSPlan','fastPathEpochCompleted','explicitEarlyRetirement','firmwareZeroAfterRetirement','tagsRemoved','qosRestored','qosModuleUnloaded','dualPhysicalQueuesReady','dualPhysicalQueuesRestored','wanRestored','mwan3Restored','stateNodeRemoved'])assert.equal(latest[key],true,key);
  assert.equal(latest.abaCompleted,false);assert.equal(latest.fastPathMeasurement.qualified,true,latest.fastPathMeasurement.reason);assert.ok(latest.renewals.length>0);assert.deepEqual(latest.phases.map(p=>p.name),['B']);for(const p of latest.phases){assert.ok(p.completed&&p.seconds>=90&&p.seconds<=91.5&&p.sampleCount>=178);for(const t of latest.samples.slice(p.sampleStart-1,p.sampleEnd)){assert.equal(t.phase,p.name);assert.equal(t.counts['ecm_nss_ipv4/accelerated_count'],p.name==='B'?3:0);}}
  save('actual-accelerated-state-proof',validateAcceleratedState(latest.acceleratedState,selected));
  save('functional-runtime-proof',{passed:true,observedAt:new Date().toISOString(),realCs2SteamPair:false,controlledRealWanPair:false,normalProcessOwnedFlowPair:true,naturalWanSet:[...new Set(Object.values(selected).map(f=>f.wan))],twoTcpBulkOneUdpRt:true,nativeRenewal:true,firmwareZero:true,cleanupVerified:true,automaticLifecycleEpoch:true,matchedForwardingABA:false,offeredGameSteamLoadEqualityRequiresReview:true,highLoadCpuBenefitConclusion:false,gameQualityConclusion:false,selectedSubgroupCeilingMbps:18,selectedUplinkSubgroupCeilingMbps:60,unselectedPhysicalFallbackMbps:950});
  completed=true;
 }catch(error){failures.push(String(error));save('controller-error',{error:String(error),stack:String(error.stack)});process.exitCode=1;}
 finally{
  if(context)try{await waitStageUndo(context);}catch(e){failures.push('cleanup: '+String(e));process.exitCode=1;}
  if(before&&c)try{const after=await readBaseline(c,dir,'after');runNode('work/resident-rc1-run-20261008000711-77b1d8a2/current-audit-diagnostic.mjs',[dir.split('/').at(-1)+'-after','recovery',dir]);save('baseline-audit',auditScopedBaseline(before,after));}catch(e){failures.push('baseline: '+String(e));process.exitCode=1;}
  c?.close();save('result',{passed:completed&&failures.length===0,mode:'lifecycle',controlledOwnerRequired:true,trafficGenerated:false,matchedForwardingABARequested:false,matchedForwardingABACompleted:false,classLifecycleCompleted:completed&&expectedExit==='change',automaticLifecycleEpochCompleted:completed&&failures.length===0,flowEligibilityExitCompleted:completed&&expectedExit,gameQualityConclusion:false,errors:failures});
  return {passed:completed&&failures.length===0,mode:'lifecycle',output:dir,errors:failures};
 }
}

}
