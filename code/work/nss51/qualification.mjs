import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';
import {verifyPreparation as base,verifyCandidate as candidate} from '../nss49/qualification.mjs';
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
export function verifyPreparation(){
 const q=base(),phase=JSON.parse(fs.readFileSync('work/nss51/phase-qualified.json')),d=JSON.parse(fs.readFileSync('work/nss47/deployment-latest.json'));
 assert.equal(d.committed,true);assert.equal(q.configuration.configSha256,d.configHash);
 assert.ok(phase.passed&&phase.noRouterWrites&&phase.noNssPermission&&phase.waitFreshByteIdentical&&phase.nativeLua&&phase.cases.length===22&&phase.liveReadOnlyPhases.length===2);
 assert.equal(phase.sourceSha256,hash('work/nss51/core-guard-phase.lua'));assert.equal(phase.originalSourceSha256,hash('work/nss49/core-guard-phase.lua'));
 return{...q,sourceManifest:{...q.sourceManifest,'work/nss51/core-guard-phase.lua':hash('work/nss51/core-guard-phase.lua'),'work/nss51/phase-qualified.json':hash('work/nss51/phase-qualified.json')},phaseDiscoveryOnlyChanged:true};
}
export function verifyCandidate(input){verifyPreparation();candidate(input);}
