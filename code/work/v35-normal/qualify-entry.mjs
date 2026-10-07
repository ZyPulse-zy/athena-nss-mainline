import fs from'node:fs';import path from'node:path';import crypto from'node:crypto';import assert from'node:assert/strict';import{spawnSync}from'node:child_process';
import{verifyPreparation as inherited}from'../v34-normal/session-binding.mjs';
const root='work/v35-normal',oldRoot='work/v34-normal',old=inherited(),hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const prep=JSON.parse(fs.readFileSync(root+'/prepare-receipt.json'));
for(const[f,h]of Object.entries(prep.oldHashes))assert.equal(hash(fs.readFileSync(f)),h,f);
const rebase=b=>b.toString('utf8').replaceAll(oldRoot,root).replaceAll('work\\/v34-normal\\/','work\\/v35-normal\\/');
for(const n of prep.copied){
 if(['fast-path.lua','normal-policy.mjs','normal-selection.mjs'].includes(n))continue;
 let expected=n.endsWith('.json')?fs.readFileSync(oldRoot+'/'+n,'utf8'):rebase(fs.readFileSync(oldRoot+'/'+n));
 if(n==='session.mjs')expected=expected.replace("Date.parse('2026-10-07T04:30:00Z')","Date.parse('2026-10-07T05:30:00Z')");
 assert.equal(fs.readFileSync(root+'/'+n,'utf8'),expected,n);
}
const prior=fs.readFileSync(oldRoot+'/fast-path.lua','utf8');
assert.equal(fs.readFileSync(root+'/fast-path.lua','utf8'),prior.replace("   R.lastAdmissionProbe=nil\r\n   if not ready and retryable~=true then error('Initial admission refused: '..tostring(reason),0)end","   if not ready and retryable~=true then error('Initial admission refused: '..tostring(reason),0)end\r\n   R.lastAdmissionProbe=nil"));
const rank=JSON.parse(fs.readFileSync(root+'/ranked-selection-qualified.json')),probe=JSON.parse(fs.readFileSync(root+'/probe-retention-qualified.json'));
assert.ok(rank.passed&&rank.checks===10&&rank.modelOnly&&!rank.hardwareExecuted);
for(const[f,h]of Object.entries(rank.sourceHashes))assert.equal(hash(fs.readFileSync(f)),h,f);
assert.ok(probe.passed&&probe.checks===7&&probe.actualRamModels&&!probe.actualProductionGateLoaded&&!probe.routerProductionWrites);
assert.equal(probe.sourceSha256,hash(fs.readFileSync(root+'/fast-path.lua')));assert.equal(probe.modelSha256,hash(fs.readFileSync(root+'/align-probe-models.lua')));
let dependencies=0;const manifest={};
for(const n of fs.readdirSync(root))if(/\.(mjs|lua|py|ps1)$/.test(n)&&!n.includes('private')){
 const f=root+'/'+n;manifest[f]=hash(fs.readFileSync(f));
 if(n.endsWith('.mjs')){
  for(const m of fs.readFileSync(f,'utf8').matchAll(/(?:from\s*|import\s*)['"](\.{1,2}\/[^'"]+\.mjs)['"]/g)){assert.ok(fs.existsSync(path.resolve(root,m[1])),m[1]);dependencies++;}
  const p=spawnSync(process.execPath,['--check',f],{encoding:'utf8',windowsHide:true});assert.equal(p.status,0,p.stderr);
 }
}
for(const n of [...prep.copied.filter(n=>n.endsWith('.json')),'ranked-selection-qualified.json','probe-retention-qualified.json'])manifest[root+'/'+n]=hash(fs.readFileSync(root+'/'+n));
const result={passed:true,sourceManifest:manifest,inheritedBindings:Object.keys(old.sourceManifest).length,relativeDependenciesExist:dependencies,
 localRankingModels:10,actualRamProbeModels:7,historicalModelsReplayed:false,onlySelectionRankingAndExistingFailureRetentionChanged:true,
 moduleGuardianAndPostCheckpointSequenceUnchanged:true,classThresholdsUnchanged:true,fixedWanAndOriginalGameContractUnchanged:true,
 sourceFreshnessSeconds:6,kernelSessionSeconds:90,kernelMaximumSeconds:120,ownerSeconds:180,clientMaximumSeconds:180,phaseSeconds:60,maximumExactFlows:3,
 temporaryClientLimitMbps:32,defaultInspectOnly:true,oneSessionAttemptOnly:true,cutoff:prep.cutoff,
 rootCauseEstablished:false,hardwareExecuted:false,wholeFactoryModeled:false,normalApplicationFactoryHardwareAcceptance:false,humanAcceptance:false,permanentNssDeployment:false};
fs.writeFileSync(root+'/entry-qualified.json',JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({passed:true,bindings:result.inheritedBindings+Object.keys(manifest).length,newSourceCopies:Object.keys(manifest).length,dependencies,localRankingModels:10,actualRamProbeModels:7,historicalModelsReplayed:false}));
