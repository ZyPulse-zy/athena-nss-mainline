import fs from 'node:fs';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
const root='work/v57-run-20261007132518-89cdd084',dir=process.argv[2],config=JSON.parse(fs.readFileSync(dir+'/client-config-private.json'));
assert.ok(dir.startsWith(root+'/load-'));assert.equal(config.seconds,180);assert.equal(config.pps,50);
const trials=[];
for(const [exe,prefix] of [['python',['-u',root+'/udp-probe.py']],
  [process.execPath,[root+'/udp-probe.mjs']],
  [process.execPath,[root+'/udp-probe.mjs']]]){
 const mode=trials.length===1?'connected':'unconnected',c={...config,probeBaseSequence:10000*(trials.length+1)};
 const args=[...prefix,JSON.stringify(c),...(exe==='python'?[]:[mode])];
 const p=spawnSync(exe,args,{encoding:'utf8',windowsHide:true,timeout:4000,maxBuffer:65536});
 const record={code:p.status,stdout:p.stdout,stderr:p.stderr,error:p.error?.code??null};
 fs.writeFileSync(dir+'/udp-path-'+trials.length+'-raw-private.json',JSON.stringify(record,null,2)+'\n',{flag:'wx'});
 assert.equal(p.status,0,'Owned UDP probe failed; original output retained');trials.push(JSON.parse(p.stdout));
}
const result={passed:trials.every(t=>t.sent===20&&t.received>0&&t.nonceVerified),trials,
  sameFixedTupleAndNonce:true,disjointSequenceRanges:true,noNssWrites:true,noFirewallOrPbrChanges:true};
fs.writeFileSync(dir+'/udp-path-preflight.json',JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify(result));assert.ok(result.passed,'Actual UDP echo is required before TCP client and NSS admission');
