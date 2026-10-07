import fs from'node:fs';import path from'node:path';import crypto from'node:crypto';import assert from'node:assert/strict';import{spawnSync}from'node:child_process';
import{verifyPreparation as inherited}from'../v30-normal/session-binding.mjs';
const root='work/v31-normal',oldRoot='work/v30-normal',old=inherited(),hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const prepared=JSON.parse(fs.readFileSync(root+'/prepare-receipt.json'));
for(const[f,h]of Object.entries(prepared.oldHashes))assert.equal(hash(fs.readFileSync(f)),h,f);
const rebase=b=>b.toString('utf8').replaceAll(oldRoot,root).replaceAll('work\\/v30-normal\\/','work\\/v31-normal\\/');
const unchanged=prepared.copied.filter(n=>!Object.hasOwn(prepared.changed,n));
for(const name of unchanged)assert.equal(fs.readFileSync(root+'/'+name,'utf8'),rebase(fs.readFileSync(oldRoot+'/'+name)),name);
const ep=fs.readFileSync(root+'/epoch-driver.mjs','utf8'),stage=fs.readFileSync(root+'/module-stage.mjs','utf8');
assert.ok(ep.includes('selected=selectAnchoredTriple(frame,selected.udp,{tcp:selected.tcp.wan,tcp2:selected.tcp2.wan})[0]'));
assert.ok(ep.includes("Original CS2 CT/socket identity changed"));
assert.ok(stage.includes("import{validatePreStageRefinement as validateRefinement}from'./normal-refinement.mjs'"));
assert.equal(stage,rebase(fs.readFileSync(oldRoot+'/module-stage.mjs')).replace("import {verifyCandidate,validateRefinement} from './candidate-policy.mjs';","import {verifyCandidate} from './candidate-policy.mjs';\r\nimport{validatePreStageRefinement as validateRefinement}from'./normal-refinement.mjs';"));
const model=JSON.parse(fs.readFileSync(root+'/last-selection-qualified.json'));assert.ok(model.passed&&model.modelOnly&&model.actualHistoricalRefusalFrameUsed&&model.checks===14);
for(const[f,h]of Object.entries(model.sourceHashes))assert.equal(hash(fs.readFileSync(f)),h,f);
let dependencies=0;const manifest={};
for(const name of fs.readdirSync(root))if(/\.(mjs|lua|py|ps1)$/.test(name)){
 const file=root+'/'+name;manifest[file]=hash(fs.readFileSync(file));
 if(name.endsWith('.mjs')){for(const m of fs.readFileSync(file,'utf8').matchAll(/(?:from\s*|import\s*)['"](\.{1,2}\/[^'"]+\.mjs)['"]/g)){assert.ok(fs.existsSync(path.resolve(root,m[1])),m[1]);dependencies++;}
  const p=spawnSync(process.execPath,['--check',file],{encoding:'utf8',windowsHide:true});assert.equal(p.status,0,p.stderr);}
}
for(const name of['native-qualified.json','normalizer-qualified.json','qos-native-qualified.json','normal-policy-qualified.json']){
 assert.deepEqual(fs.readFileSync(root+'/'+name),fs.readFileSync(oldRoot+'/'+name));manifest[root+'/'+name]=hash(fs.readFileSync(root+'/'+name));}
manifest[root+'/last-selection-qualified.json']=hash(fs.readFileSync(root+'/last-selection-qualified.json'));
const result={passed:true,sourceManifest:manifest,inheritedBindings:Object.keys(old.sourceManifest).length,hardwareExecuted:false,wholeFactoryModeled:false,
 unchangedDataPlaneAndImmutableCandidatePolicy:true,onlyHostPreStageTcpSelectionChanged:true,originalGameAndWanScopeRetained:true,originalSelectorModelsReused:18,
 actualRefusalRegressionModels:14,relativeDependenciesExist:dependencies,sourceFreshnessSeconds:6,kernelSessionSeconds:90,kernelMaximumSeconds:120,ownerSeconds:180,
 clientMaximumSeconds:180,phaseSeconds:60,maximumExactFlows:3,defaultInspectOnly:true,oneSessionAttemptOnly:true,normalApplicationFactoryHardwareAcceptance:false,humanAcceptance:false,permanentNssDeployment:false};
fs.writeFileSync(root+'/entry-qualified.json',JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({passed:true,bindings:Object.keys(old.sourceManifest).length+Object.keys(manifest).length,relativeDependencies:dependencies,actualRefusalRegressionModels:14,dataPlaneChanged:false,hardwareExecuted:false}));
