// Derive tags from an already authenticated classification frame. Never authorize ECM.
import assert from'node:assert/strict';import{wanTags}from'./wan-tag-plan.mjs';import{canonicalSelection}from'../nss27/flow-selection.mjs';
const values=Object.freeze({BULK:{up:0x8e050000,down:0x8f050000},RT:{up:0x8e060000,down:0x8f060000}});
export function mapClassifiedPair(frame,selected){
 assert.equal(frame.nssAdmissionAllowed,false);assert.equal(frame.routerWrites,false);assert.ok(typeof frame.producer==='string'&&frame.producer.length>0);assert.ok(Number.isSafeInteger(frame.sourceSequence)&&frame.sourceSequence>0);assert.ok(Number.isFinite(frame.sourceAge)&&frame.sourceAge>=0&&frame.sourceAge<6);assert.ok(Array.isArray(frame.flows));
 const keys=new Set();for(const f of frame.flows){assert.ok(typeof f.key==='string'&&!keys.has(f.key),'Duplicate classification key');keys.add(f.key);}
 const decisions=[];let epochUntil=Infinity;
 for(const slot of ['tcp','udp','tcp2']){
  const wanted=selected[slot];assert.ok(wanted&&wanted.protocol===(slot==='udp'?17:6));assert.equal(wanted.mark&0x2000,0,'Proxy flow refused');
  const found=frame.flows.filter(f=>f.identity.protocolNumber===wanted.protocol&&Number(f.identity.connectionId)===wanted.id&&Number(f.identity.zone)===wanted.zone);assert.equal(found.length,1,'Exact classified CT instance missing or duplicated');const f=found[0],i=f.identity,d=f.decision,l=f.leaf,q=i.queryProvenance;
  assert.deepEqual(canonicalSelection(f),wanted,'Classified CT/NAT identity changed');assert.equal(i.instanceTagSafe,true);assert.equal(i.instanceMetadataComplete,true);assert.equal(q.querySequence,frame.sourceSequence);assert.equal(q.idFieldPresent,true);assert.equal(q.fullMarkFieldPresent,true);assert.ok(['successful-explicit-zone0-query','explicit-row-zone0'].includes(q.zoneSource));
  assert.ok(Number.isFinite(q.startedAtUptime)&&Number.isFinite(q.finishedAtUptime)&&q.startedAtUptime<=q.finishedAtUptime&&q.finishedAtUptime-q.startedAtUptime<=2);assert.equal(f.observationStartedAtUptime,q.startedAtUptime);assert.equal(f.observedAtUptime,q.finishedAtUptime);assert.ok(Number.isFinite(f.validUntilUptime)&&f.validUntilUptime<=q.startedAtUptime+6&&q.startedAtUptime+frame.sourceAge<f.validUntilUptime,'Classified flow lease expired');
  assert.ok(Object.hasOwn(values,d.class),'Unknown class default deny');if(d.class==='RT')assert.equal(d.budgetAdmitted,true,'RT budget not admitted');else assert.equal(d.reason,'bulk','BULK reason changed');
  const tag=values[d.class];assert.equal(l.class,d.class);assert.equal(l.candidate,true);assert.equal(l.nssPermit,false);assert.equal(l.requiresKernelCTPin,true);assert.equal(l.requiresFreshOwner,true);assert.equal(l.requiresDefaultDenyGate,true);assert.equal(l.changeRequiresExactRetire,true);assert.equal(l.upTag,0,'Resident upTag contract changed');assert.equal(l.downTag,tag.down,'Published down tag differs from class');
  const native=wanTags(wanted.wan,d.class);epochUntil=Math.min(epochUntil,f.validUntilUptime);decisions.push({slot,class:d.class,protocol:wanted.protocol,downTag:native.down,upTag:native.up,flow:wanted,validUntilUptime:f.validUntilUptime,classifierKey:f.key});
 }
 assert.notEqual(selected.tcp.wan,selected.tcp2.wan);for(const f of Object.values(selected)){assert.ok(Number.isInteger(f.wan)&&f.wan>=1&&f.wan<=5);assert.equal((f.mark>>>16)&255,f.wan);}
 return{decisions,producer:frame.producer,sourceSequence:frame.sourceSequence,sourceAge:frame.sourceAge,epochUntil,nssAdmissionAllowed:false,mappingByActualClass:true,mappingByProtocol:false,kernelPinsStillRequired:true,tagGetterAndLeafProofStillRequired:true,continuousFreshnessAndScopedRetirementStillRequired:true};
}
