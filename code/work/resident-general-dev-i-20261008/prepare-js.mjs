import fs from 'node:fs';import assert from 'node:assert/strict';
const root='work/resident-general-dev-i-20261008',normal='work/resident-normal-dev-i-20261008',service='work/resident-service-dev-i-20261008';
const once=(s,a,b)=>{assert.equal(s.split(a).length,2,a);return s.replace(a,()=>b);};
const put=(name,s)=>fs.writeFileSync(name,s,{flag:'wx'});
for(const [from,to] of [['work/resident-normal-dev-g-20261008',normal],['work/resident-service-dev-g-20261008',service]]){
 fs.mkdirSync(to);for(const name of fs.readdirSync(from).filter(n=>/\.(mjs|ps1)$/.test(n))){
  let s=fs.readFileSync(from+'/'+name,'utf8').replaceAll('\r\n','\n').replaceAll('resident-normal-dev-g-20261008','resident-normal-dev-i-20261008').replaceAll('resident-service-dev-g-20261008','resident-service-dev-i-20261008');put(to+'/'+name,s);
 }
}
const slotImport="import{activeSlots}from'../resident-general-dev-i-20261008/selection.mjs';\n";
for(const name of ['class-leaf-map.mjs','wan-tag-plan.mjs','candidate-policy.mjs','parse-ecm.mjs','guardian-plan.mjs']){
 let s=slotImport+fs.readFileSync('work/v20-five/'+name,'utf8').replaceAll('\r\n','\n');
 if(name==='class-leaf-map.mjs'){
  s=once(s,"for(const slot of ['tcp','udp','tcp2'])","for(const slot of activeSlots(selected))");
  s=once(s,'assert.notEqual(selected.tcp.wan,selected.tcp2.wan);','');
  s=once(s,"assert.ok(Object.hasOwn(values,d.class),'Unknown class default deny');","assert.ok(Object.hasOwn(values,d.class),'Unknown class default deny');assert.equal(d.class,slot==='udp'?'RT':'BULK');");
 }else if(name==='wan-tag-plan.mjs'){
  s=once(s,"assert.deepEqual(Object.keys(mapping).sort(),['tcp','tcp2','udp']);assert.notEqual(mapping.tcp.wan,mapping.tcp2.wan);","assert.ok(Object.keys(mapping).length>=1&&Object.keys(mapping).length<=3);");
 }else if(name==='candidate-policy.mjs'){
  s=once(s,"const a=input.selected.tcp,b=input.selected.udp,d=input.selected.tcp2,p=input.wanPrerequisites;assert.notEqual(a.wan,d.wan);assert.equal(p.boot,q.boot);assert.ok(p.members.length>=2&&p.members.length<=3);assert.equal(p.members.length,new Set([a.wan,b.wan,d.wan]).size);","const slots=activeSlots(input.selected),p=input.wanPrerequisites;assert.equal(p.boot,q.boot);assert.ok(p.members.length>=1&&p.members.length<=3);assert.equal(p.members.length,new Set(slots.map(k=>input.selected[k].wan)).size);assert.equal(new Set(p.members.map(e=>e.w)).size,p.members.length);");
  s=once(s,'for(const f of[a,b,d])','for(const f of slots.map(k=>input.selected[k]))');
  s=once(s,"assert.equal(a.protocol,6);assert.equal(b.protocol,17);assert.equal(d.protocol,6);for(const[slot,f]of[['tcp',a],['udp',b],['tcp2',d]]){","assert.deepEqual(Object.keys(input.tagPlan.wanLeafAssignments).sort(),slots.slice().sort());for(const slot of slots){const f=input.selected[slot];");
  s=once(s,"for(const slot of['tcp','udp','tcp2']){","assert.deepEqual(activeSlots(after.selected),activeSlots(before.selected));for(const slot of activeSlots(before.selected)){");
 }else if(name==='parse-ecm.mjs'){
  s=once(s,"assert.ok(selected&&selected.tcp&&selected.udp&&selected.tcp2,'Missing selected pair');assert.equal(selected.tcp.protocol,6);assert.equal(selected.udp.protocol,17);\n assert.notEqual(selected.tcp.wan,selected.tcp2.wan,'Two distinct selected WANs required');","const slots=activeSlots(selected);if(remainingUdpOnly)assert.ok(selected.udp);");
  s=once(s,'for(const f of [selected.tcp,selected.udp,selected.tcp2])','for(const f of slots.map(k=>selected[k]))');
  s=once(s,"remainingUdpOnly?1:3","remainingUdpOnly?1:slots.length");
  s=once(s,"remainingUdpOnly?[['udp',2399535104]]:[['tcp',2399469568],['udp',2399535104],['tcp2',2399469568]]","(remainingUdpOnly?['udp']:slots).map(s=>[s,0])");
 }else s=once(s,"assert.deepEqual(Object.keys(plan.selected).sort(),['tcp','tcp2','udp']);","activeSlots(plan.selected);");
 put(root+'/'+name,s);
}
const edit=(file,fn)=>fs.writeFileSync(file,fn(fs.readFileSync(file,'utf8')));
edit(normal+'/normal-policy.mjs',s=>{
 s=slotImport+s.replace("../v20-five/class-leaf-map.mjs","../resident-general-dev-i-20261008/class-leaf-map.mjs").replace("import {eligibleTriples} from '../resident-dev-20261007/eligible-selection.mjs';","import{eligibleSelections}from'../resident-general-dev-i-20261008/selection.mjs';");
 const a="owners[f.key]=[...matches.values()][0];(i.protocolNumber===6?tcp:udp).push(f);";
 s=once(s,a,"try{mapClassifiedPair(frame,{[i.protocolNumber===6?'tcp':'udp']:selected});}catch{continue;}\n  "+a);
 s=once(s,'eligibleTriples(rankedTcp,rankedUdp,canonicalSelection)','eligibleSelections(rankedTcp,rankedUdp,canonicalSelection)');
 s=once(s,"const mapped=mapClassifiedPair(frame,p);assert.deepEqual(mapped.decisions.map(d=>d.class),['BULK','RT','BULK']);pairs.push(p);","mapClassifiedPair(frame,p);pairs.push(p);");
 s=once(s,"for(const slot of ['tcp','udp','tcp2'])","for(const slot of activeSlots(selected))");return s;
});
edit(normal+'/read-prerequisites.mjs',s=>once(slotImport+s,"for(const slot of ['tcp','udp','tcp2'])","for(const slot of activeSlots(selected))"));
edit(normal+'/normal-entry.mjs',s=>s.replace('resident-normal-fixture-\\d{14}','resident-normal-(?:fixture|session)-\\d{14}'));
edit(service+'/generation-outcome.mjs',s=>s.replaceAll('No currently eligible normal triple','No currently eligible owned flow set'));
edit(normal+'/materialize-normal.mjs',s=>{
 s="import{adaptGeneralRuntime}from'../resident-general-dev-i-20261008/adapt-runtime.mjs';\n"+s;
 s=s.replaceAll('No currently eligible normal triple','No currently eligible owned flow set');
 s=once(s," const result={...q,actualBindings:q.actualBindings+17,"," adaptGeneralRuntime(runtimeRoot,q);\n const result={...q,actualBindings:Object.keys(q.sourceManifest).length+q.inheritedBindings,");
 s=s.replace('sixDataPlaneLuaByteExactWithRc1:true','sixDataPlaneLuaByteExactWithRc1:false').replace('onlyPublicationReadChanged:true','onlyPublicationReadChanged:false,optionalSlotNative:true,independentQualifiedAdmission:true');return s;
});
console.log(JSON.stringify({prepared:true,normal,service,routerAccess:false}));
