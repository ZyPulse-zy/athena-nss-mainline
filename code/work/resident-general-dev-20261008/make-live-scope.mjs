import fs from'node:fs';import crypto from'node:crypto';import assert from'node:assert/strict';import{readNormalCandidates}from'../resident-normal-dev-h-20261008/normal-reader.mjs';import{pinNormalOwnership}from'../resident-normal-dev-h-20261008/normal-policy.mjs';
const root='work/resident-normal-observe-'+new Date().toISOString().replace(/\D/g,'').slice(0,14)+'-'+crypto.randomBytes(4).toString('hex');fs.mkdirSync(root);
const frame=await readNormalCandidates(root);assert.ok(frame.pairs.length,'No live owned eligible flow for bounded integration');
const pair=frame.pairs[0],slot=pair.udp?'udp':'tcp',selected={[slot]:pair[slot]},owners=Object.values(pinNormalOwnership(frame,selected));
const scope={version:1,owners,tcp:slot==='tcp'?[selected.tcp.original]:[],udp:slot==='udp'?[selected.udp.original]:[]};
const dir='work/resident-normal-session-'+new Date().toISOString().replace(/\D/g,'').slice(0,14)+'-'+crypto.randomBytes(4).toString('hex');fs.mkdirSync(dir);fs.writeFileSync(dir+'/scope-private.json',JSON.stringify(scope,null,2)+'\n',{flag:'wx'});
fs.writeFileSync('work/resident-general-dev-20261008/integration-source-private.json',JSON.stringify({dir,observationRoot:root,selected,sourceSequence:frame.sourceSequence,sourceAge:frame.sourceAge,trafficGenerated:false},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({scope:dir+'/scope-private.json',activeSlot:slot,wan:selected[slot].wan,trafficGenerated:false,desktopOperated:false}));
