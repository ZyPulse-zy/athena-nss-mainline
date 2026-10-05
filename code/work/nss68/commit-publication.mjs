// Commit only a live guarded installation after the complete original audit.
import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {connectRouter} from '../nss20/connect-router.mjs';
import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
const root='work/nss68',ctx=JSON.parse(fs.readFileSync(root+'/trial-private.json'));
assert.equal(ctx.committed,false);
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const cfg=JSON.parse(fs.readFileSync(ctx.localDir+'/config.json'));
assert.equal(hash(fs.readFileSync(ctx.localDir+'/config.json')),ctx.configHash);
assert.equal(hash(fs.readFileSync(ctx.localDir+'/worker.lua')),cfg.files['worker.lua']);
assert.equal(cfg.files['worker.lua'],'40169ce6c8e866cc989c651b24d435777bc422bf10f67c58f5e9ab033e7f3828');
const audit=JSON.parse(fs.readFileSync(root+'/trial-retention-health.json'));
const full=JSON.parse(fs.readFileSync(root+'/trial-retention-audit-private.json'));
assert.ok(audit.passed&&audit.originalFullLockedAudit&&audit.configurationMatches&&audit.ecmStoppedAndZero);
assert.equal(audit.configSha256,ctx.configHash);assert.ok(full.passed&&full.result.producer);
assert.ok(Date.now()-Date.parse(audit.observedAt)<30000,'Commit audit is old');
const arm=JSON.parse(fs.readFileSync(ctx.localDir+'/armed-proof-private.json'));
assert.ok(arm.passed&&arm.independentOfSsh&&arm.parent===1&&arm.transaction===ctx.transactionId&&arm.checkpoint===ctx.checkpoint);
const oldTrial=JSON.parse(fs.readFileSync('work/nss67/trial-private.json'));
const undo=JSON.parse(fs.readFileSync(oldTrial.localDir+'/rollback-qualified.json'));
assert.ok(undo.passed&&undo.automaticExpiryWithoutControllerRollback&&undo.previousWorkerAndConfigRestored);
const json=o=>JSON.stringify(o,null,2)+'\n';
const spec={id:ctx.transactionId,base:ctx.base,hash:ctx.configHash,worker:cfg.files['worker.lua'],generation:ctx.id,producer:full.result.producer,pid:full.result.pid,guardianPid:full.result.guardianPid,files:cfg.files};
const precommit=String.raw`local j=require('luci.jsonc');local fs=require('nixio.fs');local P=assert(j.parse([=[__PLAN__]=]))
local function read(p,l)local f=assert(io.open(p));local s=f:read(l+1)or'';f:close();assert(#s<=l);return s end
local now=tonumber(read('/proc/uptime',128):match('^[%d.]+'))
local id,boot,deadline=read('/root/router-project/active-transaction',512):match('^(%S+) (%S+) (%d+)\n$')
assert(id==P.id and boot==read('/proc/sys/kernel/random/boot_id',128):gsub('%s+$','')and now+40<tonumber(deadline))
assert(read('/root/router-project/game-classifier-generation',512)==P.base..' '..P.hash..'\n')
local function digest(p)local h=assert(io.popen('/usr/bin/sha256sum '..p));local s=h:read(256);assert(h:close());return assert(s:match('^(%x+) '))end
assert(digest(P.base..'/config.json')==P.hash);for name,h in pairs(P.files)do assert(digest(P.base..'/'..name)==h)end
local s=assert(j.parse(read('/tmp/router-project-game-classifier/snapshot.json',4194304)))
local g=assert(j.parse(read('/tmp/router-project-game-classifier/guardian.json',8192)))
local a=assert(j.parse(read('/tmp/router-project-game-classifier/classification.json',4194304)))
assert(s.status=='running'and s.dataHealthy and s.generation==P.generation and s.configSha256==P.hash and s.nssPermit==false and not s.error)
assert(s.producer==P.producer and s.pid==P.pid and g.pid==P.guardianPid and g.producer==P.producer and g.healthy and g.configSha256==P.hash)
assert(now-s.atUptime<9 and now<s.snapshot.provenance.startedAtUptime+6 and now-g.atUptime<6)
assert(a.publication=='before-software-baseline'and a.producer==P.producer and a.configSha256==P.hash and a.nssPermit==false and now<a.snapshot.provenance.startedAtUptime+6)
assert(a.snapshot.admissionProjection.version==1 and a.snapshot.admissionProjection.scope=='bulk-and-admitted-rt')
assert(read('/proc/'..P.pid..'/cmdline',8192)==table.concat({'/usr/bin/lua',P.base..'/worker.lua','watch',P.base,P.hash},'\0')..'\0')
assert(not fs.lstat('/tmp/router-project-game-classifier/stopped'))
assert(not fs.lstat('/sys/module/rp_ecm_gate_lab_ct')and not fs.lstat('/sys/module/qca_nss_qdisc'))
for _,p in ipairs({'front_end_ipv4_stop','front_end_ipv6_stop'})do assert(tonumber(read('/sys/kernel/debug/ecm/'..p,128))==1)end
for _,p in ipairs({'ecm_db/connection_count','ecm_nss_ipv4/accelerated_count','ecm_nss_ipv6/accelerated_count','ecm_nss_ipv4/pending_accel_count','ecm_nss_ipv6/pending_accel_count','ecm_nss_ipv4/pending_decel_count','ecm_nss_ipv6/pending_decel_count'})do assert(tonumber(read('/sys/kernel/debug/ecm/'..p,128))==0)end
local path='/root/router-project/transactions/'..P.id..'/verification.txt';assert(not fs.lstat(path))
local f=assert(io.open(path,'w'));assert(f:write(j.stringify({originalFullAudit=true,producer=P.producer,workerSha256=P.worker,configSha256=P.hash,publicationBoundaryOnly=true,nssEnabled=false,atUptime=now})..'\n'));assert(f:close());assert(fs.chmod(path,600));print('NSS68_PRECOMMIT_VERIFIED')`;
const body='exec 8>/tmp/router-project-transaction.lock\nflock -x 8\n/usr/bin/lua - <<\'NSS68_COMMIT\'\n'+precommit.replace('__PLAN__',()=>JSON.stringify(spec))+'\nNSS68_COMMIT\nexec 8>&-\nsh /root/router-project/scripts/transaction.sh commit '+ctx.transactionId+'\n';
const c=await connectRouter();try{
 const e=encode(body),raw=receipt(await c.run(e.command),e);
 fs.writeFileSync(ctx.localDir+'/commit-raw-private.json',json(raw),{flag:'wx'});
 assert.equal(raw.code,0,raw.stderr);assert.ok(raw.stdout.includes('COMMITTED='+ctx.transactionId));
 const code=String.raw`local j=require('luci.jsonc');local f=require('nixio.fs');local function read(p)local h=assert(io.open(p));local s=h:read('*a');h:close();return s end
local h=assert(io.popen('/usr/bin/sha256sum __BASE__/worker.lua __BASE__/config.json'));local hashes=h:read(2048);h:close();local w,c=hashes:match('^(%x+) [^\n]+\n(%x+) ')
print(j.stringify({transactionResult=read('/root/router-project/transactions/__ID__/result'),active=f.lstat('/root/router-project/active-transaction')~=nil,workerSha256=w,configSha256=c,pointer=read('/root/router-project/game-classifier-generation')}))`;
 const ce=encode("/usr/bin/lua - <<'NSS68_COMMIT_READBACK'\n"+code.replaceAll('__BASE__',()=>ctx.base).replaceAll('__ID__',()=>ctx.transactionId)+'\nNSS68_COMMIT_READBACK\n');
 const cr=receipt(await c.run(ce.command),ce);assert.equal(cr.code,0,cr.stderr);const remote=JSON.parse(cr.stdout);
 fs.writeFileSync(ctx.localDir+'/commit-remote-private.json',json(remote),{flag:'wx'});
 assert.equal(remote.transactionResult,'committed\n');assert.equal(remote.active,false);
 assert.equal(remote.workerSha256,cfg.files['worker.lua']);assert.equal(remote.configSha256,ctx.configHash);
 assert.equal(remote.pointer,ctx.base+' '+ctx.configHash+'\n');
 fs.writeFileSync(ctx.localDir+'/retention-audit.json',json(audit),{flag:'wx'});
 const proof={passed:true,committed:true,observedAt:new Date().toISOString(),transactionId:ctx.transactionId,configHash:ctx.configHash,workerSha256:cfg.files['worker.lua'],remoteCommittedReceiptVerified:true,originalFullAuditPassed:true,protectedConfigurationUnchanged:true,independent180SecondRollbackVerifiedBeforeWrite:true,priorNaturalRollbackVerified:true,nssEnabled:false};
 fs.writeFileSync(ctx.localDir+'/permanent-commit.json',json(proof),{flag:'wx'});
 ctx.committed=true;ctx.permanentClassifier=true;ctx.armed=false;ctx.commitAt=proof.observedAt;
 fs.writeFileSync(root+'/deployment-latest.json',json(ctx),{flag:'wx'});
 console.log(JSON.stringify({...proof,transactionId:undefined}));
}finally{c.close()}
