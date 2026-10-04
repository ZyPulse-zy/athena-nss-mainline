"""New entry for the retained classifier; historical entries stay immutable."""
from pathlib import Path
import hashlib,json,subprocess
here=Path(__file__).resolve().parent;root=here.parents[1]
def emit(name,s):(here/name).write_text(s,encoding='utf-8',newline='\n')
for name in ['fast-path.lua','classifier.lua','core-guard-phase.lua','classified-tags.lua','qos-physical.lua','tag-normalizer.lua','wan-scope.lua','state-node.lua','module-stage-guardian.lua','read-prerequisites.lua']:
    assert not(here/name).exists();(here/name).write_bytes((root/'work/nss39'/name).read_bytes())
for name in ['aba-qualified.json','consumer-qualified.json','mainline-preflight-qualified.json']:(here/name).write_bytes((root/'work/nss39'/name).read_bytes())
for name in ['module-stage.mjs','payload.mjs']:
    s=(root/'work/nss39'/name).read_text().replace('work/nss39','work/nss46');emit(name,s)
for name in ['real-session.mjs','record-candidates.mjs','read-real-candidates.mjs','parse-ecm-any-wan.mjs','publication-wait.lua','parse-dependency-graph.mjs']:
    s=(root/'work/nss42'/name).read_text().replace('work/nss42','work/nss46')
    if name=='real-session.mjs':
        s=s.replace("const root='work/nss39'","const root='work/nss46'").replace("from '../nss39/module-stage.mjs'","from './module-stage.mjs'")
    if name=='read-real-candidates.mjs':
        s=s.replace("from '../nss39/binding.mjs'","from './binding.mjs'").replace('work/nss39/deployment-latest.json','work/nss46/deployment-latest.json').replace('work/nss39/classifier.lua','work/nss46/classifier.lua')
    emit(name,s)
s=(root/'work/nss44/wait-ready-candidate.mjs').read_text().replace('work/nss39/deployment-latest.json','work/nss46/deployment-latest.json').replace('work/nss42/publication-wait.lua','work/nss46/publication-wait.lua').replace('work/nss44','work/nss46').replace('Uninstalled readonly scheduling candidate.','Bound readonly scheduling hint.')
emit('wait-ready-candidate.mjs',s)
s=(root/'work/nss44/candidate-audit-readonly.mjs').read_text().replace("from '../nss42/session-binding.mjs'","from './session-binding.mjs'").replace('work/nss39/deployment-latest.json','work/nss46/deployment-latest.json').replace('work/nss44','work/nss46')
emit('current-audit-diagnostic.mjs',s)
s=(root/'work/nss42/dependency-closure.mjs').read_text().replace('work/nss42','work/nss46');emit('dependency-closure.mjs',s)
s=(root/'work/nss42/session-binding.mjs').read_text().replace("from '../nss39/qualification.mjs'","from './qualification.mjs'").replace('work/nss42','work/nss46').replace('p.runtimeRouterPayloadsUnchanged','p.nssRouterPayloadsUnchanged');emit('session-binding.mjs',s)
s=(root/'work/nss45/final-closure.mjs').read_text().replace('work/nss39/deployment-latest.json','work/nss46/deployment-latest.json').replace('work/nss45','work/nss46');emit('final-closure.mjs',s)
for name in ['test-parser.mjs','test-controller.mjs','test-dependencies.mjs','test-binding.mjs']:
    s=(root/'work/nss42'/name).read_text().replace('work/nss42','work/nss46')
    if name=='test-controller.mjs':s=s.replace("import {beginStage,uploadStage,readStage,waitStageUndo} from '../nss39/module-stage.mjs';","import {beginStage,uploadStage,readStage,waitStageUndo} from './module-stage.mjs';").replace("const root='work/nss39'","const root='work/nss46'")
    if name=='test-binding.mjs':s=s.replace("import {verifyPreparation as runtime} from '../nss39/qualification.mjs';","import {verifyPreparation as runtime} from './qualification.mjs';").replace('q.auditPurposeSeparated=false','q.auditPurposeSeparated=false')
    emit(name,s)
node='C:/Users/lishu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
for p in here.glob('*.mjs'):
    r=subprocess.run([node,'--check',str(p)],capture_output=True,text=True);assert r.returncode==0,r.stderr
print(json.dumps({'prepared':True,'newEntry':'NSS46','originalNss42EntryUntouched':True,'nssLuaPayloadsByteIdenticalToNss39':True,'newSchedulingSource':'before-software-baseline classification','originalLockedAuditRetained':True}))
