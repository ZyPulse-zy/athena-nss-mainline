import fs from'node:fs';import assert from'node:assert/strict';import{connectRouter}from'../nss20/connect-router.mjs';import{encode,receipt}from'../nss11/v7-observe-repair/observe2/transport.mjs';
const label=process.argv[2]??'trial';assert.match(label,/^[a-z0-9-]+$/);const out='work/nss40/'+label+'-observation.json';assert.ok(!fs.existsSync(out));
const lua=String.raw`local j=require('luci.jsonc');local n=require('nixio')
local function read(p,l)local f=io.open(p);if not f then return nil end;local s=f:read(l+1)or'';f:close();assert(#s<=l);return s end
local function now()return tonumber(read('/proc/uptime',128):match('^[%d.]+'))end
local rows={};local done=false;local semantic
local function same(a,b)if type(a)~=type(b)then return false end;if type(a)~='table'then return a==b end;for k,v in pairs(a)do if not same(v,b[k])then return false end end;for k in pairs(b)do if a[k]==nil then return false end end;return true end
for i=1,35 do
 local start=now();local raw=read('/tmp/router-project-game-classifier/classification.json',4194304);local s=assert(j.parse(raw));local parsed=now();local g=assert(j.parse(read('/tmp/router-project-game-classifier/guardian.json',8192)));local p=s.snapshot and s.snapshot.provenance
 local o={uptime=start,status=s.status,pid=s.pid,producer=s.producer,bytes=#raw,parseSeconds=parsed-start,sequence=p and p.sequence,age=p and parsed-p.startedAtUptime,publishDelay=p and s.atUptime-p.startedAtUptime,projection=s.snapshot and s.snapshot.admissionProjection,guardianHealthy=g.healthy,accel=tonumber(read('/sys/kernel/debug/ecm/ecm_nss_ipv4/accelerated_count',64)),frontend=tonumber(read('/sys/kernel/debug/ecm/front_end_ipv4_stop',64)),cpu=read('/proc/stat',65536):match('^cpu [^\n]+'),softnet=read('/proc/net/softnet_stat',8192),txBytes=tonumber(read('/sys/class/net/lan4/statistics/tx_bytes',64)),txPackets=tonumber(read('/sys/class/net/lan4/statistics/tx_packets',64))}
 if p and not done then
  local primary=read('/tmp/router-project-game-classifier/snapshot.json',4194304)
  local seq=primary and tonumber(primary:match('"sequence"%s*:%s*(%d+)'))
  if seq==p.sequence then
   local f=assert(j.parse(primary));if f.producer==s.producer and f.snapshot.provenance.sequence==p.sequence then
    assert(same(f.snapshot.provenance,p));local expected={};for _,flow in ipairs(f.snapshot.flows)do if flow.leaf.candidate then expected[flow.key]=flow end end
    local count=0;for _,flow in ipairs(s.snapshot.flows)do local e=assert(expected[flow.key]);assert(same(e.identity,flow.identity)and same(e.decision,flow.decision)and same(e.leaf,flow.leaf));assert(e.validUntilUptime==flow.validUntilUptime);expected[flow.key]=nil;count=count+1 end
    assert(next(expected)==nil and s.snapshot.admissionProjection.completeInputFlowCount==#f.snapshot.flows)
    semantic={passed=true,sequence=p.sequence,fullFlows=#f.snapshot.flows,fullBytes=#primary,candidateFlows=count,candidateBytes=#raw,fullSnapshotRetained=true,identityDecisionLeafAndExpiryEqual=true,softwareVerifiedRt=0}
    for _,flow in ipairs(f.snapshot.flows)do if flow.decision.class=='RT'and flow.decision.budgetAdmitted and flow.applied and flow.applied.verified then semantic.softwareVerifiedRt=semantic.softwareVerifiedRt+1 end end;done=true
   end
  end
 end
 rows[#rows+1]=o;n.nanosleep(0,500000000)
end
print(j.stringify({readonly=true,rows=rows,semantic=semantic,nssEnabled=false}))`;
const c=await connectRouter();try{const e=encode("/usr/bin/lua - <<'NSS33_COMPACT_OBSERVE'\n"+lua+"\nNSS33_COMPACT_OBSERVE\n");const r=receipt(await c.run(e.command),e);assert.equal(r.code,0,r.stderr);const d=JSON.parse(r.stdout);fs.writeFileSync(out,JSON.stringify(d,null,2)+'\n');const a=d.rows[0],b=d.rows.at(-1);console.log(JSON.stringify({out,samples:d.rows.length,semantic:d.semantic,mbps:(b.txBytes-a.txBytes)*8/(b.uptime-a.uptime)/1e6,ageMin:Math.min(...d.rows.map(s=>s.age??Infinity)),ageMax:Math.max(...d.rows.map(s=>s.age??0)),parseMax:Math.max(...d.rows.map(s=>s.parseSeconds)),underOneSecond:d.rows.filter(s=>s.age<1).length,allHealthy:d.rows.every(s=>s.status==='running'&&s.guardianHealthy&&s.accel===0&&s.frontend===1)}));}finally{c.close()}
