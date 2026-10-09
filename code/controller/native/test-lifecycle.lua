local root=assert(arg[0]:match('^(.*)/[^/]+$'));local m=dofile(root..'/lifecycle.lua')
local f={lock=false,gate=false,receipts=false,stop4=1,stop6=1,accelerated4=0,accelerated6=0,connections=0,mwan=0,originalGuard=true}
local r={phase='restored',rollbackConfirmed=true,running=false,supervisedOwnerPid=42,finishedAtUptime=101}
local count=0
local function test(expected,retries,stopped)count=count+1;assert(m.retry(r,f,42,100,retries or 0,stopped)==expected,'Recovery case '..count)end
test(true);test(false,0,true);test(true,2);test(false,3)
for _,key in ipairs{'lock','gate','receipts'}do f[key]=true;test(false);f[key]=false end
for _,key in ipairs{'stop4','stop6'}do f[key]=0;test(false);f[key]=1 end
for _,key in ipairs{'accelerated4','accelerated6','connections','mwan'}do f[key]=1;test(false);f[key]=0 end
f.originalGuard=false;test(false);f.originalGuard=true
r.phase='rollback-unconfirmed';test(false);r.phase='restored'
r.rollbackConfirmed=false;test(false);r.rollbackConfirmed=true
r.running=true;test(false);r.running=false
r.supervisedOwnerPid=41;test(false);r.supervisedOwnerPid=42
r.finishedAtUptime=99;test(false);r.finishedAtUptime=101
test(true);assert(m.maximumRetries==3 and m.delays[1]==5 and m.delays[2]==15 and m.delays[3]==30)
assert(m.startupRetry(f,true,0,false));assert(not m.startupRetry(f,false,0,false))
assert(not m.startupRetry(f,true,3,false));assert(not m.startupRetry(f,true,0,true))
f.gate=true;assert(not m.startupRetry(f,true,0,false));f.gate=false
count=count+5
print('bounded-recovery-models-passed '..count)
