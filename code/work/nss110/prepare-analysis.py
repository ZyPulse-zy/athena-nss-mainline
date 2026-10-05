from pathlib import Path
r=Path('work/nss110');s=Path('work/nss100/analyze-long.py').read_text(encoding='utf-8')
s=s.replace("'schema':'nss100-long-controlled-actual-v1'","'schema':'nss110-long-controlled-actual-v1'")
s=s.replace("'qosBytesUnchanged':False","'qosBytesUnchanged':True")
s=s.replace("'protectedConfigurationRestored':json.loads((case/'baseline-audit.json').read_text())['configurationMatches']", "'protectedConfigurationRestored':False,'originalRecoveryAuditRejected':True,'singleWanStageRestored':all(json.loads((case/'stage-undo-verified.json').read_text()).values()),'latestDeclaredReadonlyClosurePassed':json.loads(Path('work/nss110/v2-final-health.json').read_text())['passed']")
(r/'analyze-long.py').write_text(s,encoding='utf-8')
print('Prepared actual metrics with original rejection retained')
