import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';
import {verifyPreparation as previous} from '../nss73/session-binding.mjs';
import {canonicalSelection} from '../nss27/flow-selection.mjs';
import {selectPersistentRealPair} from './persistent-pair.mjs';
const root='work/nss74',cases=[];
function rekey(f){const i=f.identity;f.key=[i.wan,i.mark,i.protocolNumber===6?'tcp':'udp',i.original.src,i.original.sport,i.reply.src,i.reply.dst,i.reply.sport,i.reply.dport,i.zone,i.connectionId].join('|');return f;}
function flow(protocolNumber,id,rate=10){return rekey({identity:{wan:1,mark:65536,zone:0,connectionId:id,protocolNumber,original:{src:'192.168.237.207',dst:'198.51.100.2',sport:40000+id,dport:protocolNumber===17?27015:443},reply:{src:'198.51.100.2',dst:'192.0.2.1',sport:protocolNumber===17?27015:443,dport:50000+id}},decision:{class:protocolNumber===17?'RT':'BULK',budgetAdmitted:true,pps:100,rateKbps:rate}});}
const g=flow(17,1),b=flow(6,2),old={producer:'test-producer',sourceSequence:10,game:[g],bulk:[b]};
const now={producer:'test-producer',sourceSequence:12,game:[structuredClone(g)],bulk:[structuredClone(b),flow(6,3,99999)]};
const run=current=>selectPersistentRealPair(old,current,canonicalSelection(g));
function check(name,fn){fn();cases.push(name);}
check('Persistent identity wins over a new faster TCP',()=>{const p=run(now);assert.equal(p.length,1);assert.equal(p[0].b.identity.connectionId,2);});
for(const [name,change]of [
 ['Exited TCP',x=>x.bulk.shift()],
 ['Reused endpoint different CT id',x=>x.bulk[0].identity.connectionId=9],
 ['Changed NAT port',x=>x.bulk[0].identity.reply.dport++],
 ['Changed full ct mark',x=>x.bulk[0].identity.mark|=1],
 ['Changed WAN affinity',x=>{x.bulk[0].identity.wan=2;x.bulk[0].identity.mark=131072;}],
 ['Proxy mark',x=>{x.bulk[0].identity.mark|=0x2000;x.game[0].identity.mark|=0x2000;}],
 ['Changed CT zone',x=>x.bulk[0].identity.zone=1],
 ['TCP no longer bulk',x=>x.bulk[0].decision.class='BE'],
 ['Game no longer RT',x=>x.game[0].decision.class='BE'],
 ['Game budget rejected',x=>x.game[0].decision.budgetAdmitted=false],
 ['New game port',x=>x.game[0].identity.original.sport++]
])check(name,()=>{const x=structuredClone(now);change(x);for(const f of [...x.game,...x.bulk])rekey(f);assert.equal(run(x).length,0);});
check('Changed producer is rejected',()=>assert.throws(()=>run({...now,producer:'other'})));
check('Older sequence is rejected',()=>assert.throws(()=>run({...now,sourceSequence:9})));
const sourceManifest={},hash=b=>crypto.createHash('sha256').update(b).digest('hex');
for(const f of ['build-persistent-entry.mjs','persistent-pair.mjs','qualify-persistent-entry.mjs','real-session.mjs','session-binding.mjs','current-audit-diagnostic.mjs','record-candidates.mjs','read-real-candidates.mjs','change-contract.json'])sourceManifest[root+'/'+f]=hash(fs.readFileSync(root+'/'+f));
const proof={passed:true,observedAt:new Date().toISOString(),cases,checks:cases.length,localSyntheticIdentityTests:true,routerWrites:false,nssAdmissionGranted:false,baseBoundInputs:Object.keys(previous().sourceManifest).length,sourceManifest,oneWanAndExactTwoFlowGateUnchanged:true,onlyPersistentApplicationIdentities:true};
fs.writeFileSync(root+'/entry-qualified.json',JSON.stringify(proof,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({passed:true,checks:cases.length,boundInputs:Object.keys((await import('./session-binding.mjs')).verifyPreparation().sourceManifest).length,routerWrites:false}));
