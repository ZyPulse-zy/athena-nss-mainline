// Derive a controlled physical-WAN tag from the current BULK/RT classification.
// Resident publication upTag=0 is preserved; it is not claimed to supply this tag.
import assert from 'node:assert/strict';
import {packetTemplate as original} from '../nss16/automatic-leaf-plan.mjs';
export function packetTemplate(decision,owner,neighborPort){
 const p=original(decision,owner,neighborPort);const tags={tcp:0x8e050000,udp:0x8e060000};
 for(const object of p.expected.nftables){const r=object.rule;if(!r)continue;const name=r.comment.slice(owner.length+1);if(name.includes('neighbor'))continue;
  const slot=name.startsWith('tcp_')?'tcp':name.startsWith('udp_')?'udp':null;assert.ok(slot);
  if(!name.includes('_up'))continue;
  for(const e of r.expr){if(e.mangle?.key.meta?.key==='priority'){assert.equal(e.mangle.value,0);e.mangle.value=tags[slot];}
   if(e.match?.left.meta?.key==='priority'){assert.equal(e.match.right,0);e.match.right=tags[slot];}}
 }
 p.batch={nftables:p.expected.nftables.map((x,i)=>({[i===0?'create':'add']:x}))};
 return p;
}
