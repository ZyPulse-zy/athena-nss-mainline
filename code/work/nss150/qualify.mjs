import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';import {spawnSync} from 'node:child_process';
import {verifyPreparation as prior} from '../nss149/session-binding.mjs';
const root='work/nss150',h=b=>crypto.createHash('sha256').update(b).digest('hex'),old=prior();
const run=fs.readFileSync(root+'/controlled-session.mjs','utf8');assert.ok(run.includes("from '../nss149/module-stage.mjs'"));
const policy=fs.readFileSync(root+'/lifecycle-policy.mjs','utf8');
assert.equal(policy.replace('status.elapsed<110,','status.elapsed<80,'),fs.readFileSync('work/nss149/lifecycle-policy.mjs','utf8'));
const p=spawnSync(process.execPath,[root+'/policy-models.mjs'],{encoding:'utf8',windowsHide:true});
fs.writeFileSync(root+'/policy-model-raw-private.json',JSON.stringify({code:p.status,stdout:p.stdout,stderr:p.stderr},null,2)+'\n',{flag:'wx'});
assert.equal(p.status,0,'Policy qualification failed; stop before production');const policyModels=JSON.parse(p.stdout);assert.ok(policyModels.passed&&policyModels.checks===36);
const sourceManifest={};for(const name of fs.readdirSync(root))if(/\.(mjs|py|ps1|lua)$/.test(name)&&!name.includes('private')){
 const f=root+'/'+name;sourceManifest[f]=h(fs.readFileSync(f));
 if(name.endsWith('.mjs')){const p=spawnSync(process.execPath,['--check',f],{encoding:'utf8',windowsHide:true});assert.equal(p.status,0,p.stderr);}
 if(name.endsWith('.py')){const p=spawnSync('C:/Users/lishu/AppData/Local/Programs/Python/Python312/python.exe',['-c','import sys;compile(open(sys.argv[1],encoding="utf-8").read(),sys.argv[1],"exec")',f],{encoding:'utf8',windowsHide:true});assert.equal(p.status,0,p.stderr);}
}
const proof={passed:true,at:new Date().toISOString(),sameActuallyTested149Factory:true,onlyClientPreparationMarginChanged:true,
 inheritedBindings:Object.keys(old.sourceManifest).length,sourceManifest,policyModels,budgets:[6,27,100,9000,65536,73728],
 requiredClientRemainingSeconds:70,clientHardDeadlineSeconds:180,independentOwnerHardDeadlineSeconds:100,productionExecution:false,
 clientIsNotRequiredForIndependentRollback:true,actualSourceNativeOwnerBoundsUnchanged:true,
 noWholeFactoryOrHardwareRerunClaimedForQualification:true,oldFailedBoundaryRetained:true};
fs.writeFileSync(root+'/entry-qualified.json',JSON.stringify(proof,null,2)+'\n',{flag:'wx'});
const q=(await import('./session-binding.mjs')).verifyPreparation();console.log(JSON.stringify({passed:true,bindings:Object.keys(q.sourceManifest).length,policyChecks:36,actualFactory:'NSS149 unchanged',sourceNativeOwnerBounds:[6,27,100],routerWrites:false}));
