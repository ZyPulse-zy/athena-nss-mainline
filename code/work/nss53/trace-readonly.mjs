// Full consumer callback and new ancestry parser, fresh runtime ownership pin.
// Read-only on the router; no load generation or NSS permission.
import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {connectRouter}from '../nss20/connect-router.mjs';import {encode,receipt}from '../nss11/v7-observe-repair/observe2/transport.mjs';
import {verifyPreparation}from '../nss51/session-binding.mjs';
verifyPreparation();const label=process.argv[2];assert.match(label,/^[a-z0-9-]+$/);
const root='work/nss53',output=root+'/'+label+'-trace-private.json';assert.ok(!fs.existsSync(output));
const ctx=JSON.parse(fs.readFileSync('work/nss47/deployment-latest.json')),cfg=JSON.parse(fs.readFileSync(ctx.localDir+'/config.json'));
const owner={base:ctx.base,configSha256:ctx.configHash,workerSha256:cfg.files['worker.lua']};
const phase=fs.readFileSync(root+'/core-guard-phase.lua','utf8'),adapter=fs.readFileSync(root+'/classifier.lua','utf8');
assert.equal(phase,fs.readFileSync('work/nss52/core-guard-phase.lua','utf8'));
const consumer=adapter.slice(0,adapter.indexOf('function M.pair('))+'return M\nend)()\n';
const start=adapter.indexOf('function A.new('),cut=adapter.indexOf(' local epoch\n',start),cs=adapter.indexOf(' function out.candidates()',cut),ce=adapter.indexOf(' function out.ready()',cs);assert.ok(start>0&&cut>start&&cs>cut&&ce>cs);
const reader=consumer+'local A={}\n'+adapter.slice(start,cut)+' local out={}\n'+adapter.slice(cs,ce)+'return out\nend\nreturn A';
const code=`local M=(function()\n${phase}\nend)();local A=(function()\n${reader}\nend)();local fs=require('nixio.fs');local j=require('luci.jsonc');local n=require('nixio')
local function read(p,l)local f=assert(io.open(p));local s=f:read(l+1)or'';f:close();assert(#s<=l);return s end
local function now()return assert(tonumber(read('/proc/uptime',128):match('^[%d.]+')))end
local function run(c)assert(c:match('^/usr/bin/sha256sum /root/router%-project/classifier/'));local f=assert(io.popen(c));local s=f:read('*a');f:close();return s end
local paths={'ecm_db/connection_count','ecm_nss_ipv4/accelerated_count','ecm_nss_ipv6/accelerated_count','ecm_nss_ipv4/pending_accel_count','ecm_nss_ipv6/pending_accel_count','ecm_nss_ipv4/pending_decel_count','ecm_nss_ipv6/pending_decel_count'}
local function stopped()assert(tonumber(read('/sys/kernel/debug/ecm/front_end_ipv4_stop',128))==1 and tonumber(read('/sys/kernel/debug/ecm/front_end_ipv6_stop',128))==1);for _,p in ipairs(paths)do assert(tonumber(read('/sys/kernel/debug/ecm/'..p,128))==0)end end
stopped();local initial=M.scan(fs,read);local pin={pid=initial.guard.pid,start=initial.guard.start};local P={coreGuard=pin,classifierOwner=assert(j.parse([==[${JSON.stringify(owner)}]==])),boot=read('/proc/sys/kernel/random/boot_id',128):gsub('%s+$',''),selected={}}
local record={};local classifier=A.new(P,fs,j,read,now,run,record);local attempts={}
local function telemetry()return{at=now(),cpu=read('/proc/stat',16384),softnet=read('/proc/net/softnet_stat',16384),rxBytes=tonumber(read('/sys/class/net/lan4/statistics/tx_bytes',128)),pps=tonumber(read('/sys/class/net/lan4/statistics/tx_packets',128))}end
for attempt=1,3 do
 local rows={};local nextObservation=0;local lastEnd;local previous;local before=telemetry();local started=now()
 local ok,result=pcall(M.waitFresh,pin,function()
  local a=now();local row={began=a,priorGap=lastEnd and a-lastEnd or nil};stopped()
  if a>=nextObservation then local f=classifier.candidates();row.observationSeconds=now()-a;row.sourceAge=now()-f.startedAtUptime;row.sequence=f.sourceSequence;row.flows=#f.flows;nextObservation=now()+0.5 end
  local s=M.scan(fs,read,pin);local b=now();row.ended=b;row.scanSeconds=b-a;row.fullInventory=s.fullInventory==true or s.refreshInventory==true;row.inventoryProcesses=s.inventoryProcesses
  if s.sleep then local p=s.sleep;row.sleepPid=p.pid;row.sleepStart=p.start;row.birthAge=b-tonumber(p.start)/s.clockTicks;row.changed=previous and(previous.pid~=p.pid or previous.start~=p.start)or false;previous={pid=p.pid,start=p.start}end
  rows[#rows+1]=row;lastEnd=b;return s
 end,now,function()n.nanosleep(0,30000000)end,started+7)
 stopped();attempts[#attempts+1]={passed=ok,result=result,rows=rows,seconds=now()-started,before=before,after=telemetry()}
end
stopped();print(j.stringify({readonly=true,attempts=attempts,guardUntouched=true,ecmClosedThroughout=true,completeConsumerCandidatesPathExecuted=true,unusedAdapterFunctionsOmitted=true,originalConsumerByteIdentical=true,freshRuntimePin=true,notInstalled=true}))`;
const e=encode("/usr/bin/timeout -k 1 24 /usr/bin/lua - <<'NSS53_FULL_READONLY'\n"+code+'\nNSS53_FULL_READONLY\n');
const c=await connectRouter();try{const raw=receipt(await c.run(e.command),e);fs.writeFileSync(root+'/'+label+'-raw-private.json',JSON.stringify(raw,null,2)+'\n',{flag:'wx'});assert.equal(raw.code,0,raw.stderr);const r=JSON.parse(raw.stdout);fs.writeFileSync(output,JSON.stringify(r,null,2)+'\n',{flag:'wx'});
const safe={observedAt:new Date().toISOString(),readonly:true,execBytes:e.execBytes,phaseSha256:crypto.createHash('sha256').update(phase).digest('hex'),adapterSha256:crypto.createHash('sha256').update(adapter).digest('hex'),attempts:r.attempts.map(a=>({passed:a.passed,seconds:a.seconds,scans:a.rows.length,maxScanSeconds:Math.max(0,...a.rows.map(x=>x.scanSeconds)),maxObservationSeconds:Math.max(0,...a.rows.map(x=>x.observationSeconds||0)),lan4Mbps:(a.after.rxBytes-a.before.rxBytes)*8/(a.after.at-a.before.at)/1e6,lan4Pps:(a.after.pps-a.before.pps)/(a.after.at-a.before.at),newChildren:a.rows.filter(x=>x.changed).map(x=>({birthAge:x.birthAge,scanSeconds:x.scanSeconds,priorGap:x.priorGap,inventoryProcesses:x.inventoryProcesses}))})),ecmClosedThroughout:true,noRouterWrites:true,guardUntouched:true,completeConsumerCandidatesPathExecuted:true,unusedAdapterFunctionsOmitted:true,originalConsumerByteIdentical:true,highLoadQualificationRequiresActualLoad:true,notInstalled:true};
fs.writeFileSync(root+'/'+label+'-trace-sanitized.json',JSON.stringify(safe,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(safe));}finally{c.close();}
