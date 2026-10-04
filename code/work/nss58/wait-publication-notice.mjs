import fs from 'node:fs';import assert from 'node:assert/strict';
import {waitReady as classificationReady} from '../nss49/wait-ready-candidate.mjs';
import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
export async function waitReady(c,ctx,label){
 const lib=fs.readFileSync('work/nss58/publication-notice.lua','utf8');
 const stat=encode("/usr/bin/lua - <<'NSS58_NOTICE_INITIAL'\nlocal fs=require('nixio.fs');local j=require('luci.jsonc');local L=assert(loadstring([====["+lib+"]====]))();local s=L.valid(assert(fs.lstat('/tmp/router-project-game-classifier/snapshot.json')));print(j.stringify(s))\nNSS58_NOTICE_INITIAL\n");
 const initialRaw=receipt(await c.run(stat.command),stat);assert.equal(initialRaw.code,0,initialRaw.stderr);const initial=JSON.parse(initialRaw.stdout);
 const hint=await classificationReady(c,ctx,label);const spec={initial,base:ctx.base,hash:ctx.configHash};
 const code=String.raw`local j=require('luci.jsonc');local fs=require('nixio.fs');local n=require('nixio');local S=assert(j.parse([===[${JSON.stringify(spec)}]===]));local L=assert(loadstring([====[${lib}]====]))()
local function read(p,l)local f=assert(io.open(p));local x=f:read(l+1)or'';f:close();assert(#x<=l);return x end
local function now()return tonumber(read('/proc/uptime',128):match('^[%d.]+'))end
local function closed()for _,k in ipairs({'front_end_ipv4_stop','front_end_ipv6_stop'})do assert(tonumber(read('/sys/kernel/debug/ecm/'..k,128))==1)end;for _,k in ipairs({'ecm_db/connection_count','ecm_nss_ipv4/accelerated_count','ecm_nss_ipv6/accelerated_count','ecm_nss_ipv4/pending_accel_count','ecm_nss_ipv6/pending_accel_count','ecm_nss_ipv4/pending_decel_count','ecm_nss_ipv6/pending_decel_count'})do assert(tonumber(read('/sys/kernel/debug/ecm/'..k,128))==0)end end
closed();assert(not fs.lstat('/root/router-project/active-transaction'));assert(read('/root/router-project/game-classifier-generation',512)==S.base..' '..S.hash..'\n');local started=now();local out=L.wait(S.initial,function()closed();return assert(fs.lstat('/tmp/router-project-game-classifier/snapshot.json'))end,now,function()n.nanosleep(0,50000000)end,started+4);closed();out.startedAt=started;out.finishedAt=now();out.routerConfigurationWrites=false;out.fullSnapshotNotReadByHint=true;print(j.stringify(out))`;
 const e=encode(ctx.base+'/group-runner 5 /bin/sh -c '+"'"+("/usr/bin/lua - <<'NSS58_NOTICE_READONLY'\n"+code+"\nNSS58_NOTICE_READONLY\n").replaceAll("'","'\\''")+"'");
 const raw=receipt(await c.run(e.command),e);fs.writeFileSync('work/nss58/'+label+'-notice-raw-private.json',JSON.stringify(raw,null,2)+'\n',{flag:'wx'});assert.equal(raw.code,0,raw.stderr);const out=JSON.parse(raw.stdout);assert.ok(out.noticeObserved&&out.nssAdmissionAllowed===false);fs.writeFileSync('work/nss58/'+label+'-notice-private.json',JSON.stringify({...out,observedAt:new Date().toISOString()},null,2)+'\n',{flag:'wx'});
 return hint.alignment;
}
