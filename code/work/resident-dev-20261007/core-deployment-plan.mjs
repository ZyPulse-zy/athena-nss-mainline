// Reuse the existing exact classifier transaction/180s restore; change one source file.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import {root,digest} from './build-classifier.mjs';
import {validateCoreChange} from './deployment-binding.mjs';

export const shellQuote=s=>"'"+s.replaceAll("'","'\\''")+"'";
export function coreDeploymentPlan(original,id){
 assert.match(id,/^resident-core-\d{14}-[a-f0-9]{8}$/);
 const {deployment:old,config:previous}=original;
 const oldCore=fs.readFileSync(old.localDir+'/classifier-core.lua'),core=fs.readFileSync(root+'/classifier-core.lua');
 const oldCfg=fs.readFileSync(old.localDir+'/config.json');
 assert.equal(digest(oldCfg),old.configHash);assert.equal(digest(oldCore),previous.files['classifier-core.lua']);
 const cfg=structuredClone(previous);cfg.files['classifier-core.lua']=digest(core);cfg.installTransaction=id;
 const newCfg=Buffer.from(JSON.stringify(cfg,null,2)+'\n');
 const backup=old.base+'/backup-'+id;
 const deployment={...old,transactionId:id,configHash:digest(newCfg),localDir:root+'/'+id,backup,previous:old,
  committed:false,permanentClassifier:false,nssEnabled:false,deadlineSeconds:180,onlyChange:'TCP BULK current-sample classification'};
 validateCoreChange(deployment,cfg,old,previous);
 const fields={ID:id,BASE:old.base,BACKUP:backup,OLD_HASH:old.configHash,NEW_HASH:deployment.configHash,
  OLD_CORE:digest(oldCore),NEW_CORE:digest(core)};
 const render=text=>text.replace(/__([A-Z0-9_]+)__/g,(_,key)=>{assert.ok(key in fields,key);return fields[key];});
 const support=Object.entries(previous.files).filter(([name])=>name!=='classifier-core.lua');
 const supportChecks=support.map(([name,hash])=>'test "$(sha256sum '+old.base+'/'+name+"|cut -d' ' -f1)\" = "+hash).join('\n')+'\n';
 const stopGuard=render(String.raw`/usr/bin/lua - <<'RESIDENT_STOP_CLASSIFIER_GUARD'
local fs=require('nixio.fs');local function read(p)local f=io.open(p);if not f then return nil end;local s=f:read(8192);f:close();return s end
local boot=assert(read('/proc/sys/kernel/random/boot_id')):gsub('%s+$','')
for _,hash in ipairs({'__OLD_HASH__','__NEW_HASH__'})do
 local expected=table.concat({'/usr/bin/lua','__BASE__/guardian.lua','__BASE__',hash},'\0')..'\0';local selected={}
 for pid in fs.dir('/proc')do if pid:match('^%d+$')and read('/proc/'..pid..'/cmdline')==expected then
  local f={};for v in assert(read('/proc/'..pid..'/stat'):match('^%d+ %b() (.*)$')):gmatch('%S+')do f[#f+1]=v end;selected[#selected+1]={pid=pid,start=f[20]}
 end end;assert(#selected<=1)
 for _,p in ipairs(selected)do assert(os.execute('__BASE__/process-stop '..p.pid..' '..p.start..' '..boot..' /usr/bin/lua __BASE__/guardian.lua __BASE__ '..hash)==0)end
end
RESIDENT_STOP_CLASSIFIER_GUARD
`);
 const undo=render(String.raw`#!/bin/sh
set -eu
umask 077
if [ "$(readlink /proc/self/fd/9)" = /tmp/router-project-transaction.lock ];then exec 8>&9;fi
test "$(readlink /proc/self/fd/8)" = /tmp/router-project-transaction.lock
grep -q 'FLOCK.*WRITE' /proc/self/fdinfo/8
read -r ai ab ad </root/router-project/active-transaction
test "$ai" = __ID__;test "$ab" = "$(cat /proc/sys/kernel/random/boot_id)"
if [ ! -f __BACKUP__/ready ];then
 test "$(sha256sum __BASE__/classifier-core.lua|cut -d' ' -f1)" = __OLD_CORE__
 test "$(sha256sum __BASE__/config.json|cut -d' ' -f1)" = __OLD_HASH__
 exit 0
fi
test "$(sha256sum __BACKUP__/old-core.lua|cut -d' ' -f1)" = __OLD_CORE__
test "$(sha256sum __BACKUP__/old-config.json|cut -d' ' -f1)" = __OLD_HASH__
for hash in __OLD_HASH__ __NEW_HASH__;do /usr/bin/lua __BASE__/stop-worker.lua __BASE__ "$hash" service-stop;done
ubus call service delete '{"name":"router-project-game-classifier"}' || true
`)+stopGuard+supportChecks+render(String.raw`cp __BACKUP__/old-core.lua __BASE__/classifier-core.lua.new
cp __BACKUP__/old-config.json __BASE__/config.json.new
chmod 600 __BASE__/classifier-core.lua.new __BASE__/config.json.new
mv __BASE__/classifier-core.lua.new __BASE__/classifier-core.lua
mv __BASE__/config.json.new __BASE__/config.json
printf '%s\n' '__BASE__ __OLD_HASH__' >/root/router-project/game-classifier-generation.new
chmod 600 /root/router-project/game-classifier-generation.new
mv /root/router-project/game-classifier-generation.new /root/router-project/game-classifier-generation
NSS23_DELEGATED_LOCK=1 /bin/sh __BASE__/cleanup.sh __BASE__ __OLD_HASH__ service-stop
printf 'service-stop\n' >/tmp/router-project-game-classifier/stopped
chmod 600 /tmp/router-project-game-classifier/stopped
/etc/init.d/router-project-game-classifier start
echo RESIDENT_PREVIOUS_CLASSIFIER_RESTORED
`);
 const locked=render(String.raw`set -eu
exec 8>/tmp/router-project-transaction.lock
flock -x -w 2 8
read -r ai ab ad </root/router-project/active-transaction
test "$ai" = __ID__
`);
 const install=stage=>locked+render(String.raw`umask 077
test "$ab" = "$(cat /proc/sys/kernel/random/boot_id)"
test "$(cut -d. -f1 /proc/uptime)" -lt "$((ad-40))"
test "$(sha256sum __BASE__/classifier-core.lua|cut -d' ' -f1)" = __OLD_CORE__
test "$(sha256sum __BASE__/config.json|cut -d' ' -f1)" = __OLD_HASH__
`)+supportChecks+render(`cp ${stage}/new-core.lua __BASE__/classifier-core.lua.new
cp ${stage}/new-config.json __BASE__/config.json.new
chmod 600 __BASE__/classifier-core.lua.new __BASE__/config.json.new
mv __BASE__/classifier-core.lua.new __BASE__/classifier-core.lua
mv __BASE__/config.json.new __BASE__/config.json
printf '%s\\n' '__BASE__ __NEW_HASH__' >/root/router-project/game-classifier-generation.new
chmod 600 /root/router-project/game-classifier-generation.new
mv /root/router-project/game-classifier-generation.new /root/router-project/game-classifier-generation
test "$(sha256sum __BASE__/classifier-core.lua|cut -d' ' -f1)" = __NEW_CORE__
test "$(sha256sum __BASE__/config.json|cut -d' ' -f1)" = __NEW_HASH__
`);
 const backupFiles=stage=>locked+render(String.raw`umask 077
test "$ab" = "$(cat /proc/sys/kernel/random/boot_id)"
test "$(cut -d. -f1 /proc/uptime)" -lt "$((ad-40))"
test ! -e __BACKUP__
test "$(sha256sum __BASE__/classifier-core.lua|cut -d' ' -f1)" = __OLD_CORE__
test "$(sha256sum __BASE__/config.json|cut -d' ' -f1)" = __OLD_HASH__
mkdir __BACKUP__
`)+render(`cp ${stage}/old-core.lua __BACKUP__/old-core.lua
cp ${stage}/old-config.json __BACKUP__/old-config.json
test "$(sha256sum __BACKUP__/old-core.lua|cut -d' ' -f1)" = __OLD_CORE__
test "$(sha256sum __BACKUP__/old-config.json|cut -d' ' -f1)" = __OLD_HASH__
printf ready >__BACKUP__/ready
`);
 const stop=locked+stopGuard+"ubus call service delete '{\"name\":\"router-project-game-classifier\"}'\n";
 const cleanup=locked+render('NSS23_DELEGATED_LOCK=1 /bin/sh __BASE__/cleanup.sh __BASE__ __OLD_HASH__ service-stop\n');
 const copies={'old-core.lua':oldCore,'old-config.json':oldCfg,'new-core.lua':core,'new-config.json':newCfg,'undo.sh':Buffer.from(undo),cancel:Buffer.from('1')};
 return{deployment,cfg,core,oldCore,oldCfg,newCfg,copies,undo,locked,install,backupFiles,stop,cleanup,stopGuard,supportChecks,render};
}
