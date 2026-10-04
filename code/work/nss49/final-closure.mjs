import fs from 'node:fs';import assert from 'node:assert/strict';
import {connectRouter} from '../nss20/connect-router.mjs';import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
const ctx=JSON.parse(fs.readFileSync('work/nss49/deployment-latest.json'));assert.equal(ctx.committed,true);
const code=String.raw`local fs=require('nixio.fs');local j=require('luci.jsonc');local stages={};for x in fs.dir('/tmp')do if x:match('^rp%-nss%d+%-stage%-')then stages[#stages+1]=x end end
local stateDirs={};for x in fs.dir('/root/router-project/experiments')do if x:match('^rp%-nss%d+%-state%-')then stateDirs[#stateDirs+1]=x end end
local function read(p)local f=assert(io.open(p));local s=f:read(65536);f:close();return s end
local modules=read('/proc/modules');local experiments={};for x in modules:gmatch('([^\n]+)')do if x:match('^rp_ecm_gate')or x:match('^qca_nss_qdisc ')then experiments[#experiments+1]=x:match('^(%S+)')end end
print(j.stringify({stageDirectories=stages,stateDirectories=stateDirs,experimentModules=experiments,boot=read('/proc/sys/kernel/random/boot_id'),uptime=tonumber(read('/proc/uptime'):match('^[%d.]+'))}))`;
const c=await connectRouter();try{
 const status=await c.run('sh /root/router-project/scripts/transaction.sh status');assert.equal(status.code,0);assert.equal(status.stdout.trim(),'NO_ACTIVE_TRANSACTION');
 const e=encode("/usr/bin/lua - <<'NSS28_FINAL_READONLY'\n"+code+"\nNSS28_FINAL_READONLY\n"),r=receipt(await c.run(e.command),e);assert.equal(r.code,0,r.stderr);const d=JSON.parse(r.stdout);
 for(const name of ['stageDirectories','stateDirectories','experimentModules'])assert.equal(d[name].length,0,JSON.stringify({[name]:d[name]}));
 const out={passed:true,observedAt:new Date().toISOString(),readonly:true,noActiveRootTransaction:true,noNssStagingDirectory:true,noExperimentStateNodeDirectory:true,noExperimentalGateOrQdiscModule:true,uptime:d.uptime};
 fs.writeFileSync('work/nss49/final-closure.json',JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify(out));
}finally{c.close()}
