import fs from 'node:fs';import assert from 'node:assert/strict';
import {connectRouter} from '../nss20/connect-router.mjs';
const ctx=JSON.parse(fs.readFileSync('work/nss33/deployment-latest.json'));assert.match(ctx.id,/^nss23-[a-z0-9-]+$/);
const c=await connectRouter();try{const r=await c.run("/usr/bin/timeout -k 1 3 /sbin/logread -e '"+ctx.id+"' | /usr/bin/tail -n 80");assert.equal(r.code,0);fs.writeFileSync('work/nss34/classifier-service-log-private.txt',r.stdout);console.log(r.stdout);}finally{c.close()}
