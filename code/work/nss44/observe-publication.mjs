// Finite passive timing window. No traffic generator, injected failure, or NSS permission.
import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';
import {verifyPreparation} from '../nss42/session-binding.mjs';import {connectRouter} from '../nss20/connect-router.mjs';
import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
const q=verifyPreparation();const source=fs.readFileSync('work/nss41/observe-publication.lua','utf8');
const code=source.replace('__SPEC__',()=>JSON.stringify({configSha256:q.configuration.configSha256}));
const c=await connectRouter();try{
 const e=encode("/usr/bin/lua - <<'NSS44_PASSIVE_TIMING'\n"+code+"\nNSS44_PASSIVE_TIMING\n");
 const raw=receipt(await c.run(e.command),e);fs.writeFileSync('work/nss44/publication-raw-private.json',JSON.stringify(raw,null,2)+'\n');assert.equal(raw.code,0,raw.stderr);
 const data=JSON.parse(raw.stdout);data.observedAt=new Date().toISOString();data.sourceSha256=crypto.createHash('sha256').update(source).digest('hex');data.syntheticTrafficGenerated=false;
 fs.writeFileSync('work/nss44/publication-private.json',JSON.stringify(data,null,2)+'\n');
 console.log(JSON.stringify({readonly:true,seconds:data.seconds,frames:data.frames.length,observerCpuSeconds:data.observerCpuSeconds,
  compactDelays:data.updates.classification.map(r=>r.published-r.queryStart),fullDelays:data.updates.snapshot.map(r=>r.published-r.queryStart),
  completeInputFlows:data.updates.snapshot.map(r=>r.flows),nssOpened:false}));
}finally{c.close()}
