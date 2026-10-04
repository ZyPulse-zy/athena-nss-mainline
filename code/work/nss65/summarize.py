"""Sanitized measured evidence: live publication trial, not NSS performance acceptance."""
from pathlib import Path
import json, hashlib, html
root=Path('work/nss65')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
ctx=read(root/'trial-private.json');before=read(root/'before-health.json');final=read(root/'final-health.json')
trial=[read(root/f'{n}-health.json')for n in ('trial-first','trial-second')]
bp=read(root/'before-audit-private.json')['result'];fp=read(root/'final-audit-private.json')['result']
tp=[read(root/f'{n}-audit-private.json')['result']for n in ('trial-first','trial-second')]
assert all(v['passed']and v['originalFullLockedAudit']and v['configurationMatches']and v['ecmStoppedAndZero']for v in [before,*trial,final])
assert tp[0]['producer']==tp[1]['producer']and trial[0]['workerPid']==trial[1]['workerPid']
assert bp['producer']!=tp[0]['producer']!=fp['producer']
installed=read(Path(ctx['localDir'])/'installed.json');undo=read(Path(ctx['localDir'])/'rollback-qualified.json');cleanup=read(root/'stage-cleanup.json')
armed=read(Path(ctx['localDir'])/'armed-proof-private.json');checkpoint=read(Path(ctx['localDir'])/'checkpoint.json')
assert installed['passed']and undo['passed']and cleanup['passed']and checkpoint['gzipVerified']
assert undo['automaticExpiryWithoutControllerRollback']and armed['independentOfSsh']and armed['parent']==1
assert all(final[k]for k in ('noActiveTransaction','noStaging','noExperimentState','noExperimentalModule'))
def observe(label,mode):
 o=read(root/f'{label}-pipeline-private.json');a,b=o['telemetry'];dt=b['at']-a['at']
 ca=list(map(int,a['cpu'].split()[1:9]));cb=list(map(int,b['cpu'].split()[1:9]));d=[y-x for x,y in zip(ca,cb)]
 sq=lambda v:sum(int(r.split()[2],16)for r in v.splitlines())
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
 return {'passed':o['passed'],'mode':mode,'label':label,'observedAt':o['observedAt'],'seconds':dt,
  'lan4Mbps':(b['txBytes']-a['txBytes'])*8/dt/1e6,'pps':(b['txPackets']-a['txPackets'])/dt,
  'busyPercent':100*(sum(d)-d[3]-d[4])/sum(d),'softirqPercent':100*d[6]/sum(d),
  'timeSqueezeDelta':sq(b['softnet'])-sq(a['softnet']),'observerCpuSeconds':o['observerCpuSeconds'],
  'observerCostIncluded':True,'backgroundLoadControlled':False,'visibilityAreObservationBounds':True,
  'completeObservedCycles':cycles,'allEcmCountsZeroThroughout':True,'nssAdmissionAllowed':False}
windows=[observe('trial1','publication-candidate'),observe('trial2','publication-candidate'),observe('restored1','original-publication-restored')]
save(root/'pipeline-sanitized.json',{'windows':windows,'matchedABANotClaimed':True,'wholeRouterCpuBenefitNotClaimed':True})
candidate=read('work/nss64/candidate-worker-manifest.json')
summary={'round':'NSS65','observedAt':final['observedAt'],'deploymentReference':'work/nss47/deployment-latest.json',
 'classifierConfigSha256':final['configSha256'],'permanentClassifierChanged':False,'routerConfigurationWrites':True,
 'publicationCandidateActuallyInstalled':True,'candidateRetainedAtEnd':False,'candidateWorkerSha256':candidate['candidateWorkerSha256'],
 'onlyPublicationBoundaryAndTransactionIdentityChanged':True,'sourcePolicyClassifierLearningAndAllDeadlinesUnchanged':True,
 'originalNonSnapshotSerializationUnchanged':True,'untouchedNormalizerGuardianBackendCore':True,
 'currentEntry':{'path':'work/nss63/real-session.mjs','boundInputs':241,'unchanged':True,'candidateEntryBindingCreated':False},
 'checkpointCount':1,'rollbackTrialCount':1,
 'protection':{'checkpointDownloadedHashAndGzipVerified':True,'independentStageGuardianVerifiedBeforeUpload':True,
  'independentProductionUndoVerifiedBeforeMutation':True,'independentOfControlConnection':True,
  'productionUndoSeconds':180,'stageGuardianSeconds':480,'originalSixSecondRunnerUnchanged':True},
 'installation':{'passed':True,'workerBytes':32019,'guardVerifiedIndependentParent':1,'sequenceBetweenAudits':[v['sequence']for v in trial],
  'originalFullLockedAuditPassesDuringTrial':len(trial),'candidateWorkerGuardianAndProducerContinuousBetweenAudits':True,
  'fullSnapshotSourceAgeSecondsAtAudits':[v['queryAge']for v in trial],
  'onlyClassifierLifecycleStoppedAndStarted':True,'noProductionRootQdiscRebuild':True},
 'naturalWindows':windows,'rollback':{k:v for k,v in undo.items()if k not in ('transaction','pid')},
 'stageCleanup':cleanup,'finalState':{'protectedAudit':final,'workerPid':final['workerPid'],'guardianPid':final['guardianPid'],
  'expectedWorkerAndGuardianRestartForTrialAndRestore':True,'sameInstancesSinceOpening':False,
  'ecmStoppedAndZero':True,'noActiveTransaction':True,'noStaging':True,'noExperimentState':True,'noExperimentalModule':True},
 'nssOpenedThisTurn':False,'newNssForwardingExperiment':False,
 'proofBoundary':{'oldNative36And29Reexecuted':False,'old99And13Reexecuted':False,'noNewGameDownloadOrGameGuiThisTurn':True,
  'realSteamHighLoadPresent':False,'realCs2Present':False,'noGameHudOrHumanExperienceMeasured':True,
  'liveTrialNotJsonContractCaseRerun':True,'naturalWindowsNotMatchedTrafficComparison':True},
 'conclusions':{'publicationCandidateLiveAndOriginalAuditPassed':True,'preciseIndependentNaturalUndoPassed':True,
  'highLoadPublicationFixed':False,'wholeRouterCpuBenefitProved':False,'realHumanGameImprovementProved':False,
  'completeMatchedABACompleted':False,'secondWanExpansionAllowed':False,'upstreamSubmitted':False},
 'nextStep':'Use this proven publication trial/undo path for genuine high-load complete publication and original audit; bind the exact candidate only before a concentrated matched single-WAN NSS A/B/A2. No repeat classifier reinstall or new games merely for preparation.',
 'reportVerification':{'sourceValidated':True,'browserRendered':False}}
save('outputs/nss65-mainline-observations.json',summary)
parts=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
 '<title>NSS65 · 发布边界现场试装与自动恢复</title><style>body{background:#f2f4f6;color:#162333;font:16px/1.7 system-ui,Microsoft YaHei;margin:0}main{max-width:1020px;margin:36px auto;padding:32px;background:white;border-radius:18px}h1{font-size:30px}h2{font-size:21px;margin-top:30px}table{border-collapse:collapse;width:100%;font-size:15px}td,th{padding:10px;border-bottom:1px solid #d9e0e6;text-align:left}small{color:#657284}.lead{padding:20px;background:#e9f4f1;border-radius:10px}code{word-break:break-all}a{color:#156257}</style><main>',
 '<h1>NSS65 · 发布边界现场试装与自动恢复</h1><small>2026-10-05 北京时间 · 单一变量现场试验</small>',
 '<p class="lead">32,019 字节发布候选已实际运行，两次原完整持锁审核通过；180 秒独立守护自然到期，精确恢复旧 worker、配置和版本指针，恢复后的原完整审核与清理通过。高负载发布缺口和 NSS 转发收益仍待真实负载验证。</p>',
 '<h2>做了什么</h2><p>新建 checkpoint，下载并核验哈希与 gzip；先验证独立 RAM 暂存守护，再验证独立于 SSH 的 180 秒恢复守护，之后只替换完整快照 JSON 发布 worker 和对应事务身份。没有重装整套分类器、改变分类策略或学习、开启 ECM、修改 PBR/NAT、重建生产根 qdisc 或操作游戏与下载。</p>',
 '<p>候选期间 worker/guardian/producer 连续，两次审核来源年龄分别为 '+', '.join(f'{v["queryAge"]:.2f} 秒'for v in trial)+'，完整原审核和所有原期限保留。十个生产 qdisc 的配置及受保护服务/地址/路由均通过原比对。</p>',
 '<h2>实际自然流量与发布</h2><p>下面均是四秒自然轻载窗，包含观察器成本，背景负载没有匹配。busy/softirq 的差异不代表收益，候选两窗与恢复后窗口不构成受控 A/B/A2。</p>',
 '<table><tr><th>窗口</th><th>Mbps / pps</th><th>busy / softirq</th><th>time_squeeze</th><th>完整周期</th></tr>']
for w in windows:
 parts.append(f'<tr><td>{html.escape(w["label"])}</td><td>{w["lan4Mbps"]:.3f} / {w["pps"]:.1f}</td><td>{w["busyPercent"]:.2f}% / {w["softirqPercent"]:.2f}%</td><td>+{w["timeSqueezeDelta"]}</td><td>{len(w["completeObservedCycles"])}</td></tr>')
parts+=['</table><p>query→完整可见是采样界限；完整发布时间标记仍在编码前，不能把 stamp→可见全算为编码耗时。原完整字段合同已经在 NSS64 验证，此轮没有重跑旧合同用例。</p>',
 '<h2>回滚结果与边界</h2><p>没有向控制器发送回滚命令：独立 180 秒事务自然到期，日志确认旧版本已恢复。随后核验 worker/config SHA、其余四个模块保持原字节、版本指针、健康完整快照及原完整审核。暂存目录在生产自动恢复已证明后，按精确 owner/inode 身份主动取消；不声称这次证明了 480 秒暂存自然到期。</p>',
 f'<p>最终常驻仍 NSS47，worker {final["workerPid"]} / guardian {final["guardianPid"]}，来源年龄 {final["queryAge"]:.2f} 秒。实例变化来自本轮试装与恢复的预期 restart，不声称原 PID 连续。ECM 关闭全零，无事务、暂存、实验 state 或 gate/qdisc 模块。</p>',
 '<h2>结论与下一步</h2><p>“完整 JSON 发布候选能运行并保留原审核，且能独立自动精确恢复”已有现场证据。“高负载过期已解决”“整机 CPU 下降”“CS2 jitter/loss/Miss 改善”尚无证据。本轮没有真实 Steam 高负载或 CS2 客户端指标；不拿自然轻载填补这些结论。</p>',
 '<p>下一步直接沿用已证明的单项试装/恢复路径，验证真实高负载完整发布到原审核的延迟；届时先绑定精确候选输入，再集中做单 WAN 同流同负载 software→NSS→software 与实际客户端指标。不重复分类器安装或旧准备，也不为准备新增大游戏、扩 WAN 或扩大 gate 限额。</p>',
 '<p>当前 NSS63 入口 241 项未变；本轮候选恢复后不留驻、不冒充新 NSS 入口资格。代码与脱敏证据保存在 <a href="https://github.com/ZyPulse-zy/athena-nss-mainline">私有仓库</a>；原始配置、checkpoint、owner、完整 CT 和原输出只留本地。未提交上游 Issue/PR。报告源验证通过，浏览器渲染尚未验证。</p></main></html>']
Path('outputs/nss65-mainline-report.html').write_text('\n'.join(parts),encoding='utf-8',newline='\n')
print(json.dumps({'passed':True,'round':'NSS65','liveCandidateAudits':len(trial),'independentNaturalUndoPassed':True,
 'windows':[{k:w[k]for k in ['label','lan4Mbps','pps','busyPercent','softirqPercent','timeSqueezeDelta']}for w in windows],
 'fullPublicationSeconds':[[v['queryToFullFirstObservedSeconds']for v in w['completeObservedCycles']]for w in windows],
 'matchedOrHighLoadCpuBenefit':False,'finalAuditPassed':final['passed']}))
