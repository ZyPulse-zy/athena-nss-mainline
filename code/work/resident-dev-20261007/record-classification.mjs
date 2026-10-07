import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
export function createClassificationFrameWriter(){
 const invocation=crypto.randomUUID();let sequence=0;
 return function writeFrame(root,out){
  assert.match(root,/^work\/resident-rc1-run-\d{14}-[a-f0-9]{8}$/);
  const bytes=JSON.stringify(out,null,2)+'\n';
  assert.ok(Buffer.byteLength(bytes)<=1048576,'Original record byte ceiling');
  const file=root+'/classification-read-'+invocation+'-'+String(++sequence).padStart(4,'0')+'-private.json';
  fs.writeFileSync(file,bytes,{flag:'wx'});
  fs.writeFileSync(root+'/controlled-candidates-private.json',bytes);
  return file;
 };
}
export function findExistingSelection(pairs,selected){
 assert.ok(Array.isArray(pairs)&&pairs.length<=12&&selected&&Object.keys(selected).length===3);
 const original=JSON.stringify(selected),matches=pairs.filter(p=>JSON.stringify(p)===original);
 assert.ok(matches.length<=1,'Duplicate selected identity');
 return matches[0];
}
