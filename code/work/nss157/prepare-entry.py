from pathlib import Path
r=Path(__file__).resolve().parent;old=r.parent/'nss156'
copies={'start-dallas.mjs':'start-dallas-v7.mjs','read-controlled.mjs':'read-controlled-v7.mjs','match-controlled.mjs':'match-cohort.mjs','module-stage.mjs':'module-stage.mjs','current-audit-diagnostic.mjs':'current-audit-diagnostic.mjs','close-control.mjs':'close-control.mjs','close-endpoint.mjs':'close-endpoint.mjs'}
for n in ['cohort-client.mjs','upload-ack.mjs','bounded-pacer.mjs','cohort-policy.mjs','upload-server.py','server.py','receiver.py','discover-peer.py','probe-peer.py','client-watchdog.ps1','endpoint-firewall-guardian.py','crash-read.lua','module-stage-guardian.lua']:
 copies[n]=n
for dst,src in copies.items():
 s=(old/src).read_text(encoding='utf-8')
 if dst not in ['cohort-client.mjs','upload-ack.mjs','bounded-pacer.mjs','cohort-policy.mjs','upload-server.py','server.py','receiver.py','discover-peer.py','probe-peer.py','client-watchdog.ps1','endpoint-firewall-guardian.py','crash-read.lua','module-stage-guardian.lua']:
  s=s.replace('work/nss156','work/nss157').replace('work\\/nss156','work\\/nss157').replace('nss156-','nss157-').replace('NSS156','NSS157').replace('read-controlled-v7.mjs','read-controlled.mjs').replace('session-binding-v7.mjs','session-binding.mjs')
 if dst=='module-stage.mjs':s=s.replace("'./payload.mjs'","'./payload-v2.mjs'")
 p=r/dst;assert not p.exists();p.write_text(s,encoding='utf-8',newline='')
s=(old/'epoch-driver-v7.mjs').read_text(encoding='utf-8').replace('work/nss156','work/nss157').replace('session-binding-v7.mjs','session-binding.mjs').replace('read-controlled-v7.mjs','read-controlled.mjs').replace("observationRoot='work/nss157'","observationRoot='work/nss157'")
s=s.replace("['work/nss157/run7/continuity-private.json','work/nss157/run7/successor-continuity-private.json']","['work/nss157/run1/continuity-private.json','work/nss157/run1/successor-continuity-private.json','work/nss157/run2/continuity-private.json','work/nss157/run2/successor-continuity-private.json']")
anchor="if(expectedExit){assert.equal(latest.flowEligibilityExitCompleted,true);";assert s.count(anchor)==1
s=s.replace(anchor,"if(expectedExit){if(expectedExit==='change'){assert.equal(latest.classChangeTestCompleted,true);assert.equal(latest.terminalInvalidation.reason,'AUTHENTICATED_BULK_TO_BE');assert.equal(latest.terminalInvalidation.exactSingleCiRetirementClaimed,true);save('actual-remaining-udp-proof',validateAcceleratedState(latest.remainingUdpState,selected,true));}assert.equal(latest.flowEligibilityExitCompleted,true);")
s=s.replace('automaticLifecycleEpochCompleted:completed&&!expectedExit,','classLifecycleCompleted:completed&&expectedExit===\'change\',automaticLifecycleEpochCompleted:completed&&!expectedExit,')
p=r/'epoch-driver.mjs';assert not p.exists();p.write_text(s,encoding='utf-8',newline='')
s=(r.parent/'nss151/transition-policy.mjs').read_text(encoding='utf-8')
s=s.replace("assert.equal(result.mode,'change')","assert.equal(result.mode,'epoch')").replace("'unchangedQoSPlan','fastPathEpochCompleted','explicitEarlyRetirement'","'unchangedQoSPlan','explicitEarlyRetirement'")
s=s.replace("assert.equal(r.expiredState,'');","assert.equal(r.terminalPairFirmwareZero,true);assert.equal(r.flowEligibilityExitCompleted,true);assert.equal(r.fastPathEpochCompleted,false);assert.equal(r.terminalInvalidation.reason,'AUTHENTICATED_BULK_TO_BE');assert.equal(r.terminalInvalidation.exactSingleCiRetirementClaimed,true);assert.equal(r.terminalInvalidation.ctExitInferredFromProjection,false);")
s=s.replace('assert.equal(r.fastPathMeasurement.qualified,true);','assert.equal(r.fastPathMeasurement.qualified,false);assert.equal(r.fastPathMeasurement.terminalLifecycleOnly,true);')
p=r/'combined-policy.mjs';assert not p.exists();p.write_text(s,encoding='utf-8',newline='')
print('Combined entry uses exact run1/run2 inputs, existing fixed budgets, and fresh checkpoint/owner per epoch.')
