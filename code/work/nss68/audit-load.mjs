// Read-only original locked audit with traffic counters bracketing its execution.
// All original assertions, deadlines and source bindings remain in the renderer.
import fs from 'node:fs';import assert from 'node:assert/strict';
import {connectRouter} from '../nss27/connect-router.mjs';
import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
import {render} from '../nss49/audit-renderer.mjs';
import {verifyPreparation} from './session-binding.mjs';
verifyPreparation();
const label=process.argv[2];assert.match(label,/^[a-z0-9-]+$/);
const trial=label.startsWith('trial-');
const ctx=JSON.parse(fs.readFileSync('work/nss68/deployment-latest.json'));assert.equal(ctx.committed,true);
let source=render(fs.readFileSync('work/nss23/operational-audit.lua','utf8'));
const trace="local function trace(name)diagnostic.events[#diagnostic.events+1]={name=name,at=clock()}end";
assert.equal(source.split(trace).length,2);
source=source.replace(trace,String.raw`local function capture()
 local function read(p,l)local f=assert(io.open(p));local s=f:read(l+1)or'';f:close();assert(#s<=l);return s end
 for _,k in ipairs({'front_end_ipv4_stop','front_end_ipv6_stop'})do assert(tonumber(read('/sys/kernel/debug/ecm/'..k,128))==1)end
 for _,k in ipairs({'ecm_db/connection_count','ecm_nss_ipv4/accelerated_count','ecm_nss_ipv6/accelerated_count','ecm_nss_ipv4/pending_accel_count','ecm_nss_ipv6/pending_accel_count','ecm_nss_ipv4/pending_decel_count','ecm_nss_ipv6/pending_decel_count'})do assert(tonumber(read('/sys/kernel/debug/ecm/'..k,128))==0)end
 return{at=clock(),cpu=read('/proc/stat',16384):match('^[^\n]+'),softnet=read('/proc/net/softnet_stat',16384),txBytes=tonumber(read('/sys/class/net/lan4/statistics/tx_bytes',128)),txPackets=tonumber(read('/sys/class/net/lan4/statistics/tx_packets',128))}
end
local function trace(name)
 diagnostic.events[#diagnostic.events+1]={name=name,at=clock()}
 if name=='locked-audit-start'then diagnostic.loadFirst=capture()end
 if name=='locked-audit-end'then diagnostic.loadLast=capture()end
end`);
const body='exec 8>/tmp/router-project-transaction.lock\nflock -x 8\n/usr/bin/lua - '+ctx.base+' '+ctx.configHash+" <<'NSS68_LOAD_AUDIT'\n"+source+'\nNSS68_LOAD_AUDIT\n';
const e=encode(ctx.base+'/group-runner 6 /bin/sh -c '+"'"+body.replaceAll("'","'\\''")+"'");
const c=await connectRouter();try{
 const raw=receipt(await c.run(e.command),e);
 fs.writeFileSync('work/nss68/'+label+'-load-audit-raw-private.json',JSON.stringify(raw,null,2)+'\n',{flag:'wx'});
 assert.equal(raw.code,0,raw.stderr);
 const r=JSON.parse(raw.stdout);
 fs.writeFileSync('work/nss68/'+label+'-load-audit-private.json',JSON.stringify(r,null,2)+'\n',{flag:'wx'});
 assert.ok(r.originalAssertionsRetained);
 const a=r.diagnostic.loadFirst,b=r.diagnostic.loadLast,dt=b.at-a.at;assert.ok(dt>0);
 const cpu=s=>s.trim().split(/\s+/).slice(1,9).map(Number),x=cpu(a.cpu),y=cpu(b.cpu),d=y.map((v,i)=>v-x[i]),total=d.reduce((s,v)=>s+v,0);
 const squeeze=s=>s.trim().split('\n').reduce((v,row)=>v+parseInt(row.trim().split(/\s+/)[2],16),0);
 const out={passed:r.passed,observedAt:new Date().toISOString(),readonly:true,originalFullLockedAudit:true,allOriginalAssertionsRetained:true,
  queryAge:r.result?.queryAge,sequence:r.result?.querySequence,originalDeadlinesUnchanged:true,
  seconds:dt,lan4Mbps:(b.txBytes-a.txBytes)*8/dt/1e6,pps:(b.txPackets-a.txPackets)/dt,
  busyPercent:100*(total-d[3]-d[4])/total,softirqPercent:100*d[6]/total,timeSqueezeDelta:squeeze(b.softnet)-squeeze(a.softnet),
  measurementCoversActualAudit:true,auditObserverCostIncluded:true,ecmStoppedAndZeroAtBothBoundaries:true,nssAdmissionAllowed:false};
 fs.writeFileSync('work/nss68/'+label+'-load-audit-sanitized.json',JSON.stringify(out,null,2)+'\n',{flag:'wx'});
 console.log(JSON.stringify(out));assert.equal(r.passed,true,r.error);
}finally{c.close()}
