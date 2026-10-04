// Native pure-Lua boundaries; no config write, conntrack query, or admission.
import fs from'node:fs';import assert from'node:assert/strict';import crypto from'node:crypto';
import{connectRouter}from'../nss27/connect-router.mjs';import{encode,receipt}from'../nss11/v7-observe-repair/observe2/transport.mjs';
const lib=fs.readFileSync('work/nss54/baseline-publication-join.lua','utf8');
const test=String.raw`local M=assert(loadstring([====[${lib}]====]))();local checks=0
local E={producer='same-worker',sequence=2,queryStart=100,queryFinished=100.5,published=100.7}
local function F()return{producer=E.producer,sequence=2,queryStart=100,queryFinished=100.5,published=103}end
local function check(x)assert(x);checks=checks+1 end
local function rejects(f)check(not pcall(f))end
check(M.ready(E,F(),103.1));local old=F();old.sequence=1;check(not M.ready(E,old,103.1));local newer=F();newer.sequence=3;check(not M.ready(E,newer,103.1))
local wrong=F();wrong.producer='new-worker';rejects(function()M.ready(E,wrong,103.1)end)
wrong=F();wrong.sequence=0;rejects(function()M.ready(E,wrong,103.1)end)
wrong=F();wrong.queryStart=99.9;rejects(function()M.ready(E,wrong,103.1)end)
wrong=F();wrong.queryFinished=100.6;rejects(function()M.ready(E,wrong,103.1)end)
wrong=F();wrong.published=100.6;rejects(function()M.ready(E,wrong,103.1)end)
rejects(function()M.ready(E,F(),102.9)end);rejects(function()M.ready(E,F(),106)end)
local t=102;local count=0;local r=M.wait(E,function()count=count+1;return count<3 and old or F()end,function()return t end,function()t=t+0.5 end,106)
check(r.passed and count==3 and r.nssAdmissionAllowed==false and r.originalAuditStillRequired and not r.snapshotExpiryExtended)
t=103;rejects(function()M.wait(E,function()return old end,function()return t end,function()t=t+0.5 end,104)end)
t=103;rejects(function()M.wait(E,function()return F()end,function()return t end,function()end,107.01)end)
local j=require('luci.jsonc');print(j.stringify({passed=true,checks=checks,nativePureLua=true,routerConfigurationWrites=false,nssAdmissionAllowed=false}))`;
const c=await connectRouter();try{const e=encode("/usr/bin/lua - <<'NSS54_PURE_JOIN_CHECKS'\n"+test+"\nNSS54_PURE_JOIN_CHECKS\n");const raw=receipt(await c.run(e.command),e);fs.writeFileSync('work/nss54/join-tests-raw-private.json',JSON.stringify(raw,null,2)+'\n',{flag:'wx'});assert.equal(raw.code,0,raw.stderr);const r=JSON.parse(raw.stdout);assert.equal(r.passed,true);assert.equal(r.checks,13);r.sourceSha256=crypto.createHash('sha256').update(lib).digest('hex');fs.writeFileSync('work/nss54/join-tests.json',JSON.stringify(r,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(r));}finally{c.close()}
