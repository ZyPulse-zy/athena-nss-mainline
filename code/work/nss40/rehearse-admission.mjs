// Complete current ready()/pair()/inspect()/scan() paths. Uncalled methods omitted
// to stay within the existing SSH transport cap; no decision or check is removed.
import fs from 'node:fs';import assert from 'node:assert/strict';
import {connectRouter} from '../nss20/connect-router.mjs';
import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
import {verifyPreparation} from './session-binding.mjs';
import {verifyCurrentClassifier} from '../nss39/binding.mjs';
import {selectRealPair} from '../nss39/pair-policy.mjs';
import {canonicalSelection} from '../nss27/flow-selection.mjs';
verifyPreparation();const {deployment:d,config:cfg}=verifyCurrentClassifier();
const root='work/nss40',candidates=JSON.parse(fs.readFileSync(root+'/real-candidates-private.json'));
assert.ok(Date.now()-Date.parse(candidates.pcObservedAt)<15000);
const pair=selectRealPair(candidates);assert.ok(pair.length,'No same-WAN actual application pair');
const selected={tcp:canonicalSelection(pair[0].b),udp:canonicalSelection(pair[0].g)};
for(const slot of ['tcp','udp']){const f=selected[slot];f.classifierKey=[f.wan,f.mark,slot,f.original.src,f.original.sport,f.reply.src,f.reply.dst,f.reply.sport,f.reply.dport,f.zone,f.id].join('|');}
const source=name=>{
 let body=fs.readFileSync('work/nss39/'+name+'.lua','utf8');
 const between=(a,b)=>{const x=body.indexOf(a),y=body.indexOf(b,x);assert.ok(x>0&&y>x);body=body.slice(0,x)+body.slice(y);};
 if(name==='classifier'){
  between('function M.compareEpoch(','return M\n\nend)()');
  between(' function out.candidates()',' function out.ready()');
  between(' function out.sample()',' return out\nend');
  between('local activeInstance','function A.new(');
  const tail=body.indexOf('return setmetatable(A,');assert.ok(tail>0);body=body.slice(0,tail)+'return A\n';
 }else{const tail=body.indexOf('function M.waitFresh(');assert.ok(tail>0);body=body.slice(0,tail)+'return M\n';}
 return body.split('\n').filter(l=>!l.trimStart().startsWith('--')).join('\n');
};
const plan={selected,classifierOwner:{base:d.base,configSha256:d.configHash,workerSha256:cfg.files['worker.lua']}};
const code=String.raw`local j=require('luci.jsonc');local fs=require('nixio.fs');local n=require('nixio')
local function read(p,l)local f=assert(io.open(p));local s=f:read(l+1)or'';f:close();assert(#s<=l);return s end
local function now()return tonumber(read('/proc/uptime',128):match('^[%d.]+'))end
local function run(s)assert(s:match('^/usr/bin/sha256sum /root/router%-project/classifier/nss23%-[%w%-]+/config.json$'));local f=assert(io.popen(s));local s=f:read(256);f:close();return s end
local A=assert(loadstring([====[${source('classifier')}]====]))();local Phase=assert(loadstring([====[${source('core-guard-phase')}]====]))()
local P=assert(j.parse([===[${JSON.stringify(plan)}]===]));P.boot=read('/proc/sys/kernel/random/boot_id',128):gsub('%s+$','')
local function closed()for _,k in ipairs({'front_end_ipv4_stop','front_end_ipv6_stop'})do assert(tonumber(read('/sys/kernel/debug/ecm/'..k,128))==1)end;for _,k in ipairs({'ecm_db/connection_count','ecm_nss_ipv4/accelerated_count','ecm_nss_ipv6/accelerated_count','ecm_nss_ipv4/pending_accel_count','ecm_nss_ipv6/pending_accel_count','ecm_nss_ipv4/pending_decel_count','ecm_nss_ipv6/pending_decel_count'})do assert(tonumber(read('/sys/kernel/debug/ecm/'..k,128))==0)end end
local function telemetry()return{uptime=now(),cpu=read('/proc/stat',16384):match('^[^\n]+'),softnet=read('/proc/net/softnet_stat',16384),txBytes=tonumber(read('/sys/class/net/lan4/statistics/tx_bytes',128)),txPackets=tonumber(read('/sys/class/net/lan4/statistics/tx_packets',128))}end
local record={deadline=now()+30};local a=A.new(P,fs,j,read,now,run,record);local initial=Phase.scan(fs,read);local expected={pid=initial.guard.pid,start=initial.guard.start};local rows={};local t={telemetry()};local due=now()+9;local observer=os.clock()
repeat
 local start=now();closed();local phaseStart=now();local p=Phase.scan(fs,read,expected);local phaseEnd=now();local ready,reason,retryable=a.ready();local done=now()
 rows[#rows+1]={at=done,ready=ready,reason=reason,retryable=retryable,iterationSeconds=done-start,phaseSeconds=phaseEnd-phaseStart,adapter=record.lastAdmissionProbe,fullInventory=p.fullInventory==true,refreshInventory=p.refreshInventory==true};record.lastAdmissionProbe=nil
 if not ready and not retryable then break end;n.nanosleep(0,20000000)
until now()>=due
closed();t[2]=telemetry();print(j.stringify({readonly=true,routerWrites=false,nssOpened=false,trafficGenerated=false,rows=rows,telemetry=t,observerCpuSeconds=os.clock()-observer,completeReadinessAndPhaseScanFunctions=true,unreachableMethodsOmitted=true,initialAgeLimitSeconds=1,prelearningAgeLimitSeconds=2}))`;
const stamp=new Date().toISOString().replace(/\D/g,'').slice(0,14),path=root+'/admission-'+stamp;
fs.writeFileSync(path+'-selected-private.json',JSON.stringify(selected,null,2)+'\n');
const e=encode("/usr/bin/lua - <<'NSS40_READONLY_ADMISSION'\n"+code+"\nNSS40_READONLY_ADMISSION\n");
const c=await connectRouter();try{const r=receipt(await c.run(e.command),e);fs.writeFileSync(path+'-raw-private.json',JSON.stringify(r,null,2)+'\n');assert.equal(r.code,0,r.stderr);const out=JSON.parse(r.stdout);out.observedAt=new Date().toISOString();out.execBytes=e.execBytes;out.selectedWan=selected.tcp.wan;fs.writeFileSync(path+'-private.json',JSON.stringify(out,null,2)+'\n');
const reasons={};for(const row of out.rows)if(!row.ready){const reason=row.reason.replace(/^\[string .*?\]:\d+: /,'');reasons[reason]=(reasons[reason]??0)+1;}
const summary={path,observedAt:out.observedAt,samples:out.rows.length,ready:out.rows.filter(r=>r.ready).length,reasons,wan:out.selectedWan,routerWrites:false,execBytes:e.execBytes,observerCpuSeconds:out.observerCpuSeconds,completeReadinessAndPhaseScanFunctions:true,unreachableMethodsOmitted:true,adapterMaxSeconds:Math.max(...out.rows.map(r=>r.adapter.checkSeconds)),phaseMaxSeconds:Math.max(...out.rows.map(r=>r.phaseSeconds)),sourceAgeMinSeconds:Math.min(...out.rows.map(r=>r.adapter.sourceAge))};
fs.writeFileSync(root+'/rehearsal-summary.json',JSON.stringify(summary,null,2)+'\n');console.log(JSON.stringify(summary));}finally{c.close()}
