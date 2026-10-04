// Read-only original full operational audit; no admission or replacement input.
import fs from 'node:fs';import assert from 'node:assert/strict';
import {connectRouter} from '../nss20/connect-router.mjs';
import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
import {readBaseline,auditBaseline} from '../nss15/baseline.mjs';
import {adoptServices,verifyEpochServices} from '../nss50/service-epoch.mjs';
import {render} from '../nss49/audit-renderer.mjs';
import {verifyPreparation} from '../nss63/session-binding.mjs';
verifyPreparation();
const label=process.argv[2];assert.match(label,/^[a-z0-9-]+$/);
const trial=label.startsWith('trial-');
const ctx=JSON.parse(fs.readFileSync(trial?'work/nss65/trial-private.json':'work/nss47/deployment-latest.json'));
const resident=trial?ctx.previous:ctx;
const original=JSON.parse(fs.readFileSync(resident.localDir+'/before-private.json'));
const c=await connectRouter();
try{
 const baseline=await readBaseline(c,'work/nss65',label+'-baseline');
 const service=baseline.services['router-project-game-classifier'];
 assert.equal(service.classifier.running,true);assert.equal(service.guardian.running,true);
 let epoch;
 if(label==='before'){
  const adopted=adoptServices(original.services,baseline.services);
  epoch={version:1,boot:baseline.boot,services:adopted.services,changes:adopted.changes,observedAt:new Date().toISOString()};
  fs.writeFileSync('work/nss65/health-epoch-private.json',JSON.stringify(epoch,null,2)+'\n',{flag:'wx'});
 }else{
  epoch=JSON.parse(fs.readFileSync('work/nss65/health-epoch-private.json'));
  assert.equal(baseline.boot,epoch.boot);verifyEpochServices(epoch.services,baseline.services);
 }
 const code=render(fs.readFileSync('work/nss23/operational-audit.lua','utf8'));
 const body='exec 8>/tmp/router-project-transaction.lock\nflock -x 8\n/usr/bin/lua - '+ctx.base+' '+ctx.configHash+" <<'NSS65_FULL_AUDIT'\n"+code+'\nNSS65_FULL_AUDIT\n';
 const e=encode(ctx.base+'/group-runner 6 /bin/sh -c '+"'"+body.replaceAll("'","'\\''")+"'");
 const raw=receipt(await c.run(e.command),e);
 fs.writeFileSync('work/nss65/'+label+'-audit-raw-private.json',JSON.stringify(raw,null,2)+'\n',{flag:'wx'});
 assert.equal(raw.code,0,raw.stderr);const envelope=JSON.parse(raw.stdout);
 fs.writeFileSync('work/nss65/'+label+'-audit-private.json',JSON.stringify(envelope,null,2)+'\n',{flag:'wx'});
 assert.equal(envelope.passed,true,envelope.error);const proof=envelope.result;
 assert.equal(service.classifier.pid,proof.pid);assert.equal(service.guardian.pid,proof.guardianPid);
 const adjusted={...baseline,native:original.native,services:{...baseline.services}};
 adjusted.services['router-project-game-classifier']=original.services['router-project-game-classifier'];
 const ref={...original,services:{...epoch.services}};
 ref.services['router-project-game-classifier']=original.services['router-project-game-classifier'];
 const unchanged=auditBaseline(ref,adjusted);
 const status=await c.run('sh /root/router-project/scripts/transaction.sh status');
 assert.equal(status.code,0);if(!trial)assert.equal(status.stdout.trim(),'NO_ACTIVE_TRANSACTION');
 const closure=String.raw`local fs=require('nixio.fs');local j=require('luci.jsonc');local stages,states,modules={},{},{}
for x in fs.dir('/tmp')do if x:match('^rp%-nss%d+%-stage%-')then stages[#stages+1]=x end end
for x in fs.dir('/root/router-project/experiments')do if x:match('^rp%-nss%d+%-state%-')then states[#states+1]=x end end
local f=assert(io.open('/proc/modules'));local text=f:read(65536);f:close();for x in text:gmatch('([^\n]+)')do if x:match('^rp_ecm_gate')or x:match('^qca_nss_qdisc ')then modules[#modules+1]=x:match('^(%S+)')end end
print(j.stringify({stages=stages,states=states,modules=modules}))`;
 const ce=encode("/usr/bin/lua - <<'NSS65_CLOSURE'\n"+closure+"\nNSS65_CLOSURE\n");
 const cr=receipt(await c.run(ce.command),ce);assert.equal(cr.code,0,cr.stderr);const closed=JSON.parse(cr.stdout);
 for(const k of ['states','modules'])assert.equal(closed[k].length,0,k+' remain');
 if(trial){assert.deepEqual(closed.stages,[ctx.stagePath.split('/').at(-1)]);}else assert.equal(closed.stages.length,0,'stages remain');
 const out={passed:true,observedAt:new Date().toISOString(),readonly:true,configurationMatches:unchanged.configurationMatches,
  deploymentReference:trial?'work/nss65/trial-private.json':'work/nss47/deployment-latest.json',configSha256:ctx.configHash,workerPid:proof.pid,guardianPid:proof.guardianPid,
  originalFullLockedAudit:true,selectors:proof.selectors,queryAge:proof.queryAge,sequence:proof.querySequence,
  ecmStoppedAndZero:unchanged.checks.ecmStoppedAndZero,noActiveTransaction:!trial,noStaging:!trial,publicationTrial:trial,noExperimentState:true,noExperimentalModule:true,
  diagnostic:envelope.diagnostic,serviceEpochPinned:true,nssAdmissionAllowed:false};
 fs.writeFileSync('work/nss65/'+label+'-health.json',JSON.stringify(out,null,2)+'\n',{flag:'wx'});
 console.log(JSON.stringify({...out,diagnostic:undefined}));
}finally{c.close()}
