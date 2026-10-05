import assert from 'node:assert/strict';
import {selectRealPair} from '../nss39/pair-policy.mjs';
import {canonicalSelection} from '../nss27/flow-selection.mjs';
const key=f=>JSON.stringify(canonicalSelection(f));
export function selectPersistentRealPair(initial,current,originalGame){
 assert.equal(current.producer,initial.producer,'Classifier producer changed during preparation');
 assert.ok(Number.isSafeInteger(current.sourceSequence)&&current.sourceSequence>=initial.sourceSequence,'Classifier sequence moved backwards');
 const bulk=new Set(initial.bulk.map(key)),game=new Set(initial.game.map(key));
 const gameKey=JSON.stringify(originalGame);
 return selectRealPair(current).filter(p=>bulk.has(key(p.b))&&game.has(key(p.g))&&key(p.g)===gameKey);
}
