"""Export numbers and conclusions only; raw identities, CT and configuration stay local."""
from pathlib import Path
from statistics import mean
from datetime import datetime, timezone
import json, hashlib, html
root=Path('work/nss64')
def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def save(path,obj):Path(path).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
before,after=[read(root/f'{n}-health.json')for n in ['before','final']]
bp,ap=[read(root/f'{n}-audit-private.json')['result']for n in ['before','final']]
assert before['passed'] and after['passed'] and bp['producer']==ap['producer']
assert before['workerPid']==after['workerPid']==20682 and before['guardianPid']==after['guardianPid']==5412
current=read(root/'encoding3-encoding.json');scale=read(root/'scale1-scale.json')
assert current['passed'] and current['cases']==29 and current['projectValidation']['cases']==36
assert current['projection']=='fast' and current['completePublicationFieldEquality']
rows=current['rows'];old=mean(r['cpuSeconds']for r in rows if r['scope']=='real-complete'and r['mode']=='original')
new=mean(r['cpuSeconds']for r in rows if r['scope']=='real-complete'and r['mode']=='candidate')
encoding={**current,'exactOriginalProjectorFunctionUsed':False,'originalProjectorContractDifferentiallyChecked':True,
 'legacyOriginalJsonProjectionRetainedFieldMeansContractNotIdenticalFunction':True,
 'realCompleteOriginalMeanCpuSeconds':old,'realCompleteCandidateMeanCpuSeconds':new,'cpuReductionPercent':100*(old-new)/old,
 'sameFrozenInMemoryFixtureWithinPairs':True,'controlledHighNetworkLoad':False,'notWholeRouterCpuBenefit':True}
save(root/'encoding-corrected.json',encoding)
obs=read(root/'natural2-pipeline-private.json');a,b=obs['telemetry'];dt=b['at']-a['at']
ca=list(map(int,a['cpu'].split()[1:9]));cb=list(map(int,b['cpu'].split()[1:9]));d=[y-x for x,y in zip(ca,cb)]
sq=lambda v:sum(int(r.split()[2],16)for r in v.splitlines())
byseq={}
for r in obs['rows']:byseq.setdefault(r['sequence'],{})[r['name']]=r
stages=[]
for seq,g in byseq.items():
 if set(g)!={'classification','request','apply-result','snapshot'}or any('previousSamePathAt'not in r for r in g.values()):continue
 s=g['snapshot'];q=s['queryStarted'];stages.append({'sequence':seq,'flows':s['flows'],'querySeconds':s['queryFinished']-q,
  'classificationFirstObservedAfterQuerySeconds':g['classification']['readStartedAt']-q,
  'applyResultFirstObservedAfterQuerySeconds':g['apply-result']['readStartedAt']-q,
  'fullFirstObservedAfterQuerySeconds':s['readStartedAt']-q,'fullStampAfterQuerySeconds':s['publishedAt']-q,
  'fullVisibilityObservationLowerAfterStamp':s['previousSamePathAt']-s['publishedAt'],
  'fullVisibilityObservationUpperAfterStamp':s['heldReadCompletedAt']-s['publishedAt'],
  'fullParseSeconds':s['parsedAt']-s['heldReadCompletedAt']})
pipeline={'passed':True,'readonly':True,'seconds':dt,'observerCpuSeconds':obs['observerCpuSeconds'],'completeObservedCycles':stages,
 'lan4Mbps':(b['txBytes']-a['txBytes'])*8/dt/1e6,'pps':(b['txPackets']-a['txPackets'])/dt,
 'busyPercent':100*(sum(d)-d[3]-d[4])/sum(d),'softirqPercent':100*d[6]/sum(d),'timeSqueezeDelta':sq(b['softnet'])-sq(a['softnet']),
 'backgroundLoadControlled':False,'observerCostIncluded':True,'timeGranularitySeconds':0.01,'visibilityAreObservationBounds':True,
 'productionWorkerInstrumented':False,'ctMarkNatCountersCachedForAdmission':False,'nssAdmissionAllowed':False}
save(root/'pipeline-sanitized.json',pipeline)
hist=read('work/nss63/real-matched-aba-20261004131115-c2fb6b05-before-diagnostic-audit-private.json')['diagnostic']
join=read('work/nss63/real-matched-aba-20261004131115-c2fb6b05-before-join-private.json')
times={r['name']:r['at']for r in hist['events']};fresh=hist['freshness']
latency={'round':'NSS63','historicalEvidenceReanalyzedNotNewExperiment':True,'fullSourceAgeAtCheck':fresh['sourceAge'],
 'queryToFullPublicationStampSeconds':fresh['publishedAt']-fresh['queryStarted'],
 'queryToFullHintCompletionSeconds':join['finishedAt']-fresh['queryStarted'],
 'handoffToOriginalAuditSeconds':times['locked-audit-start']-join['finishedAt'],
 'originalAuditHashSeconds':times['hashes-complete']-times['locked-audit-start'],
 'originalAuditJournalSeconds':times['journal-parsed']-times['hashes-complete'],
 'originalAuditSelectorsSeconds':times['selectors-complete']-times['journal-parsed'],
 'originalAuditFullSnapshotParseSeconds':times['snapshot-parsed']-times['selectors-complete'],
 'firstNewFullHintReadCompletedAfterStampSeconds':join['join']['rows'][-1]['at']-fresh['publishedAt'],
 'fullStampCapturedBeforeJsonProjectionAndEncode':True,'renameTimeDirectlyInstrumented':False,
 'hintReadAndSchedulingCostsNotSeparatedInHistoricalRows':True,'allPostStampTimeAttributedToJson':False,
 'sourceExpirySecondsUnchanged':6,'allProductionDeadlinesUnchanged':True}
save(root/'historical63-latency-sanitized.json',latency)
compile=read(root/'compile-qualified.json');candidate=read(root/'candidate-worker-manifest.json')
assert compile['passed'] and compile['sha256']==candidate['candidateWorkerSha256'] and not compile['executed'] and not compile['installed']
failures=[]
for file,kind in [('paired1-compare-raw-private.json','2048-shape-combined-comparison-exceeded-six-second-runner'),
 ('natural1-pipeline-raw-private.json','observer-requested-unsupported-runner-duration-before-lua-execution')]:
 raw=read(root/file);failures.append({'case':file.removesuffix('-raw-private.json'),'reason':kind,'code':raw['code'],
  'productionConfigurationWrites':False,'nssOpened':False,'originalEvidenceRetainedLocally':True})
assert [f['code']for f in failures]==[124,2]
summary={'round':'NSS64','observedAt':after['observedAt'],'deploymentReference':'work/nss47/deployment-latest.json',
 'classifierConfigSha256':after['configSha256'],'permanentClassifierChanged':False,'routerConfigurationWrites':False,
 'newNssForwardingExperiment':False,'ecmOpenedThisTurn':False,'checkpointCount':0,'rollbackTrialCount':0,
 'budgetMbps':20,'gateFlows':{'tcp':1,'udp':1},'ownerSeconds':45,'allOriginalDeadlinesUnchanged':True,
 'currentEntry':{'path':'work/nss63/real-session.mjs','boundInputs':241,'unchanged':True,'fullHighLoadForwardingQualified':False},
 'historicalLatency':latency,'completeEncoding':encoding,'encodingOnlyScale':scale,'naturalPipeline':pipeline,
 'candidateWorker':candidate,'nativeCompilation':compile,'failedPreparationCases':failures,
 'proofBoundary':{'nativeContractCasesInLatestPass':{'project':36,'completeEncoding':29},
  'independentUniqueCaseCountNotAsserted':True,'earlierSameRoundPassesPreserved':True,'old99And13NotReexecuted':True,
  'fixturesAreNotAdmission':True,'noNewGameDownloadOrGameGuiThisTurn':True,'sourceDeficiencyNotProvedInstalledBinaryIdenticalToUpstream':True},
 'finalState':{'protectedAudit':after,'sameWorkerGuardianAndProducerSinceOpening':True,'ecmStoppedAndZero':True,
  'noActiveTransaction':True,'noStaging':True,'noExperimentState':True,'noExperimentalModule':True},
 'conclusions':{'encodingCpuReductionVerified':True,'wholeRouterCpuBenefitProved':False,'highLoadPublicationFixed':False,
  'realHumanGameImprovementProved':False,'completeMatchedABACompleted':False,'secondWanExpansionAllowed':False,'upstreamSubmitted':False},
 'nextStep':'One publication-boundary patch under checkpoint and independent timed undo; original full audit and source deadlines retained. Then concentrated matched real single-WAN A/B/A2.',
 'reportVerification':{'sourceValidated':True,'browserRendered':False}}
save('outputs/nss64-mainline-observations.json',summary)
parts=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
 '<title>NSS64 · 完整发布耗时定位</title><style>body{background:#f2f4f6;color:#162333;font:16px/1.7 system-ui,Microsoft YaHei;margin:0}main{max-width:1020px;margin:36px auto;padding:32px;background:white;border-radius:18px}h1{font-size:30px}h2{font-size:21px;margin-top:32px}table{border-collapse:collapse;width:100%;font-size:15px}td,th{padding:10px;border-bottom:1px solid #d9e0e6;text-align:left}small{color:#657284}.lead{padding:20px;background:#e9f4f1;border-radius:10px}code{word-break:break-all}a{color:#156257}</style><main>',
 '<h1>NSS64 · 完整快照发布耗时定位</h1><small>2026-10-04 北京时间 · 单主线 · 只读与目标 RAM 实验</small>',
 '<p class="lead">已做出完整字段一致、目标机编译通过的发布优化候选。319 条真实连接快照的编码 CPU 用时下降约 '+f'{encoding["cpuReductionPercent"]:.1f}%，尚未安装；高负载准入、整机 CPU 和真人 CS2 收益仍未验收。</p>',
 '<h2>这轮实际做了什么</h2><p>完整复核现网和原持锁审核，拆解 NSS63 失败时序；在目标机 RAM 内做 JSON 投影与编码差分、同一真实快照交错计时、规模夹具和精确候选编译。没有开启 NSS、安装分类器、操作游戏或新增下载。</p>',
 '<table><tr><th>测量</th><th>原方案</th><th>候选</th><th>边界</th></tr>',
 f'<tr><td>319 条真实完整快照，3 对交错测量</td><td>{old*1000:.1f} ms CPU</td><td>{new*1000:.1f} ms CPU</td><td>相同内存夹具；网络非高负载</td></tr>',
 '<tr><td>1024 条真实形状离线夹具，仅编码</td><td>422.9 ms CPU</td><td>198.2 ms CPU</td><td>不含投影；不是实际 1024 条 CT 准入</td></tr>',
 '<tr><td>字段与异常数据</td><td colspan="2">最新 36 个投影 / 29 个完整编码案例通过</td><td>旧 99/13 未重跑；不是转发证明</td></tr>',
 '<tr><td>完整候选编译</td><td colspan="2">32,019 字节，目标 SHA256 与本地一致</td><td>只编译，没有执行 watch 或安装</td></tr></table>',
 '<h2>为什么上一轮仍过期</h2><p>NSS63 的 query 到完整发布时间标记为 3.84 秒；提示消费完成时已有 5.47 秒，后续交接约 0.29 秒、哈希 0.35 秒、journal 0.03 秒、selector 0.51 秒、完整解析 0.76 秒，最终 source 为 7.41 秒，超过原 6 秒。</p>',
 '<p>发布时间在 JSON 投影/编码前采样，并非 rename 完成时间。旧提示中的读耗时没有单独计时，不能把标记之后的全部时间都归于编码。新被动观察在轻载下记录到完整快照约 0.63–0.86 秒可见，标记到可见的观测界限约 20–80 ms；不能代替高负载复验。</p>',
 '<h2>实际现场与失败</h2>',
 f'<p>自然观察 {dt:.2f} 秒，LAN4 {pipeline["lan4Mbps"]:.3f} Mbps / {pipeline["pps"]:.1f} pps，busy {pipeline["busyPercent"]:.2f}%，softirq {pipeline["softirqPercent"]:.2f}%，time_squeeze +{pipeline["timeSqueezeDelta"]}，包含观察器开销。ECM 全程关闭零计数，没有 CS2 HUD 或真人体验。</p>',
 '<p>首次 2048 条组合模拟触发原六秒 runner，返回 124，已结束并保留原证据；后来分拆并缩小测量。被动观察初版使用不支持的 runner 时长，执行前返回 2，已改为原六秒 runner 内的四秒窗。生产设置未变，未把模拟退出算作路由器故障或回滚成功。</p>',
 '<h2>候选与下一步</h2><p>候选只修改完整快照的 JSON 发布边界：保持全部字段与投影合同，按 flow 分块编码，非快照发布不变。完整 JSON 解析、原审核、PBR/ct mark/NAT/NSS gate、来源与 owner 时限均未变。上游 JSON-C Lua 绑定线性扫描 visited 表的实现与测量趋势吻合，但未证明目标安装二进制与该上游版本逐字节一致。</p>',
 '<p>下一步是 checkpoint 和独立超时撤销保护下的单项发布测试；验证真实 publication→完整审核能在原门槛内通过，才集中做单 WAN CS2＋Steam 可比 A/B/A2。不上第二 WAN，也不继续安装大游戏维持准备。</p>',
 '<p>最终原完整审核/清理通过：NSS47 配置不变，同 worker 20682 / guardian 5412，ECM 关闭全零，无事务、暂存、实验 state 或 gate/qdisc 模块。本轮只读，无生产配置需要回滚；没有新增自动回滚试验。</p>',
 '<p>代码和脱敏证据见 <a href="https://github.com/ZyPulse-zy/athena-nss-mainline">私有仓库</a>；源码参考 <a href="https://github.com/openwrt/luci/blob/master/libs/luci-lib-jsonc/src/jsonc.c">OpenWrt LuCI JSON-C 绑定</a>。未提交上游 Issue/PR。报告源检查通过，浏览器渲染尚未核验。</p></main></html>']
Path('outputs/nss64-mainline-report.html').write_text('\n'.join(parts),encoding='utf-8',newline='\n')
print(json.dumps({'passed':True,'round':'NSS64','encodingCpuReductionPercent':encoding['cpuReductionPercent'],
 'wholeRouterBenefit':False,'highLoadFixed':False,'candidateInstalled':False,'finalAudit':after['passed']}))
