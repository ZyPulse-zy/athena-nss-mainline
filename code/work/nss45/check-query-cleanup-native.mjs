import fs from'node:fs';import assert from'node:assert/strict';import crypto from'node:crypto';
import{verifyPreparation}from'../nss42/session-binding.mjs';import{connectRouter}from'../nss20/connect-router.mjs';import{encode,receipt}from'../nss11/v7-observe-repair/observe2/transport.mjs';
verifyPreparation();const root='work/nss45',d=JSON.parse(fs.readFileSync('work/nss39/deployment-latest.json')),cfg=JSON.parse(fs.readFileSync(d.localDir+'/config.json'));
const sha=b=>crypto.createHash('sha256').update(b).digest('hex'),prepared=JSON.parse(fs.readFileSync(root+'/query-cleanup-prepared.json')),fixture=fs.readFileSync(root+'/query-cleanup-replay.lua','utf8');
assert.equal(sha(fixture),prepared.fixtureSha256);assert.equal(sha(fs.readFileSync(root+'/conntrack-source.lua')),prepared.candidateSourceSha256);
const payload=d.base+"/group-runner 6 /usr/bin/lua - "+d.base+" <<'NSS45_QUERY_CHILD_RAM'\n"+fixture+'\nNSS45_QUERY_CHILD_RAM\n',e=encode(payload);assert.ok(e.execBytes<=9000);
const c=await connectRouter();try{
 const h=await c.run('/usr/bin/sha256sum '+d.base+'/config.json '+d.base+'/conntrack-source.lua '+d.base+'/group-runner');assert.equal(h.code,0);assert.deepEqual(h.stdout.trim().split('\n').map(s=>s.split(/\s/)[0]),[d.configHash,cfg.files['conntrack-source.lua'],cfg.files['group-runner']]);
 const r=receipt(await c.run(e.command),e);fs.writeFileSync(root+'/query-cleanup-native-raw-private.json',JSON.stringify(r,null,2)+'\n');assert.equal(r.code,0,r.stderr);
 const x=JSON.parse(r.stdout);assert.ok(x.passed);assert.equal(x.checks,7);assert.equal(sha(x.candidateSource),prepared.candidateSourceSha256);delete x.candidateSource;
 const out={...x,observedAt:new Date().toISOString(),execBytes:e.execBytes,fixtureSha256:prepared.fixtureSha256,candidateSourceSha256:prepared.candidateSourceSha256};fs.writeFileSync(root+'/query-cleanup-native-qualified.json',JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify(out));
}finally{c.close()}
