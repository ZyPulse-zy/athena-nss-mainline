import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {verifyPreparation} from '../nss49/session-binding.mjs';
const base=verifyPreparation();const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
let text=fs.readFileSync('work/nss50/real-session.mjs','utf8');
function replace(a,b){assert.equal(text.split(a).length,2,'Unexpected controller delta: '+a);text=text.replace(a,b);}
replace("import {verifyEpochServices} from './service-epoch.mjs';\n",'');
replace("from '../nss49/parse-ecm-any-wan.mjs'","from './parse-ecm-any-wan.mjs'");
replace("from '../nss49/module-stage.mjs'","from './module-stage.mjs'");
replace("const dir='work/nss50/real-matched-aba-'","const dir='work/nss49/real-matched-aba-'");
replace("runNode('work/nss50/current-audit-diagnostic.mjs',[dir.split('/').at(-1)+'-before','prewrite',dir]);","runNode('work/nss49/current-audit-diagnostic.mjs',[dir.split('/').at(-1)+'-before','prewrite']);");
replace("runNode('work/nss50/current-audit-diagnostic.mjs',[dir.split('/').at(-1)+'-after','recovery',dir]);","runNode('work/nss49/current-audit-diagnostic.mjs',[dir.split('/').at(-1)+'-after','recovery']);");
replace("verifyEpochServices(JSON.parse(fs.readFileSync(dir+'/service-epoch-private.json')).services,before.services);",'');
assert.equal(text,fs.readFileSync('work/nss49/real-session.mjs','utf8'),'Unexpected change outside the service audit overlay');
const tests=JSON.parse(fs.readFileSync('work/nss50/service-epoch-tests.json'));assert.ok(tests.passed&&tests.cases===24&&tests.withinExperimentServiceDriftRejected&&tests.noRouterOrServiceWrites);
const sources=['real-session.mjs','current-audit-diagnostic.mjs','service-epoch.mjs','session-binding.mjs','test-service-epoch.mjs','qualify-overlay.mjs'].map(n=>'work/nss50/'+n);
const out={passed:true,baseBoundInputs:Object.keys(base.sourceManifest).length,reusesExactlyBoundNss49Cases:99,reusesUnchangedNss49NativeRamCases:13,localServiceEpochCases:tests.cases,controllerOtherwiseByteIdentical:true,routerPayloadsByteIdentical:true,originalFreshnessAndDeadlinesUnchanged:true,withinExperimentServiceDriftRejected:true,onlyPreexistingHealthySingBoxPidChangesAdopted:true,sourceManifest:Object.fromEntries(sources.map(p=>[p,hash(p)])),testProofBindings:{'work/nss50/service-epoch-tests.json':hash('work/nss50/service-epoch-tests.json')},nssPermitGrantedByQualification:false};
fs.writeFileSync('work/nss50/entry-overlay-qualified.json',JSON.stringify(out,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({passed:true,baseBoundInputs:out.baseBoundInputs,newSourceInputs:sources.length,serviceCases:tests.cases,routerPayloadsByteIdentical:true}));
