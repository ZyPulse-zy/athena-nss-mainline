// Read-only timing and load diagnostic; no gate, qdisc, or traffic generation.
import fs from 'node:fs';import assert from 'node:assert/strict';
import {connectRouter} from '../nss20/connect-router.mjs';
import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
import {verifyPreparation} from './qualification.mjs';
import {verifyCurrentClassifier} from './binding.mjs';
const root='work/nss36',trial='real-matched-aba-20261003091409-28454bad';
verifyPreparation();const {deployment:d,config:cfg}=verifyCurrentClassifier();
const selected=JSON.parse(fs.readFileSync(root+'/'+trial+'/selected-private.json'));
for(const slot of ['tcp','udp']){const f=selected[slot];f.classifierKey=[f.wan,f.mark,slot,f.original.src,f.original.sport,f.reply.src,f.reply.dst,f.reply.sport,f.reply.dport,f.zone,f.id].join('|');}
const adapter=fs.readFileSync(root+'/classifier.lua','utf8').split('\n').filter(l=>!l.trimStart().startsWith('--')).join('\n');
const plan={selected,classifierOwner:{base:d.base,configSha256:d.configHash,workerSha256:cfg.files['worker.lua']}};
const code=String.raw`local realj=require('luci.jsonc');local fs=require('nixio.fs');local n=require('nixio');local lastRaw,last
local function read(p,l)local f=assert(io.open(p));local s=f:read(l+1);f:close();assert(#s<=l);if p=='/tmp/router-project-game-classifier/classification.json'then lastRaw=s end;return s end
local function now()return tonumber(read('/proc/uptime',128):match('^[%d.]+'))end
local j={parse=function(raw)local v=realj.parse(raw);if raw==lastRaw then last=v end;return v end,stringify=realj.stringify}
local function run(s)assert(s:match('^/usr/bin/sha256sum /root/router%-project/classifier/nss23%-[%w%-]+/config.json$'));local f=assert(io.popen(s));local b=f:read(256);f:close();return b end
local A=assert(loadstring([====[${adapter}]====]))();local P=assert(j.parse([===[${JSON.stringify(plan)}]===]));P.boot=read('/proc/sys/kernel/random/boot_id',128):gsub('%s+$','')
local a=A.new(P,fs,j,read,now,run,{deadline=now()+30});local rows={};local due=now()+18
local function telemetry()return {uptime=now(),cpu=read('/proc/stat',16384):match('^[^\n]+'),softnet=read('/proc/net/softnet_stat',16384),txBytes=tonumber(read('/sys/class/net/lan4/statistics/tx_bytes',128)),txPackets=tonumber(read('/sys/class/net/lan4/statistics/tx_packets',128)),stop4=tonumber(read('/sys/kernel/debug/ecm/front_end_ipv4_stop',128)),accel=tonumber(read('/sys/kernel/debug/ecm/ecm_nss_ipv4/accelerated_count',128))}end
local samples={telemetry()}
while now()<due do
 local began=now();local ready,reason,retryable=a.ready();local t=now();local p=last and last.snapshot and last.snapshot.provenance
 local row={at=t,ready=ready,reason=reason,retryable=retryable,readSeconds=t-began,sequence=p and p.sequence,sourceAge=p and t-p.startedAtUptime,publicationDelay=p and last.atUptime-p.startedAtUptime,querySeconds=p and p.finishedAtUptime-p.startedAtUptime,bytes=lastRaw and #lastRaw,status=last and last.status,selected={}}
 for _,slot in ipairs({'tcp','udp'})do local found;for _,f in ipairs(last and last.snapshot and last.snapshot.flows or{})do if f.key==P.selected[slot].classifierKey then found=f end end;row.selected[slot]={present=found~=nil,class=found and found.decision.class,admitted=found and found.decision.budgetAdmitted}end
 rows[#rows+1]=row;n.nanosleep(0,200000000)
end
samples[2]=telemetry();print(realj.stringify({readonly=true,routerWrites=false,nssOpened=false,rows=rows,telemetry=samples}))`;
const c=await connectRouter();try{
 const e=encode("/usr/bin/lua - <<'NSS36_READONLY_REHEARSAL'\n"+code+"\nNSS36_READONLY_REHEARSAL\n");
 const r=receipt(await c.run(e.command),e);assert.equal(r.code,0,r.stderr);const out=JSON.parse(r.stdout);out.observedAt=new Date().toISOString();out.historicalPairIdentityRechecked=true;out.currentApplicationOwnershipRechecked=false;
 const path=root+'/admission-rehearsal-'+out.observedAt.replace(/\D/g,'').slice(0,14)+'-private.json';fs.writeFileSync(path,JSON.stringify(out,null,2)+'\n');
 const reasons={};for(const row of out.rows)if(!row.ready)reasons[row.reason]=(reasons[row.reason]??0)+1;
 const summary={path,samples:out.rows.length,ready:out.rows.filter(r=>r.ready).length,reasons,ageMin:Math.min(...out.rows.map(r=>r.sourceAge)),readMax:Math.max(...out.rows.map(r=>r.readSeconds)),publicationDelayMin:Math.min(...out.rows.map(r=>r.publicationDelay)),publicationDelayMax:Math.max(...out.rows.map(r=>r.publicationDelay)),selectedTcpPresent:out.rows.filter(r=>r.selected.tcp.present).length,selectedGamePresent:out.rows.filter(r=>r.selected.udp.present).length,routerWrites:false,execBytes:e.execBytes};
 fs.writeFileSync(root+'/rehearsal-summary.json',JSON.stringify(summary,null,2)+'\n');console.log(JSON.stringify(summary));
}finally{c.close()}
