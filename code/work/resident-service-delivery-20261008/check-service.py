"""Check the manual resident process deployment, without inventing hardware facts."""
from pathlib import Path
import hashlib,json,sys

def check(root):
 read=lambda p:json.loads((root/p).read_text(encoding='utf-8'))
 h=read('evidence/resident-service-runtime.json');s=read('evidence/resident-service-source-proof.json');m=read('source-manifest.json')
 assert h['manualResidentPilotStarted'] and h['gracefulStopAndRestartPassed'] and h['originalNormalEntryUnmodified']
 assert h['localChecks']==18 and h['javascriptSyntaxSources']==8 and h['powershellSyntaxSources']==2
 assert h['unchangedHistoricalNormalSoakReused'] and h['sevenDataPlaneLuaUnmodified']
 assert h['newHardwareGenerations']==0 and not h['newNssHardwareAcceptanceClaim']
 assert not any(h[k] for k in ['automaticStartAtLogon','automaticRestartOnFailure','trafficGenerated','cs2OrSteamOperated','newCpuBenchmark','uninterruptedNssClaim'])
 p=h['plan'];assert p['phaseSeconds']==90 and p['sourceSeconds']==6 and p['kernelMaximumSeconds']==120 and p['ownerSeconds']==p['clientSeconds']==180
 assert p['maximumGenerationsPerWindow']==4 and p['windowSeconds']==1200 and p['generationCutoffSeconds']==600 and p['retainedObservationGroups']==16
 assert h['first']['reads']<h['progress']['reads'] and h['first']['sourceSequence']<h['progress']['sourceSequence']
 assert h['stopped']['state']=='STOPPED' and h['stopped']['restorationPassed'] and not h['stopped']['running'] and not h['stopped']['controllerLockPresent'] and not h['stopped']['activeGenerationLockPresent']
 r=h['retained'];assert r['state']=='WAITING_FLOW' and r['running'] and r['identityVerified'] and r['heartbeatFresh'] and r['reads']>=2 and r['generationsStarted']==0
 assert r['lastObservation']['triples']==0 and not r['activeGenerationLockPresent']
 for a in h['startupHealth']:
  assert a['passed'] and a['queryAge']<6 and a['ecmClosedAndZero'] and a['allFiveHealthyWanBaseline'] and a['protectedConfigurationUnchanged'] and a['physicalQueuesOptionsAndHandlesExact']
 t=h['task'];assert t['knownTaskFingerprintsUnchanged']==4 and t['logonTriggerCount']==t['restartCount']==0 and t['runLevel']=='Limited' and t['hardTerminationDisabled'] and t['unlimitedProcessResidence']
 assert s['passed'] and s['noPrivateRuntimeInputsExported'] and s['historicalCodeEvidenceUnmodified'] and s['historicalSourcePrefix']==5939
 assert m['residentServiceExport']=='MANUAL_RESIDENT_PROCESS_NORMAL_FLOW_WAITING'
 end=s['historicalSourcePrefix']+s['newSources'];assert len(m['sources'])>=end
 assert {x['workspaceSource']:x['sha256'] for x in m['sources'][s['historicalSourcePrefix']:end]}==s['sourceHashes']
 for p,expected in s['sourceHashes'].items():assert hashlib.sha256((root/'code'/p).read_bytes()).hexdigest()==expected,p
 return{'passed':True,'manualResidentProcessDeployed':True,'newHardwareGenerations':0,'sourceHashesChecked':s['newSources']}

if __name__=='__main__':print(json.dumps(check(Path(sys.argv[1]).resolve())))
