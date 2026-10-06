import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';import {spawnSync} from 'node:child_process';
import {verifyPreparation as prior} from '../nss147/session-binding.mjs';
import {packLua} from './pack-lua.mjs';import {packGuardian} from './pack-guardian.mjs';import {buildPayload} from './payload.mjs';
import {packetTemplate} from './uplink-tag-plan.mjs';import {mapClassifiedPair} from '../nss127/class-leaf-map.mjs';
import {connectRouter} from '../nss27/connect-router.mjs';import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
const root='work/nss149',h=b=>crypto.createHash('sha256').update(b).digest('hex'),old=prior();
const version=process.argv[2];assert.match(version,/^v\d+$/);const proofDir=root+'/qualification-'+version;fs.mkdirSync(proofDir);
const fast=fs.readFileSync(root+'/fast-path.lua','utf8'),previous=fs.readFileSync('work/nss147/fast-path.lua','utf8');
let expected=previous.replace('R.abaVersion=140;','R.lifecycleVersion=149;')
 .replace("R.qosAtA=qos.snapshot();measure('A');G('tagsAfterA',I)","tick('CLOSED');G('tagsBeforeLearning',I)")
 .replace("G('tagsBeforeA2',I);measure('A2');G('tagsAfterA2',I)","G('tagsAfterLifecycle',I);tick('CLOSED')")
 .replace('R.qosAfterA2=qos.snapshot();','')
 .replace('R.fastPathEpochCompleted=true;R.abaCompleted=true','R.fastPathEpochCompleted=true;R.abaCompleted=false;R.automaticLifecycleEpochCompleted=true')
 .replaceAll('R.phases[2]','R.phases[1]').replace('Native session lacks ABA retirement margin','Native session lacks lifecycle retirement margin')
 .replace('local function measure(name)','local function measure()')
 .replace("R.deadline-(name=='A'and 78 or name=='B'and 55 or 28)",'R.deadline-55')
 .replace('local p={name=name,requestedSeconds',"local p={name='B',requestedSeconds")
 .replace('local s=tick(name);last=s',"local s=tick('B');last=s")
 .replace("qos.snapshot();measure('B')",'qos.snapshot();measure()');
const actualText=packLua(fast),expectedText=packLua(expected);
if(actualText!==expectedText){let i=0;while(i<Math.min(actualText.length,expectedText.length)&&actualText[i]===expectedText[i])i++;
 fs.writeFileSync(proofDir+'/static-source-diff.json',JSON.stringify({index:i,actual:actualText.slice(i-100,i+200),expected:expectedText.slice(i-100,i+200)},null,2)+'\n',{flag:'wx'});
 throw Error('Undeclared static source change; exact first difference retained');}
const guardian=fs.readFileSync(root+'/module-stage-guardian.lua','utf8');
assert.equal(guardian,fs.readFileSync('work/nss147/module-stage-guardian.lua','utf8').replace('if record.classChangeTestCompleted or record.freshEpochRelearningCompleted then','if record.automaticLifecycleEpochCompleted or record.classChangeTestCompleted or record.freshEpochRelearningCompleted then'));
for(const name of ['classifier.lua','qos-physical.lua','tag-normalizer.lua','pack-lua.mjs','pack-guardian.mjs','compact-default-queues.mjs','uplink-tag-plan.mjs','parse-ecm-any-wan.mjs','failed-wan-owner.lua','declared-baseline.mjs','service-epoch.mjs'])assert.equal(h(fs.readFileSync(root+'/'+name)),h(fs.readFileSync('work/nss147/'+name)),name);
const d='work/nss147/controlled-matched-aba-20261006030739-426623cb';
const frame=JSON.parse(fs.readFileSync(d+'/post-checkpoint-controlled-receipt-private.json')),plan=JSON.parse(fs.readFileSync(d+'/stage-plan-private.json'));
const selected=structuredClone(plan.selected);for(const f of Object.values(selected))delete f.classifierKey;
const mapped=mapClassifiedPair(frame,selected),template=packetTemplate(mapped,plan.tagPlan.owner,plan.selected.udp.original.sport===59999?59998:59999);
template.expected.nftables=template.expected.nftables.filter(x=>x.chain?.name!=='forward'&&x.rule?.chain!=='forward');
const helpers={qos:fs.readFileSync(root+'/qos-physical.lua','utf8'),phase:fs.readFileSync('work/nss69/core-guard-phase.lua','utf8'),classifier:fs.readFileSync(root+'/classifier.lua','utf8'),tags:fs.readFileSync('work/nss49/classified-tags.lua','utf8'),normalizer:fs.readFileSync(root+'/tag-normalizer.lua','utf8')};
const payload=buildPayload({tagPlan:{table:template.expected.nftables[0].table.name,owner:plan.tagPlan.owner,mode:'rt',expected:template.expected}},helpers);
const payloadBytes=Buffer.byteLength(payload.stagedCode);assert.ok(payloadBytes<=73728);
for(const k of ['guardianSourceSha256','selectedGuardianSha256','oneEpochControlledPair','phaseSourceSha256','qosSourceSha256','execBytes'])delete plan[k];
plan.qosCodeBytes=payloadBytes;plan.qosCodeSha256=h(payload.stagedCode);
const packedGuardian=packGuardian(guardian).replace('__PLAN__',()=>JSON.stringify(plan)).replace('__CORE_PHASE__',()=> 'return{}').replace('__QOS_PHYSICAL__',()=> 'return{}');
const ge=encode("/usr/bin/lua - <<'NSS20_STAGE_BEGIN'\n"+packedGuardian+"\nNSS20_STAGE_BEGIN\n");assert.ok(ge.execBytes<=9000);
const cut=(s,a,b)=>{const i=s.indexOf(a),z=s.indexOf(b,i);assert.ok(i>=0&&z>i,'Actual function extraction failed: '+a);return s.slice(i,z);};
const nativeCode="local j=require('luci.jsonc');\n"+fs.readFileSync(root+'/lifecycle-models.lua','utf8')
 .replace('__TICK_MEASURE__',()=>cut(fast,' local function tick(name)',' function out.align(deadline)'))
 .replace('__RUN__',()=>cut(fast,' function out.run(due,',' return out'));
fs.writeFileSync(proofDir+'/lifecycle-model-rendered-private.lua',nativeCode,{flag:'wx'});
const enc=encode("lua - <<'NSS149_LIFECYCLE_MODEL'\n"+nativeCode+"\nNSS149_LIFECYCLE_MODEL\n");
const syntax=encode("lua - <<'NSS149_SYNTAX'\nassert(loadstring([====["+packLua(fast)+"]====]));print('FAST_SYNTAX_OK')\nNSS149_SYNTAX\n");
const pr=spawnSync(process.execPath,[root+'/policy-models.mjs'],{encoding:'utf8',windowsHide:true});
fs.writeFileSync(proofDir+'/policy-model-raw-private.json',JSON.stringify({code:pr.status,stdout:pr.stdout,stderr:pr.stderr},null,2)+'\n',{flag:'wx'});
assert.equal(pr.status,0,'Supervisor policy failed; exact failure retained');const policyModels=JSON.parse(pr.stdout);assert.ok(policyModels.passed&&policyModels.checks===35);
let nativeModels;const c=await connectRouter();
try{
 const raw=receipt(await c.run(enc.command),enc);fs.writeFileSync(proofDir+'/lifecycle-model-raw-private.json',JSON.stringify(raw,null,2)+'\n',{flag:'wx'});assert.equal(raw.code,0,'RAM model failed; exact failure retained');nativeModels=JSON.parse(raw.stdout);assert.ok(nativeModels.passed&&nativeModels.checks===5);
 const sr=receipt(await c.run(syntax.command),syntax);fs.writeFileSync(proofDir+'/syntax-raw-private.json',JSON.stringify(sr,null,2)+'\n',{flag:'wx'});assert.equal(sr.code,0);assert.equal(sr.stdout.trim(),'FAST_SYNTAX_OK');
}finally{c.close()}
const sourceManifest={};for(const name of fs.readdirSync(root))if(/\.(mjs|py|ps1|lua)$/.test(name)&&!name.includes('private')){
 const file=root+'/'+name;sourceManifest[file]=h(fs.readFileSync(file));
 if(name.endsWith('.mjs')){const p=spawnSync(process.execPath,['--check',file],{encoding:'utf8',windowsHide:true});assert.equal(p.status,0,p.stderr);}
 if(name.endsWith('.py')){const p=spawnSync('C:/Users/lishu/AppData/Local/Programs/Python/Python312/python.exe',['-c','import sys;compile(open(sys.argv[1],encoding="utf-8").read(),sys.argv[1],"exec")',file],{encoding:'utf8',windowsHide:true});assert.equal(p.status,0,p.stderr);}
}
const proof={passed:true,at:new Date().toISOString(),finiteTwoEpochSupervisor:true,actualNewRunModeled:true,fullFactoryModeled:false,productionExecution:false,
 inheritedBoundInputs:Object.keys(old.sourceManifest).length,sourceManifest,budgets:[6,27,100,9000,65536,73728],payloadBytes,
 qualificationGuardianExecBytes:ge.execBytes,modelExecBytes:enc.execBytes,syntaxExecBytes:syntax.execBytes,
 policyModels,nativeModels,exactPermanentClassifierAndNativeGateUnchanged:true,
 actualClassChangeRetirementImplementationUnchanged:true,newOwnerAfterCompleteRestorationOnly:true,desktopOperated:false};
fs.writeFileSync(root+'/entry-qualified.json',JSON.stringify(proof,null,2)+'\n',{flag:'wx'});
const verified=(await import('./session-binding.mjs')).verifyPreparation();
console.log(JSON.stringify({passed:true,bindings:Object.keys(verified.sourceManifest).length,payloadBytes,guardianExecBytes:ge.execBytes,modelExecBytes:enc.execBytes,policyChecks:policyModels.checks,nativeChecks:nativeModels.checks,routerWrites:false}));
