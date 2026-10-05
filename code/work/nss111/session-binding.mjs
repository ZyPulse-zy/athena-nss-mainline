import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';
import {verifyPreparation as previous} from '../nss110/session-binding.mjs';
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
export function verifyPreparation(){const prior=previous(),p=JSON.parse(fs.readFileSync('work/nss111/entry-qualified.json'));assert.ok(p.passed&&p.onlyFailedUnselectedWan4ProcessEpochChanged&&p.productionExecution===false);assert.ok(p.checks.length>=27);assert.equal(p.routingChangesAllowed,false);assert.equal(p.nssHardwarePayloadChanged,false);for(const[f,h]of Object.entries(p.sourceManifest))assert.equal(hash(fs.readFileSync(f)),h,f);return {...prior,sourceManifest:{...prior.sourceManifest,...p.sourceManifest}};}
