import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';
import {verifyClosedQualification} from '../nss31/qualification.mjs';import {verifyOpenQualification} from '../nss31/verify-open-qualification.mjs';
const read=p=>JSON.parse(fs.readFileSync(p)),hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
export function verifyCandidate(input){
 verifyClosedQualification(input);verifyOpenQualification();
 for(const [file,proof,field]of [['fast-path.lua','aba-qualified.json','sourceSha256'],['classifier.lua','consumer-qualified.json','adapterSha256']]){const p=read('work/nss32/'+proof);assert.equal(p.passed,true);assert.equal(p.routerWrites,false);assert.equal(hash('work/nss32/'+file),p[field]);}
 const p=read('work/nss32/mainline-preflight-qualified.json');assert.equal(p.passed,true);assert.equal(p.phasedIntegration,true);assert.equal(p.routerMutationAttempted,false);
 assert.equal(input.openFrontend,true);assert.equal(input.qosDevice,'lan4');assert.equal(input.selected.tcp.wan,5);assert.equal(input.selected.udp.wan,5);
}
