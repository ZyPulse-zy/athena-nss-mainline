// Consolidate the completed software repairs into one RC; historical batches stay immutable.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import {root, digest} from './build-classifier.mjs';

const sourceRoot='work/v66-final-selection';
const names=['entry.mjs','materialize.mjs','check-model.mjs','platform-preflight.mjs',
 'fixture-startup.mjs','ssh-phase.mjs','ssh-options.mjs','persistent-ssh.mjs','resident-window.mjs',
 'route-acquisition.mjs','acquisition-order.mjs','selected-acquisition.mjs','udp-discovery.mjs',
 'eligible-selection.mjs','full-classification.mjs','record-classification.mjs','final-selection.mjs',
 'udp-probe.py','udp-probe.mjs','check-udp-path.mjs','recheck-partial-endpoint.mjs',
 'capture-no-client-closure.ps1','recheck-endpoint-readonly.mjs','prepare.mjs',
 'check-frame-identity.mjs','check-route-acquisition.mjs','check-selected-acquisition.mjs',
 'check-udp-discovery.mjs','check-final-selection.mjs'];
const copied=[];
for(const name of names){
 let source=fs.readFileSync(sourceRoot+'/'+name,'utf8').replaceAll('v66-final-selection','resident-dev-20261007').replaceAll('v66-run-','resident-rc1-run-');
 if(name==='materialize.mjs'){
  const anchor="  fs.writeFileSync(runtimeRoot+'/'+name,bytes,{flag:'wx'});";
  assert.equal(source.split(anchor).length,2);
  source=source.replace(anchor,`  if(path.extname(name)==='.mjs')bytes=Buffer.from(bytes.toString().replaceAll('../nss68/deployment-binding.mjs','../resident-dev-20261007/deployment-binding.mjs'));
`+anchor);
  source=source.replace('classificationAndQosPolicyUnchanged:true','rtAndQosPolicyUnchanged:true,tcpBulkShapeCorrection:true');
  const bind="generatedHashes[entryRoot+'/'+name]=hash(fs.readFileSync(entryRoot+'/'+name));";
  assert.equal(source.split(bind).length,2);
  source=source.replace(bind,bind+"\n for(const name of ['classifier-core.lua','classifier-build.json','build-classifier.mjs','deployment-binding.mjs','classifier-tests-latest.json'])generatedHashes[entryRoot+'/'+name]=hash(fs.readFileSync(entryRoot+'/'+name));");
 }
 if(name==='check-model.mjs')source=source.replace('q.classificationAndQosPolicyUnchanged','q.rtAndQosPolicyUnchanged&&q.tcpBulkShapeCorrection');
 if(name==='entry.mjs')source=source.replace("const mode=process.argv[2]??'inspect';","const mode=process.argv[2]??'inspect';");
 if(name==='check-final-selection.mjs'){
  // The previous completed runtime supplies immutable classification fixtures;
  // this is local regression, not an execution of that runtime.
  source=source.replaceAll('work/resident-rc1-run-20261007145152-711b56e2','work/v65-run-20261007145152-711b56e2');
 }
 const target=root+'/'+name;
 if(fs.existsSync(target))assert.equal(fs.readFileSync(target,'utf8'),source,target);
 else fs.writeFileSync(target,source,{flag:'wx'});
 copied.push({file:name,sha256:digest(Buffer.from(source))});
}
console.log(JSON.stringify({consolidatedFiles:copied.length,formalHardwareVersionCreated:false,routerAccess:false}));
