import fs from 'node:fs';import assert from 'node:assert/strict';import {connectRouter} from '../nss27/connect-router.mjs';
import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
const c=await connectRouter(),results=[];try{
for(const round of [108,109]){
 const tap=JSON.parse(fs.readFileSync('work/nss'+round+'/tap-stage-latest-private.json')),s=tap.stage;
 const plan={dir:s.ready.dir,pid:s.ready.pid,start:s.ready.stat.start,boot:s.ready.boot,owner:s.ready.owner,due:s.ready.deadline,ownerDev:s.files.owner.dev,ownerIno:s.files.owner.ino};
 const code=String.raw`local fs=require('nixio.fs');local j=require('luci.jsonc');local P=assert(j.parse([=[__PLAN__]=]));local function read(p)local f=assert(io.open(p));local t=f:read('*a');f:close();return t end
assert(read('/proc/sys/kernel/random/boot_id'):gsub('%s+$','')==P.boot);local now=tonumber(read('/proc/uptime'):match('^[%d.]+'))
local d,a,b=fs.lstat(P.dir);if not d then assert(a==2 or b==2);assert(now>=P.due);print(j.stringify({passed=true,alreadyAbsentAfterIndependentDeadline=true,controllerCancellation=false,uptime=now}));os.exit(0)end
assert(d.type=='dir'and d.uid==0 and d.gid==0 and d.modedec==700);local o=assert(fs.lstat(P.dir..'/owner'));assert(o.type=='reg'and o.uid==0 and o.modedec==600 and o.nlink==1 and o.dev==P.ownerDev and o.ino==P.ownerIno)
assert(read(P.dir..'/owner')==P.owner..' '..P.boot..' '..P.due..'\n');local a={};for x in read('/proc/'..P.pid..'/stat'):match('^%d+ %b() (.*)$'):gmatch('%S+')do a[#a+1]=x end;assert(a[20]==P.start and tonumber(a[2])==1 and a[1]~='Z')
print(j.stringify({passed=true,ownerAndInodeMatched=true,independentParentVerified=true,controllerCancellation=true,uptime=now}))`;
 const e=encode("lua - <<'NSS109_STAGE_OWNER'\n"+code.replace('__PLAN__',()=>JSON.stringify(plan))+'\nNSS109_STAGE_OWNER\n'),r=receipt(await c.run(e.command),e);assert.equal(r.code,0,r.stderr);const checked=JSON.parse(r.stdout);
 if(checked.controllerCancellation){const p='work/nss109/tap'+round+'-cancel';fs.writeFileSync(p,Buffer.from('1'),{flag:'wx'});await c.upload(p,s.ready.dir+'/cancel');let absent=false;for(let i=0;i<12;i++){if((await c.run('test ! -e '+s.ready.dir)).code===0){absent=true;break;}await new Promise(x=>setTimeout(x,250));}assert.ok(absent);}
 results.push({round,...checked,stageAbsent:true});
}
fs.writeFileSync('work/nss109/tap-cleanup.json',JSON.stringify({passed:true,results},null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({passed:true,results}));
}finally{c.close()}
