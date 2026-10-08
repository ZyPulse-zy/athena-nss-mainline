import fs from'node:fs';import crypto from'node:crypto';import assert from'node:assert/strict';
import{materializeNormal}from'../resident-normal-dev-h-20261008/materialize-normal.mjs';import{activeSlots,activeMask,choosePreparationPair}from'./selection.mjs';
import{canonicalSelection}from'../nss27/flow-selection.mjs';import{mapClassifiedPair}from'./class-leaf-map.mjs';import{packetTemplate}from'./wan-tag-plan.mjs';import{verifyCandidate}from'./candidate-policy.mjs';
import{luaSlots}from'./adapt-plane.mjs';import{executeLua,luaLiteral}from'../resident-dev-20261007/lua-local.mjs';import{packGuardian}from'../nss149/pack-guardian.mjs';import{encode}from'../nss11/v7-observe-repair/observe2/transport.mjs';
const root='work/resident-general-dev-20261008',runtime='work/resident-rc1-run-'+new Date().toISOString().replace(/\D/g,'').slice(0,14)+'-'+crypto.randomBytes(4).toString('hex');
materializeNormal(runtime,Date.now()+600000);const{buildPayload}=await import('../../'+runtime+'/payload.mjs');
const original=JSON.parse(fs.readFileSync('work/resident-rc1-run-20261007163534-ae83fa69/controlled-candidates-private.json'));
const frame={...original,flows:[...original.tcp,...original.udp],nssAdmissionAllowed:false,routerWrites:false};
const all={tcp:canonicalSelection(frame.tcp[0]),udp:canonicalSelection(frame.udp[0]),tcp2:canonicalSelection(frame.tcp.find(f=>f.identity.wan!==frame.tcp[0].identity.wan))};
const oldPlan=JSON.parse(fs.readFileSync('work/resident-rc1-run-20261008055107-ba4ee68e/session-20261008055133-b77e15b3/stage-plan-private.json'));
const sources=Object.fromEntries(['qos','phase','classifier','tags','normalizer'].map(n=>[n,fs.readFileSync(n==='phase'?'work/nss69/core-guard-phase.lua':runtime+'/'+({qos:'qos-physical',classifier:'classifier',tags:'classified-tags',normalizer:'tag-normalizer'}[n])+'.lua','utf8')]));
const checks=[],shapes=[],luas=[];const check=(n,f)=>{f();checks.push(n);};
for(let mask=1;mask<8;mask++){
 const selected=Object.fromEntries(Object.entries(all).filter(([k])=>mask&{tcp:1,udp:2,tcp2:4}[k]));
 check('mask '+mask+' maps exact qualified classes and active leaves',()=>{assert.equal(activeMask(selected),mask);const mapped=mapClassifiedPair(frame,selected);assert.equal(mapped.decisions.length,activeSlots(selected).length);for(const d of mapped.decisions)assert.equal(d.class,d.slot==='udp'?'RT':'BULK');});
 const mapped=mapClassifiedPair(frame,selected),template=packetTemplate(mapped,'1'.repeat(32),59999);
 template.expected.nftables=template.expected.nftables.filter(x=>x.chain?.name!=='forward'&&x.rule?.chain!=='forward');
 const tagPlan={table:template.expected.nftables[0].table.name,owner:'1'.repeat(32),mode:'rt',expected:template.expected,wanLeafAssignments:template.wanLeafAssignments};
 const memberWans=new Set(Object.values(selected).map(f=>f.wan));
 const input={...oldPlan,selected,tagPlan,wanPrerequisites:{...oldPlan.wanPrerequisites,members:oldPlan.wanPrerequisites.members.filter(m=>memberWans.has(m.w)).map(m=>({...m,ip:Object.values(selected).find(f=>f.wan===m.w).reply.dst}))}};
 // The historical plan covers all selected WANs; these values are local models only.
 for(const w of memberWans)if(!input.wanPrerequisites.members.some(m=>m.w===w))input.wanPrerequisites.members.push({...oldPlan.wanPrerequisites.members[0],w,ip:Object.values(selected).find(f=>f.wan===w).reply.dst});
 check('mask '+mask+' candidate scope includes only active WANs',()=>verifyCandidate(input));
 for(const k of ['guardianSourceSha256','selectedGuardianSha256','oneEpochControlledPair','phaseSourceSha256','qosSourceSha256','execBytes'])delete input[k];
 const{stagedCode,tagSource}=buildPayload(input,sources),guardian=packGuardian(fs.readFileSync(runtime+'/module-stage-guardian.lua','utf8')).replace('__PLAN__',()=>JSON.stringify((({selected,...p})=>({...p,tagPlan:{owner:tagPlan.owner,table:tagPlan.table,mode:tagPlan.mode}}))(input))).replace('__CORE_PHASE__','return{}').replace('__QOS_PHYSICAL__','return{}');
 shapes.push({mask,slots:activeSlots(selected),bundleBytes:Buffer.byteLength(stagedCode),guardianExecBytes:null});
 check('mask '+mask+' retains bundle and transport limits',()=>{try{assert.ok(Buffer.byteLength(stagedCode)<=73728,'bundle '+Buffer.byteLength(stagedCode));shapes.at(-1).guardianExecBytes=encode("lua - <<'SUBSET_GUARD'\n"+guardian+"\nSUBSET_GUARD\n").execBytes;}catch(error){fs.writeFileSync(root+'/subset-size-refusal-'+Date.now()+'.json',JSON.stringify({error:String(error),mask,bundleBytes:Buffer.byteLength(stagedCode),guardianBytes:Buffer.byteLength(guardian),modelOnly:true,routerAccess:false})+'\n',{flag:'wx'});throw error;}});
 for(const [label,text]of[['bundle',stagedCode],['guardian',guardian],['tag-plan',tagSource]])luas.push('assert(loadstring('+luaLiteral(text)+'),'+luaLiteral(label+mask)+');');
 const counters={};for(const s of activeSlots(selected))for(const d of ['up','down'])for(const k of ['total','expected','unexpected'])counters[s+'_post_'+d+'_'+k]={packets:k==='unexpected'?0:10,bytes:k==='unexpected'?0:1000};if(selected.udp)counters.udp_post_neighbor_nonzero={packets:0,bytes:0};
 const k={epoch_refresh:'sequence=2 classifier_until_ms=5500 session_until_ms=100000'};
 for(const [n,s]of[['tcp','tcp'],['game','udp'],['tcp2','tcp2']]){k[n+'_permit']=selected[s]?'Y':'N';k[n+'_pinned_state']=selected[s]?'pinned=1 current_hash_matches=1':'pinned=0 current_hash_matches=0';k[n+'_state']=selected[s]?'ever_opened=1 terminal=0 admit=1':'ever_opened=0 terminal=0 admit=0';}
 luas.push('do local F=assert(loadstring('+luaLiteral(luaSlots+fs.readFileSync(runtime+'/fast-path.lua','utf8'))+'))();local s='+luaLiteral(selected)+';local c='+luaLiteral(counters)+';assert(not F.tagCounterAudit(c,false,nil,s).pending);assert(F.verifyRenewalAck('+luaLiteral(k)+',{nextSequence=2,untilMs=5500},100000,s).sequence==2);local key='+luaLiteral(activeSlots(selected)[0]+'_post_up_unexpected')+';c[key]={packets=1,bytes=10};assert(not pcall(F.tagCounterAudit,c,false,nil,s)) end;');
 const scope=Object.fromEntries(activeSlots(selected).filter(k=>k!=='udp').map(k=>[k,selected[k].wan]));
 check('mask '+mask+' preserves frozen active preparation scope',()=>assert.deepEqual(choosePreparationPair({...frame,pairs:[all]},selected.udp,scope),selected));
}
for(const n of ['classifier.lua','classified-tags.lua','fast-path.lua','qos-physical.lua','wan-scope.lua','tag-normalizer.lua'])luas.push('assert(loadstring('+luaLiteral(luaSlots+fs.readFileSync(runtime+'/'+n,'utf8'))+'));');
const lua=executeLua(luas.join('\n')+'\nprint("SUBSET_LUA_PASS")','general-subsets');assert.equal(lua.code,0,lua.stderr);assert.equal(lua.stdout.trim(),'SUBSET_LUA_PASS');checks.push('actual Lua51 syntax, tag counters and native lease acknowledgments for seven masks');
check('unknown selected slot refused',()=>assert.throws(()=>activeSlots({rogue:all.tcp})));
check('empty selected scope refused',()=>assert.throws(()=>activeSlots({})));
check('duplicate native flow refused',()=>assert.throws(()=>activeSlots({tcp:all.tcp,tcp2:all.tcp})));
check('changed mark cannot inherit qualification',()=>{const s=structuredClone(all);s.tcp.mark^=0x10000;assert.throws(()=>mapClassifiedPair(frame,s));});
const out=root+'/subset-model-'+Date.now()+'.json',result={passed:true,checks:checks.length,names:checks,shapes,runtime,luaDirectory:lua.directory,modelOnly:true,routerAccess:false,hardwareQualified:false};fs.writeFileSync(out,JSON.stringify(result,null,2)+'\n',{flag:'wx'});fs.writeFileSync(root+'/subset-model-latest.json',JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({passed:true,checks:checks.length,shapes,modelOnly:true}));
