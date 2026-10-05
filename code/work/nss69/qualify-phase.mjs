import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';
import {connectRouter} from '../nss20/connect-router.mjs';import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
const old=fs.readFileSync('work/nss63/core-guard-phase.lua','utf8'),source=fs.readFileSync('work/nss69/core-guard-phase.lua','utf8'),fixtures=fs.readFileSync('work/nss69/stat-eof-fixtures.lua','utf8');
assert.equal(source.slice(source.indexOf('function M.waitFresh')),old.slice(old.indexOf('function M.waitFresh')));
const hash=x=>crypto.createHash('sha256').update(x).digest('hex');
const c=await connectRouter();try{
 const code='local OLD=[====['+old+']====]\nlocal NEW=[====['+source+']====]\n'+fixtures;
 const e=encode("/usr/bin/lua - <<'NSS69_STAT_EOF_RAM'\n"+code+"\nNSS69_STAT_EOF_RAM\n");const raw=receipt(await c.run(e.command),e);
 fs.writeFileSync('work/nss69/stat-eof-raw-private.json',JSON.stringify(raw,null,2)+'\n',{flag:'wx'});assert.equal(raw.code,0,raw.stderr);const r=JSON.parse(raw.stdout);assert.equal(r.passed,true);
 const code2='local M=assert(loadstring([====['+source+']====]))();local fs=require("nixio.fs");local function read(p,l)local f=assert(io.open(p));local x=f:read(l+1)or"";f:close();assert(#x<=l);return x end;local s=M.scan(fs,read);local t=M.scan(fs,read,{pid=s.guard.pid,start=s.guard.start});print(require("luci.jsonc").stringify({passed=true,clockTicks=s.clockTicks,liveFullAndScopedScan=true,guardSame=t.guard.pid==s.guard.pid and t.guard.start==s.guard.start,routerWrites=false}))';
 const e2=encode("/usr/bin/lua - <<'NSS69_LIVE_READONLY_SCAN'\n"+code2+"\nNSS69_LIVE_READONLY_SCAN\n");const raw2=receipt(await c.run(e2.command),e2);
 fs.writeFileSync('work/nss69/live-phase-read-raw-private.json',JSON.stringify(raw2,null,2)+'\n',{flag:'wx'});assert.equal(raw2.code,0,raw2.stderr);const s=JSON.parse(raw2.stdout);assert.ok(s.passed&&s.guardSame&&s.clockTicks===100);
 const proof={...r,...s,observedAt:new Date().toISOString(),sourceSha256:hash(source),previousSourceSha256:hash(old),fixtureSha256:hash(fixtures),fullSyntaxCompiled:true,waitFreshByteIdentical:true,limitsUnchanged:true,originalFailedBundleSha256:'5f6a0bad5a79512a9bd38f3378e0625e017bf956a37ef84a049a9476185de94b'};
 fs.writeFileSync('work/nss69/phase-qualified.json',JSON.stringify(proof,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(proof));
}finally{c.close()}
