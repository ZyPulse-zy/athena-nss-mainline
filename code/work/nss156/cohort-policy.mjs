import assert from 'node:assert/strict';
export function cohortPorts(start,number){assert.ok(Number.isInteger(start)&&start>=57000&&start<57800);assert.ok(number===0||number===1);return Array.from({length:4},(_,i)=>start+number*4+i)}
export function validateChosen(port,available){assert.ok(Number.isInteger(port)&&available.includes(port),'Only an authenticated owned cohort port can be chosen');return port}
