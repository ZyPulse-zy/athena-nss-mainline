import fs from'node:fs';import assert from'node:assert/strict';import{spawnSync}from'node:child_process';
import{connectRouter}from'../nss20/connect-router.mjs';import{encode,receipt}from'../nss11/v7-observe-repair/observe2/transport.mjs';import{selectRealPair}from'./pair-policy.mjs';import{canonicalSelection}from'../nss27/flow-selection.mjs';
const child=spawnSync(process.execPath,['work/nss33/read-real-candidates.mjs'],{encoding:'utf8',windowsHide:true,timeout:20000});assert.equal(child.status,0,child.stderr);
const candidates=JSON.parse(fs.readFileSync('work/nss33/real-candidates-private.json')),pairs=selectRealPair(candidates);assert.ok(pairs.length,'No actual application pair for read-only rehearsal');
const selected={tcp:canonicalSelection(pairs[0].b),udp:canonicalSelection(pairs[0].g)};for(const slot of['tcp','udp']){const f=selected[slot];f.classifierKey=[f.wan,f.mark,slot,f.original.src,f.original.sport,f.reply.src,f.reply.dst,f.reply.sport,f.reply.dport,f.zone,f.id].join('|')}
const d=JSON.parse(fs.readFileSync('work/nss33/deployment-latest.json')),cfg=JSON.parse(fs.readFileSync(d.localDir+'/config.json'));
const adapter=fs.readFileSync('work/nss33/classifier.lua','utf8').split('\n').filter(l=>!l.trimStart().startsWith('--')).join('\n');
const plan={selected,classifierOwner:{base:d.base,configSha256:d.configHash,workerSha256:cfg.files['worker.lua']}};
const code=String.raw`local realj=require('luci.jsonc');local fs=require('nixio.fs');local n=require('nixio');local lastRaw,last
local function read(p,l)local f=assert(io.open(p));local s=f:read(l+1);f:close();assert(#s<=l);if p=='/tmp/router-project-game-classifier/classification.json'then lastRaw=s end;return s end
local function now()return tonumber(read('/proc/uptime',128):match('^[%d.]+'))end
local j={parse=function(raw)local v=realj.parse(raw);if raw==lastRaw then last=v end;return v end,stringify=realj.stringify}
local function run(s)assert(s:match('^/usr/bin/sha256sum /root/router%-project/classifier/nss23%-[%w%-]+/config.json$'));local f=assert(io.popen(s));local b=f:read(256);f:close();return b end
local A=assert(loadstring([====[${adapter}]====]))();local P=assert(j.parse([===[${JSON.stringify(plan)}]===]));P.boot=read('/proc/sys/kernel/random/boot_id',128):gsub('%s+$','')
local a=A.new(P,fs,j,read,now,run,{deadline=now()+30});local rows={};local due=now()+18
while now()<due do
 local began=now();local ready,reason=a.ready();local t=now();local p=last and last.snapshot and last.snapshot.provenance
 local row={at=t,ready=ready,reason=reason,readSeconds=t-began,sequence=p and p.sequence,sourceAge=p and t-p.startedAtUptime,publicationDelay=p and last.atUptime-p.startedAtUptime,querySeconds=p and p.finishedAtUptime-p.startedAtUptime,bytes=lastRaw and #lastRaw,selected={}}
 for _,slot in ipairs({'tcp','udp'})do local found;for _,f in ipairs(last and last.snapshot and last.snapshot.flows or{})do if f.key==P.selected[slot].classifierKey then found=f end end;row.selected[slot]={present=found~=nil,class=found and found.decision.class,admitted=found and found.decision.budgetAdmitted}end
 rows[#rows+1]=row;n.nanosleep(0,200000000)
end
print(realj.stringify({readonly=true,routerWrites=false,nssOpened=false,rows=rows}))`;
const c=await connectRouter();try{const e=encode("/usr/bin/lua - <<'NSS33_READONLY_REHEARSAL'\n"+code+"\nNSS33_READONLY_REHEARSAL\n");const r=receipt(await c.run(e.command),e);assert.equal(r.code,0,r.stderr);const out=JSON.parse(r.stdout);out.selected=selected;out.observedAt=new Date().toISOString();const p='work/nss33/admission-rehearsal-'+out.observedAt.replace(/\D/g,'').slice(0,14)+'-private.json';fs.writeFileSync(p,JSON.stringify(out,null,2)+'\n');const reasons={};for(const r of out.rows)if(!r.ready)reasons[r.reason]=(reasons[r.reason]??0)+1;console.log(JSON.stringify({path:p,samples:out.rows.length,ready:out.rows.filter(r=>r.ready).length,reasons,ageMin:Math.min(...out.rows.map(r=>r.sourceAge)),readMax:Math.max(...out.rows.map(r=>r.readSeconds)),publicationDelayMin:Math.min(...out.rows.map(r=>r.publicationDelay)),publicationDelayMax:Math.max(...out.rows.map(r=>r.publicationDelay)),selectedTcpPresent:out.rows.filter(r=>r.selected.tcp.present).length,selectedGamePresent:out.rows.filter(r=>r.selected.udp.present).length,routerWrites:false}));}finally{c.close()}
