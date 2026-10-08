import hashlib,json
def check(root):
 e=json.loads((root/'evidence/resident-continuous.json').read_text(encoding='utf-8'));assert e['passed']
 i=e['implementation'];assert all(i[k] is None for k in ['fixedNssPhaseSeconds','fixedGenerationCutoffSeconds','maximumGenerationsPerWindow','windowSeconds'])
 assert i['healthyQualifiedLifetimeIndefinite'] and not i['safetyWatchdogsRemoved'];assert (i['freshClassificationSeconds'],i['freshSocketOwnershipSeconds'],i['nativeRollingWindowSeconds'],i['guardianRollingWindowSeconds'],i['controlHeartbeatLossSeconds'])==(6,6,120,180,30)
 h=e['actualIntegration'];assert h['completed'] and h['activeMask']==2 and h['nssSeconds']>=190 and h['renewals']>60 and h['samplesValidated']>370 and h['operatorStopPassed'] and h['restorationPassed'];assert h['retainedSamplesEcm1'] and h['retainedSamples']<=32 and h['retainedRenewals']<=16 and h['recordBytes']<1048576 and h['nativeSessionAdvanceMs']>180000 and h['guardianExtendedBeyondInitialDeadline']
 assert all(e['restoration'].values());assert e['originalFailures']['preserved'] and not e['originalFailures']['nssRootCauseClaimed'];assert e['retainedService']['running'] and e['retainedService']['startupHealthPassed'] and e['retainedService']['identityVerified'];assert not e['scope']['privateInputsExported'];assert e['regression']['nativeControlChecks']==4409 and e['regression']['batchChecks']==27
 p=e['prewriteProtection'];assert p['freshCheckpointDownloadedShaAndGzipVerified'] and p['independentDetachedRollbackVerifiedBeforeFirstWrite'] and p['independentUndoVerified'] and p['stageExecBytes']<=9000 and p['bundleBytes']<=73728
 for p,h in e['sourceHashes'].items():assert hashlib.sha256((root/'code'/p).read_bytes()).hexdigest()==h,p
 assert hashlib.sha256((root/'code/work/resident-continuous-dev-20261008/endpoint-gate/rp_ecm_gate_lab_ct.c').read_bytes()).hexdigest()==e['actualIntegration']['nativeSourceSha256']
