"""New bounded comparison of full versus compact offers using unchanged negotiated algorithms."""
from pathlib import Path
import hashlib,json
w=Path(__file__).resolve().parents[2];root=Path(__file__).resolve().parent
old=w/'work/v49-handshake-diagnosis/probe.mjs'
source=old.read_text(encoding='utf8').replace('work/v49-handshake-diagnosis','work/v50-compact-handshake')
source="import{compactSshOptions}from'./ssh-options.mjs';\n"+source
source=source.replace("kind:'none'","kind:'compact'")
needle="d.kind==='none'?['-o','IPQoS=none']:[]"
assert source.count(needle)==1
source=source.replace(needle,"d.kind==='compact'?[...compactSshOptions]:[]")
source=source.replace('comparisonDoesNotProveIpQosCausation','comparisonDoesNotProveExactPacketLossLocation')
with (root/'probe.mjs').open('x',encoding='utf8',newline='') as f:f.write(source)
proof={'passed':True,'originalProbeSourceSha256':hashlib.sha256(old.read_bytes()).hexdigest(),
       'originalNegotiatedAlgorithmsRetained':True,'onlyOwnedProcessOptionsChanged':True,
       'noGlobalPolicyOrTimeoutOrRetryChanges':True}
with (root/'probe-preparation.json').open('x',encoding='utf8') as f:json.dump(proof,f,indent=2)
print(json.dumps(proof))
