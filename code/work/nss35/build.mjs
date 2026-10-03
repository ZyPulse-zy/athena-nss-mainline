import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
const root='work/nss35';const read=n=>fs.readFileSync(root+'/'+n,'utf8');const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const frozen=JSON.parse(read('original-manifest.json'));
for(const n of ['worker.lua','guardian.lua','conntrack-source.lua'])assert.equal(hash(fs.readFileSync(root+'/original-'+n)),frozen.files[n]);
const policy=read('observation-policy.lua');const query=read('address-query.lua');
function replaceOnce(s,a,b){assert.equal(s.split(a).length,2,'Expected one exact source anchor');return s.replace(a,()=>b)}
function policyReplace(s){const begin=s.indexOf('local Overload=(function()');const end=s.indexOf('\nend)()',begin)+7;assert.ok(begin>=0&&end>begin);return s.slice(0,begin)+'local Overload=(function()\n'+policy+'\nend)()'+s.slice(end)}
let worker=policyReplace(read('original-worker.lua'));
worker=replaceOnce(worker,"local runtime={boot=boot,now=now,query=query}\nlocal step=factory({observer=cfg.source,boot=thisBoot},cfg.policy,read,function(cmd)assert(cmd=='ip -j -4 address show');return bounded('/sbin/'..cmd,65536)end,source,runtime)",
 "local AddressQuery=(function()\n"+query+"\nend)()\nlocal runtime={boot=boot,now=now,query=query}\nlocal step=factory({observer=cfg.source,boot=thisBoot},cfg.policy,read,function(cmd)assert(cmd=='ip -j -4 address show');return AddressQuery.run(n,now,j.parse,base..'/group-runner')end,source,runtime)");
worker=replaceOnce(worker,'local detail={kind=snap.kind,limit=snap.limit,queryCleanupCompleted=true,attempts=overflowAttempts,baselineRecoveryComplete=overflowRecovered}',
 'local detail={kind=snap.kind,stream=snap.stream,limit=snap.limit,reason=snap.reason,exitCode=snap.exitCode,queryCleanupCompleted=true,attempts=overflowAttempts,baselineRecoveryComplete=overflowRecovered}');
assert.equal(worker.split("'degraded',nil,'bounded-source-overflow',detail").length,5);
worker=worker.replaceAll("'degraded',nil,'bounded-source-overflow',detail","'degraded',nil,snap.kind,detail");
fs.writeFileSync(root+'/worker.lua',worker);fs.writeFileSync(root+'/guardian.lua',policyReplace(read('original-guardian.lua')));
fs.copyFileSync(root+'/original-conntrack-source.lua',root+'/conntrack-source.lua');
const hashes={};for(const n of ['worker.lua','guardian.lua','conntrack-source.lua','observation-policy.lua','address-query.lua'])hashes[n]=hash(fs.readFileSync(root+'/'+n));
fs.writeFileSync(root+'/candidate-manifest.json',JSON.stringify({basedOn:frozen,sha256:hashes,routerWrites:false},null,2)+'\n');
console.log(JSON.stringify({candidateBuilt:true,sha256:hashes,routerWrites:false}));
