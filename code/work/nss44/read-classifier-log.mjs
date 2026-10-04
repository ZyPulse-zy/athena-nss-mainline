// Current generation log evidence, read-only; full service log stays private.
import fs from 'node:fs';import assert from 'node:assert/strict';
import {verifyPreparation} from '../nss42/session-binding.mjs';
import {connectRouter} from '../nss20/connect-router.mjs';
verifyPreparation();const d=JSON.parse(fs.readFileSync('work/nss39/deployment-latest.json'));assert.match(d.id,/^[a-z0-9-]+$/);
const c=await connectRouter();try{
 const r=await c.run("/usr/bin/timeout -k 1 3 /sbin/logread -e '"+d.id+"' | /usr/bin/tail -n 160");assert.equal(r.code,0);
 fs.writeFileSync('work/nss44/classifier-service-log-private.txt',r.stdout);
 const lines=r.stdout.split('\n').filter(x=>/\b(?:13248|2771)\b/.test(x)&&/assert|failed|stale|Recovery|\.lua:\d+:|Terminated/.test(x));
 console.log(JSON.stringify({readonly:true,lines:lines.map(x=>x.replaceAll(d.base,'<classifier-base>'))}));
}finally{c.close()}
