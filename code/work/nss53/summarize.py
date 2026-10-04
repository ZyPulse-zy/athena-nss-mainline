"""Summarize exact readonly receipts. Raw connections and process identities stay local."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, html

root = Path('work/nss53')
def read(name):
    return json.loads((root / name).read_text(encoding='utf-8-sig'))
def save(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def counters(text):
    row = next(line for line in text.splitlines() if line.startswith('cpu '))
    values = list(map(int, row.split()[1:9]))
    return values
def softnet(text, column):
    return sum(int(line.split()[column], 16) for line in text.splitlines() if line.strip())
def summarize_window(label):
    safe = read(label + '-trace-sanitized.json')
    raw = read(label + '-trace-private.json')
    assert safe['ecmClosedThroughout'] and safe['noRouterWrites']
    rows = []
    for n, (s, r) in enumerate(zip(safe['attempts'], raw['attempts']), 1):
        assert s['passed'] == r['passed']
        # Cached sleep identity is allowed to age while waiting for a replacement.
        # Only newly observed children and the accepted waitFresh result use 200 ms.
        assert r['result']['birthClockChecked'] and r['result']['guardUntouched']
        assert 0 <= r['result']['maxBirthAgeSeconds'] <= 0.2
        assert all(c['birthAge'] <= 0.2 + 1e-8 for c in s['newChildren'])
        a, b = r['before'], r['after']
        delta = [y-x for x, y in zip(counters(a['cpu']), counters(b['cpu']))]
        total = sum(delta)
        assert total > 0 and all(x >= 0 for x in delta)
        rows.append({**s, 'attempt': n,
                     'acceptedMaxBirthAgeSeconds':r['result']['maxBirthAgeSeconds'],
                     'busyPercent': 100*(total-delta[3]-delta[4])/total,
                     'softirqPercent': 100*delta[6]/total,
                     'timeSqueezeDelta': softnet(b['softnet'], 2)-softnet(a['softnet'], 2),
                     'softnetDropDelta': softnet(b['softnet'], 1)-softnet(a['softnet'], 1),
                     'allNewChildBirthAgesWithinOriginal200ms': True,
                     'includesProfilerCost': True})
    return {**safe, 'attempts': rows}

loads = [summarize_window(x) for x in ['steam-load-a', 'steam-load-b']]
assert all(g['adapterSha256'] == sha(root/'classifier.lua') for g in loads)
assert all(g['phaseSha256'] == sha(root/'core-guard-phase.lua') for g in loads)
all_rows = [r for g in loads for r in g['attempts']]
assert len(all_rows) == 6 and all(r['passed'] for r in all_rows)
assert min(r['lan4Mbps'] for r in all_rows) > 290
initial = read('initial-prewrite-ownership-private.json')
final = read('final-post-load-ownership-private.json')
same = all(initial[k] == final[k] for k in ['pid', 'guardianPid', 'producer'])
assert same and final['querySequence'] > initial['querySequence']
diag, ready, loaded_ready, entry = (read(x) for x in [
    'diagnostic-qualified.json', 'ready-readonly-qualified.json',
    'ready-steam-load-qualified.json', 'entry-qualified.json'])
assert entry['baseBoundInputs']+entry['newBoundInputs'] == 159
assert diag['localChecks'] == 60 and diag['nativeDiagnosticHelperChecks'] == 14
assert ready['sameSourceCompleteDiagnosticObserved']
assert not loaded_ready['sameSourceCompleteDiagnosticObserved']
assert loaded_ready['completeDiagnosticUnavailable'].endswith('Complete diagnostic source differs')
application = json.loads(Path('work/nss49/real-session-readiness.json').read_text())
assert application['actualBulkCandidates'] == 24 and application['actualGameCandidates'] == 0
assert application['sameWanPairs'] == 0 and not application['nssPermissionGranted']
closure = read('final-post-load-cleanup-audit.json')
assert closure['passed']
out = {
    'round': 'NSS53', 'observedAt': closure['observedAt'],
    'deploymentReference': 'work/nss47/deployment-latest.json',
    'classifierConfigSha256': closure['configSha256'],
    'permanentClassifierChanged': False, 'routerConfigurationWrites': False,
    'ecmOpenedThisTurn': False, 'forwardingABACompletedThisTurn': False,
    'budgetMbps': 20, 'gateFlows': {'tcp':1,'udp':1}, 'ownerSeconds':45,
    'allOriginalDeadlinesUnchanged': True,
    'entry': {'path':'work/nss53/real-session.mjs', 'boundInputs':159,
              'baseBoundInputs':140, 'newBoundInputs':19,
              'preparationVerified':True, 'sourceChecksPassed':True,
              'controllerDecisionAndRecoveryBarriersUnchanged':True,
              'phaseByteIdenticalToNss52':True, 'sourcePolicyByteIdenticalToNss49':True,
              'sameSourceDiagnosticOnly':True, 'notInstalled':True,
              'actualNssABATestedThisEntry':False, 'completeHighLoadForwardingQualified':False,
              'historical99And13CasesReusedNotReexecuted':True},
    'diagnostics': {**diag, 'nativeActualReadyLight':ready,
                    'nativeActualReadyUnderDownload':loaded_ready,
                    'actualHighLoadRejectionUsesSyntheticAbsentKeys':True,
                    'projectionAbsenceDoesNotProveFullCtAbsence':True,
                    'onlyAfterTerminalRefusalReadsMatchingFullSnapshot':True,
                    'unknownDoesNotChangeDecisionOrRetry':True},
    'phaseDiscovery': {'readonlyWindows':loads,
                       'actualAttempts':6, 'actualPasses':6,
                       'minLan4Mbps':min(r['lan4Mbps'] for r in all_rows),
                       'maxLan4Mbps':max(r['lan4Mbps'] for r in all_rows),
                       'attemptsAtLeast300Mbps':sum(r['lan4Mbps'] >= 300 for r in all_rows),
                       'maxCallbackSeconds':max(r['maxScanSeconds'] for r in all_rows),
                       'maxObservationSeconds':max(r['maxObservationSeconds'] for r in all_rows),
                       'maxObservedBirthAgeSeconds':max(r['acceptedMaxBirthAgeSeconds'] for r in all_rows),
                       'original200msRequirementUnchanged':True,
                       'guardNotModifiedOrSignalled':True,
                       'completeConsumerCandidatesReadContextInspectExecuted':True,
                       'unusedAdapterFunctionsOmittedOnlyInReadonlyRamHarness':True,
                       'scope':'Six short actual-load discovery observations, not full high-load lifecycle or NSS forwarding qualification.',
                       'oldNss49ActualLoadPassed':0, 'oldNss49ActualLoadAttempts':3,
                       'oldNss51ActualLoadPassed':1, 'oldNss51ActualLoadAttempts':3,
                       'historicalWindowsNotSameOfferedLoad':True},
    'applicationReadiness':application,
    'steamLoad': {'title':'DOOM (2016)', 'availableSteamLibraryContent':True,
                  'selectedLibrary':'D:', 'availableGBBeforeRequest':218.25,
                  'displayedDiskRequirementGB':68.69, 'displayedDownloadGB':59.3,
                  'lastDisplayedDownloadedGBBeforePause':6.1,
                  'approximateGuiVolumeNotExactByteCounter':True,
                  'pausedConfirmed':True, 'networkBpsAfterPause':0,
                  'purchaseOrUninstallOccurred':False, 'newGameLaunched':False,
                  'completedDoomEternalNotRedownloaded':True,
                  'cs2GuiNotOperatedThisRound':True, 'hudNotCapturedThisRound':True},
    'preparationFailures': {'localTransportCeilingRejections':3,
                            'ceilingNotRaised':True,
                            'localFixtureAndOutputParsingCorrectedBeforeNativeReadyTest':True,
                            'entryDeltaTestSliceOffsetCorrectedBeforeQualification':True,
                            'firstDiagnosticProjectionInterpretationCorrectedBeforeBinding':True,
                            'originalFirstCandidateLocalEvidencePreserved':True,
                            'summaryCachedSleepAgeAndResultFieldCorrections':2,
                            'productionChangesDueToPreparationFailures':False},
    'finalState': {'sameCacheRetainedWorkerAndGuardianAndProducer':same,
                   'sequenceAdvanced':True,
                   'protectedAudit':read('final-post-load-audit.json'), 'closure':closure,
                   'checkpointsAndRouterRollbackTrialsThisRound':0,
                   'noRouterExperimentWritesRollbackNotNeeded':True},
    'conclusions': {'newActualLoadDiscoveryPassed':True,
                     'exactRefusalDiagnosticImplementedAndBound':True,
                     'newNssFastPathTrialExecuted':False,
                     'softwareVersusNssCpuBenefitProvedThisTurn':False,
                     'gameJitterLossMissCapturedThisTurn':False,
                     'realHumanExperienceProved':False,
                     'completeHighLoadLifecycleQualified':False,
                     'completeHighLoadLoopPassed':False,
                     'secondWanExpansionAllowed':False,
                     'sharedBudgetAllowed':False, 'upstreamSubmitted':False},
    'reportVerification': {'sourceValidated':True,'browserRendered':False},
    'next':'Use the bound NSS53 entry once a real single-WAN CS2 UDP + Steam TCP pair is visible; record aligned HUD before original checkpoint/independent rollback/software-NSS-software. Do not reinstall the resident classifier or replay old 99/13 preparation.'
}
save(Path('outputs/nss53-mainline-observations.json'), out)
save(root/'phase-load-sanitized.json', out['phaseDiscovery'])
save(root/'diagnostics-sanitized.json', out['diagnostics'])
save(root/'entry-binding-sanitized.json', out['entry'])
save(root/'steam-load-sanitized.json', out['steamLoad'])

rows = ''.join('<tr>'+''.join('<td>'+str(v)+'</td>' for v in [n, '通过',
                  f"{r['lan4Mbps']:.2f}", f"{r['lan4Pps']:.0f}",
                  f"{r['busyPercent']:.2f}", f"{r['softirqPercent']:.2f}",
                  r['timeSqueezeDelta'], r['softnetDropDelta'],
                  f"{1000*r['maxScanSeconds']:.0f}"])+'</tr>'
               for n,r in enumerate(all_rows,1))
page = f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>NSS53 高负载准入与分类拒绝诊断</title><style>
body{{font:16px/1.75 system-ui,"Microsoft YaHei",sans-serif;background:#f3f5f7;color:#182330;margin:0}}main{{max-width:1100px;margin:32px auto;padding:28px;background:white;border-radius:12px}}h1{{font-size:28px}}h2{{font-size:21px;margin-top:30px}}.notice{{padding:16px;background:#e9f3ed;border-left:4px solid #377654}}table{{border-collapse:collapse;width:100%;font-size:14px}}th,td{{padding:10px;border-bottom:1px solid #d7dde3;text-align:right}}th:first-child,td:first-child{{text-align:left}}code{{font-size:13px;overflow-wrap:anywhere}}.muted{{color:#526375}}@media(max-width:800px){{main{{margin:0;padding:18px}}.scroll{{overflow:auto}}}}</style>
<main><h1>NSS53：高负载准入与分类拒绝诊断</h1><p class="muted">2026-10-04 · 最终现网审核 18:38 北京时间 · 单一主线</p>
<p class="notice">真实 Steam 下载 294–366 Mbps，两组共六次进程发现全部通过；精确拒绝诊断已绑定新入口。常驻仍 NSS47，ECM 关闭全零。本轮没有 NSS B 段、真人 CS2 指标或 CPU 收益结论。</p>
<h2>本轮做了什么</h2><p>先完整核验现网和服务 epoch。NSS52 父进程字段解析候选原样纳入 NSS53 实验入口；waitFresh、200 ms 出生要求与全部准入、来源、owner 期限不变。没有重装常驻分类器或重做旧 99 / 13 项准备。新入口绑定 159 项输入，使用原单 WAN、20 Mbps、一 TCP＋一 UDP、独立 45 秒恢复流程；本轮只读，未运行该写入流程。</p>
<p>按用户授权，从已有 Steam 库选择未安装的 DOOM（2016），D 盘剩余 218.25 GB。真实下载页面曾显示 323.3 Mbps，暂停前约 6.1 / 59.3 GB。短测后暂停并核验 0 bps，未购买、卸载、启动新游戏或重下已完成的 DOOM Eternal。本轮未操作 CS2 界面。</p>
<h2>真实高负载只读结果</h2><div class="scroll"><table><thead><tr><th>尝试</th><th>发现</th><th>LAN4 Mbps</th><th>pps</th><th>busy %</th><th>softirq %</th><th>squeeze Δ</th><th>drop Δ</th><th>最长回调 ms</th></tr></thead><tbody>{rows}</tbody></table></div>
<p>六次均执行实际 candidates → readContext → Consumer.inspect 读取，再等待固定 guard 的真实新子进程；guard 没有被修改、signal 或暂停。四次平均负载至少 300 Mbps，另外两次 294–297 Mbps。实际 waitFresh 接纳结果中的最大出生年龄 180 ms，最长 consumer 读取约 180 ms、含读取的回调约 200 ms；uptime 为约 10 ms 粒度，余量仍有限。表中 CPU 包含 profiler 开销，各窗不是相同 offered load，只说明软件路径现场情况，不是 CPU A/B。</p>
<p>历史旧 helper 实际下载 0/3、NSS51 1/3，当前 NSS52 同字节候选在这六个窗口 6/6；这支持父进程解析改动能在短时高负载下完成发现。不同轮次负载不完全相同，不能计算整机 CPU 收益，也不能扩大成完整高负载恢复、长期稳定或 NSS 转发资格。</p>
<h2>拒绝帧诊断：投影缺失不能直接判流退出</h2><p>源码确认提前发布的 classification.json 只包含 bulk 和已准入 RT 的投影，不包含全部分类输入。缺失可能来自预算拒绝、改类或流退出。新的诊断保存发生拒绝的同一准入帧；在最终拒绝后至多读一次完整 snapshot.json，只有 producer 和全部 query 来源字段一致且原 Consumer.inspect 通过，才补充完整分类事实。来源不同明确记录未知，不改放行、重试或恢复决定，不重新查询 conntrack。</p>
<p>本地 60 断言通过（原 21 项重放＋新增 39 断言），目标原生 JSON helper 14 项通过。轻载实际 ready 使用合成不存在键，在真实发布的同源完整帧确认不存在；真实下载期间同一 ready 路径明确拒绝，完整帧与准入帧来源不同，按设计保留未知。两次均是默认拒绝诊断，不是实际连接 NSS 准入或加速证明。IO / 时钟 / ACK 被替代的完整本地适配器检查与原生只读 ready 分别记录，未混算。</p>
<h2>现网与未完成项</h2><p>真实应用核查识别 24 条 Steam bulk、0 条对局 UDP、0 个同 WAN 配对，因此没有 checkpoint / 队列暂存 / ECM 放行。末次原完整持锁保护审核与清理通过；worker、guardian、producer 与开场一致，来源序列继续前进。没有事务、暂存、实验 state 或 gate/qdisc 模块，认证/PBR/sing-box/Tailscale 等保护配置不变。只读工具无需执行路由器回滚；Steam 下载暂停已核验。</p>
<p>此前 NSS49 单 WAN ECM0→2→0、正确 bulk/RT leaf、mark/NAT/WAN affinity 和精确恢复的功能证据保持。本轮未重新取得 leaf / CAKE tin 或真实游戏 jitter/loss/Miss，不填零、不伪造体验。目前仍不能永久开放 NSS，也不扩第二 WAN、共享预算、Wi-Fi、autorate。</p>
<h2>下一步</h2><p>只需在自然 CS2 对局与暂停的 DOOM 下载恢复后出现真实同 WAN 配对，使用已绑定的 <code>work/nss53/real-session.mjs</code>，先同步记录 HUD，再按原 checkpoint、独立回滚和同负载 software → NSS → software 跑一轮。检查实际 bulk/RT tag、ECM/leaf、出口/ct mark/NAT/affinity、softirq/time_squeeze、吞吐与客户端指标。无需继续安装分类器或重复准备；没有真实对局时不凭合成 UDP 验收。发现及投影诊断问题属于本地控制器 backlog，没有向上游提交。</p>
<p class="muted">三个本地传输长度拒绝、夹具/输出解析与入口差分切片修正均留存，未提高传输上限或触发生产变更；第一诊断候选已另行保存。可读源码与脱敏证据按明确白名单入私有仓库；凭据、完整 CT/socket、原始进程/配置和截图留本地。报告源与链接核验；未声称浏览器视觉验收。</p>
<p><a href="nss53-mainline-observations.json">结构化观测</a></p></main></html>'''
assert page.count('<tr>') == 7 and '未知' in page and '没有 NSS B 段' in page
Path('outputs/nss53-mainline-report.html').write_text(page, encoding='utf-8', newline='\n')
print(json.dumps({'round':'NSS53','actualLoadAttempts':6,'actualLoadPasses':6,
                  'sourceValidated':True,'browserRendered':False,
                  'ecmOpened':False,'cpuBenefitClaimed':False,
                  'sameWorkerGuardianProducer':same}, ensure_ascii=False))
