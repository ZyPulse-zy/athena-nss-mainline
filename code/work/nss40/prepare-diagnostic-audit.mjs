// Local diagnostic entry derived from the frozen actual attempt. It does not
// alter any router payload, freshness predicate, or audit failure decision.
import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
const trace=fs.readFileSync('work/nss40/trace-protected-audit.mjs','utf8');
const start=trace.indexOf('let body=original;'),end=trace.indexOf("const payload=",start);assert.ok(start>0&&end>start);
const renderer=trace.slice(start,end)+'return code;';
const render="import assert from 'node:assert/strict';\nexport function render(original){\n"+renderer+"\n}\n";
fs.writeFileSync('work/nss40/audit-renderer.mjs',render);
let body=fs.readFileSync('work/nss40/current-audit.mjs','utf8');
body="import {render} from './audit-renderer.mjs';\n"+body;
const a="const code=fs.readFileSync('work/nss23/operational-audit.lua','utf8');",b="const code=render(fs.readFileSync('work/nss23/operational-audit.lua','utf8'));";
assert.ok(body.includes(a));body=body.replace(a,b);
const c="const proof=JSON.parse(raw.stdout);",d="const envelope=JSON.parse(raw.stdout);fs.writeFileSync('work/nss40/'+label+'-diagnostic-audit-private.json',JSON.stringify({...envelope,observedAt:new Date().toISOString()},null,2)+'\\n');assert.equal(envelope.passed,true,envelope.error);const proof=envelope.result;";
assert.ok(body.includes(c));body=body.replace(c,d);
fs.writeFileSync('work/nss40/current-audit-diagnostic.mjs',body);
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const out={prepared:true,routerWrites:false,originalAssertionsRetained:true,sourceSha256:hash('work/nss23/operational-audit.lua'),currentEntryNotRetriedWithGame:true,files:Object.fromEntries(['work/nss40/audit-renderer.mjs','work/nss40/current-audit-diagnostic.mjs'].map(p=>[p,hash(p)]))};
fs.writeFileSync('work/nss40/diagnostic-preparation.json',JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify(out));
