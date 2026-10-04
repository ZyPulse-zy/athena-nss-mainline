// Read-only closure. Current deployment is NSS47; NSS49 code remains frozen.
import fs from 'node:fs';import assert from 'node:assert/strict';
import {connectRouter} from '../nss20/connect-router.mjs';import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
const ctx=JSON.parse(fs.readFileSync('work/nss47/deployment-latest.json'));assert.equal(ctx.committed,true);
const label=process.argv[2];assert.match(label,/^[a-z0-9-]+$/);
const output='work/nss62/'+label+'-cleanup-audit.json';assert.ok(!fs.existsSync(output));
const code=String.raw`local fs=require('nixio.fs');local j=require('luci.jsonc');local stages={};for x in fs.dir('/tmp')do if x:match('^rp%-nss%d+%-stage%-')then stages[#stages+1]=x end end
local states={};for x in fs.dir('/root/router-project/experiments')do if x:match('^rp%-nss%d+%-state%-')then states[#states+1]=x end end
local f=assert(io.open('/proc/modules'));local modules=f:read(65536);f:close();local experiments={};for x in modules:gmatch('([^\n]+)')do if x:match('^rp_ecm_gate')or x:match('^qca_nss_qdisc ')then experiments[#experiments+1]=x:match('^(%S+)')end end
local f=assert(io.open('/proc/uptime'));local u=f:read(128);f:close();print(j.stringify({stageDirectories=stages,stateDirectories=states,experimentModules=experiments,uptime=tonumber(u:match('^[%d.]+'))}))`;
const c=await connectRouter();try{
 const status=await c.run('sh /root/router-project/scripts/transaction.sh status');assert.equal(status.code,0);assert.equal(status.stdout.trim(),'NO_ACTIVE_TRANSACTION');
 const e=encode("/usr/bin/lua - <<'NSS50_CLOSURE_READONLY'\n"+code+'\nNSS50_CLOSURE_READONLY\n'),r=receipt(await c.run(e.command),e);
 assert.equal(r.code,0,r.stderr);const d=JSON.parse(r.stdout);
 for(const name of ['stageDirectories','stateDirectories','experimentModules'])assert.equal(d[name].length,0,JSON.stringify({[name]:d[name]}));
 const out={passed:true,observedAt:new Date().toISOString(),readonly:true,deploymentReference:'work/nss47/deployment-latest.json',configSha256:ctx.configHash,noActiveRootTransaction:true,noNssStagingDirectory:true,noExperimentStateNodeDirectory:true,noExperimentalGateOrQdiscModule:true,uptime:d.uptime};
 fs.writeFileSync(output,JSON.stringify(out,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(out));
}finally{c.close()}
