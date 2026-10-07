// Only the new initial-selection boundary is modeled. The factory is not run.
import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {selectPreparedTriple} from './prepared-selection.mjs';
const root='work/v37-sim',prior='work/v33-normal/session-20261007025747-bf198fc4';
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const frame=read(prior+'/refusal-controlled-candidates-private.json');
const original=read(prior+'/persistent-selection-private.json').selected;
const reference={boot:'model-native-boot',stateMajor:42};
const wans=new Map();
for(const f of [...frame.game,...frame.bulk]){
 const w=f.identity.wan,ip=f.identity.reply.dst;
 if(wans.has(w))assert.equal(wans.get(w).status['ipv4-address'][0].address,ip);
 wans.set(w,{wan:w,...reference,status:{up:true,l3_device:'rpwan'+w,'ipv4-address':[{address:ip}]}});
}
const prepared=[...wans.values()],clone=structuredClone;
let checks=0;
const pass=()=>{checks++;};
assert.equal(selectPreparedTriple(frame,original.udp,prepared,reference).length,1);pass();
const changed=clone(original.udp);changed.id++;assert.equal(selectPreparedTriple(frame,changed,prepared,reference).length,0);pass();
const noGameWan=prepared.filter(q=>q.wan!==original.udp.wan);assert.equal(selectPreparedTriple(frame,original.udp,noGameWan,reference).length,0);pass();
for(const mutate of [
 q=>q.status['ipv4-address'][0].address='192.0.2.1',
 q=>q.boot='other-boot',q=>q.stateMajor++,q=>q.status.up=false,
 q=>q.status.l3_device='wrong-interface']){
 const bad=clone(prepared);bad.forEach(mutate);assert.equal(selectPreparedTriple(frame,original.udp,bad,reference).length,0);pass();
}
assert.throws(()=>selectPreparedTriple(frame,original.udp,[prepared[0],prepared[0]],reference));pass();
assert.throws(()=>selectPreparedTriple(frame,original.udp,Array(6).fill(prepared[0]),reference));pass();
const singleWan=prepared.filter(q=>q.wan===original.udp.wan);assert.equal(selectPreparedTriple(frame,original.udp,singleWan,reference).length,0);pass();
const badMark=clone(frame);badMark.bulk.forEach(f=>f.identity.mark^=0x10000);assert.equal(selectPreparedTriple(badMark,original.udp,prepared,reference).length,0);pass();
const missingBulk=clone(frame);missingBulk.bulk=[];assert.equal(selectPreparedTriple(missingBulk,original.udp,prepared,reference).length,0);pass();
assert.equal(checks,13);
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const sourceHashes=Object.fromEntries(['prepared-selection.mjs','model-prepared-selection.mjs'].map(n=>[root+'/'+n,hash(fs.readFileSync(root+'/'+n))]));
fs.writeFileSync(root+'/prepared-selection-qualified.json',JSON.stringify({passed:true,modelOnly:true,checks,
 actualV33RefusalFrameReused:true,nativePrerequisitesModeledOnly:true,hardwareExecuted:false,
 normalFactoryExecuted:false,networkReads:0,routerWrites:0,sourceHashes},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({passed:true,checks,actualFrozenRefusalFrameUsed:true,nativePrerequisitesModelOnly:true,hardwareExecuted:false}));
