import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
const root='work/nss154/run2',file=root+'/journal-private.json';
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
export function readJournal(){const b=fs.readFileSync(file);assert.ok(b.length<=1048576);const j=JSON.parse(b);validateJournal(j);return j;}
export function validateJournal(j){
 assert.equal(j.schema,'nss154-finite-supervisor-v1');assert.ok(['READY','STAGED','CLOSED','COMPLETE'].includes(j.state));
 assert.ok(Number.isSafeInteger(j.revision)&&j.revision>=0);assert.equal(j.maxEpochs,2);assert.ok(Array.isArray(j.history)&&j.history.length<=2);
 assert.match(j.entryManifestSha256,/^[a-f0-9]{64}$/);assert.match(j.continuitySha256,/^[a-f0-9]{64}$/);
 if(j.state==='STAGED'){assert.ok(j.history.length<2);assert.match(j.caseDir,/^work\/nss154\/automatic-epoch-\d+-[a-f0-9]+$/);assert.match(j.planSha256,/^[a-f0-9]{64}$/);assert.match(j.receiptSha256,/^[a-f0-9]{64}$/);assert.ok(Number.isSafeInteger(j.process.pid)&&j.process.pid>1);assert.ok(Number.isFinite(Date.parse(j.process.started)));assert.equal(j.process.script,'work/nss154/pilot-supervisor-v2.mjs');}
 if(j.state==='CLOSED')assert.equal(j.history.length,1);
 if(j.state==='COMPLETE')assert.equal(j.history.length,2);
 return true;
}
export function verifyJournalInputs(j){validateJournal(j);assert.equal(hash(fs.readFileSync('work/nss154/entry-source-manifest-v2.json')),j.entryManifestSha256);assert.equal(hash(fs.readFileSync(root+'/continuity-private.json')),j.continuitySha256);if(j.state==='STAGED'){assert.equal(hash(fs.readFileSync(j.caseDir+'/stage-plan-private.json')),j.planSha256);assert.equal(hash(fs.readFileSync(j.caseDir+'/stage-receipt-private.json')),j.receiptSha256);}return j;}
export function writeJournal(j){validateJournal(j);const bytes=Buffer.from(JSON.stringify(j,null,2)+'\n');assert.ok(bytes.length<=1048576);const pending=file+'.'+crypto.randomBytes(4).toString('hex')+'.tmp';const fd=fs.openSync(pending,'wx');try{fs.writeFileSync(fd,bytes);fs.fsyncSync(fd);}finally{fs.closeSync(fd)}fs.renameSync(pending,file);return j;}
export function advance(j,state,extra={}){assert.ok((j.state==='READY'&&state==='STAGED')||(j.state==='CLOSED'&&state==='STAGED')||(j.state==='STAGED'&&state==='CLOSED')||(j.state==='STAGED'&&state==='COMPLETE'));const next={...j,...extra,state,revision:j.revision+1};writeJournal(next);return next;}
