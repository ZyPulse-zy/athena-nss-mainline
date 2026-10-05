import {verifyDeployment} from '../nss68/deployment-binding.mjs';
// Same full native audit and freshness predicates; a per-experiment service reference.
import {waitReady} from '../nss68/wait-publication-metadata.mjs';
import {render} from '../nss49/audit-renderer.mjs';
import {verifyPreparation} from './session-binding.mjs';
import {adoptServices,verifyEpochServices} from '../nss50/service-epoch.mjs';
import fs from 'node:fs';import assert from 'node:assert/strict';
import {connectRouter} from '../nss20/connect-router.mjs';
import {readBaseline,auditBaseline} from '../nss15/baseline.mjs';
import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
verifyPreparation();
const label=process.argv[2];assert.match(label,/^[a-zA-Z0-9_-]+$/);
const purpose=process.argv[3];assert.ok(['prewrite','recovery'].includes(purpose));
const caseDir=process.argv[4];assert.match(caseDir,/^work\/nss79\/controlled-matched-aba-\d+-[a-f0-9]+$/);
const refPath=caseDir+'/service-epoch-private.json';
const {deployment:ctx}=verifyDeployment();
const historical=JSON.parse(fs.readFileSync(ctx.localDir+'/before-private.json'));
const c=await connectRouter();try{
 const after=await readBaseline(c,'work/nss79',label+'-baseline');
 const service=after.services['router-project-game-classifier'];
 assert.equal(service.classifier.running,true);assert.equal(service.guardian.running,true);assert.equal(Object.keys(service).length,2);
 let epoch,hint;
 if(purpose==='prewrite'){
  assert.ok(!fs.existsSync(refPath),'Cannot replace an existing service epoch');
  const adopted=adoptServices(historical.services,after.services);
  epoch={version:1,observedAt:new Date().toISOString(),boot:after.boot,services:adopted.services,changes:adopted.changes,routerWrites:false};
  fs.writeFileSync(refPath,JSON.stringify(epoch,null,2)+'\n',{flag:'wx'});
  hint=await waitReady(c,ctx,label);
 }else{
  epoch=JSON.parse(fs.readFileSync(refPath));assert.equal(epoch.version,1);assert.equal(epoch.boot,after.boot);
  verifyEpochServices(epoch.services,after.services);
 }
 const code=render(fs.readFileSync('work/nss23/operational-audit.lua','utf8'));
 const body='exec 8>/tmp/router-project-transaction.lock\nflock -x 8\n/usr/bin/lua - '+ctx.base+' '+ctx.configHash+" <<'NSS23_AUDIT'\n"+code+'\nNSS23_AUDIT\n';
 const e=encode(ctx.base+'/group-runner 6 /bin/sh -c '+"'"+body.replaceAll("'","'\\''")+"'");
 const raw=receipt(await c.run(e.command),e);
 fs.writeFileSync('work/nss79/'+label+'-ownership-raw-private.json',JSON.stringify(raw,null,2)+'\n',{flag:'wx'});
 assert.equal(raw.code,0,raw.stderr);const envelope=JSON.parse(raw.stdout);
 fs.writeFileSync('work/nss79/'+label+'-diagnostic-audit-private.json',JSON.stringify({...envelope,observedAt:new Date().toISOString()},null,2)+'\n',{flag:'wx'});
 assert.equal(envelope.passed,true,envelope.error);const proof=envelope.result;
 fs.writeFileSync('work/nss79/'+label+'-ownership-private.json',JSON.stringify(proof,null,2)+'\n',{flag:'wx'});
 assert.equal(service.classifier.pid,proof.pid);assert.equal(service.guardian.pid,proof.guardianPid);
 if(purpose==='prewrite'){assert.equal(proof.producer,hint.producer,'Original full audit producer differs from classification hint');assert.equal(proof.querySequence,hint.selectedSequence,'Original full audit query differs from classification hint');}
 const adjusted={...after,native:historical.native,services:{...after.services}};
 adjusted.services['router-project-game-classifier']=historical.services['router-project-game-classifier'];
 const reference={...historical,services:{...epoch.services}};
 reference.services['router-project-game-classifier']=historical.services['router-project-game-classifier'];
 const baseline=auditBaseline(reference,adjusted);
 const out={passed:true,auditPurpose:purpose,prelearningSchedulingRequested:purpose==='prewrite',nssAdmissionAllowed:false,originalLockedFreshnessPredicatesRetained:true,protectedConfigurationUnchanged:baseline.configurationMatches,exactOwnedNativeAudit:proof.exactOwnedNativeAudit,selectors:proof.selectors,queryAge:proof.queryAge,sequence:proof.querySequence,ecmClosedAndZero:baseline.checks.ecmStoppedAndZero,serviceEpochPinned:true,servicePidChangesAcknowledgedBeforeExperiment:epoch.changes,serviceChangesDuringExperimentAllowed:false};
 fs.writeFileSync('work/nss79/'+label+'-audit.json',JSON.stringify(out,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(out));
}finally{c.close()}
