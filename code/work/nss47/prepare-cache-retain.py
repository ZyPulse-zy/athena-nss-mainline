"""One-variable cache retention after an observed independent expiry rollback."""
from pathlib import Path
import json,hashlib,subprocess
here=Path(__file__).resolve().parent;root=here.parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
trial=json.loads((here/'cache-trial/deployment-latest.json').read_text())
undo=json.loads((root/trial['localDir']/'rollback-qualified.json').read_text())
bound=json.loads((here/'cache-bound-qualified.json').read_text())
assert undo['passed'] and undo['automaticExpiryWithoutControllerRollback'] and undo['previousClassifierCoreRestored']
assert bound['passed'] and bound['candidateSha256']==sha((here/'classifier-core-cache.lua').read_bytes())
dest=here/'cache-retain';dest.mkdir(exist_ok=True)
for name in ['worker.lua','guardian.lua','conntrack-source.lua','backend.lua','classifier-core.lua']:
    (dest/name).write_bytes((here/'cache-trial'/name).read_bytes())
s=(here/'upgrade-cache.mjs').read_text().replace("root='work/nss47/cache-trial'","root='work/nss47/cache-retain'").replace("const id='nss47-cache-'","const id='nss47-retain-'")
s=s.replace('const previousConfig=',"const bound=JSON.parse(fs.readFileSync('work/nss47/cache-bound-qualified.json'));assert.ok(bound.passed&&bound.candidateSha256===native.candidateSha256);const previousConfig=",1)
(here/'upgrade-cache-retain.mjs').write_text(s,encoding='utf-8',newline='\n')
a=(here/'audit-cache.mjs').read_text().replace('work/nss47/cache-trial/deployment-latest.json','work/nss47/cache-retain/deployment-latest.json')
(here/'audit-cache-retain.mjs').write_text(a,encoding='utf-8',newline='\n')
c=(root/'work/nss46/commit-row.mjs').read_text().replace('work/nss46/row-retain/deployment-latest.json','work/nss47/cache-retain/deployment-latest.json')
start=c.index('const qualified=');end=c.index('const c=await connectRouter();')
c=c[:start]+"""const qualified=JSON.parse(fs.readFileSync('work/nss47/cache-qualified.json')),native=JSON.parse(fs.readFileSync('work/nss47/native-cache-qualified.json')),bound=JSON.parse(fs.readFileSync('work/nss47/cache-bound-qualified.json')),trial=JSON.parse(fs.readFileSync('work/nss47/cache-trial/deployment-latest.json')),undo=JSON.parse(fs.readFileSync(trial.localDir+'/rollback-qualified.json'));assert.ok(qualified.passed&&native.passed&&bound.passed&&undo.passed&&undo.automaticExpiryWithoutControllerRollback&&undo.previousClassifierCoreRestored);const cfg=JSON.parse(fs.readFileSync(ctx.localDir+'/config.json'));assert.equal(qualified.candidateSha256,cfg.files['classifier-core.lua']);assert.equal(native.candidateSha256,qualified.candidateSha256);assert.equal(bound.candidateSha256,qualified.candidateSha256);
"""+c[end:]
c=c.replace('boundedRowOverflowQualified=true','boundedPureAddressCacheQualified=true').replace("fs.writeFileSync('work/nss46/deployment-latest.json'","fs.writeFileSync('work/nss47/deployment-latest.json'")
(here/'commit-cache.mjs').write_text(c,encoding='utf-8',newline='\n')
node='C:/Users/lishu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
for name in ['upgrade-cache-retain.mjs','audit-cache-retain.mjs','commit-cache.mjs']:
    subprocess.run([node,'--check',str(here/name)],check=True)
print(json.dumps({'prepared':True,'singleVariable':'pure IPv4 computation cache','independentUndoVerified':True,'rollbackSeconds':180,'nssEnabled':False}))
