// Exact original consumer and phase library, with timing diagnostics only.
import fs from 'node:fs';import assert from 'node:assert/strict';
import {connectRouter} from '../nss20/connect-router.mjs';import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
const label=process.argv[2];assert.match(label,/^[a-z0-9-]+$/);const output='work/nss51/'+label+'-exact-private.json';assert.ok(!fs.existsSync(output));
const p=JSON.parse(fs.readFileSync('work/nss50/real-matched-aba-20261004083901-c4b7888d/stage-plan-private.json'));
const phasePath=process.argv[3]==='candidate'?'work/nss51/core-guard-phase.lua':'work/nss49/core-guard-phase.lua';
const phase=fs.readFileSync(phasePath,'utf8').replace(/^\s*--[^\n]*$/gm,''),originalAdapter=fs.readFileSync('work/nss49/classifier.lua','utf8');
// Keep the complete original candidates()/readContext()/Consumer.inspect path.
// Omit unused renewal, pair and permission-planning functions to fit transport.
const consumer=originalAdapter.slice(0,originalAdapter.indexOf('function M.pair('))+'return M\nend)()\n';
const start=originalAdapter.indexOf('function A.new('),cut=originalAdapter.indexOf(' local epoch\n',start);
const cs=originalAdapter.indexOf(' function out.candidates()',cut),ce=originalAdapter.indexOf(' function out.ready()',cs);
assert.ok(start>0&&cut>start&&cs>cut&&ce>cs);
const adapter=consumer+'local A={}\n'+originalAdapter.slice(start,cut)+' local out={}\n'+originalAdapter.slice(cs,ce)+'return out\nend\nreturn A';
const code=`local M=(function()\n${phase}\nend)();local A=(function()\n${adapter}\nend)();local fs=require('nixio.fs');local j=require('luci.jsonc');local n=require('nixio');local P=assert(j.parse([==[${JSON.stringify({coreGuard:p.coreGuard,classifierOwner:p.classifierOwner,boot:p.boot})}]==]))
local function read(p,l)local f=assert(io.open(p));local s=f:read(l+1)or'';f:close();assert(#s<=l);return s end
local function now()return assert(tonumber(read('/proc/uptime',128):match('^[%d.]+')))end
local function run(c)assert(c:match('^/usr/bin/sha256sum /root/router%-project/classifier/'));local f=assert(io.popen(c));local s=f:read('*a');f:close();return s end
local paths={'ecm_db/connection_count','ecm_nss_ipv4/accelerated_count','ecm_nss_ipv6/accelerated_count','ecm_nss_ipv4/pending_accel_count','ecm_nss_ipv6/pending_accel_count','ecm_nss_ipv4/pending_decel_count','ecm_nss_ipv6/pending_decel_count'}
local function stopped()assert(tonumber(read('/sys/kernel/debug/ecm/front_end_ipv4_stop',128))==1 and tonumber(read('/sys/kernel/debug/ecm/front_end_ipv6_stop',128))==1);for _,p in ipairs(paths)do assert(tonumber(read('/sys/kernel/debug/ecm/'..p,128))==0)end end
local record={};local classifier=A.new(P,fs,j,read,now,run,record);local attempts={};stopped()
for attempt=1,3 do
 local rows={};local nextObservation=0;local lastEnd;local previous;local started=now()
 local ok,result=pcall(M.waitFresh,P.coreGuard,function()
  local a=now();local row={began=a,priorGap=lastEnd and a-lastEnd or nil};stopped()
  if a>=nextObservation then local f=classifier.candidates();row.observationSeconds=now()-a;row.sourceAge=now()-f.startedAtUptime;row.sequence=f.sourceSequence;nextObservation=now()+0.5 end
  local s=M.scan(fs,read,P.coreGuard);local b=now();row.ended=b;row.scanSeconds=b-a;row.fullInventory=s.fullInventory==true or s.refreshInventory==true
  if s.sleep then local p=s.sleep;row.sleepPid=p.pid;row.sleepStart=p.start;row.birthAge=b-tonumber(p.start)/s.clockTicks;row.changed=previous and(previous.pid~=p.pid or previous.start~=p.start)or false;previous={pid=p.pid,start=p.start}end
  rows[#rows+1]=row;lastEnd=b;return s
 end,now,function()n.nanosleep(0,30000000)end,started+7)
 stopped();attempts[#attempts+1]={passed=ok,result=result,rows=rows,seconds=now()-started}
end
print(j.stringify({readonly=true,attempts=attempts,guardUntouched=true,ecmClosedThroughout=true,exactOriginalObserver=true}))`;
const c=await connectRouter();try{const e=encode("/usr/bin/timeout -k 1 24 /usr/bin/lua - <<'NSS51_EXACT_READONLY'\n"+code+'\nNSS51_EXACT_READONLY\n');const raw=receipt(await c.run(e.command),e);assert.equal(raw.code,0,raw.stderr);const r=JSON.parse(raw.stdout);fs.writeFileSync(output,JSON.stringify(r,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({readonly:true,execBytes:e.execBytes,attempts:r.attempts.map(a=>({passed:a.passed,seconds:a.seconds,scans:a.rows.length,maxScanSeconds:Math.max(...a.rows.map(x=>x.scanSeconds)),maxObservationSeconds:Math.max(0,...a.rows.map(x=>x.observationSeconds||0)),newChildren:a.rows.filter(x=>x.changed).map(x=>({birthAge:x.birthAge,scanSeconds:x.scanSeconds,priorGap:x.priorGap}))})),ecmClosedThroughout:true}));}finally{c.close()}
