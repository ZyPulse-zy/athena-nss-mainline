// A past successful route is only an acquisition hint. All current proofs remain mandatory.
import fs from 'node:fs';import assert from 'node:assert/strict';
export function initialUdpPort(preferred,draw){
 if(preferred!==undefined){assert.ok(Number.isSafeInteger(preferred)&&preferred>=59000&&preferred<59800);return preferred;}
 const n=draw(800);assert.ok(Number.isSafeInteger(n)&&n>=0&&n<800);return 59000+n;
}
export function preferredPort(){const p=JSON.parse(fs.readFileSync('work/resident-dev-20261007/udp-preferred-port.json'));assert.ok(p.previousSessionRestored&&p.onlyAcquisitionHint&&!p.currentAdmissionGranted);return initialUdpPort(p.port,()=>assert.fail('Preferred input missing'));}
