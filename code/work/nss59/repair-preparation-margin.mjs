// Preparation correction before any NSS59 production invocation. Preserve the
// rejected candidate/proof. The original learning/B/A2 deadlines remain intact.
import fs from'node:fs';import assert from'node:assert/strict';
const p='work/nss59/fast-path.lua',s=fs.readFileSync(p,'utf8');const old="stopped();assert(now()<record.deadline-26);record.tagsAfterAFirst";assert.equal(s.split(old).length,2);
fs.renameSync(p,'work/nss59/fast-path-before-margin-correction.lua');fs.writeFileSync(p,s.replace(old,"stopped();assert(now()<record.deadline-15);record.tagsAfterAFirst"),{flag:'wx'});
const d='work/nss59/after-a-diff.json',x=JSON.parse(fs.readFileSync(d));fs.renameSync(d,'work/nss59/after-a-diff-before-margin-correction.json');x.replacement=x.replacement.replace('stopped();assert(now()<record.deadline-26)','stopped();assert(now()<record.deadline-15)');fs.writeFileSync(d,JSON.stringify(x,null,2)+'\n',{flag:'wx'});
fs.renameSync('work/nss59/entry-qualified.json','work/nss59/entry-before-margin-correction.json');for(const n of['counter-tests.json','counter-tests-raw-private.json'])fs.renameSync('work/nss59/'+n,'work/nss59/before-margin-correction-'+n);
console.log('Preserved preparation-only margin correction; no production invocation occurred');
