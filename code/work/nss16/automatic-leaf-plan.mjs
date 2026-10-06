import assert from 'node:assert/strict';import {buildPlan} from '../nss15/packet-model.mjs';
const tuple=t=>({src:t.src,dst:t.dst,sport:t.sport,dport:t.dport});
export function decidePair(bundle,{owner,boot,generation,worker,now,selected}){
 assert.equal(bundle.owner,owner);assert.equal(bundle.boot,boot);assert.equal(bundle.generation,generation);assert.equal(bundle.pid,worker.pid);assert.equal(bundle.start,worker.start);assert.equal(worker.alive,true);
 assert.ok(Number.isFinite(now)&&now>=bundle.finishedAtUptime&&now<bundle.validUntilUptime-1,'Classifier result expired or too close to expiry');
 assert.ok(bundle.validUntilUptime<=bundle.startedAtUptime+6);assert.equal(bundle.flows.length,2);
 const decisions=[];
 for(const[protocol,target,tag,key]of[[6,'BULK',2399469568,'tcp'],[17,'RT',2399535104,'udp']]){
  const rows=bundle.flows.filter(f=>f.identity.protocolNumber===protocol);assert.equal(rows.length,1);const f=rows[0],i=f.identity,wanted=selected[key];
  assert.equal(f.decision.class,target,'Default deny until class is known');if(target==='RT')assert.equal(f.decision.budgetAdmitted,true,'RT budget not admitted');
  assert.equal(i.instanceMetadataComplete,true);assert.equal(i.instanceTagSafe,true);assert.equal(Number(i.zone),0);assert.equal(Number(i.connectionId),wanted.id);assert.equal(i.mark,wanted.mark);assert.equal(i.wan,wanted.wan);assert.deepEqual(tuple(i.original),wanted.original);assert.deepEqual(tuple(i.reply),wanted.reply);
  assert.ok(i.queryProvenance.idFieldPresent&&i.queryProvenance.fullMarkFieldPresent&&i.queryProvenance.zoneSource==='successful-explicit-zone0-query');assert.ok(now<f.validUntilUptime-1);
  assert.equal(wanted.protocol,protocol);assert.equal(wanted.zone,0);assert.ok(!(wanted.mark&0x2000));
  decisions.push({slot:key,class:target,protocol,downTag:tag,upTag:0,flow:wanted,validUntilUptime:Math.min(bundle.validUntilUptime,f.validUntilUptime)-1});
 }
 assert.equal(decisions[0].flow.wan,decisions[1].flow.wan);assert.equal(decisions[0].flow.mark,decisions[1].flow.mark);assert.equal(decisions[0].flow.reply.dst,decisions[1].flow.reply.dst);
 return{decisions,nssAdmissionAllowed:false,kernelPinsStillRequired:true,tagGetterAndLeafProofStillRequired:true,continuousFreshnessAndScopedRetirementStillRequired:true};
}
export function packetTemplate(decision,owner,neighborSourcePort){
 assert.match(owner,/^[a-f0-9]{32}$/);assert.ok(Number.isInteger(neighborSourcePort)&&neighborSourcePort>1023&&neighborSourcePort<=65535);
 const objects=[{table:{family:'inet',name:'rp_nss16_'+owner.slice(0,16),comment:owner}}];const seen=new Set();
 for(const d of decision.decisions){
  const p=buildPlan({...d.flow,protocol:17},owner,'rt',20);
  for(const item of p.expected.nftables.slice(1)){
   const x=structuredClone(item);const v=x.chain??x.rule;v.table=objects[0].table.name;
   if(x.chain){if(!seen.has(v.name)){seen.add(v.name);objects.push(x)}continue;}
   const oldName=v.comment.slice(owner.length+1);if(d.protocol===6&&oldName.includes('neighbor'))continue;
   v.comment=owner+':'+d.slot+'_'+oldName;
   for(const e of v.expr){const m=e.match;
    if(m&&(m.left.meta?.key==='l4proto'||m.left.ct?.key==='protocol'))m.right=d.protocol;
    if(e.mangle?.key.meta?.key==='priority'&&e.mangle.value!==0)e.mangle.value=d.downTag;
    if(m&&m.left.meta?.key==='priority'&&m.right!==0)m.right=d.downTag;
    if(m?.left.payload?.protocol==='udp'&&m.left.payload.field==='sport'&&oldName.includes('neighbor'))m.right=neighborSourcePort;
   }
   if(!oldName.includes('neighbor')){
    v.expr.splice(10,0,{match:{op:'==',left:{'&':[{ct:{key:'status'}},8]},right:8}},{match:{op:'==',left:{'&':[{ct:{key:'status'}},512]},right:0}});
   }
   objects.push(x);
  }
 }
 const expected={nftables:objects};return{batch:{nftables:objects.map((x,i)=>({[i===0?'create':'add']:x}))},expected,compileOnly:true,nssAdmissionAllowed:false,requiresIndependentExpiryNoLaterThan:Math.min(...decision.decisions.map(d=>d.validUntilUptime)),mustRefreshOrRetireBeforeExpiry:true};
}
