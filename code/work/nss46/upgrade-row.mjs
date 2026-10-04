import fs from'node:fs';import assert from'node:assert/strict';import crypto from'node:crypto';import zlib from'node:zlib';import{connectRouter}from'../nss20/connect-router.mjs';import{readBaseline}from'../nss15/baseline.mjs';import{encode,receipt}from'../nss11/v7-observe-repair/observe2/transport.mjs';
const root='work/nss46/row-retain',old=JSON.parse(fs.readFileSync('work/nss46/deployment-latest.json')),sha=b=>crypto.createHash('sha256').update(b).digest('hex'),json=o=>JSON.stringify(o,null,2)+'\n';assert.equal(old.committed,true);
const qualified=JSON.parse(fs.readFileSync('work/nss46/row-qualified.json')),expiry=JSON.parse(fs.readFileSync('work/nss46/combined-expiry-qualified.json')),native=JSON.parse(fs.readFileSync('work/nss45/query-cleanup-native-qualified.json')),historical=JSON.parse(fs.readFileSync('work/nss45/row-trial/deployment-latest.json')),undoProof=JSON.parse(fs.readFileSync(historical.localDir+'/rollback-qualified.json'));assert.ok(qualified.passed&&qualified.checks===48&&expiry.passed&&expiry.checks===34&&native.passed&&native.checks===7&&undoProof.passed&&undoProof.automaticExpiryWithoutControllerRollback);for(const name of ['worker.lua','guardian.lua','conntrack-source.lua'])assert.equal(qualified.sources[name],sha(fs.readFileSync(root+'/'+name)));
const previousConfig=JSON.parse(fs.readFileSync(old.localDir+'/config.json'));assert.equal(sha(fs.readFileSync(root+'/backend.lua')),previousConfig.files['backend.lua']);
const id='nss46-row-'+new Date().toISOString().replace(/\D/g,'').slice(0,14)+'-'+crypto.randomBytes(4).toString('hex'),dir=root+'/'+id,backup=old.base+'/backup-'+id;fs.mkdirSync(dir,{recursive:true});const save=(n,o)=>fs.writeFileSync(dir+'/'+n+'.json',json(o));
const worker=fs.readFileSync(root+'/worker.lua');const cfg=JSON.parse(fs.readFileSync(old.localDir+'/config.json'));assert.equal(sha(fs.readFileSync(old.localDir+'/config.json')),old.configHash);const oldCfg=Buffer.from(fs.readFileSync(old.localDir+'/config.json'));const oldWorker=fs.readFileSync(old.localDir+'/worker.lua');assert.equal(sha(oldWorker),cfg.files['worker.lua']);const extraNames=['guardian.lua','conntrack-source.lua','backend.lua'];const extras=Object.fromEntries(extraNames.map(n=>{const oldPath=fs.existsSync(old.localDir+'/'+n)?old.localDir+'/'+n:'work/nss23/'+n;const a=fs.readFileSync(oldPath),b=fs.readFileSync(root+'/'+n);assert.equal(sha(a),cfg.files[n]);cfg.files[n]=sha(b);return[n,{old:a,new:b}]}));
assert.equal(cfg.source.maxSourceBytes,524288);cfg.files['worker.lua']=sha(worker);cfg.nssPublication='classification.json';cfg.installTransaction=id;const normalized=structuredClone(cfg);for(const name of ['worker.lua','guardian.lua','conntrack-source.lua'])normalized.files[name]=previousConfig.files[name];normalized.installTransaction=previousConfig.installTransaction;assert.deepEqual(normalized,previousConfig,'Only qualified bounded row-overflow handling and binding may change');const newCfg=Buffer.from(json(cfg)),newHash=sha(newCfg);
const fields={ID:id,BASE:old.base,OLD_HASH:old.configHash,NEW_HASH:newHash,OLD_WORKER:sha(oldWorker),NEW_WORKER:sha(worker),BACKUP:backup,OLD_GENERATION:old.id,OLD_GUARDIAN:sha(extras['guardian.lua'].old),NEW_GUARDIAN:sha(extras['guardian.lua'].new),OLD_SOURCE:sha(extras['conntrack-source.lua'].old),NEW_SOURCE:sha(extras['conntrack-source.lua'].new),OLD_BACKEND:sha(extras['backend.lua'].old),NEW_BACKEND:sha(extras['backend.lua'].new)};
const render=s=>s.replace(/__([A-Z0-9_]+)__/g,(_,k)=>{assert.ok(k in fields,k);return String(fields[k])});
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
/usr/bin/lua - <<'NSS26_STOP_GUARD'
local n=require('nixio');local fs=require('nixio.fs');local function read(p)local f=io.open(p);if not f then return nil end;local s=f:read(8192);f:close();return s end
local boot=assert(read('/proc/sys/kernel/random/boot_id')):gsub('%s+$','')
for _,h in ipairs({'__OLD_HASH__','__NEW_HASH__'})do local expected=table.concat({'/usr/bin/lua','__BASE__/guardian.lua','__BASE__',h},'\0')..'\0';local selected={}
for pid in fs.dir('/proc')do if pid:match('^%d+$')and read('/proc/'..pid..'/cmdline')==expected then local a={};for v in assert(read('/proc/'..pid..'/stat'):match('^%d+ %b() (.*)$')):gmatch('%S+')do a[#a+1]=v end;selected[#selected+1]={pid=pid,start=a[20]}end end;assert(#selected<=1)
for _,p in ipairs(selected)do assert(os.execute('__BASE__/process-stop '..p.pid..' '..p.start..' '..boot..' /usr/bin/lua __BASE__/guardian.lua __BASE__ '..h)==0)end end
NSS26_STOP_GUARD
test "$(sha256sum __BACKUP__/old-guardian.lua|cut -d' ' -f1)" = __OLD_GUARDIAN__
test "$(sha256sum __BACKUP__/old-conntrack-source.lua|cut -d' ' -f1)" = __OLD_SOURCE__
test "$(sha256sum __BACKUP__/old-backend.lua|cut -d' ' -f1)" = __OLD_BACKEND__
cp __BACKUP__/old-backend.lua __BASE__/backend.lua.new
chmod 600 __BASE__/backend.lua.new
mv __BASE__/backend.lua.new __BASE__/backend.lua
cp __BACKUP__/old-guardian.lua __BASE__/guardian.lua.new
cp __BACKUP__/old-conntrack-source.lua __BASE__/conntrack-source.lua.new
chmod 600 __BASE__/guardian.lua.new __BASE__/conntrack-source.lua.new
mv __BASE__/guardian.lua.new __BASE__/guardian.lua
mv __BASE__/conntrack-source.lua.new __BASE__/conntrack-source.lua
cp __BACKUP__/old-worker.lua __BASE__/worker.lua.new
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
echo NSS28_PREVIOUS_HEALTHY_CLASSIFIER_RESTORED
`);
const copies={'old-worker.lua':oldWorker,'old-config.json':oldCfg,'new-worker.lua':worker,'new-config.json':newCfg,'undo.sh':Buffer.from(undo),cancel:Buffer.from('1')};for(const[n,v]of Object.entries(extras)){copies['old-'+n]=v.old;copies['new-'+n]=v.new}for(const[n,b]of Object.entries(copies))fs.writeFileSync(dir+'/'+n,b);
let c,armed=false;const run=async t=>{const e=encode(t),r=receipt(await c.run(e.command),e);assert.equal(r.code,0,r.stderr||r.stdout);return r.stdout};
try{
 c=await connectRouter();const before=await readBaseline(c,dir,'before');assert.equal((await run('sh /root/router-project/scripts/transaction.sh status')).trim(),'NO_ACTIVE_TRANSACTION');assert.equal(before.services['router-project-game-classifier'].classifier.running,true);assert.equal(before.services['router-project-game-classifier'].guardian.running,true);for(const[k,v]of Object.entries(before.ecm))assert.equal(v,['stop4','stop6'].includes(k)?1:0);
 assert.equal((await run('/usr/bin/sha256sum '+old.base+'/worker.lua')).split(/\s/)[0],sha(oldWorker));assert.equal((await run('/usr/bin/sha256sum '+old.base+'/config.json')).split(/\s/)[0],old.configHash);
 // Full syntax was checked offline; the target compiles the exact uploaded bytes below.
 for(const[n,v]of Object.entries(extras))assert.equal((await run('/usr/bin/sha256sum '+old.base+'/'+n)).split(/\s/)[0],sha(v.old));
 const cp=(await run('sh /root/router-project/scripts/checkpoint.sh before-'+id)).match(/CHECKPOINT=([A-Za-z0-9-]+)/)?.[1];assert.ok(cp);const path='/root/router-project/backups/'+cp+'/config.tar.gz',digest=(await run('/usr/bin/sha256sum '+path)).split(/\s/)[0];await c.download(path,dir+'/checkpoint-private.tar.gz');const bytes=fs.readFileSync(dir+'/checkpoint-private.tar.gz');assert.equal(sha(bytes),digest);zlib.gunzipSync(bytes);save('checkpoint',{name:cp,sha256:digest,gzipVerified:true});
 const owner=crypto.randomBytes(16).toString('hex'),plan={owner,boot:before.boot,seconds:480,files:Object.fromEntries(Object.entries(copies).map(([n,b])=>[n,{bytes:b.length,sha256:sha(b)}]))};
 const body=fs.readFileSync('work/nss23/stage-guardian.lua','utf8').replace('__PLAN__',()=>JSON.stringify(plan));const stage=JSON.parse(await run("/usr/bin/lua - <<'NSS26_STAGE'\n"+body+"\nNSS26_STAGE\n"));assert.equal(stage.success,true);assert.ok(stage.rollbackBeforeFirstWrite&&stage.parentIdentityVerified&&stage.pipeInodesVerified);save('stage',stage);c.close();c=await connectRouter();
 const detach=JSON.parse(await run("/usr/bin/lua -e 'local fs=require(\"nixio.fs\");local j=require(\"luci.jsonc\");local f=assert(io.open(\"/proc/"+stage.ready.pid+"/stat\"));local s=f:read(\"*a\");f:close();local a={};for x in s:match(\"^%d+ %b() (.*)$\"):gmatch(\"%S+\")do a[#a+1]=x end;local fd={};for x in fs.dir(\"/proc/"+stage.ready.pid+"/fd\")do fd[x]=fs.readlink(\"/proc/"+stage.ready.pid+"/fd/\"..x)end;print(j.stringify({parent=tonumber(a[2]),start=a[20],fds=fd}))'"));assert.equal(detach.parent,1);assert.equal(detach.start,stage.ready.stat.start);assert.deepEqual(detach.fds,{'0':'/dev/null','1':'/dev/null','2':'/dev/null'});save('stage-detached',detach);
 for(const[n,b]of Object.entries(copies))if(n!=='cancel'){await c.upload(dir+'/'+n,stage.ready.dir+'/'+n);assert.equal((await run('/usr/bin/sha256sum '+stage.ready.dir+'/'+n)).split(/\s/)[0],sha(b))}
 for(const name of ['new-worker.lua','new-guardian.lua','new-conntrack-source.lua','new-backend.lua'])await run("/usr/bin/lua -e 'assert(loadfile(\""+stage.ready.dir+'/'+name+"\"));print(\"SYNTAX_PASS\")'");
 await run('sh -n '+stage.ready.dir+'/undo.sh');await run('sh /root/router-project/scripts/transaction.sh arm '+id+' '+cp+' 180 '+stage.ready.dir+'/undo.sh');armed=true;
 const rollbackProof=JSON.parse(await run("/usr/bin/lua - <<'NSS33_INDEPENDENT_GUARD'\n"+String.raw`local j=require('luci.jsonc');local fs=require('nixio.fs');local function read(p,l)local f=assert(io.open(p));local s=f:read(l+1);f:close();assert(#s<=l);return s end
local f=assert(io.popen('/bin/ubus call service list \'{"name":"router-project-guard"}\''));local svc=assert(j.parse(f:read(32768)));f:close();local g=assert(svc['router-project-guard'].instances.guard);assert(g.running and g.pid>1)
assert(read('/proc/'..g.pid..'/cmdline',8192)==table.concat({'/bin/sh','/root/router-project/scripts/transaction.sh','watch'},'\0')..'\0')
local t={};for x in assert(read('/proc/'..g.pid..'/stat',8192):match('^%d+ %b() (.*)$')):gmatch('%S+')do t[#t+1]=x end;assert(tonumber(t[2])==1 and t[1]~='Z')
local id,boot,deadline=read('/root/router-project/active-transaction',1024):match('^(%S+) (%S+) (%d+)\n$');assert(id=='${id}'and boot==read('/proc/sys/kernel/random/boot_id',128):gsub('%s+$',''));local now=tonumber(read('/proc/uptime',128):match('^[%d.]+'));assert(tonumber(deadline)>now+150)
assert(read('/root/router-project/transactions/'..id..'/checkpoint',512)=='${cp}\n')
print(j.stringify({passed=true,pid=g.pid,start=t[20],parent=1,independentOfSsh=true,transaction=id,checkpoint='${cp}',deadline=tonumber(deadline),observedUptime=now}))`+"\nNSS33_INDEPENDENT_GUARD\n"));save('armed-proof',rollbackProof);
 await run(render('set -eu\numask 077\nexec 8>/tmp/router-project-transaction.lock\nflock -x 8\ntest ! -e __BACKUP__\nmkdir __BACKUP__\ncp '+stage.ready.dir+'/old-worker.lua __BACKUP__/old-worker.lua\ncp '+stage.ready.dir+'/old-config.json __BACKUP__/old-config.json\ntest "$(sha256sum __BACKUP__/old-worker.lua|cut -d\' \' -f1)" = __OLD_WORKER__\ntest "$(sha256sum __BACKUP__/old-config.json|cut -d\' \' -f1)" = __OLD_HASH__\ncp '+stage.ready.dir+'/old-guardian.lua __BACKUP__/old-guardian.lua\ncp '+stage.ready.dir+'/old-conntrack-source.lua __BACKUP__/old-conntrack-source.lua\ntest "$(sha256sum __BACKUP__/old-guardian.lua|cut -d\' \' -f1)" = __OLD_GUARDIAN__\ntest "$(sha256sum __BACKUP__/old-conntrack-source.lua|cut -d\' \' -f1)" = __OLD_SOURCE__\ncp '+stage.ready.dir+'/old-backend.lua __BACKUP__/old-backend.lua\ntest "$(sha256sum __BACKUP__/old-backend.lua|cut -d\' \' -f1)" = __OLD_BACKEND__\nprintf ready >__BACKUP__/ready\n'));
 const shellQuote=s=>"'"+s.replaceAll("'","'\\''")+"'";
 await run(old.base+'/group-runner 6 /bin/sh -c '+shellQuote(render(String.raw`set -eu
exec 8>/tmp/router-project-transaction.lock
flock -x -w 2 8
read -r ai ab ad </root/router-project/active-transaction
test "$ai" = __ID__
/usr/bin/lua - <<'NSS26_STOP_GUARD'
local n=require('nixio');local fs=require('nixio.fs');local function read(p)local f=io.open(p);if not f then return nil end;local s=f:read(8192);f:close();return s end
local boot=assert(read('/proc/sys/kernel/random/boot_id')):gsub('%s+$','')
for _,h in ipairs({'__OLD_HASH__','__NEW_HASH__'})do local expected=table.concat({'/usr/bin/lua','__BASE__/guardian.lua','__BASE__',h},'\0')..'\0';local selected={}
for pid in fs.dir('/proc')do if pid:match('^%d+$')and read('/proc/'..pid..'/cmdline')==expected then local a={};for v in assert(read('/proc/'..pid..'/stat'):match('^%d+ %b() (.*)$')):gmatch('%S+')do a[#a+1]=v end;selected[#selected+1]={pid=pid,start=a[20]}end end;assert(#selected<=1)
for _,p in ipairs(selected)do assert(os.execute('__BASE__/process-stop '..p.pid..' '..p.start..' '..boot..' /usr/bin/lua __BASE__/guardian.lua __BASE__ '..h)==0)end end
NSS26_STOP_GUARD
ubus call service delete '{"name":"router-project-game-classifier"}' || true
`)));
 await run(old.base+'/group-runner 6 /bin/sh -c '+shellQuote(render(String.raw`set -eu
exec 8>/tmp/router-project-transaction.lock
flock -x -w 2 8
read -r ai ab ad </root/router-project/active-transaction
test "$ai" = __ID__
NSS23_DELEGATED_LOCK=1 /bin/sh __BASE__/cleanup.sh __BASE__ __OLD_HASH__ service-stop
`)));
 const install=render(String.raw`set -eu
umask 077
exec 8>/tmp/router-project-transaction.lock
flock -x 8
read -r ai ab ad </root/router-project/active-transaction
test "$ai" = __ID__;test "$ab" = "__BOOT__";test "$(cut -d. -f1 /proc/uptime)" -lt "$((ad-40))"
test "$(sha256sum __BASE__/worker.lua|cut -d' ' -f1)" = __OLD_WORKER__
test "$(sha256sum __BASE__/config.json|cut -d' ' -f1)" = __OLD_HASH__
test "$(sha256sum __BASE__/guardian.lua|cut -d' ' -f1)" = __OLD_GUARDIAN__
test "$(sha256sum __BASE__/conntrack-source.lua|cut -d' ' -f1)" = __OLD_SOURCE__
test "$(sha256sum __BASE__/backend.lua|cut -d' ' -f1)" = __OLD_BACKEND__
cp __STAGE__/new-backend.lua __BASE__/backend.lua.new
chmod 600 __BASE__/backend.lua.new
mv __BASE__/backend.lua.new __BASE__/backend.lua
cp __STAGE__/new-guardian.lua __BASE__/guardian.lua.new
cp __STAGE__/new-conntrack-source.lua __BASE__/conntrack-source.lua.new
chmod 600 __BASE__/guardian.lua.new __BASE__/conntrack-source.lua.new
mv __BASE__/guardian.lua.new __BASE__/guardian.lua
mv __BASE__/conntrack-source.lua.new __BASE__/conntrack-source.lua
cp __STAGE__/new-worker.lua __BASE__/worker.lua.new
cp __STAGE__/new-config.json __BASE__/config.json.new
chmod 600 __BASE__/worker.lua.new __BASE__/config.json.new
mv __BASE__/worker.lua.new __BASE__/worker.lua
mv __BASE__/config.json.new __BASE__/config.json
printf '%s\n' '__BASE__ __NEW_HASH__' >/root/router-project/game-classifier-generation.new
chmod 600 /root/router-project/game-classifier-generation.new
mv /root/router-project/game-classifier-generation.new /root/router-project/game-classifier-generation
test "$(sha256sum __BASE__/worker.lua|cut -d' ' -f1)" = __NEW_WORKER__
test "$(sha256sum __BASE__/config.json|cut -d' ' -f1)" = __NEW_HASH__
test "$(sha256sum __BASE__/backend.lua|cut -d' ' -f1)" = __NEW_BACKEND__
`.replaceAll('__BOOT__',()=>before.boot).replaceAll('__STAGE__',()=>stage.ready.dir));fs.writeFileSync(dir+'/install.sh',install);await run(install);await run('/etc/init.d/router-project-game-classifier start');
 const ctx={...old,transactionId:id,configHash:newHash,localDir:dir,checkpoint:cp,stagePath:stage.ready.dir,stagePid:stage.ready.pid,stageStart:stage.ready.stat.start,backup,previous:old,committed:false,permanentClassifier:false,deadlineSeconds:180,nssEnabled:false,nssPublication:'classification.json'};fs.writeFileSync(dir+'/config.json',newCfg);fs.writeFileSync(dir+'/worker.lua',worker);for(const[n,v]of Object.entries(extras))fs.writeFileSync(dir+'/'+n,v.new);fs.writeFileSync(root+'/deployment-latest.json',json(ctx));console.log(JSON.stringify({qualifiedRowOverloadRetention:true,independent180SecondRollback:true,checkpointVerified:true,conntrackAndAdmissionBoundsUnchanged:true,nssEnabled:false}));
}catch(e){save('error',{error:String(e),armed});console.error(String(e));process.exitCode=1}finally{c?.close()}
