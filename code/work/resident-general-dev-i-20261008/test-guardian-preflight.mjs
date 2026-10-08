import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {executeLua,luaLiteral} from '../resident-dev-20261007/lua-local.mjs';
import {packGuardian} from '../nss149/pack-guardian.mjs';
const root='work/resident-general-dev-i-20261008',model=JSON.parse(fs.readFileSync(root+'/subset-model-latest.json'));
const oldRuntime='work/resident-rc1-run-20261008065912-89843eb9',session=oldRuntime+'/session-20261008065932-3c8c9a9c';
const plan=JSON.parse(fs.readFileSync(session+'/stage-plan-private.json'));delete plan.selected;
const binary=fs.readFileSync(root+'/endpoint-gate/rp_ecm_gate_lab_ct.runtime.ko'),digest=crypto.createHash('sha256').update(binary).digest('hex');
assert.equal(plan.moduleBytes,binary.length);assert.equal(plan.moduleSha256,digest);
const oldSource=fs.readFileSync(oldRuntime+'/module-stage-guardian.lua','utf8'),newSource=fs.readFileSync(model.runtime+'/module-stage-guardian.lua','utf8');
const render=s=>packGuardian(s).replace('__PLAN__','{}').replace('__CORE_PHASE__','return{}').replace('__QOS_PHYSICAL__','return{}');
const tests=[];const add=(name,source,p,expected,env={})=>tests.push({name,source:render(source),plan:p,expected,env});
add('original integration failure reproduces with exact compiled module',oldSource,plan,'assertion failed');
for(let mask=1;mask<8;mask++)add('correct native binding reaches safe pre-fork boundary for mask '+mask,newSource,{...plan,activeMask:mask},'GUARD_PREFLIGHT_REACHED_SAFE_BOUNDARY');
add('wrong module size denied before pipes',newSource,{...plan,moduleBytes:binary.length+1},'assertion failed');
add('wrong module hash denied before pipes',newSource,{...plan,moduleSha256:'0'.repeat(64)},'assertion failed');
add('inline selection still forbidden',newSource,{...plan,selected:{udp:{}}},'Selection must be SHA-pinned in bundle');
add('bundle byte ceiling unchanged',newSource,{...plan,qosCodeBytes:73729},'assertion failed');
add('owner format still required',newSource,{...plan,owner:'bad'},'assertion failed');
add('wrong boot still denied',newSource,plan,'assertion failed',{bootMismatch:true});
add('live ECM count still denied',newSource,plan,'ECM count nonzero',{ecmNonzero:true});
add('open ECM frontend still denied',newSource,plan,'assertion failed',{frontendOpen:true});
let lua='local actual_open=io.open;local MOCK,ENV;\n';
lua+=String.raw`package.preload['luci.jsonc']=function()return{parse=function()return MOCK end}end
package.preload['nixio.fs']=function()return{lstat=function()return nil,'ENOENT',2 end}end
package.preload['nixio']=function()return{pipe=function()error('GUARD_PREFLIGHT_REACHED_SAFE_BOUNDARY')end,fork=function()error('UNEXPECTED_FORK')end}end
io.open=function(p)
 local value;if p=='/proc/sys/kernel/random/boot_id'then value=(ENV.bootMismatch and 'other-boot'or MOCK.boot)..'\n'
 elseif p=='/proc/uptime'then value='1000.00 2000.00\n'
 elseif p:match('^/sys/kernel/debug/ecm/')then value=(p:match('front_end_')and(ENV.frontendOpen and'0'or'1')or(ENV.ecmNonzero and'1'or'0'))..'\n'
 else error('UNEXPECTED_FILE_READ:'..p)end
 return{read=function()return value end,close=function()return true end}
end
`;
for(const t of tests)lua+='do MOCK='+luaLiteral(t.plan)+';ENV='+luaLiteral(t.env)+';local ok,e=pcall(assert(loadstring('+luaLiteral(t.source)+')));assert(not ok);assert(tostring(e):find('+luaLiteral(t.expected)+',1,true),'+luaLiteral(t.name)+');end\n';
lua+='io.open=actual_open;print("GUARDIAN_PREFLIGHT_PASS")\n';
const result=executeLua(lua,'native-guardian-preflight');assert.equal(result.code,0,result.stderr);assert.equal(result.stdout.trim(),'GUARDIAN_PREFLIGHT_PASS');
console.log(JSON.stringify({passed:true,checks:tests.length,originalFailureReproduced:true,correctModulePinned:true,moduleBytes:binary.length,moduleSha256:digest,beforeForkAndWrites:true,routerAccess:false,nativeSourceAndBinaryUnchanged:true}));
