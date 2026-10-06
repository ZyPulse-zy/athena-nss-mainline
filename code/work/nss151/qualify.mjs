import fs from'node:fs';import path from'node:path';import assert from'node:assert/strict';import crypto from'node:crypto';import{spawnSync}from'node:child_process';
import{verifyPreparation as prior}from'../nss150/session-binding-v5.mjs';
const root='work/nss151',h=b=>crypto.createHash('sha256').update(b).digest('hex'),old=prior();
const version=process.argv[2];assert.match(version,/^v\d+$/);const dir=root+'/qualification-'+version;fs.mkdirSync(dir);
const save=(n,v)=>fs.writeFileSync(dir+'/'+n+'.json',JSON.stringify(v,null,2)+'\n',{flag:'wx'});
const first=JSON.parse(fs.readFileSync('work/nss138/entry-qualified.json'));
assert.equal(first.passed,true);for(const[f,d]of Object.entries(first.sourceManifest)){assert.equal(h(fs.readFileSync(f)),d);assert.equal(old.sourceManifest[f],d,'Unbound native class-change input: '+f);}
const sourceManifest={};
for(const name of fs.readdirSync(root))if(/\.(mjs|py|ps1|lua)$/.test(name)&&!name.includes('private')){
 const file=root+'/'+name,text=fs.readFileSync(file,'utf8');sourceManifest[file]=h(fs.readFileSync(file));
 if(name.endsWith('.mjs'))for(const m of text.matchAll(/from\s*['"]([^'"]+)['"]/g))if(m[1].startsWith('.'))assert.ok(fs.existsSync(path.resolve(path.dirname(file),m[1])),'Missing relative import: '+file+' '+m[1]);
 for(const m of text.matchAll(/['"](work\/nss151\/[^'"\n]+\.(?:mjs|lua|py|ps1))['"]/g))assert.ok(fs.existsSync(m[1]),'Missing own static source: '+m[1]);
 if(name.endsWith('.mjs')){const p=spawnSync(process.execPath,['--check',file],{encoding:'utf8',windowsHide:true});save(name+'-syntax',{code:p.status,stdout:p.stdout,stderr:p.stderr});assert.equal(p.status,0);}
 if(name.endsWith('.py')){const p=spawnSync('C:/Users/lishu/AppData/Local/Programs/Python/Python312/python.exe',['-c','import sys;compile(open(sys.argv[1],encoding="utf-8").read(),sys.argv[1],"exec")',file],{encoding:'utf8',windowsHide:true});save(name+'-syntax',{code:p.status,stdout:p.stdout,stderr:p.stderr});assert.equal(p.status,0);}
}
const p=spawnSync(process.execPath,[root+'/policy-models.mjs'],{encoding:'utf8',windowsHide:true});save('policy-model-raw-private',{code:p.status,stdout:p.stdout,stderr:p.stderr});assert.equal(p.status,0,'Transition policy failed; exact output kept privately');
const models=JSON.parse(p.stdout);assert.ok(models.passed&&models.checks>=35);
for(const f of ['ssh-client.mjs','bounded-pacer.mjs','upload-ack.mjs','upload-server.py','watcher-read.lua'])assert.equal(h(fs.readFileSync(root+'/'+f)),h(fs.readFileSync('work/nss138/'+f)),f);
assert.equal(h(fs.readFileSync(root+'/endpoint-firewall-guardian.py')),h(fs.readFileSync('work/nss150/endpoint-firewall-guardian.py')));
const change=fs.readFileSync(root+'/class-session.mjs','utf8'),stable=fs.readFileSync(root+'/epoch-session.mjs','utf8');
assert.ok(change.includes("from '../nss138/module-stage.mjs'")&&stable.includes("from '../nss149/module-stage.mjs'"));
assert.ok(change.includes("const continuityPath=process.argv[3];assert.equal(continuityPath,'work/nss151/run/continuity-private.json')"));
assert.ok(stable.includes("const continuityPath=process.argv[3];assert.equal(continuityPath,'work/nss151/run/continuity-private.json')"));
const upload=fs.readFileSync(root+'/start-dallas.mjs','utf8');assert.ok(upload.includes("config.bulkDirection='upload'")&&upload.includes('seconds:180')&&upload.includes('expirySeconds:180'));
const q={passed:true,inheritedBindings:Object.keys(old.sourceManifest).length,sourceManifest,existingNativeFactoriesUnchanged:true,
 firstFactory:'work/nss138/module-stage.mjs',successorFactory:'work/nss149/module-stage.mjs',defaultRejectUnknownTransition:true,
 freshOwnerOnlyAfterCompleteRestoration:true,onlyApplicationPayloadPaused:true,sameTcpSocketAndUdpRequired:true,
 models,budgets:[6,27,100,9000,65536,73728],clientHardSeconds:180,clientPreparationRemainingSeconds:70,
 sourceClosureBeforeEndpointTraffic:true,firstAndSuccessorCheckpointsRequired:true,permanentClassifierChanged:false,
 entireIntegratedSupervisorModeled:false,integratedHardwareProof:false,productionExecution:false};
fs.writeFileSync(root+'/entry-qualified.json',JSON.stringify(q,null,2)+'\n',{flag:'wx'});
const verified=(await import('./session-binding.mjs')).verifyPreparation();save('qualification',q);
console.log(JSON.stringify({passed:true,bindings:Object.keys(verified.sourceManifest).length,newSources:Object.keys(sourceManifest).length,policyChecks:models.checks,nativeFactoryCodeChanged:false,routerWrites:false}));
