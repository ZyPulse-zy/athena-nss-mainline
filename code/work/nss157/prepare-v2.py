from pathlib import Path
r=Path(__file__).resolve().parent
def put(n,s):p=r/n;assert not p.exists();p.write_text(s,encoding='utf-8',newline='')
put('failed-wan-owner.lua',(r.parent/'nss156/failed-wan-owner.lua').read_text(encoding='utf-8'))
put('epoch-driver-v2.mjs',(r/'epoch-driver.mjs').read_text(encoding='utf-8').replace("'./session-binding.mjs'","'./session-binding-v2.mjs'").replace('/run1/','/run3/').replace('/run2/','/run4/'))
put('pilot-supervisor-v2.mjs',(r/'pilot-supervisor.mjs').read_text(encoding='utf-8').replace("'./session-binding.mjs'","'./session-binding-v2.mjs'").replace("'./epoch-driver.mjs'","'./epoch-driver-v2.mjs'").replace("?'/run1':'/run2'","?'/run3':'/run4'"))
put('session-binding-v2.mjs',"import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';import {verifyPreparation as original} from './session-binding.mjs';\nexport function verifyPreparation(){const old=original(),q=JSON.parse(fs.readFileSync('work/nss157/entry-qualified-v2.json'));assert.ok(q.passed&&!q.productionExecution&&q.completeLiteralReadDependenciesVerified);for(const[f,d]of Object.entries(q.sourceManifest))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex'),d,f);return{...old,...q,sourceManifest:{...old.sourceManifest,...q.sourceManifest},externalSourceBindings:old.externalSourceBindings};}\n")
print('Missing existing failed-WAN read helper added without modifications; run1 remains frozen and new attempts use run3/run4.')
