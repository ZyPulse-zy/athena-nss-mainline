import assert from'node:assert/strict';
// Count server-confirmed delivery, not bytes submitted to the local SSH stream.
export function uploadAck(previous,text){
 const x=JSON.parse(text);assert.deepEqual(Object.keys(x),['received']);
 assert.ok(Number.isSafeInteger(x.received)&&x.received>=previous&&x.received<=1024*1024*1024,'Invalid remote delivery counter');return x.received;
}
