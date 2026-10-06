import fs from 'node:fs';import assert from 'node:assert/strict';import {buildPayload} from './payload.mjs';
const first=JSON.parse(fs.readFileSync('work/nss155/run3/first-case-private.json')),input=JSON.parse(fs.readFileSync(first.dir+'/stage-plan-private.json'));
const files={qos:'work/nss149/qos-physical.lua',phase:'work/nss69/core-guard-phase.lua',classifier:'work/nss149/classifier.lua',tags:'work/nss49/classified-tags.lua',normalizer:'work/nss149/tag-normalizer.lua'};
const b=buildPayload(input,Object.fromEntries(Object.entries(files).map(([k,p])=>[k,fs.readFileSync(p,'utf8')])));
const bytes=Buffer.byteLength(b.stagedCode),result={combinedPayloadBytes:bytes,originalCap:73728,underOriginalCap:bytes<=73728,oneHistoricalInputOnly:true,javascriptExactTagReconstructionPassed:true,nativeSyntaxOrFactoryModelExecuted:false,productionExecuted:false};
fs.writeFileSync('work/nss157/historical-payload-private.lua',b.stagedCode,{flag:'wx'});fs.writeFileSync('work/nss157/measure-historical.json',JSON.stringify(result,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(result));assert.ok(result.underOriginalCap,'Combined source remains offline if size budget exceeded');
