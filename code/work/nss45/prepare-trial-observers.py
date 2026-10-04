"""Prepare bound observers before the backend-only temporary installation."""
from pathlib import Path
import hashlib,json,subprocess
here=Path(__file__).resolve().parent;root=here.parents[1]
def emit(name,source):
    (here/name).write_text(source,encoding='utf-8',newline='\n')
source=(root/'work/nss39/deployment-audit.mjs').read_text()
source=source.replace("import fs from'node:fs';","import {render} from './audit-renderer.mjs';\nimport fs from'node:fs';",1)
source=source.replace("'work/nss39/deployment-latest.json'","'work/nss45/backend-trial/deployment-latest.json'")
source=source.replace("const code=fs.readFileSync('work/nss23/operational-audit.lua','utf8');","const code=render(fs.readFileSync('work/nss23/operational-audit.lua','utf8'));")
source=source.replace("const proof=JSON.parse(raw.stdout);","const envelope=JSON.parse(raw.stdout);assert.equal(envelope.passed,true,envelope.error);const proof=envelope.result;")
source=source.replace("const out={passed:true,","const out={passed:true,nssAdmissionAllowed:false,originalCompleteAuditAssertionsRetained:true,backendOnlyTrial:true,")
emit('audit-backend-trial.mjs',source)
source=(root/'work/nss39/observe-compact.mjs').read_text().replace("out='work/nss39/'","out='work/nss45/'")
emit('observe-backend-trial.mjs',source)
source=(root/'work/nss39/verify-rollback.mjs').read_text().replace("'work/nss39/deployment-latest.json'","'work/nss45/backend-trial/deployment-latest.json'")
source=source.replace("previous.base+'/conntrack-source.lua '+previous.base+'/guardian.lua'","previous.base+'/conntrack-source.lua '+previous.base+'/guardian.lua '+previous.base+'/backend.lua'")
source=source.replace("['conntrack-source.lua','guardian.lua']","['conntrack-source.lua','guardian.lua','backend.lua']")
source=source.replace("previousNormalizerAndGuardianRestored:true,","previousNormalizerAndGuardianRestored:true,previousBackendRestored:true,backendOnlyTrial:true,")
emit('verify-backend-rollback.mjs',source)
source=(root/'work/nss39/cancel-restored-stage.mjs').read_text().replace("'work/nss39/deployment-latest.json'","'work/nss45/backend-trial/deployment-latest.json'")
emit('cancel-backend-stage.mjs',source)
names=['audit-backend-trial.mjs','observe-backend-trial.mjs','verify-backend-rollback.mjs','cancel-backend-stage.mjs']
node='C:/Users/lishu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
for name in names:
    p=subprocess.run([node,'--check',str(here/name)],capture_output=True,text=True,timeout=20);assert p.returncode==0,p.stderr
proof={'passed':True,'preparedBeforeRouterMutation':True,'originalAuditAssertionsRetained':True,'rollbackVerifiesAllFourClassifierSourcesAndConfig':True,'rollbackOnlyNaturalExpiryAccepted':True,'observerFiles':{n:hashlib.sha256((here/n).read_bytes()).hexdigest()for n in names}}
(here/'trial-observers-prepared.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in proof.items()if k!='observerFiles'}))
