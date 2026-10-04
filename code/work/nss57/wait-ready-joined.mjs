// Additional read-only publication join after the unchanged NSS49 ready hint.
// No retry, alternate audit input, permission, identity or deadline relaxation.
import fs from 'node:fs';import assert from 'node:assert/strict';
import {waitReady as classificationReady}from'../nss49/wait-ready-candidate.mjs';
import{encode,receipt}from'../nss11/v7-observe-repair/observe2/transport.mjs';
export async function waitReady(c,ctx,label){
 const hint=await classificationReady(c,ctx,label);const expected=hint.alignment;
 const library=fs.readFileSync('work/nss57/baseline-publication-join.lua','utf8');
 const spec={producer:expected.producer,sequence:expected.selectedSequence,base:ctx.base,hash:ctx.configHash};
 // Preserve exact provenance numbers by reading the current same-sequence
 // classification publication; derived timestamps are not used for identity.
 const code=String.raw`local j=require('luci.jsonc');local fs=require('nixio.fs');local n=require('nixio');local S=assert(j.parse([===[${JSON.stringify(spec)}]===]))
local function read(p,l)local f=assert(io.open(p));local x=f:read(l+1)or'';f:close();assert(#x<=l);return x end
local function now()return tonumber(read('/proc/uptime',128):match('^[%d.]+'))end
local function stable(p)local f=assert(n.open(p,'r'));local a=assert(f:stat());assert(a.type=='reg'and a.uid==0 and a.gid==0 and a.nlink==1);local parts={};local bytes=0;while true do local x=assert(f:read(math.min(65536,4194305-bytes)));if #x==0 then break end;bytes=bytes+#x;assert(bytes<=4194304);parts[#parts+1]=x end;local z=assert(f:stat());for _,k in ipairs({'dev','ino','type','uid','gid','modedec','size'})do assert(z[k]==a[k],'Held publication changed in place')end;assert(f:close());local b=assert(fs.lstat(p));if a.dev~=b.dev or a.ino~=b.ino then return nil end;assert(b.type=='reg'and b.uid==0 and b.gid==0 and b.nlink==1 and b.size==a.size);return assert(j.parse(table.concat(parts)))end
local function closed()for _,k in ipairs({'front_end_ipv4_stop','front_end_ipv6_stop'})do assert(tonumber(read('/sys/kernel/debug/ecm/'..k,128))==1)end;for _,k in ipairs({'ecm_db/connection_count','ecm_nss_ipv4/accelerated_count','ecm_nss_ipv6/accelerated_count','ecm_nss_ipv4/pending_accel_count','ecm_nss_ipv6/pending_accel_count','ecm_nss_ipv4/pending_decel_count','ecm_nss_ipv6/pending_decel_count'})do assert(tonumber(read('/sys/kernel/debug/ecm/'..k,128))==0)end end
closed();assert(not fs.lstat('/root/router-project/active-transaction'));assert(read('/root/router-project/game-classifier-generation',512)==S.base..' '..S.hash..'\n')
local C=assert(stable('/tmp/router-project-game-classifier/classification.json'),'Classification changed before join identity');assert(C.publication=='before-software-baseline'and C.producer==S.producer and C.snapshot.provenance.sequence==S.sequence);assert(C.configSha256==S.hash and C.status=='running'and C.dataHealthy and C.nssPermit==false and not C.error)
local P=C.snapshot.provenance;local E={producer=C.producer,sequence=P.sequence,queryStart=P.startedAtUptime,queryFinished=P.finishedAtUptime,published=C.atUptime};local started=now();local L=assert(loadstring([====[${library}]====]))();local result;local rows={}
local ok,err=xpcall(function()result=L.wait(E,function()closed();local F=stable('/tmp/router-project-game-classifier/snapshot.json');if not F then return nil end;assert(F.status=='running'and F.configSha256==S.hash and F.nssPermit==false and not F.error);assert(F.pid==C.pid and F.start==C.start and F.boot==C.boot and F.generation==C.generation);local p=assert(F.snapshot.provenance);assert(p.version==1 and p.method=='conntrack-cli'and p.rawStatus==0 and p.exitCode==0 and p.boot==C.boot);return{producer=F.producer,sequence=p.sequence,queryStart=p.startedAtUptime,queryFinished=p.finishedAtUptime,published=F.atUptime}end,now,function()n.nanosleep(0,50000000)end,started+4,function(row)rows[#rows+1]=row end)end,debug.traceback)
closed();print(j.stringify({passed=ok,error=not ok and tostring(err)or nil,startedAt=started,finishedAt=now(),join=result,rejectedRows=not ok and rows or nil,routerConfigurationWrites=false,nssAdmissionAllowed=false,originalAuditStillRequired=true}))`;
 const e=encode(ctx.base+'/group-runner 5 /bin/sh -c '+"'"+("/usr/bin/lua - <<'NSS54_JOIN_READONLY'\n"+code+"\nNSS54_JOIN_READONLY\n").replaceAll("'","'\\''")+"'");
 const raw=receipt(await c.run(e.command),e);fs.writeFileSync('work/nss57/'+label+'-join-raw-private.json',JSON.stringify(raw,null,2)+'\n',{flag:'wx'});assert.equal(raw.code,0,raw.stderr);
 const out=JSON.parse(raw.stdout);out.observedAt=new Date().toISOString();fs.writeFileSync('work/nss57/'+label+'-join-private.json',JSON.stringify(out,null,2)+'\n',{flag:'wx'});assert.equal(out.passed,true,out.error);return{classificationHint:hint,baselineJoin:out};
}
