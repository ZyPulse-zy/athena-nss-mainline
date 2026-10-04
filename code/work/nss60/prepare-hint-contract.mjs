import fs from 'node:fs';
import assert from 'node:assert/strict';
assert.deepEqual(fs.readdirSync('work/nss61'),['publication-hint.mjs','qualify-entry.mjs','session-binding.mjs','test-hint-contract.mjs']);
for (const n of ['real-session.mjs','current-audit-diagnostic.mjs','cleanup-audit.mjs','clock-anchor.mjs','wait-publication-metadata.mjs']) {
  let s=fs.readFileSync('work/nss60/'+n,'utf8').replaceAll('nss60','nss61');
  if(n==='wait-publication-metadata.mjs') {
    s=s.replace("import fs from 'node:fs';", "import {normalizePublicationHint} from './publication-hint.mjs';\nimport fs from 'node:fs';");
    s=s.replace("'work/nss61/baseline-publication-join.lua'", "'work/nss60/baseline-publication-join.lua'").replace("'work/nss61/metadata-hint.lua'", "'work/nss60/metadata-hint.lua'");
    assert.equal(s.split('return{classificationHint:hint,baselineJoin:out}').length,2);
    s=s.replace('return{classificationHint:hint,baselineJoin:out}', 'return normalizePublicationHint(hint,out)');
  }
  fs.writeFileSync('work/nss61/'+n,s,{flag:'wx'});
}
console.log('NSS61 prepared with unchanged NSS59 payload and NSS60 native scheduling helpers');
