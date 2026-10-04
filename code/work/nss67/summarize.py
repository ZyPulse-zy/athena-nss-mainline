"""Measured NSS66/67 publication evidence; no CT, owner, raw config or HUD export."""
from pathlib import Path
import json,html,hashlib

def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')

def observe(root,label,mode):
 o=read(root/f'{label}-pipeline-private.json');a,b=o['telemetry'];dt=b['at']-a['at']
 ca=list(map(int,a['cpu'].split()[1:9]));cb=list(map(int,b['cpu'].split()[1:9]));d=[y-x for x,y in zip(ca,cb)]
 squeeze=lambda s:sum(int(r.split()[2],16)for r in s.splitlines())
 grouped={}
 for r in o['rows']:grouped.setdefault(r['sequence'],{})[r['name']]=r
 cycles=[]
 for seq,g in grouped.items():
  if set(g)!=set(('classification','request','apply-result','snapshot'))or any('previousSamePathAt'not in r for r in g.values()):continue
  s=g['snapshot'];q=s['queryStarted']
  cycles.append({'sequence':seq,'flows':s['flows'],'querySeconds':s['queryFinished']-q,
   'queryToFullFirstObservedSeconds':s['readStartedAt']-q,'queryToFullStampSeconds':s['publishedAt']-q,
   'stampToVisibilityLowerSeconds':s['previousSamePathAt']-s['publishedAt'],
   'stampToVisibilityUpperSeconds':s['heldReadCompletedAt']-s['publishedAt'],
   'fullParseSeconds':s['parsedAt']-s['heldReadCompletedAt']})
 return {'passed':o['passed'],'label':label,'mode':mode,'observedAt':o['observedAt'],'seconds':dt,
  'lan4Mbps':(b['txBytes']-a['txBytes'])*8/dt/1e6,'pps':(b['txPackets']-a['txPackets'])/dt,
  'busyPercent':100*(sum(d)-d[3]-d[4])/sum(d),'softirqPercent':100*d[6]/sum(d),
  'timeSqueezeDelta':squeeze(b['softnet'])-squeeze(a['softnet']),'observerCpuSeconds':o['observerCpuSeconds'],
  'observerCostIncluded':True,'backgroundLoadControlled':False,'visibilityAreObservationBounds':True,
  'fullSnapshotSizesFlows':[r['flows']for r in o['rows']if r['name']=='snapshot'],
  'completeObservedCycles':cycles,'ecmStoppedAndZeroThroughout':True,'nssAdmissionAllowed':False}

def expired_failure(root,ctx,label,kind):
 suffix='-load-audit-private.json'if kind=='instrumented'else'-audit-private.json'
 r=read(root/(label+suffix));assert r['passed']is False and r['originalAssertionsRetained']
 arm=read(Path(ctx['localDir'])/'armed-proof-private.json')
 events=r['diagnostic']['events'];assert events[0]['at']>arm['deadline']
 assert [v['name']for v in events]==['locked-audit-start','locked-audit-end']
 assert 'assertion failed!'in r['error']
 return {'label':label,'passed':False,'originalFailurePreserved':True,'originalAssertionsRetained':True,
  'afterIndependentProductionDeadline':True,'secondsAfterDeadline':events[0]['at']-arm['deadline'],
  'failedAssertion':'requested config SHA equals current production config SHA',
  'expiredCandidateContextAgainstRestoredOriginal':True,'sourceStalenessFailure':False,
  'timingStatsRejectedAsPerformanceEvidence':True,'laterRestoredOriginalAuditPassed':True}

candidate=read('work/nss64/candidate-worker-manifest.json')
summaries=[]
for number in (66,67):
 root=Path(f'work/nss{number}');ctx=read(root/'trial-private.json')
 before=read(root/'before-health.json');final=read(root/('handoff-health.json'if(root/'handoff-health.json').exists()else'final-health.json'))
 labels=['trial-first','trial-loaded-1']if number==66 else['trial-first','trial-loaded-1','trial-loaded-2']
 audits=[read(root/f'{x}-health.json')for x in labels]
 native=[read(root/f'{x}-audit-private.json')['result']for x in labels]
 assert all(x['passed']and x['originalFullLockedAudit']and x['configurationMatches']and x['ecmStoppedAndZero']for x in [before,*audits,final])
 assert len({x['producer']for x in native})==1
 assert all(x['queryAge']<6 for x in audits)
 cp=read(Path(ctx['localDir'])/'checkpoint.json');arm=read(Path(ctx['localDir'])/'armed-proof-private.json')
 installed=read(Path(ctx['localDir'])/'installed.json');undo=read(Path(ctx['localDir'])/'rollback-qualified.json');cleanup=read(root/'stage-cleanup.json')
 assert cp['gzipVerified']and installed['passed']and undo['passed']and cleanup['passed']and arm['independentOfSsh']and arm['parent']==1
 assert undo['automaticExpiryWithoutControllerRollback']
 assert all(final[k]for k in ['noActiveTransaction','noStaging','noExperimentState','noExperimentalModule'])
 window_labels=[('steam-original','original-publication-ramp'),('trial-idle','publication-candidate-idle'),('steam-candidate-1','publication-candidate-loaded'),('steam-candidate-2','publication-candidate-loaded')]if number==66 else[(f'steam-candidate-{x}','publication-candidate-loaded')for x in (1,2,3)]+[('steam-restored','original-publication-restored-loaded'),('final-idle','original-publication-restored-idle')]
 windows=[observe(root,*x)for x in window_labels]
 late=expired_failure(root,ctx,'trial-loaded-2'if number==66 else'trial-loaded-exact','original'if number==66 else'instrumented')
 exact=read(root/'restored-loaded-load-audit-sanitized.json')if number==67 else None
 if exact:assert exact['passed']and exact['measurementCoversActualAudit']and exact['queryAge']<6
 client={'noGameLaunched':True,'noPurchaseOrUninstall':True,'noCs2ProcessAtFinalCheck':True,'actualHumanGameMetricsAvailable':False,
  'independent360SecondClientGuard':True,'networkLoadNoLongerRunning':True}
 if number==66:
  first=read(root/'client-window/result.json');second=read(root/'client-window2/result.json')
  assert first['passed']and first['timedExitExecuted']and first['exactOriginalSteamInstanceGone']
  assert second['passed']and second['cancelledAfterClientRestore']and not second['timedExitExecuted']
  client.update({'title':'Disco Elysium','library':'D:','requiredSpaceGb':9.57,'downloadCompleted':True,'downloadedUiGb':8.7,
   'firstGuardNaturalTimedGracefulExitVerified':True,'secondGuardCancelledOnlyAfterCompletedUiZeroNetworkAndDisk':True,
   'uiPeakBeforeFirstExitMbps':331.7,'restartSessionFinalUiPeakMbps':224.1,'uiPeakIsNotWholeRouterWindow':True})
 else:
  end=read(root/'client-window/result.json');assert end['passed']and end['cancelledAfterClientRestore']and not end['timedExitExecuted']
  client.update({'title':'Dead by Daylight','library':'D:','requiredSpaceGb':61.01,'freeSpaceBeforeGb':298.21,
   'downloadPausedAtUiPercent':17,'downloadCompleted':False,'networkBpsAtFinalUi':0,'diskBpsAtFinalUi':0,
   'finalUiPeakMbps':381.3,'uiPeakIsNotWholeRouterWindow':True,'guardCancelledOnlyAfterObservedPause':True,
   'noDesktopOrStartMenuShortcutsSelected':True,'existingScheduled317KbUpdateUnchanged':True,
   'partialAuthorizedDownloadLeftPaused':True})
 pipeline={'windows':windows,'matchedABANotClaimed':True,'wholeRouterCpuBenefitNotClaimed':True,
  'sourceMarkerPrecedesJsonEncodingNotRename':True,'exactRestoredAuditLoad':exact,'lateExpiredContextFailure':late}
 save(root/'pipeline-sanitized.json',pipeline)
 loaded=[x for x in windows if x['mode']=='publication-candidate-loaded']
 above300=[x for x in loaded if x['lan4Mbps']>=300]
 summary={'round':f'NSS{number}','observedAt':final['observedAt'],'deploymentReference':'work/nss47/deployment-latest.json',
  'classifierConfigSha256':final['configSha256'],'permanentClassifierChanged':False,'routerConfigurationWrites':True,
  'publicationCandidateActuallyInstalled':True,'candidateRetainedAtEnd':False,'candidateWorkerSha256':candidate['candidateWorkerSha256'],
  'onlyPublicationBoundaryAndTransactionIdentityChanged':True,'sourcePolicyClassifierLearningAndAllDeadlinesUnchanged':True,
  'originalNonSnapshotSerializationUnchanged':True,'untouchedNormalizerGuardianBackendCore':True,
  'currentEntry':{'path':'work/nss63/real-session.mjs','boundInputs':241,'unchanged':True,'candidateEntryBindingCreated':False},
  'checkpointCount':1,'rollbackTrialCount':1,
  'protection':{'checkpointDownloadedHashAndGzipVerified':True,'independentStageGuardianVerifiedBeforeUpload':True,
   'independentProductionUndoVerifiedBeforeMutation':True,'independentOfControlConnection':True,'productionUndoSeconds':180,
   'stageGuardianSeconds':480,'originalSixSecondRunnerUnchanged':True},
  'installation':{'passed':True,'workerBytes':32019,'guardVerifiedIndependentParent':1,
   'originalFullLockedAuditPassesDuringTrial':len(audits),'fullSnapshotSourceAgeSecondsAtAudits':[x['queryAge']for x in audits],
   'candidateWorkerGuardianAndProducerContinuousBetweenAudits':True,'onlyClassifierLifecycleStoppedAndStarted':True,
   'noProductionRootQdiscRebuild':True},
  'candidateAudits':audits,'actualTrafficWindows':windows,'lateExpiredContextFailure':late,'exactRestoredAuditLoad':exact,
  'rollback':{k:v for k,v in undo.items()if k not in ('transaction','pid')},'stageCleanup':cleanup,
  'finalState':{'protectedAudit':final,'workerPid':final['workerPid'],'guardianPid':final['guardianPid'],
   'sameInstancesSinceOpening':False,'expectedRestartForTrialAndRestore':True,'ecmStoppedAndZero':True,
   'noActiveTransaction':True,'noStaging':True,'noExperimentState':True,'noExperimentalModule':True},
  'client':client,'nssOpenedThisTurn':False,'newNssForwardingExperiment':False,
  'proofBoundary':{'oldNative36And29Reexecuted':False,'old99And13Reexecuted':False,'realSteamDownloadLoadPresent':True,
   'loadedCandidateWindowsAtOrAbove300Mbps':len(above300),'originalAuditsUseFullSnapshotNotMetadataReplacement':True,
   'loadAuditsAndFourSecondWindowsAdjacentNotSameWindow':True,'noGameHudOrHumanExperienceMeasured':True,
   'nssLeafCountersAndCakeTinNotMeasured':True,'noNewAcceleratedFlowMarkNatWanProof':True},
  'conclusions':{'publicationCandidateLiveAndOriginalAuditPassed':True,'preciseIndependentNaturalUndoPassed':True,
   'testedAbove300MbpsPublicationWindowSupported':bool(above300),'generalHighLoadStabilityProved':False,
   'wholeRouterCpuBenefitProved':False,'realHumanGameImprovementProved':False,'completeMatchedABACompleted':False,
   'secondWanExpansionAllowed':False,'upstreamSubmitted':False},
  'nextStep':'Bind the exact qualified publication worker/config/actual deployment context to the existing single-WAN NSS entry, preserving all 241 original inputs and source/owner limits, then use the paused existing download in a concentrated real CS2 matched A/B/A2. Do not reinstall the classifier, rerun old preparation or expand WANs.',
  'reportVerification':{'sourceValidated':True,'browserRendered':False}}
 if number==66:
  probes=[read(root/f'load-probe{x}.json')for x in ('','2')]
  summary['failedPublicLoadProbes']=[{'parallel':p['parallel'],'configuredSeconds':p['seconds'],'receivedBytes':p['receivedBytes'],
   'httpStatuses':sorted({r.get('httpStatus')for r in p['requests']if r.get('httpStatus')is not None}),
   'notQualifiedSteadyHighLoad':True,'allPayloadDiscardedAndNeverExecuted':True}for p in probes]
  summary['publicProbe429StoppedAndNotRetried']=True
 save(f'outputs/nss{number}-mainline-observations.json',summary);summaries.append(summary)

for s in summaries:
 n=s['round'];w=s['actualTrafficWindows'];f=s['finalState']['protectedAudit']
 high=s['conclusions']['testedAbove300MbpsPublicationWindowSupported']
 parts=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
  f'<title>{n} · 真实下载下的发布验证</title><style>body{{background:#f2f4f6;color:#162333;font:16px/1.7 system-ui,Microsoft YaHei;margin:0}}main{{max-width:1050px;margin:36px auto;padding:32px;background:white;border-radius:18px}}h1{{font-size:30px}}h2{{font-size:21px;margin-top:30px}}table{{border-collapse:collapse;width:100%;font-size:14px}}td,th{{padding:9px;border-bottom:1px solid #d9e0e6;text-align:left}}small{{color:#657284}}.lead{{padding:20px;background:#e9f4f1;border-radius:10px}}code{{word-break:break-all}}a{{color:#156257}}</style><main>',
  f'<h1>{n} · 真实下载下的发布验证</h1><small>2026-10-05 北京时间 · 单一 publication 变量 · ECM 保持关闭</small>',
  '<p class="lead">'+('本轮候选在路由器实测 300 Mbps 以上的真实 Steam 下载中运行，两次高负载期间的原完整审核通过。原 6 秒来源限制、完整字段和审核保持。'if high else'候选已在真实下载下运行并通过原完整审核，但本轮路由器测量为 148–209 Mbps，不足以验证 300 Mbps 以上。后续 NSS67 已另行补充更高负载证据。')+'180 秒独立回滚自然到期，原 worker、配置、版本指针和四个模块精确恢复。</p>',
  '<h2>变更、负载和实际观测</h2><p>写前创建 checkpoint，下载并验证 SHA 和 gzip，分别核验独立 480 秒暂存守护与 180 秒生产撤销。只替换 32,019 字节完整 JSON 发布 worker 和对应 config.files/事务身份。分类策略、学习、PBR/NAT、十个生产根 qdisc、所有原期限保持；没有开放 ECM 或新的 NSS leaf。</p>',
  '<p>候选原完整审核 source 年龄：'+', '.join(f'{a["queryAge"]:.2f} 秒'for a in s['candidateAudits'])+'。高负载完整审核与下表四秒窗口是相邻采样，不是同一测量窗口。候选窗口包含观察器成本，不能据 busy/softirq 差异作因果收益结论。</p>',
  '<table><tr><th>窗口</th><th>Mbps / pps</th><th>busy / softirq</th><th>time_squeeze</th><th>完整快照条数</th></tr>']
 for x in w:
  parts.append(f'<tr><td>{html.escape(x["label"])}</td><td>{x["lan4Mbps"]:.3f} / {x["pps"]:.0f}</td><td>{x["busyPercent"]:.2f}% / {x["softirqPercent"]:.2f}%</td><td>+{x["timeSqueezeDelta"]}</td><td>{html.escape(str(x["fullSnapshotSizesFlows"]))}</td></tr>')
 parts+=['</table><p>完整 publish 的 query→首次可见是观察界限；atUptime 标记仍在 JSON 编码前，不能将 stamp→可见全算为编码成本。没有同负载 A/B/A2，未测 CAKE tin 或 NSS leaf 计数。NSS 未开放，本轮没有新的加速流 mark/NAT/WAN affinity 证明。</p>']
 if s['exactRestoredAuditLoad']:
  a=s['exactRestoredAuditLoad'];parts.append(f'<p>恢复后的原完整审核另有同窗流量计数：{a["lan4Mbps"]:.2f} Mbps / {a["pps"]:.0f} pps，审核 {a["seconds"]:.2f} 秒、source {a["queryAge"]:.2f} 秒。距原 6 秒上限仅约 {6-a["queryAge"]:.2f} 秒；不能据这一短窗保证稳定，也不是候选与原版 CPU 对照。</p>')
 parts+=['<h2>失败、回滚和客户端恢复</h2><p>保留了一次到期后的旧候选 context 审核失败：独立生产期限已过，原配置已经恢复，候选 config SHA 与现网不符，在配置断言立即拒绝。它不是 source 超时失败，微小失败窗口的流量和 CPU 统计不作性能证据；之后原配置的完整审核通过。原失败输出未覆盖。</p>',
  f'<p>180 秒生产撤销自然执行，没有控制器主动回滚；其后核验旧 worker/config SHA、版本指针及其余四模块，健康快照和原保护审核通过。按精确 owner/inode 主动取消已无生产作用的暂存，不宣称该 stage 自然 480 秒到期。最终常驻 NSS47，worker {f["workerPid"]} / guardian {f["guardianPid"]}，ECM 关闭全零，无事务、暂存、state 或实验模块。</p>',
  '<p>'+('Disco Elysium 下载完成，界面显示 8.7 GB。第一段独立客户端限时守护确实自然执行 Steam -shutdown，并验证原进程退出；重开后下载自动接续。最后网络和磁盘均 0 bps，第二个客户端守护在确认完成后取消。'if n=='NSS66'else'依照已授权的库内下载选取黎明杀机，放到 D 盘，安装要求 61.01 GB、起始可用 298.21 GB，未选快捷方式。短测后在 17% 暂停，实际界面确认网络/磁盘 0 bps，独立客户端守护随后取消。保留部分下载，没有购买、卸载或启动游戏；此前的 317 KB 自动更新未操作。')+'</p>']
 if n=='NSS66':parts.append('<p>先前公共下载探针分别返回 403 和 429，未取得合格稳定高负载，429 后停止且未继续重试。负载 payload 丢弃未执行。随后改用已授权的 Steam 下载。这些失败不计为高负载成功。</p>')
 parts+=['<h2>支持的结论及下一步</h2><p>'+('支持“该完整 JSON 发布候选在本次 300 Mbps 以上真实下载中仍能通过原完整审核，且可以独立精确恢复”。'if high else'支持“候选在本次实际下载中能通过原完整审核并独立精确恢复”。')+'不支持“所有高负载过期都解决”“整机 CPU 获益”或“CS2 jitter/loss/Miss 改善”。本轮没有真实 CS2/HUD/真人体验，缺失指标不填零。</p>',
  '<p>下一步是将候选精确 worker/config 和实际部署 context 绑定到单 WAN NSS 入口，保留原 241 项输入、20 Mbps、一 TCP＋一 UDP、45 秒 owner 及 1/2/6/9 秒 source 限制；随后集中使用已有暂停下载和真实 CS2 做完整可比 software→NSS→software。当前旧入口未改变，本次 publication 试装不能当作新 NSS 准入资格。</p>',
  '<p>源码和脱敏证据同步到 <a href="https://github.com/ZyPulse-zy/athena-nss-mainline">私有仓库</a>，原配置、checkpoint、owner、CT/socket 和截图只留本地。不提交上游，不扩 WAN/共享预算，不重复旧合同和分类器安装。报告源验证通过，浏览器渲染未核验。</p></main></html>']
 Path(f'outputs/{n.lower()}-mainline-report.html').write_text('\n'.join(parts),encoding='utf-8',newline='\n')
 print(json.dumps({'round':n,'summaryPassed':True,'fullAudits':s['installation']['originalFullLockedAuditPassesDuringTrial'],
  'candidateLoadedMbps':[x['lan4Mbps']for x in w if x['mode']=='publication-candidate-loaded'],
  'sourceAges':s['installation']['fullSnapshotSourceAgeSecondsAtAudits'],'independentNaturalUndo':True,'ecmZero':True}))
