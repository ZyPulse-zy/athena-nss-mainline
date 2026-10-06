import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {verifyPreparation as inherited} from '../nss157/session-binding-live.mjs';
const root='work/nss158',old=inherited(),hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const names=['prepare-aba.py','fast-path.lua','module-stage-guardian.lua','payload.mjs','measure-payload.mjs','measure-payload-v2.mjs','prepare-model.py','combined-models.lua','qualify-native.mjs','prepare-entry.py','module-stage.mjs','current-audit-diagnostic.mjs','failed-wan-owner.lua','epoch-driver.mjs','session-binding.mjs','pilot-supervisor.mjs','qualify-entry.mjs','prepare-qualification-v2.py','qualify-entry-v2.mjs','declared-baseline.mjs','prepare-qualification-v3.py','qualify-entry-v3.mjs'];
const sourceManifest={};
for(const name of names){const f=root+'/'+name,text=fs.readFileSync(f,'utf8');sourceManifest[f]=hash(fs.readFileSync(f));
 if(name.endsWith('.mjs')||name.endsWith('.py')){const t=name.endsWith('.mjs')?spawnSync(process.execPath,['--check',f],{encoding:'utf8',windowsHide:true}):spawnSync('C:/Users/lishu/AppData/Local/Programs/Python/Python312/python.exe',['-c','import sys;compile(open(sys.argv[1],encoding="utf-8").read(),sys.argv[1],"exec")',f],{encoding:'utf8',windowsHide:true});assert.equal(t.status,0,t.stderr);}
 if(name.endsWith('.mjs'))for(const m of text.matchAll(/\b(?:from|import)\s*['"]([^'"]+)['"]/g)){if(!m[1].startsWith('.'))continue;const d=path.posix.normalize(path.posix.join(root,m[1]));assert.ok(names.includes(path.posix.relative(root,d))||d in old.sourceManifest,'Unbound import '+d);assert.ok(fs.existsSync(d));}
 if(name.endsWith('.mjs'))for(const m of text.matchAll(/(?:readFileSync|runNode)\(\s*['"](work\/[^'"]+)['"]/g)){if(!m[1].endsWith('.mjs')&&!m[1].endsWith('.lua'))continue;assert.ok(m[1] in old.sourceManifest||names.includes(path.posix.relative(root,m[1])),'Unbound literal '+m[1]);assert.ok(fs.existsSync(m[1]));}
}
const native=JSON.parse(fs.readFileSync(root+'/native-qualified.json'));assert.ok(native.passed&&!native.productionExecuted&&!native.fullFactoryModeled);assert.equal(native.fastSourceSha256,sourceManifest[root+'/fast-path.lua']);
const size=JSON.parse(fs.readFileSync(root+'/historical-size-v2.json'));assert.ok(size.passed&&size.historicalPlanPacketAstReconstructedExactly&&size.actualEncodedBytes<=73728);
const original=fs.readFileSync('work/nss157/fast-path-v2.lua','utf8'),candidate=fs.readFileSync(root+'/fast-path.lua','utf8');
const section=(s,a,b)=>s.slice(s.indexOf(a),s.indexOf(b,s.indexOf(a)));
for(const[a,b]of [[' local function observe()',' local function counters('],[' retire=function(C)',' local function tick('],[' local function tick(name)',' local function measure('],[' function out.align(deadline)',' function out.run(']])assert.equal(section(original,a,b),section(candidate,a,b));
assert.equal(fs.readFileSync(root+'/module-stage-guardian.lua','utf8').replace('if record.abaCompleted or record.automaticLifecycleEpochCompleted','if record.automaticLifecycleEpochCompleted'),fs.readFileSync('work/nss157/module-stage-guardian.lua','utf8'));
const driver=fs.readFileSync(root+'/epoch-driver.mjs','utf8');assert.ok(driver.includes("['A','B','A2']")&&driver.includes("assert.equal(latest.automaticLifecycleEpochCompleted,false)")&&driver.includes('matchedForwardingABACompleted:completed&&failures.length===0'));
const q={passed:true,inheritedBindings:Object.keys(old.sourceManifest).length,sourceManifest,productionExecution:false,completeLiteralReadDependenciesVerified:true,fullFactoryModelExecuted:false,actualChangedFunctionsNativeMockCases:native.model.checks,originalObserveRetireTickAlignmentUnchanged:true,fullBundleActualWriteStillBounded:true,originalBudgetsSeconds:[6,27,100,180],byteLimits:[9000,65536,73728,1048576],classifierKernelGateAndQoSUnchanged:true,sharedBoundedSoftwareFixtureUnchanged:true};
fs.writeFileSync(root+'/entry-qualified.json',JSON.stringify(q,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({passed:true,bindings:Object.keys((await import('./session-binding.mjs')).verifyPreparation().sourceManifest).length,historicalBundleBytes:size.actualEncodedBytes,nativeChangedFunctionMockCases:native.model.checks,productionExecution:false}));
