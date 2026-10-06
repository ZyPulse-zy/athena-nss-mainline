// Verify the existing prepared entry and its already frozen inputs; do not replay models.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {verifyPreparation} from '../nss140/session-binding.mjs';
const h=b=>crypto.createHash('sha256').update(b).digest('hex');
const current=verifyPreparation().sourceManifest;
const frozen=JSON.parse(fs.readFileSync('work/nss141/prepared-bindings-private.json','utf8'));
assert.deepEqual(current,frozen);assert.equal(Object.keys(current).length,1385);
for(const[f,x]of Object.entries(current)){
 assert.equal(h(fs.readFileSync(f)),x,f);
 assert.equal(h(fs.readFileSync('work/nss141/prepared-inputs-private/'+f)),x,f);
}
const out={passed:true,observedAt:new Date().toISOString(),readonly:true,preparedEntry:'work/nss140/real-session.mjs',boundInputs:1385,currentAndPreviouslyFrozenInputsExact:true,modelsReplayed:false,routerConnected:false,productionWrites:false,newHardwareAbaProof:false};
fs.writeFileSync('work/nss142/prepared-bindings-final.json',JSON.stringify(out,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(out));
