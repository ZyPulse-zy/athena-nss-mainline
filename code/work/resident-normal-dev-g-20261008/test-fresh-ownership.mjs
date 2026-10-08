import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {collectFreshOwnedFrame} from './fresh-ownership.mjs';
import {normalReaderCode} from './normal-reader.mjs';
import {executeLua,luaLiteral} from '../resident-dev-20261007/lua-local.mjs';
import {encode} from '../nss11/v7-observe-repair/observe2/transport.mjs';
const root='work/resident-normal-dev-g-20261008';
const dir=root+'/freshness-tests-'+Date.now()+'-'+crypto.randomBytes(4).toString('hex');fs.mkdirSync(dir);
const checks=[];const test=async(name,f)=>{await f();checks.push(name);};
function model(options={}){
 let t=0;const origin=Date.parse('2026-10-08T00:00:00.000Z');const events=[];
 const frame=(seq,age)=>({producer:'exact-process-instance',sourceSequence:seq,sourceAge:age,flows:[{identity:{original:{sport:1000}},decision:{class:'RT',budgetAdmitted:true}}],routerWrites:false,nssAdmissionAllowed:false});
 const discovery=frame(10,4.8),final=frame(11,0.8);
 options.change?.(discovery,final);
 const pc={at:'',processes:[],tcp:[],udp:[]};
 const hooks={clock:{monotonic:()=>t,wall:()=>origin+t},
  readNative:async phase=>{events.push(phase);t+=phase==='discovery'?1000:(options.finalMs??1000);return structuredClone(phase==='discovery'?discovery:final);},
  readPc:async()=>{events.push('pc');pc.at=new Date(origin+t).toISOString();t+=options.pcMs??1000;return structuredClone(pc);}};
 return {hooks,events,discovery,final};
}
await test('original pre-OS proof expires; final proof has independently fresh age',async()=>{
 const m=model();assert.ok(m.discovery.sourceAge+2>=6,'Reproduce the original order failure');const r=await collectFreshOwnedFrame(m.hooks);assert.equal(r.native.sourceAge,1.8);assert.equal(r.pc.ageSeconds,2);assert.deepEqual(m.events,['discovery','pc','final']);assert.equal(r.native.sourceSequence,11);
});
await test('final classification change is kept rather than old RT decision',async()=>{
 const m=model({change:(_,f)=>{f.flows[0].decision={class:'BE',budgetAdmitted:false};}});const r=await collectFreshOwnedFrame(m.hooks);assert.equal(r.native.flows[0].decision.class,'BE');assert.equal(r.native.flows[0].decision.budgetAdmitted,false);
});
await test('new uninspected ports do not receive cached socket ownership',async()=>{
 const m=model({change:(_,f)=>f.flows.push({identity:{original:{sport:2000}},decision:{class:'RT',budgetAdmitted:true}})});const r=await collectFreshOwnedFrame(m.hooks);assert.deepEqual(r.native.flows.map(f=>f.identity.original.sport),[1000]);
});
await test('disappeared final flow remains absent',async()=>{
 const m=model({change:(_,f)=>{f.flows=[];}});assert.equal((await collectFreshOwnedFrame(m.hooks)).native.flows.length,0);
});
for(const [name,options,error]of [
 ['changed producer refused',{change:(_,f)=>{f.producer='replacement';}},/owner changed/],
 ['regressed query refused',{change:(_,f)=>{f.sourceSequence=9;}},/query regressed/],
 ['fractional query refused',{change:(_,f)=>{f.sourceSequence=10.5;}},/query regressed/],
 ['final source6 remains refused',{change:(_,f)=>{f.sourceAge=5;}},/classifier source expired/],
 ['OS source6 remains refused',{pcMs:5000},/OS socket source expired/],
 ['negative final age refused',{change:(_,f)=>{f.sourceAge=-2;}},/classifier source expired/],
 ['nonfinite final age refused',{change:(_,f)=>{f.sourceAge=NaN;}},/classifier source expired/],
 ['remote admission permission refused',{change:(_,f)=>{f.nssAdmissionAllowed=true;}},/false/]
 ])await test(name,async()=>{await assert.rejects(collectFreshOwnedFrame(model(options).hooks),error);});
await test('empty discovery never reads OS or performs permission writes',async()=>{
 const m=model({change:d=>{d.flows=[];d.sourceAge=1;}});const r=await collectFreshOwnedFrame(m.hooks);assert.deepEqual(m.events,['discovery']);assert.equal(r.discoveryOnlyEmpty,true);assert.equal(r.native.sourceAge,2);assert.equal(r.native.routerWrites,false);assert.equal(r.native.nssAdmissionAllowed,false);
});
await test('empty source6 still refused',async()=>{
 const m=model({change:d=>{d.flows=[];d.sourceAge=5;}});await assert.rejects(collectFreshOwnedFrame(m.hooks),/Empty classifier source expired/);
});
await test('actual final Lua51 compiles within existing 9000 exec bytes',async()=>{
 const lua=normalReaderCode({fresh:true}),e=encode("lua - <<'NORMAL_FLOW_READ'\n"+lua+'\nNORMAL_FLOW_READ\n');assert.ok(e.execBytes<=9000);const r=executeLua('assert(loadstring('+luaLiteral(lua)+'));print("FRESH_READER_SYNTAX_PASS")','fresh-normal-reader-syntax');assert.equal(r.stdout.trim(),'FRESH_READER_SYNTAX_PASS');
});
const result={passed:true,checks:checks.length,cases:checks,routerAccess:false,source6Unchanged:true,osSource6Unchanged:true,proofRefreshedAfterOsQuery:true,routerWrites:false,trafficGenerated:false};
fs.writeFileSync(dir+'/result.json',JSON.stringify(result,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({...result,dir}));
