import fs from'node:fs';import path from'node:path';import crypto from'node:crypto';import assert from'node:assert/strict';import{spawnSync}from'node:child_process';import{verifyPreparation as inherited}from'../v26-normal/session-binding.mjs';
const root='work/v30-normal',oldRoot='work/v26-normal',old=inherited(),hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const rebase=b=>b.toString('utf8').replaceAll(oldRoot,root).replaceAll('work\\/v26-normal\\/','work\\/v30-normal\\/');
const prepared=JSON.parse(fs.readFileSync(root+'/prepare-receipt.json'));
for(const[name,h]of Object.entries(prepared.oldHashes))assert.equal(hash(fs.readFileSync(oldRoot+'/'+name)),h,'Frozen v26 changed: '+name);
for(const name of prepared.copied){
 let expected=rebase(fs.readFileSync(oldRoot+'/'+name));
 if(name==='session.mjs'){
  expected=expected.replace("assert.ok(Date.now()<Date.parse('2026-10-06T23:40:00Z'),'Night production authorization has expired');", "assert.ok(Date.now()<Date.parse('2026-10-07T01:30:00Z'),'Current bounded application authorization has expired');\r\n fs.writeFileSync(root+'/one-session-attempt.json',JSON.stringify({startedAt:new Date().toISOString(),oneAttemptOnly:true,source:'Current human continuation after morning closure'})+'\\n',{flag:'wx'});");
 }
 assert.equal(fs.readFileSync(root+'/'+name,'utf8'),expected,name+' unexpected semantic change');
}
const dataPlane=['classified-tags.lua','classifier.lua','fast-path.lua','wan-scope.lua','qos-physical.lua','tag-normalizer.lua','module-stage-guardian.lua','class-leaf-map.mjs','module-stage.mjs','payload.mjs','parse-ecm.mjs','wan-tag-plan.mjs','candidate-policy.mjs','guardian-plan.mjs'];
for(const name of dataPlane)assert.equal(fs.readFileSync(root+'/'+name,'utf8'),rebase(fs.readFileSync(oldRoot+'/'+name)));
const models=JSON.parse(fs.readFileSync(root+'/normal-policy-qualified.json'));assert.ok(models.passed&&models.checks===18&&models.modelOnly);
let dependencies=0;const manifest={};
for(const name of fs.readdirSync(root))if(/\.(mjs|lua|py)$/.test(name)){
 const file=root+'/'+name;manifest[file]=hash(fs.readFileSync(file));
 if(name.endsWith('.mjs')){const source=fs.readFileSync(file,'utf8');for(const m of source.matchAll(/(?:from\s*|import\s*)['"](\.{1,2}\/[^'"]+\.mjs)['"]/g)){assert.ok(fs.existsSync(path.resolve(root,m[1])),'Missing import '+m[1]);dependencies++;}const p=spawnSync(process.execPath,['--check',file],{encoding:'utf8',windowsHide:true});assert.equal(p.status,0,p.stderr);}
}
for(const name of['native-qualified.json','normalizer-qualified.json','qos-native-qualified.json','normal-policy-qualified.json']){assert.deepEqual(fs.readFileSync(root+'/'+name),fs.readFileSync(oldRoot+'/'+name));manifest[root+'/'+name]=hash(fs.readFileSync(root+'/'+name));}
const q={passed:true,sourceManifest:manifest,inheritedBindings:Object.keys(old.sourceManifest).length,hardwareExecuted:false,wholeFactoryModeled:false,exactV26DataPlaneAndPolicyAfterPathRebase:true,onlySessionChange:'Current cutoff and single-attempt local claim',oneSessionAttemptOnly:true,normalModelsReused:18,relativeDependenciesExist:dependencies,sourceFreshnessSeconds:6,kernelSessionSeconds:90,kernelMaximumSeconds:120,ownerSeconds:180,phaseSeconds:60,maximumExactFlows:3,defaultInspectOnly:true,normalApplicationFactoryHardwareAcceptance:false,humanAcceptance:false,permanentNssDeployment:false};
fs.writeFileSync(root+'/entry-qualified.json',JSON.stringify(q,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({passed:true,bindings:Object.keys(old.sourceManifest).length+Object.keys(manifest).length,relativeDependencies:dependencies,dataPlaneChanged:false,hardwareExecuted:false}));
