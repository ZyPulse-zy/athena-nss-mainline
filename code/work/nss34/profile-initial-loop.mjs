import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {connectRouter} from '../nss20/connect-router.mjs';import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
const source=fs.readFileSync('work/nss34/original-core-guard-phase.lua','utf8');
const code=String.raw`local n=require('nixio');local fs=require('nixio.fs');local j=require('luci.jsonc');local reads=0
local function read(p,l)local f=assert(io.open(p));local s=f:read(l+1);f:close();assert(#s<=l);reads=reads+1;return s end
local function now()return tonumber(read('/proc/uptime',128):match('^[%d.]+'))end
local function closed()for _,p in ipairs({'front_end_ipv4_stop','front_end_ipv6_stop'})do assert(tonumber(read('/sys/kernel/debug/ecm/'..p,128))==1)end;for _,p in ipairs({'ecm_db/connection_count','ecm_nss_ipv4/accelerated_count','ecm_nss_ipv6/accelerated_count','ecm_nss_ipv4/pending_accel_count','ecm_nss_ipv6/pending_accel_count','ecm_nss_ipv4/pending_decel_count','ecm_nss_ipv6/pending_decel_count'})do assert(tonumber(read('/sys/kernel/debug/ecm/'..p,128))==0)end end
local Phase=assert(loadstring([====[${source}]====]))();closed();local initial=Phase.scan(fs,read);local expected={pid=initial.guard.pid,start=initial.guard.start}
local began=now();local rows={};local due=began+15
repeat
 local t0=now();local n0=reads;closed();local t1=now();local p=Phase.scan(fs,read,expected);local t2=now();local phaseReads=reads-n0
 local raw=read('/tmp/router-project-game-classifier/classification.json',4194304);local t3=now();local s=assert(j.parse(raw));local t4=now();local q=s.snapshot and s.snapshot.provenance
 rows[#rows+1]={at=t4,closedSeconds=t1-t0,phaseSeconds=t2-t1,readSeconds=t3-t2,parseSeconds=t4-t3,iterationReads=phaseReads,fullInventory=p.fullInventory==true,refreshInventory=p.refreshInventory==true,sourceSequence=q and q.sequence,sourceAge=q and t4-q.startedAtUptime,publicationDelay=q and s.atUptime-q.startedAtUptime,ageOnlyReserveAvailable=q and t4<q.startedAtUptime+1,classifiedFlowCount=s.snapshot and #s.snapshot.flows,status=s.status}
 n.nanosleep(0,20000000)
until now()>=due
closed();print(j.stringify({routerWrites=false,nssOpened=false,actualFlowAdmissionChecked=false,guard=expected,started=began,ended=now(),rows=rows}))`;
const e=encode("/usr/bin/lua - <<'NSS34_READONLY_LOOP'\n"+code+"\nNSS34_READONLY_LOOP\n");
const c=await connectRouter();try{const raw=receipt(await c.run(e.command),e);fs.writeFileSync('work/nss34/loop-profile-raw-private.json',JSON.stringify(raw,null,2));assert.equal(raw.code,0,raw.stderr);const data=JSON.parse(raw.stdout);data.observedAt=new Date().toISOString();data.sourceSha256=crypto.createHash('sha256').update(source).digest('hex');data.execBytes=e.execBytes;fs.writeFileSync('work/nss34/loop-profile.json',JSON.stringify(data,null,2)+'\n');
const summary={samples:data.rows.length,fullInventory:data.rows.filter(r=>r.fullInventory).length,maxPhaseSeconds:Math.max(...data.rows.map(r=>r.phaseSeconds)),meanPhaseSeconds:data.rows.reduce((n,r)=>n+r.phaseSeconds,0)/data.rows.length,maxReads:Math.max(...data.rows.map(r=>r.iterationReads)),ageOnlyReady:data.rows.filter(r=>r.ageOnlyReserveAvailable).length,routerWrites:false,actualFlowAdmissionChecked:false};console.log(JSON.stringify(summary));}finally{c.close()}
