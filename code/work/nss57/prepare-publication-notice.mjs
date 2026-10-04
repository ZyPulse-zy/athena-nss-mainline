// Preserve NSS57. Change only the read-only scheduling hint; the same locked
// original audit must also match the selected classification query/producer.
import fs from 'node:fs';import assert from 'node:assert/strict';
assert.ok(!fs.existsSync('work/nss58/real-session.mjs'));if(!fs.existsSync('work/nss58'))fs.mkdirSync('work/nss58');
let ctl=fs.readFileSync('work/nss57/real-session.mjs','utf8').replaceAll('nss57','nss58');
ctl=ctl.replace("from './module-stage.mjs'","from '../nss57/module-stage.mjs'");
fs.writeFileSync('work/nss58/real-session.mjs',ctl,{flag:'wx'});
let audit=fs.readFileSync('work/nss57/current-audit-diagnostic.mjs','utf8').replaceAll('nss57','nss58').replace("from './wait-ready-joined.mjs'","from './wait-publication-notice.mjs'").replace(' let epoch;',' let epoch,hint;').replace('  await waitReady(c,ctx,label);','  hint=await waitReady(c,ctx,label);');
const token='assert.equal(service.classifier.pid,proof.pid);assert.equal(service.guardian.pid,proof.guardianPid);';
assert.equal(audit.split(token).length,2);
audit=audit.replace(token,()=>token+"\n if(purpose==='prewrite'){assert.equal(proof.producer,hint.producer,'Original full audit producer differs from classification hint');assert.equal(proof.querySequence,hint.selectedSequence,'Original full audit query differs from classification hint');}");
fs.writeFileSync('work/nss58/current-audit-diagnostic.mjs',audit,{flag:'wx'});
for(const n of['cleanup-audit.mjs','clock-anchor.mjs'])fs.writeFileSync('work/nss58/'+n,fs.readFileSync('work/nss57/'+n,'utf8').replaceAll('nss57','nss58'),{flag:'wx'});
console.log('NSS58 read-only publication-notice scheduling prepared; NSS payload references frozen NSS57');
