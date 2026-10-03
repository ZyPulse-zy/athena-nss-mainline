import fs from'node:fs';import assert from'node:assert/strict';import crypto from'node:crypto';
import{verifyNativeABA}from'../nss32/verify-native.mjs';
const read=p=>JSON.parse(fs.readFileSync(p));const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
export function verifyPreparation(){
 const historical=verifyNativeABA();
 const q=read('work/nss33/affinity-qualified.json');assert.equal(q.passed,true);assert.equal(q.hardwareRuntimeQualified,false);
 for(const[p,h]of Object.entries(q.sourceManifest))assert.equal(hash(p),h,'Prepared source changed: '+p);
 const d=read('work/nss33/deployment-latest.json');assert.equal(d.committed,true);assert.equal(d.configHash,q.configuration.configSha256);
 const current=read(d.localDir+'/config.json'),old=read(read('work/nss30/deployment-latest.json').localDir+'/config.json');
 const projection=read('work/nss33/compact-trial-qualified.json');assert.equal(projection.passed,true);assert.equal(current.files['worker.lua'],projection.workerSha256);
 const normalized=structuredClone(current);normalized.files['worker.lua']=old.files['worker.lua'];normalized.installTransaction=old.installTransaction;assert.deepEqual(normalized,old,'Unrelated classifier policy changed');
 assert.equal(hash('work/nss33/classifier.lua'),hash('work/nss32/classifier.lua'));
 assert.equal(hash('work/nss27/endpoint-gate/rp_ecm_gate_lab_ct.runtime.ko'),historical.sourceManifest['work/nss27/endpoint-gate/rp_ecm_gate_lab_ct.runtime.ko']);
 return q;
}
export function verifyCandidate(input){
 const q=verifyPreparation();
 assert.equal(input.mode,'stage');assert.equal(input.openFrontend,true);assert.equal(input.autoClassified,true);assert.equal(input.qosDevice,'lan4');
 const a=input.selected.tcp,b=input.selected.udp,w=a.wan;
 assert.ok(Number.isInteger(w)&&w>=1&&w<=5);assert.equal(b.wan,w);assert.equal(input.wanPrerequisites.wan,w);assert.equal(input.wanPrerequisites.boot,q.boot);
 assert.equal(a.mark,b.mark,'Native gate requires identical full ct marks');assert.equal(a.reply.dst,b.reply.dst);
 for(const f of[a,b]){assert.equal(f.original.src,'192.168.237.207');assert.equal(f.zone,0);assert.equal(Math.floor(f.mark/65536)%256,w);assert.equal(f.mark&0x2000,0);assert.ok(Number.isInteger(f.id)&&f.id>0&&f.id<=0xffffffff);}
}
