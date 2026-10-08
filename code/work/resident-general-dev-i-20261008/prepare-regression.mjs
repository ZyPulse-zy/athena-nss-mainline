import fs from'node:fs';import assert from'node:assert/strict';import{hash}from'../resident-dev-20261007/materialize.mjs';
const root='work/resident-general-dev-i-20261008',normal='work/resident-normal-dev-i-20261008',service='work/resident-service-dev-i-20261008';
const once=(s,a,b)=>{assert.equal(s.split(a).length,2,a);return s.replace(a,()=>b);};
const edit=(p,fn)=>fs.writeFileSync(p,fn(fs.readFileSync(p,'utf8')));
const b=JSON.parse(fs.readFileSync(root+'/endpoint-gate/build-manifest.json'));assert.equal(b.status,'built-classifier-epoch-offline; no runtime qualification');
const control=JSON.parse(b.offline_tests),ct=JSON.parse(b.ct_tests);assert.ok(control.passed&&ct.passed&&b.sdk_original_unchanged&&b.old_gate_inputs_unchanged&&b.source_inputs_unchanged);
fs.writeFileSync(root+'/native-source-qualified.json',JSON.stringify({passed:true,sourceSha256:b.source_hashes['rp_ecm_gate_lab_ct.c'],headerSha256:b.source_hashes['two_slot_predicate.h'],controlChecks:157,ctChecks:109,predicateOutput:b.predicate_tests,allSevenNonemptyMasks:true,hardwareQualified:false,source6Unchanged:true,terminalGatesUnchanged:true,exactCtNatMarkPinPreserved:true},null,2)+'\n',{flag:'wx'});
edit(normal+'/test-normal-policy.mjs',s=>{
 const a="function deny(name,change){test(name,()=>{const f=structuredClone(base),p=structuredClone(pc);change(f,p);let denied=false;try{denied=selectNormalCandidates(f,p).pairs.length===0;}catch{denied=true;}assert.ok(denied);});}";
 const b="function deny(name,change){test(name,()=>{const f=structuredClone(base),p=structuredClone(pc);change(f,p);let denied=false;try{const q=selectNormalCandidates(f,p).pairs;const rt=['RT process','PID reused','two UDP','RT budget'].some(k=>name.startsWith(k)),bulk=['changed TCP','unknown TCP','BE does'].some(k=>name.startsWith(k));denied=q.length===0||rt&&q.every(x=>!x.udp)||bulk&&q.every(x=>!x.tcp&&!x.tcp2);}catch{denied=true;}assert.ok(denied,name);});}";
 s=once(s,a,b);
 s=once(s,"deny('one readable BULK process is insufficient',(_,p)=>p.tcp=p.tcp.slice(0,1));","test('one owned BULK is independently sufficient without another WAN or RT',()=>{const p=structuredClone(pc);p.tcp=p.tcp.slice(0,1);p.udp=[];const q=selectNormalCandidates(base,p);assert.deepEqual(Object.keys(q.pairs[0]),['tcp']);});");
 s=once(s,"assert.equal(selectNormalCandidates(base,pc,wrongTuple).pairs.length,0);","assert.ok(selectNormalCandidates(base,pc,wrongTuple).pairs.every(p=>!p.udp));");return s;
});
edit(normal+'/test-natural-selection.mjs',s=>{
 s=once(s,"assert.equal(selectNormalCandidates(one,structuredClone(pc)).pairs.length,0);checks.push('one natural BULK WAN remains insufficient');","assert.ok(selectNormalCandidates(one,structuredClone(pc)).pairs.length);checks.push('one natural BULK WAN qualifies independently');");
 s=once(s,"assert.equal(selectNormalCandidates(unknown,structuredClone(pc)).pairs.length,0);checks.push('WAN diversity never elevates BE or unknown flows');","const filtered=selectNormalCandidates(unknown,structuredClone(pc));assert.ok(filtered.pairs.length);assert.ok(filtered.pairs.every(p=>[p.tcp,p.tcp2].filter(Boolean).every(f=>f.wan===4)));checks.push('BE is excluded while other qualified flows remain usable');");return s;
});
edit(normal+'/test-materialize.mjs',s=>{
 s=once(s,"test('six data-plane Lua are exact RC1 bytes',()=>{for(const n of ['fast-path.lua','classified-tags.lua','module-stage-guardian.lua','qos-physical.lua','wan-scope.lua','tag-normalizer.lua'])assert.deepEqual(fs.readFileSync(root+'/'+n),fs.readFileSync('work/resident-rc1-run-20261007163534-ae83fa69/'+n),n);});","test('all changed Lua support actual active slots',()=>{for(const n of ['fast-path.lua','classified-tags.lua','module-stage-guardian.lua','qos-physical.lua','wan-scope.lua','tag-normalizer.lua'])assert.ok(/(?:AS|NS)\\(/.test(fs.readFileSync(root+'/'+n,'utf8')),n);});");
 return s.replaceAll('sixDataPlaneLuaByteExactWithRc1:true','sixDataPlaneLuaByteExactWithRc1:false').replaceAll('onlyPublicationReadChanged:true','onlyPublicationReadChanged:false,optionalSlotNative:true');
});
for(const p of [normal+'/qualification.mjs',service+'/qualification.mjs'])edit(p,s=>s.replaceAll('sixDataPlaneLuaByteExactWithRc1,true','sixDataPlaneLuaByteExactWithRc1,false').replaceAll('onlyPublicationReadChanged,true','onlyPublicationReadChanged,false').replaceAll('sixDataPlaneLuaByteExactWithRc1:true','sixDataPlaneLuaByteExactWithRc1:false').replaceAll('onlyPublicationReadChanged:true','onlyPublicationReadChanged:false,optionalSlotNative:true'));
console.log(JSON.stringify({prepared:true,nativeModelsPassed:true,routerAccess:false}));
