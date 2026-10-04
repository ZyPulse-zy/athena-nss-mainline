"""Retain only uninstrumented, real-child-qualified expiry recovery."""
from pathlib import Path
import hashlib,json,subprocess
here=Path(__file__).resolve().parent;root=here.parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
fault=json.loads((here/'expiry-fault/deployment-latest.json').read_text());q=json.loads((root/fault['localDir']/'fault-qualified.json').read_text());assert q['passed']and q['realApplyChild']and q['exactRecoveryConfirmed']and q['refusedBeforeBatch']and q['applyChildReaped']and q['latestHealthy']
def emit(name,s):(here/name).write_text(s,encoding='utf-8',newline='\n')
trial=here/'expiry-retain';trial.mkdir(exist_ok=True)
for name,source in [('worker.lua',here/'stale-worker.lua'),('guardian.lua',here/'stale-guardian.lua'),('conntrack-source.lua',root/'work/nss45/original-conntrack-source.lua'),('backend.lua',root/'work/nss45/candidate-backend.lua')]:
    (trial/name).write_bytes(source.read_bytes())
assert 'NSS46_REAL_'not in (trial/'worker.lua').read_text()
s=(here/'upgrade-fault.mjs').read_text().replace("root='work/nss46/expiry-fault'","root='work/nss46/expiry-retain'")
a=s.index('const qualified=');b=s.index("const id='nss46-expiry-fault-'")
s=s[:a]+"""const qualified=JSON.parse(fs.readFileSync('work/nss46/stale-qualified.json')),faultCtx=JSON.parse(fs.readFileSync('work/nss46/expiry-fault/deployment-latest.json')),fault=JSON.parse(fs.readFileSync(faultCtx.localDir+'/fault-qualified.json')),undo=JSON.parse(fs.readFileSync(faultCtx.localDir+'/rollback-qualified.json'));assert.ok(qualified.passed&&qualified.checks===34&&fault.passed&&fault.realApplyChild&&fault.exactRecoveryConfirmed&&undo.passed&&undo.automaticExpiryWithoutControllerRollback);assert.equal(qualified.guardianSha256,sha(fs.readFileSync(root+'/guardian.lua')));assert.equal(qualified.workerSha256,sha(fs.readFileSync(root+'/worker.lua')));
const previousConfig=JSON.parse(fs.readFileSync(old.localDir+'/config.json'));for(const name of ['backend.lua','conntrack-source.lua'])assert.equal(sha(fs.readFileSync(root+'/'+name)),previousConfig.files[name]);
"""+s[b:]
s=s.replace("const id='nss46-expiry-fault-'","const id='nss46-expiry-'").replace('typed software expiry handling, test-only real observation delay and binding','qualified typed software expiry handling and binding').replace('realApplyExpiryFaultTrial:true','qualifiedSoftwareExpiryRetention:true')
s=s.replace("undo=JSON.parse(fs.readFileSync(faultCtx.localDir+'/rollback-qualified.json'))","undoProof=JSON.parse(fs.readFileSync(faultCtx.localDir+'/rollback-qualified.json'))").replace('&&undo.passed&&undo.automaticExpiryWithoutControllerRollback','&&undoProof.passed&&undoProof.automaticExpiryWithoutControllerRollback')
emit('upgrade-expiry.mjs',s)
emit('audit-expiry.mjs',(here/'audit-fault.mjs').read_text().replace('work/nss46/expiry-fault','work/nss46/expiry-retain').replace('realApplyExpiryFaultTrial:true','qualifiedSoftwareExpiryRetention:true'))
s=(here/'commit-backend.mjs').read_text().replace('work/nss46/backend-retain/deployment-latest.json','work/nss46/expiry-retain/deployment-latest.json')
a=s.index('const qualified=');b=s.index('const c=await connectRouter()',a)
s=s[:a]+"""const qualified=JSON.parse(fs.readFileSync('work/nss46/stale-qualified.json')),faultCtx=JSON.parse(fs.readFileSync('work/nss46/expiry-fault/deployment-latest.json')),fault=JSON.parse(fs.readFileSync(faultCtx.localDir+'/fault-qualified.json')),undo=JSON.parse(fs.readFileSync(faultCtx.localDir+'/rollback-qualified.json'));assert.ok(qualified.passed&&fault.passed&&fault.realApplyChild&&fault.exactRecoveryConfirmed&&undo.passed&&undo.automaticExpiryWithoutControllerRollback);const cfg=JSON.parse(fs.readFileSync(ctx.localDir+'/config.json'));assert.equal(qualified.workerSha256,cfg.files['worker.lua']);assert.equal(qualified.guardianSha256,cfg.files['guardian.lua']);
"""+s[b:]
s=s.replace('initialRecoveryReuseQualified=true','typedSoftwareExpiryRealChildQualified=true')
emit('commit-expiry.mjs',s)
node='C:/Users/lishu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
for name in ['upgrade-expiry.mjs','audit-expiry.mjs','commit-expiry.mjs']:
    p=subprocess.run([node,'--check',str(here/name)],capture_output=True,text=True);assert p.returncode==0,p.stderr
emit('expiry-retain-prepared.json',json.dumps({'passed':True,'faultHooksAbsent':True,'expiredChildAndExactRecoveryProved':True,'naturalExpiryRequiredBeforeInstall':True,'productionChanges':['worker.lua','guardian.lua'],'sourceAndPolicyUnchanged':True,'allDeadlinesUnchanged':True,'nssEnabled':False,'workerSha256':sha((trial/'worker.lua').read_bytes())},indent=2)+'\n')
print(json.dumps({'prepared':True,'uninstrumentedWorker':True,'naturalRollbackStillRequired':True}))
