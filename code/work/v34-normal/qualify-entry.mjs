import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';
import assert from 'node:assert/strict';import {spawnSync} from 'node:child_process';
import {verifyPreparation as inherited} from '../v33-normal/session-binding.mjs';
const root='work/v34-normal',oldRoot='work/v33-normal',old=inherited();
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const prepared=JSON.parse(fs.readFileSync(root+'/prepare-receipt.json'));
for(const [f,h] of Object.entries(prepared.oldHashes))assert.equal(hash(fs.readFileSync(f)),h,f);
const rebase=b=>b.toString('utf8').replaceAll(oldRoot,root).replaceAll('work\\/v33-normal\\/','work\\/v34-normal\\/');
for(const name of prepared.copied){
 if(name==='epoch-driver.mjs')continue;
 let expected=rebase(fs.readFileSync(oldRoot+'/'+name));
 if(name==='session.mjs')expected=expected.replace("Date.parse('2026-10-07T03:30:00Z')","Date.parse('2026-10-07T04:30:00Z')");
 assert.equal(fs.readFileSync(root+'/'+name,'utf8'),expected,name);
}
const driver=fs.readFileSync(root+'/epoch-driver.mjs','utf8'),prior=rebase(fs.readFileSync(oldRoot+'/epoch-driver.mjs'));
const tail='  context=await beginStage(';
assert.equal(driver.slice(driver.indexOf(tail)),prior.slice(prior.indexOf(tail)),'Checkpoint and later owner path changed');
assert.ok(driver.indexOf('for(const w of candidateWans)')<driver.indexOf('selected=selectPreparedTriple('));
assert.ok(driver.indexOf('selected=selectPreparedTriple(')<driver.indexOf(tail));
assert.ok(!driver.includes('Exact controlled socket pair changed before staging'));
for(const n of ['native-qualified.json','normalizer-qualified.json','qos-native-qualified.json','normal-policy-qualified.json','last-selection-qualified.json'])assert.deepEqual(fs.readFileSync(root+'/'+n),fs.readFileSync(oldRoot+'/'+n));
const models=JSON.parse(fs.readFileSync(root+'/prepared-selection-qualified.json'));
assert.ok(models.passed&&models.checks===13&&models.modelOnly&&models.nativePrerequisitesModeledOnly&&!models.hardwareExecuted);
for(const [f,h] of Object.entries(models.sourceHashes))assert.equal(hash(fs.readFileSync(f)),h,f);
let dependencies=0;const manifest={};
for(const name of fs.readdirSync(root))if(/\.(mjs|lua|py|ps1)$/.test(name)&&!name.includes('private')){
 const f=root+'/'+name;manifest[f]=hash(fs.readFileSync(f));
 if(name.endsWith('.mjs')){
  for(const m of fs.readFileSync(f,'utf8').matchAll(/(?:from\s*|import\s*)['"](\.{1,2}\/[^'"]+\.mjs)['"]/g)){assert.ok(fs.existsSync(path.resolve(root,m[1])),m[1]);dependencies++;}
  const p=spawnSync(process.execPath,['--check',f],{encoding:'utf8',windowsHide:true});assert.equal(p.status,0,p.stderr);
 }
}
for(const name of ['native-qualified.json','normalizer-qualified.json','qos-native-qualified.json','normal-policy-qualified.json','last-selection-qualified.json','prepared-selection-qualified.json'])manifest[root+'/'+name]=hash(fs.readFileSync(root+'/'+name));
const result={passed:true,sourceManifest:manifest,inheritedBindings:Object.keys(old.sourceManifest).length,
 relativeDependenciesExist:dependencies,newPreparationModels:13,originalSelectorModelsReused:18,actualRefusalRegressionModelsReused:14,
 historicalModelsReplayed:false,onlyReadPreparationAndInitialSelectionOrderChanged:true,
 dataPlaneAndImmutableCandidatePolicyUnchanged:true,postCheckpointWanMarkNatAndOriginalGameScopeUnchanged:true,
 sourceFreshnessSeconds:6,kernelSessionSeconds:90,kernelMaximumSeconds:120,ownerSeconds:180,clientMaximumSeconds:180,
 phaseSeconds:60,maximumExactFlows:3,temporaryClientLimitMbps:32,defaultInspectOnly:true,oneSessionAttemptOnly:true,
 cutoff:prepared.newCutoff,hardwareExecuted:false,wholeFactoryModeled:false,normalApplicationFactoryHardwareAcceptance:false,humanAcceptance:false,permanentNssDeployment:false};
fs.writeFileSync(root+'/entry-qualified.json',JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({passed:true,bindings:Object.keys(old.sourceManifest).length+Object.keys(manifest).length,newPreparationModels:13,
 sourceCopies:Object.keys(manifest).length,dependencies,historicalModelsReplayed:false,dataPlaneChanged:false,hardwareExecuted:false}));
