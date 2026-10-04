import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';
import {verifyPreparation as base} from '../nss50/session-binding.mjs';
import {verifyPreparation as phase} from './qualification.mjs';
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
export function verifyPreparation(){
 const q=base();phase();const p=JSON.parse(fs.readFileSync('work/nss51/entry-qualified.json'));
 assert.ok(p.passed&&p.controllerAdmissionOtherwiseByteIdentical&&p.moduleStageOtherwiseByteIdentical&&p.onlyPhaseDiscoveryRuntimeChange&&p.waitFreshByteIdentical);
 assert.equal(p.baseBoundInputs,Object.keys(q.sourceManifest).length);
 for(const[file,digest]of Object.entries(p.sourceManifest))assert.equal(hash(file),digest,'NSS51 binding changed: '+file);
 return{...q,sourceManifest:{...q.sourceManifest,...p.sourceManifest},phaseDiscoveryOverlay:p};
}
