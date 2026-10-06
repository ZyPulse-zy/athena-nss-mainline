import fs from'node:fs';import assert from'node:assert/strict';import crypto from'node:crypto';import{spawnSync}from'node:child_process';
import{verifyPreparation as inherited}from'../v15-qos/session-binding.mjs';
const root='work/v16-three',hash=b=>crypto.createHash('sha256').update(b).digest('hex'),read=p=>JSON.parse(fs.readFileSync(p));
const old=inherited(),native=read(root+'/native-qualified.json'),host=read(root+'/entry-qualified-v2.json');assert.ok(native.passed&&native.productionWrites===false&&host.passed);
for(const[k,n]of Object.entries({classifier:'classifier.lua',qos:'qos-physical.lua',normalizer:'tag-normalizer.lua',fast:'fast-path.lua'}))assert.equal(hash(fs.readFileSync(root+'/'+n)),native.sourceHashes[k]);
assert.ok(native.guardianExecBytes<=9000&&host.modeledPayloadBytes<=73728);const manifest={};
for(const dir of[root,root+'/endpoint-gate'])for(const n of fs.readdirSync(dir))if(/\.(mjs|lua|py|ps1|c|h)$/.test(n)&&!n.includes('private')&&!n.includes('failure')&&!n.includes('.generated.')){const p=dir+'/'+n;manifest[p]=hash(fs.readFileSync(p));if(n.endsWith('.mjs')){const x=spawnSync(process.execPath,['--check',p],{windowsHide:true,encoding:'utf8'});assert.equal(x.status,0,x.stderr);}}
for(const n of['normalizer-qualified.json','qos-native-qualified.json','native-source-qualified.json','runtime-elf-comparison.json','native-qualified.json','entry-qualified-v2.json'])manifest[root+'/'+n]=hash(fs.readFileSync(root+'/'+n));
const proof={...host,sourceManifest:manifest,inheritedBindings:Object.keys(old.sourceManifest).length,guardianSelectionInShaPinnedBundle:true,targetRamValidationPassed:true,wholeFactoryModeled:false,hardwareExecuted:false};
fs.writeFileSync(root+'/entry-qualified-v3.json',JSON.stringify(proof,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({passed:true,bindings:Object.keys(manifest).length+proof.inheritedBindings,payloadBytes:proof.modeledPayloadBytes,guardianExecBytes:native.guardianExecBytes}));
