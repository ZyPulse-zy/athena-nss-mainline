// Diagnostic form of the original protected audit. All original assertions remain.
import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {connectRouter} from '../nss20/connect-router.mjs';import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
import {verifyCurrentClassifier} from '../nss39/binding.mjs';
const {deployment:d}=verifyCurrentClassifier(),original=fs.readFileSync('work/nss23/operational-audit.lua','utf8');
const label=process.argv[2]??'first';assert.match(label,/^[a-z0-9-]+$/);
let body=original;
const replace=(a,b)=>{assert.equal(body.split(a).length,2);body=body.replace(a,b);};
replace("local J=assert(j.parse(read('/tmp/router-project-game-classifier/journal.json',4194304)))","trace('hashes-complete');local J=assert(j.parse(read('/tmp/router-project-game-classifier/journal.json',4194304)));trace('journal-parsed')");
replace("local s=assert(j.parse(read('/tmp/router-project-game-classifier/snapshot.json',4194304)))","trace('selectors-complete');local s=assert(j.parse(read('/tmp/router-project-game-classifier/snapshot.json',4194304)));trace('snapshot-parsed')");
replace("assert(now-s.atUptime<9 and now-s.snapshot.provenance.startedAtUptime<6)","diagnostic.freshness={checkedAt=now,publicationAge=now-s.atUptime,sourceAge=now-s.snapshot.provenance.startedAtUptime,sequence=s.snapshot.provenance.sequence,publishedAt=s.atUptime,queryStarted=s.snapshot.provenance.startedAtUptime};trace('freshness-checked');assert(now-s.atUptime<9 and now-s.snapshot.provenance.startedAtUptime<6)");
replace("print(j.stringify(own.jsonProject(out)))","return own.jsonProject(out)");
const code=String.raw`local json=require('luci.jsonc');local diagnostic={events={}}
local function clock()local f=assert(io.open('/proc/uptime'));local s=f:read(128);f:close();return tonumber(s:match('^[%d.]+'))end
local function trace(name)diagnostic.events[#diagnostic.events+1]={name=name,at=clock()}end
trace('locked-audit-start');local result;local ok,err=xpcall(function()result=(function()
${body}
end)()end,debug.traceback);trace('locked-audit-end');print(json.stringify({passed=ok,error=not ok and tostring(err)or nil,diagnostic=diagnostic,result=result,routerConfigurationWrites=false,originalAssertionsRetained=true}))`;
const payload='exec 8>/tmp/router-project-transaction.lock\nflock -x 8\n/usr/bin/lua - '+d.base+' '+d.configHash+" <<'NSS40_AUDIT_TRACE'\n"+code+'\nNSS40_AUDIT_TRACE\n';
const e=encode(d.base+'/group-runner 6 /bin/sh -c '+"'"+payload.replaceAll("'","'\\''")+"'");
const c=await connectRouter();try{const r=receipt(await c.run(e.command),e);const path='work/nss40/audit-trace-'+label;fs.writeFileSync(path+'-raw-private.json',JSON.stringify(r,null,2)+'\n');assert.equal(r.code,0,r.stderr);const out=JSON.parse(r.stdout);out.observedAt=new Date().toISOString();out.originalSha256=crypto.createHash('sha256').update(original).digest('hex');out.execBytes=e.execBytes;fs.writeFileSync(path+'-private.json',JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify({passed:out.passed,observedAt:out.observedAt,error:out.error,diagnostic:out.diagnostic,routerConfigurationWrites:false,originalAssertionsRetained:true}));}finally{c.close()}
