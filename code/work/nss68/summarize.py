"""Actual retention, context binding and bounded observations; no benefit inference."""
from pathlib import Path
import json,hashlib,html
R=Path('work/nss68');O=Path('outputs')
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
ctx=read(R/'deployment-latest.json');case=Path(ctx['localDir'])
commit=read(case/'permanent-commit.json');arm=read(case/'armed-proof-private.json')
final=read(R/'final-health.json');initial=read(R/'retained-first-health.json');entry=read(R/'entry-qualified.json')
pre=read(R/'retained-context-prewrite-audit.json');post=read(R/'retained-context-recovery-audit.json')
reader=read(R/'real-reader-qualified.json');ready=read(R/'real-session-readiness.json')
diag=read(R/'worker-recovery-private.json');rawlog=read(R/'recovery-lua-syslog-private.json')
assert ctx['committed'] and ctx['permanentClassifier'] and commit['remoteCommittedReceiptVerified']
assert arm['passed'] and arm['independentOfSsh'] and final['passed'] and pre['passed'] and post['passed']
assert final['configSha256']==ctx['configHash'] and final['ecmStoppedAndZero']
assert entry['baseBoundInputs']==241 and entry['checks']==17
p=read(R/'load-first-pipeline-private.json');a,b=p['telemetry'];dt=b['at']-a['at']
cpu=lambda x:list(map(int,x.split()[1:9]));d=[y-x for x,y in zip(cpu(a['cpu']),cpu(b['cpu']))];total=sum(d)
squeeze=lambda x:sum(int(line.split()[2],16) for line in x.strip().splitlines())
window={'passed':p['passed'],'seconds':dt,'lan4Mbps':(b['txBytes']-a['txBytes'])*8/dt/1e6,'pps':(b['txPackets']-a['txPackets'])/dt,'busyPercent':100*(total-d[3]-d[4])/total,'softirqPercent':100*d[6]/total,'timeSqueezeDelta':squeeze(b['softnet'])-squeeze(a['softnet']),'observerCostIncluded':True,'observerCpuSeconds':p['observerCpuSeconds'],'nssAdmissionAllowed':False,'qualifiedHighLoad':False}
loadAudit=read(R/'retained-loaded-load-audit-sanitized.json');assert window['lan4Mbps']<300 and loadAudit['lan4Mbps']<300
workerError=diag['lastError'];assert workerError['pid']==initial['workerPid']!=final['workerPid']
assert 'tc child cleanup not proved' in rawlog['stdout'] and 'rawStatus=256' in workerError['error']
currentWorker=Path('work/nss64/candidate-worker.lua').read_text(encoding='utf-8')
oldWorker=(Path(ctx['previous']['localDir'])/'worker.lua').read_text(encoding='utf-8')
extract=lambda s:s[s.index('local TCCommand=(function()'):s.index('local function bounded(argv,cap)')]
assert extract(oldWorker)==extract(currentWorker)
client=read(R/'client-window/result.json');ui=read(R/'client-restored-ui-private.json')
assert client['passed'] and client['cancelledAfterClientRestore'] and ui['pausedObserved'] and ui['networkZeroObserved']
combined=len(entry['sourceManifest'])+entry['baseBoundInputs']
out={'round':'NSS68','observedAt':final['observedAt'],'deploymentReference':'work/nss68/deployment-latest.json','classifierConfigSha256':ctx['configHash'],'candidateWorkerSha256':commit['workerSha256'],'candidateWorkerBytes':32019,
 'routerConfigurationWrites':True,'permanentClassifierChanged':True,'candidateRetainedAtEnd':True,'nssOpenedThisTurn':False,'newNssForwardingExperiment':False,
 'retention':{**{k:v for k,v in commit.items() if k not in ('transactionId',)},'checkpointCount':1,'originalFourModulesUnchanged':True,'old47And49ReferencesPreserved':True,'productionUndoSeconds':180,'stageGuardianSeconds':480,'committedBeforeDeadline':True,'newNaturalUndoTrialClaimed':False,'prior66And67NaturalUndoReusedAsEvidence':True,'onlyPublicationBoundaryAndOwnerConfigChanged':True},
 'stageCleanup':read(R/'stage-cleanup.json'),
 'entry':{'path':'work/nss68/real-session.mjs','baseInputs':241,'overlayInputs':len(entry['sourceManifest']),'boundInputs':combined,'checks':entry['checks'],'explicitCommittedDeploymentForReaderAuditStage':True,'originalPolicyPayloadAndTimersUnchanged':True,'nativeGateStagingExecutedThisTurn':False,'prewriteReadOnlyAudit':pre,'recoveryReadOnlyAudit':post,'consumerReadOnly':reader,'readiness':ready},
 'workerLifecycle':{'naturalRestartObserved':True,'firstWorkerPid':initial['workerPid'],'currentWorkerPid':final['workerPid'],'guardianPid':final['guardianPid'],'guardianUnchanged':initial['guardianPid']==final['guardianPid'],'restartBeforeDownloadResume':True,'applyRawStatus':256,'applyElapsedSeconds':4.35,'identifiedFailureBoundary':'tc child cleanup not proved; outer mutation must terminate','childCommandAndPidNotLogged':True,'underlyingKernelCauseProved':False,'tcSupervisorByteIdenticalToPrevious47':True,'currentOriginalAuditPassed':True,'sameProducerAcrossNewPrewriteAndRecovery':True,'noInducedCrashThisTurn':True},
 'actualTrafficWindow':window,'actualAuditWindow':loadAudit,
 'client':{'existingPausedDownloadResumed':True,'steamInstantaneousUiMbps':312,'actualSustained300MbpsNotObserved':True,'returnedPausedBeforeAudit':True,'pauseCauseNotEstablished':True,'downloadFinallyPaused':True,'networkAndDiskZeroObserved':True,'independentClientWatchdogSeconds':360,'watchdogCancelledAfterPauseObserved':True,'naturalClientShutdownThisRound':False,'noNewGameDownload':True,'noPurchaseUninstallOrGameLaunch':True,'actualCs2Candidates':reader['actualCs2RtCandidates'],'actualSteamCandidatesAtReader':reader['actualSteamBulkCandidates']},
 'finalState':{'protectedAudit':final,'noActiveTransaction':final['noActiveTransaction'],'noStage':final['noStaging'],'noExperimentalModule':final['noExperimentalModule'],'noState':final['noExperimentState'],'ecmClosedAndZero':final['ecmStoppedAndZero']},
 'conclusions':{'candidateRetentionAndExplicitBindingProved':True,'newContextPrewriteReadOnlyAuditProved':True,'highLoadAdmissionProvedThisRound':False,'newRealFlowLearningOrLeafProof':False,'wholeRouterCpuBenefitProved':False,'realHumanExperienceProved':False,'completeMatchedABACompleted':False,'generalLongTermStabilityProved':False,'secondWanExpansionAllowed':False,'upstreamSubmitted':False},
 'reportVerification':{'sourceValidated':True,'browserRendered':False}}
text=json.dumps(out,ensure_ascii=False,indent=2)+'\n'
(O/'nss68-mainline-observations.json').write_text(text,encoding='utf-8',newline='\n')
rows=''.join(f'<tr><td>{html.escape(k)}</td><td>{html.escape(str(v))}</td></tr>'for k,v in [('常驻部署','NSS68 / '+ctx['configHash']),('worker / guardian',f"{final['workerPid']} / {final['guardianPid']}"),('新入口',f"原241 + 新{len(entry['sourceManifest'])} = {combined}项，17项绑定检查"),('完整准入 / 恢复审核',f"source {pre['queryAge']:.2f} / {post['queryAge']:.2f}秒"),('实际4秒流量',f"{window['lan4Mbps']:.2f}Mbps / {window['pps']:.0f}pps"),('busy / softirq / squeeze',f"{window['busyPercent']:.2f}% / {window['softirqPercent']:.2f}% / +{window['timeSqueezeDelta']}"),('ECM','关闭 / 全零'),('下载','现有黎明杀机已暂停；未新增游戏')])
page=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NSS68：发布候选保留与新入口绑定</title><style>body{{font:16px/1.7 system-ui,sans-serif;max-width:980px;margin:36px auto;padding:0 24px;background:#f5f7fa;color:#202933}}h1{{font-size:28px}}section{{background:white;padding:20px 26px;margin:18px 0;border:1px solid #dde3ea;border-radius:12px}}table{{width:100%;border-collapse:collapse}}td{{padding:10px;border-bottom:1px solid #e4e9ef}}td:first-child{{width:32%;font-weight:600}}.warn{{border-left:5px solid #c17c20}}</style><h1>NSS68：发布候选已长期保留，新入口已绑定</h1><p>2026-10-05 · 单 WAN 主线 · 本轮没有开启 NSS</p><section><p>32,019字节完整JSON发布候选已在checkpoint和写前验证的独立180秒回滚保护下保留。实际远端commit、配置/worker SHA及指针均读回验证；独立常驻健康守护继续运行。新消费者、完整审核和stage使用同一明确部署，原47/49引用及全部241项旧资格保持。</p><table>{rows}</table></section><section class="warn"><h2>发现一次自然退出，已自动恢复</h2><p>10:32:50–10:32:52，tc子进程回收未获证明，apply子进程状态256、耗时4.35秒，原worker退出；随后健康实例恢复。TC监督源码与47相同，发生在恢复下载之前。没有具体tc命令、child PID或阻塞栈，不能归因于JSON改动、下载负载或内核缺陷；不能称长期稳定已验收。</p></section><section><h2>本轮证明与边界</h2><p>17项新绑定检查和原完整准入/恢复现场审核通过；所有读者核验实际committed部署。Steam界面瞬时312Mbps后已回到暂停，测量窗仅{window['lan4Mbps']:.2f}Mbps，不能算300Mbps准入证明。本轮无真实CS2配对、ECM学习、bulk/RT leaf或HUD/真人体验，CPU读数包含观察器且没有同负载NSS对照。</p><p>候选留驻成功，本轮没有再触发自然180秒撤销；此前66/67自然恢复证明保留。自己的passive stage在commit后按owner/inode取消，客户端360秒守护在观察到暂停后取消。最终原完整审核、无事务/暂存/模块/state与ECM关闭全零通过。</p></section><section><h2>下一步</h2><p>直接用work/nss68/real-session.mjs，在一次真实CS2＋现有Steam下载窗口做单WAN同TCP/UDP、同负载software→NSS→software。每次重新核验当前producer、来源和连接身份；若分类器在实验中更换实例则拒绝并精确回滚。已有完整发布证据和准备不重放，不扩大20Mbps/一TCP一UDP/45秒与原source限制，不扩第二WAN。</p></section></html>'''
(O/'nss68-mainline-report.html').write_text(page,encoding='utf-8',newline='\n')
print(json.dumps({'summarized':True,'candidateRetained':True,'boundInputs':combined,'realForwardingTestThisRound':False,'naturalRestartRecorded':True,'actualMbps':window['lan4Mbps']},ensure_ascii=False))
