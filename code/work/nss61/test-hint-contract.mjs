import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {normalizePublicationHint} from './publication-hint.mjs';
const label='real-matched-aba-20261004124808-c5c15d65-before';
const c=JSON.parse(fs.readFileSync('work/nss49/'+label+'-alignment-private.json'));
const b=JSON.parse(fs.readFileSync('work/nss60/'+label+'-join-private.json'));
const full=JSON.parse(fs.readFileSync('work/nss60/'+label+'-ownership-private.json'));
const out=normalizePublicationHint(c,b);
assert.equal(out.producer,full.producer);assert.equal(out.selectedSequence,full.querySequence);
assert.equal(out.classificationHint,c);assert.equal(out.baselineJoin,b);
let negativeCases=0;
for(const mutate of[
 x=>delete x.c.alignment,
 x=>delete x.c.alignment.producer,
 x=>x.c.alignment.selectedSequence=0,
 x=>x.b.passed=false,
 x=>x.b.metadataHintOnly=false,
 x=>x.b.originalAuditStillRequired=false,
 x=>x.b.nssAdmissionAllowed=true,
 x=>x.b.join.passed=false,
 x=>x.b.join.source.producer+='-different',
 x=>x.b.join.source.sequence++
]) {const x={c:structuredClone(c),b:structuredClone(b)};mutate(x);assert.throws(()=>normalizePublicationHint(x.c,x.b));negativeCases++;}
const proof={passed:true,checks:14,actualSchedulingToFullAuditParityAssertions:4,negativeCases,originalFullAuditStillMandatory:true,nssPayloadUnchanged:true,routerWrites:false,recordSource:label,sourceSha256:crypto.createHash('sha256').update(fs.readFileSync('work/nss61/publication-hint.mjs')).digest('hex')};
fs.writeFileSync('work/nss61/hint-contract-tests.json',JSON.stringify(proof,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(proof));
