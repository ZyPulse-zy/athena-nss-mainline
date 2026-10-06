import assert from 'node:assert/strict';
export function validateServerReady(x){assert.deepEqual(x,{event:'ready',rateBytesPerSecond:4000000,creditBytes:65536,maximumSeconds:180});}
export function nextPort(base,current,selected){assert.equal(selected,null);assert.ok(Number.isInteger(base)&&Number.isInteger(current)&&base>=57000&&base+7<=65535&&current>=base&&current<base+7);return current+1;}
export function canReplaceSender(code,receipt){assert.equal(code,0);assert.equal(receipt?.event,'closed');assert.equal(receipt.reason,'owned-stop');assert.equal(receipt.serverStopped,true);assert.ok(Number.isSafeInteger(receipt.bytes)&&receipt.bytes>=0&&receipt.bytes<=1073741824);return true;}
