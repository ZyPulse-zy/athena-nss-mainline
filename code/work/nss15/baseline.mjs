import fs from 'node:fs';
import assert from 'node:assert/strict';
import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
import {canonical} from '../nss12/forward-tag-trial/model.mjs';
export async function readBaseline(c,dir,name){
 const source=fs.readFileSync('work/nss11/v7-observe-repair/observe2/capture.lua','utf8');
 const enc=encode("/usr/bin/lua - 192.168.237.207 full <<'NSS15_BASELINE'\n"+source+"\nNSS15_BASELINE\n");
 const raw=receipt(await c.run(enc.command),enc);fs.writeFileSync(dir+'/'+name+'-raw-private.json',JSON.stringify(raw,null,2)+'\n');assert.equal(raw.code,0);
 const b=JSON.parse(raw.stdout);fs.writeFileSync(dir+'/'+name+'-private.json',JSON.stringify(b,null,2)+'\n');return b;
}
function dns(text){
 let count=0;const normalized=text.replace(/(^\tset bulk_dns4 \{\n)([\s\S]*?)(^\t\}\n)/gm,(_,start,body,end)=>{
  count++;body=body.replace(/\t# count [0-9]+/g,'');
  body=body.replace(/^\s*elements = \{ ([^\n]*) \}\n/gm,(_,items)=>{assert.ok(items.split(', ').every(x=>/^\d+\.\d+\.\d+\.\d+$/.test(x)));return''});return start+body+end;
 });assert.equal(count,1,'Unknown DNS set shape');return normalized;
}
function queues(q){const x=structuredClone(q);for(const rows of Object.values(x))for(const r of rows){for(const k of['bytes','packets','drops','overlimits','requeues','backlog','qlen','memory_used'])delete r[k];if(r.options&&!Array.isArray(r.options))delete r.options.bandwidth}return x}
export function auditBaseline(a,b){
 const checks={};for(const k of['boot','native','lan4','rules','services','addresses','routes','originalFiles','protectedManifestSha256'])checks[k]=canonical(a[k])===canonical(b[k]);
 for(const k of['pbr','nftRuleset'])checks[k+'Configuration']=dns(a[k])===dns(b[k]);
 checks.tenQueueConfigurations=canonical(queues(a.queues))===canonical(queues(b.queues));
 checks.protectedManifest=b.protectedManifestPassed===true;
 checks.ecmStoppedAndZero=Object.entries(b.ecm).every(([k,v])=>v===(['stop4','stop6'].includes(k)?1:0));
 assert.ok(Object.values(checks).every(Boolean),JSON.stringify(checks));
 return{configurationMatches:true,checks,rawRulesetIdentical:a.nftRuleset===b.nftRuleset,ignoredOnlyExistingDynamicDnsElementsAndAutorateBandwidth:true};
}
