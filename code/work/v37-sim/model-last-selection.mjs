import fs from'node:fs';import crypto from'node:crypto';import assert from'node:assert/strict';
import{selectAnchoredTriple}from'./normal-selection.mjs';
import{validatePreStageRefinement}from'./normal-refinement.mjs';
import{validateRefinement}from'./candidate-policy.mjs';
import{verifyPreparation}from'../v12/session-binding.mjs';
const dir='work/v30-normal/session-20261007005055-dbc327f6',root='work/v37-sim';
const read=n=>JSON.parse(fs.readFileSync(dir+'/'+n));
const old=read('selected-preaudit-private.json'),frame=read('rejected-selection-frame-private.json');
const fresh=selectAnchoredTriple(frame,old.udp)[0];let checks=0;
const check=f=>{f();checks++;};
const denied=f=>{let refused=false;try{refused=f().length===0;}catch{refused=true;}assert.ok(refused);checks++;};
check(()=>{assert.ok(fresh);assert.deepEqual(fresh.udp,old.udp);assert.notDeepEqual(fresh.tcp,old.tcp);assert.notEqual(fresh.tcp.wan,fresh.tcp2.wan);});
check(()=>assert.deepEqual(selectAnchoredTriple(frame,old.udp,{tcp:fresh.tcp.wan,tcp2:fresh.tcp2.wan})[0],fresh));
denied(()=>selectAnchoredTriple({...frame,game:[]},old.udp));
denied(()=>selectAnchoredTriple({...frame,bulk:frame.bulk.filter(f=>f.identity.wan!==fresh.tcp.wan)},old.udp,{tcp:fresh.tcp.wan,tcp2:fresh.tcp2.wan}));
denied(()=>selectAnchoredTriple({...frame,sourceAge:6},old.udp));
const notAdmitted=structuredClone(frame);for(const f of notAdmitted.game)f.decision.budgetAdmitted=false;
denied(()=>selectAnchoredTriple(notAdmitted,old.udp));
const missingClass=structuredClone(frame);missingClass.flows=missingClass.flows.filter(f=>f.identity.protocolNumber!==17);
denied(()=>selectAnchoredTriple(missingClass,old.udp));
const mismatchedGame=structuredClone(old.udp);mismatchedGame.mark^=1;
denied(()=>selectAnchoredTriple(frame,mismatchedGame));
const tags=selected=>Object.fromEntries(Object.entries(selected).map(([slot,f])=>[slot,{wan:f.wan,class:slot==='udp'?'RT':'BULK',upTag:(0x8e00+f.wan*16+(slot==='udp'?6:5))*65536,downTag:(0x8f00+f.wan*16+(slot==='udp'?6:5))*65536}]));
const q=verifyPreparation(),input=selected=>({mode:'stage',openFrontend:true,autoClassified:true,qosDevice:'lan4',
 selected:structuredClone(selected),wanPrerequisites:{boot:q.boot,members:[...new Set(Object.values(selected).map(f=>f.wan))].map(w=>({w,ip:Object.values(selected).find(f=>f.wan===w).reply.dst,pid:2,start:'1',failure:0,index:1,link:'wan',mac:'00:00:00:00:00:00'}))},
 tagPlan:{owner:'model-only',table:'model-only',mode:'rt',wanLeafAssignments:tags(selected)},frozenHash:'0'.repeat(64),insmodArguments:'model=1',protectedModelField:'unchanged'});
const before=input(old),after=input(fresh);
check(()=>assert.deepEqual(validatePreStageRefinement(before,after),after));
check(()=>assert.throws(()=>validateRefinement(before,after),'Original immutable refinement must still refuse a changed TCP'));
check(()=>{const a=structuredClone(after);a.selected.udp.id++;assert.throws(()=>validatePreStageRefinement(before,a));});
check(()=>{const a=structuredClone(after);a.selected.tcp.mark^=1;assert.throws(()=>validatePreStageRefinement(before,a));});
check(()=>{const a=structuredClone(after);a.protectedModelField='changed';assert.throws(()=>validatePreStageRefinement(before,a));});
check(()=>{const a=structuredClone(after);a.tagPlan.wanLeafAssignments.tcp.upTag++;assert.throws(()=>validatePreStageRefinement(before,a));});
const sha=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const result={passed:true,modelOnly:true,checks,actualHistoricalRefusalFrameUsed:true,
 originalGameRetained:true,provisionalTcpMayChangeOnlyBeforeDetachedStage:true,unchangedWanFullMarkNatAddressAndProtectedInputsRequired:true,
 originalImmutableRefinementStillRefusesChangedTcp:true,noGateRetargeting:true,noRouterWrites:true,hardwareExecuted:false,
 actualFrameSha256:sha(dir+'/rejected-selection-frame-private.json'),originalSelectionSha256:sha(dir+'/selected-preaudit-private.json'),
 sourceHashes:Object.fromEntries(['normal-selection.mjs','normal-refinement.mjs','model-last-selection.mjs'].map(n=>[root+'/'+n,sha(root+'/'+n)]))};
fs.writeFileSync(root+'/last-selection-qualified.json',JSON.stringify(result,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(result));
