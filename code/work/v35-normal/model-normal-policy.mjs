import fs from'node:fs';import assert from'node:assert/strict';import{selectNormalTriple}from'./normal-policy.mjs';
// Actual classifier provenance, with application role lists mocked only in this local model.
const root='work/v35-normal',base=JSON.parse(fs.readFileSync('work/v20-five/session-20261006194426-648cb0de/post-checkpoint-controlled-receipt-private.json'));base.bulk=structuredClone(base.tcp);base.game=structuredClone(base.udp);let checks=0;
const keep=selectNormalTriple(base);assert.equal(keep.length,1);checks++;
function deny(change){const f=structuredClone(base);change(f);assert.deepEqual(selectNormalTriple(f),[]);checks++;}
function edit(f,list,index,change){const item=f[list][index],native=f.flows.find(x=>x.key===item.key);change(item);change(native);}
deny(f=>f.game=[]);deny(f=>f.bulk=[]);deny(f=>f.bulk=f.bulk.slice(0,1));deny(f=>f.bulk=[f.bulk[0],structuredClone(f.bulk[0])]);
deny(f=>edit(f,'bulk',0,x=>x.decision.class='BE'));deny(f=>edit(f,'game',0,x=>x.decision.budgetAdmitted=false));
deny(f=>f.sourceAge=6);deny(f=>f.sourceSequence++);deny(f=>f.flows.push(structuredClone(f.flows[0])));
deny(f=>edit(f,'bulk',0,x=>x.identity.instanceTagSafe=false));deny(f=>edit(f,'game',0,x=>x.leaf.nssPermit=true));
deny(f=>f.bulk[0].decision.reason='altered-only-in-role-list');deny(f=>edit(f,'bulk',0,x=>x.identity.reply.src='203.0.113.99'));
deny(f=>edit(f,'bulk',0,x=>x.identity.queryProvenance.idFieldPresent=false));deny(f=>edit(f,'bulk',0,x=>x.identity.zone=1));
deny(f=>f.game=[structuredClone(f.bulk[0])]);
const forbidden=structuredClone(base);forbidden.nssAdmissionAllowed=true;assert.throws(()=>selectNormalTriple(forbidden));checks++;
fs.writeFileSync(root+'/normal-policy-qualified.json',JSON.stringify({passed:true,checks,modelOnly:true,sourceHistoricalProvenanceRetained:true,applicationRoleListsMocked:true,applicationSocketOwnershipStillUsesNss160Filter:true,realGameExecuted:false,multiWanRealApplicationFactoryHardwareExecuted:false,unknownAndWrongRoleDefaultDeny:true,slotCount:3,twoDistinctTcpWanRequired:true,gameWanMayBeEitherOrThird:true},null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({passed:true,checks,modelOnly:true}));
