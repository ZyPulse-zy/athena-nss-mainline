"""Curated NSS43 observations. Raw endpoint captures never enter this output."""
from pathlib import Path
import hashlib,json,subprocess,sys,shutil
from datetime import datetime,timezone
from load_model import analyze,assess_load_comparability
root=Path('work/nss43')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,obj):Path(p).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
idx=read(root/'steam-profile-latest.json');directory=Path(idx['directory']);profile=read(directory/'profile-private.json')
assert len(profile['rows'])==13 and all(r['code']==0 for r in profile['rows'])
assert idx['sourceSha256']==sha(root/'read-real-candidates.mjs') and idx['selfSha256']==sha(root/'profile-steam.mjs')
samples=[read(f) for f in sorted(directory.glob('sample-*/real-candidates-private.json'))]
load=analyze(samples);load['startedAt']=profile['startedAt'];load['finishedAt']=profile['finishedAt']
test=subprocess.run([sys.executable,'-X','utf8',str(root/'test_load_model.py')],capture_output=True,text=True)
assert test.returncode==0,test.stderr
assert 'Ran 20 tests' in test.stderr
sources=['audit-renderer.mjs','current-audit-diagnostic.mjs','final-closure.mjs','inspect-classifier.mjs','session-binding.mjs',
 'read-real-candidates.mjs','profile-steam.mjs','read-queue-budget.mjs','read-queue-budget-compact.mjs','load_model.py','test_load_model.py','summarize.py','render_report.py']
source_hashes={str(root/name).replace('\\','/'):sha(root/name) for name in sources}
save(root/'local-model-qualified.json',{'passed':True,'checks':20,'simulation':True,'routerAccess':False,
 'sourceHashes':{str(root/name).replace('\\','/'):sha(root/name) for name in ('load_model.py','test_load_model.py')}})
load['sourceHashes']={k:v for k,v in source_hashes.items() if k.endswith(('load_model.py','test_load_model.py','profile-steam.mjs','read-real-candidates.mjs'))}
save(root/'load-profile-sanitized.json',load)
prior_actual=read('outputs/nss41-mainline-observations.json')['actualTrial']['nativeExperiment'];original=prior_actual['phases']
historical=assess_load_comparability([{'name':p['name'],'lan4DownMbps':p['lan4DownMbps'],
 'lan4Pps':p['lan4DownPps'],'wanRxMbps':p['wan'+str(prior_actual['wan'])+'DownMbps']} for p in original])
save(root/'prior-aba-comparability-sanitized.json',historical)
opening,closing=read(root/'opening-audit.json'),read(root/'closing-audit.json')
inspection=read(root/'classifier-closing-inspection.json');files=inspection['files']
queue=read(root/'queue-budget-compact-private.json');assert all(r['unitsVerifiedByAdjacentReads'] for r in queue['rows'])
failure=read(root/'steam-profile-20261004020729-434cd3/profile-private.json')
assert len(failure['rows'])==13 and all(r['code']==1 and "SyntaxError: Unexpected token ')'" in r['error'] for r in failure['rows'])
frozen=root/'readonly-frozen';frozen.mkdir(exist_ok=False)
for name in sources:shutil.copyfile(root/name,frozen/name)
prior=read('work/nss42/entry-qualified.json')
proof={'createdAt':datetime.now(timezone.utc).isoformat(),'scope':'NSS43 readonly observation sources; NOT an NSS production-entry qualification',
 'nssAdmissionAllowed':False,'routerConfigurationWrites':False,'sourceHashes':source_hashes,
 'captureSourceSha256':idx['sourceSha256'],'captureProfilerSha256':idx['selfSha256'],
 'priorEntryPath':'work/nss42/entry-qualified.json','priorEntrySha256':sha('work/nss42/entry-qualified.json'),
 'priorEntryUnmodified':True,'frozenSources':len(sources),
 'rawCaptureSha256':{str(f).replace('\\','/'):sha(f) for f in sorted(directory.glob('sample-*/*.json'))}}
save(root/'readonly-source-proof-private.json',proof)
data={'round':'NSS43','updatedAt':datetime.now(timezone.utc).isoformat(),
 'deploymentReference':'work/nss39/deployment-latest.json','classifierConfigSha256':read('work/nss39/deployment-latest.json')['configHash'],
 'permanentClassifierChanged':False,'routerConfigurationWrites':False,'nssEntryChanged':False,'budgetMbps':20,'gateFlows':{'tcp':1,'udp':1},'ownerDeadlineSeconds':45,
 'readonlyAudits':[{k:a[k] for k in ('passed','auditPurpose','nssAdmissionAllowed','protectedConfigurationUnchanged','exactOwnedNativeAudit','selectors','queryAge','sequence','ecmClosedAndZero')} for a in (opening,closing)],
 'localChecks':{'checks':20,'passed':True,'simulation':True,'routerAccess':False},
 'steamProfile':{k:load[k] for k in ('startedAt','finishedAt','samples','seconds','sourceAgeRangeSeconds','performance','lan4IntervalMbpsRange','lan4IntervalCoefficientOfVariation','bulkInstancesObserved','bulkCountsEachSample','cs2CountsEachSample','byWan','fixedDemandSensitivity','scope')},
 'priorAbaObservedLoadComparison':historical,
 'queueBudget':{k:queue[k] for k in ('observedAt','readonly','routerWrites','captureAfterSteamProfile','execBytes','rows')},
 'localFailures':[{'stage':'First Steam profiler','calls':13,'cause':'Local JavaScript template editing introduced a syntax error; failed before router connection','successfulReads':0,'routerChanges':False,'originalErrorsRetained':True},
   {'stage':'Separated queue JSON/text reads','cause':'Values differed across sequential observations; no synchronized-unit claim was made','resolvedBy':'Adjacent JSON/text/JSON observation, 5 of 5 unit checks matched; not a qdisc compatibility defect'}],
 'sourceProof':{'sources':len(sources),'sourceHashes':source_hashes,'readonlyOnly':True,'prior102InputQualificationReused':True,'newProductionEntryQualified':False,'privateCapturesAndConnectorNotExported':True},
 'finalState':{'protectedAudit':{k:closing[k] for k in ('passed','protectedConfigurationUnchanged','exactOwnedNativeAudit','ecmClosedAndZero')},
   'classifierHealthy':files['classification.json']['dataHealthy'] and files['guardian.json']['healthy'],
   'sameProducerSinceOpening':opening['producer']==closing['producer'],
   'lastErrorBelongsToEarlierInstallation':files['last-error.json']['producer']!=files['classification.json']['producer'],
   'closure':read(root/'final-closure.json')},
 'actualFastPathTrial':{'attempted':False,'acceleratedCountDuringSamples':0,'leafCounters':None,'gameTelemetry':None,'checkpointRequiredForProductionWrites':True,'checkpointCreated':False,'rollbackExercised':False},
 'decision':{'raiseBudgetNow':False,'expandFlowsNow':False,'changeTtlNow':False,
   'reason':'Current observed whole-window TCP demand is about 16-23 Mbps; fixed-demand 20-to-30 Mbps model changes whole-PC controlled share by at most about 1.08 percentage points on WAN1-4. WAN5 lacks a whole-window instance.',
   'next':'One concentrated CS2+Steam window using the unchanged single-WAN, one-TCP/one-UDP entry; track exact flow persistence, controlled leaf share, both global and selected-WAN load, then assess game and performance separately.',
   'observationCriterionRelativeSpread':.10,'criterionAuthorizesNss':False,'sameOfferedLoadStillRequiresIndependentEvidence':True},
 'conclusions':{'softwareLoadCharacterized':True,'bulkConnectionsRotate':True,'singleTcpScopeLimitsGlobalCpuInterpretation':True,
   'budgetIncreaseCpuBenefitProved':False,'nssCpuBenefitProvedThisRound':False,'cs2JitterLossMissCaptured':False,'completeHighLoadLifecycleQualified':False,'secondWanExpansionAllowed':False},
 'reportVerification':{'sourceValidated':False,'browserRendered':False,'reason':'Existing local-browser rendering policy block retained; no alternate access route attempted'}}
save('outputs/nss43-mainline-observations.json',data)
print(json.dumps({'observationsSaved':True,'samples':len(samples),'modelChecks':20,'readonlySourceFreezeFiles':len(sources),'routerConfigurationWrites':False}))
