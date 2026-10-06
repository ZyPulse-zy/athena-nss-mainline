"""Fresh namespace; reuse qualified NSS152 native factories and fixed budgets."""
from pathlib import Path
r = Path(__file__).resolve().parent
old = r.parent / 'nss152'
def put(name, text):
    target = r / name
    assert not target.exists(), name
    target.write_text(text, encoding='utf-8', newline='')
files = {'start-dallas-v3.mjs':'start-dallas.mjs', 'match-controlled-v3.mjs':'match-controlled.mjs', 'read-controlled-v3.mjs':'read-controlled.mjs', 'epoch-session-v4.mjs':'epoch-session.mjs', 'current-audit-diagnostic-v4.mjs':'current-audit-diagnostic.mjs', 'crash-controller-v4.mjs':'supervisor.mjs'}
for name in ['client.mjs','ssh-client.mjs','client-guard.ps1','server.py','upload-server.py','upload-ack.mjs','discover-peer.py','probe-peer.py','endpoint-firewall-guardian.py','close-endpoint.mjs','failed-wan-owner.lua','declared-baseline.mjs','crash-read.lua']:
    files[name] = name
for source, name in files.items():
    s = (old / source).read_text(encoding='utf-8')
    s = s.replace('work/nss152', 'work/nss153').replace('work\\/nss152', 'work\\/nss153').replace('nss152-', 'nss153-').replace('NSS152', 'NSS153')
    for a,b in [('session-binding-v4.mjs','session-binding.mjs'),('current-audit-diagnostic-v4.mjs','current-audit-diagnostic.mjs'),('epoch-session-v4.mjs','epoch-session.mjs'),('start-dallas-v3.mjs','start-dallas.mjs'),('read-controlled-v3.mjs','read-controlled.mjs'),('match-controlled-v3.mjs','match-controlled.mjs'),('/run-v4/','/run1/'),("out=root+'/run-v4'", "out=root+'/run1'"),('frozen-qualified-inputs-v4','frozen-qualified-inputs'),('entry-source-manifest-v4.json','entry-source-manifest.json')]:
        s = s.replace(a,b)
    if name == 'supervisor.mjs':
        s = s.replace("import{requireOwnedUpload}from'../nss151/transition-policy.mjs';", "import{requireOwnedUpload,allowSuccessor,validateStableEpoch}from'../nss151/transition-policy.mjs';\nimport{validateRecoveredEpoch}from'./recovery-policy.mjs';")
        s = s.replace("events=[];let started=false", "events=[],history=[];let started=false")
        s = s.replace("exact owned controller crash", "finite supervisor crash and automatic successor")
        original = "console.log(JSON.stringify({passed:true,independentCrashRecovery:true,nativeRenewals:latest.renewals.length,allOriginalStateRestored:true}));"
        assert s.count(original) == 1
        successor = """
 const firstBundle={record:latest,plan:ctx.plan,checkpoint:read(caseDir,'stage-checkpoint-verified'),undo:read(caseDir,'stage-undo-verified'),detached:read(caseDir,'stage-detached-private'),receipt:ctx.receipt,baseline:read(out,'baseline-audit'),classified:read(caseDir,'post-checkpoint-class-leaf-map-proof'),ecm:validateAcceleratedState(latest.acceleratedState,selected),frame:read(caseDir,'post-checkpoint-controlled-receipt-private'),crash:read(out,'controller-crash-private'),parentRecovery:read(out,'independent-crash-result'),normalHostReceiptPresent:fs.existsSync(caseDir+'/result.json')};
 history.push(validateRecoveredEpoch(firstBundle,selected));save('recovered-first-epoch-private',firstBundle);save('history-private',{history,cases:[caseDir]});
 console.log(JSON.stringify({independentCrashRecovery:true,nativeRenewals:latest.renewals.length,allOriginalStateRestored:true,successorStillNotAdmitted:true}));
 save('successor-policy-private',allowSuccessor(history));save('successor-lifetime',requireOwnedUpload(config,read(load.dir,'status-private'),load));
 await run(root+'/read-controlled.mjs',[],20);const newFrame=read(root,'controlled-candidates-private');assert.ok(newFrame.pairs.some(p=>JSON.stringify(p)===JSON.stringify(selected)),'Exact original pair no longer completely classified');
 const next=await run(root+'/epoch-session.mjs',['epoch',out+'/continuity-private.json'],145);assert.equal(next.passed,true);save('successor-reference',next);
 const bundleNames={result:'result',record:'last-record-private',plan:'stage-plan-private',checkpoint:'stage-checkpoint-verified',undo:'stage-undo-verified',detached:'stage-detached-private',receipt:'stage-receipt-private',baseline:'baseline-audit',classified:'post-checkpoint-class-leaf-map-proof',ecm:'actual-accelerated-state-proof',frame:'post-checkpoint-controlled-receipt-private'};
 const nextBundle=Object.fromEntries(Object.entries(bundleNames).map(([key,name])=>[key,read(next.output,name)]));history.push(validateStableEpoch(nextBundle,selected,history[0]));save('history-private',{history,cases:[caseDir,next.output]});
 save('automatic-result',{passed:true,completedEpochs:history.length,controllerActuallyKilled:true,routerGuardianCompletedWithoutPcController:true,automaticSuccessorAfterVerifiedRestoration:true,newQueryCheckpointOwnerPinAndBothCis:true,sameSocketCtMarkNatWan:true,oldTerminalGateNeverReopened:true,finiteTwoEpochBudgetKept:true,matchedCpuComparison:false,cs2Acceptance:false,permanentNssDeployment:false});
 console.log(JSON.stringify({passed:true,completedEpochs:2,actualCrashThenAutomaticRelearning:true,sameSocketCtMarkNatWan:true}));
"""
        s = s.replace(original, successor)
        s = s.replace("process.exitCode=1;save('independent-crash-result',{passed:false", "process.exitCode=1;save('automatic-result',{passed:false,completedEpochs:history.length").replace("controllerKilled:killed,furtherAdmissionStopped:true", "controllerKilled:killed,furtherAdmissionStopped:true")
    put(name,s)
print('Fresh finite supervisor prepared; factories 149, source/native/owner/client and byte budgets unchanged.')
