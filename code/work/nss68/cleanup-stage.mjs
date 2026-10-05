// Cancel this inode-owned passive stage only after verified committed retention.
import fs from 'node:fs';import assert from 'node:assert/strict';
import {verifyDeployment} from './deployment-binding.mjs';
import {connectRouter} from '../nss20/connect-router.mjs';
import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
const {deployment:ctx}=verifyDeployment();
const stage=JSON.parse(fs.readFileSync(ctx.localDir+'/stage-private.json'));
const p={id:ctx.transactionId,pid:ctx.stagePid,start:ctx.stageStart,path:ctx.stagePath,owner:stage.ready.owner,boot:stage.ready.boot,ownerDev:stage.files.owner.dev,ownerIno:stage.files.owner.ino,base:ctx.base,hash:ctx.configHash};
const code=String.raw`local j=require('luci.jsonc');local f=require('nixio.fs');local P=assert(j.parse([=[__PLAN__]=]))
local function read(p,l)local h=assert(io.open(p));local s=h:read(l+1);h:close();assert(#s<=l);return s end
assert(not f.lstat('/root/router-project/active-transaction'))
assert(read('/root/router-project/transactions/'..P.id..'/result',128)=='committed\n')
assert(read('/root/router-project/game-classifier-generation',512)==P.base..' '..P.hash..'\n')
assert(read('/proc/sys/kernel/random/boot_id',128):gsub('%s+$','')==P.boot)
local d=assert(f.lstat(P.path));assert(d.type=='dir'and d.uid==0 and d.gid==0 and d.modedec==700)
local o=assert(f.lstat(P.path..'/owner'));assert(o.dev==P.ownerDev and o.ino==P.ownerIno and o.type=='reg'and o.nlink==1 and o.modedec==600)
local owner,boot=read(P.path..'/owner',256):match('^(%S+) (%S+) ');assert(owner==P.owner and boot==P.boot)
local a={};for x in assert(read('/proc/'..P.pid..'/stat',8192):match('^%d+ %b() (.*)$')):gmatch('%S+')do a[#a+1]=x end
assert(a[20]==P.start and tonumber(a[2])==1 and a[1]~='Z')
print(j.stringify({passed=true,independentStageIdentityVerified=true,productionCommitAlreadyProven=true}))`;
const c=await connectRouter();try{
 const e=encode("/usr/bin/lua - <<'NSS68_STAGE_CANCEL'\n"+code.replace('__PLAN__',()=>JSON.stringify(p))+'\nNSS68_STAGE_CANCEL\n');
 const r=receipt(await c.run(e.command),e);assert.equal(r.code,0,r.stderr);assert.equal(JSON.parse(r.stdout).passed,true);
 await c.upload(ctx.localDir+'/cancel',ctx.stagePath+'/cancel');
 let gone=false;for(let i=0;i<12;i++){if((await c.run('test ! -e '+ctx.stagePath)).code===0){gone=true;break;}await new Promise(r=>setTimeout(r,250));}
 assert.ok(gone);
 const proof={passed:true,observedAt:new Date().toISOString(),onlyOwnedPassiveStageCancelled:true,productionRetentionCommitAlreadyProven:true,stageAbsent:true,stageNatural480SecondExpiryClaimed:false};
 fs.writeFileSync('work/nss68/stage-cleanup.json',JSON.stringify(proof,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(proof));
}finally{c.close()}
