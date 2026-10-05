// Credit is bounded across SSH channel stalls; no elapsed-time send debt.
import assert from 'node:assert/strict';
export function createPacer(startMs,bytesPerSecond){
 assert.ok(Number.isFinite(startMs)&&startMs>=0&&Number.isFinite(bytesPerSecond)&&bytesPerSecond>0);
 let last=startMs,credit=0;const cap=65536,chunk=16384;
 return{next(nowMs,blocked=false){assert.ok(Number.isFinite(nowMs)&&nowMs>=last);credit=Math.min(cap,credit+(nowMs-last)*bytesPerSecond/1000);last=nowMs;if(blocked||credit<chunk)return false;credit-=chunk;return true;},maximumCreditBytes:cap,chunkBytes:chunk};
}
