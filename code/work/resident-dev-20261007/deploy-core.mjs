// One complete guarded candidate deployment; the default command is local inspect.
import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';import zlib from 'node:zlib';import assert from 'node:assert/strict';import {fileURLToPath} from 'node:url';
import {root,digest} from './build-classifier.mjs';import {deploymentPath} from './deployment-binding.mjs';
import {verifyDeployment as originalDeployment} from '../nss68/deployment-binding.mjs';
import {coreDeploymentPlan,shellQuote as quote} from './core-deployment-plan.mjs';import {coreWorkflow} from './core-workflow.mjs';import * as remote from './core-remote.mjs';
import {connectRouter} from '../nss20/connect-router.mjs';import {readBaseline} from '../nss15/baseline.mjs';
import {declaredReference,verifyFailedWanState,auditScopedBaseline,authSha256,manifestSha256} from '../nss160/declared-baseline.mjs';
import {render as auditRender} from '../nss49/audit-renderer.mjs';import {waitReady} from '../nss122/wait-publication-metadata.mjs';
import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
process.chdir(path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..'));
const mode=process.argv[2]??'inspect';assert.ok(['inspect','run'].includes(mode));assert.equal(process.argv[3],undefined);
const read=p=>JSON.parse(fs.readFileSync(p)),json=v=>JSON.stringify(v,null,2)+'\n';
const original=originalDeployment();const tests=read(root+'/deployment-plan-tests-latest.json');assert.ok(tests.passed&&tests.routerAccess===false);assert.equal(tests.candidateCoreSha256,digest(fs.readFileSync(root+'/classifier-core.lua')));
if(mode==='inspect')console.log(JSON.stringify({passed:true,mode,routerWrites:false,hardwareExecuted:false,alreadyDeployed:fs.existsSync(deploymentPath),onlyProductionSourceChange:'classifier-core.lua',originalWorkerUnchanged:true,rollbackSeconds:180,sourceFreshnessSeconds:6}));
else{
 assert.ok(!fs.existsSync(deploymentPath),'RC already committed; use its binding, never repeat deployment');
 const id='resident-core-'+new Date().toISOString().replace(/\D/g,'').slice(0,14)+'-'+crypto.randomBytes(4).toString('hex'),p=coreDeploymentPlan(original,id),ctx=p.deployment,dir=ctx.localDir;
 fs.mkdirSync(dir);const save=(n,v)=>fs.writeFileSync(dir+'/'+n+'.json',json(v),{flag:'wx'});
 for(const[n,b]of Object.entries(p.copies))fs.writeFileSync(dir+'/'+n,b,{flag:'wx'});
 fs.writeFileSync(dir+'/config.json',p.newCfg,{flag:'wx'});fs.writeFileSync(dir+'/classifier-core.lua',p.core,{flag:'wx'});
 fs.writeFileSync(dir+'/worker.lua',fs.readFileSync(original.deployment.localDir+'/worker.lua'),{flag:'wx'});
 let c,before,stage,checkpoint,armedProof,postAudit,protectedCheck,verifiedCommit=false,seq=0;
 const run=async(body,label)=>{const encoded=encode(body),raw=receipt(await c.run(encoded.command),encoded);save('command-'+String(++seq).padStart(3,'0')+'-'+label+'-raw-private',raw);assert.equal(raw.code,0,raw.stderr||raw.stdout);return raw.stdout;};
 const lua=async(code,label)=>JSON.parse(await run("/usr/bin/lua - <<'RESIDENT_CORE_REMOTE'\n"+code+'\nRESIDENT_CORE_REMOTE\n',label));
 const locked=body=>ctx.base+'/group-runner 6 /bin/sh -c '+quote(body);
 const audit=async(hash,label)=>{
  const body='set -eu\nexec 8>/tmp/router-project-transaction.lock\nflock -x -w 2 8\n/usr/bin/lua - '+ctx.base+' '+hash+" <<'RESIDENT_CORE_AUDIT'\n"+auditRender(fs.readFileSync('work/nss23/operational-audit.lua','utf8'))+'\nRESIDENT_CORE_AUDIT\n';
  const out=JSON.parse(await run(locked(body),label));save(label+'-private',out);assert.equal(out.passed,true,out.error);return out;
 };
 const cleanupStage=async(result,hash)=>{
  const spec={id,pid:stage.ready.pid,start:stage.ready.stat.start,path:stage.ready.dir,owner:stage.ready.owner,boot:stage.ready.boot,dev:stage.files.owner.dev,ino:stage.files.owner.ino,base:ctx.base,hash,result};
  await lua(remote.stageCancel(spec),'stage-cancel-proof');await c.upload(dir+'/cancel',stage.ready.dir+'/cancel');
  let gone=false;for(let i=0;i<15;i++){if((await c.run('test ! -e '+stage.ready.dir)).code===0){gone=true;break;}await new Promise(r=>setTimeout(r,250));}
  assert.ok(gone,'Exact owned stage cleanup did not complete');save('stage-cleanup',{passed:true,stageAbsent:true,onlyOwnedStageCancelled:true,naturalExpiryClaimed:false});
 };
 const adapter={
  async preflight(){
   c=await connectRouter();before=await readBaseline(c,dir,'before');
   assert.equal(before.protectedManifestSha256,manifestSha256);assert.equal(before.protectedManifestPassed,true);
   assert.equal((await run('sh /root/router-project/scripts/transaction.sh status','before-transaction')).trim(),'NO_ACTIVE_TRANSACTION');
   const auth=(await run('sha256sum /root/router-project/scripts/auth-recover.sh','auth')).split(/\s/)[0];assert.equal(auth,authSha256);
   const status=JSON.parse(await run('ubus call network.interface.wan4 status','wan4'));
   const seal=await lua(fs.readFileSync('work/nss160/failed-wan-owner.lua','utf8'),'wan4-owner');verifyFailedWanState(before,status,seal);
   const health=JSON.parse(await run('cat /tmp/router-project-health/status.json','health'));
   const declaration=declaredReference(read('work/nss68/nss107-final-20261005-baseline-private.json'),before,health,auth,status,seal);save('declared-baseline',declaration.proof);
   auditScopedBaseline(declaration.reference,before);
   await waitReady(c,original.deployment,id+'-before');const full=await audit(original.deployment.configHash,'before-full-audit');
   assert.equal(full.result.pid,before.services['router-project-game-classifier'].classifier.pid);assert.equal(full.result.guardianPid,before.services['router-project-game-classifier'].guardian.pid);
   for(const[n,h]of [['classifier-core.lua',digest(p.oldCore)],['config.json',original.deployment.configHash]])assert.equal((await run('sha256sum '+ctx.base+'/'+n,'old-'+n.replaceAll('.','-'))).split(/\s/)[0],h);
  },
  async checkpoint(){
   checkpoint=(await run('sh /root/router-project/scripts/checkpoint.sh before-'+id,'checkpoint')).match(/CHECKPOINT=([A-Za-z0-9-]+)/)?.[1];assert.ok(checkpoint);
   const source='/root/router-project/backups/'+checkpoint+'/config.tar.gz',sha=(await run('sha256sum '+source,'checkpoint-sha')).split(/\s/)[0];
   await c.download(source,dir+'/checkpoint-private.tar.gz');const bytes=fs.readFileSync(dir+'/checkpoint-private.tar.gz');assert.equal(digest(bytes),sha);zlib.gunzipSync(bytes);
   save('checkpoint',{name:checkpoint,sha256:sha,gzipVerified:true});ctx.checkpoint=checkpoint;
  },
  async stage(){
   const plan={owner:crypto.randomBytes(16).toString('hex'),boot:before.boot,seconds:480,files:Object.fromEntries(Object.entries(p.copies).map(([n,b])=>[n,{bytes:b.length,sha256:digest(b)}]))};
   const code=fs.readFileSync('work/nss23/stage-guardian.lua','utf8').replace('__PLAN__',()=>JSON.stringify(plan));stage=await lua(code,'stage');
   assert.ok(stage.success&&stage.rollbackBeforeFirstWrite&&stage.parentIdentityVerified&&stage.pipeInodesVerified);save('stage-private',stage);
   c.close();c=await connectRouter();await lua(remote.detachedStage({pid:stage.ready.pid,start:stage.ready.stat.start}),'stage-detached');
   for(const[n,b]of Object.entries(p.copies))if(n!=='cancel'){await c.upload(dir+'/'+n,stage.ready.dir+'/'+n);assert.equal((await run('sha256sum '+stage.ready.dir+'/'+n,'upload-'+n.replaceAll('.','-'))).split(/\s/)[0],digest(b));}
   await run("/usr/bin/lua -e 'assert(loadfile(\""+stage.ready.dir+"/new-core.lua\"));print(\"SYNTAX_PASS\")'",'target-syntax');await run('sh -n '+stage.ready.dir+'/undo.sh','undo-syntax');
   ctx.stagePath=stage.ready.dir;ctx.stagePid=stage.ready.pid;ctx.stageStart=stage.ready.stat.start;
  },
  async arm(){await run('sh /root/router-project/scripts/transaction.sh arm '+id+' '+checkpoint+' 180 '+stage.ready.dir+'/undo.sh','arm');save('trial-private',ctx);},
  async verifyRollback(){armedProof=await lua(remote.rollbackProof({id,checkpoint}),'rollback-owner');assert.ok(armedProof.passed&&armedProof.independentOfSsh&&armedProof.parent===1);save('armed-proof-private',armedProof);},
  async backup(){await run(locked(p.backupFiles(stage.ready.dir)),'backup-ready');},
  async stop(){await run(locked(p.stop),'stop-owned-classifier');await run(locked(p.cleanup),'software-cleanup');},
  async install(){const code=p.install(stage.ready.dir);fs.writeFileSync(dir+'/install.sh',code,{flag:'wx'});await run(locked(code),'install-core');},
  async start(){await run('/etc/init.d/router-project-game-classifier start','start-classifier');},
  async healthy(){
   const after=await readBaseline(c,dir,'candidate');protectedCheck=auditScopedBaseline(before,after);save('candidate-protected-audit',protectedCheck);
   const hint=await lua(remote.waitHealthy({hash:ctx.configHash}),'candidate-ready');save('candidate-ready',hint);
   postAudit=await audit(ctx.configHash,'candidate-full-audit');assert.equal(postAudit.result.producer,hint.producer);
   assert.equal(postAudit.result.pid,after.services['router-project-game-classifier'].classifier.pid);assert.equal(postAudit.result.guardianPid,after.services['router-project-game-classifier'].guardian.pid);
  },
  async commit(){
   const spec={id,base:ctx.base,hash:ctx.configHash,worker:p.cfg.files['worker.lua'],generation:ctx.id,producer:postAudit.result.producer,pid:postAudit.result.pid,guardianPid:postAudit.result.guardianPid,files:p.cfg.files};
   const body="set -eu\nexec 8>/tmp/router-project-transaction.lock\nflock -x -w 2 8\n/usr/bin/lua - <<'RESIDENT_CORE_COMMIT'\n"+remote.precommit(spec)+'\nRESIDENT_CORE_COMMIT\nexec 8>&-\nsh /root/router-project/scripts/transaction.sh commit '+id+'\n';
   assert.ok((await run(body,'commit')).includes('COMMITTED='+id));
  },
  async verifyCommit(){
   const result=await lua(remote.readback({id,base:ctx.base}),'commit-readback');save('commit-remote-private',result);
   assert.equal(result.transactionResult,'committed\n');assert.equal(result.active,false);assert.equal(result.pointer,ctx.base+' '+ctx.configHash+'\n');
   assert.equal(result.configSha256,ctx.configHash);assert.equal(result.coreSha256,digest(p.core));assert.equal(result.workerSha256,p.cfg.files['worker.lua']);
   const proof={passed:true,committed:true,observedAt:new Date().toISOString(),transactionId:id,configHash:ctx.configHash,coreSha256:digest(p.core),workerSha256:p.cfg.files['worker.lua'],originalFullAuditPassed:postAudit.passed,independent180SecondRollbackVerifiedBeforeWrite:armedProof.passed,checkpointShaGzipVerified:true,protectedConfigurationUnchanged:protectedCheck.configurationMatches,nssEnabled:false,onlyCoreChanged:true};
   save('commit-proof',proof);ctx.committed=true;ctx.permanentClassifier=true;ctx.commitAt=proof.observedAt;verifiedCommit=true;
   fs.writeFileSync(deploymentPath,json(ctx),{flag:'wx'});
  },
  async cleanup(){await cleanupStage('committed',ctx.configHash);},
  async recordFailure(failure){save('deployment-failure-private',failure);},
  async recover(){
   if(verifiedCommit)return;
   // Guard the old single global transaction by its exact ID; never undo another owner.
   const status=(await run('sh /root/router-project/scripts/transaction.sh status','failure-status')).trim();
   if(status!=='NO_ACTIVE_TRANSACTION'){assert.equal(status.split(/\s/)[0],id);await run('sh /root/router-project/scripts/transaction.sh rollback','failure-rollback');}
   const state=await lua(remote.readback({id,base:ctx.base}),'failure-readback');save('failure-readback-private',state);
   if(state.transactionResult==='committed\n'){assert.equal(state.active,false);assert.equal(state.configSha256,ctx.configHash);assert.equal(state.coreSha256,digest(p.core));return;}
   assert.equal(state.transactionResult,'rolled-back\n');assert.equal(state.active,false);assert.equal(state.configSha256,original.deployment.configHash);assert.equal(state.coreSha256,digest(p.oldCore));
   const restored=await readBaseline(c,dir,'restored');const protectedState=auditScopedBaseline(before,restored);await lua(remote.waitHealthy({hash:original.deployment.configHash}),'restored-ready');await audit(original.deployment.configHash,'restored-full-audit');
   await cleanupStage('rolled-back',original.deployment.configHash);save('restore-proof',{passed:true,softwareRestored:true,fullAuditPassed:true,protectedConfigurationUnchanged:protectedState.configurationMatches});
  }
 };
 for(const key of ['preflight','checkpoint','stage','arm','verifyRollback','backup','stop','install','start','healthy','commit','verifyCommit','cleanup']){const step=adapter[key];adapter[key]=async()=>{await step();console.log(JSON.stringify({step:key,passed:true,nssEnabled:false}));};}
 try{const result=await coreWorkflow(adapter);save('deployment-result',{...result,observedAt:new Date().toISOString(),classifierOnly:true,nssEnabled:false});console.log(JSON.stringify({...result,classifierOnly:true,nssEnabled:false}));}
 catch(error){console.error('Candidate deployer stopped; local failure and exact recovery evidence retained. Step: '+error.step);process.exitCode=1;}
 finally{c?.close();}
}
