import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {connectRouter} from '../nss20/connect-router.mjs';
const root='work/nss35',read=p=>JSON.parse(fs.readFileSync(p));const ctx=read(root+'/deployment-latest.json'),obs=read(root+'/trial-observation.json');
assert.equal(ctx.committed,false);assert.equal(obs.semantic.passed,true);assert.equal(obs.semantic.identityDecisionLeafAndExpiryEqual,true);
assert.ok(obs.rows.length>=30);assert.ok(obs.rows.every(s=>s.status==='running'&&s.guardianHealthy&&s.accel===0&&s.frontend===1));assert.equal(new Set(obs.rows.map(s=>s.producer)).size,1);
const rollback=read(ctx.localDir+'/rollback-qualified.json'),audit=read(ctx.localDir+'/trial-before-rollback-audit.json');assert.equal(rollback.passed,true);assert.equal(rollback.automaticExpiryWithoutControllerRollback,true);assert.equal(audit.passed,true);
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');const source=read(root+'/recovery-qualified.json');for(const n of ['worker.lua','guardian.lua'])assert.equal(source.sourceSha256[n],sha(root+'/'+n));
const names=['recovery-qualified.json','query-local-qualified.json','query-native-qualified.json','history-native-qualified.json','projection-qualified.json'];let checks=0;
for(const n of names){const p=read(root+'/'+n);assert.equal(p.passed,true);checks+=p.checks;}
const proof={passed:true,observedAt:new Date().toISOString(),workerSha256:sha(root+'/worker.lua'),guardianSha256:sha(root+'/guardian.lua'),checks,trialTransaction:ctx.transactionId,trialConfigSha256:ctx.configHash,healthySamples:obs.rows.length,producerStable:true,semantic:obs.semantic,independentRollback:rollback,protectedAudit:audit,productionAddressFaultInjected:false,underlyingBlockingOrSignalRootCauseProved:false,highLoadQualified:false,nssEnabled:false};
fs.writeFileSync(root+'/address-trial-qualified.json',JSON.stringify(proof,null,2)+'\n');fs.writeFileSync(ctx.localDir+'/deployment-trial.json',JSON.stringify(ctx,null,2)+'\n');
const c=await connectRouter();try{await c.upload(ctx.localDir+'/cancel',ctx.stagePath+'/cancel');}finally{c.close()}
console.log(JSON.stringify({passed:true,checks,healthySamples:obs.rows.length,independentRollback:true,stageCancellationRequested:true,nssEnabled:false}));
