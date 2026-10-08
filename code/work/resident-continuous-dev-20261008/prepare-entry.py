"""Fork the qualified entry and service, keeping historical inputs unchanged."""
from pathlib import Path

root = Path(__file__).resolve().parent
normal = root.parent/'resident-normal-dev-i-20261008'
service = root.parent/'resident-service-dev-i-20261008'

def once(s, a, b):
    assert s.count(a) == 1, a
    return s.replace(a, b)

s = (normal/'normal-entry.mjs').read_text()
s = once(s, "import {materializeNormal,normalRoot} from './materialize-normal.mjs';", "import {materializeContinuous,root as normalRoot} from './adapt.mjs';")
s = once(s, "import {processIdentity} from './normal-policy.mjs';", "import {processIdentity} from '../resident-normal-dev-i-20261008/normal-policy.mjs';")
s = s.replace('materializeNormal(runtimeRoot', 'materializeContinuous(runtimeRoot')
s = once(s, "const timer=setTimeout(()=>child.kill(),seconds*1000);", "const timer=seconds===null?null:setTimeout(()=>child.kill(),seconds*1000);")
s = once(s, "runtimeRoot+'/pilot-supervisor.mjs',420", "runtimeRoot+'/pilot-supervisor.mjs',null")
s = s.replace('activeOwnerEndsByOriginalDeadline:true', 'activeOwnerGracefulStop:true')
(root/'normal-entry.mjs').write_text(s)

s = (normal/'run-generation.mjs').read_text()
s = once(s, "import {normalRoot} from './materialize-normal.mjs';", "import {root as normalRoot} from './adapt.mjs';")
s = once(s, "Date.now()/1000>=until", "Number.isFinite(until)&&Date.now()/1000>=until")
s = s.replace('activeOwnerEndsByOriginalDeadline:true', 'activeOwnerGracefulStop:true')
s = once(s, "renewals=record.renewals.length", "renewals=record.totalRenewals??record.renewals.length")
(root/'run-generation.mjs').write_text(s)

s = (service/'generation-outcome.mjs').read_text()
s = s.replace("../resident-normal-dev-i-20261008/run-generation.mjs", "./run-generation.mjs")
(root/'generation-outcome.mjs').write_text(s)

s = (root/'daemon.mjs').read_text()
s = s.replace("import {verifyLocalBatch} from '../resident-normal-dev-i-20261008/qualification.mjs';", "import {verifyLocalBatch} from './qualification.mjs';")
s = once(s, 'Date.now()/1000+servicePlan.generationCutoffSeconds', 'Infinity')
s = once(s, 'uninterruptedNssClaim:false});', 'uninterruptedNssClaim:false,continuousQualifiedResidency:true,fixedSessionLimitSeconds:null,fixedOwnerLimitSeconds:null});')
(root/'daemon.mjs').write_text(s)

s = (root/'service.ps1').read_text()
s = s.replace('manual resident pilot; finite 90-second generations', 'continuous qualified resident controller; rolling leases')
(root/'service.ps1').write_text(s)
print('Continuous entry and service prepared locally; production untouched')
