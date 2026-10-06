import fs from'node:fs';import assert from'node:assert/strict';import crypto from'node:crypto';import{spawnSync}from'node:child_process';
import{verifyPreparation as prior}from'../nss147/session-binding.mjs';
const root='work/nss148',h=b=>crypto.createHash('sha256').update(b).digest('hex'),q=prior();
const caseDir='work/nss147/controlled-matched-aba-20261006030739-426623cb';
const result=JSON.parse(fs.readFileSync(caseDir+'/result.json')),proof=JSON.parse(fs.readFileSync(caseDir+'/functional-runtime-proof.json'));
assert.ok(result.passed&&result.matchedForwardingABACompleted&&proof.passed&&proof.nativeRenewal&&proof.firmwareZero&&proof.cleanupVerified&&!proof.gameQualityConclusion);
const entry=fs.readFileSync(root+'/real-session.mjs','utf8'),audit=fs.readFileSync(root+'/current-audit-diagnostic.mjs','utf8');
for(const name of['module-stage.mjs','uplink-tag-plan.mjs','declared-baseline.mjs','service-epoch.mjs','parse-ecm-any-wan.mjs','compact-default-queues.mjs'])assert.ok(entry.includes("'../nss147/"+name+"'"),name);
for(const value of["const mode=process.argv[2]??'inspect'",'chooseAfterCheckpoint','mapClassifiedPair(selectionFrame,selected)','validateAcceleratedState','p.seconds>=20&&p.seconds<=21.5','waitStageUndo'])assert.ok(entry.includes(value),value);
assert.ok(audit.includes('/^work\\/nss148\\/real-matched-aba-\\d+-[a-f0-9]+$/'));
for(const name of ['failed-wan-owner.lua','declared-baseline.mjs'])assert.equal(h(fs.readFileSync(root+'/'+name)),h(fs.readFileSync('work/nss147/'+name)));
assert.ok(fs.readFileSync(root+'/read-real-candidates.mjs','utf8').includes("from'../nss143/candidate-adapter.mjs'"));
const sourceManifest={};for(const name of fs.readdirSync(root))if(/\.(mjs|py|lua)$/.test(name)&&!name.includes('private')){
 const file=root+'/'+name;sourceManifest[file]=h(fs.readFileSync(file));if(name.endsWith('.mjs')){const p=spawnSync(process.execPath,['--check',file],{encoding:'utf8',windowsHide:true});assert.equal(p.status,0,p.stderr);}
}
const out={passed:true,at:new Date().toISOString(),sameTestedNss147Factory:true,candidateVisibilityAdapter143:true,defaultReadonly:true,
 inheritedBindings:Object.keys(q.sourceManifest).length,controlledFactoryBindings:1518,controlledHardwareAbaAccepted:true,
 realWrapperHardwareAbaAccepted:false,sourceManifest,budgets:[6,27,100,9000,65536,73728],desktopOperated:false,productionExecution:false,
 auditCaseNamespaceAndExactSourceDependenciesChecked:true,gameQualityConclusion:false};
fs.writeFileSync(root+'/entry-qualified.json',JSON.stringify(out,null,2)+'\n',{flag:'wx'});
const checked=(await import('./session-binding.mjs')).verifyPreparation();console.log(JSON.stringify({passed:true,totalBindings:Object.keys(checked.sourceManifest).length,testedFactoryRound:147,newRealWrapperHardwareAbaAccepted:false,defaultReadonly:true,routerWrites:false}));
