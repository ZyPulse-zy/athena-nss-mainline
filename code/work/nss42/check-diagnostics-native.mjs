// Target Lua/jsonc RAM tests. No classifier fault injection, configuration writes or NSS permission.
import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {verifyPreparation} from './session-binding.mjs';import {connectRouter} from '../nss20/connect-router.mjs';import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
verifyPreparation();const root='work/nss42',library=fs.readFileSync(root+'/publication-wait.lua','utf8');
const code=String.raw`local j=require('luci.jsonc');local function read(p)local f=assert(io.open(p));local s=f:read(128);f:close();return tonumber(s)end
local function closed()for _,k in ipairs({'front_end_ipv4_stop','front_end_ipv6_stop'})do assert(read('/sys/kernel/debug/ecm/'..k)==1)end;for _,k in ipairs({'ecm_db/connection_count','ecm_nss_ipv4/accelerated_count','ecm_nss_ipv6/accelerated_count','ecm_nss_ipv4/pending_accel_count','ecm_nss_ipv6/pending_accel_count','ecm_nss_ipv4/pending_decel_count','ecm_nss_ipv6/pending_decel_count'})do assert(read('/sys/kernel/debug/ecm/'..k)==0)end end
closed();local M=assert(loadstring([====[${library}]====]))();local cases={}
local function value(seq,start,producer)return{sequence=seq,queryStart=start or 99,queryFinished=(start or 99)+0.2,published=(start or 99)+0.4,producer=producer or 'isolated-ram-fixture',healthy=true}end
local function check(name,items,fragment,lastSequence)
 local t=100;local pos=0;local rows={};local result
 local ok,err=pcall(function()result=M.wait(function()pos=pos+1;local v=items[math.min(pos,#items)];if type(v)=='function'then return v()end;return v end,function()return t end,function()t=t+0.25 end,101,function(row)rows[#rows+1]=row end)end)
 assert(not ok and tostring(err):find(fragment,1,true));local decoded=assert(j.parse(j.stringify({passed=ok,error=tostring(err),rejectedPolls=rows,nssAdmissionAllowed=false,routerConfigurationWrites=false})))
 assert(decoded.passed==false and decoded.nssAdmissionAllowed==false and decoded.routerConfigurationWrites==false and #decoded.rejectedPolls==#rows and #rows>0)
 assert(decoded.rejectedPolls[#rows].sequence==lastSequence);assert(type(decoded.rejectedPolls[#rows].sourceAge)=='number')
 cases[#cases+1]={name=name,passed=true,serializedObservations=#rows,lastSequence=lastSequence}
end
check('timeout-rows-survive-native-jsonc',{value(10)},'deadline',10)
check('newer-but-old-source-rows-survive',{value(10),value(11,97)},'deadline',11)
check('producer-mismatch-row-survives',{value(10),value(11,99,'changed-fixture')},'Producer changed',11)
check('read-error-preserves-completed-rows',{value(10),function()error('isolated fixture read failure')end},'isolated fixture read failure',10)
closed();print(j.stringify({passed=true,checks=#cases,cases=cases,simulation=true,nativeLuaAndJsonc=true,productionFaultInjected=false,routerConfigurationWrites=false,nssOpened=false}))`;
const c=await connectRouter();try{const e=encode("/usr/bin/lua - <<'NSS42_DIAGNOSTIC_RAM'\n"+code+"\nNSS42_DIAGNOSTIC_RAM\n");assert.ok(e.execBytes<=9000);const raw=receipt(await c.run(e.command),e);fs.writeFileSync(root+'/diagnostics-native-raw-private.json',JSON.stringify(raw,null,2)+'\n');assert.equal(raw.code,0,raw.stderr);const out=JSON.parse(raw.stdout);assert.equal(out.passed,true);assert.equal(out.checks,4);out.observedAt=new Date().toISOString();out.execBytes=e.execBytes;out.plannerSha256=crypto.createHash('sha256').update(library).digest('hex');fs.writeFileSync(root+'/diagnostics-native-qualified.json',JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify(out));}finally{c.close()}
