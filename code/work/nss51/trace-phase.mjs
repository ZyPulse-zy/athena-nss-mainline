// Read-only reproduction of the exact NSS49 sleep synchronizer. No staging.
import fs from 'node:fs';import assert from 'node:assert/strict';
import {connectRouter} from '../nss20/connect-router.mjs';
import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
const label=process.argv[2],poll=process.argv[3]==='publication';assert.match(label,/^[a-z0-9-]+$/);
const output='work/nss51/'+label+'-trace-private.json';assert.ok(!fs.existsSync(output));
const pin=JSON.parse(fs.readFileSync('work/nss50/real-matched-aba-20261004083901-c4b7888d/stage-plan-private.json')).coreGuard;
const phase=fs.readFileSync('work/nss49/core-guard-phase.lua','utf8');
const code=`local M=(function()\n${phase}\nend)();local fs=require('nixio.fs');local j=require('luci.jsonc');local n=require('nixio');local pin={pid=${pin.pid},start='${pin.start}'}
local function read(p,l)local f=assert(io.open(p));local s=f:read(l+1)or'';f:close();assert(#s<=l);return s end
local function now()return assert(tonumber(read('/proc/uptime',128):match('^[%d.]+')))end
local paths={'ecm_db/connection_count','ecm_nss_ipv4/accelerated_count','ecm_nss_ipv6/accelerated_count','ecm_nss_ipv4/pending_accel_count','ecm_nss_ipv6/pending_accel_count','ecm_nss_ipv4/pending_decel_count','ecm_nss_ipv6/pending_decel_count'}
local function stopped()assert(tonumber(read('/sys/kernel/debug/ecm/front_end_ipv4_stop',128))==1 and tonumber(read('/sys/kernel/debug/ecm/front_end_ipv6_stop',128))==1);for _,p in ipairs(paths)do assert(tonumber(read('/sys/kernel/debug/ecm/'..p,128))==0)end end
local rows={};local nextPublication=0;local lastEnd;local previous;local started=now();stopped()
local ok,result=pcall(M.waitFresh,pin,function()
 local a=now();local row={began=a,priorGap=lastEnd and a-lastEnd or nil};stopped()
 if ${poll?'true':'false'} and a>=nextPublication then local p=assert(j.parse(read('/tmp/router-project-game-classifier/classification.json',4194304)));row.publicationReadSeconds=now()-a;row.sourceAge=now()-p.snapshot.provenance.startedAtUptime;row.sequence=p.snapshot.provenance.sequence;nextPublication=now()+0.5 end
 local s=M.scan(fs,read,pin);local b=now();row.ended=b;row.scanSeconds=b-a;row.fullInventory=s.fullInventory==true or s.refreshInventory==true
 if s.sleep then local p=s.sleep;row.sleepPid=p.pid;row.sleepStart=p.start;row.birthAge=b-tonumber(p.start)/s.clockTicks;row.changed=previous and(previous.pid~=p.pid or previous.start~=p.start)or false;previous={pid=p.pid,start=p.start}end
 rows[#rows+1]=row;lastEnd=b;return s
end,now,function()n.nanosleep(0,30000000)end,started+7)
stopped();print(j.stringify({readonly=true,passed=ok,result=result,rows=rows,seconds=now()-started,guardUntouched=true,ecmClosedThroughout=true,publicationPolling=${poll?'true':'false'}}))`;
const c=await connectRouter();try{const e=encode("/usr/bin/timeout -k 1 10 /usr/bin/lua - <<'NSS51_PHASE_READONLY'\n"+code+'\nNSS51_PHASE_READONLY\n');const raw=receipt(await c.run(e.command),e);assert.equal(raw.code,0,raw.stderr);const r=JSON.parse(raw.stdout);fs.writeFileSync(output,JSON.stringify(r,null,2)+'\n',{flag:'wx'});const out={readonly:true,passed:r.passed,seconds:r.seconds,scans:r.rows.length,fullInventories:r.rows.filter(x=>x.fullInventory).length,maximumScanSeconds:Math.max(...r.rows.map(x=>x.scanSeconds)),newChildren:r.rows.filter(x=>x.changed).map(x=>({birthAge:x.birthAge,scanSeconds:x.scanSeconds,priorGap:x.priorGap})),ecmClosedThroughout:r.ecmClosedThroughout};console.log(JSON.stringify(out));}finally{c.close()}
