// Target read-only comparison. Does not execute or install the worker candidate.
import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {verifyPreparation} from '../nss42/session-binding.mjs';import {connectRouter} from '../nss20/connect-router.mjs';
import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
verifyPreparation();const d=JSON.parse(fs.readFileSync('work/nss39/deployment-latest.json'));const spec={base:d.base,configHash:d.configHash};
const helper=fs.readFileSync('work/nss44/hash-batch.lua','utf8');
const code=String.raw`local j=require('luci.jsonc');local S=assert(j.parse([===[${JSON.stringify(spec)}]===]));local M=assert(loadstring([====[${helper}]====]))()
local function read(p,l)local f=assert(io.open(p));local s=f:read(l+1)or'';f:close();assert(#s<=l);return s end
local function now()return tonumber(read('/proc/uptime',128):match('^[%d.]+'))end
local function run(cmd)local f=assert(io.popen(cmd));local s=f:read(16385)or'';assert(f:close());assert(#s<=16384);return s end
local cfg=assert(j.parse(read(S.base..'/config.json',131072)));assert(run('/usr/bin/sha256sum '..S.base..'/config.json'):match('^(%x+) ')==S.configHash)
local cmd=M.command(S.base,cfg.files);local names={};for name in pairs(cfg.files)do names[#names+1]=name end;table.sort(names)
local function closed()for _,k in ipairs({'front_end_ipv4_stop','front_end_ipv6_stop'})do assert(tonumber(read('/sys/kernel/debug/ecm/'..k,128))==1)end;assert(tonumber(read('/sys/kernel/debug/ecm/ecm_nss_ipv4/accelerated_count',128))==0)end
local before={uptime=now(),tx=tonumber(read('/sys/class/net/lan4/statistics/tx_bytes',128))};local rows={};closed();local due=now()+5
for pair=1,3 do for _,which in ipairs(pair%2==1 and{'individual','batch'}or{'batch','individual'})do
 assert(now()<due,'Read-only benchmark deadline');local start=now();local cpu=os.clock()
 if which=='individual'then for _,name in ipairs(names)do assert(run('/usr/bin/sha256sum '..S.base..'/'..name):match('^(%x+) ')==cfg.files[name])end
 else assert(M.verify(S.base,cfg.files,run(cmd))==#names)end
 rows[#rows+1]={pair=pair,mode=which,seconds=now()-start,observerCpuSeconds=os.clock()-cpu,payloads=#names}
end end
closed();local after=now();print(j.stringify({readonly=true,routerWrites=false,candidateInstalled=false,everyPayloadMatchedExpectedHash=true,rows=rows,seconds=after-before.uptime,
 backgroundLan4Mbps=(tonumber(read('/sys/class/net/lan4/statistics/tx_bytes',128))-before.tx)*8/(after-before.uptime)/1000000,hashSubprocessCpuIncluded=false}))`;
const c=await connectRouter();try{
 const e=encode(d.base+"/group-runner 6 /usr/bin/lua - <<'NSS44_HASH_READONLY'\n"+code+"\nNSS44_HASH_READONLY\n");
 const raw=receipt(await c.run(e.command),e);fs.writeFileSync('work/nss44/hash-benchmark-raw-private.json',JSON.stringify(raw,null,2)+'\n');assert.equal(raw.code,0,raw.stderr);
 const data=JSON.parse(raw.stdout);data.observedAt=new Date().toISOString();data.execBytes=e.execBytes;data.helperSha256=crypto.createHash('sha256').update(helper).digest('hex');
 fs.writeFileSync('work/nss44/hash-benchmark.json',JSON.stringify(data,null,2)+'\n');console.log(JSON.stringify(data));
}finally{c.close()}
