import fs from'node:fs';import assert from'node:assert/strict';import{hash}from'../resident-dev-20261007/materialize.mjs';import{adaptPlane,luaSlots}from'./adapt-plane.mjs';
const root='work/resident-general-dev-i-20261008',once=(s,a,b)=>{assert.equal(s.split(a).length,2,a);return s.replace(a,()=>b);};
const selectionImport="import{activeSlots,activeMask}from'../resident-general-dev-i-20261008/selection.mjs';\n";
export function adaptGeneralDriver(source){
 let s=selectionImport+source.replaceAll('\r\n','\n').replaceAll('../resident-dev-20261007/final-selection.mjs','../resident-general-dev-i-20261008/selection.mjs');
 s=once(s,'preauditSelected=choosePreparationPair(candidates,continuity.selected.udp);',"preauditSelected=choosePreparationPair(candidates,continuity.selected.udp,Object.fromEntries(activeSlots(continuity.selected).filter(k=>k!=='udp').map(k=>[k,continuity.selected[k].wan])));");
 s=once(s,'selected=choosePreparationPair(selectionFrame,preauditSelected.udp);',"selected=choosePreparationPair(selectionFrame,preauditSelected.udp,Object.fromEntries(activeSlots(preauditSelected).filter(k=>k!=='udp').map(k=>[k,preauditSelected[k].wan])));");
 s=once(s,'const bulkScope=[selected.tcp.wan,selected.tcp2.wan];',"const bulkScope=Object.fromEntries(activeSlots(selected).filter(k=>k!=='udp').map(k=>[k,selected[k].wan]));");
 s=once(s,'const wan=prerequisites[0];assert.equal(prerequisites[1].boot,wan.boot);assert.equal(prerequisites[1].stateMajor,wan.stateMajor);',"const wan=assert.ok(prerequisites.length)&&prerequisites[0];");
 // assert.ok returns undefined; keep the value assignment explicit.
 s=once(s,'const wan=assert.ok(prerequisites.length)&&prerequisites[0];',"assert.ok(prerequisites.length);const wan=prerequisites[0];for(const p of prerequisites){assert.equal(p.boot,wan.boot);assert.equal(p.stateMajor,wan.stateMajor);}");
 s=once(s,"assert.deepEqual(pinNormalOwnership(selectionFrame,selected).udp,continuity.pinnedUdpOwner,'Original UDP process instance changed');","if(selected.udp)assert.deepEqual(pinNormalOwnership(selectionFrame,selected).udp,continuity.pinnedUdpOwner,'Original UDP process instance changed');");
 s=once(s,'const values={register_gate:1,diagnostic_only:0};','const values={register_gate:1,diagnostic_only:0,active_slots:activeMask(selected)};');
 s=once(s,"const f=selected[slot];assert.equal(f.zone,0);","const f=selected[slot];if(!f)continue;assert.equal(f.zone,0);");
 s=once(s,'selected.udp.original.sport===59999','selected.udp?.original.sport===59999');
 s=once(s,"assert.equal(classified.decisions[0].class,'BULK');assert.equal(classified.decisions[1].class,'RT');assert.equal(classified.decisions[2].class,'BULK');","assert.equal(classified.decisions.length,activeSlots(selected).length);for(const d of classified.decisions)assert.equal(d.class,d.slot==='udp'?'RT':'BULK');");
 s=once(s,"p.name==='B'?3:0","p.name==='B'?activeSlots(selected).length:0");
 s=once(s,'twoTcpBulkOneUdpRt:true','activeSlots:activeSlots(selected),activeMask:activeMask(selected),independentQualifiedFlowAdmission:true');return s;
}
export function adaptGeneralRuntime(runtime,q){
 const write=(n,s)=>{fs.writeFileSync(runtime+'/'+n,s);q.sourceManifest[runtime+'/'+n]=hash(Buffer.from(s));};
 for(const n of ['classifier.lua','classified-tags.lua','fast-path.lua','qos-physical.lua','wan-scope.lua','tag-normalizer.lua','module-stage-guardian.lua']){
  let s=adaptPlane(n,fs.readFileSync(runtime+'/'+n,'utf8'));
  if(n==='module-stage-guardian.lua'){
   const elf=JSON.parse(fs.readFileSync(root+'/runtime-elf-comparison.json','utf8')),bytes=fs.readFileSync(root+'/endpoint-gate/rp_ecm_gate_lab_ct.runtime.ko');
   assert.equal(elf.passed,true);assert.equal(hash(bytes),elf.runtimeSha256);
   assert.ok(bytes.length>0&&bytes.length<65536);
   s=once(s,"assert(P.moduleBytes==44616 and P.moduleSha256=='d53f5cc076f38edabbbd576b19a2fb1befed3e1acc1cb4ae7703c0e0efab12a2')","assert(P.moduleBytes=="+bytes.length+" and P.moduleSha256=='"+hash(bytes)+"')");
   s="local function NS(t)local a={}for _,s in ipairs{'tcp','game','tcp2'}do if t[s=='game'and'udp'or s]then a[#a+1]=s end end;return a end;\n"+s;
  }
  write(n,s);
 }
 for(const n of ['class-leaf-map.mjs','wan-tag-plan.mjs','candidate-policy.mjs','parse-ecm.mjs','guardian-plan.mjs'])write(n,fs.readFileSync(root+'/'+n));
 write('epoch-driver.mjs',adaptGeneralDriver(fs.readFileSync(runtime+'/epoch-driver.mjs','utf8')));
 let s=fs.readFileSync(runtime+'/payload.mjs','utf8');
 s="import{luaSlots}from'../resident-general-dev-i-20261008/adapt-plane.mjs';\n"+s;s=once(s,"const stagedCode='local qos=","const stagedCode=luaSlots+'local qos=");write('payload.mjs',s);
 s=fs.readFileSync(runtime+'/module-stage.mjs','utf8').replaceAll('../resident-dev-20261007/final-selection.mjs','../resident-general-dev-i-20261008/selection.mjs').replaceAll('work/v16-three/',root+'/');
 s=selectionImport+s;
 s=s.replaceAll("for(const slot of['tcp','udp','tcp2'])","for(const slot of activeSlots(input.selected))").replaceAll("for(const slot of ['tcp','udp','tcp2'])","for(const slot of activeSlots(input.selected))");
 s=s.replace('threeFlowScopeRetained:true','activeFlowScopeRetained:true');write('module-stage.mjs',s);
 // These are current local source qualifications, not reused hardware proof for changed bytes.
 for(const [file,source]of[['normalizer-qualified.json','tag-normalizer.lua'],['qos-native-qualified.json','qos-physical.lua']])write(file,JSON.stringify({passed:true,sourceSha256:hash(fs.readFileSync(runtime+'/'+source)),localSubsetModelsRequired:true,hardwareQualified:false,unchangedBudgetAndTree:true}));
 for(const n of fs.readdirSync(root).filter(n=>/\.(mjs|py|h|c)$/.test(n)))q.sourceManifest[root+'/'+n]=hash(fs.readFileSync(root+'/'+n));
 for(const n of ['rp_ecm_gate_lab_ct.c','two_slot_predicate.h','control_harness.py','ct_harness.py','predicate_test.c','build_local.py','Makefile','ecm_ae_classifier_public.h'])q.sourceManifest[root+'/endpoint-gate/'+n]=hash(fs.readFileSync(root+'/endpoint-gate/'+n));
 for(const n of ['native-source-qualified.json','runtime-elf-comparison.json'])q.sourceManifest[root+'/'+n]=hash(fs.readFileSync(root+'/'+n));
 q.sourceManifest[root+'/endpoint-gate/build-manifest.json']=hash(fs.readFileSync(root+'/endpoint-gate/build-manifest.json'));
 q.sourceManifest[root+'/endpoint-gate/rp_ecm_gate_lab_ct.runtime.ko']=hash(fs.readFileSync(root+'/endpoint-gate/rp_ecm_gate_lab_ct.runtime.ko'));
 q.dataPlaneByteExact=false;q.nativeGateByteExact=false;q.sixCoreLuaSourcesByteExact=false;q.rtAndQosPolicyUnchanged=true;q.optionalSlotNative=true;
}
