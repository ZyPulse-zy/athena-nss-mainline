// Recovery audit keeps original <6/<9 predicates; no learning/scheduling needed.
// Never use this recovery-only entry to admit NSS or begin a new transaction.
import fs from 'node:fs';import assert from 'node:assert/strict';
let body=fs.readFileSync('work/nss41/current-audit-diagnostic.mjs','utf8');
for(const line of ["import {waitFull} from './wait-full-publication.mjs';\n"," await waitFull(c,ctx,label);\n"]){assert.ok(body.includes(line));body=body.replace(line,'');}
fs.writeFileSync('work/nss41/posttrial-protected-audit.mjs',body);
console.log(JSON.stringify({prepared:true,readonlyRecoveryOnly:true,originalAuditPredicatesUnchanged:true,nssAdmissionAllowed:false}));
