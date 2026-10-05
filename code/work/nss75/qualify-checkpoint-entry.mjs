import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';
import {verifyPreparation as previous} from '../nss74/session-binding.mjs';
import {chooseAfterCheckpoint,validateRefinement} from './refinement.mjs';
import {canonicalSelection} from '../nss27/flow-selection.mjs';
import {buildPayload} from '../nss73/payload.mjs';
import {packetTemplate} from '../nss16/automatic-leaf-plan.mjs';
const root='work/nss75',cases=[];
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
function flow(protocolNumber,id){const identity={wan:1,mark:65536,zone:0,connectionId:id,protocolNumber,original:{src:'192.168.237.207',dst:'198.51.100.2',sport:40000+id,dport:protocolNumber===17?27015:443},reply:{src:'198.51.100.2',dst:'192.0.2.1',sport:protocolNumber===17?27015:443,dport:50000+id}};return {identity,key:[1,65536,protocolNumber===6?'tcp':'udp',identity.original.src,identity.original.sport,identity.reply.src,identity.reply.dst,identity.reply.sport,identity.reply.dport,0,id].join('|'),decision:{class:protocolNumber===17?'RT':'BULK',budgetAdmitted:true,pps:100,rateKbps:1000}};}
const g=flow(17,1),b=flow(6,2),frame={producer:'fixture-producer',sourceSequence:30,game:[g],bulk:[b]};
const selected={udp:canonicalSelection(g),tcp:canonicalSelection(b)};
const base={mode:'stage',openFrontend:true,autoClassified:true,qosDevice:'lan4',qosStaged:true,qosBoot:'fixture-boot',wanPrerequisites:{wan:1,boot:'fixture-boot'},selected:structuredClone(selected),tagPlan:{owner:'a'.repeat(32),table:'fixture',mode:'rt',expected:{nftables:[]}},frozenHash:'b'.repeat(64),insmodArguments:'register_gate=1',classifierOwner:{base:'fixture',configSha256:'c'.repeat(64)}};
base.selected.udp.classifierKey=g.key;base.selected.tcp.classifierKey=b.key;
function check(name,fn){fn();cases.push(name);}
check('Current app-owned TCP may replace provisional before stage',()=>{const x={...frame,bulk:[flow(6,4)]};assert.equal(chooseAfterCheckpoint(x,frame.producer,29,selected.udp).tcp.id,4);});
for(const [name,change]of [['No TCP',x=>x.bulk=[]],['No game',x=>x.game=[]],['Unclassified TCP',x=>x.bulk[0].decision.class='BE'],['Unadmitted game',x=>x.game[0].decision.budgetAdmitted=false],['Changed producer',x=>x.producer='changed'],['Older source',x=>x.sourceSequence=28],['Wrong NAT address',x=>x.bulk[0].identity.reply.dst='192.0.2.4'],['Changed game connection',x=>{x.game[0]=flow(17,8);}]])check(name,()=>{const x=structuredClone(frame);change(x);assert.throws(()=>chooseAfterCheckpoint(x,frame.producer,29,selected.udp));});
const next=structuredClone(base);next.selected={udp:selected.udp,tcp:canonicalSelection(flow(6,4))};next.frozenHash='d'.repeat(64);next.insmodArguments='register_gate=1 tcp_ct_id_raw=4';
check('Exact scope accepts before-stage TCP refinement',()=>assert.deepEqual(validateRefinement(base,next),next));
for(const [name,change]of [['Game changed',x=>x.selected.udp.id++],['WAN changed',x=>x.selected.tcp.wan=2],['Full mark changed',x=>x.selected.tcp.mark++],['NAT changed',x=>x.selected.tcp.reply.dst='192.0.2.4'],['Queue device changed',x=>x.qosDevice='lan1'],['Queue owner changed',x=>x.tagPlan.owner='f'.repeat(32)],['Table changed',x=>x.tagPlan.table='other'],['Source scope changed',x=>x.classifierOwner.configSha256='e'.repeat(64)],['Stage field injection',x=>x.extraPrivilege=true]])check(name,()=>{const x=structuredClone(next);change(x);assert.throws(()=>validateRefinement(base,x));});
const stage=fs.readFileSync(root+'/module-stage.mjs','utf8'),entry=fs.readFileSync(root+'/real-session.mjs','utf8');
check('Final selection occurs after downloaded SHA and gzip checkpoint',()=>assert.ok(stage.indexOf('zlib.gunzipSync(bytes)')<stage.indexOf('await finalizeSelection(')));
check('Selection still precedes stage guardian first write',()=>assert.ok(stage.indexOf('await finalizeSelection(')<stage.indexOf("save(dir,'stage-guardian-raw-private'")));
check('Guardian source and deadlines unchanged',()=>{assert.ok(stage.includes("work/nss49/module-stage-guardian.lua"));assert.ok(!stage.includes('nanosleep('));assert.ok(stage.includes("plan.qosCodeBytes<=73728"));assert.ok(entry.includes('await uploadStage(context)'));});
check('Final selected flow is frozen exactly once',()=>{assert.ok(entry.includes("frozen-private.json',frozen,{flag:'wx'}"));assert.ok(entry.includes('chooseAfterCheckpoint(frame'));});
const prior=JSON.parse(fs.readFileSync('work/nss74/real-matched-aba-20261005052526-2a557970/stage-plan-private.json'));
const libs=Object.fromEntries([['qos','work/nss49/qos-physical.lua'],['phase','work/nss69/core-guard-phase.lua'],['classifier','work/nss73/classifier.lua'],['tags','work/nss49/classified-tags.lua'],['normalizer','work/nss49/tag-normalizer.lua']].map(([k,p])=>[k,fs.readFileSync(p,'utf8')]));
// The live plan stores only the compact table identity; the actual packed tag
// policy is taken from a preserved full input and rebuilt by the normal helper.
const oldDir='work/nss74/real-matched-aba-20261005052526-2a557970';
const oldBundle=fs.readFileSync(oldDir+'/frozen/work/nss73/payload.mjs','utf8');
check('Payload builder is the exact qualified NSS73 helper',()=>assert.equal(oldBundle,fs.readFileSync('work/nss73/payload.mjs','utf8')));
check('Actual frozen policy rebuild has exact previous bundle SHA',()=>{
 const s=JSON.parse(fs.readFileSync(oldDir+'/selected-private.json'));
 const t=packetTemplate({decisions:[{slot:'tcp',protocol:6,downTag:2399469568,flow:s.tcp,validUntilUptime:0},{slot:'udp',protocol:17,downTag:2399535104,flow:s.udp,validUntilUptime:0}]},prior.tagPlan.owner,s.udp.original.sport===59999?59998:59999);
 t.expected.nftables=t.expected.nftables.filter(x=>x.chain?.name!=='forward'&&x.rule?.chain!=='forward');
 const tagPlan={table:t.expected.nftables[0].table.name,owner:prior.tagPlan.owner,mode:'rt',expected:t.expected};
 const built=buildPayload({tagPlan},libs);assert.equal(Buffer.byteLength(built.stagedCode),prior.qosCodeBytes);assert.equal(hash(built.stagedCode),prior.qosCodeSha256);
 assert.ok(Buffer.byteLength(built.stagedCode)<=73728);assert.equal(prior.moduleSha256,'2926791b561bbc90494210f9c77335ece7779f0183bc95457e4ffd9761ca083a');
});
const sourceManifest={};for(const f of ['build-checkpoint-entry.mjs','refinement.mjs','qualify-checkpoint-entry.mjs','module-stage.mjs','real-session.mjs','session-binding.mjs','current-audit-diagnostic.mjs','record-candidates.mjs','read-real-candidates.mjs','change-contract.json'])sourceManifest[root+'/'+f]=hash(fs.readFileSync(root+'/'+f));
const proof={passed:true,observedAt:new Date().toISOString(),checks:cases.length,cases,localSyntheticIdentityAndControllerTests:true,routerWrites:false,nssAdmissionGranted:false,beforeStageOnly:true,nativeGateUnchanged:true,checkpointBeforeFinalSelection:true,guardedActualBundleCompilationRequired:true,baseBoundInputs:Object.keys(previous().sourceManifest).length,sourceManifest};
fs.writeFileSync(root+'/entry-qualified.json',JSON.stringify(proof,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({passed:true,checks:cases.length,boundInputs:Object.keys((await import('./session-binding.mjs')).verifyPreparation().sourceManifest).length,routerWrites:false}));
