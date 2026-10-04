// Read-only RAM replay of the exact deployed observation pipeline.
// Never writes production files, publishes classification, or enables NSS.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {connectRouter} from '../nss20/connect-router.mjs';
import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
const root='work/nss47', label=process.argv[2]??'profile';
assert.match(label,/^[a-z0-9-]+$/);
const out=root+'/'+label+'-private.json';assert.ok(!fs.existsSync(out));
const deployed=JSON.parse(fs.readFileSync('work/nss46/deployment-latest.json'));
const cfg=JSON.parse(fs.readFileSync(deployed.localDir+'/config.json'));
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const worker=fs.readFileSync('work/nss46/worker.lua','utf8');assert.equal(sha(worker),cfg.files['worker.lua']);
let source=fs.readFileSync('work/nss46/conntrack-source.lua','utf8');assert.equal(sha(source),cfg.files['conntrack-source.lua']);
let core=fs.readFileSync('work/nss29/classifier-core.lua','utf8');assert.equal(sha(core),cfg.files['classifier-core.lua']);
const backend=fs.readFileSync(deployed.localDir+'/backend.lua','utf8');assert.equal(sha(backend),cfg.files['backend.lua']);
const original={worker:sha(worker),source:sha(source),core:sha(core),backend:sha(backend)};
const once=(s,a,b)=>{assert.equal(s.split(a).length,2,a);return s.replace(a,()=>b);};
const coreEdits=[
 ['local rows,provenance=ctSource.collect(observer,queryRuntime,scope.boot,querySequence)',"local cw,cpu=PROFILE_NOW(),os.clock();local rows,provenance=ctSource.collect(observer,queryRuntime,scope.boot,querySequence);PROFILE_ADD('query-and-normalize',cw,cpu);cw,cpu=PROFILE_NOW(),os.clock()"],
 ['history=nextHistory;selection.tracked=count;selection.untracked=overflow',"PROFILE_ADD('parse-and-learn',cw,cpu);cw,cpu=PROFILE_NOW(),os.clock();history=nextHistory;selection.tracked=count;selection.untracked=overflow"],
 ['\n decisions={}\n for key,o',"\n PROFILE_ADD('admission-sort',cw,cpu);cw,cpu=PROFILE_NOW(),os.clock();decisions={}\n for key,o"],
 ['table.sort(decisions,function(a,b)return a.key<b.key end)',"table.sort(decisions,function(a,b)return a.key<b.key end);PROFILE_ADD('decision-construction',cw,cpu)"]
];
for(const [a,b] of coreEdits)core=once(core,a,b);
const edits=coreEdits.map(([a,b])=>'core=replace(core,[===['+a+']===],[===['+b+']===])').join('\n');
const query=worker.slice(worker.indexOf('local function query(cmd,limit)'),worker.indexOf('local AddressQuery='));
assert.ok(query.startsWith('local function query(cmd,limit)'));
const projection=worker.slice(worker.indexOf('local AdmissionPublication='),worker.indexOf('local function publishClassification'));
const lua=String.raw`local n=require('nixio');local fs=require('nixio.fs');local j=require('luci.jsonc')
local base='${deployed.base}';local rows={};local profile={}
local function read(p,l)local f=assert(io.open(p));local s=f:read((l or 4194304)+1)or'';f:close();assert(#s<=(l or 4194304));return s end
local function now()return tonumber(read('/proc/uptime',128):match('^[%d.]+'))end
local function boot()return read('/proc/sys/kernel/random/boot_id',128):gsub('%s+$','')end
local function hash(p,h)local f=assert(io.popen('/usr/bin/sha256sum '..p));local s=f:read(256);f:close();assert(s:match('^(%x+) ')==h)end
hash(base..'/config.json','${deployed.configHash}')
local cfg=assert(j.parse(read(base..'/config.json',131072)))
for _,name in ipairs({'worker.lua','conntrack-source.lua','classifier-core.lua','backend.lua','owned.lua'})do hash(base..'/'..name,cfg.files[name])end
function PROFILE_NOW()return now()end
function PROFILE_ADD(k,w,c)local a=profile[k]or{wall=0,cpu=0};a.wall=a.wall+now()-w;a.cpu=a.cpu+os.clock()-c;profile[k]=a end
local source=dofile(base..'/conntrack-source.lua');local originalNormalize=source.normalize
source.normalize=function(...)local w,c=now(),os.clock();local a,b=originalNormalize(...);PROFILE_ADD('normalize',w,c);return a,b end
local function replace(s,a,b)local first,last=s:find(a,1,true);assert(first and not s:find(a,last+1,true));return s:sub(1,first-1)..b..s:sub(last+1)end
local core=read(base..'/classifier-core.lua');${edits}
local factory=assert(loadstring(core))()
local Backend=dofile(base..'/backend.lua')
local own=dofile(base..'/owned.lua')
${query}
${projection}
local step=factory({observer=cfg.source,boot=boot()},cfg.policy,read,function(cmd)
 assert(cmd=='ip -j -4 address show');local f=assert(io.popen(cmd));local s=f:read(65537);f:close();assert(#s<=65536);return s
end,source,{boot=boot,now=now,query=query})
local function checkClosed()assert(tonumber(read('/sys/kernel/debug/ecm/front_end_ipv4_stop',64))==1);assert(tonumber(read('/sys/kernel/debug/ecm/ecm_nss_ipv4/accelerated_count',64))==0)end
for i=1,3 do
 checkClosed();profile={};local began,cpu=now(),os.clock();local snap=step();PROFILE_ADD('entire-step',began,cpu)
 local w,c=now(),os.clock();for _,f in ipairs(snap.flows)do f.leaf=Backend.leaf(f);f.applied={backend='CAKE-software-baseline',verified=false,softwareReconcilePending=true}end;PROFILE_ADD('leaf-construction',w,c)
 w,c=now(),os.clock();local projected=AdmissionPublication.project(snap);PROFILE_ADD('admission-projection',w,c)
 w,c=now(),os.clock();local clean=own.jsonProject(projected);PROFILE_ADD('json-projection',w,c)
 w,c=now(),os.clock();local bytes=assert(j.stringify(clean));PROFILE_ADD('json-serialize',w,c)
 rows[#rows+1]={iteration=i,queryStarted=snap.provenance.startedAtUptime,querySeconds=snap.provenance.finishedAtUptime-snap.provenance.startedAtUptime,sourceAgeAtSerialize=now()-snap.provenance.startedAtUptime,tracked=#snap.flows,candidates=#projected.flows,bytes=#bytes,profile=profile}
 checkClosed();if i<3 then n.nanosleep(3,0)end
end
print(j.stringify({readonly=true,productionInstrumentation=false,privateRamObserver=true,nssEnabled=false,rows=rows}))`;
const c=await connectRouter();try{
 const e=encode("/usr/bin/lua - <<'NSS47_READONLY_PROFILE'\n"+lua+"\nNSS47_READONLY_PROFILE\n");
 const r=receipt(await c.run(e.command),e);assert.equal(r.code,0,r.stderr);
 const d=JSON.parse(r.stdout);d.observedAt=new Date().toISOString();d.originalSources=original;d.execBytes=e.execBytes;
 fs.writeFileSync(out,JSON.stringify(d,null,2)+'\n',{flag:'wx'});
 console.log(JSON.stringify(d));
}finally{c.close()}
