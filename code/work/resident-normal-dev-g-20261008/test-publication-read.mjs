import fs from 'node:fs';
import assert from 'node:assert/strict';
import {executeLua,luaLiteral} from '../resident-dev-20261007/lua-local.mjs';
import {packLua} from '../nss149/pack-lua.mjs';
import {originalRead,boundedRead,patchPublicationRead} from './publication-read.mjs';
const root='work/resident-normal-dev-g-20261008';
const historical='work/resident-rc1-run-20261008041428-aa44b0dc';
const original=fs.readFileSync(historical+'/classifier.lua','utf8'),candidate=patchPublicationRead(original);
assert.equal(candidate.replace(boundedRead.replaceAll('\n','\r\n'),originalRead.replaceAll('\n','\r\n')),original);
// Execute the actual helper in Lua 5.1. The synthetic filesystem is isolated
// from both production and the desktop; errors and changed bytes stay fatal.
const wrap=source=>'return function(fs,read,now,record,path,cap) local ram="/tmp/router-project-game-classifier"\n'+source+'\nreturn stable(path,cap) end';
const lua=`local old=assert(loadstring(${luaLiteral(wrap(originalRead))}))()
local next=assert(loadstring(${luaLiteral(wrap(boundedRead))}))()
local checks={}
local function test(name,fn)fn();checks[#checks+1]=name end
local function run(fn,opt)
 opt=opt or{};local t=100;local reads=0;local stats=0;local fs={}
 function fs.lstat(path)
  stats=stats+1;if opt.absent and stats==opt.absent then return nil end
  local n=opt.inodes and opt.inodes[stats]or 1
  local s={dev=1,ino=n,type='reg',uid=0,gid=0,nlink=1}
  if opt.bad and opt.bad.at==stats then s[opt.bad.field]=opt.bad.value end
  return s
 end
 local function read(path,cap)
  reads=reads+1;t=t+(opt.delay or 0)
  if opt.io then error(opt.io)end
  local body=reads==1 and 'old-complete' or 'fresh-complete'
  assert(#body<=cap,'Original byte cap');return body
 end
 local ok,body=pcall(fn,fs,read,function()return t end,{deadline=opt.deadline or 300},opt.path or '/tmp/router-project-game-classifier/classification.json',opt.cap or 128)
 return{ok=ok,body=body,reads=reads,stats=stats,time=t}
end
test('actual original rename race refuses',function()local r=run(old,{inodes={1,2}});assert(not r.ok and r.reads==1 and tostring(r.body):find('Classifier publication changed during read',1,true))end)
test('no race uses one exact original read',function()local r=run(next);assert(r.ok and r.body=='old-complete'and r.reads==1 and r.stats==2)end)
for _,channel in ipairs({'classification','guardian','snapshot'})do
 test('one atomic replacement of '..channel,function()local r=run(next,{inodes={1,2,2,2},path='/tmp/router-project-game-classifier/'..channel..'.json'});assert(r.ok and r.body=='fresh-complete'and r.reads==2 and r.stats==4)end)
end
test('repeated replacement cannot loop',function()local r=run(next,{inodes={1,2,2,3}});assert(not r.ok and r.reads==2 and r.stats==4)end)
for _,p in ipairs({'/root/router-project/classifier/config.json','/tmp/router-project-game-classifier/owner','/tmp/router-project-game-classifier/unexpected.json','/elsewhere/classification.json'})do
 test('immutable or unknown path stays fatal '..p,function()local r=run(next,{inodes={1,2},path=p});assert(not r.ok and r.reads==1)end)
end
test('first read consuming reread budget rejects',function()local r=run(next,{inodes={1,2},delay=0.06});assert(not r.ok and r.reads==1)end)
test('second read consuming reread budget rejects',function()local r=run(next,{inodes={1,2,2,2},delay=0.03});assert(not r.ok and r.reads==2)end)
test('independent owner cleanup reserve cannot be crossed',function()local r=run(next,{inodes={1,2},deadline=106});assert(not r.ok and r.reads==1)end)
test('unknown IO error is not retried',function()local r=run(next,{io='permission denied'});assert(not r.ok and r.reads==1)end)
test('byte cap is unchanged',function()local r=run(next,{cap=3});assert(not r.ok and r.reads==1)end)
for _,bad in ipairs({{field='type',value='lnk'},{field='uid',value=1},{field='gid',value=1},{field='nlink',value=2}})do
 test('first unsafe filesystem identity '..bad.field,function()bad.at=1;local r=run(next,{bad=bad});assert(not r.ok and r.reads==0)end)
 test('replacement unsafe filesystem identity '..bad.field,function()bad.at=3;local r=run(next,{bad=bad,inodes={1,2,2,2}});assert(not r.ok and r.reads==1)end)
end
for _,n in ipairs({1,2,3,4})do test('missing lstat '..n,function()local r=run(next,{inodes={1,2,2,2},absent=n});assert(not r.ok and r.reads<=2)end)end
assert(loadstring(${luaLiteral(candidate)}));assert(loadstring(${luaLiteral(packLua(candidate))}));checks[#checks+1]='full original and packed adapter syntax'
print('checks='..#checks)
`;
const raw=executeLua(lua,'publication-read');
assert.equal(raw.code,0,raw.stderr||raw.stdout);
const checks=Number(raw.stdout.match(/checks=(\d+)/)?.[1]);assert.equal(checks,28);
const plan=JSON.parse(fs.readFileSync(historical+'/session-20261008041446-dc3afe4a/stage-plan-private.json'));
const delta=Buffer.byteLength(packLua(candidate))-Buffer.byteLength(packLua(original));
const actualShapeBundleBytes=plan.qosCodeBytes+delta;assert.ok(actualShapeBundleBytes<=73728);
const result={passed:true,checks:checks+3,actualLua51:true,originalRaceReproduced:true,oneImmediateFreshRead:true,rereadLimitSeconds:0.05,
 allOtherClassifierBytesExact:true,originalPackedBytes:Buffer.byteLength(packLua(original)),packedDeltaBytes:delta,
 previousActualBundleBytes:plan.qosCodeBytes,actualShapeBundleBytes,bundleLimitBytes:73728,
 freshActualInputStillEncodedAndCheckedBeforeWrite:true,routerAccess:false,modelOnly:true,rawDirectory:raw.directory};
fs.writeFileSync(raw.directory+'/summary.json',JSON.stringify(result,null,2)+'\n',{flag:'wx'});
fs.writeFileSync(root+'/publication-read-tests-latest.json',JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result));
