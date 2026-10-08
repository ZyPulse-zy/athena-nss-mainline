import fs from'node:fs';import assert from'node:assert/strict';
const normal='work/resident-normal-dev-h-20261008',service='work/resident-service-dev-h-20261008';
const once=(s,a,b)=>{assert.equal(s.split(a).length,2,a);return s.replace(a,()=>b);};const edit=(p,fn)=>fs.writeFileSync(p,fn(fs.readFileSync(p,'utf8')));
edit(normal+'/qualification.mjs',s=>{
 s="import{verifyGeneralBatch}from'../resident-general-dev-20261008/qualification.mjs';\n"+s;
 s=once(s,'export function verifyLocalBatch(){','export function verifyLocalBatch(){verifyGeneralBatch();');
 s=once(s," const dir=root+'/local-batch-"," verifyGeneralBatch();const dir=root+'/local-batch-");return s;
});
edit(normal+'/normal-entry.mjs',s=>{
 s="import{verifyLocalBatch}from'./qualification.mjs';\n"+s;
 s=once(s,' inspection();platformPreflight();',' verifyLocalBatch();inspection();platformPreflight();');return s;
});
edit(service+'/daemon.mjs',s=>s.replace('sixDataPlaneLuaByteExactWithRc1:true,onlyPublicationReadChanged:true','sixDataPlaneLuaByteExactWithRc1:false,onlyPublicationReadChanged:false,independentQualifiedAdmission:true'));
edit(service+'/generation-outcome.mjs',s=>{
 s=once(s,"assert.equal(refusal.reason,'No currently eligible owned flow set');","assert.ok(['No currently eligible normal triple','No currently eligible owned flow set'].includes(refusal.reason));");
 s=s.replaceAll("reason:'No currently eligible owned flow set'","reason:refusal.reason");return s;
});
console.log(JSON.stringify({bound:true,routerAccess:false}));
