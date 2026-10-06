import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';import {spawnSync} from 'node:child_process';
import {verifyPreparation} from './session-binding.mjs';import {runEpoch} from './epoch-driver.mjs';import {readJournal,verifyJournalInputs,writeJournal,advance} from './journal.mjs';import {readProcess} from './process-identity.mjs';
import {requireOwnedUpload,allowSuccessor,validateStableEpoch} from '../nss151/transition-policy.mjs';import {validateRecoveredEpoch} from '../nss153/recovery-policy.mjs';
import {readStage,waitStageUndo} from '../nss149/module-stage.mjs';import {connectRouter} from '../nss27/connect-router.mjs';import {readBaseline} from '../nss15/baseline.mjs';import {auditScopedBaseline} from '../nss140/declared-baseline.mjs';import {validateAcceleratedState} from '../nss140/parse-ecm-any-wan.mjs';
const root='work/nss154',out=root+'/run1',mode=process.argv[2],hash=b=>crypto.createHash('sha256').update(b).digest('hex'),read=(d,n)=>JSON.parse(fs.readFileSync(d+'/'+n+'.json'));
assert.ok(['fresh','resume'].includes(mode));verifyPreparation();const continuity=read(out,'continuity-private'),selected=continuity.selected;const load=read(root,'load-latest-private'),config=read(load.dir,'client-config-private');const self=readProcess(process.pid);assert.ok(self.exactExe&&self.exactOwnedScript);
const save=(n,v)=>fs.writeFileSync(out+'/'+n+'.json',JSON.stringify(v,null,2)+'\n',{flag:'wx'});const run=(file,args)=>{const p=spawnSync(process.execPath,[file,...args],{encoding:'utf8',windowsHide:true,timeout:30000});assert.equal(p.status,0,p.stderr);return JSON.parse(p.stdout.trim())};
const names={result:'result',record:'last-record-private',plan:'stage-plan-private',checkpoint:'stage-checkpoint-verified',undo:'stage-undo-verified',detached:'stage-detached-private',receipt:'stage-receipt-private',baseline:'baseline-audit',classified:'post-checkpoint-class-leaf-map-proof',ecm:'actual-accelerated-state-proof',frame:'post-checkpoint-controlled-receipt-private'};
let journal,c;const cases=[];
try{
 if(mode==='fresh'){
  assert.ok(!fs.existsSync(out+'/journal-private.json'));
  journal=writeJournal({schema:'nss154-finite-supervisor-v1',state:'READY',revision:0,maxEpochs:2,history:[],cases:[],entryManifestSha256:hash(fs.readFileSync(root+'/entry-source-manifest.json')),continuitySha256:hash(fs.readFileSync(out+'/continuity-private.json'))});
 }else{
  journal=verifyJournalInputs(readJournal());assert.equal(journal.state,'STAGED');assert.equal(journal.history.length,0);
  const old=readProcess(journal.process.pid);assert.ok(!old||old.started!==journal.process.started,'Original supervisor still alive; duplicate admission refused');save('old-process-absence-private',{passed:true,sameOriginalIdentityPresent:false,pidReused:!!old});
  const crash=read(out,'supervisor-crash-private');assert.equal(crash.pid,journal.process.pid);assert.equal(crash.identity.started,journal.process.started);assert.equal(crash.ownedKillReturnedTrue,true);assert.equal(crash.terminationSignal,'SIGTERM');assert.equal(crash.routerGuardianNotKilled,true);
  const ctx={dir:journal.caseDir,plan:read(journal.caseDir,'stage-plan-private'),receipt:read(journal.caseDir,'stage-receipt-private')};assert.equal(ctx.plan.boot,journal.boot);assert.equal(ctx.plan.owner,journal.owner);assert.equal(ctx.receipt.rollbackBeforeFirstWrite,true);assert.equal(read(journal.caseDir,'stage-detached-private').identity.ppid,1);
  const cp=read(journal.caseDir,'stage-checkpoint-verified');assert.equal(hash(fs.readFileSync(journal.caseDir+'/stage-checkpoint-config-private.tar.gz')),cp.sha256);assert.equal(cp.gzipVerified,true);
  const atCrash=read(out,'precrash-native-state-private'),nativeCrash=atCrash.raw;assert.equal(nativeCrash.count,2);assert.equal(nativeCrash.frozen_record_sha256,ctx.plan.frozenHash);assert.equal(nativeCrash.tcp_permit,'Y');assert.equal(nativeCrash.game_permit,'Y');for(const slot of ['tcp','game'])assert.ok(nativeCrash[slot+'_pinned_state'].includes('pinned=1 current_hash_matches=1'));const crashEcm=validateAcceleratedState(nativeCrash.state,selected);assert.deepEqual(crashEcm,atCrash.proof);assert.equal(atCrash.checkpointDownloadedBeforeFirstWrite,true);assert.equal(atCrash.detachedRollbackVerified,true);
  save('restart-recovery-private',{readOnlyUntilOriginalOwnerVerifiedRestored:true,reopenOldGate:false,extendOldLease:false,newSupervisorPid:process.pid,originalSupervisorPid:crash.pid});
  c=await connectRouter();const due=performance.now()+105000;let latest,restored=false;
  while(performance.now()<due){const s=await readStage(c,ctx);assert.equal(s.sameBoot,true);if(s.record){latest=s.record;fs.writeFileSync(ctx.dir+'/crash-last-record-private.json',JSON.stringify(latest,null,2)+'\n');}if(!s.directoryPresent&&!s.stateDirectoryPresent&&!s.modulePresent&&!s.qosModulePresent){restored=true;break}await new Promise(r=>setTimeout(r,400));}
  assert.ok(restored&&latest,'Independent complete terminal record missing; no new admission');await waitStageUndo(ctx);assert.equal(latest.error,undefined);assert.ok(!fs.existsSync(ctx.dir+'/result.json'));
  const after=await readBaseline(c,ctx.dir,'restart-after');c.close();c=undefined;
  run(root+'/current-audit-diagnostic.mjs',[ctx.dir.split('/').at(-1)+'-restart-after','recovery',ctx.dir]);const baseline=auditScopedBaseline(read(ctx.dir,'before-private'),after);
  const parentRecovery={passed:true,originalControllerKilledDuringEcm2:true,exactFlowMarkNatWanAndDualTagsAtCrash:true,routerGuardianIndependentOfController:true,automatic20SecondEpochFinishedWithoutPcController:latest.automaticLifecycleEpochCompleted===true,nativeRenewalsWithoutPcController:latest.renewals.length,restoredWithoutManualRouterUndo:true,noRouterGuardianOrServiceKilled:true,physicalRootsTagsModulesRoutingRestored:latest.dualPhysicalQueuesRestored===true,normalHostControllerReceiptAbsent:true};
  const finalEcm=validateAcceleratedState(latest.acceleratedState,selected);for(const slot of ['tcp','udp'])assert.equal(finalEcm.proof[slot].serial,crashEcm.proof[slot].serial,'Original crash CI identity changed');
  const bundle={...Object.fromEntries(Object.entries(names).filter(([k])=>!['result','record','baseline','ecm'].includes(k)).map(([k,n])=>[k,read(ctx.dir,n)])),record:latest,baseline,ecm:finalEcm,crash,parentRecovery,normalHostReceiptPresent:false};
  const epoch=validateRecoveredEpoch(bundle,selected);save('recovered-first-epoch-private',bundle);save('independent-crash-result',{...parentRecovery,caseDir:ctx.dir,mode:'newSupervisorFromDiskJournal'});
  journal=advance(journal,'CLOSED',{history:[epoch]});console.log(JSON.stringify({supervisorRestartRecovered:true,oldEpochFullyRestored:true,firstNativeRenewals:latest.renewals.length,newAdmissionStillStopped:true}));
 }
 while(journal.history.length<2){
  verifyPreparation();save(mode+'-generation'+(journal.history.length+1)+'-lifetime',requireOwnedUpload(config,read(load.dir,'status-private'),load));
  if(journal.history.length)allowSuccessor(journal.history);
  const result=await runEpoch(out+'/continuity-private.json',async ctx=>{
   journal=advance(journal,'STAGED',{caseDir:ctx.dir,boot:ctx.plan.boot,owner:ctx.plan.owner,planSha256:hash(fs.readFileSync(ctx.dir+'/stage-plan-private.json')),receiptSha256:hash(fs.readFileSync(ctx.dir+'/stage-receipt-private.json')),process:self,cases:[...journal.cases,ctx.dir]});
   console.log(JSON.stringify({supervisorJournalStaged:true,generation:journal.history.length+1,independentRollbackVerified:true}));
  });
  assert.ok(result?.passed,'Fresh epoch did not complete');const bundle=Object.fromEntries(Object.entries(names).map(([k,n])=>[k,read(result.output,n)]));const epoch=validateStableEpoch(bundle,selected,journal.history.at(-1)??null);
  journal=advance(journal,journal.history.length===0?'CLOSED':'COMPLETE',{history:[...journal.history,epoch]});
 }
 save(mode+'-supervisor-result',{passed:true,mode,completedEpochs:2,supervisorPid:process.pid,sameSocketCtMarkNatWan:true,newQueryCheckpointOwnerPinBothCis:true,journalFinalState:journal.state,originalSupervisorActuallyReplaced:mode==='resume',oldGateNeverReopened:true});console.log(JSON.stringify({passed:true,mode,completedEpochs:2,actualSupervisorRestart:mode==='resume',sameSocketCtMarkNatWan:true}));
}catch(error){process.exitCode=1;save(mode+'-failure-private',{passed:false,error:String(error),state:journal?.state,recoveryAdmissionStopped:true});console.error(String(error).split('\n')[0]);}
finally{c?.close()}
