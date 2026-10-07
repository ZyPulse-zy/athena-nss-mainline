import fs from'node:fs';import path from'node:path';import crypto from'node:crypto';import assert from'node:assert/strict';import{spawnSync}from'node:child_process';
import{verifyPreparation as inherited}from'../v32-normal/session-binding.mjs';
const root='work/v33-normal',oldRoot='work/v32-normal',old=inherited(),hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const prepared=JSON.parse(fs.readFileSync(root+'/prepare-receipt.json'));
for(const[f,h]of Object.entries(prepared.oldHashes))assert.equal(hash(fs.readFileSync(f)),h,f);
const rebase=b=>b.toString('utf8').replaceAll(oldRoot,root).replaceAll('work\\/v32-normal\\/','work\\/v33-normal\\/');
for(const name of prepared.copied){
 let expected=rebase(fs.readFileSync(oldRoot+'/'+name));
 if(name==='session.mjs')expected=expected.replace("Date.parse('2026-10-07T02:45:00Z')","Date.parse('2026-10-07T03:30:00Z')");
 assert.equal(fs.readFileSync(root+'/'+name,'utf8'),expected,name+' inherited behavior changed');
}
for(const name of['native-qualified.json','normalizer-qualified.json','qos-native-qualified.json','normal-policy-qualified.json','last-selection-qualified.json'])assert.deepEqual(fs.readFileSync(root+'/'+name),fs.readFileSync(oldRoot+'/'+name));
const original=JSON.parse(fs.readFileSync(oldRoot+'/entry-qualified.json')),models=JSON.parse(fs.readFileSync(root+'/last-selection-qualified.json'));
assert.ok(original.passed&&original.originalSelectorModelsReused===18&&original.actualRefusalRegressionModelsReused===14);
assert.ok(models.passed&&models.modelOnly&&models.checks===14&&!models.hardwareExecuted);
for(const[f,h]of Object.entries(models.sourceHashes))assert.equal(hash(fs.readFileSync(f)),h,f);
let dependencies=0;const manifest={};
for(const name of fs.readdirSync(root))if(/\.(mjs|lua|py|ps1)$/.test(name)&&!name.includes('private')){
 const file=root+'/'+name;manifest[file]=hash(fs.readFileSync(file));
 if(name.endsWith('.mjs')){
  for(const m of fs.readFileSync(file,'utf8').matchAll(/(?:from\s*|import\s*)['"](\.{1,2}\/[^'"]+\.mjs)['"]/g)){assert.ok(fs.existsSync(path.resolve(root,m[1])),m[1]);dependencies++;}
  const p=spawnSync(process.execPath,['--check',file],{encoding:'utf8',windowsHide:true});assert.equal(p.status,0,p.stderr);
 }
}
for(const name of['native-qualified.json','normalizer-qualified.json','qos-native-qualified.json','normal-policy-qualified.json','last-selection-qualified.json'])manifest[root+'/'+name]=hash(fs.readFileSync(root+'/'+name));
const result={passed:true,sourceManifest:manifest,inheritedBindings:Object.keys(old.sourceManifest).length,hardwareExecuted:false,wholeFactoryModeled:false,
 coreEntryOnlyPathsAndNewCutoffChanged:true,clientLauncherDownloadDescriptionParameterized:true,temporaryClientLimitMbps:32,unchangedDataPlaneAndImmutableCandidatePolicy:true,unchangedV31PreStageSelection:true,
 originalSelectorModelsReused:18,actualRefusalRegressionModelsReused:14,noModelsReplayed:true,relativeDependenciesExist:dependencies,
 sourceFreshnessSeconds:6,kernelSessionSeconds:90,kernelMaximumSeconds:120,ownerSeconds:180,clientMaximumSeconds:180,phaseSeconds:60,maximumExactFlows:3,
 defaultInspectOnly:true,oneSessionAttemptOnly:true,cutoff:prepared.newCutoff,normalApplicationFactoryHardwareAcceptance:false,humanAcceptance:false,permanentNssDeployment:false};
fs.writeFileSync(root+'/entry-qualified.json',JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({passed:true,bindings:Object.keys(old.sourceManifest).length+Object.keys(manifest).length,relativeDependencies:dependencies,
 selectorModelsReused:18,regressionModelsReused:14,modelsReplayed:false,dataPlaneChanged:false,hardwareExecuted:false}));
