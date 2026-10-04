// Reuses 22 process-model checks and two live readonly phase observations.
// Adds 12 parent-parser differential cases; no filesystem/router configuration writes.
import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {connectRouter}from '../nss20/connect-router.mjs';import {encode,receipt}from '../nss11/v7-observe-repair/observe2/transport.mjs';
const source=fs.readFileSync('work/nss52/core-guard-phase.lua','utf8'),old=fs.readFileSync('work/nss51/core-guard-phase.lua','utf8');
const delta=JSON.parse(fs.readFileSync('work/nss52/phase-delta.json'));const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
assert.equal(source.replace(delta.to,()=>delta.from),old);assert.equal(sha(source),delta.candidateSha256);
const prior=fs.readFileSync('work/nss51/qualify-phase.mjs','utf8');
const begin=prior.indexOf('const tests=String.raw`')+'const tests=String.raw`'.length;const end=prior.indexOf('`;\nconst code=',begin);assert.ok(begin>20&&end>begin);
let tests=prior.slice(begin,end);
const anchor="local n=require('nixio');local fs=require('nixio.fs');local j=require('luci.jsonc')";assert.equal(tests.split(anchor).length,2);
const added=String.raw`
local function oldParent(raw)local a={};for v in assert(raw:match('^%d+ %b() (.*)$')):gmatch('%S+')do a[#a+1]=v end;return tonumber(a[2])end
local function newParent(raw)return tonumber(assert(raw:match('^%d+ %b() (.*)$')):match('^%s*%S+%s+(%S+)'))end
local tails={'S 100 0','S 1 0','S 0 0','S 999999 0','S   100   0','  S 100 0','S\t100\t0','R 100 0','S x 0','S','S 100','S -1 0'}
for index,tail in ipairs(tails)do test('parent parser differential '..index,function()
 local raw='300 (fixture with (nested) parentheses) '..tail
 assert(oldParent(raw)==newParent(raw),'Parent parsing differs')
end)end
local timings={};local sample='300 (fixture) S 100 '..string.rep('0 ',49)
for _,method in ipairs({'old','new'})do local start=os.clock();local parse=method=='old'and oldParent or newParent;for i=1,10000 do assert(parse(sample)==100)end;timings[method]=os.clock()-start end
`;
tests=tests.replace(anchor,()=>added+'\n'+anchor).replace('cases=results,liveReadOnlyPhases=live','cases=results,parentParserBench=timings,liveReadOnlyPhases=live');
const code='local SOURCE=[==['+source+']==]\n'+tests;
const c=await connectRouter();try{
 const e=encode("/usr/bin/timeout -k 1 20 /usr/bin/lua - <<'NSS52_PHASE_READONLY'\n"+code+'\nNSS52_PHASE_READONLY\n');const raw=receipt(await c.run(e.command),e);
 fs.writeFileSync('work/nss52/phase-tests-raw-private.json',JSON.stringify(raw,null,2)+'\n',{flag:'wx'});assert.equal(raw.code,0,raw.stderr);
 const result=JSON.parse(raw.stdout);assert.ok(result.passed&&result.cases.length===34&&result.liveReadOnlyPhases.length===2);
 Object.assign(result,{sourceSha256:sha(source),originalSourceSha256:sha(old),fixtureSha256:sha(tests),nativeLua:true,reusedProcessModelCases:22,newParentDifferentialCases:12,syntheticCasesUseMockedProcessFiles:true,productionGuardUntouched:true,notInstalled:true,notBoundToProductionEntry:true,highLoadQualified:false,benchmarkIsPureParserOnly:true});
 fs.writeFileSync('work/nss52/phase-qualified-private.json',JSON.stringify(result,null,2)+'\n',{flag:'wx'});
 const safe={passed:true,nativeLua:true,sourceSha256:sha(source),originalSourceSha256:sha(old),reusedProcessModelCases:22,newParentDifferentialCases:12,caseResults:result.cases,liveReadOnlyPhases:result.liveReadOnlyPhases.map(p=>({scanSeconds:p.scanSeconds,birthAgeSeconds:p.maxBirthAgeSeconds,waitSeconds:p.waitSeconds,reads:p.reads,birthClockChecked:p.birthClockChecked,guardUntouched:p.guardUntouched})),parentParserBenchSeconds:result.parentParserBench,benchmarkTraversalsPerVersion:10000,benchmarkIsPureParserOnly:true,notWholeRouterCpuBenefit:true,noRouterWrites:true,noNssPermission:true,notInstalled:true,notBoundToProductionEntry:true,highLoadQualified:false,waitFreshByteIdentical:true};
 fs.writeFileSync('work/nss52/phase-qualified-sanitized.json',JSON.stringify(safe,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({...safe,caseResults:undefined}));
}finally{c.close()}
