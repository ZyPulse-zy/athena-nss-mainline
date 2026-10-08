import fs from 'node:fs';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import vm from 'node:vm';
import {selectNormalCandidates} from './normal-policy.mjs';
import {selectNormalCandidates as originalSelect} from '../resident-normal-dev-c-20261008/normal-policy.mjs';
import {adaptNormalDriver} from './materialize-normal.mjs';
const root='work/resident-rc1-run-20261008040304-eda516d2',token='3d84d211-1581-4213-a47c-9c8336c0aa28';
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const failed=read(root+'/normal-frame-'+token+'-private.json');
const native=JSON.parse(read(root+'/normal-native-'+token+'-private.json').stdout);
native.sourceAge=failed.sourceAge;
const pc={...JSON.parse(read(root+'/normal-pc-'+token+'-private.json').stdout),ageSeconds:0.1};
const checks=[];
const old=originalSelect(structuredClone(native),structuredClone(pc));
assert.equal(old.pairs.length,0);assert.deepEqual([...new Set(old.tcp.map(f=>f.identity.wan))],[4]);checks.push('actual four-fastest-WAN4 omission reproduced from original complete frame and OS records');
const next=selectNormalCandidates(structuredClone(native),structuredClone(pc));
assert.ok(next.pairs.length>0);assert.ok(new Set(next.tcp.map(f=>f.identity.wan)).size>1);checks.push('same current eligible full frame preserves distinct natural WAN candidates');
assert.ok(next.tcp.length<=4&&next.udp.length<=1&&next.pairs.length<=12);checks.push('original candidate and three-slot admission bounds unchanged');
for(const f of next.tcp){const same=old.flows.filter(x=>x.identity.wan===f.identity.wan&&x.decision.class==='BULK');assert.ok(same.every(x=>(x.decision.rateKbps??0)<=(f.decision.rateKbps??0)));}
checks.push('strongest verified flow retained per represented WAN');
assert.equal(next.sourceSequence,old.sourceSequence);assert.equal(next.sourceAge,old.sourceAge);assert.deepEqual(next.owners,old.owners);assert.deepEqual(next.udp,old.udp);checks.push('source identity, exact OS owners and original RT selection preserved');
const one=structuredClone(native);one.flows=one.flows.filter(f=>f.identity.protocolNumber===17||f.identity.wan===4);
assert.ok(selectNormalCandidates(one,structuredClone(pc)).pairs.length);checks.push('one natural BULK WAN qualifies independently');
const unknown=structuredClone(native);for(const f of unknown.flows)if(f.identity.protocolNumber===6&&f.identity.wan!==4)f.decision.class='BE';
const filtered=selectNormalCandidates(unknown,structuredClone(pc));assert.ok(filtered.pairs.length);assert.ok(filtered.pairs.every(p=>[p.tcp,p.tcp2].filter(Boolean).every(f=>f.wan===4)));checks.push('BE is excluded while other qualified flows remain usable');
// Execute the actual adapted driver's initial empty-pair branch in a filesystem
// sandbox. Any session mkdir, network connection or checkpoint call is fatal.
const original=fs.readFileSync('work/resident-rc1-run-20261007163534-ae83fa69/epoch-driver.mjs','utf8');
const adapted=adaptNormalDriver(original).replace(/^import[^\n]*\n/gm,'').replace('export async function runEpoch','async function runEpoch');
const writes=new Map(),scope='MODEL_SCOPE',sha=crypto.createHash('sha256').update(scope).digest('hex');
const files={
 'work/nss49/mainline-preflight-qualified.json':JSON.stringify({passed:true,phasedIntegration:true}),
 'work/nss27/wan-scope-qualified.json':JSON.stringify({passed:true,sourceSha256:sha}),
 'work/nss49/wan-scope.lua':scope
};
const sandbox={assert,crypto,verifyPreparation:()=>{},console:{log:()=>{}},process:{execPath:'model'},
 fs:{readFileSync:p=>{if(p.endsWith('/controlled-candidates-private.json'))return JSON.stringify({pairs:[],tcp:[],udp:[],sourceSequence:7,sourceAge:1});assert.ok(p in files,p);return files[p];},writeFileSync:(p,v)=>writes.set(p,JSON.parse(v)),mkdirSync:()=>{throw new Error('Empty candidate must not create stage/session');}},
 spawnSync:()=>({status:0,stderr:'',stdout:''}),connectRouter:()=>{throw new Error('Empty candidate must not connect');},beginStage:()=>{throw new Error('Empty candidate must not begin checkpoint');}};
const result=await vm.runInNewContext(adapted+"\nrunEpoch('model',()=>{},false)",sandbox);
assert.equal(result,undefined);assert.equal(writes.size,2);assert.ok([...writes].some(([p,v])=>p.endsWith('/driver-initial-no-candidate-private.json')&&v.beforeCheckpoint===true&&v.routerWrites===false&&v.sourceSequence===7));
checks.push('actual adapted driver emits a pre-checkpoint witness without session, router connection or checkpoint');
console.log(JSON.stringify({passed:true,checks:checks.length,names:checks,routerAccess:false,modelOnly:true,actualFailedFrameReplayed:true}));
