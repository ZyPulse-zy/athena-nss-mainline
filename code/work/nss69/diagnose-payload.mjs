import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {packetTemplate} from '../nss16/automatic-leaf-plan.mjs';
import {buildPayload} from '../nss63/payload.mjs';
const dir='work/nss68/real-matched-aba-20261005035144-b351a48d';
const p=JSON.parse(fs.readFileSync(dir+'/stage-plan-private.json'));
const selected=JSON.parse(fs.readFileSync(dir+'/selected-private.json'));
const template=packetTemplate({decisions:[
 {slot:'tcp',protocol:6,downTag:2399469568,flow:selected.tcp,validUntilUptime:0},
 {slot:'udp',protocol:17,downTag:2399535104,flow:selected.udp,validUntilUptime:0}
]},p.tagPlan.owner,selected.udp.original.sport===59999?59998:59999);
template.expected.nftables=template.expected.nftables.filter(x=>x.chain?.name!=='forward'&&x.rule?.chain!=='forward');
const input={...p,tagPlan:{...p.tagPlan,expected:template.expected}};
const read=name=>fs.readFileSync(name,'utf8');
const old=buildPayload(input,{qos:read('work/nss49/qos-physical.lua'),phase:read('work/nss63/core-guard-phase.lua'),classifier:read('work/nss53/classifier.lua'),tags:read('work/nss49/classified-tags.lua'),normalizer:read('work/nss49/tag-normalizer.lua')});
const digest=crypto.createHash('sha256').update(old.stagedCode).digest('hex');
assert.equal(digest,p.qosCodeSha256,'Refuse to diagnose a reconstructed bundle that differs from the actual failed bytes');
fs.writeFileSync('work/nss69/failed-bundle-private.lua',old.stagedCode,{flag:'wx'});
const lines=old.stagedCode.split('\n');
const runtime=JSON.parse(fs.readFileSync(dir+'/last-record-private.json'));
console.log(JSON.stringify({actualBundleSha256:digest,exactBundleMatched:true,failureContext:lines.slice(119,129).map((line,i)=>({line:120+i,text:line})),phaseCount:runtime.phases?.length??0,ecmOpened:runtime.fastPathEpochCompleted??false,cleanup:JSON.parse(fs.readFileSync(dir+'/stage-undo-verified.json')),baseline:JSON.parse(fs.readFileSync(dir+'/baseline-audit.json'))},null,2));
