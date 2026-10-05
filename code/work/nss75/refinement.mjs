import assert from 'node:assert/strict';
import {selectRealPair} from '../nss39/pair-policy.mjs';
import {canonicalSelection} from '../nss27/flow-selection.mjs';

// This occurs before the detached stage, tags, qdisc setup or ECM permit exists.
// Checkpoint protects the configuration; it does not grant a flow permission.
export function chooseAfterCheckpoint(frame,producer,sequence,originalGame){
 assert.equal(frame.producer,producer,'Classifier producer changed during preparation');
 assert.ok(Number.isSafeInteger(frame.sourceSequence)&&frame.sourceSequence>=sequence,'Classifier sequence moved backwards');
 const identity=JSON.stringify(originalGame);
 const pairs=selectRealPair(frame).filter(p=>JSON.stringify(canonicalSelection(p.g))===identity);
 assert.ok(pairs.length,'No current real application pair after checkpoint');
 return {tcp:canonicalSelection(pairs[0].b),udp:canonicalSelection(pairs[0].g)};
}

export function validateRefinement(before,after){
 const mutable=new Set(['selected','tagPlan','frozenHash','insmodArguments']);
 const fixed=x=>Object.fromEntries(Object.entries(x).filter(([k])=>!mutable.has(k)));
 assert.deepEqual(fixed(after),fixed(before),'Checkpoint refinement changed protected scope');
 const identity=x=>{const y=structuredClone(x);delete y.classifierKey;return y;};
 assert.deepEqual(identity(after.selected.udp),identity(before.selected.udp),'Game connection changed');
 if(after.selected.udp.classifierKey!==undefined)assert.equal(after.selected.udp.classifierKey,before.selected.udp.classifierKey);
 for(const k of ['wan','mark','zone'])assert.equal(after.selected.tcp[k],after.selected.udp[k],k+' changed');
 assert.equal(after.selected.tcp.protocol,6);assert.equal(after.selected.udp.protocol,17);
 assert.equal(after.selected.tcp.original.src,after.selected.udp.original.src);
 assert.equal(after.selected.tcp.reply.dst,after.selected.udp.reply.dst,'NAT address changed');
 assert.equal(after.tagPlan.owner,before.tagPlan.owner);assert.equal(after.tagPlan.table,before.tagPlan.table);assert.equal(after.tagPlan.mode,before.tagPlan.mode);
 assert.match(after.frozenHash,/^[a-f0-9]{64}$/);assert.ok(typeof after.insmodArguments==='string'&&after.insmodArguments.length<2048);
 return structuredClone(after);
}
