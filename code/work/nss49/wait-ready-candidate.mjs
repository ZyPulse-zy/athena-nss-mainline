// Bound readonly scheduling hint. The original complete locked audit is still required.
import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {connectRouter} from '../nss20/connect-router.mjs';import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
export async function waitReady(c,ctx,label){
 assert.match(label,/^[a-zA-Z0-9_-]+$/);const deployment=JSON.parse(fs.readFileSync('work/nss49/deployment-latest.json')),cfg=JSON.parse(fs.readFileSync(deployment.localDir+'/config.json'));
 const spec={base:ctx.base,configHash:ctx.configHash,generation:cfg.generation,boot:cfg.adoptionBoot};
 const library=fs.readFileSync('work/nss49/publication-wait.lua','utf8');
 const code=String.raw`local n=require('nixio');local fs=require('nixio.fs');local j=require('luci.jsonc');local S=assert(j.parse([===[${JSON.stringify(spec)}]===]))
local function read(p,l)local f=assert(io.open(p));local s=f:read(l+1)or'';f:close();assert(#s<=l);return s end
local function now()return tonumber(read('/proc/uptime',128):match('^[%d.]+'))end
local function stable(p,l)local a=assert(fs.lstat(p));assert(a.type=='reg'and a.uid==0 and a.gid==0 and a.nlink==1);local s=read(p,l);local b=assert(fs.lstat(p));assert(a.dev==b.dev and a.ino==b.ino,'Publication changed during scheduling read');return s,b end
assert(read('/root/router-project/game-classifier-generation',512)==S.base..' '..S.configHash..'\n')
assert(not fs.lstat('/root/router-project/active-transaction'),'Active transaction cannot await publication')
local function closed()for _,k in ipairs({'front_end_ipv4_stop','front_end_ipv6_stop'})do assert(tonumber(read('/sys/kernel/debug/ecm/'..k,128))==1)end;for _,k in ipairs({'ecm_db/connection_count','ecm_nss_ipv4/accelerated_count','ecm_nss_ipv6/accelerated_count','ecm_nss_ipv4/pending_accel_count','ecm_nss_ipv6/pending_accel_count','ecm_nss_ipv4/pending_decel_count','ecm_nss_ipv6/pending_decel_count'})do assert(tonumber(read('/sys/kernel/debug/ecm/'..k,128))==0)end end
local cached;local ram='/tmp/router-project-game-classifier';local ioPhase='before-poll'
local function current()
 ioPhase='check-closed-identity';closed();assert(read('/proc/sys/kernel/random/boot_id',128):gsub('%s+$','')==S.boot);assert(not fs.lstat(ram..'/stopped'))
 ioPhase='stat-classification-publication'
 local st=assert(fs.lstat(ram..'/classification.json'));assert(st.type=='reg'and st.uid==0 and st.gid==0 and st.nlink==1)
 if not cached or st.dev~=cached.dev or st.ino~=cached.ino then
  ioPhase='read-parse-classification-publication';local raw,after=stable(ram..'/classification.json',4194304);local s=assert(j.parse(raw));assert(s.publication=='before-software-baseline');local p=assert(s.snapshot.provenance);local projection=assert(s.snapshot.admissionProjection);assert(projection.version==1 and projection.scope=='bulk-and-admitted-rt'and projection.sourceSequence==p.sequence and projection.candidateFlowCount==#s.snapshot.flows and projection.completeInputFlowCount>=#s.snapshot.flows)
  assert(s.configSha256==S.configHash and s.generation==S.generation and s.boot==S.boot and s.status=='running'and s.dataHealthy==true and s.nssPermit==false and not s.error)
  assert(p.version==1 and p.method=='conntrack-cli'and p.rawStatus==0 and p.exitCode==0 and p.boot==S.boot)
  local text=read('/proc/'..s.pid..'/stat',8192);local a={};for v in assert(text:match('^%d+ %b() (.*)$')):gmatch('%S+')do a[#a+1]=v end;assert(a[20]==s.start and a[1]~='Z')
  assert(read('/proc/'..s.pid..'/cmdline',8192)==table.concat({'/usr/bin/lua',S.base..'/worker.lua','watch',S.base,S.configHash},'\0')..'\0')
  cached={dev=after.dev,ino=after.ino,value={sequence=p.sequence,producer=s.producer,queryStart=p.startedAtUptime,queryFinished=p.finishedAtUptime,published=s.atUptime,healthy=true}}
 end
 ioPhase='check-guardian';local g=assert(j.parse(stable(ram..'/guardian.json',8192)));assert(g.healthy==true and g.producer==cached.value.producer and g.configSha256==S.configHash and now()-g.atUptime<6);ioPhase='poll-complete'
 return cached.value
end
local M=assert(loadstring([====[${library}]====]))();local start=now();local result;local polls={};local ok,err=xpcall(function()result=M.wait(current,now,function()n.nanosleep(0,100000000)end,start+5,function(row)polls[#polls+1]=row end)end,debug.traceback)
closed();print(j.stringify({passed=ok,error=not ok and tostring(err)or nil,startedAt=start,finishedAt=now(),alignment=result,rejectedPolls=not ok and polls or nil,lastIoPhase=ioPhase,routerConfigurationWrites=false,lockHeld=false,nssAdmissionAllowed=false}))`;
 const e=encode(ctx.base+'/group-runner 6 /bin/sh -c '+"'"+("/usr/bin/lua - <<'NSS41_WAIT_FULL'\n"+code+"\nNSS41_WAIT_FULL\n").replaceAll("'","'\\''")+"'");
 const raw=receipt(await c.run(e.command),e);fs.writeFileSync('work/nss49/'+label+'-alignment-raw-private.json',JSON.stringify(raw,null,2)+'\n');assert.equal(raw.code,0,raw.stderr);const out=JSON.parse(raw.stdout);out.observedAt=new Date().toISOString();out.execBytes=e.execBytes;out.plannerSha256=crypto.createHash('sha256').update(library).digest('hex');out.wrapperSha256=crypto.createHash('sha256').update(fs.readFileSync('work/nss49/wait-ready-candidate.mjs')).digest('hex');fs.writeFileSync('work/nss49/'+label+'-alignment-private.json',JSON.stringify(out,null,2)+'\n');assert.equal(out.passed,true,out.error);return out;
}
