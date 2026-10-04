import fs from 'node:fs';import assert from 'node:assert/strict';
import {connectRouter} from '../nss20/connect-router.mjs';
import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
const label=process.argv[2];assert.match(label,/^[a-z0-9-]+$/);
const ctx=JSON.parse(fs.readFileSync('work/nss66/trial-private.json'));
const source=fs.readFileSync('work/nss66/observe-trial.lua','utf8');
const body='/usr/bin/lua - '+ctx.base+' '+ctx.configHash+' '+ctx.transactionId+" <<'NSS66_PASSIVE'\n"+source+'\nNSS66_PASSIVE\n';
const e=encode(ctx.base+'/group-runner 6 /bin/sh -c '+"'"+body.replaceAll("'","'\\''")+"'");
const c=await connectRouter();try{
 const raw=receipt(await c.run(e.command),e);
 fs.writeFileSync('work/nss66/'+label+'-pipeline-raw-private.json',JSON.stringify(raw,null,2)+'\n',{flag:'wx'});
 assert.equal(raw.code,0,raw.stderr);const result=JSON.parse(raw.stdout);assert.equal(result.passed,true);
 result.observedAt=new Date().toISOString();
 fs.writeFileSync('work/nss66/'+label+'-pipeline-private.json',JSON.stringify(result,null,2)+'\n',{flag:'wx'});
 console.log(JSON.stringify({passed:true,readonly:true,rows:result.rows.length,seconds:result.finishedAt-result.startedAt,
  observerCpuSeconds:result.observerCpuSeconds,nssAdmissionAllowed:false}));
}finally{c.close()}
