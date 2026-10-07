import fs from 'node:fs';import assert from 'node:assert/strict';
import{choosePreparationPair,validatePreparingRefinement}from'./final-selection.mjs';
import{validateRefinement as immutable}from'../v20-five/candidate-policy.mjs';
const root='work/resident-dev-20261007',checks=[],test=(n,f)=>{f();checks.push(n);};
const m=JSON.parse(fs.readFileSync(JSON.parse(fs.readFileSync(root+'/entry-model-latest-private.json')).receipt));
const flow=(id,wan,protocol=6)=>({id,wan,protocol,zone:0,mark:wan*65536,original:{src:'192.168.237.207',sport:40000+id},reply:{dst:'192.0.2.'+wan}});
const udp=flow(3,1,17),a=flow(1,2),b=flow(2,4),next=flow(8,2);
const frame={sourceAge:1,pairs:[{tcp:b,udp,tcp2:next}]};
const before={mode:'stage',limits:{source:6,owner:180,client:180},selected:{tcp:a,udp,tcp2:b},tagPlan:{owner:'fixed',table:'fixed',mode:'rt',wanLeafAssignments:{tcp:{wan:2},udp:{wan:1},tcp2:{wan:4}}},frozenHash:'a'.repeat(64),insmodArguments:'fixed'};
const after=structuredClone(before);after.selected.tcp=next;after.frozenHash='b'.repeat(64);after.insmodArguments='new';let validation=0;
test('current qualified TCP may replace stale preparation TCP only within verified WAN slots',()=>assert.deepEqual(choosePreparationPair(frame,udp,[2,4]),after.selected));
test('a different UDP or different bulk WAN remains refused',()=>{assert.throws(()=>choosePreparationPair(frame,flow(9,1,17),[2,4]));assert.throws(()=>choosePreparationPair(frame,udp,[2,5]));});
test('no eligible pair and stale source refuse without a wait loop',()=>{assert.throws(()=>choosePreparationPair({...frame,pairs:[]},udp,[2,4]));assert.throws(()=>choosePreparationPair({...frame,sourceAge:6},udp,[2,4]));});
test('pre owner refinement retains protected fields and calls actual candidate validator',()=>{validatePreparingRefinement(before,after,x=>{validation++;assert.equal(x.selected.tcp.wan,2);});assert.equal(validation,1);});
test('UDP identity, WAN affinity, tag assignments and safety limits cannot change',()=>{for(const edit of [x=>x.selected.udp.id++,x=>x.selected.tcp.wan=5,x=>x.tagPlan.wanLeafAssignments.tcp.wan=5,x=>x.limits.owner=181]){const x=structuredClone(after);edit(x);assert.throws(()=>validatePreparingRefinement(before,x,()=>{}));}});
test('candidate validator rejection is not bypassed',()=>assert.throws(()=>validatePreparingRefinement(before,after,()=>{throw Error('actual class refused');})));
test('original post selection immutable policy still rejects CT retargeting',()=>assert.throws(()=>immutable(before,after),/Immutable CT changed/));
test('actual v65 final frame has an alternate qualified pair before any owner',()=>{
 const r='work/v65-run-20261007145152-711b56e2';
 const rows=fs.readdirSync(r).filter(n=>/^classification-read-.*-private\.json$/.test(n)).map(n=>JSON.parse(fs.readFileSync(r+'/'+n))).filter(x=>x.pairs?.length&&x.sourceSequence===12311);
 assert.ok(rows.length);const current=rows[0],p=current.pairs[0];
 const selected=choosePreparationPair(current,p.udp);assert.equal(selected.udp.id,2428634464);assert.deepEqual([selected.tcp.wan,selected.tcp2.wan].sort(),[3,4]);
 assert.ok(!fs.readdirSync(r,{recursive:true}).some(n=>/^(stage-checkpoint-private\.json|stage-checkpoint-verified\.json|stage-guardian-raw-private\.json)$/.test(n.split(/[\\/]/).at(-1))));
});
test('generated final refinement runs after downloaded checkpoint and before guardian starts',()=>{
 const s=fs.readFileSync(m.modelRuntime+'/module-stage.mjs','utf8');
 const verify=s.indexOf("save(dir,'stage-checkpoint-verified'"),refine=s.indexOf('const refined=validatePreparingRefinement'),start=s.indexOf('const raw=receipt(await c.run(enc.command)',refine);
 assert.ok(verify>0&&refine>verify&&start>refine);assert.ok(s.includes('assert.equal(ctx,undefined)'));
});
test('generated driver confines later selections to verified scope and freezes before owner',()=>{
 const s=fs.readFileSync(m.modelRuntime+'/epoch-driver.mjs','utf8');
 for(const text of ['choosePreparationPair(candidates,continuity.selected.udp)','choosePreparationPair(selectionFrame,preauditSelected.udp)','choosePreparationPair(fresh,originalUdp,bulkScope)','choosePreparationPair(frame,originalUdp,bulkScope)','const refined=makeInput(selected,frame,true)'])assert.ok(s.includes(text),text);
 assert.ok(s.indexOf('const refined=makeInput(selected,frame,true)')<s.indexOf('await onDetached(context);await uploadStage(context)'));
});
fs.writeFileSync(root+'/final-selection-qualified-'+Date.now()+'.json',JSON.stringify({passed:true,checks,sourceBindings:m.sourceBindings,hardwareExecuted:false,actualPriorFrameUsed:true,udpRetained:true,verifiedBulkWanScopeRetained:true,selectionBeforeOwnerOnly:true,noDeadlineOrByteLimitChange:true},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({passed:true,checks:checks.length,sourceBindings:m.sourceBindings,hardwareExecuted:false}));
