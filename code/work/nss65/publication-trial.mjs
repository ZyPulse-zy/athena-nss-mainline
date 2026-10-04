// One production variable: the qualified full-snapshot publication boundary.
// Independent staging guardian and 180-second undo must be proven before mutation.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import zlib from 'node:zlib';
import {connectRouter} from '../nss20/connect-router.mjs';
import {readBaseline} from '../nss15/baseline.mjs';
import {verifyEpochServices} from '../nss50/service-epoch.mjs';
import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
import {render as auditRender} from '../nss49/audit-renderer.mjs';

const root='work/nss65', sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const json=o=>JSON.stringify(o,null,2)+'\n', q=s=>"'"+s.replaceAll("'","'\\''")+"'";
const old=JSON.parse(fs.readFileSync('work/nss47/deployment-latest.json'));
assert.equal(old.committed,true);
const qualification=JSON.parse(fs.readFileSync('work/nss64/candidate-worker-manifest.json'));
const compiled=JSON.parse(fs.readFileSync('work/nss64/compile-qualified.json'));
assert.ok(qualification.passed&&compiled.passed&&compiled.compiledExactCandidateInRam&&compiled.originalWorkerByteRestorationVerified);
const worker=fs.readFileSync('work/nss64/candidate-worker.lua');
assert.equal(sha(worker),qualification.candidateWorkerSha256);
assert.equal(sha(worker),compiled.sha256);assert.equal(worker.length,32019);
const oldWorker=fs.readFileSync(old.localDir+'/worker.lua');
const oldCfg=fs.readFileSync(old.localDir+'/config.json'), previous=JSON.parse(oldCfg);
assert.equal(sha(oldWorker),qualification.originalWorkerSha256);
assert.equal(sha(oldWorker),previous.files['worker.lua']);assert.equal(sha(oldCfg),old.configHash);
const untouched=['guardian.lua','conntrack-source.lua','backend.lua','classifier-core.lua'];
for(const n of untouched) assert.match(previous.files[n],/^[a-f0-9]{64}$/);
const id='nss65-publication-'+new Date().toISOString().replace(/\D/g,'').slice(0,14)+'-'+crypto.randomBytes(4).toString('hex');
const dir=root+'/'+id, backup=old.base+'/backup-'+id;
fs.mkdirSync(dir,{recursive:true});const save=(n,o)=>fs.writeFileSync(dir+'/'+n+'.json',json(o),{flag:'wx'});
const cfg=structuredClone(previous);cfg.files['worker.lua']=sha(worker);cfg.installTransaction=id;
const normalized=structuredClone(cfg);normalized.files['worker.lua']=previous.files['worker.lua'];normalized.installTransaction=previous.installTransaction;
assert.deepEqual(normalized,previous,'Only worker publication bytes and transaction identity may change');
const newCfg=Buffer.from(json(cfg)),newHash=sha(newCfg);
const fields={ID:id,BASE:old.base,BACKUP:backup,OLD_HASH:old.configHash,NEW_HASH:newHash,OLD_WORKER:sha(oldWorker),NEW_WORKER:sha(worker)};
const render=s=>s.replace(/__([A-Z0-9_]+)__/g,(_,k)=>{assert.ok(k in fields,k);return fields[k]});
const stopGuard=render(String.raw`/usr/bin/lua - <<'NSS65_STOP_GUARD'
local fs=require('nixio.fs');local function read(p)local f=io.open(p);if not f then return nil end;local s=f:read(8192);f:close();return s end
local boot=assert(read('/proc/sys/kernel/random/boot_id')):gsub('%s+$','')
for _,h in ipairs({'__OLD_HASH__','__NEW_HASH__'})do
 local expected=table.concat({'/usr/bin/lua','__BASE__/guardian.lua','__BASE__',h},'\0')..'\0';local selected={}
 for pid in fs.dir('/proc')do if pid:match('^%d+$')and read('/proc/'..pid..'/cmdline')==expected then
  local a={};for v in assert(read('/proc/'..pid..'/stat'):match('^%d+ %b() (.*)$')):gmatch('%S+')do a[#a+1]=v end;selected[#selected+1]={pid=pid,start=a[20]}
 end end;assert(#selected<=1)
 for _,p in ipairs(selected)do assert(os.execute('__BASE__/process-stop '..p.pid..' '..p.start..' '..boot..' /usr/bin/lua __BASE__/guardian.lua __BASE__ '..h)==0)end
end
NSS65_STOP_GUARD
`);
const unchangedChecks=untouched.map(n=>'test "$(sha256sum '+old.base+'/'+n+"|cut -d' ' -f1)\" = "+previous.files[n]).join('\n')+'\n';
const undo=render(String.raw`#!/bin/sh
set -eu
umask 077
if [ "$(readlink /proc/self/fd/9)" = /tmp/router-project-transaction.lock ];then exec 8>&9;fi
test "$(readlink /proc/self/fd/8)" = /tmp/router-project-transaction.lock
grep -q 'FLOCK.*WRITE' /proc/self/fdinfo/8
read -r ai ab ad </root/router-project/active-transaction
test "$ai" = __ID__;test "$ab" = "$(cat /proc/sys/kernel/random/boot_id)"
if [ ! -f __BACKUP__/ready ];then
 test "$(sha256sum __BASE__/worker.lua|cut -d' ' -f1)" = __OLD_WORKER__
 test "$(sha256sum __BASE__/config.json|cut -d' ' -f1)" = __OLD_HASH__
 exit 0
fi
test "$(sha256sum __BACKUP__/old-worker.lua|cut -d' ' -f1)" = __OLD_WORKER__
test "$(sha256sum __BACKUP__/old-config.json|cut -d' ' -f1)" = __OLD_HASH__
for h in __OLD_HASH__ __NEW_HASH__;do /usr/bin/lua __BASE__/stop-worker.lua __BASE__ "$h" service-stop;done
ubus call service delete '{"name":"router-project-game-classifier"}' || true
`)+stopGuard+unchangedChecks+render(String.raw`cp __BACKUP__/old-worker.lua __BASE__/worker.lua.new
cp __BACKUP__/old-config.json __BASE__/config.json.new
chmod 600 __BASE__/worker.lua.new __BASE__/config.json.new
mv __BASE__/worker.lua.new __BASE__/worker.lua
mv __BASE__/config.json.new __BASE__/config.json
printf '%s\n' '__BASE__ __OLD_HASH__' >/root/router-project/game-classifier-generation.new
chmod 600 /root/router-project/game-classifier-generation.new
mv /root/router-project/game-classifier-generation.new /root/router-project/game-classifier-generation
NSS23_DELEGATED_LOCK=1 /bin/sh __BASE__/cleanup.sh __BASE__ __OLD_HASH__ service-stop
printf 'service-stop\n' >/tmp/router-project-game-classifier/stopped
chmod 600 /tmp/router-project-game-classifier/stopped
/etc/init.d/router-project-game-classifier start
echo NSS65_PREVIOUS_HEALTHY_CLASSIFIER_RESTORED
`);
const copies={'old-worker.lua':oldWorker,'old-config.json':oldCfg,'new-worker.lua':worker,'new-config.json':newCfg,'undo.sh':Buffer.from(undo),cancel:Buffer.from('1')};
for(const[n,b]of Object.entries(copies))fs.writeFileSync(dir+'/'+n,b,{flag:'wx'});
let c,armed=false,ctx;
const run=async t=>{const e=encode(t),r=receipt(await c.run(e.command),e);assert.equal(r.code,0,r.stderr||r.stdout);return r.stdout};
try{
 c=await connectRouter();const before=await readBaseline(c,dir,'before');
 const epoch=JSON.parse(fs.readFileSync(root+'/health-epoch-private.json'));
 assert.equal(before.boot,epoch.boot);verifyEpochServices(epoch.services,before.services);
 assert.equal((await run('sh /root/router-project/scripts/transaction.sh status')).trim(),'NO_ACTIVE_TRANSACTION');
 for(const[k,v]of Object.entries(before.ecm))assert.equal(v,['stop4','stop6'].includes(k)?1:0);
 const auditBody='exec 8>/tmp/router-project-transaction.lock\nflock -x 8\n/usr/bin/lua - '+old.base+' '+old.configHash+" <<'NSS65_BEFORE_WRITE'\n"+auditRender(fs.readFileSync('work/nss23/operational-audit.lua','utf8'))+'\nNSS65_BEFORE_WRITE\n';
 const fullAudit=JSON.parse(await run(old.base+'/group-runner 6 /bin/sh -c '+q(auditBody)));save('write-before-audit-private',fullAudit);assert.equal(fullAudit.passed,true,fullAudit.error);
 assert.equal(before.services['router-project-game-classifier'].classifier.pid,fullAudit.result.pid);
 assert.equal(before.services['router-project-game-classifier'].guardian.pid,fullAudit.result.guardianPid);
 for(const[n,h]of [['worker.lua',sha(oldWorker)],['config.json',old.configHash],...untouched.map(n=>[n,previous.files[n]])])assert.equal((await run('sha256sum '+old.base+'/'+n)).split(/\s/)[0],h);
 const cp=(await run('sh /root/router-project/scripts/checkpoint.sh before-'+id)).match(/CHECKPOINT=([A-Za-z0-9-]+)/)?.[1];assert.ok(cp);
 const remote='/root/router-project/backups/'+cp+'/config.tar.gz',digest=(await run('sha256sum '+remote)).split(/\s/)[0];
 await c.download(remote,dir+'/checkpoint-private.tar.gz');const bytes=fs.readFileSync(dir+'/checkpoint-private.tar.gz');assert.equal(sha(bytes),digest);zlib.gunzipSync(bytes);save('checkpoint',{name:cp,sha256:digest,gzipVerified:true});
 const plan={owner:crypto.randomBytes(16).toString('hex'),boot:before.boot,seconds:480,files:Object.fromEntries(Object.entries(copies).map(([n,b])=>[n,{bytes:b.length,sha256:sha(b)}]))};
 const stageCode=fs.readFileSync('work/nss23/stage-guardian.lua','utf8').replace('__PLAN__',()=>JSON.stringify(plan));
 const stage=JSON.parse(await run("/usr/bin/lua - <<'NSS65_STAGE'\n"+stageCode+'\nNSS65_STAGE\n'));
 assert.equal(stage.success,true);assert.ok(stage.rollbackBeforeFirstWrite&&stage.parentIdentityVerified&&stage.pipeInodesVerified);save('stage-private',stage);
 c.close();c=await connectRouter();
 const detached=JSON.parse(await run("/usr/bin/lua -e 'local fs=require(\"nixio.fs\");local j=require(\"luci.jsonc\");local f=assert(io.open(\"/proc/"+stage.ready.pid+"/stat\"));local s=f:read(\"*a\");f:close();local a={};for x in s:match(\"^%d+ %b() (.*)$\"):gmatch(\"%S+\")do a[#a+1]=x end;local fd={};for x in fs.dir(\"/proc/"+stage.ready.pid+"/fd\")do fd[x]=fs.readlink(\"/proc/"+stage.ready.pid+"/fd/\"..x)end;print(j.stringify({parent=tonumber(a[2]),start=a[20],fds=fd}))'"));
 assert.equal(detached.parent,1);assert.equal(detached.start,stage.ready.stat.start);assert.deepEqual(detached.fds,{'0':'/dev/null','1':'/dev/null','2':'/dev/null'});save('stage-detached-private',detached);
 for(const[n,b]of Object.entries(copies))if(n!=='cancel'){await c.upload(dir+'/'+n,stage.ready.dir+'/'+n);assert.equal((await run('sha256sum '+stage.ready.dir+'/'+n)).split(/\s/)[0],sha(b))}
 // Compilation is a byte/SHA check, not a repeated native qualification suite.
 await run("/usr/bin/lua -e 'assert(loadfile(\""+stage.ready.dir+"/new-worker.lua\"));print(\"SYNTAX_PASS\")'");await run('sh -n '+stage.ready.dir+'/undo.sh');
 await run('sh /root/router-project/scripts/transaction.sh arm '+id+' '+cp+' 180 '+stage.ready.dir+'/undo.sh');armed=true;
 ctx={...old,transactionId:id,configHash:newHash,localDir:dir,checkpoint:cp,stagePath:stage.ready.dir,stagePid:stage.ready.pid,stageStart:stage.ready.stat.start,backup,previous:old,committed:false,permanentClassifier:false,deadlineSeconds:180,nssEnabled:false,onlyChange:'Full snapshot publication JSON boundary'};
 fs.writeFileSync(root+'/trial-private.json',json(ctx),{flag:'wx'});fs.writeFileSync(dir+'/config.json',newCfg);fs.writeFileSync(dir+'/worker.lua',worker);
 const guardCode=String.raw`local j=require('luci.jsonc');local function read(p,l)local f=assert(io.open(p));local s=f:read(l+1);f:close();assert(#s<=l);return s end
local f=assert(io.popen('/bin/ubus call service list \'{"name":"router-project-guard"}\''));local svc=assert(j.parse(f:read(32768)));f:close();local g=assert(svc['router-project-guard'].instances.guard);assert(g.running and g.pid>1)
assert(read('/proc/'..g.pid..'/cmdline',8192)==table.concat({'/bin/sh','/root/router-project/scripts/transaction.sh','watch'},'\0')..'\0')
local t={};for x in assert(read('/proc/'..g.pid..'/stat',8192):match('^%d+ %b() (.*)$')):gmatch('%S+')do t[#t+1]=x end;assert(tonumber(t[2])==1 and t[1]~='Z')
local id,boot,deadline=read('/root/router-project/active-transaction',1024):match('^(%S+) (%S+) (%d+)\n$');assert(id=='${id}'and boot==read('/proc/sys/kernel/random/boot_id',128):gsub('%s+$',''));local now=tonumber(read('/proc/uptime',128):match('^[%d.]+'));assert(tonumber(deadline)>now+150)
assert(read('/root/router-project/transactions/'..id..'/checkpoint',512)=='${cp}\n')
print(j.stringify({passed=true,pid=g.pid,start=t[20],parent=1,independentOfSsh=true,transaction=id,checkpoint='${cp}',deadline=tonumber(deadline),observedUptime=now}))`;
 const rollbackProof=JSON.parse(await run("/usr/bin/lua - <<'NSS65_UNDO_PROOF'\n"+guardCode+'\nNSS65_UNDO_PROOF\n'));save('armed-proof-private',rollbackProof);
 // Both independent protectors are now verified. No production mutation above.
 await run(render(String.raw`set -eu
umask 077
exec 8>/tmp/router-project-transaction.lock
flock -x -w 2 8
read -r ai ab ad </root/router-project/active-transaction
test "$ai" = __ID__
test ! -e __BACKUP__
mkdir __BACKUP__
cp `)+stage.ready.dir+'/old-worker.lua '+backup+'/old-worker.lua\ncp '+stage.ready.dir+'/old-config.json '+backup+'/old-config.json\n'+render(String.raw`test "$(sha256sum __BACKUP__/old-worker.lua|cut -d' ' -f1)" = __OLD_WORKER__
test "$(sha256sum __BACKUP__/old-config.json|cut -d' ' -f1)" = __OLD_HASH__
printf ready >__BACKUP__/ready
`));
 const locked=render(String.raw`set -eu
exec 8>/tmp/router-project-transaction.lock
flock -x -w 2 8
read -r ai ab ad </root/router-project/active-transaction
test "$ai" = __ID__
`);
 await run(old.base+'/group-runner 6 /bin/sh -c '+q(locked+stopGuard+"ubus call service delete '{\"name\":\"router-project-game-classifier\"}'\n"));
 await run(old.base+'/group-runner 6 /bin/sh -c '+q(locked+render('NSS23_DELEGATED_LOCK=1 /bin/sh __BASE__/cleanup.sh __BASE__ __OLD_HASH__ service-stop\n')));
 const install=locked+render(String.raw`umask 077
test "$ab" = "__BOOT__";test "$(cut -d. -f1 /proc/uptime)" -lt "$((ad-40))"
test "$(sha256sum __BASE__/worker.lua|cut -d' ' -f1)" = __OLD_WORKER__
test "$(sha256sum __BASE__/config.json|cut -d' ' -f1)" = __OLD_HASH__
`.replaceAll('__BOOT__',()=>before.boot))+unchangedChecks+render(String.raw`cp __STAGE__/new-worker.lua __BASE__/worker.lua.new
cp __STAGE__/new-config.json __BASE__/config.json.new
chmod 600 __BASE__/worker.lua.new __BASE__/config.json.new
mv __BASE__/worker.lua.new __BASE__/worker.lua
mv __BASE__/config.json.new __BASE__/config.json
printf '%s\n' '__BASE__ __NEW_HASH__' >/root/router-project/game-classifier-generation.new
chmod 600 /root/router-project/game-classifier-generation.new
mv /root/router-project/game-classifier-generation.new /root/router-project/game-classifier-generation
test "$(sha256sum __BASE__/worker.lua|cut -d' ' -f1)" = __NEW_WORKER__
test "$(sha256sum __BASE__/config.json|cut -d' ' -f1)" = __NEW_HASH__
`.replaceAll('__STAGE__',()=>stage.ready.dir));
 fs.writeFileSync(dir+'/install.sh',install,{flag:'wx'});
 await run(old.base+'/group-runner 6 /bin/sh -c '+q(install));await run('/etc/init.d/router-project-game-classifier start');
 save('installed',{passed:true,observedAt:new Date().toISOString(),checkpointVerified:true,independent180SecondRollback:true,stagingGuardianIndependent:true,installedWorkerSha256:sha(worker),onlyPublicationBoundaryChanged:true,nssEnabled:false,configOwnerOnlyOtherChange:true});
 console.log(JSON.stringify({publicationTrialInstalled:true,independent180SecondRollback:true,checkpointVerified:true,workerBytes:worker.length,nssEnabled:false}));
}catch(e){save('error-private',{error:String(e),armed,trialReferenceSaved:!!ctx});console.error(String(e));process.exitCode=1}finally{c?.close()}
