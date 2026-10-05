import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';import{spawnSync}from'node:child_process';
import {verifyDeployment,deploymentPath} from '../nss68/deployment-binding.mjs';
import {connectRouter}from'../nss20/connect-router.mjs';import{encode,receipt}from'../nss11/v7-observe-repair/observe2/transport.mjs';
const script=String.raw`$ErrorActionPreference='Stop'
$processes=@(Get-Process -Name cs2,steam -ErrorAction SilentlyContinue)
$pids=@($processes | ForEach-Object {$_.Id})
$udp=@(Get-NetUDPEndpoint -ErrorAction Stop | Where-Object {$_.OwningProcess -in $pids} | Select-Object LocalAddress,LocalPort,OwningProcess)
$tcp=@(Get-NetTCPConnection -State Established -ErrorAction Stop | Where-Object {$_.OwningProcess -in $pids} | Select-Object LocalAddress,LocalPort,RemoteAddress,RemotePort,OwningProcess)
@{at=(Get-Date).ToUniversalTime().ToString('o');processes=@($processes|ForEach-Object {@{name=$_.ProcessName;pid=$_.Id;start=$_.StartTime.ToUniversalTime().ToString('o')}});udp=$udp;tcp=$tcp}|ConvertTo-Json -Depth 5 -Compress`;
const p=spawnSync('powershell.exe',['-NoProfile','-NonInteractive','-Command',script],{encoding:'utf8',windowsHide:true,timeout:15000});assert.equal(p.status,0,p.stderr);const pc=JSON.parse(p.stdout);fs.writeFileSync('work/nss71/pc-app-endpoints-private.json',JSON.stringify(pc,null,2)+'\n');
const ctxPath=process.argv[2]??deploymentPath;assert.equal(ctxPath,deploymentPath);
const {deployment:ctx,config:cfg}=verifyDeployment();
const adapter=fs.readFileSync('work/nss49/classifier.lua','utf8').split('\n').filter(x=>!x.trimStart().startsWith('--')).join('\n');
const plan={base:ctx.base,configSha256:ctx.configHash,workerSha256:cfg.files['worker.lua']};
const code=String.raw`local fs=require('nixio.fs');local j=require('luci.jsonc');local function read(p,l)local h=assert(io.open(p));local s=h:read(l+1);h:close();assert(#s<=l);return s end;local function now()return tonumber(read('/proc/uptime',128):match('^[%d.]+'))end
local function run(s)assert(s:match('^/usr/bin/sha256sum /root/router%-project/classifier/nss23%-[%w%-]+/config.json$'));local h=assert(io.popen(s));local b=h:read(256);h:close();return b end
local A=assert(loadstring([====[${adapter}]====]))();local P={boot=read('/proc/sys/kernel/random/boot_id',128):gsub('%s+$',''),classifierOwner=assert(j.parse([===[${JSON.stringify(plan)}]===])),selected={}}
local r={deadline=now()+10};local a=A.new(P,fs,j,read,now,run,r);local candidates=a.candidates();local flows={}
for _,f in ipairs(candidates.flows)do local i,d=f.identity,f.decision;if i.original.src=='192.168.237.207'and math.floor(i.mark/8192)%2==0 then
 if i.protocolNumber==17 and d.class=='RT'and d.budgetAdmitted or i.protocolNumber==6 and d.class=='BULK'then
  flows[#flows+1]={key=f.key,identity={protocolNumber=i.protocolNumber,connectionId=i.connectionId,zone=i.zone,wan=i.wan,mark=i.mark,original=i.original,reply=i.reply},decision={class=d.class,budgetAdmitted=d.budgetAdmitted,pps=d.pps,rateKbps=d.rateKbps}};assert(#flows<=128,'Candidate count exceeds bounded reader')
 end
end end
local result=assert(j.stringify({sourceSequence=candidates.sourceSequence,producer=candidates.producer,sourceAge=now()-candidates.startedAtUptime,flows=flows,nssAdmissionAllowed=false,routerWrites=false}));assert(#result<=65536,'Candidate output exceeds bounded reader');print(result)`;
const c=await connectRouter();try{const e=encode("/usr/bin/lua - <<'NSS27_REAL_CANDIDATES'\n"+code+"\nNSS27_REAL_CANDIDATES\n"),r=receipt(await c.run(e.command),e);fs.writeFileSync('work/nss71/real-candidates-raw-private.json',JSON.stringify(r,null,2)+'\n');assert.equal(r.code,0,r.stderr);const native=JSON.parse(r.stdout);assert.ok(Date.now()-Date.parse(pc.at)<12000,'PC endpoint observation became stale');
const ids=new Map(pc.processes.map(p=>[p.pid,p.name]));const addressMatches=(e,f)=>['0.0.0.0','::',f.identity.original.src].includes(e.LocalAddress);
const game=native.flows.filter(f=>f.identity.protocolNumber===17&&f.decision.class==='RT'&&f.decision.budgetAdmitted&&pc.udp.some(e=>ids.get(e.OwningProcess)==='cs2'&&addressMatches(e,f)&&e.LocalPort===f.identity.original.sport));
const bulk=native.flows.filter(f=>f.identity.protocolNumber===6&&f.decision.class==='BULK'&&pc.tcp.some(e=>ids.get(e.OwningProcess)==='steam'&&addressMatches(e,f)&&e.LocalPort===f.identity.original.sport&&e.RemoteAddress===f.identity.original.dst&&e.RemotePort===f.identity.original.dport));
const {flows,...meta}=native;const out={...meta,game,bulk,pcObservedAt:pc.at,applicationMatching:'local exact socket ownership',execBytes:e.execBytes};fs.writeFileSync('work/nss71/real-candidates-private.json',JSON.stringify(out,null,2)+'\n');const wans=[...new Set(out.game.flatMap(g=>out.bulk.filter(b=>b.identity.wan===g.identity.wan).map(()=>g.identity.wan)))];
const result={observedAt:new Date().toISOString(),readonly:true,gameProcessRunning:pc.processes.some(p=>p.name==='cs2'),steamProcessRunning:pc.processes.some(p=>p.name==='steam'),actualCs2RtCandidates:out.game.length,actualSteamBulkCandidates:out.bulk.length,sameWanCandidates:wans,sourceAge:out.sourceAge,sourceSequence:out.sourceSequence,nssAdmissionAllowed:false,controllerPrototypeOnly:true,adapterSha256:crypto.createHash('sha256').update(fs.readFileSync('work/nss49/classifier.lua')).digest('hex')};fs.writeFileSync('work/nss71/real-reader-qualified.json',JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));}finally{c.close()}
