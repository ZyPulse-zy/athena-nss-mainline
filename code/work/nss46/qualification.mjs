import assert from'node:assert/strict';import {verifyPreparation as historical}from'../nss39/qualification.mjs';import {verifyCurrentClassifier,read,hash}from'./binding.mjs';
export function verifyPreparation(){
 const q=historical(),current=verifyCurrentClassifier();const names=['fast-path.lua','classifier.lua','core-guard-phase.lua','classified-tags.lua','qos-physical.lua','tag-normalizer.lua','wan-scope.lua','state-node.lua','module-stage-guardian.lua','read-prerequisites.lua'];
 const manifest={...q.sourceManifest};for(const name of names){assert.equal(hash('work/nss46/'+name),hash('work/nss39/'+name),'NSS router code may not change with classifier reliability');manifest['work/nss46/'+name]=hash('work/nss46/'+name);}
 assert.equal(current.config.adoptionBoot,q.boot);assert.equal(current.config.source.maxSourceRows,2048);assert.equal(current.config.source.maxSourceBytes,524288);assert.equal(current.config.source.maxQueryAgeSeconds,2);
 return{...q,configuration:current.configuration,sourceManifest:manifest,currentClassifierReliabilityChanges:true,historicalNssHardwareProofReused:true,hardwareRuntimeQualified:false};
}
export function verifyCandidate(input){
 const q=verifyPreparation();assert.equal(input.mode,'stage');assert.equal(input.openFrontend,true);assert.equal(input.autoClassified,true);assert.equal(input.qosDevice,'lan4');const a=input.selected.tcp,b=input.selected.udp,w=a.wan;assert.ok(Number.isInteger(w)&&w>=1&&w<=5);assert.equal(b.wan,w);assert.equal(input.wanPrerequisites.wan,w);assert.equal(input.wanPrerequisites.boot,q.boot);assert.equal(a.mark,b.mark);assert.equal(a.reply.dst,b.reply.dst);
 for(const f of[a,b]){assert.equal(f.original.src,'192.168.237.207');assert.equal(f.zone,0);assert.equal(Math.floor(f.mark/65536)%256,w);assert.equal(f.mark&0x2000,0);assert.ok(Number.isInteger(f.id)&&f.id>0&&f.id<=0xffffffff);}
}
