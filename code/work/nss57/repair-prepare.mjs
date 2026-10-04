import fs from'node:fs';import assert from'node:assert/strict';
const p='work/nss57/fast-path.lua',bad=fs.readFileSync(p,'utf8');const original=fs.readFileSync('work/nss49/fast-path.lua','utf8');
const marker='function M.verifyRenewalAck';const head=bad.slice(0,bad.indexOf(marker));assert.ok(head.includes('function M.mayRereadCounterSnapshot'));
let result=head+original.slice(original.indexOf(marker));
const old="record.tagsBeforeA2=live();getter(record.tagsBeforeA2);measure('A2')";assert.equal(result.split(old).length,2);
const text="record.tagsBeforeA2=live();local a2Counters={};for _,x in ipairs(record.tagsBeforeA2.nftables)do if x.rule then for _,e in ipairs(x.rule.expr)do if e.counter then a2Counters[x.rule.comment:match('([^:]+)$')]=e.counter end end end end\n  if M.mayRereadCounterSnapshot(a2Counters)then assert(now()<record.deadline-8);record.tagsBeforeA2First=record.tagsBeforeA2;record.a2CounterSnapshotReread={reason='one TCP download packet and 1500 bytes ahead in a live counter dump',reads=1,at=now(),nssAdmissionAllowed=false,originalGetterStillRequired=true};record.tagsBeforeA2=live()end\n  getter(record.tagsBeforeA2);measure('A2')";
result=result.replace(old,()=>text);fs.renameSync(p,'work/nss57/fast-path-prepare-error.lua');fs.writeFileSync(p,result,{flag:'wx'});fs.renameSync('work/nss57/counter-tests-raw-private.json','work/nss57/counter-tests-first-syntax-error-raw-private.json');
console.log('Literal replacement repaired; rejected preparation preserved locally');
