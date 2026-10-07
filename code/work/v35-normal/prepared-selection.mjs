// This helper runs only before beginStage and before any WAN scope is frozen.
import assert from 'node:assert/strict';
import {canonicalSelection} from '../nss27/flow-selection.mjs';
import {selectAnchoredTriple} from './normal-selection.mjs';

export function selectPreparedTriple(frame,originalGame,prepared,reference){
 assert.ok(Array.isArray(prepared)&&prepared.length>=1&&prepared.length<=5);
 assert.equal(typeof reference.boot,'string');
 assert.ok(Number.isSafeInteger(reference.stateMajor)&&reference.stateMajor>0);
 const byWan=new Map();
 for(const q of prepared){assert.ok(Number.isSafeInteger(q.wan)&&q.wan>=1&&q.wan<=5);assert.ok(!byWan.has(q.wan));byWan.set(q.wan,q);}
 const usable=f=>{
  try{
   const identity=canonicalSelection(f),q=byWan.get(identity.wan);
   return Boolean(q&&q.boot===reference.boot&&q.stateMajor===reference.stateMajor&&q.status?.up===true&&
    q.status.l3_device==='rpwan'+identity.wan&&q.status['ipv4-address']?.[0]?.address===identity.reply.dst);
  }catch{return false;}
 };
 return selectAnchoredTriple({...frame,bulk:frame.bulk.filter(usable),game:frame.game.filter(usable)},originalGame);
}
