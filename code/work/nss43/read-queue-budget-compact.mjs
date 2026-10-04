// Adjacent tc reads distinguish autorate movement from JSON unit conversion.
import fs from 'node:fs';import assert from 'node:assert/strict';
import {verifyPreparation} from './session-binding.mjs';import {connectRouter} from '../nss20/connect-router.mjs';
import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
verifyPreparation();const ctx=JSON.parse(fs.readFileSync('work/nss39/deployment-latest.json'));
const code=String.raw`local j=require('luci.jsonc');local function now()local f=assert(io.open('/proc/uptime'));local s=f:read(128);f:close();return tonumber(s:match('^[%d.]+'))end
local function run(cmd)local f=assert(io.popen(cmd));local s=f:read(32769);local ok=f:close();assert(ok);assert(#s<=32768);return s end
local rows={};for wan=1,5 do local name='rpifb'..wan;local at=now();local a=assert(j.parse(run('/sbin/tc -j qdisc show dev '..name)));local b=run('/sbin/tc -s -d qdisc show dev '..name);local c=assert(j.parse(run('/sbin/tc -j qdisc show dev '..name)));rows[#rows+1]={wan=wan,atUptime=at,finishedUptime=now(),before=a,text=b,after=c}end;print(j.stringify({rows=rows}))`;
const c=await connectRouter();try{
 const e=encode(ctx.base+"/group-runner 6 /usr/bin/lua - <<'NSS43_QUEUE_READONLY'\n"+code+"\nNSS43_QUEUE_READONLY\n");
 const raw=receipt(await c.run(e.command),e);fs.writeFileSync('work/nss43/queue-budget-compact-raw-private.json',JSON.stringify(raw,null,2)+'\n');assert.equal(raw.code,0,raw.stderr);
 const data=JSON.parse(raw.stdout);const rows=data.rows.map(row=>{
  const root=q=>{const a=q.filter(x=>x.kind==='cake'&&x.root);assert.equal(a.length,1);return a[0].options.bandwidth;};
  const match=row.text.match(/\bbandwidth\s+([\d.]+)([GMK]?bit)\b/);assert.ok(match);
  const textMbps=Number(match[1])*{Gbit:1e9,Mbit:1e6,Kbit:1e3,bit:1}[match[2]]/1e6;
  const before=root(row.before),after=root(row.after);
  return {wan:row.wan,seconds:row.finishedUptime-row.atUptime,beforeJsonBytesPerSecond:before,afterJsonBytesPerSecond:after,textMbps,
   unitsVerifiedByAdjacentReads:[before,after].some(v=>Math.abs(v*8/1e6-textMbps)<=Math.max(.001,textMbps*.0001)),
   autorateChangedBetweenBracketReads:before!==after};
 });
 const out={observedAt:new Date().toISOString(),readonly:true,routerWrites:false,captureAfterSteamProfile:true,execBytes:e.execBytes,rows};
 fs.writeFileSync('work/nss43/queue-budget-compact-private.json',JSON.stringify({...out,native:data},null,2)+'\n');console.log(JSON.stringify(out));
}finally{c.close()}
