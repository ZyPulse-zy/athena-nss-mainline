// Rendering-only size review. These tuples never authorize a flow or a stage.
import fs from'node:fs';import assert from'node:assert/strict';import crypto from'node:crypto';
import{verifyPreparation}from'../nss140/session-binding.mjs';import{buildPayload}from'../nss140/payload.mjs';import{packetTemplate}from'../nss140/uplink-tag-plan.mjs';import{packGuardian}from'../nss140/pack-guardian.mjs';import{encode}from'../nss11/v7-observe-repair/observe2/transport.mjs';
verifyPreparation();const root='work/nss140',prior=JSON.parse(fs.readFileSync('work/nss138/controlled-class-20261005222654-399b3465/stage-plan-private.json'));
for(const k of['guardianSourceSha256','selectedGuardianSha256','oneEpochControlledPair','phaseSourceSha256','qosSourceSha256','execBytes'])delete prior[k];
const helpers={qos:fs.readFileSync(root+'/qos-physical.lua','utf8'),phase:fs.readFileSync('work/nss69/core-guard-phase.lua','utf8'),classifier:fs.readFileSync(root+'/classifier.lua','utf8'),tags:fs.readFileSync('work/nss49/classified-tags.lua','utf8'),normalizer:fs.readFileSync(root+'/tag-normalizer.lua','utf8')};
const cases=[];
for(const kind of['historical-real-owned-pair','maximal-decimal-IPv4-and-fields-size-only']){
 const selected=structuredClone(prior.selected);
 if(kind.startsWith('maximal'))for(const[slot,f]of Object.entries(selected)){
  f.id=slot==='tcp'?4294967294:4294967295;f.wan=5;f.mark=0x50000;
  f.original.dst=slot==='tcp'?'255.254.253.252':'254.253.252.251';f.original.sport=slot==='tcp'?65534:65535;f.original.dport=65535;
  f.reply.src=f.original.dst;f.reply.dst='253.252.251.250';f.reply.sport=f.original.dport;f.reply.dport=f.original.sport;
  f.classifierKey=[f.wan,f.mark,slot,f.original.src,f.original.sport,f.reply.src,f.reply.dst,f.reply.sport,f.reply.dport,f.zone,f.id].join('|');
 }
 const mapping={mappingByActualClass:true,nssAdmissionAllowed:false,decisions:['tcp','udp'].map(slot=>({slot,protocol:selected[slot].protocol,class:slot==='tcp'?'BULK':'RT',upTag:slot==='tcp'?0x8e050000:0x8e060000,downTag:slot==='tcp'?0x8f050000:0x8f060000,flow:selected[slot]}))};
 const p=packetTemplate(mapping,'f1e2d3c4b5a697887766554433221100',59999);p.expected.nftables=p.expected.nftables.filter(x=>x.chain?.name!=='forward'&&x.rule?.chain!=='forward');
 for(const o of p.expected.nftables)if(o.rule)for(const e of o.rule.expr)if(e.match&&(e.match.left.meta?.key==='l4proto'||e.match.left.ct?.key==='protocol'))assert.ok([6,17].includes(e.match.right),'Protocol missing from size model');
 const payload=buildPayload({tagPlan:{table:p.expected.nftables[0].table.name,owner:'f1e2d3c4b5a697887766554433221100',mode:'rt',expected:p.expected}},helpers),bytes=Buffer.byteLength(payload.stagedCode);
 const plan={...prior,selected,qosCodeBytes:bytes,qosCodeSha256:crypto.createHash('sha256').update(payload.stagedCode).digest('hex')};
 const rendered=packGuardian(fs.readFileSync(root+'/module-stage-guardian.lua','utf8')).replace('__PLAN__',()=>JSON.stringify(plan)).replace('__CORE_PHASE__',()=> 'return{}').replace('__QOS_PHYSICAL__',()=> 'return{}');
 let execBytes=null,execFits=false;try{const e=encode("/usr/bin/lua - <<'NSS20_STAGE_BEGIN'\n"+rendered+"\nNSS20_STAGE_BEGIN\n");execBytes=e.execBytes;execFits=execBytes<=9000;}catch(e){assert.equal(String(e),'Error: Transport length refused');}
 cases.push({kind,renderingOnly:true,currentNssAuthorization:false,productionWrites:false,qosBundleBytes:bytes,qosBundleFitsOriginal73728:bytes<=73728,guardianExecBytes:execBytes,guardianFitsOriginal9000:execFits});
}
const result={passed:cases.every(x=>x.qosBundleFitsOriginal73728&&x.guardianFitsOriginal9000),sizeReviewOnly:true,packetProtocolFieldsValidated:true,invalidV1SizeModelRetained:true,v1UnusableReason:'Model omitted per-decision protocol; template retained extra TCP neighbor rules and had undefined l4proto matches. No entry code or valid payload qualification used this model.',sourceMaximumSeconds:6,nativeMaximumSeconds:27,ownerMaximumSeconds:100,noBudgetWidened:true,oversizedFutureRealInputMustRefuseBeforeStage:true,cases};
fs.writeFileSync('work/nss141/entry-size-review.json',JSON.stringify(result,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(result));
