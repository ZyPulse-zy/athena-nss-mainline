"""Export narrowly proven flow-exit evidence; failed successors remain failures."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib,subprocess,copy,html
w=Path(__file__).resolve().parents[3];r=w/'work/nss155';repo=w/'athena-nss-mainline';base='8b40364eeb1693afb2bd9daf672ed7c552d5bf77'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda b:hashlib.sha256(b).hexdigest()
def put(p,v):
    assert not p.exists(),str(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def ev(n,v):put(repo/f'evidence/nss155-{n}.json',v)
qualified=[read(r/f'entry-qualified{s}.json') for s in ['', '-v2','-v3']];assert all(q['passed'] for q in qualified)
sources={f:d for q in qualified for f,d in q['sourceManifest'].items()};assert len(sources)==41
actual=read(r/'entry-source-manifest-v3.json');assert len(actual)==1836
for f,d in actual.items():assert sha((w/f).read_bytes())==sha((r/'frozen-qualified-inputs-v3'/f).read_bytes())==d
trials=[]
for run,bindings in [('run2',1831),('run3',1836)]:
    folder=read(r/run/'first-case-private.json')['dir'];p=w/folder
    record=read(p/'last-record-private.json');result=read(p/'result.json');history=read(r/run/'exit-history-private.json');plan=read(p/'stage-plan-private.json');cp=read(p/'stage-checkpoint-verified.json');undo=read(p/'stage-undo-verified.json');receipt=read(p/'stage-receipt-private.json');detached=read(p/'stage-detached-private.json');trigger=read(p/'owned-tcp-close-private.json');inputs=read(p/'source-manifest-preaudit.json')
    assert result['passed'] and result['flowEligibilityExitCompleted'] and not result['automaticLifecycleEpochCompleted']
    assert history['closedAndRestored'] and history['wholePairTerminated'] and not history['ctExitInferred']
    assert record.get('error') is None and record['flowEligibilityExitCompleted'] and record['terminalPairFirmwareZero'] and not record['fastPathMeasurement']['qualified']
    assert record['firmwareZeroAfterRetirement'] and record['dualPhysicalQueuesRestored'] and record['successEarlyCompletion']
    for k in ['ctExitInferredFromProjection','exactSingleCiRetirementClaimed','nssAdmissionAllowed']:assert not record['terminalInvalidation'][k]
    assert trigger['passed'] and trigger['ecmbeforeClose']==2 and trigger['udpContinued'] and not trigger['ctExitClaimed']
    assert len(inputs)==bindings and all(undo.values()) and cp['gzipVerified'] and receipt['rollbackBeforeFirstWrite'] and detached['identity']['ppid']==1
    for f,d in inputs.items():assert sha((w/f).read_bytes())==sha((p/'frozen'/f).read_bytes())==d
    assert plan['qosCodeBytes']<=73728 and plan['execBytes']<=9000
    trials.append({'case':run,'passed':True,'test':'owned TCP close terminates whole pair epoch','wan':plan['selected']['tcp']['wan'],'ecmSequence':[0,2,0],'controlledTcpActuallyClosed':True,'udpApplicationContinued':True,'frontendStoppedBeforeWithdrawal':True,'wholePairFirmwareZero':True,'fullOriginalRestore':True,'newConnectionLearned':False,'ctExitInferredFromProjection':False,'exactSingleCiRetirementClaimed':False,'originalPreCloseCtMarkNatWanFourTagsCorrect':True,'boundInputs':bindings,'payloadBytes':plan['qosCodeBytes'],'guardianExecBytes':plan['execBytes'],'checkpointDownloadedShaGzipVerified':True,'independentPpidOneRollbackVerifiedBeforeWrite':True,'nativeHardSeconds':27,'ownerMaxSeconds':100,'terminalReason':record['terminalInvalidation']['reason'],'observedPairCountAtInvalidation':record['terminalInvalidation']['counts']['ecm_nss_ipv4/accelerated_count'],'udpRepliesAfterClientClose':trigger['udpRepliesAfterClose'],'performanceComparison':False,'cpuReductionConclusion':None,'cs2Acceptance':False,'undo':undo})
failures=[]
for run,cause,stage in [('run1','Owned SSH upload Keepalive timeout before router checkpoint/staging; cause remains unproved',False),('run2','Old pair restored successfully, but original eight-port candidate range exhausted before new TCP creation',True),('run3','Old pair restored successfully; new SSH upload transport Keepalive timeout prevented successor qualification',True)]:
    f=read(r/run/'automatic-result.json');assert not f['passed'];assert not (r/run/'second-case-private.json').exists()
    failures.append({'case':run,'overallSuccessorPassed':False,'cause':cause,'routerNssStageOccurred':stage,'oldFlowExitPassed':stage,'successorNssStageOccurred':False,'originalFailureAndSourcesPreserved':True,'rootCauseProven':run=='run2'})
post=read(r/'postcheck-path-failure.json');assert post['error']=='EEXIST' and not post['previousEvidenceOverwritten'];failures.append({'case':'postcheck-output-path-v1','cause':post['cause'],'sourceAndFailurePreserved':True,'correctedOnlyOutputNamespace':True,'previousEvidenceOverwritten':False,'publicationStoppedUntilChecksPassed':True})
diagnostics=[]
for pattern in ['transport-diagnostic-*','transport-load32-diagnostic-*']:
    dirs=[p for p in r.glob(pattern) if p.is_dir()];assert len(dirs)==1;d=read(dirs[0]/'summary.json');assert d['readonlyRouter'] and not d['productionConfigurationWrites'] and not d['nssEnabled'] and not d['rootCauseProven']
    assert len(d['twoSequentialConnections'])==2 and all(not x['errors'] and x['received']>0 for x in d['twoSequentialConnections']);diagnostics.append(d)
health=read(r/'v1-final-health.json');physical=read(r/'physical-final.json');endpoints=read(r/'endpoint-client-closure.json');recv=read(r/'receiver-closure.json');down=read(r/'download-receiver-closure.json')
assert all(x['passed'] for x in [health,physical,endpoints,recv,down]);assert health['queryAge']<6 and health['ecmStoppedAndZero'] and health['noStaging'] and health['noExperimentState'] and health['noExperimentalModule']
assert endpoints['previousLoadsChecked']==endpoints['ownedUnitsInactiveMainPidZero']==27 and endpoints['ownedClientOrGuardProcessesRemaining']==0
assert recv['exactOwnedReceiverAndTimeoutProcessesRemaining']==down['exactOwnedReceiverAndTimeoutProcessesRemaining']==0
extras=['prepare-postchecks.py','health.mjs','read-final-physical.mjs','verify-all-endpoints.mjs','verify-receivers.mjs','verify-downloaders.mjs','verify-receivers-v1-refused.mjs','verify-downloaders-v1-refused.mjs','calibrate-clock.mjs','analyze.py','fix-postcheck-paths.py','transport-reopen-diagnostic.mjs','prepare-transport-load32.py','transport-load32-diagnostic.mjs','reporting/export.py','reporting/update-checker.py','reporting/verify-published.py']
for n in extras:sources['work/nss155/'+n]=sha((r/n).read_bytes())
for f,d in sources.items():assert f.startswith('work/nss155/') and f.endswith(('.mjs','.py','.ps1','.lua')) and all(x not in f.lower() for x in ['private','credential','connect-router']) and sha((w/f).read_bytes())==d
manifest=read(repo/'source-manifest.json');prefix=copy.deepcopy(manifest['sources']);assert len(prefix)==2371 and manifest['lastAppendExport']=='NSS154'
oldruntime=subprocess.check_output(['git','show',base+':evidence/current-runtime.json'],cwd=repo);assert read(repo/'evidence/current-runtime.json')['round']=='NSS154';assert not (repo/'evidence/nss154-runtime.json').exists()
proof={'passed':True,'historicPrefixSources':2371,'historicPrefixCanonicalSha256':sha(json.dumps(prefix,sort_keys=True,separators=(',',':')).encode()),'historicManifestPrefixUnchanged':True,'sources':len(sources),'sourceHashes':sources,'actualBindings':1836,'actualFlowExitBindings':[1831,1836],'privateCapabilityInputsBoundLocally':3,'privateCapabilityInputContentsExcluded':True,'originalRefusalSourcesKept':True,'newNativeWholePairTerminalBranch':155,'classifierKernelGateAndQoSUnchanged':True,'fullFactoryRamModelExecuted':False}
# All proof, failure and closure validation precedes any Git workspace mutation.
(repo/'evidence/nss154-runtime.json').write_bytes(oldruntime)
for f,d in sorted(sources.items()):
    p=repo/'code'/f;assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True);b=(w/f).read_bytes();p.write_bytes(b);manifest['sources'].append({'path':'code/'+f,'workspaceSource':f,'sha256':d,'bytes':len(b),'role':'owned-flow-exit-experiment-or-explicit-diagnostic-reporting'})
assert manifest['sources'][:2371]==prefix;manifest.update(lastAppendExport='NSS155',generatedAt=datetime.now(timezone.utc).isoformat(),privateDataExcluded=True,preservesOriginalSourceBytes=True);(repo/'source-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
main={'round':'NSS155','passed':True,'scope':'Only actual owned-flow-exit and whole-pair restoration passed; fresh TCP successor did not pass','status':'FLOW_EXIT_PASSED_NEW_TCP_SUCCESSOR_PENDING','observedAt':health['observedAt'],'flowExitCasesPassed':2,'completed20SecondSuccessorEpochs':0,'actualOldPairExitAndRestoration':True,'newTcpSuccessorPassed':False,'wholePairWithdrawal':True,'exactSingleCiRetirementClaimed':False,'ctExitInferredFromProjection':False,'qualifiedController':'work/nss155/pilot-supervisor-v3.mjs','boundInputs':1836,'nativeFlowExitBranch':155,'native149FullFactoryUnchanged':False,'classifierKernelGateAndQoSUnchanged':True,'sourceNativeOwnerSeconds':[6,27,100],'clientHardSeconds':180,'execRawBundleRecordBytes':[9000,65536,73728,1048576],'originalEightCandidateTcpPortBudget':8,'matchedCpuComparison':False,'cpuReductionConclusion':None,'realHumanGameAcceptance':False,'highLoad300MbpsAcceptance':False,'permanentNssControllerInstalled':False,'nssPermanentlyEnabled':False,'desktopOperated':False,'steamOrCs2Started':False,'dayHeartbeatActiveUntilBeijing':'2026-10-06T20:00:00+08:00','repositoryVisibility':'public','failuresPreserved':len(failures),'exportedSources':len(sources),'old154RuntimeRetainedSha256':sha(oldruntime),'trials':trials,'finalAudit':health,'physicalRestore':physical,'endpointClosure':endpoints}
for n,v in [('source-proof',proof),('qualification',{'passed':True,'versions':qualified,'actualBindings':1836,'wholePairExitOnly':True}),('trials',trials),('failures',failures),('software-transport-diagnostics',diagnostics),('final-audit',health),('physical-final',physical),('endpoint-client-closure',endpoints),('receiver-closure',recv),('download-receiver-closure',down),('mainline',main)]:ev(n,v)
runtime={'round':'NSS155','observedAt':health['observedAt'],'workerPid':health['workerPid'],'guardianPid':health['guardianPid'],'classifierConfigSha256':health['configSha256'],'classifierDeployment':'NSS68','qualifiedExperimentalController':main['qualifiedController'],'boundInputs':1836,'flowExitCasesPassed':2,'newTcpSuccessorPassed':False,'completed20SecondSuccessorEpochs':0,'nssPermanentlyEnabled':False,'permanentNssControllerInstalled':False,'cpuConclusion':None,'realHumanGameAcceptance':False,'dayHeartbeatActiveUntilBeijing':main['dayHeartbeatActiveUntilBeijing'],'historical154RuntimePreservedSha256':sha(oldruntime),'audit':health,'physicalRootRestoreAudit':physical,'endpointClientClosureAudit':endpoints,'ownedReceiverClosureAudit':recv,'ownedDownloadReceiverClosureAudit':down,'repositoryVisibility':'public'}
(repo/'evidence/current-runtime.json').write_text(json.dumps(runtime,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
when=datetime.fromisoformat(health['observedAt'].replace('Z','+00:00')).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
body=f'''# 真实流退出通过，新TCP后继仍待验证

更新：{when}，北京时间。最新NSS155。两次在真实ECM2时关闭自有TCP上传socket，旧双流代停止新学习、精确范围内撤销整个pair并完整恢复；原UDP应用继续收发。WAN5与WAN2分别验证，每次只有一个健康WAN。

**退出与恢复已证明；新TCP后继没有通过。** 首次SSH保活超时发生在router checkpoint/stage前；第二次退出成功但8个候选端口用尽，未开启新代；第三次先保留候选，退出成功后新SSH上传再次保活超时。失败原样保留，不把原代恢复写成后继重学通过。

1831与1836项实际绑定/冻结副本对应两次退出。每次新checkpoint下载SHA/gzip、写前PPID1独立恢复、source6/native27/owner100/client180秒和9000/65536/73728/1MiB保持；端口仍8个。常驻分类器、kernel gate和QoS计划不变；本实验只给native fast/guardian加whole-pair terminal分支，未声称149完整factory不变。投影缺失不推断CT退出，本轮不声称仅TCP CI撤销；先前151精确BULK→BE证据仍按原字节保留，部署整合时必须接回该分支。

纯软件两条连续SSH连接在约2.62Mbps及32Mbps分别短测成功，未复现保活超时，根因仍未证明。下一步使用现有自有端点的nonce认证raw TCP上传＋UDP，替代SSH上传fixture，继续新TCP重学；不改学校策略/PBR/NAT/affinity，不扩大WAN/预算/期限，不新增游戏下载。

本轮没有20秒后继、同负载CPU对照、300Mbps或真人CS2验收，CPU降幅null。终态完整原审核source{health['queryAge']:.2f}秒、NSS68/{health['workerPid']}/{health['guardianPid']}配置不变，ECM关闭全零，无事务/stage/state/模块；两物理原mq+四fq_codel恢复，27个历史端点/客户端和自有SSH接收器关闭，WAN4既有down/四路failover保持。两份postcheck旧输出路径触发EEXIST，独占创建阻止覆盖，原错误源码保存；只修正路径后检查通过再发布。

继续至20:00；19:40收尾，19:50不新开生产实验。凭据/完整CT/nonce/配置/checkpoint/二进制只在本地。旧154及更早runtime和证据原Git字节保存，仓库按用户明确偏好保持public。

证据：LINKS
'''
names=[('主线','mainline'),('退出实测','trials'),('入口','qualification'),('失败','failures'),('软件传输诊断','software-transport-diagnostics'),('终态','final-audit'),('端点','endpoint-client-closure')]
for file in ['AGENTS.md','docs/STATE.md','docs/PLAN.md','docs/EXPERIMENT_LOG.md']:
    p=repo/file;prefix='../' if file.startswith('docs/') else '';links='、'.join(f'[{label}]({prefix}evidence/nss155-{n}.json)' for label,n in names);p.write_text(body.replace('LINKS',links)+'\n## NSS154及更早历史\n\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
p=repo/'README.md';p.write_text('# Athena NSS mainline\n\n最新[NSS155](evidence/nss155-mainline.json)：真实自有TCP退出后whole-pair恢复通过，新TCP后继仍待验证。继续至20:00，先读[STATE](docs/STATE.md)。\n\n## NSS154及更早历史\n\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
page='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>NSS155 真实流退出</title><style>body{font:16px/1.8 system-ui;max-width:960px;margin:40px auto;padding:24px;color:#182638;background:#f3f5f7}pre{white-space:pre-wrap;background:white;padding:25px}a{color:#1761a2}</style><body><h1>NSS155 · 退出通过，后继待验证</h1><pre>'+html.escape(body.replace('LINKS','源码与脱敏证据见GitHub STATE'))+'</pre><a href="https://github.com/ZyPulse-zy/athena-nss-mainline/blob/main/docs/STATE.md">GitHub STATE</a></body></html>'
p=w/'outputs/nss155-mainline-report.html';assert not p.exists();p.write_text(page,encoding='utf-8');(repo/'reports/nss155-mainline-report.html').write_text(page,encoding='utf-8')
put(r/'reporting/export-receipt.json',{'passed':True,'sourcesAdded':len(sources),'sourcesTotal':len(manifest['sources']),'flowExitCasesPassed':2,'newTcpSuccessorPassed':False,'old154RuntimeGitBytesPreserved':True});print(json.dumps({'passed':True,'sourcesAdded':len(sources),'sourcesTotal':len(manifest['sources']),'flowExitPassed':2,'newTcpSuccessorPassed':False}))
