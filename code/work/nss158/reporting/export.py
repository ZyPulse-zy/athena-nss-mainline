"""Seal actual NSS157 lifecycle and NSS158 ABA without changing old evidence."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib,subprocess,copy,html
w=Path(__file__).resolve().parents[3];r=w/'work/nss158';p=w/'work/nss157';repo=w/'athena-nss-mainline'
base='b49135086dd54d0ef68e452850acb7fed6d0c1ae'
read=lambda f:json.loads(f.read_text(encoding='utf-8-sig'))
sha=lambda b:hashlib.sha256(b).hexdigest()
dump=lambda x:json.dumps(x,ensure_ascii=False,indent=2)+'\n'
q157=[read(p/('entry-qualified'+s+'.json')) for s in ['', '-v2','-v3','-v4','-v5','-v6','-v7','-v8','-live']]
q158=read(r/'entry-qualified.json');assert all(x['passed'] for x in q157+[q158])
qs={f:d for x in q157+[q158] for f,d in x['sourceManifest'].items()}
assert len({f for f in qs if f.startswith('work/nss157/')})==111
for f,d in qs.items():assert sha((w/f).read_bytes())==d
sources={}
for root in [p,r]:
    for f in root.iterdir():
        if f.suffix not in ['.mjs','.py','.lua','.ps1'] or any(x in f.name.lower() for x in ['private','credential','connect-router']):continue
        sources[f.relative_to(w).as_posix()]=sha(f.read_bytes())
for f in (r/'reporting').iterdir():
    if f.suffix in ['.py','.mjs','.ps1']:sources[f.relative_to(w).as_posix()]=sha(f.read_bytes())
assert all(f in sources and sources[f]==d for f,d in qs.items())
audited=[]
for root in [p,r]:
    for d in sorted(root.glob('automatic-epoch-*')):
        if not d.is_dir() or not (d/'stage-receipt-private.json').exists():continue
        inp=read(d/'source-manifest-preaudit.json');cp=read(d/'stage-checkpoint-verified.json');undo=read(d/'stage-undo-verified.json')
        receipt=read(d/'stage-receipt-private.json');detached=read(d/'stage-detached-private.json');plan=read(d/'stage-plan-private.json');rec=read(d/'last-record-private.json')
        assert cp['gzipVerified'] and all(undo.values()) and receipt['rollbackBeforeFirstWrite'] and receipt['pipeInodesVerified'] and receipt['parentIdentityVerified']
        assert detached['identity']['ppid']==1 and plan['qosCodeBytes']<=73728 and plan['execBytes']<=9000
        assert rec['firmwareZeroAfterRetirement'] and rec['dualPhysicalQueuesRestored']
        for f,h in inp.items():assert sha((w/f).read_bytes())==sha((d/'frozen'/f).read_bytes())==h
        result=read(d/'result.json')
        audited.append({'epoch':d.name,'round':root.name,'boundInputs':len(inp),'nativeResultPassed':result['passed'],
            'checkpointDownloadedShaGzipVerified':True,'independentPpidOneRollbackVerifiedBeforeWrite':True,
            'payloadBytes':plan['qosCodeBytes'],'guardianExecBytes':plan['execBytes'],
            'allOriginalRestoreChecks':undo,'firmwareZeroAndPhysicalQueuesRestored':True,
            'fullPrivateInputsAndFrozenCopiesHashChecked':True,'rawRecordSha256':sha((d/'last-record-private.json').read_bytes())})
assert len(audited)==8
change=p/'pilot-change-20261006095750-870d9521f64bee9a';a=read(change/'automatic-result.json')
for k in ['passed','exactSingleTcpCiRetirement','oldEpochRestoredBeforeNewOwner','sameOriginalUdp','newQueryCheckpointOwnerPinsCis']:assert a[k]
first=w/read(change/'first-case-private.json')['dir'];second=w/read(change/'second-case-private.json')['dir']
rec=read(first/'last-record-private.json');c=rec['actualReclassification'];facts=c['evidence']['completeSelected']
assert c['action']=='RETIRE_EXACT_SELECTED_SLOTS' and c['affected']==['tcp'] and not c['clearConntrack'] and not c['changeQoSBeforeRetirement']
assert rec['noRetagBeforeSingleCiAbsence'] and rec['terminalPairFirmwareZero'] and rec['classChangeTestCompleted']
assert facts['comparisonMadeFromThisCompleteQuery'] and facts['completeReadCount']==2 and facts['completeWaitSeconds']<.65
actualClasses={f['identity']['protocol']:f['decision']['class'] for f in facts['authenticatedSelectedFlows']}
assert actualClasses=={'tcp':'BE','udp':'RT'}
old=read(change/'event-history-private.json');new=read(change/'successor-history-private.json')
assert old['closedAndRestored'] and new['closedAndRestored'] and old['selected']==new['selected']
assert all(old[k]!=new[k] for k in ['owner','tagOwner','frozenHash','checkpointName']) and old['firstSequence']<new['firstSequence']
assert len(old['nativeCis'])==len(new['nativeCis'])==2 and all(x!=y for x,y in zip(old['nativeCis'],new['nativeCis']))
metrics157=read(second/'lifecycle-metrics.json');assert 20<=metrics157['seconds']<=21.5 and metrics157['causalCpuReductionPercent'] is None
classTrial={'passed':True,'wan':metrics157['selectedWan'],'ecmSequence':[0,2,1,0,2,0],
    'actualClassesAfterPause':actualClasses,'affectedSlots':['tcp'],'sameSingleCompleteQueryEvidence':True,
    'completeReadCount':facts['completeReadCount'],'completeWaitSeconds':facts['completeWaitSeconds'],
    'targetTcpCiAbsentAndOriginalUdpCiTagsRetained':True,'oldPairRestoredBeforeNewEpoch':True,
    'sameTcpSocketCtAndOriginalUdp':True,'freshQueryCheckpointOwnerPinsBothCis':True,'oldGateNotReopened':True,
    'exactRetirementAndNewEpochBothPassed':True,'metrics':metrics157,'matchedCpuComparison':False,'cs2Acceptance':False}
aba=r/'pilot-aba-20261006101739-594f251aa928f1c3';a=read(aba/'automatic-result.json');d=w/read(aba/'case-reference-private.json')['dir']
assert a['passed'] and a['allThreeTwentySecondPhases'] and a['matchedForwardingABACompleted']
assert read(d/'result.json')['matchedForwardingABACompleted'] and read(d/'last-record-private.json')['abaCompleted']
metrics=read(d/'actual-long-metrics.json');comparison=read(d/'same-load-comparison.json')
assert metrics['passed'] and [x['acceleratedCounts'] for x in metrics['phases']]==[[0],[2],[0]]
assert all(20<=x['whole']['seconds']<=21.5 and x['sampleCount']==41 for x in metrics['phases'])
assert comparison['passed'] and not comparison['comparabilityAccepted'] and sum(comparison['checks'].values())==5
assert comparison['softirqRelativeReductionPercent'] is None
assert all(x['whole']['udp']['sent']==x['whole']['udp']['received'] for x in metrics['phases'])
for case in [first,second,d]:
    em=read(case/'actual-accelerated-state-proof.json');mapping=read(case/'post-checkpoint-class-leaf-map-proof.json')
    assert em['passed'] and em['connectionCount']==2 and mapping['mappingByActualClass']
    for slot,v in em['proof'].items():assert v['accelerated'] and v['natCorrect'] and v['fromLan4'] and v['fromBridgeLan']
    assert em['proof']['tcp']['wanAffinity']==em['proof']['udp']['wanAffinity']
    assert em['proof']['tcp']['ctMark']==em['proof']['udp']['ctMark']
native157=read(p/'native-qualified-v2.json');wait=read(p/'complete-wait-qualified.json');native158=read(r/'native-qualified.json')
assert native157['passed'] and native158['passed'] and wait['passed']
assert not native157['fullFactoryModeled'] and not native158['fullFactoryModeled']
assert wait['models']['checks']==14 and native157['model']['checks']==native158['model']['checks']==9
pub=read(p/'publication-order-v2.json');rows=pub['rows'];assert len(rows)==24 and pub['readonly'] and pub['flowsExcluded']
ahead=sum(x['projectionQuery']>x['completeQuery'] for x in rows);assert ahead==6
delays=[x['completePublished']-x['projectionPublished'] for x in rows if x['projectionQuery']==x['completeQuery']]
publication={'readonly':True,'observations':24,'projectionAheadOneQueryObservations':ahead,
    'sameQueryFullPublishAfterProjectionSecondsRange':[min(delays),max(delays)],
    'permanentClassifierChanged':False,'maximumCompleteWaitSeconds':.65,'maximumCompleteReads':15,
    'oldEpochLeaseReserveSeconds':.5,'querySourceSecondsNotExtended':True,'factsTakenFromSingleFinalFullQuery':True}
matching=read(p/'finite-matching-diagnosis.json');assert matching['lastTcpWans']==[2,2,5,5] and matching['lastUdpWans']==[1] and matching['lastSameWanPairs']==0
assert len(matching['closePilots'])==4 and not any(x['wholePilotPassed'] for x in matching['closePilots'])
assert sum(x['initialEpochStarted'] for x in matching['closePilots'])==2 and not any(x['newSuccessorEpochStarted'] for x in matching['closePilots'])
failureCauses={1:'Declared audit helper missing before fixture/checkpoint/stage',3:'First partial endpoint marker retained old namespace; refused before firewall/client/checkpoint',5:'Projection and full diagnostic query differ; old pair restored; first post-audit also refused transient WAN4 state',7:'Four software TCP candidates had no same-WAN pair; no stage',9:'Full read lagged projection; exact-class evidence unavailable; old pair restored',11:'Actual target jsonc alias made class record null; native exact CI retirement passed but host pipeline failed',13:'Four software candidates did not match fixed UDP WAN; no stage',15:'Both finite software cohorts did not match fixed UDP WAN; no stage'}
failures=[]
for i,cause in failureCauses.items():
    f=p/f'run{i}/automatic-result.json';assert not read(f)['passed']
    failures.append({'case':f'NSS157-run{i}','wholePilotPassed':False,'cause':cause,
        'firstEpochStarted':(f.parent/'first-case-private.json').exists(),'originalFailureRecordSha256':sha(f.read_bytes()),'originalSourceAndPrivateEvidencePreserved':True})
for x in matching['closePilots']:
    failures.append({'case':'NSS157-'+x['trial'],'wholePilotPassed':False,
        'cause':'Finite original or successor software TCP cohort does not match the fixed UDP WAN',
        'oldPairExitAndRestorePassed':x.get('oldPairExitPassed',False),'newSuccessorEpochStarted':False,
        'originalSourceAndPrivateEvidencePreserved':True})
failures += [
 {'case':'publication-order-v1','cause':'Atomic publication inode changed during first read; original read refused; v2 records without mixing frames','productionWrite':False},
 {'case':'qualification-current-full-v1/v2/v5','cause':'Three offline input/dependency assertions refused before production; original sources and errors retained','productionWrite':False},
 {'case':'endpoint-audit-v2','cause':'Startup summary has no unit; refused before remote connect; v3 resolves same owned runtime-250 receipt','productionWrite':False},
 {'case':'NSS158-size-model-v1','cause':'Stored plan lacked tag packet AST; reconstructed only from actual same complete input; prior exact payload matched','productionWrite':False},
 {'case':'NSS158-qualification-v1/v2','cause':'Dependency scanner inspected Python replacement text, then a declared-baseline helper was missing; refused before connect and fixed in new sources','productionWrite':False},
 {'case':'NSS158-analysis-v1','cause':'Local pretty record exceeded 1MiB; native compact record was within original 1MiB and target reader had passed; v2 fixes local analysis accounting only','productionWrite':False}]
health=read(r/'v2-final-health.json');physical=read(r/'v2-physical-final.json');end=read(r/'endpoint-client-closure-v2.json')
recv=read(r/'v2-receiver-closure.json');down=read(r/'v2-download-receiver-closure.json')
assert all(x['passed'] for x in [health,physical,end,recv,down])
assert health['queryAge']<6 and health['ecmStoppedAndZero'] and all(health[k] for k in ['noActiveTransaction','noStaging','noExperimentState','noExperimentalModule'])
assert end['previousLoadsChecked']==end['ownedUnitsInactiveMainPidZero']==46 and end['temporaryFirewallRulesRemaining']==end['ownedClientOrGuardProcessesRemaining']==0
manifest=read(repo/'source-manifest.json');prefix=copy.deepcopy(manifest['sources']);assert len(prefix)==2521 and manifest['lastAppendExport']=='NSS156'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()==base
oldruntime=subprocess.check_output(['git','show',base+':evidence/current-runtime.json'],cwd=repo)
assert read(repo/'evidence/current-runtime.json')['round']=='NSS156'
proof={'passed':True,'historicPrefixSources':2521,'historicPrefixCanonicalSha256':sha(json.dumps(prefix,sort_keys=True,separators=(',',':')).encode()),
    'historicManifestPrefixUnchanged':True,'sourceHashes':sources,'sources':len(sources),
    'allEightActualEpochFullInputsFrozenCopiesVerified':True,'actualStagedEpochs':len(audited),
    'classPilotActualBindings':2020,'abaActualBindings':2042,'privateInputContentsExcluded':True,
    'fullFactoryModelExecuted':False,'old156RuntimeExactGitBytes':True}
main={'round':'NSS158','passed':True,'status':'INTEGRATED_CLASS_RETIRE_RELEARN_AND_FUNCTIONAL_ABA_PASSED_CPU_COMPARABILITY_FAILED',
    'observedAt':health['observedAt'],'classPilot157':classTrial,'functionalTwentySecondABA':True,
    'abaSelectedWan':metrics['oneWan'],'abaMetrics':metrics,'abaComparison':comparison,'cpuReductionConclusion':None,
    'exactClassLifecycleIntegratedIntoNormalABA':True,'classSpecificChangeEndsOldPairBeforeFreshEpoch':True,
    'newTcpSuccessorInLatestCombinedClosePilotsPassed':False,'old156NewTcpSuccessorHistoricalPassed':True,
    'latestClosePilots':matching,'publicationDiagnosis':publication,'actualStagedEpochs':audited,
    'qualifiedExperimentalController':'work/nss158/pilot-supervisor.mjs','classController':'work/nss157/pilot-supervisor-live.mjs',
    'boundInputs':2042,'classPilotBoundInputs':2020,'nssScopeOneTcpBulkOneUdpRt':True,
    'softwareMaximumTcpPorts':8,'softwareTotalOfferedMbps':32,'globalPacerCreditBytes':65536,
    'sourceNativeOwnerClientSeconds':[6,27,100,180],'execRawBundleRecordBytes':[9000,65536,73728,1048576],
    'permanentClassifierKernelGateAndQoSUnchanged':True,'fullFactoryModelExecuted':False,
    'pbrCtMarkNatWanAffinityUnchanged':True,'realHumanGameAcceptance':False,'highLoad300MbpsAcceptance':False,
    'permanentNssControllerInstalled':False,'nssPermanentlyEnabled':False,'desktopOperated':False,
    'steamOrCs2Started':False,'ctExitInferredFromProjection':False,'cpuBarrierIsFirmwareAck':False,
    'repositoryVisibility':'public','autonomyDeadlineBeijing':'2026-10-06T20:00:00+08:00',
    'failuresPreserved':len(failures),'exportedSources':len(sources),'old156RuntimeRetainedSha256':sha(oldruntime),
    'finalAudit':health,'physicalRestore':physical,'endpointClosure':end}
runtime={'round':'NSS158','observedAt':health['observedAt'],'classifierDeployment':'NSS68',
    'workerPid':health['workerPid'],'guardianPid':health['guardianPid'],'classifierConfigSha256':health['configSha256'],
    'qualifiedExperimentalController':main['qualifiedExperimentalController'],'boundInputs':2042,
    'integratedClassRetireRelearnPassed':True,'functionalTwentySecondABA':True,'cpuComparabilityAccepted':False,
    'cpuConclusion':None,'realHumanGameAcceptance':False,'nssPermanentlyEnabled':False,'permanentNssControllerInstalled':False,
    'historical156RuntimePreservedSha256':sha(oldruntime),'repositoryVisibility':'public',
    'autonomyDeadlineBeijing':main['autonomyDeadlineBeijing'],'audit':health,'physicalRootRestoreAudit':physical,
    'endpointClientClosureAudit':end,'ownedReceiverClosureAudit':recv,'ownedDownloadReceiverClosureAudit':down}
when=datetime.fromisoformat(health['observedAt'].replace('Z','+00:00')).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
body=f'''# 改类撤销与重学整合通过，完整三段对照已完成

更新：{when}，北京时间。最新NSS158，合并封存NSS157真实生命周期。未操作桌面、Steam或CS2。

**自动分类→双向NSS bulk/RT leaf已在新整合版本完成真实20秒software→NSS→software。另一次实际暂停自有TCP发送造成BULK→BE/cooldown，完整同query仅TCP受影响；精确撤销TCP CI，ECM2→1且原UDP CI/tag保持，再结束旧代0。原TCP socket/CT与UDP继续，新query/checkpoint/owner/kernel pin和不同两个CI重学20.01秒2→0。**

改类后WAN3上传30.384Mbps，softirq5.396%、UDP771/771、四leaf drop0与squeeze/drop0；没有软件对照，不宣称CPU收益。NSS158同WAN5三段各20.00/20.01/20.01秒：

| 指标 | software A | NSS B | software A2 |
|---|---:|---:|---:|
| 服务器确认上传 Mbps | 30.767 | 30.101 | 30.426 |
| softirq % | 10.242 | 1.283 | 7.122 |
| CPU busy % | 26.422 | 17.053 | 23.548 |
| UDP收/发 | 855/855 | 861/861 | 824/824 |
| UDP echo RTT p95 ms | 181.700 | 181.718 | 181.736 |
| time_squeeze / softnet drop | 0/0 | 0/0 | 0/0 |

**功能闭环通过，CPU可比性未通过。** 原七项条件保留，仅五项通过：其它WAN背景1.956/1.648/1.981Mbps超原0.5Mbps上限且波动0.333Mbps超0.25Mbps。相对CPU收益null，不放宽条件或重试追门槛。物理WAN RX drop A/A2各1、B0也保留；UDP echo不是CS2 jitter/loss/Miss。本轮约30Mbps受控上传，下行主要ACK和小UDP，没有300Mbps下载、真人、长期稳定或拥塞AQM验收。

定位两项兼容问题后只改实验入口：常驻classification投影比完整snapshot同query先400–550ms；完整证据最多等.65秒/15次且保留旧lease .5秒余量，最后一份完整query独立比较，不混旧事实、不延长source6秒。实际jsonc重复引用同对象导致class记录null，原run11精确native撤销通过但host整体失败保留；新版本只存一次完整对象并用字段名引用，9项实际改动函数RAM模型及随后真实完整pilot通过。14项完整读取RAM检查属于局部模型，整套factory模型未运行。

新整合close四次整体失败：两次在真实ECM2关闭TCP并恢复旧pair成功，后继四软件TCP未匹配固定UDP WAN，没有新stage；另外两次初始不匹配、没有stage。最后TCP走WAN2/2/5/5、UDP留WAN1；只证明准入不匹配，未证明PBR故障，不盲重试、强制换WAN或扩大端口。NSS156旧版本新TCP重学成功仍保留，不能代替新整合版本后继通过。

所有八个实际stage的完整绑定/冻结输入核验、checkpoint下载SHA/gzip、写前PPID1独立超时恢复与精确恢复通过。分类pilot2020、ABA2042绑定；source6/native27/owner100/client180、9000/65536/73728/1MiB不变；一健康WAN仅一TCP BULK＋一UDP RT，软件准备共享32Mbps/64KiB、最多8端口。PBR/完整ct mark/NAT/affinity和NSS68常驻配置未改。

终态source{health['queryAge']:.2f}秒，NSS68/{health['workerPid']}/{health['guardianPid']}健康，ECM关闭全零，无事务/stage/state/模块；两物理原mq+四fq_codel恢复，46历史端点/客户端/自有接收器全关闭。WAN4自然exec-minieap仍down、四路failover保持，未主动认证。

下一步只完善新整合控制器的可部署生命周期和最后集中真人验证；不把有限pilot称为永久NSS部署，不扩第二WAN/共享预算/WiFi/autorate。继续本日授权到20:00；19:40最终只读收尾，19:50不新开生产实验，完成推送/archive后暂停heartbeat。凭据/完整CT/nonce/配置/checkpoint/二进制仅本地，仓库按用户新偏好保持public。

证据：LINKS
'''
evidence={'mainline':main,'source-proof':proof,'qualification':{'passed':True,'classVersions':q157,'aba':q158,'native157':native157,'native158':native158,'completeWait':wait,'fullFactoryModelExecuted':False},
    'class-lifecycle':classTrial,'actual-stages':audited,'aba-metrics':metrics,'aba-comparison':comparison,
    'finite-matching':matching,'publication-order':publication,'failures':failures,'final-audit':health,
    'physical-final':physical,'endpoint-client-closure':end,'receiver-closure':recv,'download-receiver-closure':down}
# All assertions and all destination checks precede any Git workspace mutation.
planned={repo/f'evidence/nss158-{n}.json':dump(v).encode('utf-8') for n,v in evidence.items()}
planned[repo/'evidence/nss156-runtime.json']=oldruntime
for f,h in sorted(sources.items()):
    b=(w/f).read_bytes();assert sha(b)==h;planned[repo/'code'/f]=b
    manifest['sources'].append({'path':'code/'+f,'workspaceSource':f,'sha256':h,'bytes':len(b),'role':'integrated-single-wan-exact-class-retirement-aba-and-explicit-reporting'})
for dest in planned:assert not dest.exists(),str(dest)
for dest,b in planned.items():dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b)
manifest.update(lastAppendExport='NSS158',generatedAt=datetime.now(timezone.utc).isoformat(),privateDataExcluded=True,preservesOriginalSourceBytes=True)
assert manifest['sources'][:2521]==prefix
(repo/'source-manifest.json').write_text(dump(manifest),encoding='utf-8')
(repo/'evidence/current-runtime.json').write_text(dump(runtime),encoding='utf-8')
labels=[('主线','mainline'),('改类实测','class-lifecycle'),('三段数据','aba-metrics'),('可比性','aba-comparison'),('失败','failures'),('入口','qualification'),('完整恢复','final-audit'),('端点','endpoint-client-closure')]
for file in ['AGENTS.md','docs/STATE.md','docs/PLAN.md','docs/EXPERIMENT_LOG.md']:
    dest=repo/file;prefixlink='../' if file.startswith('docs/') else ''
    links='、'.join(f'[{label}]({prefixlink}evidence/nss158-{n}.json)' for label,n in labels)
    dest.write_text(body.replace('LINKS',links)+'\n## NSS156及更早历史\n\n'+dest.read_text(encoding='utf-8'),encoding='utf-8')
dest=repo/'README.md';dest.write_text('# Athena NSS mainline\n\n最新[NSS158](evidence/nss158-mainline.json)：真实改类精确撤销、新代重学与20秒三段功能闭环通过；本轮CPU可比性未通过。先读[STATE](docs/STATE.md)。\n\n## NSS156及更早历史\n\n'+dest.read_text(encoding='utf-8'),encoding='utf-8')
page='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>NSS158 主线</title><style>body{font:16px/1.8 system-ui;max-width:980px;margin:40px auto;padding:24px;color:#182638;background:#f3f5f7}pre{white-space:pre-wrap;background:white;padding:25px}a{color:#1761a2}</style><body><h1>NSS158 · 改类重学与完整ABA</h1><pre>'+html.escape(body.replace('LINKS','源码与脱敏证据见GitHub STATE'))+'</pre><a href="https://github.com/ZyPulse-zy/athena-nss-mainline/blob/main/docs/STATE.md">GitHub STATE</a></body></html>'
for dest in [w/'outputs/nss158-mainline-report.html',repo/'reports/nss158-mainline-report.html']:
    assert not dest.exists();dest.write_text(page,encoding='utf-8')
receipt={'passed':True,'sourcesAdded':len(sources),'sourcesTotal':len(manifest['sources']),'actualEpochsVerified':len(audited),'classAndFunctionalABAPassed':True,'cpuComparabilityAccepted':False,'old156RuntimeExactGitBytes':True}
with (r/'reporting/export-receipt.json').open('x',encoding='utf-8') as f:f.write(dump(receipt))
print(json.dumps(receipt))
