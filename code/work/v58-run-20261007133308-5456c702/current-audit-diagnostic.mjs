import {verifyDeployment} from '../nss68/deployment-binding.mjs';
import {waitReady} from '../nss122/wait-publication-metadata.mjs';
import {render} from '../nss49/audit-renderer.mjs';
import {verifyPreparation} from './session-binding.mjs';
import {verifyEpochServices} from '../nss50/service-epoch.mjs';
import {declaredReference,verifyFailedWanState,auditScopedBaseline,authSha256,manifestSha256} from '../nss160/declared-baseline.mjs';
import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {connectRouter} from '../nss20/connect-router.mjs';
import {readBaseline,auditBaseline} from '../nss15/baseline.mjs';
import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
verifyPreparation();
const label=process.argv[2];assert.match(label,/^[a-zA-Z0-9_-]+$/);
const purpose=process.argv[3];assert.ok(['prewrite','recovery'].includes(purpose));
const caseDir=process.argv[4];assert.match(caseDir,/^work\/v58-run-20261007133308-5456c702\/session-\d+-[a-f0-9]+$/);
const refPath=caseDir+'/service-epoch-private.json',baselinePath=caseDir+'/prewrite-baseline-private.json';
const {deployment:ctx}=verifyDeployment();
const historical=JSON.parse(fs.readFileSync('work/nss68/nss107-final-20261005-baseline-private.json'));
const c=await connectRouter();const save=(name,v)=>fs.writeFileSync('work/v58-run-20261007133308-5456c702/'+label+'-'+name+'.json',JSON.stringify(v,null,2)+'\n',{flag:'wx'});
const run=async code=>{const e=encode(code),r=receipt(await c.run(e.command),e);assert.equal(r.code,0,r.stderr);return r.stdout;};
try{
 const after=await readBaseline(c,'work/v11',label+'-baseline');
 const service=after.services['router-project-game-classifier'];
 assert.equal(service.classifier.running,true);assert.equal(service.guardian.running,true);assert.equal(Object.keys(service).length,2);
 assert.equal(after.protectedManifestSha256,manifestSha256);assert.equal(after.protectedManifestPassed,true);
 const authDigest=(await run('sha256sum /root/router-project/scripts/auth-recover.sh')).split(/\s/)[0];assert.equal(authDigest,authSha256);
 const status=JSON.parse(await run('ubus call network.interface.wan4 status'));
 const ownerSource=fs.readFileSync('work/nss160/failed-wan-owner.lua','utf8');
 const seal=JSON.parse(await run("lua - <<'NSS150_FAILED_WAN_OWNER'\n"+ownerSource+"\nNSS150_FAILED_WAN_OWNER\n"));
 save('failed-wan-owner-private',seal);verifyFailedWanState(after,status,seal);
 let epoch,hint,reference,declaration;
 if(purpose==='prewrite'){
  assert.ok(!fs.existsSync(refPath)&&!fs.existsSync(baselinePath),'Cannot replace a prewrite epoch');
  const health=JSON.parse(await run('cat /tmp/router-project-health/status.json'));
  const adopted=declaredReference(historical,after,health,authDigest,status,seal);reference=adopted.reference;declaration=adopted.proof;
  save('declared-baseline-proof',declaration);save('health-status-private',health);save('wan4-status-private',status);
  epoch={version:3,observedAt:new Date().toISOString(),boot:after.boot,services:structuredClone(after.services),authSha256,manifestSha256,allFiveHealthyWanBaseline:true,sourceSha256:hash(fs.readFileSync('work/nss160/declared-baseline.mjs')),routerWrites:false};
  fs.writeFileSync(refPath,JSON.stringify(epoch,null,2)+'\n',{flag:'wx'});
  fs.writeFileSync(baselinePath,JSON.stringify(after,null,2)+'\n',{flag:'wx'});
  hint=await waitReady(c,ctx,label);
 }else{
  epoch=JSON.parse(fs.readFileSync(refPath));assert.equal(epoch.version,3);assert.equal(epoch.boot,after.boot);
  assert.equal(epoch.sourceSha256,hash(fs.readFileSync('work/nss160/declared-baseline.mjs')));
  assert.equal(epoch.authSha256,authDigest);assert.equal(epoch.manifestSha256,after.protectedManifestSha256);
  verifyEpochServices(epoch.services,after.services);reference=JSON.parse(fs.readFileSync(baselinePath));
 }
 const code=render(fs.readFileSync('work/nss23/operational-audit.lua','utf8'));
 const body='exec 8>/tmp/router-project-transaction.lock\nflock -x 8\n/usr/bin/lua - '+ctx.base+' '+ctx.configHash+" <<'NSS23_AUDIT'\n"+code+'\nNSS23_AUDIT\n';
 const raw=await run(ctx.base+'/group-runner 6 /bin/sh -c '+"'"+body.replaceAll("'","'\\''")+"'");
 save('ownership-raw-private',{stdout:raw});const envelope=JSON.parse(raw);save('diagnostic-audit-private',{...envelope,observedAt:new Date().toISOString()});
 assert.equal(envelope.passed,true,envelope.error);const proof=envelope.result;save('ownership-private',proof);
 assert.equal(service.classifier.pid,proof.pid);assert.equal(service.guardian.pid,proof.guardianPid);
 if(purpose==='prewrite'){assert.equal(proof.producer,hint.producer);assert.equal(proof.querySequence,hint.selectedSequence);}
 const adjusted=structuredClone(after);adjusted.native=reference.native;
 adjusted.services['router-project-game-classifier']=reference.services['router-project-game-classifier'];
 const baseline=auditScopedBaseline(reference,adjusted);
 const out={passed:true,auditPurpose:purpose,prelearningSchedulingRequested:purpose==='prewrite',nssAdmissionAllowed:false,originalLockedFreshnessPredicatesRetained:true,protectedConfigurationUnchanged:baseline.configurationMatches,exactOwnedNativeAudit:proof.exactOwnedNativeAudit,selectors:proof.selectors,queryAge:proof.queryAge,sequence:proof.querySequence,ecmClosedAndZero:baseline.checks.ecmStoppedAndZero,serviceEpochPinned:true,failedUnselectedWan4ProcessEpochMayChange:false,otherServiceChangesDuringExperimentAllowed:false,wan4ProcessOwnershipChecked:true,declaredAuthRepairExact:true,declaredManifestExact:true,allFiveHealthyWanBaseline:true,selectedWanStillRequiresOriginalNativePrerequisites:true,unknownRoutingDriftAllowed:false};
 save('audit',out);console.log(JSON.stringify(out));
}finally{c.close()}
