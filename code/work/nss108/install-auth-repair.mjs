// Fix only PID discovery. No authenticator/interface/service is restarted here.
import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';import zlib from 'node:zlib';
import {connectRouter} from '../nss27/connect-router.mjs';import {readBaseline,auditBaseline} from '../nss15/baseline.mjs';
import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';import {render} from '../nss49/audit-renderer.mjs';
const root='work/nss108',hash=b=>crypto.createHash('sha256').update(b).digest('hex'),q=s=>"'"+s.replaceAll("'","'\\''")+"'";
const qualified=JSON.parse(fs.readFileSync(root+'/auth-qualification.json'));assert.ok(qualified.passed&&qualified.onlyPidDiscoveryChanged&&qualified.protectedManifestIncludesTarget);
const target='/root/router-project/scripts/auth-recover.sh',manifestPath='/root/router-project/experiments/nss6-install-20260930/protected.sha256';
const old=fs.readFileSync(root+'/auth-before.sh'),candidate=fs.readFileSync(root+'/auth-candidate.sh'),manifest=fs.readFileSync(root+'/protected-manifest-private.txt');
assert.equal(hash(old),qualified.sourceSha256);assert.equal(hash(candidate),qualified.candidateSha256);
const manifestLine=manifest.toString().split('\n').filter(x=>x.endsWith('  '+target));assert.equal(manifestLine.length,1);assert.equal(manifestLine[0],hash(old)+'  '+target);
const newManifest=Buffer.from(manifest.toString().replace(manifestLine[0],hash(candidate)+'  '+target));
const id='nss108-auth-'+new Date().toISOString().replace(/\D/g,'').slice(0,14)+'-'+crypto.randomBytes(4).toString('hex'),dir=root+'/'+id;
fs.mkdirSync(dir);const save=(n,o)=>fs.writeFileSync(dir+'/'+n+'.json',JSON.stringify(o,null,2)+'\n',{flag:'wx'});let c,stage,armed=false,committed=false;
const run=async s=>{const e=encode(s),r=receipt(await c.run(e.command),e);assert.equal(r.code,0,r.stderr||'Remote operation failed');return r.stdout;};
try{
 c=await connectRouter();const before=await readBaseline(c,dir,'before');assert.ok(before.protectedManifestPassed);assert.equal(before.protectedManifestSha256,hash(manifest));
 for(const[k,v]of Object.entries(before.ecm))assert.equal(v,['stop4','stop6'].includes(k)?1:0);
 assert.equal((await run('sh /root/router-project/scripts/transaction.sh status')).trim(),'NO_ACTIVE_TRANSACTION');
 for(const[p,h]of[[target,hash(old)],[manifestPath,hash(manifest)]])assert.equal((await run('sha256sum '+p)).split(/\s/)[0],h);
 const ctx=JSON.parse(fs.readFileSync('work/nss68/deployment-latest.json'));
 const body='exec 8>/tmp/router-project-transaction.lock\nflock -x 8\n/usr/bin/lua - '+ctx.base+' '+ctx.configHash+" <<'NSS108_NATIVE_AUDIT'\n"+render(fs.readFileSync('work/nss23/operational-audit.lua','utf8'))+'\nNSS108_NATIVE_AUDIT\n';
 const audit=JSON.parse(await run(ctx.base+'/group-runner 6 /bin/sh -c '+q(body)));save('native-before-private',audit);assert.equal(audit.passed,true,audit.error);
 const checkpoint=(await run('sh /root/router-project/scripts/checkpoint.sh before-'+id)).match(/CHECKPOINT=([a-zA-Z0-9-]+)/)?.[1];assert.ok(checkpoint);
 const remote='/root/router-project/backups/'+checkpoint+'/config.tar.gz',digest=(await run('sha256sum '+remote)).split(/\s/)[0];await c.download(remote,dir+'/checkpoint-private.tar.gz');
 const bytes=fs.readFileSync(dir+'/checkpoint-private.tar.gz');assert.equal(hash(bytes),digest);zlib.gunzipSync(bytes);save('checkpoint',{name:checkpoint,sha256:digest,gzipVerified:true});
 const files={'auth-before.sh':old,'auth-candidate.sh':candidate,'manifest-before.txt.gz':zlib.gzipSync(manifest),'manifest-candidate.txt.gz':zlib.gzipSync(newManifest),'cancel':Buffer.from('1')};
 // The standard detached staging owner is established before uploading files.
 const owner=crypto.randomBytes(16).toString('hex'),plan={owner,boot:before.boot,seconds:480,files:{...Object.fromEntries(Object.entries(files).map(([n,b])=>[n,{bytes:b.length,sha256:hash(b)}])),'undo.sh':{bytes:8192,sha256:hash(Buffer.from('undo'))}}};
 const code=fs.readFileSync('work/nss23/stage-guardian.lua','utf8').replace('__PLAN__',()=>JSON.stringify(plan));
 stage=JSON.parse(await run("/usr/bin/lua - <<'NSS108_STAGE'\n"+code+'\nNSS108_STAGE\n'));assert.ok(stage.success&&stage.rollbackBeforeFirstWrite&&stage.parentIdentityVerified&&stage.pipeInodesVerified);save('stage-private',stage);
 c.close();c=await connectRouter();const sp=stage.ready.dir;
 const detached=JSON.parse(await run("lua -e 'local j=require(\"luci.jsonc\");local fs=require(\"nixio.fs\");local f=assert(io.open(\"/proc/"+stage.ready.pid+"/stat\"));local s=f:read(\"*a\");f:close();local a={};for v in s:match(\"^%d+ %b() (.*)$\"):gmatch(\"%S+\")do a[#a+1]=v end;local fd={};for v in fs.dir(\"/proc/"+stage.ready.pid+"/fd\")do fd[v]=fs.readlink(\"/proc/"+stage.ready.pid+"/fd/\"..v)end;print(j.stringify({parent=tonumber(a[2]),start=a[20],fds=fd}))'"));
 assert.equal(detached.parent,1);assert.equal(detached.start,stage.ready.stat.start);assert.deepEqual(detached.fds,{'0':'/dev/null','1':'/dev/null','2':'/dev/null'});save('stage-detached-private',detached);
 const undo=String.raw`#!/bin/sh
set -eu
test "$(readlink /proc/self/fd/9)" = /tmp/router-project-transaction.lock
read -r ai ab ad </root/router-project/active-transaction
test "$ai" = ${id}
test "$(sha256sum ${sp}/auth-before.sh|cut -d' ' -f1)" = ${hash(old)}
test "$(gzip -dc ${sp}/manifest-before.txt.gz|sha256sum|cut -d' ' -f1)" = ${hash(manifest)}
cp -p ${target} ${target}.nss108-undo
cat ${sp}/auth-before.sh >${target}.nss108-undo
mv ${target}.nss108-undo ${target}
cp -p ${manifestPath} ${manifestPath}.nss108-undo
gzip -dc ${sp}/manifest-before.txt.gz >${manifestPath}.nss108-undo
mv ${manifestPath}.nss108-undo ${manifestPath}
test "$(sha256sum ${target}|cut -d' ' -f1)" = ${hash(old)}
test "$(sha256sum ${manifestPath}|cut -d' ' -f1)" = ${hash(manifest)}
sha256sum -c ${manifestPath} >/dev/null
printf 'NSS108_AUTH_SOURCE_RESTORED\n'
`;
 files['undo.sh']=Buffer.from(undo);for(const[n,b]of Object.entries(files))if(n!=='cancel'){fs.writeFileSync(dir+'/'+n,b,{flag:'wx'});await c.upload(dir+'/'+n,sp+'/'+n);assert.equal((await run('sha256sum '+sp+'/'+n)).split(/\s/)[0],hash(b));}
 await run('sh -n '+sp+'/undo.sh; sh -n '+sp+'/auth-candidate.sh');
 await run('sh /root/router-project/scripts/transaction.sh arm '+id+' '+checkpoint+' 180 '+sp+'/undo.sh');armed=true;
 const proofCode=String.raw`local j=require('luci.jsonc');local u=assert(require('ubus').connect());local s=assert(u:call('service','list',{name='router-project-guard'}));u:close();local p=assert(s['router-project-guard'].instances.guard);assert(p.running and p.pid>1)
local function read(p)local f=assert(io.open(p));local s=f:read('*a');f:close();return s end
assert(read('/proc/'..p.pid..'/cmdline')==table.concat({'/bin/sh','/root/router-project/scripts/transaction.sh','watch'},'\0')..'\0')
local a={};for x in read('/proc/'..p.pid..'/stat'):match('^%d+ %b() (.*)$'):gmatch('%S+')do a[#a+1]=x end;assert(tonumber(a[2])==1 and a[1]~='Z')
local id,boot,due=read('/root/router-project/active-transaction'):match('^(%S+) (%S+) (%d+)\n$');assert(id=='${id}'and boot==read('/proc/sys/kernel/random/boot_id'):gsub('%s+$',''))
local now=tonumber(read('/proc/uptime'):match('^[%d.]+'));assert(tonumber(due)>now+150);assert(read('/root/router-project/transactions/'..id..'/checkpoint')=='${checkpoint}\n')
print(j.stringify({passed=true,parent=1,pid=p.pid,start=a[20],independentOfSsh=true,deadline=tonumber(due),observedUptime=now}))`;
 save('rollback-before-write-private',JSON.parse(await run("lua - <<'NSS108_GUARD'\n"+proofCode+'\nNSS108_GUARD\n')));
 await run(String.raw`set -eu
exec 8>/tmp/router-project-transaction.lock
flock -x -w 2 8
read -r ai ab ad </root/router-project/active-transaction
test "$ai" = ${id};test "$(cut -d. -f1 /proc/uptime)" -lt "$((ad-40))"
test "$(sha256sum ${target}|cut -d' ' -f1)" = ${hash(old)}
test "$(sha256sum ${manifestPath}|cut -d' ' -f1)" = ${hash(manifest)}
cp -p ${target} ${target}.nss108-new
cat ${sp}/auth-candidate.sh >${target}.nss108-new
mv ${target}.nss108-new ${target}
cp -p ${manifestPath} ${manifestPath}.nss108-new
gzip -dc ${sp}/manifest-candidate.txt.gz >${manifestPath}.nss108-new
mv ${manifestPath}.nss108-new ${manifestPath}
sha256sum -c ${manifestPath} >/dev/null
`);
 // A distinct SSH connection verifies installation and every unrelated runtime/config field.
 c.close();c=await connectRouter();const after=await readBaseline(c,dir,'after');assert.equal(after.protectedManifestSha256,hash(newManifest));
 const adjusted={...after,protectedManifestSha256:before.protectedManifestSha256};const stable=auditBaseline(before,adjusted);save('unchanged-runtime',{...stable,onlyDeclaredProtectedManifestRowChanged:true,authenticatorRestarted:false});
 assert.equal((await run('sha256sum '+target)).split(/\s/)[0],hash(candidate));
 const finalAudit=JSON.parse(await run(ctx.base+'/group-runner 6 /bin/sh -c '+q(body)));save('native-after-private',finalAudit);assert.equal(finalAudit.passed,true,finalAudit.error);
 await run('printf %s '+q('NSS108 PID-discovery fixtures, separate SSH, full native ownership audit, exact source/manifest SHA and unchanged runtime passed\n')+' >/root/router-project/transactions/'+id+'/verification.txt');
 await run('sh /root/router-project/scripts/transaction.sh commit '+id);committed=true;
 assert.equal((await run('cat /root/router-project/transactions/'+id+'/result')).trim(),'committed');
 const repair={passed:true,committed:true,id,localDir:dir,checkpoint,stagePath:sp,oldAuthSha256:hash(old),newAuthSha256:hash(candidate),oldManifestSha256:hash(manifest),newManifestSha256:hash(newManifest),independent180SecondRollbackVerifiedBeforeWrite:true,authenticatorRestarted:false,interfacesRestarted:false,unchangedServicesAndRouting:true,ecmStoppedAndZero:true,naturalRollbackTested:false,observedAt:new Date().toISOString()};
 fs.writeFileSync(root+'/auth-repair-latest-private.json',JSON.stringify(repair,null,2)+'\n',{flag:'wx'});save('committed',repair);
 fs.writeFileSync(dir+'/cancel',Buffer.from('1'),{flag:'wx'});await c.upload(dir+'/cancel',sp+'/cancel');let absent=false;for(let i=0;i<12;i++){if((await c.run('test ! -e '+sp)).code===0){absent=true;break;}await new Promise(r=>setTimeout(r,250));}assert.ok(absent);save('stage-cleanup',{passed:true,ownedStageCancelledAfterCommit:true,naturalExpiryClaimed:false});
 console.log(JSON.stringify({...repair,id:undefined,localDir:undefined,checkpoint:undefined,stagePath:undefined}));
}catch(e){save('failure-private',{error:String(e),armed,committed});console.error(String(e).split('\n')[0]);process.exitCode=1;}finally{c?.close();}
