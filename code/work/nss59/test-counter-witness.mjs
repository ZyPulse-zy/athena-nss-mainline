import fs from'node:fs';import assert from'node:assert/strict';import crypto from'node:crypto';import{connectRouter}from'../nss27/connect-router.mjs';import{encode,receipt}from'../nss11/v7-observe-repair/observe2/transport.mjs';
const source=fs.readFileSync('work/nss59/fast-path.lua','utf8');const helper=source.slice(source.indexOf('function M.mayRereadCounterSnapshot'),source.indexOf('function M.verifyRenewalAck'));
const record=JSON.parse(fs.readFileSync('work/nss58/real-matched-aba-20261004121718-a769d145/last-record-private.json'));const counters={};for(const x of record.tagsAfterA.nftables)if(x.rule)for(const e of x.rule.expr)if(e.counter)counters[x.rule.comment.split(':').at(-1)]=e.counter;
const body=String.raw`local j=require('luci.jsonc');local M={};${helper}
local seed=[===[${JSON.stringify(counters)}]===];local checks=0;local function c()return assert(j.parse(seed))end
assert(M.mayRereadCounterSnapshot(c()));checks=checks+1
local x=c();x.tcp_post_down_unexpected.packets=1;assert(not M.mayRereadCounterSnapshot(x));checks=checks+1
x=c();x.tcp_post_down_expected.packets=x.tcp_post_down_expected.packets+1;assert(not M.mayRereadCounterSnapshot(x));checks=checks+1
x=c();x.tcp_post_down_expected.bytes=x.tcp_post_down_expected.bytes+1;assert(not M.mayRereadCounterSnapshot(x));checks=checks+1
x=c();x.udp_post_down_expected.packets=x.udp_post_down_expected.packets+1;assert(not M.mayRereadCounterSnapshot(x));checks=checks+1
x=c();x.tcp_post_up_total.packets=0;assert(not M.mayRereadCounterSnapshot(x));checks=checks+1
x=c();x.tcp_post_down_expected.packets=x.tcp_post_down_total.packets;x.tcp_post_down_expected.bytes=x.tcp_post_down_total.bytes;assert(not M.mayRereadCounterSnapshot(x));checks=checks+1
print(j.stringify({passed=true,checks=checks,nativePureLua=true,nssAdmissionAllowed=false,routerConfigurationWrites=false}))`;
const e=encode("/usr/bin/lua - <<'NSS59_COUNTER_BOUNDARIES'\n"+body+"\nNSS59_COUNTER_BOUNDARIES\n"),c=await connectRouter();try{const raw=receipt(await c.run(e.command),e);fs.writeFileSync('work/nss59/counter-tests-raw-private.json',JSON.stringify(raw,null,2)+'\n',{flag:'wx'});assert.equal(raw.code,0,raw.stderr);const out=JSON.parse(raw.stdout);assert.equal(out.checks,7);const h=s=>crypto.createHash('sha256').update(s).digest('hex');Object.assign(out,{sourceSha256:h(source),helperSha256:h(helper),realRejectedFrameSource:'NSS58-after-A'});fs.writeFileSync('work/nss59/counter-tests.json',JSON.stringify(out,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(out));}finally{c.close()}
