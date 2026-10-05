// Bounded readonly diagnosis. Restart evidence is separate from current health.
import fs from 'node:fs';import assert from 'node:assert/strict';
import {verifyDeployment} from './deployment-binding.mjs';
import {connectRouter} from '../nss20/connect-router.mjs';
import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
const {deployment}=verifyDeployment();
const code=String.raw`local j=require('luci.jsonc');local fs=require('nixio.fs');local function read(p,l)local f=io.open(p);if not f then return nil end;local s=f:read(l+1)or'';f:close();assert(#s<=l);return s end
local function parsed(p,l)local s=read(p,l);return s and assert(j.parse(s))or nil end
local s=assert(parsed('/tmp/router-project-game-classifier/snapshot.json',4194304));local g=assert(parsed('/tmp/router-project-game-classifier/guardian.json',8192))
local names={};for n in fs.dir('/tmp/router-project-game-classifier')do if n:match('error')or n:match('recover')then names[#names+1]=n end end
print(j.stringify({at=tonumber(read('/proc/uptime',128):match('^[%d.]+')),pointer=read('/root/router-project/game-classifier-generation',512),current={pid=s.pid,start=s.start,producer=s.producer,status=s.status,configSha256=s.configSha256,sequence=s.snapshot and s.snapshot.provenance.sequence,queryStarted=s.snapshot and s.snapshot.provenance.startedAtUptime,error=s.error},guardian=g,lastError=parsed('/tmp/router-project-game-classifier/last-error.json',8192),recoveryFiles=names}))`;
const c=await connectRouter();try{
 const e=encode("/usr/bin/lua - <<'NSS68_WORKER_RECOVERY'\n"+code+'\nNSS68_WORKER_RECOVERY\n'),r=receipt(await c.run(e.command),e);assert.equal(r.code,0,r.stderr);
 const out=JSON.parse(r.stdout);assert.equal(out.current.configSha256,deployment.configHash);
 fs.writeFileSync('work/nss68/worker-recovery-private.json',JSON.stringify(out,null,2)+'\n',{flag:'wx'});
 const error=out.lastError?.error?.replace(/\b(?:\d{1,3}\.){3}\d{1,3}\b/g,'[address]');
 console.log(JSON.stringify({current:out.current,guardianHealthy:out.guardian.healthy,lastErrorAt:out.lastError?.atUptime,lastErrorPid:out.lastError?.pid,lastError:error,recoveryFiles:out.recoveryFiles}));
}finally{c.close()}
