import assert from 'node:assert/strict';import {verifyNativeABA} from '../nss32/verify-native.mjs';import {verifyCurrentClassifier,read,hash} from './binding.mjs';
export function verifyPreparation(){
 const historical=verifyNativeABA(),current=verifyCurrentClassifier();const q=read('work/nss39/affinity-qualified.json');assert.equal(q.passed,true);assert.equal(q.hardwareRuntimeQualified,false);
 for(const[p,h]of Object.entries(q.sourceManifest))assert.equal(hash(p),h,'Prepared source changed: '+p);
 assert.deepEqual(q.configuration,current.configuration);
 assert.equal(hash('work/nss27/endpoint-gate/rp_ecm_gate_lab_ct.runtime.ko'),historical.sourceManifest['work/nss27/endpoint-gate/rp_ecm_gate_lab_ct.runtime.ko']);
 assert.equal(q.boot,read('work/nss39/mainline-begin-baseline-private.json').boot);return q;
}
export function verifyCandidate(input){
 const q=verifyPreparation();assert.equal(input.mode,'stage');assert.equal(input.openFrontend,true);assert.equal(input.autoClassified,true);assert.equal(input.qosDevice,'lan4');
 const a=input.selected.tcp,b=input.selected.udp,w=a.wan;assert.ok(Number.isInteger(w)&&w>=1&&w<=5);assert.equal(b.wan,w);assert.equal(input.wanPrerequisites.wan,w);assert.equal(input.wanPrerequisites.boot,q.boot);
 assert.equal(a.mark,b.mark,'Native gate requires identical full ct marks');assert.equal(a.reply.dst,b.reply.dst);
 for(const f of [a,b]){assert.equal(f.original.src,'192.168.237.207');assert.equal(f.zone,0);assert.equal(Math.floor(f.mark/65536)%256,w);assert.equal(f.mark&0x2000,0);assert.ok(Number.isInteger(f.id)&&f.id>0&&f.id<=0xffffffff);}
}
