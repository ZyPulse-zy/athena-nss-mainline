import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {connectRouter} from '../nss27/connect-router.mjs';import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
const lib=fs.readFileSync('work/nss58/publication-notice.lua','utf8');
const lua=String.raw`local j=require('luci.jsonc');local L=assert(loadstring([====[${lib}]====]))();local checks=0
local function copy()return{type='reg',uid=0,gid=0,nlink=1,dev=1,ino=2,size=100}end
local a=copy();assert(not L.replaced(a,copy()));checks=checks+1
local b=copy();b.ino=3;assert(L.replaced(a,b));checks=checks+1
b=copy();b.dev=2;assert(L.replaced(a,b));checks=checks+1
for _,v in ipairs({{'uid',1},{'nlink',2},{'size',4194305},{'size',0},{'type','lnk'}})do b=copy();b[v[1]]=v[2];assert(not pcall(L.replaced,a,b));checks=checks+1 end
assert(not pcall(L.wait,a,function()return copy()end,function()return 0 end,function()end,4.01));checks=checks+1
b=copy();b.ino=3;local r=L.wait(a,function()return b end,function()return 0 end,function()error('must not wait')end,4);assert(r.noticeObserved and r.nssAdmissionAllowed==false and r.originalFullAuditRequired);checks=checks+1
print(j.stringify({passed=true,checks=checks,nativePureLua=true,routerConfigurationWrites=false,nssAdmissionAllowed=false}))`;
const e=encode("/usr/bin/lua - <<'NSS58_NOTICE_BOUNDARIES'\n"+lua+"\nNSS58_NOTICE_BOUNDARIES\n");const c=await connectRouter();try{const raw=receipt(await c.run(e.command),e);fs.writeFileSync('work/nss58/notice-tests-raw-private.json',JSON.stringify(raw,null,2)+'\n',{flag:'wx'});assert.equal(raw.code,0,raw.stderr);const out=JSON.parse(raw.stdout);assert.equal(out.checks,10);out.sourceSha256=crypto.createHash('sha256').update(lib).digest('hex');fs.writeFileSync('work/nss58/notice-tests.json',JSON.stringify(out,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(out));}finally{c.close()}
