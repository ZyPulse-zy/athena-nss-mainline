import {verifyPreparation} from './session-binding.mjs';
import {verifyEpochServices} from '../nss50/service-epoch.mjs';
import {selectRealPair} from '../nss39/pair-policy.mjs';
import {validateAcceleratedState} from '../nss49/parse-ecm-any-wan.mjs';
// Single real CS2/Steam pair. Default inspection is read-only. No traffic generator.
// Exact single-WAN pair only after native renewal, expiry, acceleration and cleanup qualify.
// Identical queue budget and common observer across A/B/A2. Real offered load and
// game telemetry still need review before any performance conclusion.
import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';import {spawnSync} from 'node:child_process';
import {beginStage,uploadStage,readStage,waitStageUndo} from '../nss53/module-stage.mjs';
import {connectRouter} from '../nss27/connect-router.mjs';import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
import {readBaseline,auditBaseline} from '../nss15/baseline.mjs';import {packetTemplate} from '../nss16/automatic-leaf-plan.mjs';
import {canonicalSelection} from '../nss27/flow-selection.mjs';
const mode=process.argv[2]??'inspect';assert.ok(['inspect','aba'].includes(mode));
const root='work/nss49', observationRoot='work/nss49',hash=b=>crypto.createHash('sha256').update(b).digest('hex');
function runNode(file,args=[]){const p=spawnSync(process.execPath,[file,...args],{encoding:'utf8',windowsHide:true,timeout:30000});assert.equal(p.status,0,p.stderr);return p.stdout.trim();}
const preflight=JSON.parse(fs.readFileSync(root+'/mainline-preflight-qualified.json'));assert.equal(preflight.passed,true);assert.equal(preflight.phasedIntegration,true);
verifyPreparation();
const proof=JSON.parse(fs.readFileSync('work/nss27/wan-scope-qualified.json'));assert.equal(proof.passed,true);assert.equal(proof.sourceSha256,hash(fs.readFileSync(root+'/wan-scope.lua')));
runNode(observationRoot+'/record-candidates.mjs');
const candidates=JSON.parse(fs.readFileSync(observationRoot+'/real-candidates-private.json'));
const pair=selectRealPair(candidates);
const observed={observedAt:new Date().toISOString(),mode,actualGameCandidates:candidates.game.length,actualBulkCandidates:candidates.bulk.length,sameWanPairs:pair.length,routerWrites:false,trafficGenerated:false,openFrontend:false};
if(!pair.length||mode==='inspect'){
 observed.status=pair.length?'SINGLE_WAN_REAL_PAIR_VISIBLE_NOT_STARTED':'WAITING_FOR_REAL_CS2_STEAM_PAIR';
 observed.nssPermissionGranted=false;fs.writeFileSync(observationRoot+'/real-session-readiness.json',JSON.stringify(observed,null,2)+'\n');console.log(JSON.stringify(observed));
}else{
 const convert=canonicalSelection;
 const selected={tcp:convert(pair[0].b),udp:convert(pair[0].g)};
 verifyPreparation();
 const dir='work/nss54/real-matched-aba-'+new Date().toISOString().replace(/\D/g,'').slice(0,14)+'-'+crypto.randomBytes(4).toString('hex');fs.mkdirSync(dir);
 const save=(n,v)=>fs.writeFileSync(dir+'/'+n+'.json',JSON.stringify(v,null,2)+'\n');
 // Freeze identity and exact application observation before the first audit.
 save('selected-preaudit-private',selected);
 const application=JSON.parse(fs.readFileSync(observationRoot+'/recorded-application-latest.json'));
 assert.equal(application.passed,true);save('application-preaudit-receipt-private',application);
 fs.mkdirSync(dir+'/application-preaudit');
 for(const [name,digest] of Object.entries(application.manifest)){assert.match(name,/^[a-z-]+\.json$/);const src=application.directory+'/'+name;assert.equal(hash(fs.readFileSync(src)),digest);fs.copyFileSync(src,dir+'/application-preaudit/'+name);}
 const preauditQualification=verifyPreparation();save('external-source-hashes-preaudit-private',preauditQualification.externalSourceBindings??[]);const preauditManifest={...preauditQualification.sourceManifest};save('source-manifest-preaudit',preauditManifest);
 fs.mkdirSync(dir+'/frozen');for(const [file,digest] of Object.entries(preauditManifest)){assert.equal(hash(fs.readFileSync(file)),digest);const dst=dir+'/frozen/'+file;fs.mkdirSync(dst.slice(0,dst.lastIndexOf('/')),{recursive:true});fs.copyFileSync(file,dst);}
 let c,context,before,completed=false;const failures=[];
 try{
  // Validate the exact current source set, never a historical passing receipt alone.
  for(const [source,proof,key] of [['fast-path.lua','aba-qualified.json','sourceSha256'],['classifier.lua','consumer-qualified.json','adapterSha256']]){const p=JSON.parse(fs.readFileSync(root+'/'+proof));assert.equal(p.passed,true);assert.equal(p[key],hash(fs.readFileSync(root+'/'+source)));}
  runNode('work/nss54/current-audit-diagnostic.mjs',[dir.split('/').at(-1)+'-before','prewrite',dir]);
  c=await connectRouter();before=await readBaseline(c,dir,'before');verifyEpochServices(JSON.parse(fs.readFileSync(dir+'/service-epoch-private.json')).services,before.services);
  const source=fs.readFileSync(root+'/read-prerequisites.lua','utf8');const e=encode("/usr/bin/lua - "+selected.tcp.wan+" <<'NSS27_REAL_PREREQUISITES'\n"+source+"\nNSS27_REAL_PREREQUISITES\n");
  const r=receipt(await c.run(e.command),e);assert.equal(r.code,0,r.stderr);const wan=JSON.parse(r.stdout);save('prerequisites-private',wan);
  assert.equal(wan.status['ipv4-address'][0].address,selected.tcp.reply.dst);assert.equal(wan.status.l3_device,'rpwan'+selected.tcp.wan);
  const pin=JSON.parse(fs.readFileSync('work/nss16/qos-capacity-private.json'));assert.equal(pin.boot.trim(),wan.boot);
  const frozen=Buffer.from(JSON.stringify({schema:'nss27-real-pair-v1',selected,sourceSequence:candidates.sourceSequence,producer:candidates.producer,pcEvidenceSha256:hash(fs.readFileSync(observationRoot+'/pc-app-endpoints-private.json'))}));
  fs.writeFileSync(dir+'/frozen-private.json',frozen);save('selected-private',selected);
  const values={register_gate:1,diagnostic_only:0};
  for(const [slot,name] of [['tcp','tcp'],['udp','game']]){const f=selected[slot];assert.equal(f.zone,0);assert.ok(Number.isSafeInteger(f.id)&&f.id>0&&f.id<=0xffffffff);assert.equal(f.original.src,'192.168.237.207');assert.equal((f.mark&0xff0000)>>>16,f.wan);assert.equal(f.mark&0x2000,0);
   Object.assign(values,{[name+'_ct_id_raw']:((f.id>>>24)|((f.id>>>8)&0xff00)|((f.id<<8)&0xff0000)|(f.id<<24))>>>0,[name+'_server']:f.original.dst,[name+'_source_port']:f.original.sport,[name+'_server_port']:f.original.dport,[name+'_ct_mark']:f.mark,[name+'_nat_address']:f.reply.dst,[name+'_nat_port']:f.reply.dport});}
  values.frozen_record_sha256=hash(frozen);
  const insmodArguments=Object.entries(values).map(([k,v])=>{assert.match(k,/^[a-z0-9_]+$/);assert.match(String(v),/^[a-f0-9.]+$/);return k+'='+v;}).join(' ');
  const owner=crypto.randomBytes(16).toString('hex');const unusedPort=selected.udp.original.sport===59999?59998:59999;
  const template=packetTemplate({decisions:[{slot:'tcp',protocol:6,downTag:2399469568,flow:selected.tcp,validUntilUptime:0},{slot:'udp',protocol:17,downTag:2399535104,flow:selected.udp,validUntilUptime:0}]},owner,unusedPort);
  template.expected.nftables=template.expected.nftables.filter(x=>x.chain?.name!=='forward'&&x.rule?.chain!=='forward');
  const tagPlan={table:template.expected.nftables[0].table.name,owner,mode:'rt',expected:template.expected};
  // Refresh real application ownership before any checkpoint or staging operation.
  runNode(observationRoot+'/record-candidates.mjs');const fresh=JSON.parse(fs.readFileSync(observationRoot+'/real-candidates-private.json'));
  assert.equal(fresh.producer,candidates.producer);assert.ok(fresh.sourceSequence>=candidates.sourceSequence);
  assert.ok(fresh.game.some(f=>JSON.stringify(convert(f))===JSON.stringify(selected.udp))&&fresh.bulk.some(f=>JSON.stringify(convert(f))===JSON.stringify(selected.tcp)),'Exact real application pair changed before staging');
  const manifest={...verifyPreparation().sourceManifest};for(const file of ['work/nss39/pair-policy.mjs','work/nss49/real-session.mjs','work/nss49/session-binding.mjs','work/nss49/read-real-candidates.mjs','work/nss49/record-candidates.mjs','work/nss49/current-audit-diagnostic.mjs','work/nss49/audit-renderer.mjs','work/nss27/flow-selection.mjs'])manifest[file]=hash(fs.readFileSync(file));save('source-manifest',manifest);
  context=await beginStage({mode:'stage',openFrontend:true,wanPrerequisites:{wan:wan.wan,boot:wan.boot,auth:wan.auth,mode:wan.mode.map(x=>({ifindex:x.ifindex,address:x.address,link_index:x.link_index})),status:{up:wan.status.up,l3_device:wan.status.l3_device,'ipv4-address':wan.status['ipv4-address']}},stateMajor:wan.stateMajor,frozenHash:hash(frozen),insmodArguments,autoClassified:true,selected,tagPlan,qosStaged:true,qosDevice:'lan4',qosTc:pin.tc,qosModule:pin.qdiscModule,qosBaseline:pin.interfaces.lan4.qdiscs,qosBoot:wan.boot},dir);
  await uploadStage(context);let latest;
  for(let i=0;i<26;i++){const s=await readStage(c,context);if(s.record){latest=s.record;save('last-record-private',latest);}if(!s.directoryPresent)break;await new Promise(r=>setTimeout(r,1700));}
  await waitStageUndo(context);assert.ok(latest,'No bounded-owner receipt');assert.equal(latest.error,undefined,latest.error);
  for(const key of ['abaCompleted','unchangedQoSPlan','fastPathEpochCompleted','explicitEarlyRetirement','firmwareZeroAfterRetirement','tagsRemoved','qosRestored','qosModuleUnloaded','wanRestored','mwan3Restored','stateNodeRemoved'])assert.equal(latest[key],true,key);
  assert.equal(latest.fastPathMeasurement.qualified,true,latest.fastPathMeasurement.reason);assert.ok(latest.renewals.length>0);assert.deepEqual(latest.phases.map(p=>p.name),['A','B','A2']);for(const p of latest.phases){assert.ok(p.completed&&p.seconds>=5&&p.seconds<=6.5&&p.sampleCount>=8);for(const t of latest.samples.slice(p.sampleStart-1,p.sampleEnd)){assert.equal(t.phase,p.name);assert.equal(t.counts['ecm_nss_ipv4/accelerated_count'],p.name==='B'?2:0);}}
  save('actual-accelerated-state-proof',validateAcceleratedState(latest.acceleratedState,selected));
  save('functional-runtime-proof',{passed:true,observedAt:new Date().toISOString(),realCs2SteamPair:true,oneWan:selected.udp.wan,nativeRenewal:true,firmwareZero:true,cleanupVerified:true,matchedForwardingABA:true,offeredGameSteamLoadEqualityRequiresReview:true,highLoadCpuBenefitConclusion:false,gameQualityConclusion:false,selectedSubgroupCeilingMbps:20,unselectedPhysicalFallbackMbps:950});
  completed=true;
 }catch(error){failures.push(String(error));save('controller-error',{error:String(error)});process.exitCode=1;}
 finally{
  if(context)try{await waitStageUndo(context);}catch(e){failures.push('cleanup: '+String(e));process.exitCode=1;}
  if(before&&c)try{const after=await readBaseline(c,dir,'after');runNode('work/nss54/current-audit-diagnostic.mjs',[dir.split('/').at(-1)+'-after','recovery',dir]);save('baseline-audit',auditBaseline(before,{...after,native:before.native}));}catch(e){failures.push('baseline: '+String(e));process.exitCode=1;}
  c?.close();save('result',{passed:completed&&failures.length===0,mode:'aba',realPairRequired:true,trafficGenerated:false,matchedForwardingABARequested:true,matchedForwardingABACompleted:completed,gameQualityConclusion:false,errors:failures});
  console.log(JSON.stringify({passed:failures.length===0,mode:'aba',output:dir,errors:failures}));
 }
}
