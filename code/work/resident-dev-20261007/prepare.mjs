import fs from 'node:fs';import assert from 'node:assert/strict';
const root='work/resident-dev-20261007',old='work/v65-selected-wan';
for(const name of fs.readdirSync(old)){
 if(!/\.(mjs|ps1|py)$/.test(name)||name==='prepare.mjs'||name==='publish.py')continue;
 let s=fs.readFileSync(old+'/'+name,'utf8').replaceAll('v65-selected-wan','resident-dev-20261007').replaceAll('v65-run-','resident-rc1-run-');
 if(name==='materialize.mjs'){
  s="import{patchFinalDriver,patchFinalStage}from'./final-selection.mjs';\n"+s;
  const point="if(name==='native-client.mjs'){";assert.equal(s.split(point).length,2);
  s=s.replace(point,"if(name==='epoch-driver.mjs')bytes=Buffer.from(patchFinalDriver(bytes.toString()));\n  if(name==='module-stage.mjs')bytes=Buffer.from(patchFinalStage(bytes.toString()));\n  "+point);
  const binding="['selected-acquisition.mjs','acquisition-order.mjs'";assert.equal(s.split(binding).length,2);
  s=s.replace(binding,"['final-selection.mjs','selected-acquisition.mjs','acquisition-order.mjs'");
 }
 fs.writeFileSync(root+'/'+name,s,{flag:'wx'});
}
console.log(JSON.stringify({prepared:true,selectionOnlyBeforeDetachedOwner:true,productionExecuted:false}));
