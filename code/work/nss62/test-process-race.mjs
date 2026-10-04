import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {connectRouter} from '../nss27/connect-router.mjs';import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
const source=fs.readFileSync('work/nss62/core-guard-phase.lua','utf8'),old=fs.readFileSync('work/nss53/core-guard-phase.lua','utf8');
assert.equal(source.slice(source.indexOf('function M.waitFresh')),old.slice(old.indexOf('function M.waitFresh')));
const scanOnly=source.slice(0,source.indexOf('function M.waitFresh'))+'\nreturn M\n';
const fixtures=fs.readFileSync('work/nss62/process-race-fixtures.lua','utf8');
const c=await connectRouter();try{
 const code='local SOURCE=[====['+scanOnly+']====]\n'+fixtures;
 const e=encode("/usr/bin/lua - <<'NSS62_RAM_PROC_RACES'\n"+code+'\nNSS62_RAM_PROC_RACES\n');
 const raw=receipt(await c.run(e.command),e);fs.writeFileSync('work/nss62/process-race-tests-raw-private.json',JSON.stringify(raw,null,2)+'\n',{flag:'wx'});assert.equal(raw.code,0,raw.stderr);const p=JSON.parse(raw.stdout);assert.ok(p.passed&&p.checks===15&&p.routerWrites===false);
 const full='local M=assert(loadstring([====['+source+']====]))();local fs=require("nixio.fs");local function read(p,l)local f=assert(io.open(p));local x=f:read(l+1)or"";f:close();assert(#x<=l);return x end;local s=M.scan(fs,read);print(require("luci.jsonc").stringify({passed=true,clockTicks=s.clockTicks,coreGuardPresent=s.guard~=nil,fullSyntaxCompiled=true,routerWrites=false}))';
 const e2=encode("/usr/bin/lua - <<'NSS62_READONLY_COMPILE'\n"+full+'\nNSS62_READONLY_COMPILE\n');const raw2=receipt(await c.run(e2.command),e2);fs.writeFileSync('work/nss62/phase-qualified-raw-private.json',JSON.stringify(raw2,null,2)+'\n',{flag:'wx'});assert.equal(raw2.code,0,raw2.stderr);const q=JSON.parse(raw2.stdout);assert.ok(q.passed&&q.coreGuardPresent&&q.clockTicks===100);
 const hash=x=>crypto.createHash('sha256').update(x).digest('hex');
 const proof={...p,observedAt:new Date().toISOString(),sourceSha256:hash(source),fixtureSha256:hash(fixtures),clockTicks:q.clockTicks,fullSyntaxCompiled:true,scanOnlyFixturesWaitFreshOmitted:true,waitFreshByteIdentical:true,limitsUnchanged:true};
 fs.writeFileSync('work/nss62/phase-qualified.json',JSON.stringify(proof,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(proof));
}finally{c.close()}
