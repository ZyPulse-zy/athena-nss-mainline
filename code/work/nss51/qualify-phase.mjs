// Pure process-model cases plus live read-only phases; never authorizes ECM.
import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';
import {connectRouter} from '../nss20/connect-router.mjs';import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
const source=fs.readFileSync('work/nss51/core-guard-phase.lua','utf8'),old=fs.readFileSync('work/nss49/core-guard-phase.lua','utf8');
const delta=JSON.parse(fs.readFileSync('work/nss51/phase-delta.json'));const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
assert.equal(source.replace(delta.to,()=>delta.from),old);assert.equal(sha(source),delta.candidateSha256);
const tests=String.raw`
local results={};local expected={pid=100,start='1000'}
local function test(name,fn)local ok,err=pcall(fn);assert(ok,name..': '..tostring(err));results[#results+1]={name=name,passed=true}end
local function lib()return assert(loadstring(SOURCE))()end
local function stat(pid,parent,start,state)local a={state or'S',tostring(parent),'0'};for i=4,19 do a[i]='0'end;a[20]=start;return pid..' (fixture) '..table.concat(a,' ')end
local function fixture()
 local f={['/proc/100/stat']=stat(100,1,'1000'),['/proc/100/cmdline']='/bin/sh\0/root/router-project/scripts/core-guard.sh\0watch\0',['/proc/100/wchan']='do_wait',['/proc/200/stat']=stat(200,100,'2000'),['/proc/200/cmdline']=table.concat({'sleep','5'},'\0')..'\0',['/proc/200/wchan']='hrtimer_nanosleep',['/proc/300/stat']=stat(300,1,'3000'),['/proc/self/auxv']=string.char(17)..string.rep('\0',7)..string.char(100)..string.rep('\0',7)..string.rep('\0',16)}
 local reads,enumerations={},0;local ids={'100','200','300'};local function read(p,l)reads[p]=(reads[p]or 0)+1;local s=assert(f[p],p);assert(#s<=l);return s end
 local fs={dir=function()enumerations=enumerations+1;local k=0;return function()k=k+1;return ids[k]end end}
 return lib(),f,read,fs,reads,ids,function()return enumerations end
end
test('fresh discovery reads only stat for unrelated processes',function()local m,f,r,fs,reads=fixture();local s=m.scan(fs,r,expected);assert(s.parentScopedInventory and s.sleep.pid==200 and s.clockTicks==100 and s.inventoryProcesses==3);assert(reads['/proc/300/stat']==1 and not reads['/proc/300/cmdline']and not reads['/proc/300/wchan'])end)
test('cached child still checks full identity without enumeration',function()local m,f,r,fs,reads,ids,counts=fixture();m.scan(fs,r,expected);local n=counts();local s=m.scan(fs,r,expected);assert(s.sleep.pid==200 and counts()==n and reads['/proc/200/cmdline']>=2 and reads['/proc/200/wchan']>=2)end)
for _,kind in ipairs({'parent','argv','duration','state','wchan'})do test('wrong child '..kind..' cannot be returned',function()local m,f,r,fs=fixture();if kind=='parent'then f['/proc/200/stat']=stat(200,300,'2000')elseif kind=='state'then f['/proc/200/stat']=stat(200,100,'2000','R')elseif kind=='argv'then f['/proc/200/cmdline']='not-sleep\05\0'elseif kind=='duration'then f['/proc/200/cmdline']=table.concat({'sleep','6'},'\0')..'\0'else f['/proc/200/wchan']='wrong'end;assert(not m.scan(fs,r,expected).sleep)end)end
test('cached reparenting forces discovery without a phase',function()local m,f,r,fs=fixture();m.scan(fs,r,expected);f['/proc/200/stat']=stat(200,300,'2000');local s=m.scan(fs,r,expected);assert(s.parentScopedInventory and not s.sleep)end)
test('cached PID reuse revalidates a new complete child identity',function()local m,f,r,fs=fixture();m.scan(fs,r,expected);f['/proc/200/stat']=stat(200,100,'2001');local s=m.scan(fs,r,expected);assert(s.parentScopedInventory and s.sleep.start=='2001')end)
test('multiple direct sleep children fail closed',function()local m,f,r,fs,reads,ids=fixture();ids[#ids+1]='201';for _,k in ipairs({'stat','cmdline','wchan'})do f['/proc/201/'..k]=f['/proc/200/'..k]end;f['/proc/201/stat']=stat(201,100,'2010');assert(not pcall(m.scan,fs,r,expected))end)
test('guard PID reuse before discovery rejected',function()local m,f,r,fs=fixture();f['/proc/100/stat']=stat(100,1,'other');assert(not pcall(m.scan,fs,r,expected))end)
test('guard PID reuse during discovery rejected',function()local m,f,r,fs=fixture();local count=0;local function changed(p,l)if p=='/proc/100/stat'then count=count+1;if count>=3 then return stat(100,1,'other')end end;return r(p,l)end;assert(not pcall(m.scan,fs,changed,expected))end)
test('guard absence rejected',function()local m,f,r,fs=fixture();f['/proc/100/stat']=nil;assert(not pcall(m.scan,fs,r,expected))end)
test('guard argv change rejected',function()local m,f,r,fs=fixture();f['/proc/100/cmdline']='other\0';assert(not pcall(m.scan,fs,r,expected))end)
test('4096 process inventory bound retained',function()local m,f,r,fs=fixture();fs.dir=function()local k=0;return function()k=k+1;if k<=4097 then return tostring(10000+k)end end end;assert(not pcall(m.scan,fs,r,expected))end)
local function waitTest(name,success,fn)
 test(name,function()local t=100;local m=lib();local function now()return t end;local ok,res=pcall(m.waitFresh,expected,function()return fn(t-100,function(x)t=t+x end)end,now,function()t=t+0.03 end,100.3);assert(ok==success,tostring(res))end)
end
local function state(t)local p=t<0.06 and 200 or 201;return{guard={pid=100,start='1000',state='S'},sleep={pid=p,start=t<0.06 and'2000'or'2001',ppid=100,state='S',wchan='hrtimer_nanosleep'}}end
waitTest('legacy bounded child transition retained',true,function(t)return state(t)end)
waitTest('same old child never grants phase',false,function()return state(0)end)
waitTest('200 ms scan bound retained',false,function(t,advance)advance(0.21);return state(t)end)
waitTest('old absolute birth cannot be revived by rediscovery',false,function(t)local s=state(t);s.clockTicks=100;s.sleep.start='0';return s end)
waitTest('changed guard refused by wait',false,function(t)local s=state(t);s.guard.start='other';return s end)
waitTest('unconfirmed sleep refused by wait',false,function(t)local s=state(t);s.sleep.wchan='unknown';return s end)
waitTest('future sleep birth refused',false,function(t)local s=state(t);s.clockTicks=100;s.sleep.start='100000';return s end)
local n=require('nixio');local fs=require('nixio.fs');local j=require('luci.jsonc')
local function read(p,l)local f=assert(io.open(p));local s=f:read(l+1)or'';f:close();assert(#s<=l);return s end
local function now()return assert(tonumber(read('/proc/uptime',128):match('^[%d.]+')))end
local function stopped()assert(tonumber(read('/sys/kernel/debug/ecm/front_end_ipv4_stop',128))==1 and tonumber(read('/sys/kernel/debug/ecm/front_end_ipv6_stop',128))==1);for _,p in ipairs({'ecm_db/connection_count','ecm_nss_ipv4/accelerated_count','ecm_nss_ipv6/accelerated_count','ecm_nss_ipv4/pending_accel_count','ecm_nss_ipv6/pending_accel_count','ecm_nss_ipv4/pending_decel_count','ecm_nss_ipv6/pending_decel_count'})do assert(tonumber(read('/sys/kernel/debug/ecm/'..p,128))==0)end end
local m=lib();local initial=m.scan(fs,read);local pin={pid=initial.guard.pid,start=initial.guard.start};local live={};stopped()
for i=1,2 do local p=m.waitFresh(pin,function()stopped();return m.scan(fs,read,pin)end,now,function()n.nanosleep(0,30000000)end,now()+7);assert(p.birthClockChecked and p.scopedIdentityRead and p.scanSeconds<=0.2);live[#live+1]=p;stopped()end
print(j.stringify({passed=true,cases=results,liveReadOnlyPhases=live,clockTicks=m.clockTicks(read),noRouterWrites=true,noNssPermission=true,waitFreshByteIdentical=true,guardUntouched=true}))`;
const code='local SOURCE=[==['+source+']==]\n'+tests;
const c=await connectRouter();try{const e=encode("/usr/bin/timeout -k 1 20 /usr/bin/lua - <<'NSS51_PHASE_QUALIFY_READONLY'\n"+code+'\nNSS51_PHASE_QUALIFY_READONLY\n');const raw=receipt(await c.run(e.command),e);fs.writeFileSync('work/nss51/phase-tests-raw-private.json',JSON.stringify(raw,null,2)+'\n',{flag:'wx'});assert.equal(raw.code,0,raw.stderr);const r=JSON.parse(raw.stdout);assert.ok(r.passed&&r.cases.length===22&&r.liveReadOnlyPhases.length===2);Object.assign(r,{sourceSha256:sha(source),originalSourceSha256:sha(old),fixtureSha256:sha(tests),nativeLua:true,syntheticCasesUseMockedProcessFiles:true,productionGuardUntouched:true});fs.writeFileSync('work/nss51/phase-qualified.json',JSON.stringify(r,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({passed:true,cases:r.cases.length,livePhases:r.liveReadOnlyPhases.map(p=>({scanSeconds:p.scanSeconds,birthAge:p.maxBirthAgeSeconds})),noRouterWrites:true,waitFreshByteIdentical:true}));}finally{c.close()}
