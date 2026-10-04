// Project live filter reads to an empty journal in RAM. Every write callback rejects.
import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {verifyPreparation} from '../nss42/session-binding.mjs';import {connectRouter} from '../nss20/connect-router.mjs';import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
verifyPreparation();const root='work/nss45',d=JSON.parse(fs.readFileSync('work/nss39/deployment-latest.json')),cfg=JSON.parse(fs.readFileSync(d.localDir+'/config.json'));
const sha=s=>crypto.createHash('sha256').update(s).digest('hex'),old=fs.readFileSync(root+'/original-backend.lua','utf8'),candidate=fs.readFileSync(root+'/candidate-backend.lua','utf8'),tc=fs.readFileSync('work/nss39/tc-command.lua','utf8');
const start=old.indexOf('   local l=J.wans[tostring(w)];inspect(w)'),end=old.indexOf('\n   assert(r.ok',start);assert.ok(start>0&&end>start);
const patchOld=old.slice(start,end),candidateStart=candidate.indexOf('   local l=J.wans[tostring(w)];local initial=inspect(w)'),candidateEnd=candidate.indexOf('\n   assert(r.ok',candidateStart),patchNew=candidate.slice(candidateStart,candidateEnd);
assert.equal(old.slice(0,start)+patchNew+old.slice(end),candidate);
const lua=String.raw`local j=require('luci.jsonc');local n=require('nixio')
local function read(p,cap)local f=assert(io.open(p));local s=f:read(cap+1)or'';f:close();assert(#s<=cap);return s end
local function now()return tonumber(read('/proc/uptime',128):match('^[%d.]+'))end
local tc=assert(loadstring([=======[${tc}]=======]))()
local cfg=assert(j.parse(read('${d.base}/config.json',131072)));local own=assert(dofile('${d.base}/owned.lua'))
local source=read('${d.base}/backend.lua',65536);local a=[=======[${patchOld}]=======];local b=[=======[${patchNew}]=======]
local x,y=source:find(a,1,true);assert(x and not source:find(a,y+1,true));local newSource=source:sub(1,x-1)..b..source:sub(y+1)
local method=assert(arg[1]);assert(method=='original'or method=='candidate');local B=assert(loadstring(method=='original'and source or newSource))()
local boot=read('/proc/sys/kernel/random/boot_id',128):gsub('%s+$','');local owner=cfg.generation..'_'..boot:gsub('%-','')
local calls=0;local function q(dev)
 calls=calls+1;local out=assert(j.parse(tc.run(n,now,{'-j','qdisc','show','dev',dev},65536)));local found
 for _,v in ipairs(out)do if v.kind=='cake'and v.root then assert(not found);found=v end end;return assert(found)
end
local function native(dev,h)
 calls=calls+1;local raw=tc.run(n,now,{'-d','filter','show','dev',dev,'parent',h},262144)
 return B.baseOnly(raw,dev,h,own)
end
local journal={version=23,generation=cfg.generation,boot=boot,wans={},entries={},seq=0}
for w=1,5 do
 local l={version=1,transactionId=owner,boot=boot,wan=w,deadline=1,current={},intents={},nativeBaseline={}}
 for _,dev in ipairs({'rpwan'..w,'rpifb'..w})do l.current[dev]={};l.nativeBaseline[dev]=native(dev,cfg.queues[dev].handle)end
 journal.wans[tostring(w)]=l
end
local saveCalls=0;local R={boot=function()return boot end,queue=q,native=native,loadJournal=function()return journal end,saveJournal=function(v)assert(v==journal);saveCalls=saveCalls+1 end,
 checkFresh=function()error('No reconcile in readonly benchmark')end,batch=function()error('Readonly benchmark refuses every write')end}
local backend=B.new(cfg,R,own);calls=0;local begin=now();local tx=tonumber(read('/sys/class/net/lan4/statistics/tx_bytes',64));local cpu=os.clock()
local result=backend.recover();local elapsed=now()-begin;local background=(tonumber(read('/sys/class/net/lan4/statistics/tx_bytes',64))-tx)*8/elapsed/1000000
assert(result.exactRecovery and calls==(method=='original'and 60 or 40)and saveCalls==1)
print(j.stringify({passed=true,method=method,seconds=elapsed,observerCpuSeconds=os.clock()-cpu,readonlyCalls=calls,saveCallsInRam=saveCalls,backgroundLan4Mbps=background,projectedEmptyJournal=true,nativeSelectorsRecovered=false,routerWrites=false,ecmOpened=false,candidateSource=newSource}))`;
const capsules=Object.fromEntries(['original','candidate'].map(method=>{const body=d.base+"/group-runner 6 /usr/bin/lua - "+method+" <<'NSS45_RECOVERY_READS'\n"+lua+'\nNSS45_RECOVERY_READS\n';const e=encode(body);assert.ok(e.execBytes<=9000);return[method,e]}));
if(process.argv.includes('--prepare-only')){console.log(JSON.stringify({execBytes:Math.max(...Object.values(capsules).map(e=>e.execBytes)),readonly:true}));process.exit(0)}
const c=await connectRouter();try{
 const h=await c.run('/usr/bin/sha256sum '+d.base+'/config.json '+d.base+'/backend.lua '+d.base+'/owned.lua '+d.base+'/group-runner');assert.equal(h.code,0);const digests=h.stdout.trim().split('\n').map(s=>s.split(/\s/)[0]);assert.deepEqual(digests,[d.configHash,cfg.files['backend.lua'],cfg.files['owned.lua'],cfg.files['group-runner']]);
 const rows=[];for(let pair=1;pair<=3;pair++)for(const method of pair%2?['original','candidate']:['candidate','original']){
  const e=capsules[method],r=receipt(await c.run(e.command),e);fs.writeFileSync(root+'/recovery-readonly-'+pair+'-'+method+'-raw-private.json',JSON.stringify(r,null,2)+'\n');assert.equal(r.code,0,r.stderr);const data=JSON.parse(r.stdout);assert.equal(sha(data.candidateSource),sha(candidate));delete data.candidateSource;rows.push({pair,...data});
 }
 const means=Object.fromEntries(['original','candidate'].map(m=>[m,rows.filter(r=>r.method===m).reduce((s,r)=>s+r.seconds,0)/3]));
 const out={passed:true,observedAt:new Date().toISOString(),pairs:3,rows,meanSeconds:means,oldSha256:sha(old),candidateSha256:sha(candidate),tcHelperSha256:sha(tc),routerWrites:false,installed:false,projectedEmptyJournalOnly:true,actualSelectorRecoveryProved:false,highLoadRecoveryQualified:false,scope:'Live bounded root/filter reads and exact old/new pure recovery in RAM with empty projected dynamic state; write callback always rejects. Not service recovery or NSS CPU A/B.'};
 fs.writeFileSync(root+'/recovery-readonly-qualified.json',JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify({...out,rows:rows.map(({...r})=>r)}));
}finally{c.close()}
