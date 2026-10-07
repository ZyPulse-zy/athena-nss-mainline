import assert from'node:assert/strict';
import{canonicalSelection}from'../nss27/flow-selection.mjs';
import{selectNormalTriple,rankExistingBulk}from'./normal-policy.mjs';
// Only before the detached owner exists. All lists are the original exact
// Steam/CS2 socket-owned candidates; the established selector checks class leases.
export function selectAnchoredTriple(frame,originalGame,wanSlots){
 assert.equal(originalGame.protocol,17);
 const same=f=>JSON.stringify(canonicalSelection(f))===JSON.stringify(originalGame);
 const game=frame.game.filter(same);
 if(!game.length)return[];
 if(!wanSlots)return selectNormalTriple({...frame,game});
 assert.notEqual(wanSlots.tcp,wanSlots.tcp2);
 const ranked=rankExistingBulk(frame.bulk);
 const first=ranked.filter(f=>f.identity.wan===wanSlots.tcp);
 const second=ranked.filter(f=>f.identity.wan===wanSlots.tcp2);
 for(const a of first)for(const b of second){
  const triples=selectNormalTriple({...frame,game,bulk:[a,b]});
  if(triples.length){
   const s=triples[0];
   if(s.tcp.wan===wanSlots.tcp2&&s.tcp2.wan===wanSlots.tcp)return[{...s,tcp:s.tcp2,tcp2:s.tcp}];
   assert.equal(s.tcp.wan,wanSlots.tcp);assert.equal(s.tcp2.wan,wanSlots.tcp2);return triples;
  }
 }
 return[];
}
