import fs from 'node:fs';import assert from 'node:assert/strict';
assert.ok(!fs.existsSync('work/nss63'));fs.mkdirSync('work/nss63');
for(const n of ['real-session.mjs','current-audit-diagnostic.mjs','cleanup-audit.mjs','clock-anchor.mjs','wait-publication-metadata.mjs','module-stage.mjs'])fs.writeFileSync('work/nss63/'+n,fs.readFileSync('work/nss62/'+n,'utf8').replaceAll('nss62','nss63'),{flag:'wx'});
for(const n of ['core-guard-phase.lua','phase-qualified.json'])fs.writeFileSync('work/nss63/'+n,fs.readFileSync('work/nss62/'+n),{flag:'wx'});
fs.writeFileSync('work/nss63/payload.mjs',fs.readFileSync('work/nss59/payload.mjs'),{flag:'wx'});
console.log('NSS63 exact dependency copy prepared; NSS62 process helper unchanged');
