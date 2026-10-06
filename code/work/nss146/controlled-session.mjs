import{mapClassifiedPair}from'../nss127/class-leaf-map.mjs';
import {auditScopedBaseline} from '../nss140/declared-baseline.mjs';
import {verifyPreparation} from './session-binding.mjs';
import {verifyEpochServices} from '../nss140/service-epoch.mjs';



import {validateAcceleratedState} from '../nss140/parse-ecm-any-wan.mjs';
// Bounded owned TCP/UDP pair. Actual permanent classifier and exact native gate.
// Exact single-WAN pair only after native renewal, expiry, acceleration and cleanup qualify.
// Identical queue budget and common observer across A/B/A2. Real offered load and
// game telemetry still need review before any performance conclusion.
import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';import {spawnSync} from 'node:child_process';
import {beginStage,uploadStage,readStage,waitStageUndo} from './module-stage.mjs';
import {connectRouter} from '../nss27/connect-router.mjs';import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
import {readBaseline,auditBaseline} from '../nss15/baseline.mjs';import {packetTemplate} from '../nss140/uplink-tag-plan.mjs';
import {canonicalSelection} from '../nss27/flow-selection.mjs';
import{compactDefaultQueues}from'../nss140/compact-default-queues.mjs';
const mode=process.argv[2]??'inspect';assert.ok(['inspect','aba'].includes(mode));
const root='work/nss49', observationRoot='work/nss146',hash=b=>crypto.createHash('sha256').update(b).digest('hex');
function runNode(file,args=[]){const p=spawnSync(process.execPath,[file,...args],{encoding:'utf8',windowsHide:true,timeout:30000});assert.equal(p.status,0,p.stderr);return p.stdout.trim();}
const preflight=JSON.parse(fs.readFileSync(root+'/mainline-preflight-qualified.json'));assert.equal(preflight.passed,true);assert.equal(preflight.phasedIntegration,true);
verifyPreparation();
const proof=JSON.parse(fs.readFileSync('work/nss27/wan-scope-qualified.json'));assert.equal(proof.passed,true);assert.equal(proof.sourceSha256,hash(fs.readFileSync(root+'/wan-scope.lua')));
runNode(observationRoot+'/read-controlled.mjs');
const candidates=JSON.parse(fs.readFileSync(observationRoot+'/controlled-candidates-private.json'));
const pair=candidates.pairs;
const observed={observedAt:new Date().toISOString(),mode,actualGameCandidates:candidates.udp.length,actualBulkCandidates:candidates.tcp.length,sameWanPairs:pair.length,routerWrites:false,trafficGenerated:true,openFrontend:false};
if(!pair.length||mode==='inspect'){
 observed.status=pair.length?'SINGLE_WAN_CONTROLLED_PAIR_VISIBLE_NOT_STARTED':'WAITING_FOR_CONTROLLED_OWNED_PAIR';
 observed.nssPermissionGranted=false;fs.writeFileSync(observationRoot+'/real-session-readiness.json',JSON.stringify(observed,null,2)+'\n');console.log(JSON.stringify(observed));
}else{
 const convert=canonicalSelection;
 const preauditSelected=pair[0];let selected;
 verifyPreparation();
 const dir='work/nss146/controlled-matched-aba-'+new Date().toISOString().replace(/\D/g,'').slice(0,14)+'-'+crypto.randomBytes(4).toString('hex');fs.mkdirSync(dir);
 const save=(n,v)=>fs.writeFileSync(dir+'/'+n+'.json',JSON.stringify(v,null,2)+'\n');
 // Freeze identity and exact application observation before the first audit.
 save('selected-preaudit-private',preauditSelected);
 const load=JSON.parse(fs.readFileSync(observationRoot+'/load-latest-private.json'));
 save('controlled-client-private',{load,candidates,config:JSON.parse(fs.readFileSync(load.dir+'/client-config-private.json'))});
 const preauditQualification=verifyPreparation();save('external-source-hashes-preaudit-private',preauditQualification.externalSourceBindings??[]);const preauditManifest={...preauditQualification.sourceManifest};save('source-manifest-preaudit',preauditManifest);
 fs.mkdirSync(dir+'/frozen');for(const [file,digest] of Object.entries(preauditManifest)){assert.equal(hash(fs.readFileSync(file)),digest);const dst=dir+'/frozen/'+file;fs.mkdirSync(dst.slice(0,dst.lastIndexOf('/')),{recursive:true});fs.copyFileSync(file,dst);}
 let c,context,before,completed=false;const failures=[];
 try{
  // Validate the exact current source set, never a historical passing receipt alone.
  for(const [source,proof,key] of [['fast-path.lua','aba-qualified.json','sourceSha256'],['classifier.lua','consumer-qualified.json','adapterSha256']]){const p=JSON.parse(fs.readFileSync(root+'/'+proof));assert.equal(p.passed,true);assert.equal(p[key],hash(fs.readFileSync(root+'/'+source)));}
  runNode('work/nss146/current-audit-diagnostic.mjs',[dir.split('/').at(-1)+'-before','prewrite',dir]);
  c=await connectRouter();before=await readBaseline(c,dir,'before');verifyEpochServices(JSON.parse(fs.readFileSync(dir+'/service-epoch-private.json')).services,before.services);auditScopedBaseline(JSON.parse(fs.readFileSync(dir+'/prewrite-baseline-private.json')),before);
  // Choose only application-owned identities visible both before and after the
  // full audit. The native gate still pins one exact TCP and UDP for the epoch.
  runNode(observationRoot+'/read-controlled.mjs');
  const selectionFrame=JSON.parse(fs.readFileSync(observationRoot+'/controlled-candidates-private.json'));
  assert.equal(selectionFrame.producer,candidates.producer);
  selected=selectionFrame.pairs.find(p=>JSON.stringify(p)===JSON.stringify(preauditSelected));
  assert.ok(selected,'Controlled exact pair changed after original full audit');assert.notEqual(selected.tcp.wan,4,'Failed WAN4 cannot enter controlled NSS');
  save('persistent-selection-private',{passed:true,producer:selectionFrame.producer,initialSequence:candidates.sourceSequence,currentSequence:selectionFrame.sourceSequence,selected});
  const source=fs.readFileSync(root+'/read-prerequisites.lua','utf8');const e=encode("/usr/bin/lua - "+selected.tcp.wan+" <<'NSS27_REAL_PREREQUISITES'\n"+source+"\nNSS27_REAL_PREREQUISITES\n");
  const r=receipt(await c.run(e.command),e);assert.equal(r.code,0,r.stderr);const wan=JSON.parse(r.stdout);save('prerequisites-private',wan);
  assert.equal(wan.status['ipv4-address'][0].address,selected.tcp.reply.dst);assert.equal(wan.status.l3_device,'rpwan'+selected.tcp.wan);
  const pin=JSON.parse(fs.readFileSync('work/nss16/qos-capacity-private.json'));const up=JSON.parse(fs.readFileSync('work/nss140/uplink-capacity-private.json'));assert.equal(up.boot,wan.boot);assert.equal(up.device,'wan');assert.equal(up.ifindex,6);assert.equal(pin.boot.trim(),wan.boot);
  const owner=crypto.randomBytes(16).toString('hex');
  const makeInput=(selected,selectionFrame,freeze=false)=>{
  const frozen=Buffer.from(JSON.stringify({schema:'nss146-controlled-owned-pair-v1',selected,sourceSequence:selectionFrame.sourceSequence,producer:selectionFrame.producer,pcEvidenceSha256:hash(fs.readFileSync(observationRoot+'/controlled-pc-raw-private.json'))}));
  if(freeze){fs.writeFileSync(dir+'/frozen-private.json',frozen,{flag:'wx'});save('selected-private',selected);}
  const values={register_gate:1,diagnostic_only:0};
  for(const [slot,name] of [['tcp','tcp'],['udp','game']]){const f=selected[slot];assert.equal(f.zone,0);assert.ok(Number.isSafeInteger(f.id)&&f.id>0&&f.id<=0xffffffff);assert.equal(f.original.src,'192.168.237.207');assert.equal((f.mark&0xff0000)>>>16,f.wan);assert.equal(f.mark&0x2000,0);
   Object.assign(values,{[name+'_ct_id_raw']:((f.id>>>24)|((f.id>>>8)&0xff00)|((f.id<<8)&0xff0000)|(f.id<<24))>>>0,[name+'_server']:f.original.dst,[name+'_source_port']:f.original.sport,[name+'_server_port']:f.original.dport,[name+'_ct_mark']:f.mark,[name+'_nat_address']:f.reply.dst,[name+'_nat_port']:f.reply.dport});}
  values.frozen_record_sha256=hash(frozen);
  const insmodArguments=Object.entries(values).map(([k,v])=>{assert.match(k,/^[a-z0-9_]+$/);assert.match(String(v),/^[a-f0-9.]+$/);return k+'='+v;}).join(' ');
  const unusedPort=selected.udp.original.sport===59999?59998:59999;
  const classified=mapClassifiedPair(selectionFrame,selected);assert.equal(classified.decisions[0].class,'BULK');assert.equal(classified.decisions[1].class,'RT');
  save(freeze?'post-checkpoint-class-leaf-map-proof':'initial-class-leaf-map-proof',{passed:true,mappingByActualClass:true,sourceSequence:classified.sourceSequence,sourceAge:classified.sourceAge,producer:classified.producer,nssAdmissionAllowed:false,originalDetachedClassLeaseAndKernelPinStillRequired:true,decisions:classified.decisions.map(({slot,class:category,protocol,upTag,downTag,validUntilUptime})=>({slot,class:category,protocol,upTag,downTag,validUntilUptime}))});
  const template=packetTemplate(classified,owner,unusedPort);
  template.expected.nftables=template.expected.nftables.filter(x=>x.chain?.name!=='forward'&&x.rule?.chain!=='forward');
  const tagPlan={table:template.expected.nftables[0].table.name,owner,mode:'rt',expected:template.expected};
  return {mode:'stage',openFrontend:true,wanPrerequisites:{wan:wan.wan,boot:wan.boot,auth:wan.auth,mode:wan.mode.map(x=>({ifindex:x.ifindex,address:x.address,link_index:x.link_index})),status:{up:wan.status.up,l3_device:wan.status.l3_device,'ipv4-address':wan.status['ipv4-address']}},stateMajor:wan.stateMajor,frozenHash:hash(frozen),insmodArguments,autoClassified:true,selected,tagPlan,qosStaged:true,qosDevice:'lan4',qosTc:pin.tc,qosModule:pin.qdiscModule,qosBaseline:compactDefaultQueues(pin.interfaces.lan4.qdiscs),qosBoot:wan.boot,uplinkDevice:'wan',uplinkIfindex:6,uplinkPhysicalAeId:5,uplinkBaseline:compactDefaultQueues(up.defaultQueues)};
  };
  // Refresh real application ownership before any checkpoint or staging operation.
  runNode(observationRoot+'/read-controlled.mjs');const fresh=JSON.parse(fs.readFileSync(observationRoot+'/controlled-candidates-private.json'));
  assert.equal(fresh.producer,candidates.producer);assert.ok(fresh.sourceSequence>=candidates.sourceSequence);
  assert.ok(fresh.udp.some(f=>JSON.stringify(convert(f))===JSON.stringify(selected.udp))&&fresh.tcp.some(f=>JSON.stringify(convert(f))===JSON.stringify(selected.tcp)),'Exact controlled socket pair changed before staging');
  const manifest={...verifyPreparation().sourceManifest};for(const file of ['work/nss39/pair-policy.mjs','work/nss49/real-session.mjs','work/nss49/session-binding.mjs','work/nss49/read-real-candidates.mjs','work/nss49/record-candidates.mjs','work/nss49/current-audit-diagnostic.mjs','work/nss49/audit-renderer.mjs','work/nss27/flow-selection.mjs'])manifest[file]=hash(fs.readFileSync(file));save('source-manifest',manifest);
  context=await beginStage(makeInput(selected,selectionFrame),dir,async provisional=>{
   // Syntax and the downloaded checkpoint are complete. Select the TCP now,
   // before the independent stage begins; an existing gate is never retargeted.
   verifyPreparation();runNode(observationRoot+'/read-controlled.mjs');
   const frame=JSON.parse(fs.readFileSync(observationRoot+'/controlled-candidates-private.json'));
   assert.equal(frame.producer,selectionFrame.producer);assert.ok(frame.sourceSequence>=selectionFrame.sourceSequence);selected=frame.pairs.find(p=>JSON.stringify(p)===JSON.stringify(preauditSelected));assert.ok(selected,'Controlled exact pair changed after checkpoint');
   const refined=makeInput(selected,frame,true);
   refined.classifierOwner=provisional.classifierOwner;
   save('post-checkpoint-controlled-receipt-private',frame);
   return refined;
  });
  await uploadStage(context);let latest;
  for(let i=0;i<60;i++){const s=await readStage(c,context);if(s.record){latest=s.record;save('last-record-private',latest);}if(!s.directoryPresent)break;await new Promise(r=>setTimeout(r,1700));}
  await waitStageUndo(context);assert.ok(latest,'No bounded-owner receipt');assert.equal(latest.error,undefined,latest.error);
  for(const key of ['abaCompleted','unchangedQoSPlan','fastPathEpochCompleted','explicitEarlyRetirement','firmwareZeroAfterRetirement','tagsRemoved','qosRestored','qosModuleUnloaded','dualPhysicalQueuesReady','dualPhysicalQueuesRestored','wanRestored','mwan3Restored','stateNodeRemoved'])assert.equal(latest[key],true,key);
  assert.equal(latest.fastPathMeasurement.qualified,true,latest.fastPathMeasurement.reason);assert.ok(latest.renewals.length>0);assert.deepEqual(latest.phases.map(p=>p.name),['A','B','A2']);for(const p of latest.phases){assert.ok(p.completed&&p.seconds>=20&&p.seconds<=21.5&&p.sampleCount>=38);for(const t of latest.samples.slice(p.sampleStart-1,p.sampleEnd)){assert.equal(t.phase,p.name);assert.equal(t.counts['ecm_nss_ipv4/accelerated_count'],p.name==='B'?2:0);}}
  save('actual-accelerated-state-proof',validateAcceleratedState(latest.acceleratedState,selected));
  save('functional-runtime-proof',{passed:true,observedAt:new Date().toISOString(),realCs2SteamPair:false,controlledRealWanPair:true,oneWan:selected.udp.wan,nativeRenewal:true,firmwareZero:true,cleanupVerified:true,matchedForwardingABA:true,offeredGameSteamLoadEqualityRequiresReview:true,highLoadCpuBenefitConclusion:false,gameQualityConclusion:false,selectedSubgroupCeilingMbps:30,selectedUplinkSubgroupCeilingMbps:60,unselectedPhysicalFallbackMbps:950});
  completed=true;
 }catch(error){failures.push(String(error));save('controller-error',{error:String(error)});process.exitCode=1;}
 finally{
  if(context)try{await waitStageUndo(context);}catch(e){failures.push('cleanup: '+String(e));process.exitCode=1;}
  if(before&&c)try{const after=await readBaseline(c,dir,'after');runNode('work/nss146/current-audit-diagnostic.mjs',[dir.split('/').at(-1)+'-after','recovery',dir]);save('baseline-audit',auditScopedBaseline(before,after));}catch(e){failures.push('baseline: '+String(e));process.exitCode=1;}
  c?.close();save('result',{passed:completed&&failures.length===0,mode:'aba',controlledOwnerRequired:true,trafficGenerated:true,matchedForwardingABARequested:true,matchedForwardingABACompleted:completed,gameQualityConclusion:false,errors:failures});
  console.log(JSON.stringify({passed:failures.length===0,mode:'aba',output:dir,errors:failures}));
 }
}
