// Independent bounded read + in-memory instrumentation; no production file edits.
import fs from 'node:fs';import assert from 'node:assert/strict';
import {connectRouter} from '../nss20/connect-router.mjs';import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
const root='work/nss37',d=JSON.parse(fs.readFileSync('work/nss35/deployment-latest.json')),cfg=JSON.parse(fs.readFileSync(root+'/original-config-private.json'));
const worker=fs.readFileSync(root+'/original-worker.lua','utf8');const query=worker.slice(worker.indexOf('local function query(cmd,limit)'),worker.indexOf('local AddressQuery='));
let src=fs.readFileSync(root+'/original-conntrack-source.lua','utf8');
function replace(a,b){assert.equal(src.split(a).length,2,a);src=src.replace(a,()=>b);}
replace('local M={}',"local M={};local times={};local last;local function stamp(k)local t=os.clock();times[k]=(times[k]or 0)+t-last;last=t end;M.profile=times");
replace("for line in stdout:gmatch('[^\\n]+')do","for line in stdout:gmatch('[^\\n]+')do last=os.clock()");
replace("  local client=", "  stamp('header');local client=");
replace("  local protocol,number=", "  stamp('client');local protocol,number=");
replace("  if protocol=='udp'or protocol=='tcp'then", "  stamp('protocol');if protocol=='udp'or protocol=='tcp'then");
replace("  local id=attrs", "  stamp('tuple-count');local id=attrs");
replace("  rows[#rows+1]=", "  stamp('attributes');rows[#rows+1]=");
replace("  else ignoredProtocols[protocol]=(ignoredProtocols[protocol]or 0)+1 end", "  else ignoredProtocols[protocol]=(ignoredProtocols[protocol]or 0)+1 end;stamp('row-finish')");
fs.writeFileSync(root+'/normalizer-instrumented.lua',src);
const address=fs.readFileSync('work/nss35/address-query.lua','utf8');
const lua=String.raw`local n=require('nixio');local j=require('luci.jsonc');local base='${d.base}'
local function read(p,l)local f=assert(io.open(p));local s=f:read((l or 4194304)+1);f:close();assert(#s<=(l or 4194304));return s end
local function now()return tonumber(read('/proc/uptime',128):match('^[%d.]+'))end
local function boot()return read('/proc/sys/kernel/random/boot_id',128):gsub('%s+$','')end
local function hash(p,h)local f=assert(io.popen('/usr/bin/sha256sum '..p));local s=f:read(256);f:close();assert(s:match('^(%x+) ')==h)end
hash(base..'/config.json','${d.configHash}');hash(base..'/conntrack-source.lua','${cfg.files['conntrack-source.lua']}')
local cfg=assert(j.parse(read(base..'/config.json',131072)));local source=dofile(base..'/conntrack-source.lua')
${query}
local Address=assert(loadstring([===[${address}]===]))();local addresses=Address.run(n,now,j.parse,base..'/group-runner');local captured
local rows,p=source.collect(cfg.source,{boot=boot,now=now,query=function(...)captured=query(...);return captured end},boot(),1)
local Instrumented=assert(loadstring([===[${src}]===]))();local checked
local function same(a,b)if type(a)~=type(b)then return false end;if type(a)~='table'then return a==b end;for k,v in pairs(a)do if not same(v,b[k])then return false end end;for k in pairs(b)do if a[k]==nil then return false end end;return true end
local wall=now();local cpu=os.clock();for i=1,3 do checked=Instrumented.normalize(cfg.source,p,captured.stdout,captured.stderr,p.boot,p.finishedAtUptime);assert(same(checked,rows))end
local report={routerWrites=false,trafficGenerated=false,productionWorkerInstrumented=false,iterations=3,rows=#rows,sourceBytes=#captured.stdout,wallSeconds=now()-wall,cpuSeconds=os.clock()-cpu,buckets=Instrumented.profile,allNormalizedRowsEqual=true}
print(j.stringify({report=report,capture={stdout=captured.stdout,stderr=captured.stderr,provenance=p,options=cfg.source,addresses=addresses,policy=cfg.policy}}))`;
const c=await connectRouter();try{const e=encode("/usr/bin/lua - <<'NSS37_NORMALIZE_READONLY'\n"+lua+"\nNSS37_NORMALIZE_READONLY\n");const r=receipt(await c.run(e.command),e);assert.equal(r.code,0,r.stderr);const out=JSON.parse(r.stdout);out.report.observedAt=new Date().toISOString();out.report.execBytes=e.execBytes;
 fs.writeFileSync(root+'/source-capture-private.json',JSON.stringify(out.capture,null,2)+'\n',{flag:'wx'});fs.writeFileSync(root+'/normalizer-profile.json',JSON.stringify(out.report,null,2)+'\n');console.log(JSON.stringify(out.report));
}finally{c.close()}
