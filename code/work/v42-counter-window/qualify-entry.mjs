import fs from'node:fs';import crypto from'node:crypto';import path from'node:path';import assert from'node:assert/strict';import{spawnSync}from'node:child_process';import{verifyPreparation as inherited}from'../v41-five-sim/session-binding.mjs';
const root='work/v42-counter-window',old=inherited(),prep=JSON.parse(fs.readFileSync(root+'/prepare-receipt.json')),hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const rebase=s=>s.replaceAll('work/v41-five-sim','work/v42-counter-window').replaceAll('work\\/v41-five-sim\\/','work\\/v42-counter-window\\/').replaceAll('v41-five-sim-','v42-counter-window-').replaceAll('v41-final','v42-final');
const changes={
 'pilot-supervisor.mjs':[['2026-10-07T09:00:00Z','2026-10-07T10:00:00Z'],['v41 batched acquisition of five naturally distinct WANs','v42 bounded terminal counter-window diagnosis']],
 'fast-path.lua':[['R.acceleratedState=state();R.qosAccelerated=qos.snapshot();measure()','R.acceleratedStateRead={before=now()};R.acceleratedState=state();R.acceleratedStateRead.after=now();R.qosAccelerated=qos.snapshot();measure()'],['unload();active=false;stopped();assert(state()',"R.terminalStateRead={before=now()};local ok,v=pcall(state);R.terminalStateRead.after=now();R.terminalStateRead.ok=ok;R.terminalStateRead[ok and'body'or'error']=v;unload();active=false;stopped();assert(state()"]]
};
for(const[f,h]of Object.entries(prep.oldHashes)){
 const b=fs.readFileSync(f),n=path.basename(f);assert.equal(hash(b),h,f);if(['prepare.py','qualify-entry.mjs','session-binding.mjs'].includes(n))continue;
 let expected=f.endsWith('.json')?b:Buffer.from(rebase(b.toString('utf8')));
 if(changes[n]){let s=expected.toString('utf8');for(const[a,z]of changes[n]){assert.equal(s.split(a).length,2,n);s=s.replace(a,z)}expected=Buffer.from(s)}assert.deepEqual(fs.readFileSync(root+'/'+n),expected,n);
}
const f=fs.readFileSync(root+'/fast-path.lua','utf8');assert.ok(f.includes("readAfterStopNewLearning")===false);assert.ok(f.indexOf('R.terminalStateRead={before=now()}')>f.indexOf("put('/sys/kernel/debug/ecm/front_end_ipv4_stop','1\\n');R.frontendClosedAt"));assert.ok(f.includes('local ok,v=pcall(state)'));
const manifest={};let dependencies=0;
for(const n of fs.readdirSync(root))if(/\.(mjs|lua|py|ps1|json)$/.test(n)&&!n.includes('private')&&!['prepare-receipt.json','entry-qualified.json'].includes(n)){
 const p=root+'/'+n;manifest[p]=hash(fs.readFileSync(p));if(n.endsWith('.mjs')){for(const m of fs.readFileSync(p,'utf8').matchAll(/(?:from\s*|import\s*)['"](\.{1,2}\/[^'"]+\.mjs)['"]/g)){assert.ok(fs.existsSync(path.resolve(root,m[1])),m[1]);dependencies++;}const r=spawnSync(process.execPath,['--check',p],{encoding:'utf8',windowsHide:true});assert.equal(r.status,0,r.stderr);}
}
const inheritedQ=JSON.parse(fs.readFileSync('work/v41-five-sim/entry-qualified.json')),out={...inheritedQ,sourceManifest:manifest,inheritedBindings:Object.keys(old.sourceManifest).length,relativeDependenciesExist:dependencies,additionalTerminalStateReadsMaximum:1,terminalReadAfterStopNewLearning:true,terminalReadPcallPreservesRetirement:true,classificationNativeQosAdmissionAndRestorationUnchanged:true,hardwareExecuted:false,cutoff:prep.cutoff};
fs.writeFileSync(root+'/entry-qualified.json',JSON.stringify(out,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({passed:true,newSources:Object.keys(manifest).length,bindings:out.inheritedBindings+Object.keys(manifest).length,classificationPolicyChanged:false,hardwareExecuted:false}));
