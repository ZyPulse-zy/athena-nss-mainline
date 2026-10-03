// Paired RAM replay on the target; never installs the candidate.
import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {connectRouter} from '../nss20/connect-router.mjs';import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
const root='work/nss37',d=JSON.parse(fs.readFileSync('work/nss35/deployment-latest.json')),cfg=JSON.parse(fs.readFileSync(root+'/original-config-private.json')),q=JSON.parse(fs.readFileSync(root+'/normalizer-qualified.json'));assert.equal(q.passed,true);
const worker=fs.readFileSync(root+'/original-worker.lua','utf8');const query=worker.slice(worker.indexOf('local function query(cmd,limit)'),worker.indexOf('local AddressQuery='));
const candidate=fs.readFileSync(root+'/conntrack-source.lua','utf8');assert.equal(crypto.createHash('sha256').update(candidate).digest('hex'),q.sourceSha256);
const fields={BASE:d.base,CONFIG_HASH:d.configHash,SOURCE_HASH:cfg.files['conntrack-source.lua'],QUERY:query,CANDIDATE:candidate};
const code=fs.readFileSync(root+'/normalize-benchmark.lua','utf8').replace(/__([A-Z_]+)__/g,(_,k)=>{assert.ok(k in fields);return fields[k]});
const c=await connectRouter();try{
 const e=encode("/usr/bin/lua - <<'NSS37_RAM_AB'\n"+code+"\nNSS37_RAM_AB\n");const r=receipt(await c.run(e.command),e);assert.equal(r.code,0,r.stderr);const out=JSON.parse(r.stdout);out.observedAt=new Date().toISOString();out.sourceSha256=q.sourceSha256;out.originalSha256=q.originalSha256;out.execBytes=e.execBytes;
 for(const d of out.results){const sum=(which,key)=>d.samples.reduce((n,s)=>n+s[which][key],0);d.oldCpuMean=sum('old','cpuSeconds')/d.samples.length;d.newCpuMean=sum('new','cpuSeconds')/d.samples.length;d.cpuReductionPercent=(1-d.newCpuMean/d.oldCpuMean)*100;d.oldWallMean=sum('old','wallSeconds')/d.samples.length;d.newWallMean=sum('new','wallSeconds')/d.samples.length;}
 fs.writeFileSync(root+'/native-normalizer-qualified.json',JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify({...out,results:out.results.map(({samples,...rest})=>rest)}));
}finally{c.close()}
