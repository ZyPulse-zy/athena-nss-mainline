import fs from 'node:fs';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {patchLearningAlignment} from './learning-alignment.mjs';
import {executeLua,luaLiteral} from './lua-local.mjs';

const root='work/resident-dev-20261007';
const original=fs.readFileSync('work/v20-five/fast-path.lua','utf8').replaceAll('\r\n','\n');
const patched=patchLearningAlignment(original);
const extract=s=>s.slice(s.indexOf(' local function alignLearning(I)'),s.indexOf(' function out.run(due,I,qos,F)'));
const wrap=s=>'return function(A,R,P,phase,fs,read,stopped,now,pause,G)\n'+extract(s)+'\nreturn alignLearning(function()end) end';
const lua=`local old=assert(loadstring(${luaLiteral(wrap(original))}))()
local candidate=assert(loadstring(${luaLiteral(wrap(patched))}))()
local checks={}
local function test(name,fn) fn();checks[#checks+1]=name end
local function run(fn,options)
 options=options or{};local t=100;local reads=0;local getterAt=-1;local stoppedOnce=false
 local R={deadline=300};local phase={}
 function phase.scan()return{observedAt=t}end
 function phase.waitFresh(...) if options.stop then error('Operator requested stop')end;return{observedAt=t}end
 local function now()return t end
 local function pause(n)t=t+n;assert(t<122,'Original alignment bound exceeded')end
 local function stopped()if options.stop then error('Operator requested stop')end end
 local function getter()getterAt=t;return{}end
 local function fresh()
  reads=reads+1;assert(getterAt>=0 and t-getterAt<1.2,'Getter must precede final classification')
  if options.error and(not options.once or reads==1)then error(options.error)end
  if options.race and reads==1 then t=t+0.02;error('Pre-learning time margin insufficient')end
  if options.late and reads==1 then return{provenance={startedAtUptime=t-2.8},flows={{validUntilUptime=t+3.2}}}end
  if options.coreLate and reads==1 then t=t+1.21 end
  if options.neverFresh then return{provenance={startedAtUptime=t-2.8},flows={{validUntilUptime=t+3.2}}}end
  return{provenance={startedAtUptime=t-0.3},flows={{validUntilUptime=t+(options.shortFlow and 3.2 or 5.7)}}}
 end
 local A={resampleClosed=fresh,preLearningReady=function()return true,nil,false end}
 local ok,result,due=pcall(fn,A,R,{},phase,{},function()end,stopped,now,pause,getter)
 return{ok=ok,result=result,due=due,reads=reads,t=t,record=R}
end
test('actual old ready/resample crossing aborts',function()local r=run(old,{race=true});assert(not r.ok and tostring(r.result):find('Pre-learning time margin insufficient',1,true))end)
test('candidate crossing waits for a new valid sample',function()local r=run(candidate,{race=true});assert(r.ok and r.reads==2 and r.record.learningAlignment[1].retryable==true)end)
test('one final validation replaces ready then resample',function()local r=run(candidate);assert(r.ok and r.reads==1 and r.due==r.t+5.7)end)
for _,reason in ipairs({'Pre-learning time margin insufficient','Per-flow pre-learning time margin insufficient','Fresh epoch lacks tag setup reserve'})do
 test('exact age refusal remains retryable '..reason,function()local r=run(candidate,{error=reason,once=true});assert(r.ok and r.reads==2)end)
end
for _,reason in ipairs({'Wrong class','Connection identity changed','Wrong ct mark','Stale classifier source','Unexpected IO error'})do
 test('unsafe refusal stays fatal '..reason,function()local r=run(candidate,{error=reason});assert(not r.ok and r.reads==1 and tostring(r.result):find(reason,1,true))end)
end
test('three point two five second reserve is not relaxed',function()local r=run(candidate,{late=true});assert(r.ok and r.reads>=2 and r.due-r.t>3.25)end)
test('late core observation requires a new core window',function()local r=run(candidate,{coreLate=true});assert(r.ok and r.reads>=2)end)
test('short per flow expiry cannot authorize',function()local r=run(candidate,{shortFlow=true});assert(not r.ok and tostring(r.result):find('Fresh classifier/core phase unavailable',1,true) and r.t<=120.1)end)
test('unchanged twenty second acquisition deadline is bounded',function()local r=run(candidate,{neverFresh=true});assert(not r.ok and r.t<=120.1)end)
test('operator stop is not swallowed',function()local r=run(candidate,{stop=true});assert(not r.ok and r.reads==0)end)
print('checks='..#checks)
for _,name in ipairs(checks)do print(name)end
`;
const result=executeLua(lua,'learning-alignment');
assert.equal(result.code,0,result.stderr||result.stdout);
const count=Number(result.stdout.match(/checks=(\d+)/)?.[1]);assert.equal(count,16);
const receipt={passed:true,checks:count,actualLua51:true,routerAccess:false,originalRaceReproduced:true,
 sourceFreshnessSeconds:6,preLearningReserveSeconds:3,finalReserveSeconds:3.25,coreFreshnessSeconds:1.2,
 alignmentLimitSeconds:20,sourceSha256:crypto.createHash('sha256').update(fs.readFileSync(root+'/learning-alignment.mjs')).digest('hex'),
 rawDirectory:result.directory};
fs.writeFileSync(result.directory+'/summary.json',JSON.stringify(receipt,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify(receipt));
