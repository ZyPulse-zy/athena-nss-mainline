"""Check only the normal-controller milestone facts and curated source bytes."""
from pathlib import Path
import hashlib,json,sys

def check(root):
 read=lambda p:json.loads((root/p).read_text(encoding='utf8'))
 h=read('evidence/resident-normal-controller.json');s=read('evidence/resident-normal-source-proof.json');m=read('source-manifest.json')
 assert h['developmentMode'] and h['restorationPassed'] and h['simulatedNormalConnectionTurnover']
 assert h['localChecks']==57 and h['syntaxSources']==15 and h['allSevenDataPlaneLuaByteExactWithRc1']
 assert not any(h[k] for k in ['normalProductControllerCreatesTraffic','permanentDefaultNss','uninterruptedFifteenMinuteNssProved','cs2OrSteamOperated','newCpuBenchmark'])
 p=h['plan'];assert p['maximumGenerations']==4 and p['phaseSeconds']==90 and p['minimumControllerSeconds']==900 and p['maximumControllerSeconds']==1200
 assert p['sourceSeconds']==6 and p['kernelMaximumSeconds']==120 and p['ownerSeconds']==p['clientSeconds']==180 and p['automaticFixtureRetries']==0
 assert len(h['windows'])<=4
 for x in h['windows']:
  assert x['restorationPassed'] and x['ecmClosedAndZero'] and x['allFiveWanHealthy'] and x['protectedConfigurationUnchanged'] and x['physicalQueuesOptionsAndHandlesExact']
  assert x['ownedEndpointRulesRemaining']==x['ownedClientProcessesRemaining']==0 and x['endpointBaselineRestored'] and x['finalAuditSourceAge']<6
  if x['hardwareCompleted']:
   assert 90<=x['nssSeconds']<=91.5 and x['samples']==181 and x['renewals']==30 and x['allBSamplesEcmThree']
   assert x['actualNormalProcessOwnershipChecked'] and x['ctMarkNatWanAffinityAndTagsCorrect'] and x['freshCheckpointDownloadedShaGzipVerified'] and x['independentRestoreVerifiedBeforeWrite']
   assert x['selectedWanBySlot']['tcp']!=x['selectedWanBySlot']['tcp2']
 if h['integrationPassed']:
  assert h['controllerState']=='COMPLETE' and len(h['windows'])==4 and all(x['hardwareCompleted'] for x in h['windows'])
  assert 900<=h['controllerSeconds']<=1200 and 360<=h['nssSeconds']<=366
 assert s['passed'] and s['oldCodeEvidenceUnmodified'] and s['noPrivateRuntimeInputsExported'] and s['milestonePublicationOnly']
 assert m['normalResidentExport']=='NORMAL_SOURCE_AND_FOUR_GENERATION_BOUNDED_COORDINATION'
 # This completed milestone keeps its exact ordered manifest slice when a
 # subsequent deployment milestone appends new sources.
 end=s['historicalSourcePrefix']+s['newSources']
 assert len(m['sources'])>=end and len(s['sourceHashes'])==s['newSources']
 assert {x['workspaceSource']:x['sha256'] for x in m['sources'][s['historicalSourcePrefix']:end]}==s['sourceHashes']
 for rel,expected in s['sourceHashes'].items():assert hashlib.sha256((root/'code'/rel).read_bytes()).hexdigest()==expected,rel
 return {'passed':True,'normalIntegrationPassed':h['integrationPassed'],'generations':len(h['windows']),'newSourceHashesChecked':s['newSources']}

if __name__=='__main__':print(json.dumps(check(Path(sys.argv[1]).resolve())))
