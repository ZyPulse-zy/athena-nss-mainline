import fs from'node:fs';import assert from'node:assert/strict';import crypto from'node:crypto';import{spawnSync}from'node:child_process';
import{verifyPreparation as inherited}from'../v14-duration/session-binding.mjs';
import{mapClassifiedPair}from'./class-leaf-map.mjs';import{wanTags,packetTemplate}from'./wan-tag-plan.mjs';
import{validateAcceleratedState}from'./parse-ecm.mjs';import{buildPayload}from'./payload.mjs';
const root='work/v15-qos',old=inherited(),hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const write=(n,v)=>fs.writeFileSync(root+'/'+n+'.json',JSON.stringify(v,null,2)+'\n',{flag:'wx'});
const previous='work/v14-duration/session-20261006175602-f6752086';
const selected=JSON.parse(fs.readFileSync(previous+'/selected-private.json'));const frame=JSON.parse(fs.readFileSync(previous+'/post-checkpoint-controlled-receipt-private.json'));
const mapping=mapClassifiedPair(frame,selected);assert.equal(mapping.decisions[0].class,'BULK');assert.equal(mapping.decisions[1].class,'RT');
for(const d of mapping.decisions){const t=wanTags(d.flow.wan,d.class);assert.equal(d.upTag,t.up);assert.equal(d.downTag,t.down);}
const tags=new Set();for(let w=1;w<=5;w++)for(const c of['BULK','RT']){const t=wanTags(w,c);assert.ok(!tags.has(t.up)&&!tags.has(t.down));tags.add(t.up);tags.add(t.down);}assert.equal(tags.size,20);
assert.throws(()=>wanTags(0,'RT'));assert.throws(()=>wanTags(6,'BULK'));assert.throws(()=>wanTags(3,'BE'));
const owner='b'.repeat(32),template=packetTemplate(mapping,owner,59999);template.expected.nftables=template.expected.nftables.filter(x=>x.chain?.name!=='forward'&&x.rule?.chain!=='forward');
const resident=JSON.parse(fs.readFileSync(previous+'/last-record-private.json'));
let state=resident.acceleratedState;for(const [a,b]of[[2399469568,wanTags(4,'BULK').down],[2382692352,wanTags(4,'BULK').up],[2399535104,wanTags(3,'RT').down],[2382757888,wanTags(3,'RT').up]])state=state.replaceAll('='+a+'\n','='+b+'\n');
assert.ok(validateAcceleratedState(state,selected).passed);assert.throws(()=>validateAcceleratedState(resident.acceleratedState,selected));
const input={tagPlan:{table:template.expected.nftables[0].table.name,owner,mode:'rt',expected:template.expected,wanLeafAssignments:template.wanLeafAssignments}};
const sources={qos:fs.readFileSync(root+'/qos-physical.lua','utf8'),phase:fs.readFileSync('work/nss69/core-guard-phase.lua','utf8'),classifier:fs.readFileSync(root+'/classifier.lua','utf8'),tags:fs.readFileSync('work/nss49/classified-tags.lua','utf8'),normalizer:fs.readFileSync(root+'/tag-normalizer.lua','utf8')};
const p=buildPayload(input,sources);assert.ok(Buffer.byteLength(p.stagedCode)<=73728,'Original payload cap refused');fs.writeFileSync(root+'/modeled-payload-private.lua',p.stagedCode,{flag:'wx'});write('modeled-tag-plan-private',input.tagPlan);
const manifest={};for(const n of fs.readdirSync(root))if(/\.(mjs|lua|py|ps1)$/.test(n)&&!n.includes('private')){const f=root+'/'+n;manifest[f]=hash(fs.readFileSync(f));if(n.endsWith('.mjs')){const r=spawnSync(process.execPath,['--check',f],{encoding:'utf8',windowsHide:true});assert.equal(r.status,0,r.stderr);}}
assert.equal(hash(fs.readFileSync(root+'/classifier.lua')),hash(fs.readFileSync('work/v14-duration/classifier.lua')),'Resident consumer contract must stay unchanged');
assert.equal(hash(fs.readFileSync(root+'/fast-path.lua')),hash(fs.readFileSync('work/v14-duration/fast-path.lua')),'Duration and exact retirement stay unchanged');
write('normalizer-qualified',{passed:true,sourceSha256:hash(sources.normalizer),hostOnly:true,targetRamValidationRequiredBeforeNss:true});
write('qos-native-qualified',{passed:true,sourceSha256:hash(sources.qos),actualFirmwareExecution:false,nestedParentSourceReviewed:true,oldPhysicalRootRestoreMechanismReused:true,targetRamValidationRequiredBeforeNss:true});
for(const n of ['normalizer-qualified.json','qos-native-qualified.json'])manifest[root+'/'+n]=hash(fs.readFileSync(root+'/'+n));
write('entry-qualified',{passed:true,sourceManifest:manifest,inheritedBindings:Object.keys(old.sourceManifest).length,phaseSeconds:60,sourceFreshnessSeconds:6,kernelSessionSeconds:90,ownerSeconds:180,clientSeconds:180,nativeGateUnchanged:true,residentClassifierAndConsumerUnchanged:true,newVariable:'per-WAN/class tags and HTB groups',historicalFrameMappingModel:true,modifiedHistoricalEcmTagsModelOnly:true,twentyUniqueDirectionWanClassTags:true,modeledPayloadBytes:Buffer.byteLength(p.stagedCode),targetRamValidationRequired:true,hardwareExecuted:false});
console.log(JSON.stringify({passed:true,newSources:Object.keys(manifest).length,modeledPayloadBytes:Buffer.byteLength(p.stagedCode),hardwareExecuted:false}));
