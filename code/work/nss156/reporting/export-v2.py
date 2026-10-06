"""Export the actual single-WAN flow-exit/new-connection lifecycle, with failures."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib,subprocess,copy,html
w=Path(__file__).resolve().parents[3];r=w/'work/nss156';repo=w/'athena-nss-mainline';base='ae6fc3ab037fa73b3d1a6cb0705d54938bccde5a'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda b:hashlib.sha256(b).hexdigest()
def put(p,v):
    assert not p.exists(),str(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def ev(n,v):put(repo/f'evidence/nss156-{n}.json',v)
qualified=[read(r/f'entry-qualified{s}.json') for s in ['', '-v2','-v3','-v4','-v5','-v6','-v7']];assert all(q['passed'] for q in qualified)
sources={f:d for q in qualified for f,d in q['sourceManifest'].items()};assert len(sources)==73
actual=read(r/'entry-source-manifest-v7.json');assert len(actual)==1909
for f,d in actual.items():assert sha((w/f).read_bytes())==sha((r/'frozen-qualified-inputs-v7'/f).read_bytes())==d
auto=read(r/'run7/automatic-result.json');assert auto['passed'] and auto['newTcpSocketAndCt'] and auto['sameUdpSocketCtMarkNatWan'] and auto['newQueryCheckpointOwnerPinsBothCis']
for k in ['ctExitInferred','matchedCpuComparison','cs2Acceptance','permanentNssDeployment']:assert not auto[k]
trials=[]
for label,file,kind in [('old-pair-exit','first-case-private.json','exit'),('new-tcp-original-udp','second-case-private.json','stable')]:
    d=w/read(r/'run7'/file)['dir'];rec=read(d/'last-record-private.json');result=read(d/'result.json');plan=read(d/'stage-plan-private.json');cp=read(d/'stage-checkpoint-verified.json');undo=read(d/'stage-undo-verified.json');detached=read(d/'stage-detached-private.json');receipt=read(d/'stage-receipt-private.json');mapping=read(d/'post-checkpoint-class-leaf-map-proof.json');ecm=read(d/'actual-accelerated-state-proof.json');inputs=read(d/'source-manifest-preaudit.json')
    assert result['passed'] and not result['errors'] and not rec.get('error') and len(inputs)==1909 and all(undo.values())
    assert cp['gzipVerified'] and receipt['rollbackBeforeFirstWrite'] and receipt['pipeInodesVerified'] and receipt['parentIdentityVerified'] and detached['identity']['ppid']==1
    assert plan['qosCodeBytes']<=73728 and plan['execBytes']<=9000 and mapping['mappingByActualClass'] and ecm['passed'] and ecm['connectionCount']==2
    assert rec['firmwareZeroAfterRetirement'] and rec['dualPhysicalQueuesRestored'] and rec['successEarlyCompletion']
    for f,digest in inputs.items():assert sha((w/f).read_bytes())==sha((d/'frozen'/f).read_bytes())==digest
    metrics=read(d/'lifecycle-metrics.json') if kind=='stable' else None
    if kind=='stable':assert result['automaticLifecycleEpochCompleted'] and 20<=metrics['seconds']<=21.5 and not metrics['sameLoadSoftwareNssSoftwareComparison'] and metrics['causalCpuReductionPercent'] is None
    else:assert result['flowEligibilityExitCompleted'] and rec['terminalPairFirmwareZero'] and not rec['fastPathMeasurement']['performanceComparison'] and not rec['terminalInvalidation']['ctExitInferredFromProjection']
    trials.append({'case':label,'passed':True,'wan':plan['selected']['tcp']['wan'],'ecmSequence':[0,2,0],'boundInputs':1909,'payloadBytes':plan['qosCodeBytes'],'guardianExecBytes':plan['execBytes'],'checkpointDownloadedShaGzipVerified':True,'independentPpidOneRollbackVerifiedBeforeWrite':True,'ctMarkNatWanFourTagsCorrect':True,'nativeHardSeconds':27,'ownerMaxSeconds':100,'allOriginalRestoreChecks':undo,'completeSameSourceClassMapping':True,'metrics':metrics,'matchedCpuComparison':False,'realCs2Acceptance':False})
assert trials[0]['wan']==trials[1]['wan']==3
hist=read(r/'run7/successor-history-private.json');previous=read(r/'run7/exit-history-private.json');assert hist['closedAndRestored'] and previous['closedAndRestored'] and hist['selected']['udp']==previous['selected']['udp']
assert hist['selected']['tcp']['id']!=previous['selected']['tcp']['id'];assert all(hist[k]!=previous[k] for k in ['owner','tagOwner','frozenHash','checkpointName'])
assert all(a!=b for a,b in zip(hist['nativeCis'],previous['nativeCis']))
failures=[]
causes=['Raw TCP initial connect timed out before any checkpoint or stage','Raw nonce TCP candidates exhausted without same-WAN pair','Same-WAN pair found only at last candidate; successor reservation refused before stage','Generated driver kept old exact directory allowlist; detected and owned load stopped; actual input refused before stage','Raw initial nonce TCP candidates exhausted; no NSS stage','SSH uploaded successfully without Keepalive error, but finite matching window found no same-WAN pair']
for i,cause in enumerate(causes,1):
    out=read(r/f'run{i}/automatic-result.json');assert not out['passed'] and not (r/f'run{i}/first-case-private.json').exists()
    failures.append({'case':f'run{i}','passed':False,'cause':cause,'routerCheckpointOrNssStageStarted':False,'originalErrorAndSourcesPreserved':True,'rootCauseOfNetworkTimeoutProven':False})
cal=read(r/'calibration-namespace-failure.json');assert cal['refusedBeforeRouterConnect'] and cal['onlyExactNamespaceChanged'];failures.append({'case':'post-calibration-namespace','cause':cal['failure'],'refusedBeforeRouterConnect':True,'oldSourceRetained':True,'correctedOnlyNamespace':True,'analysisRanOnlyAfterRepair':True})
failures.append({'case':'publication-proof-path','cause':'First export referenced two JSON proofs without file extensions; repair generator default GBK decode also refused before edits','failedBeforeGitWorkspaceMutation':True,'submissionChainStoppedBeforeCommit':True,'originalSourcePreserved':True,'onlyProofFileExtensionsCorrected':True})
software=[]
for n in range(1,7):
    ref=read(r/f'load-run{n}-reference-private.json');p=w/ref['dir'];end=read(p/'result-private.json');software.append({'case':f'run{n}','seconds':end['seconds'],'serverConfirmedBytes':end['tcpBytes'],'clientErrors':end['errors'],'noNssStage':True,'transport':'raw nonce TCP' if n<=5 else 'existing SSH with owned-client Keepalive disabled','causeNotProven':True})
health=read(r/'v1-final-health.json');physical=read(r/'physical-final.json');endpoints=read(r/'endpoint-client-closure.json');recv=read(r/'receiver-closure.json');down=read(r/'download-receiver-closure.json')
assert all(x['passed'] for x in [health,physical,endpoints,recv,down]);assert health['queryAge']<6 and health['ecmStoppedAndZero'] and health['noStaging'] and health['noExperimentState'] and health['noExperimentalModule']
assert endpoints['previousLoadsChecked']==endpoints['ownedUnitsInactiveMainPidZero']==34 and endpoints['ownedClientOrGuardProcessesRemaining']==0
extras=['diagnose-routing.mjs','read-pbr-source.mjs','stop-namespace-invalid.mjs','prepare-postchecks.py','health.mjs','read-final-physical.mjs','verify-all-endpoints.mjs','verify-receivers.mjs','verify-downloaders.mjs','calibrate-clock.mjs','calibrate-clock-v2.mjs','fix-calibration-namespace.py','analyze.py','reporting/export.py','reporting/export-v2.py','reporting/update-checker.py','reporting/verify-published.py']
for n in extras:sources['work/nss156/'+n]=sha((r/n).read_bytes())
for f,d in sources.items():assert f.startswith('work/nss156/') and f.endswith(('.mjs','.py','.ps1','.lua')) and all(x not in f.lower() for x in ['private','credential','connect-router']) and sha((w/f).read_bytes())==d
manifest=read(repo/'source-manifest.json');prefix=copy.deepcopy(manifest['sources']);assert len(prefix)==2430 and manifest['lastAppendExport']=='NSS155'
oldruntime=subprocess.check_output(['git','show',base+':evidence/current-runtime.json'],cwd=repo);assert read(repo/'evidence/current-runtime.json')['round']=='NSS155';assert not (repo/'evidence/nss155-runtime.json').exists()
proof={'passed':True,'historicPrefixSources':2430,'historicPrefixCanonicalSha256':sha(json.dumps(prefix,sort_keys=True,separators=(',',':')).encode()),'historicManifestPrefixUnchanged':True,'sources':len(sources),'sourceHashes':sources,'actualBindings':1909,'actualProductionEpochCount':2,'allActualFullInputsAndFrozenCopiesVerified':True,'privateInputContentsExcluded':True,'fullNewFactoryModelExecuted':False,'nativeWholePairFactoryBytesSameAs155':True,'classifierKernelGateAndQoSUnchanged':True}
# Verify evidence/failures before changing Git workspace contents.
(repo/'evidence/nss155-runtime.json').write_bytes(oldruntime)
for f,d in sorted(sources.items()):
    p=repo/'code'/f;assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True);b=(w/f).read_bytes();p.write_bytes(b);manifest['sources'].append({'path':'code/'+f,'workspaceSource':f,'sha256':d,'bytes':len(b),'role':'bounded-owned-flow-lifecycle-fixture-and-explicit-reporting'})
manifest.update(lastAppendExport='NSS156',generatedAt=datetime.now(timezone.utc).isoformat(),privateDataExcluded=True,preservesOriginalSourceBytes=True);assert manifest['sources'][:2430]==prefix;(repo/'source-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
main={'round':'NSS156','passed':True,'status':'OWNED_FLOW_EXIT_NEW_TCP_ORIGINAL_UDP_LIFECYCLE_PASSED','scope':'One healthy WAN3: owned TCP close, whole old epoch restored, new TCP and original UDP relearnt and stable for 20 seconds','observedAt':health['observedAt'],'ecmSequence':[0,2,0,2,0],'actualOldPairExitAndRestoration':True,'newTcpSuccessorPassed':True,'completed20SecondSuccessorEpochs':1,'sameUdpSocketCtMarkNatWan':True,'newQueryCheckpointOwnerPinsBothCis':True,'oldGateNeverReopened':True,'nssScopeOneTcpBulkOneUdpRt':True,'softwarePreparationProbeCount':4,'maximumTotalOwnedTcpPorts':8,'softwarePreparationTotalOfferedMbps':32,'globalMaximumPacerCreditBytes':65536,'otherOwnTcpSocketsClosedBeforeStage':True,'qualifiedController':'work/nss156/pilot-supervisor-v7.mjs','boundInputs':1909,'nativeWholePairFactoryVersion':155,'nativeFullFactoryUnchangedFrom155':True,'classSpecific151RetirementMustBeMergedBeforeDeployablePilot':True,'classifierKernelGateAndQoSUnchanged':True,'sourceNativeOwnerSeconds':[6,27,100],'clientHardSeconds':180,'execRawBundleRecordBytes':[9000,65536,73728,1048576],'matchedCpuComparison':False,'cpuReductionConclusion':None,'realHumanGameAcceptance':False,'highLoad300MbpsAcceptance':False,'permanentNssControllerInstalled':False,'nssPermanentlyEnabled':False,'desktopOperated':False,'steamOrCs2Started':False,'ctExitInferredFromProjection':False,'keepaliveTimeoutRootCauseProven':False,'ownedSshKeepaliveOnlyChanged':True,'systemSshConfigurationChanged':False,'dayHeartbeatActiveUntilBeijing':'2026-10-06T20:00:00+08:00','repositoryVisibility':'public','failuresPreserved':len(failures),'exportedSources':len(sources),'old155RuntimeRetainedSha256':sha(oldruntime),'trials':trials,'finalAudit':health,'physicalRestore':physical,'endpointClosure':endpoints}
for n,v in [('source-proof',proof),('qualification',{'passed':True,'versions':qualified,'actualBindings':1909,'fullFactoryModelExecuted':False}),('trials',trials),('failures',failures),('software-preparation',software),('final-audit',health),('physical-final',physical),('endpoint-client-closure',endpoints),('receiver-closure',recv),('download-receiver-closure',down),('mainline',main)]:ev(n,v)
runtime={'round':'NSS156','observedAt':health['observedAt'],'workerPid':health['workerPid'],'guardianPid':health['guardianPid'],'classifierConfigSha256':health['configSha256'],'classifierDeployment':'NSS68','qualifiedExperimentalController':main['qualifiedController'],'boundInputs':1909,'newTcpSuccessorPassed':True,'completed20SecondSuccessorEpochs':1,'nssPermanentlyEnabled':False,'permanentNssControllerInstalled':False,'cpuConclusion':None,'realHumanGameAcceptance':False,'dayHeartbeatActiveUntilBeijing':main['dayHeartbeatActiveUntilBeijing'],'historical155RuntimePreservedSha256':sha(oldruntime),'audit':health,'physicalRootRestoreAudit':physical,'endpointClientClosureAudit':endpoints,'ownedReceiverClosureAudit':recv,'ownedDownloadReceiverClosureAudit':down,'repositoryVisibility':'public'}
(repo/'evidence/current-runtime.json').write_text(json.dumps(runtime,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
metric=trials[1]['metrics'];when=datetime.fromisoformat(health['observedAt'].replace('Z','+00:00')).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
body=f'''# 真实TCP退出、新TCP与原UDP重学通过

更新：{when}，北京时间。最新NSS156。后台自有流量，未操作桌面/Steam/CS2。

**WAN3真实ECM0→2→0→2→0。ECM2时关闭自有TCP；旧双流代停止新学习、撤销并完整恢复，原UDP应用继续。旧固件/标签/队列恢复后才创建新TCP；新分类query、checkpoint、owner、kernel pin及两个新CI完成第二代20.01秒并恢复。UDP的socket/CT/完整mark/NAT/WAN保持，TCP为新socket/CT，旧gate未重开。**

后继服务器确认上传{metric['serverConfirmedTcpUploadMbps']:.3f}Mbps，busy{metric['busyPercent']:.3f}%、softirq{metric['softirqPercent']:.3f}%，time_squeeze/drop均0；UDP {metric['udp']['received']}/{metric['udp']['sent']}，四个NSS bulk/RT双向FQ-CoDel leaf均有包、drop0。UDP echo RTT中位{metric['udp']['rttP50Ms']:.2f}ms、p95 {metric['udp']['rttP95Ms']:.2f}ms。没有同负载软件对照，CPU降幅null；echo不是CS2 jitter/loss/Miss，当前下行主要ACK与小UDP，不是300Mbps、真人或长期验收。

匹配准备改为四条自有软件TCP共享同一个32Mbps/64KiB credit pacer；按真实分类/mark/NAT选择后关闭其它socket，只一TCP BULK＋一UDP RT进入NSS。四个额外端口留给旧代恢复后的新TCP，共8个候选，不改PBR/mark/NAT/affinity或扩大NSS允许范围。每代1909实际绑定和冻结输入核验、新checkpoint下载SHA/gzip、写前PPID1独立恢复；source6/native27/owner100/client180及9000/65536/73728/1MiB保持。

最初raw TCP连接超时或用尽候选；第三轮仅最后候选匹配而拒绝；旧目录白名单生成错误在写前拒绝并修正。SSH仅此测试进程取消2秒保活，硬截止不变；一次80秒软件上传无该错误但未找到同WAN对，未证明保活是根因。全部六次失败保留且未开启router checkpoint/NSS stage。后处理时校时工具旧目录白名单在连接前拒绝，保留原源后只修正路径再分析。首版封存程序引用两个证明文件时漏了JSON后缀，在Git内容变更与提交前拒绝；修复生成器默认GBK读取也在改动前拒绝；原源保留后使用明确UTF8修正路径。未扩大FW来源/端口，没有系统SSH配置改动。

终态原完整审核source{health['queryAge']:.2f}秒，NSS68/{health['workerPid']}/{health['guardianPid']}配置不变，ECM关闭全零、无事务/stage/state/模块；两物理原mq+四fq_codel恢复，34个历史端点/客户端及自有SSH接收器关闭。WAN4既有down/四路failover保持。

下一步把151已证明的精确BULK→BE CI撤销接回155 whole-pair终态，再做有限单WAN pilot。当前生产native仍是155 whole-pair分支；不把未整合的离线候选写成部署完成。仍按授权推进至20:00，19:40收尾、19:50不新开生产实验；凭据/CT/nonce/配置/checkpoint/二进制仅本地，仓库按用户明确偏好保持public。

证据：LINKS
'''
names=[('主线','mainline'),('两代实测','trials'),('入口','qualification'),('失败','failures'),('软件准备','software-preparation'),('终态','final-audit'),('端点','endpoint-client-closure')]
for file in ['AGENTS.md','docs/STATE.md','docs/PLAN.md','docs/EXPERIMENT_LOG.md']:
    p=repo/file;prefixlink='../' if file.startswith('docs/') else '';links='、'.join(f'[{label}]({prefixlink}evidence/nss156-{n}.json)' for label,n in names);p.write_text(body.replace('LINKS',links)+'\n## NSS155及更早历史\n\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
p=repo/'README.md';p.write_text('# Athena NSS mainline\n\n最新[NSS156](evidence/nss156-mainline.json)：真实自有TCP退出、新TCP与原UDP新代重学20秒通过。继续至20:00，先读[STATE](docs/STATE.md)。\n\n## NSS155及更早历史\n\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
page='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>NSS156 生命周期</title><style>body{font:16px/1.8 system-ui;max-width:960px;margin:40px auto;padding:24px;color:#182638;background:#f3f5f7}pre{white-space:pre-wrap;background:white;padding:25px}a{color:#1761a2}</style><body><h1>NSS156 · 新TCP与原UDP重学通过</h1><pre>'+html.escape(body.replace('LINKS','源码与脱敏证据见GitHub STATE'))+'</pre><a href="https://github.com/ZyPulse-zy/athena-nss-mainline/blob/main/docs/STATE.md">GitHub STATE</a></body></html>'
p=w/'outputs/nss156-mainline-report.html';assert not p.exists();p.write_text(page,encoding='utf-8');(repo/'reports/nss156-mainline-report.html').write_text(page,encoding='utf-8')
put(r/'reporting/export-receipt.json',{'passed':True,'sourcesAdded':len(sources),'sourcesTotal':len(manifest['sources']),'completeNewTcpLifecyclePassed':True,'old155RuntimeGitBytesPreserved':True});print(json.dumps({'passed':True,'sourcesAdded':len(sources),'sourcesTotal':len(manifest['sources']),'lifecyclePassed':True}))
