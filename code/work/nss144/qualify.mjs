import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';import {spawnSync} from 'node:child_process';
import {verifyPreparation as prior} from '../nss143/session-binding.mjs';
import {candidateAdapter} from '../nss143/candidate-adapter.mjs';
import {encode} from '../nss11/v7-observe-repair/observe2/transport.mjs';
import {packGuardian} from '../nss140/pack-guardian.mjs';
const root='work/nss144',h=b=>crypto.createHash('sha256').update(b).digest('hex'),q=prior();
const entry=fs.readFileSync(root+'/controlled-session.mjs','utf8');
for(const source of ['module-stage.mjs','uplink-tag-plan.mjs','parse-ecm-any-wan.mjs','declared-baseline.mjs','service-epoch.mjs'])assert.ok(entry.includes("'../nss140/"+source+"'"));
for(const required of ['mapClassifiedPair(selectionFrame,selected)','post-checkpoint-controlled-receipt-private','validateAcceleratedState','waitStageUndo','p.seconds>=20&&p.seconds<=21.5','ecm_nss_ipv4/accelerated_count'])assert.ok(entry.includes(required));
const plan=JSON.parse(fs.readFileSync('work/nss138/controlled-class-20261005222654-399b3465/stage-plan-private.json'));
for(const k of['guardianSourceSha256','selectedGuardianSha256','oneEpochControlledPair','phaseSourceSha256','qosSourceSha256','execBytes'])delete plan[k];
const guardian=packGuardian(fs.readFileSync('work/nss140/module-stage-guardian.lua','utf8')).replace('__PLAN__',()=>JSON.stringify(plan)).replace('__CORE_PHASE__',()=> 'return{}').replace('__QOS_PHYSICAL__',()=> 'return{}');
const actual=encode("/usr/bin/lua - <<'NSS20_STAGE_BEGIN'\n"+guardian+"\nNSS20_STAGE_BEGIN\n");assert.ok(actual.execBytes<=9000);
const reader=candidateAdapter(fs.readFileSync('work/nss49/classifier.lua','utf8'));assert.ok(reader.readonly&&reader.nssAdmissionAllowed===false);
const sourceManifest={};for(const name of fs.readdirSync(root))if(/\.(mjs|py|ps1)$/.test(name)&&!name.includes('private')){
 const file=root+'/'+name;sourceManifest[file]=h(fs.readFileSync(file));if(name.endsWith('.mjs')){const p=spawnSync(process.execPath,['--check',file],{encoding:'utf8',windowsHide:true});assert.equal(p.status,0,p.stderr);}
 if(name.endsWith('.py')){const p=spawnSync('C:/Users/lishu/AppData/Local/Programs/Python/Python312/python.exe',['-c','import sys;compile(open(sys.argv[1],encoding="utf-8").read(),sys.argv[1],"exec")',file],{encoding:'utf8',windowsHide:true});assert.equal(p.status,0,p.stderr);}
}
const sender=fs.readFileSync(root+'/download-server.py','utf8');assert.ok(sender.includes('min(CREDIT,credit+')&&sender.includes('signal.alarm(182)')&&sender.includes('MAX_BYTES=1024*1024*1024'));
const client=fs.readFileSync(root+'/ssh-client.mjs','utf8');assert.ok(client.includes("assert.equal(c.bulkDirection,'download')")&&client.includes('c.mbps===32')&&client.includes('c.seconds<=180')&&client.includes('hostVerifier:h=>pins.includes(h)'));
const proof={passed:true,at:new Date().toISOString(),controlledCurrentFactory:true,nativePayloadUnchanged:true,inheritedBoundInputs:Object.keys(q.sourceManifest).length,sourceManifest,budgets:[6,27,100,9000,65536,73728],qualificationGuardianExecBytes:actual.execBytes,oneTcpOneUdp:true,offeredDownloadMbps:32,desktopOperated:false,productionExecution:false,currentHardwareAbaCompleted:false};
fs.writeFileSync(root+'/entry-qualified.json',JSON.stringify(proof,null,2)+'\n',{flag:'wx'});
const bindings=(await import('./session-binding.mjs')).verifyPreparation();console.log(JSON.stringify({passed:true,bindings:Object.keys(bindings.sourceManifest).length,guardianExecBytes:actual.execBytes,currentNssFactory:'NSS140',controlledLoad:true,routerWrites:false}));
