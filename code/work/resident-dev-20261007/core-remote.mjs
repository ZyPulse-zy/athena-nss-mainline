import assert from 'node:assert/strict';
const bind=(code,spec)=>{const bytes=JSON.stringify(spec);assert.ok(!bytes.includes(']=]'));return code.replace('__PLAN__',()=>bytes);};
export function rollbackProof(spec){return bind(String.raw`local j=require('luci.jsonc');local P=assert(j.parse([=[__PLAN__]=]))
local function read(p,l)local f=assert(io.open(p));local s=f:read(l+1);f:close();assert(#s<=l);return s end
local f=assert(io.popen('/bin/ubus call service list \'{"name":"router-project-guard"}\''));local svc=assert(j.parse(f:read(32768)));f:close();local g=assert(svc['router-project-guard'].instances.guard);assert(g.running and g.pid>1)
assert(read('/proc/'..g.pid..'/cmdline',8192)==table.concat({'/bin/sh','/root/router-project/scripts/transaction.sh','watch'},'\0')..'\0')
local t={};for x in assert(read('/proc/'..g.pid..'/stat',8192):match('^%d+ %b() (.*)$')):gmatch('%S+')do t[#t+1]=x end;assert(tonumber(t[2])==1 and t[1]~='Z')
local id,boot,deadline=read('/root/router-project/active-transaction',1024):match('^(%S+) (%S+) (%d+)\n$');assert(id==P.id and boot==read('/proc/sys/kernel/random/boot_id',128):gsub('%s+$',''));local now=tonumber(read('/proc/uptime',128):match('^[%d.]+'));assert(tonumber(deadline)>now+150)
assert(read('/root/router-project/transactions/'..id..'/checkpoint',512)==P.checkpoint..'\n')
print(j.stringify({passed=true,pid=g.pid,start=t[20],parent=1,independentOfSsh=true,transaction=id,checkpoint=P.checkpoint,deadline=tonumber(deadline),observedUptime=now}))`,spec);}
export function detachedStage(spec){return bind(String.raw`local fs=require('nixio.fs');local j=require('luci.jsonc');local P=assert(j.parse([=[__PLAN__]=]));local f=assert(io.open('/proc/'..P.pid..'/stat'));local s=f:read('*a');f:close();local a={};for x in s:match('^%d+ %b() (.*)$'):gmatch('%S+')do a[#a+1]=x end
assert(tonumber(a[2])==1 and a[20]==P.start and a[1]~='Z');local fd={};for x in fs.dir('/proc/'..P.pid..'/fd')do fd[x]=fs.readlink('/proc/'..P.pid..'/fd/'..x)end
assert(fd['0']=='/dev/null'and fd['1']=='/dev/null'and fd['2']=='/dev/null');local count=0;for _ in pairs(fd)do count=count+1 end;assert(count==3)
print(j.stringify({passed=true,parent=1,start=a[20],independentOfSsh=true}))`,spec);}
export function waitHealthy(spec){return bind(String.raw`local j=require('luci.jsonc');local n=require('nixio');local fs=require('nixio.fs');local P=assert(j.parse([=[__PLAN__]=]))
local function read(p,l)local f=io.open(p);if not f then return nil end;local s=f:read(l+1);f:close();assert(#s<=l);return s end
local function now()return tonumber(assert(read('/proc/uptime',128)):match('^[%d.]+'))end
local began=now();local result
while now()<began+30 do
 local a=read('/tmp/router-project-game-classifier/classification.json',4194304);local b=read('/tmp/router-project-game-classifier/snapshot.json',4194304);local c=read('/tmp/router-project-game-classifier/guardian.json',8192)
 a=a and j.parse(a);b=b and j.parse(b);c=c and j.parse(c)
 if a and b and c and a.configSha256==P.hash and b.configSha256==P.hash and c.configSha256==P.hash and a.status=='running'and b.status=='running'and a.dataHealthy and b.dataHealthy and c.healthy and not a.error and not b.error and a.nssPermit==false and b.nssPermit==false and a.producer==b.producer and c.producer==b.producer and a.snapshot.provenance.sequence==b.snapshot.provenance.sequence and now()<b.snapshot.provenance.startedAtUptime+1.8 and now()<c.atUptime+6 and not fs.lstat('/tmp/router-project-game-classifier/stopped')then
  result={passed=true,producer=b.producer,pid=b.pid,guardianPid=c.pid,sequence=b.snapshot.provenance.sequence,sourceAge=now()-b.snapshot.provenance.startedAtUptime};break
 end;n.nanosleep(0,100000000)
end
assert(result,'Candidate classifier not healthy within original 30s scheduling allowance');print(j.stringify(result))`,spec);}
export function precommit(spec){return bind(String.raw`local j=require('luci.jsonc');local fs=require('nixio.fs');local P=assert(j.parse([=[__PLAN__]=]))
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
local f=assert(io.open(path,'w'));assert(f:write(j.stringify({originalFullAudit=true,producer=P.producer,workerSha256=P.worker,configSha256=P.hash,coreCorrectionOnly=true,nssEnabled=false,atUptime=now})..'\n'));assert(f:close());assert(fs.chmod(path,600));print('RESIDENT_CORE_PRECOMMIT_VERIFIED')`,spec);}
export function readback(spec){return bind(String.raw`local j=require('luci.jsonc');local fs=require('nixio.fs');local P=assert(j.parse([=[__PLAN__]=]))
local function read(p)local f=assert(io.open(p));local s=f:read('*a');f:close();return s end
local function hash(name)local f=assert(io.popen('/usr/bin/sha256sum '..P.base..'/'..name));local s=f:read(256);assert(f:close());return assert(s:match('^(%x+) '))end
print(j.stringify({transactionResult=read('/root/router-project/transactions/'..P.id..'/result'),active=fs.lstat('/root/router-project/active-transaction')~=nil,workerSha256=hash('worker.lua'),coreSha256=hash('classifier-core.lua'),configSha256=hash('config.json'),pointer=read('/root/router-project/game-classifier-generation')}))`,spec);}
export function stageCancel(spec){return bind(String.raw`local j=require('luci.jsonc');local fs=require('nixio.fs');local P=assert(j.parse([=[__PLAN__]=]))
local function read(p,l)local f=assert(io.open(p));local s=f:read(l+1);f:close();assert(#s<=l);return s end
assert(not fs.lstat('/root/router-project/active-transaction'))
assert(read('/root/router-project/transactions/'..P.id..'/result',128)==P.result..'\n')
assert(read('/root/router-project/game-classifier-generation',512)==P.base..' '..P.hash..'\n')
assert(read('/proc/sys/kernel/random/boot_id',128):gsub('%s+$','')==P.boot)
local d=assert(fs.lstat(P.path));assert(d.type=='dir'and d.uid==0 and d.gid==0 and d.modedec==700)
local o=assert(fs.lstat(P.path..'/owner'));assert(o.dev==P.dev and o.ino==P.ino and o.type=='reg'and o.nlink==1 and o.modedec==600)
local owner,boot=read(P.path..'/owner',256):match('^(%S+) (%S+) ');assert(owner==P.owner and boot==P.boot)
local a={};for x in assert(read('/proc/'..P.pid..'/stat',8192):match('^%d+ %b() (.*)$')):gmatch('%S+')do a[#a+1]=x end
assert(a[20]==P.start and tonumber(a[2])==1 and a[1]~='Z')
print(j.stringify({passed=true,independentStageIdentityVerified=true,onlyOwnedPassiveStageCancelled=true}))`,spec);}
