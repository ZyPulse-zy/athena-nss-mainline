"""Explicit context overlay; no source-policy, timer, flow or QoS changes."""
from pathlib import Path
import hashlib,json,subprocess
R=Path('.');D=R/'work/nss68'
sha=lambda b:hashlib.sha256(b).hexdigest()
def put(name,text):
    p=D/name
    assert not p.exists(),str(p)
    p.write_text(text,encoding='utf-8',newline='\n')
def replace(s,old,new,count=1):
    assert s.count(old)==count,(old,s.count(old),count)
    return s.replace(old,new)
# Qualified publication installation: reuse the proven exact undo, arm and byte checks.
s=(R/'work/nss67/publication-trial.mjs').read_text(encoding='utf-8').replace('work/nss67','work/nss68').replace('NSS67','NSS68').replace('nss67-publication-','nss68-publication-')
s=replace(s,"const worker=fs.readFileSync('work/nss64/candidate-worker.lua');", """const trial67=JSON.parse(fs.readFileSync('work/nss67/trial-private.json'));
const priorUndo=JSON.parse(fs.readFileSync(trial67.localDir+'/rollback-qualified.json'));
assert.ok(priorUndo.passed&&priorUndo.automaticExpiryWithoutControllerRollback&&priorUndo.previousWorkerAndConfigRestored);
const highLoad=JSON.parse(fs.readFileSync('outputs/nss67-mainline-observations.json'));
// Full high-load evidence is separately frozen, never an NSS permission.
assert.ok(fs.existsSync('work/nss67/trial-loaded-1-health.json')));
const worker=fs.readFileSync('work/nss64/candidate-worker.lua');""")
# Drop the unused broad JSON read, qualify by exact high-load full audit receipts.
s=s.replace("const highLoad=JSON.parse(fs.readFileSync('outputs/nss67-mainline-observations.json'));\n",'')
s=s.replace("assert.ok(fs.existsSync('work/nss67/trial-loaded-1-health.json')));", "const loadProofs=['trial-loaded-1','trial-loaded-2'].map(n=>JSON.parse(fs.readFileSync('work/nss67/'+n+'-health.json')));\nfor(const p of loadProofs)assert.ok(p.passed&&p.originalFullLockedAudit&&p.queryAge<6);")
s=replace(s,"fs.writeFileSync(root+'/trial-private.json',json(ctx),{flag:'wx'});", "delete ctx.commitAt;fs.writeFileSync(root+'/trial-private.json',json(ctx),{flag:'wx'});")
s=replace(s,"fs.writeFileSync(dir+'/worker.lua',worker);", "fs.writeFileSync(dir+'/worker.lua',worker);for(const n of untouched)fs.copyFileSync(old.localDir+'/'+n,dir+'/'+n);")
put('publication-retain.mjs',s)
for name in ['verify-rollback.mjs']:
    put(name,(R/'work/nss67'/name).read_text(encoding='utf-8').replace('work/nss67','work/nss68').replace('NSS67','NSS68'))
# Health audit gains an explicit retained context. Original native assertions stay byte-identical.
s=(D/'health.mjs').read_text(encoding='utf-8')
s=replace(s,"trial?'work/nss68/trial-private.json':'work/nss47/deployment-latest.json'", "trial?'work/nss68/trial-private.json':label==='before'?'work/nss47/deployment-latest.json':'work/nss68/deployment-latest.json'",2)
(D/'health.mjs').write_text(s,encoding='utf-8',newline='\n')
# Consumer writes only new round artifacts; the adapter itself is unchanged.
s=(R/'work/nss49/read-real-candidates.mjs').read_text(encoding='utf-8')
s=replace(s,"import {verifyCurrentClassifier} from './binding.mjs';", "import {verifyDeployment,deploymentPath} from './deployment-binding.mjs';")
s=replace(s,"const ctxPath=process.argv[2]??'work/nss49/deployment-latest.json';assert.ok(['work/nss49/deployment-latest.json'].includes(ctxPath));\nverifyCurrentClassifier();\nconst ctx=JSON.parse(fs.readFileSync(ctxPath)),cfg=JSON.parse(fs.readFileSync(ctx.localDir+'/config.json'));", "const ctxPath=process.argv[2]??deploymentPath;assert.equal(ctxPath,deploymentPath);\nconst {deployment:ctx,config:cfg}=verifyDeployment();")
for name in ['pc-app-endpoints-private.json','real-candidates-raw-private.json','real-candidates-private.json','real-reader-qualified.json']:
    s=s.replace('work/nss49/'+name,'work/nss68/'+name)
put('read-real-candidates.mjs',s)
s=(R/'work/nss49/record-candidates.mjs').read_text(encoding='utf-8').replace('work/nss49/','work/nss68/')
put('record-candidates.mjs',s)
s=(R/'work/nss49/wait-ready-candidate.mjs').read_text(encoding='utf-8')
s=replace(s,"export async function waitReady(c,ctx,label){", "import {verifyDeployment} from './deployment-binding.mjs';\nexport async function waitReady(c,ctx,label){")
s=replace(s,"const deployment=JSON.parse(fs.readFileSync('work/nss49/deployment-latest.json')),cfg=JSON.parse(fs.readFileSync(deployment.localDir+'/config.json'));", "const {deployment,config:cfg}=verifyDeployment();assert.equal(ctx.base,deployment.base);assert.equal(ctx.configHash,deployment.configHash);")
s=s.replace("fs.writeFileSync('work/nss49/'","fs.writeFileSync('work/nss68/'")
s=s.replace("fs.readFileSync('work/nss49/wait-ready-candidate.mjs')","fs.readFileSync('work/nss68/wait-ready-candidate.mjs')")
put('wait-ready-candidate.mjs',s)
s=(R/'work/nss63/wait-publication-metadata.mjs').read_text(encoding='utf-8').replace("from'../nss49/wait-ready-candidate.mjs'","from'./wait-ready-candidate.mjs'").replace("fs.writeFileSync('work/nss63/'","fs.writeFileSync('work/nss68/'")
put('wait-publication-metadata.mjs',s)
s=(R/'work/nss63/current-audit-diagnostic.mjs').read_text(encoding='utf-8')
s=replace(s,"const ctx=JSON.parse(fs.readFileSync('work/nss47/deployment-latest.json'));", "const {deployment:ctx}=verifyDeployment();")
s="import {verifyDeployment} from './deployment-binding.mjs';\n"+s
s=s.replace('work\\/nss63\\/real-matched-aba-','work\\/nss68\\/real-matched-aba-').replace("'work/nss63'","'work/nss68'").replace("fs.writeFileSync('work/nss63/'","fs.writeFileSync('work/nss68/'")
put('current-audit-diagnostic.mjs',s)
s=(R/'work/nss63/module-stage.mjs').read_text(encoding='utf-8')
s=replace(s,"import{buildPayload}from'./payload.mjs';", "import{buildPayload}from'../nss63/payload.mjs';\nimport {verifyDeployment} from './deployment-binding.mjs';")
s=replace(s,"const deployment=JSON.parse(fs.readFileSync('work/nss47/deployment-latest.json'));assert.equal(deployment.committed,true);const configuration=JSON.parse(fs.readFileSync(deployment.localDir+'/config.json'));", "const {deployment,config:configuration}=verifyDeployment();")
put('module-stage.mjs',s)
s=(R/'work/nss63/real-session.mjs').read_text(encoding='utf-8')
s=replace(s,"const root='work/nss49', observationRoot='work/nss49'", "const root='work/nss49', observationRoot='work/nss68'")
s=s.replace("'work/nss63/real-matched-aba-'","'work/nss68/real-matched-aba-'").replace("'work/nss63/current-audit-diagnostic.mjs'","'work/nss68/current-audit-diagnostic.mjs'")
put('real-session.mjs',s)
put('session-binding.mjs',"""import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {verifyPreparation as previous} from '../nss63/session-binding.mjs';
import {verifyDeployment} from './deployment-binding.mjs';
export function verifyPreparation(){const q=previous(),p=JSON.parse(fs.readFileSync('work/nss68/entry-qualified.json'));
assert.equal(p.passed,true);assert.equal(p.baseBoundInputs,Object.keys(q.sourceManifest).length);assert.equal(p.baseBoundInputs,241);
for(const k of ['original241InputsRetained','originalNativeAuditByteIdentical','classifierAdapterByteIdentical','nativeStageAndPayloadPolicyByteIdentical','allFlowTimersAndLimitsUnchanged','explicitDeploymentForAllConsumers'])assert.equal(p[k],true,k);
for(const[f,h]of Object.entries(p.sourceManifest))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex'),h,f);
const deployment=verifyDeployment();return{...q,sourceManifest:{...q.sourceManifest,...p.sourceManifest},deploymentReference:'work/nss68/deployment-latest.json',classifierOwner:deployment.classifierOwner,publicationDeploymentOverlay:true};}
""")
# Check new wrappers only, do not replay old preparation suites.
node='C:/Users/lishu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
for p in D.glob('*.mjs'):subprocess.run([node,'--check',str(p)],check=True)
print(json.dumps({'prepared':True,'newExplicitContextOverlay':True,'retainedDeploymentRequired':True,'routerWrites':False}))
