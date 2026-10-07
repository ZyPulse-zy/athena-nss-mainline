from pathlib import Path
import json, hashlib

root=Path('work/v57-resident-bootstrap')
prior=Path('work/v55-resident-trial')
assert not (root/'materialize.mjs').exists()
names=['entry.mjs','materialize.mjs','check-model.mjs','platform-preflight.mjs','fixture-startup.mjs','ssh-phase.mjs','ssh-options.mjs','recheck-endpoint-readonly.mjs','udp-probe.py','udp-probe.mjs','check-udp-path.mjs','recheck-partial-endpoint.mjs','capture-no-client-closure.ps1','resident-window.mjs']
origins={}
for name in names:
    raw=(prior/name).read_bytes();origins[str(prior/name)]=hashlib.sha256(raw).hexdigest()
    s=raw.decode().replace('v55-resident-trial','v57-resident-bootstrap').replace('v55-run-','v57-run-')
    (root/name).write_bytes(s.encode())
helper=Path('work/v56-control-bootstrap/persistent-ssh.mjs').read_bytes()
(root/'persistent-ssh.mjs').write_bytes(helper.replace(b'v55-resident-trial',b'v57-resident-bootstrap'))
p=root/'materialize.mjs';s=p.read_text()
s="import{patchControlledReader,patchNaturalAcquisition,patchMatcher}from'./route-acquisition.mjs';\n"+s
needle="  if(name==='persistent-ssh.mjs'){bytes=fs.readFileSync(entryRoot+'/persistent-ssh.mjs');}"
assert s.count(needle)==1
s=s.replace(needle,needle+"\n  if(name==='read-controlled.mjs'){bytes=Buffer.from(patchControlledReader(bytes.toString()));}\n  if(name==='acquisition-plan.mjs'){bytes=Buffer.from(patchNaturalAcquisition(bytes.toString()));}\n  if(name==='match-controlled.mjs'){bytes=Buffer.from(patchMatcher(bytes.toString()));}")
needle="'persistent-ssh.mjs','resident-window.mjs']"
assert s.count(needle)==1;s=s.replace(needle,"'persistent-ssh.mjs','resident-window.mjs','route-acquisition.mjs']")
p.write_bytes(s.encode())
p=root/'check-model.mjs';s=p.read_text();needle="const receipt=entryRoot+'/model-'";assert s.count(needle)==1
s=s.replace(needle,"test('owned transport routes aid rotation without granting NSS class',()=>{const s=fs.readFileSync(root+'/read-controlled.mjs','utf8');assert.ok(s.includes('export async function readControlled()'));assert.ok(s.includes('ownedTransportRoutes'));assert.ok(s.includes(\"f.decision.class==='BULK'\"));assert.ok(s.includes(\"f.decision.class==='RT'&&f.decision.budgetAdmitted\"));const m=fs.readFileSync(root+'/match-controlled.mjs','utf8');assert.ok(m.includes('await readControlled()')&&m.includes('finally{closeControlledReader();}'));});\n"+needle)
p.write_bytes(s.encode())
(root/'preparation.json').write_text(json.dumps({'passed':True,'originalSources':origins,'compactBootstrapSourceSha256':hashlib.sha256(helper).hexdigest(),'sourceFreshnessSeconds':6,'naturalAcquisitionSeconds':30,'slotMaximumAttempts':8,'firstPayloadSeconds':8,'residentCandidateSeconds':90,'nativeMaximumSeconds':120,'ownerSeconds':180,'clientSeconds':180,'productionExecuted':False},indent=2)+'\n')
print(json.dumps({'passed':True,'newNamespace':str(root),'productionExecuted':False}))
