// Offline candidate only. Never alters router files or grants NSS permission.
import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
const base=fs.readFileSync('work/nss51/core-guard-phase.lua','utf8');
const from="   if ok then local a={};for v in assert(raw:match('^%d+ %b() (.*)$')):gmatch('%S+')do a[#a+1]=v end\n    if tonumber(a[2])==g.pid then";
const to="   if ok then local parent=tonumber(assert(raw:match('^%d+ %b() (.*)$')):match('^%s*%S+%s+(%S+)'))\n    if parent==g.pid then";
assert.equal(base.split(from).length,2);const candidate=base.replace(from,()=>to);
assert.equal(candidate.slice(candidate.indexOf('function M.waitFresh')),base.slice(base.indexOf('function M.waitFresh')));
const sha=s=>crypto.createHash('sha256').update(s).digest('hex');
for(const [name,body]of [['core-guard-phase.lua',candidate],['phase-delta.json',JSON.stringify({originalSha256:sha(base),candidateSha256:sha(candidate),from,to,waitFreshByteIdentical:true,onlyUnrelatedParentFieldParsingChanged:true,guardAndChildFullIdentityChecksUnchanged:true,notInstalled:true,notBoundToProductionEntry:true,sourceAndOwnerDeadlinesUnchanged:true},null,2)+'\n']])fs.writeFileSync('work/nss52/'+name,body,{flag:'wx'});
console.log(JSON.stringify({offlineCandidateCreated:true,notInstalled:true,waitFreshByteIdentical:true}));
