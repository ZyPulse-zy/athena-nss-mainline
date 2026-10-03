import fs from'node:fs';import assert from'node:assert/strict';import crypto from'node:crypto';
const root='work/nss38',old=fs.readFileSync('work/nss37/classifier.lua','utf8');let next=old;
export const replacements=[
 [' local function current()',' local function readContext()'],
 ['  Consumer.inspect(s,c,now());return s,c','  return s,c'],
 [' local epoch\n'," -- Hot readers perform the full inspection once, immediately before deciding.\n -- Renewal and retirement retain their existing validated-current contract.\n local function current()\n  local s,c=readContext();Consumer.inspect(s,c,now());return s,c\n end\n local epoch\n"],
 ['  local s,c=current();local checked=Consumer.inspect(s,c,now())','  local s,c=readContext();local checked=Consumer.inspect(s,c,now())'],
 ['local ok,result=pcall(function()local s,c=current();local e=Consumer.pair(s,c,now(),P.selected);','local ok,result=pcall(function()local s,c=readContext();local e=Consumer.pair(s,c,now(),P.selected);'],
];
for(const[a,b]of replacements){assert.equal(next.split(a).length,2,a);next=next.replace(a,()=>b);}
fs.writeFileSync(root+'/candidate-classifier.lua',next);const hash=s=>crypto.createHash('sha256').update(s).digest('hex');
fs.writeFileSync(root+'/candidate-adapter-manifest.json',JSON.stringify({onlyRedundantReadyAndObserveInspectionRemoved:true,renewalRetirementAndSamplingContractsPreserved:true,oldSha256:hash(old),newSha256:hash(next),permanentClassifierChanged:false,nssOpened:false},null,2)+'\n');
console.log(JSON.stringify({built:true,sourceSha256:hash(next),routerWrites:false}));
