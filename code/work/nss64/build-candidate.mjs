// Build a single publication-boundary patch. Does not install or enable NSS.
import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const ctx=JSON.parse(fs.readFileSync('work/nss47/deployment-latest.json'));
const cfg=JSON.parse(fs.readFileSync(ctx.localDir+'/config.json'));
assert.equal(sha(fs.readFileSync(ctx.localDir+'/config.json')),ctx.configHash);
const original=fs.readFileSync(ctx.localDir+'/worker.lua','utf8');assert.equal(sha(original),cfg.files['worker.lua']);
const projector=fs.readFileSync('work/nss64/json-project-fast.lua','utf8');
const encoder=fs.readFileSync('work/nss64/flow-json-stream.lua','utf8');
const prefix='local PublicationProject=(function()\n'+projector+'\nend)()\nlocal PublicationStringify=(function()\n'+encoder+'\nend)()\n';
const marker='local function atomic(path,value)';assert.equal(original.split(marker).length,2);
const oldCall='local raw=assert(j.stringify(own.jsonProject(value)));assert(#raw<=4194304)';assert.equal(original.split(oldCall).length,2);
const newCall="local raw=assert(type(value)=='table'and type(value.snapshot)=='table'and type(value.snapshot.flows)=='table'and PublicationStringify(value,j,PublicationProject)or j.stringify(own.jsonProject(value)));assert(#raw<=4194304)";
const candidate=original.replace(marker,prefix+marker).replace(oldCall,newCall);
assert.equal(candidate.replace(prefix+marker,marker).replace(newCall,oldCall),original,'Unexpected worker change');
fs.writeFileSync('work/nss64/candidate-worker.lua',candidate);
const result={passed:true,candidateOnly:true,installed:false,originalWorkerSha256:sha(original),candidateWorkerSha256:sha(candidate),
 originalBytes:Buffer.byteLength(original),candidateBytes:Buffer.byteLength(candidate),projectorSha256:sha(projector),encoderSha256:sha(encoder),
 onlyChange:'Complete snapshot serialization; all other worker bytes and non-snapshot serialization unchanged',
 fullFieldsRetained:true,originalOwnedModuleUnchanged:true,originalMaxBytesRetained:4194304,originalAllDeadlinesRetained:true,
 classifierPolicyAndLearningUnchanged:true,pbrCtNatAndNssGateUnchanged:true,notHighLoadForwardingQualified:true};
fs.writeFileSync('work/nss64/candidate-worker-manifest.json',JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
