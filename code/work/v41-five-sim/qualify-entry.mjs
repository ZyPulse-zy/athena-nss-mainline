import fs from'node:fs';import crypto from'node:crypto';import path from'node:path';import assert from'node:assert/strict';import{spawnSync}from'node:child_process';import{verifyPreparation as inherited}from'../v40-five-sim/session-binding.mjs';
const root='work/v41-five-sim',old=inherited(),prep=JSON.parse(fs.readFileSync(root+'/prepare-receipt.json')),hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const rebase=s=>s.replaceAll('work/v40-five-sim','work/v41-five-sim').replaceAll('work\\/v40-five-sim\\/','work\\/v41-five-sim\\/').replaceAll('v40-five-sim-','v41-five-sim-').replaceAll('v40-final','v41-final');
const skip=['prepare.py','qualify-entry.mjs','session-binding.mjs','match-controlled.mjs','repair-native-bytes.py','inspect-own-ssh-failure.mjs','model-serial.mjs'];
const changes={
 'native-client.mjs':[["import{mayRetryAcquisition}from'./fixture-retry-policy.mjs';","import{mayRetryAcquisition}from'./fixture-retry-policy.mjs';\nimport{pendingOwnedRotations}from'./acquisition-plan.mjs';"],["if(x.rotateTcp){assert.ok(['tcp','tcp2','tcp3','tcp4'].includes(x.rotateTcp.slot));const s=stats.tcpChildren.find(y=>y.slot===x.rotateTcp.slot);if(x.rotateTcp.attempt>s.attempt&&!rotating.has(s.slot)){assert.ok(!fixtureFrozen&&(performance.now()-began)/1000<30,'Natural TCP acquisition is closed');startTcp(s.slot,x.rotateTcp.attempt).catch(finish);}}","for(const request of pendingOwnedRotations(x.rotateTcpBatch??(x.rotateTcp?[x.rotateTcp]:[]),{children:stats.tcpChildren,rotating,frozen:fixtureFrozen,elapsedSeconds:(performance.now()-began)/1000}))startTcp(request.slot,request.attempt).catch(finish);"]],
 'read-controlled.mjs':[['@{pid=$p.Id;tcp=@($rows);udp=@(','@{pid=$p.Id;tcpChildren=@($s.tcpChildren);tcp=@($rows);udp=@('],['ownedTcpSlots,tcp,udp,pairs,controlledClientPid','ownedTcpSlots,ownedTcpChildren:pc.tcpChildren,tcp,udp,pairs,controlledClientPid']],
 'pilot-supervisor.mjs':[['2026-10-07T08:00:00Z','2026-10-07T09:00:00Z'],['v39 five naturally distinct WANs','v41 batched acquisition of five naturally distinct WANs']]
};
for(const[f,h]of Object.entries(prep.oldHashes)){
 const bytes=fs.readFileSync(f),name=path.basename(f);assert.equal(hash(bytes),h,f);if(skip.includes(name))continue;
 let expected=f.endsWith('.json')?bytes:Buffer.from(rebase(bytes.toString('utf8')));
 if(changes[name]){let s=expected.toString('utf8');for(const[a,b]of changes[name]){assert.equal(s.split(a).length,2,name);s=s.replace(a,b);}expected=Buffer.from(s);}
 assert.deepEqual(fs.readFileSync(root+'/'+name),expected,name);
}
const models=JSON.parse(fs.readFileSync(root+'/acquisition-model-qualified.json'));assert.ok(models.passed&&models.checks===11&&!models.hardwareExecuted);
const manifest={};let dependencies=0;
for(const name of fs.readdirSync(root))if(/\.(mjs|lua|py|ps1|json)$/.test(name)&&!name.includes('private')&&!['prepare-receipt.json','entry-qualified.json'].includes(name)){
 const f=root+'/'+name;manifest[f]=hash(fs.readFileSync(f));if(name.endsWith('.mjs')){for(const m of fs.readFileSync(f,'utf8').matchAll(/(?:from\s*|import\s*)['"](\.{1,2}\/[^'"]+\.mjs)['"]/g)){assert.ok(fs.existsSync(path.resolve(root,m[1])),m[1]);dependencies++;}const p=spawnSync(process.execPath,['--check',f],{encoding:'utf8',windowsHide:true});assert.equal(p.status,0,p.stderr);}
}
const inheritedQ=JSON.parse(fs.readFileSync('work/v40-five-sim/entry-qualified.json')),out={...inheritedQ,sourceManifest:manifest,inheritedBindings:Object.keys(old.sourceManifest).length,relativeDependenciesExist:dependencies,duplicateOwnedTcpAcquiredInBatch:true,currentPcChildIdentityCarriedWithoutNewIo:true,acquisitionModelChecks:models.checks,classificationNativeQosAdmissionAndRestorationUnchanged:true,newAcquisitionStillBefore30SecondsAndBeforeFreeze:true,hardwareExecuted:false,cutoff:prep.cutoff};
fs.writeFileSync(root+'/entry-qualified.json',JSON.stringify(out,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({passed:true,newSources:Object.keys(manifest).length,bindings:out.inheritedBindings+Object.keys(manifest).length,checks:models.checks,hardwareExecuted:false}));
