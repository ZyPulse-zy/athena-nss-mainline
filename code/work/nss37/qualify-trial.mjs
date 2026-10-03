import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';import {connectRouter} from '../nss20/connect-router.mjs';
const root='work/nss37',read=p=>JSON.parse(fs.readFileSync(p)),hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const ctx=read(root+'/deployment-latest.json'),obs=read(root+'/trial-observation.json'),rollback=read(ctx.localDir+'/rollback-qualified.json');
assert.equal(ctx.committed,false);assert.ok(rollback.passed&&rollback.automaticExpiryWithoutControllerRollback&&rollback.previousNormalizerAndGuardianRestored);
assert.ok(obs.semantic.passed&&obs.semantic.identityDecisionLeafAndExpiryEqual&&obs.rows.length===35);
assert.ok(obs.rows.every(v=>v.status==='running'&&v.guardianHealthy&&v.accel===0&&v.frontend===1));assert.equal(new Set(obs.rows.map(v=>v.producer)).size,1);
const audit=read(ctx.localDir+'/trial-before-rollback-audit.json'),restored=read(root+'/restored-audit.json');assert.ok(audit.passed&&restored.passed&&restored.ecmClosedAndZero);
const local=read(root+'/normalizer-qualified.json'),native=read(root+'/native-normalizer-qualified.json'),life=read(root+'/lifecycle-qualified.json');
assert.ok(local.passed&&native.passed&&life.passed);assert.equal(local.sourceSha256,hash(root+'/conntrack-source.lua'));assert.equal(native.sourceSha256,local.sourceSha256);assert.equal(life.ctSourceSha256,local.sourceSha256);
const proof={passed:true,observedAt:new Date().toISOString(),sourceSha256:local.sourceSha256,workerSha256:hash(root+'/worker.lua'),guardianSha256:hash(root+'/guardian.lua'),trialTransaction:ctx.transactionId,trialConfigSha256:ctx.configHash,localChecks:local.checks+life.checks,nativePairedSamples:native.results.reduce((n,r)=>n+r.samples.length,0),independentRollback:rollback,protectedAudit:audit,restoredAudit:restored,semantic:obs.semantic,healthySamples:obs.rows.length,producerStable:true,highLoadQualified:false,nssEnabled:false};
fs.writeFileSync(root+'/normalizer-trial-qualified.json',JSON.stringify(proof,null,2)+'\n');fs.writeFileSync(ctx.localDir+'/deployment-trial.json',JSON.stringify(ctx,null,2)+'\n');
const c=await connectRouter();try{await c.upload(ctx.localDir+'/cancel',ctx.stagePath+'/cancel');}finally{c.close()}
console.log(JSON.stringify({passed:true,checks:proof.localChecks,healthySamples:obs.rows.length,automaticRollback:true,stageCancellationRequested:true}));
