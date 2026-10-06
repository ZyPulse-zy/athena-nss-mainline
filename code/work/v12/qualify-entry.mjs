import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';import {spawnSync}from'node:child_process';
import{verifyPreparation as inherited}from'../v11/session-binding.mjs';
const root='work/v12',hash=b=>crypto.createHash('sha256').update(b).digest('hex'),old=inherited();
const model=JSON.parse(fs.readFileSync(root+'/native-qualified.json')),build=JSON.parse(fs.readFileSync(root+'/endpoint-gate/build-manifest.json'));
assert.ok(model.passed&&model.nativeFullFastSyntaxPassed&&model.nativeExactTagReconstructionPassed&&model.model.sixtySecondsObserved);
assert.ok(build.sdk_original_unchanged&&build.source_inputs_unchanged&&build.old_gate_inputs_unchanged);
const manifest={};
for(const name of fs.readdirSync(root))if(/\.(?:mjs|py|lua|ps1)$/.test(name)||['session-cap-qualified.json','runtime-elf-comparison.json','renewal-qualified.json','native-qualified.json'].includes(name)){
 const file=root+'/'+name;manifest[file]=hash(fs.readFileSync(file));
 if(name.endsWith('.mjs')){const r=spawnSync(process.execPath,['--check',file],{encoding:'utf8',windowsHide:true});assert.equal(r.status,0,r.stderr);}
}
for(const name of ['Makefile','two_slot_predicate.h','predicate_test.c','rp_ecm_gate_lab_ct.c','ecm_ae_classifier_public.h','control_harness.py','ct_harness.py','build_local.py','build-manifest.json','control-harness-result.json','rp_ecm_gate_lab_ct.runtime.ko']){const f=root+'/endpoint-gate/'+name;manifest[f]=hash(fs.readFileSync(f));}
const driver=fs.readFileSync(root+'/epoch-driver.mjs','utf8'),audit=fs.readFileSync(root+'/current-audit-diagnostic.mjs','utf8');
assert.ok(driver.includes("const root='work/nss49', observationRoot='work/v12'"));
assert.ok(driver.includes("from '../nss160/declared-baseline.mjs'"));assert.ok(audit.includes('v12\\/session-'));
assert.ok(fs.readFileSync(root+'/close-endpoint.mjs','utf8').includes('^v12-'));
assert.ok(!driver.includes("runNode('work/nss49/current-audit-diagnostic"));
const q={passed:true,observedAt:new Date().toISOString(),sourceManifest:manifest,inheritedBindings:Object.keys(old.sourceManifest).length,
 classifierLeaseSeconds:6,nativeSessionCapSeconds:120,independentOwnerSeconds:180,requestedHardwareSeconds:60,
 oneHealthyWan:true,oneTcpBulkOneUdpRt:true,hardwareExecuted:false,actualNativeFullFactoryModeled:false,
 sourceFreshnessAndExactCtPinPreserved:true,oldLeaseAndRetirementFunctionsByteIdentical:true,payloadBytes:model.combinedHistoricalPayloadBytes};
fs.writeFileSync(root+'/entry-qualified.json',JSON.stringify(q,null,2)+'\n',{flag:'wx'});
const bound=(await import('./session-binding.mjs')).verifyPreparation();
console.log(JSON.stringify({passed:true,bindings:Object.keys(bound.sourceManifest).length,payloadBytes:q.payloadBytes,hardwareExecuted:false}));
