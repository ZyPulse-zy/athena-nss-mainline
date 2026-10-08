import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';
import {createObserver,rotateObserver,save,read} from './storage.mjs';import {sameProcess} from './identity.mjs';
const stamp=new Date().toISOString().replace(/\D/g,'').slice(0,14);
const owner='work/resident-service-run-'+stamp+'-'+crypto.randomBytes(4).toString('hex');fs.mkdirSync(owner);
const root=createObserver(owner),files=[],checks=[];
for(let i=0;i<20;i++){
 const token=crypto.randomUUID();for(const kind of ['native','frame']){const p=root+'/normal-'+kind+'-'+token+'-private.json';save(p,{localModel:true,index:i});fs.utimesSync(p,new Date(1700000000000+i*1000),new Date(1700000000000+i*1000));files.push(p);}
}
save(root+'/historical-evidence-private.json',{mustRemain:true});
const result=rotateObserver(root,owner);assert.deepEqual(result,{groupsRetained:16,groupsPruned:4});checks.push('bounded operational observation groups');
assert.equal(files.filter(p=>fs.existsSync(p)).length,32);assert.ok(fs.existsSync(root+'/historical-evidence-private.json'));checks.push('only matching operational records pruned');
assert.throws(()=>rotateObserver(root,owner.replace(/[a-f0-9]{8}$/,'ffffffff')),/strictly equal/);checks.push('foreign owner refused before deleting');
assert.throws(()=>rotateObserver('work/nss160',owner));checks.push('frozen or foreign namespace refused');
assert.equal(read(root+'/resident-service-owner-private.json').owner,owner);checks.push('marker ownership retained');
const expected={pid:12,birth:'2026-10-08T00:00:00.0000000Z',executable:'C:\\node.exe'},actual={...expected,found:true,expectedCommand:true};
assert.equal(sameProcess(actual,expected),true);assert.equal(sameProcess({...actual,birth:'other'},expected),false);assert.equal(sameProcess({...actual,expectedCommand:false},expected),false);assert.equal(sameProcess({found:false},expected),false);checks.push('PID alone is not residence proof');
console.log(JSON.stringify({passed:true,checks:checks.length,names:checks,routerAccess:false,modelOnly:true}));
