from pathlib import Path
import json
r=Path(__file__).resolve().parent
f=r/'prequalification-v1';f.mkdir()
for name in ['supervisor.mjs','recovery-policy.mjs','policy-checks.mjs','qualify.mjs']:
    (f/name).write_bytes((r/name).read_bytes())
(r/'policy-prequalification-refusal-private.json').write_text(json.dumps({'passed':False,'policyRejectedLegacyReceiptWithoutExplicitSignal':True,'newNamespaceMissingBoundedPacerRejected':True,'routerConnectionAttempted':False,'productionWrites':False})+'\n',encoding='utf-8')
s=(r/'supervisor.mjs').read_text(encoding='utf-8')
s=s.replace("child.once('close',code=>r(code))", "child.once('close',(code,signal)=>r({code,signal}))")
s=s.replace("const exit=await closed;assert.notEqual(exit,0);", "const termination=await closed;assert.ok(termination.code!==0&&(Number.isInteger(termination.code)||termination.signal==='SIGTERM'));const exit=termination.code;")
s=s.replace("exitCode:exit,ownedSpawnProcessOnly:true", "exitCode:exit,terminationSignal:termination.signal,ownedKillReturnedTrue:killed,ownedSpawnProcessOnly:true")
s=s.replace("if(child&&child.exitCode===null)", "if(child&&child.exitCode===null&&child.signalCode===null)")
(r/'supervisor.mjs').write_text(s,encoding='utf-8',newline='')
s=(r/'recovery-policy.mjs').read_text(encoding='utf-8').replace("assert.ok(Number.isInteger(crash.exitCode) && crash.exitCode !== 0);", "assert.equal(crash.ownedKillReturnedTrue,true);\n  assert.ok((Number.isInteger(crash.exitCode)&&crash.exitCode!==0)||(crash.exitCode===null&&crash.terminationSignal==='SIGTERM'),'Explicit abnormal child termination required');")
(r/'recovery-policy.mjs').write_text(s,encoding='utf-8',newline='')
s=(r/'policy-checks.mjs').read_text(encoding='utf-8')
s=s.replace("const history=validateRecoveredEpoch(fixture,selected);", "assert.throws(()=>validateRecoveredEpoch(fixture,selected));\n// Explicit model-only signal fields; the legacy native record remains actual.\nfixture.crash.ownedKillReturnedTrue=true;fixture.crash.terminationSignal='SIGTERM';\nconst history=validateRecoveredEpoch(fixture,selected);")
s=s.replace("x=>x.crash.exitCode=0,", "x=>x.crash.exitCode=0,x=>x.crash.terminationSignal=null,x=>x.crash.ownedKillReturnedTrue=false,")
s=s.replace("historicalActualCompleteRecordAccepted:1", "historicalNativeRecordWithExplicitModelTerminationAccepted:1,legacyMissingTerminationRefused:true,terminationProvenancePartlyModelOnly:true")
(r/'policy-checks.mjs').write_text(s,encoding='utf-8',newline='')
src=r.parent/'nss152/bounded-pacer.mjs';assert src.is_file();(r/'bounded-pacer.mjs').write_bytes(src.read_bytes())
s=(r/'qualify.mjs').read_text(encoding='utf-8').replace("'prepare-v3.py',", "'prepare-v3.py','prepare-final.py','bounded-pacer.mjs',").replace('newParentPolicyRefusals===12','newParentPolicyRefusals===14').replace('newChecks:12,historicalRecord:1','newChecks:14,nativeRecordModelTermination:1')
(r/'qualify.mjs').write_text(s,encoding='utf-8',newline='')
print('Explicit termination signal and dependency coverage prepared before connection; original refusals kept.')
