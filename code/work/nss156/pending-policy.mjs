import assert from 'node:assert/strict';
export function nextPendingPort({start,port,authenticated,elapsedMs,failed=false}){
 assert.ok(Number.isInteger(start)&&Number.isInteger(port)&&port>=start&&port<start+8);
 assert.equal(typeof authenticated,'boolean');assert.equal(typeof failed,'boolean');assert.ok(Number.isFinite(elapsedMs)&&elapsedMs>=0);
 if(authenticated)return null;
 if(!failed&&elapsedMs<5500)return null;
 assert.ok(port+1<start+8,'Original eight pending TCP candidates exhausted');return port+1;
}
