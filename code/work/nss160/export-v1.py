"""Freeze the finite v1 outcome; export only source and redacted observations."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import json, hashlib, subprocess, copy, html

w = Path(__file__).resolve().parents[2]
r = w / 'work/nss160'
repo = w / 'athena-nss-mainline'
base = 'bcf1ee62991ef0aa4f6133d64fc582b8f4054ed9'
case = r / 'real-matched-aba-20261006143500-7abfb3f5'
load = r / 'load-20261006141241-50d09fc918743a3f'
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha = lambda b: hashlib.sha256(b).hexdigest()
dump = lambda x: json.dumps(x, ensure_ascii=False, indent=2) + '\n'
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo, text=True).strip() == base
assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=repo)
manifest = read(repo / 'source-manifest.json')
prefix = copy.deepcopy(manifest['sources'])
assert len(prefix) == 2753 and manifest['lastAppendExport'] == 'NSS159'
old_runtime = subprocess.check_output(['git', 'show', base + ':evidence/current-runtime.json'], cwd=repo)
assert json.loads(old_runtime)['round'] == 'NSS159'
metric = read(r / 'final-functional-metrics.json')
assert metric['passed'] and metric['realCs2DeathmatchAndExistingSteamUpdate']
assert metric['humanSubjectiveAcceptance'] is None and not metric['newCpuCausalBenefitClaimed']
assert [p['ecmAcceleratedCount'] for p in metric['phases']] == [0, 2, 0]
assert all(20 <= p['seconds'] < 21.5 and p['sampleCount'] == 41 for p in metric['phases'])
assert metric['nativeRenewals'] == 6 and metric['actualBindingsAndFrozenCopiesVerified'] == 2137
assert metric['checkpointDownloadedShaGzipVerified'] and metric['independentPpidOneRollbackVerifiedBeforeWrite']
assert metric['payloadBytes'] == 73422 and metric['guardianExecBytes'] == 8947
assert all(metric['allOriginalRestoreChecks'].values())
assert all(p['natCorrect'] and p['wanAffinity'] == 5 and p['ctMark'] == 0x50000 for p in metric['flowProof'].values())
result = read(case / 'result.json')
assert result['passed'] and result['matchedForwardingABACompleted'] and not result['gameQualityConclusion']
assert read(case / 'baseline-audit.json')['configurationMatches']
after = read(r / (case.name + '-after-audit.json'))
assert after['passed'] and after['ecmClosedAndZero'] and after['protectedConfigurationUnchanged']
assert after['exactOwnedNativeAudit'] and after['queryAge'] < 6
actual_inputs = read(case / 'source-manifest.json')
assert len(actual_inputs) == 2137
for source, digest in actual_inputs.items():
    assert sha((w / source).read_bytes()) == sha((case / 'frozen' / source).read_bytes()) == digest
health = read(r / 'v2-final-health.json')
assert health['passed'] and health['originalFullLockedNativeAudit'] and health['unrelatedConfigurationMatches']
assert health['queryAge'] < 6 and health['allFiveWanHealthy']
assert all(health[k] for k in ['ecmStoppedAndZero', 'noActiveTransaction', 'noStaging', 'noExperimentState', 'noExperimentalModule'])
guard_ref = read(r / 'steam-guard-current-private.json')
guard_dir = Path(guard_ref['caseDir'])
guard = read(guard_dir / 'result.json')
client = read(guard_dir / 'client-restored.json')
assert guard['passed'] and guard['cancelledAfterClientRestore'] and not guard['timedExitExecuted']
assert client['passed'] and client['downloadCompleted'] and client['networkBps'] == client['activeDownloads'] == 0
assert client['originalLimitDisabledRestored'] and client['originalLimitEmptyRestored']
assert client['existingQueuedUpdateOnly'] and client['noPurchase']
now = datetime.now(timezone.utc)
ui = {'passed': True, 'observedAt': now.isoformat(), 'source': 'Direct computer-use screenshots',
      'cs2DisconnectedFromTestServer': True, 'cs2MainMenuVisuallyVerified': True,
      'steamExistingUpdateCompleted': True, 'steamNoActiveDownload': True,
      'originalSteamLimitDisabledAndEmptyRestored': True, 'ownedClientGuardCancelledAfterRestore': True,
      'earlierGuardNaturalTimeoutPreserved': True, 'humanFeedback': '目前无法接手，仅记录 HUD',
      'humanSubjectiveAcceptance': None, 'noFurtherDesktopTest': True}
load_result = read(load / 'result-private.json')
fw = read(load / 'firewall-after-private.json')
fw_after = json.loads(fw['stdout'])
closed = read(load / 'server-closed-private.json')
assert fw['code'] == closed['code'] == 0 and fw_after['baselineRestored'] and fw_after['ownedRulesRemaining'] == 0
assert 'MainPID=0' in closed['stdout'] and 'ActiveState=inactive' in closed['stdout']
assert load_result['udpSent'] == 2527 and load_result['udpReceived'] == 2442 and not load_result['errors']
pilot_names = ['pilot-aba-20261006140521-a9adceb59d1dd66d',
               'pilot-aba-20261006140954-b6f8f64cd3aca7cf',
               'pilot-aba-20261006141231-09ec61f225f41d5a']
for name in pilot_names:
    assert not read(r / name / 'automatic-result.json')['passed']
assert not read(r / 'real-matched-aba-20261006142049-db6caac2/result.json')['passed']
gap = {'passed': True, 'decision': 'KNOWN_LIMITATION_NO_ESTABLISHED_V1_BLOCKER',
       'originalNss159Unreturned': 36, 'originalSingleContinuousBurstRetained': True,
       'fixed': False, 'locationProven': False, 'nssCauseProven': False,
       'newNssEchoReproductionPerformed': False, 'stableNssReproductionEstablished': False,
       'oneBoundedInvestigationClosed': True, 'furtherGapExperimentsStopped': True,
       'boundedAttempts': [
           {'result': 'source6.31 exceeded unchanged6 limit before checkpoint/endpoint/NSS'},
           {'result': 'owned endpoint launch SSH timeout; no router checkpoint/stage/NSS'},
           {'result': 'natural UDP WAN4, no same-WAN TCP among eight own candidates; software only'}],
       'softwareOnlyObservation': {'seconds': load_result['seconds'], 'udpSent': 2527, 'udpReceived': 2442,
           'unreturned': 85, 'endpointAndFirewallRestored': True,
           'closingPendingRequestsNotSteadyStateLoss': True,
           'doesNotLocateOrExplainOriginalNssBurst': True},
       'finalRealGameObservation': 'No disconnect/controller failure or obvious additional HUD deterioration at sparse NSS observation; no human experience confirmation',
       'rtQueueDropZeroIsNotEndToEndDeliveryProof': True,
       'noNewTapFirmwareInstrumentationOrGateChanges': True,
       'preconditionsForReopening': ['repeatable NSS-caused interruption', 'actual game deterioration linked to NSS', 'controller/restore/data corruption']}
cpu = read(repo / 'evidence/nss128-comparison.json')
assert cpu['comparabilityAccepted'] and all(cpu['checks'].values()) and 48 < cpu['softirqRelativeReductionPercent'] < 49
cpu_reuse = {'passed': True, 'historicalEvidenceReused': 'evidence/nss128-comparison.json',
            'historicalEvidenceSha256': sha((repo / 'evidence/nss128-comparison.json').read_bytes()),
            'softirqRelativeReductionPercent': cpu['softirqRelativeReductionPercent'],
            'scope': cpu['metricScope'], 'newCpuExperimentRequired': False,
            'currentFinalTrialCpuCausalConclusion': None,
            'not300MbpsLongTermOrAllFlowEvidence': True}
failures = [
    {'case': 'initial-parser', 'originalFailurePreserved': True, 'impact': 'offline packet parser preparation only'},
    {'case': 'initial-qualification', 'originalFailurePreserved': True, 'impact': 'offline qualification/import mismatch; no connection'},
    {'case': 'bounded-source6.31', 'originalFailurePreserved': True, 'impact': 'prewrite refusal; no NSS'},
    {'case': 'bounded-endpoint-launch-timeout', 'originalFailurePreserved': True, 'impact': 'endpoint units absent after bounded cleanup; no NSS'},
    {'case': 'bounded-natural-WAN-mismatch', 'originalFailurePreserved': True, 'impact': 'software load only; no NSS'},
    {'case': 'real-entry-v1-command-size', 'originalFailurePreserved': True, 'impact': 'refused before connection; no size limit widened'},
    {'case': 'real-entry-v2-unfiltered-PC-sockets', 'originalFailurePreserved': True, 'impact': 'native exact tuple/port subset filtering; original ownership limit unchanged'},
    {'case': 'qualify-v5-import', 'originalFailurePreserved': True, 'impact': 'missing not-yet-generated binding-v3; fixed qualify-v6 only'},
    {'case': 'real-entry-v3-NSS49-literal', 'originalFailurePreserved': True, 'impact': 'checkpoint/NSS stage not reached; original literal restored in v4'},
    {'case': 'real-entry-v3-after-audit-stale', 'originalFailurePreserved': True, 'impact': 'read-only audit refused; later original full audit passed'},
    {'case': 'earlier-Steam-guard-expiry', 'originalFailurePreserved': True, 'impact': 'independent exact timeout closed old Steam/CS2; UI restoration not claimed then; final separate UI/guard restored'},
    {'case': 'optional-evidence-file-lookup', 'originalFailurePreserved': True, 'impact': 'read-only filename guesses failed; actual names discovered; no submit chain started'}]
for file in ['initial-parser-failure.json', 'initial-qualification-failure.json', 'qualification-v5-failure.json']:
    assert (r / file).exists()
qualifications = [read(r / ('entry-qualified' + suffix + '.json')) for suffix in ['', '-v2', '-v3', '-v4']]
for q in qualifications:
    assert q['passed'] and not q['productionExecution']
    for source, digest in q['sourceManifest'].items():
        assert sha((w / source).read_bytes()) == digest
limitations = [
    '仅单健康WAN、一条TCP BULK和一条UDP RT；选中UP60/DOWN30、未选中fallback950。',
    '最后CS2只由助手进入官方死斗并记录稀疏HUD，用户无法接手；真人体感未验，A2 HUD缺失。',
    'HUD软件A与NSS B已有约2%下行Loss；此前软件路径有15.2%尖峰，不能宣称零丢包或绝对无异常。',
    'NSS159的36个连续echo缺口未定位、未修复；目前未建立NSS因果或稳定复现，按非已证实v1 blocker保留。',
    '最终Steam沿用现有更新，临时100Mbps限额已恢复；不代表全电脑/300Mbps/长期加速。',
    '本版为有界功能冻结，实验后ECM关闭；常驻分类器NSS68和软件CAKE fallback保留，未永久部署NSS控制器。',
    '不承诺机械复刻CAKE host fairness、DiffServ、autorate；当前实现明确BULK/RT双向NSS FQ-CoDel leaf。',
    '历史BULK→BE精确撤销与新epoch重学证据保留；其它改类默认拒绝，未升级为全场景长期恢复保证。']
main = {'round': 'NSS160', 'version': 'Athena NSS v1', 'passed': True,
        'status': 'V1_TECHNICAL_MAINLINE_FROZEN_REAL_CS2_STEAM_ABA_PASSED_HUMAN_EXPERIENCE_DEFERRED',
        'observedAt': now.isoformat(), 'coreFunctionalAcceptanceComplete': True,
        'v1FunctionalAcceptanceComplete': False, 'humanSubjectiveAcceptance': None,
        'humanAcceptedInThisTrial': False, 'userSelectedHudOnly': True,
        'noFurtherAutomaticExperiments': True, 'newProductionExperimentRequired': False,
        'qualifiedFrozenEntry': 'work/nss160/real-session-v4.mjs', 'boundInputs': 2137,
        'kernelGateAndQosUnchanged': True, 'sourceNativeOwnerClientSeconds': [6, 27, 100, 180],
        'execRawBundleRecordBytes': [9000, 65536, 73728, 1048576],
        'permanentNssEnabled': False, 'permanentNssControllerInstalled': False,
        'repositoryVisibility': 'public', 'functionalMetrics': metric, 'gapDecision': gap,
        'historicalCpuEvidence': cpu_reuse, 'finalAudit': health, 'originalRecoveryAudit': after,
        'clientRestore': ui, 'knownLimits': limitations, 'failuresPreserved': failures,
        'remainingAcceptanceItem': '用户正常玩CS2时的体感确认；当前仅HUD，不继续自动实验或再次要求挂机。',
        'nonBlockersMovedTo': 'docs/BACKLOG.md', 'original159RuntimeSha256': sha(old_runtime)}
runtime = {'round': 'NSS160', 'version': 'v1 frozen', 'observedAt': health['observedAt'],
           'classifierDeployment': 'NSS68', 'workerPid': health['workerPid'], 'guardianPid': health['guardianPid'],
           'classifierConfigSha256': health['configSha256'], 'boundInputs': 2137,
           'coreFunctionalAcceptanceComplete': True, 'v1FunctionalAcceptanceComplete': False,
           'humanSubjectiveAcceptance': None, 'realCs2SteamFunctionalABACompleted': True,
           'noFurtherAutomaticExperiments': True, 'nssPermanentlyEnabled': False,
           'permanentNssControllerInstalled': False, 'repositoryVisibility': 'public',
           'gapDecision': gap['decision'], 'audit': health, 'clientRestore': ui,
           'historical159RuntimePreservedSha256': sha(old_runtime)}
sources = {}
for f in r.iterdir():
    if f.is_file() and f.suffix in ['.mjs', '.py', '.lua', '.ps1'] and not any(t in f.name.lower() for t in ['private', 'credential', 'connect-router']):
        sources[f.relative_to(w).as_posix()] = sha(f.read_bytes())
assert not {x['workspaceSource'] for x in prefix}.intersection(sources)
proof = {'passed': True, 'historicPrefixSources': len(prefix),
         'historicPrefixCanonicalSha256': sha(json.dumps(prefix, sort_keys=True, separators=(',', ':')).encode()),
         'historicManifestPrefixUnchanged': True, 'old159RuntimeExactGitBytes': True,
         'sourceHashes': sources, 'sources': len(sources), 'actualInputsAndFrozenCopiesVerified': 2137,
         'privateDataExcluded': True, 'frozenFailureSourcesUnchanged': True}
evidence = {'mainline': main, 'functional-metrics': metric, 'gap-decision': gap, 'historical-cpu-reuse': cpu_reuse,
            'source-proof': proof, 'qualification': qualifications, 'failures': failures,
            'final-audit': health, 'original-recovery-audit': after, 'client-restore': ui}
planned = {repo / ('evidence/nss160-' + n + '.json'): dump(v).encode() for n, v in evidence.items()}
planned[repo / 'evidence/nss159-runtime.json'] = old_runtime
for source, digest in sorted(sources.items()):
    content = (w / source).read_bytes()
    assert sha(content) == digest
    planned[repo / 'code' / source] = content
    manifest['sources'].append({'path': 'code/' + source, 'workspaceSource': source, 'sha256': digest,
                               'bytes': len(content), 'role': 'finite-v1-freeze-real-game-observation-and-preserved-failures'})
for dest in planned:
    assert not dest.exists(), str(dest)
with (r / 'final-ui-restore.json').open('x', encoding='utf-8') as f:
    f.write(dump(ui))
for dest, content in planned.items():
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(content)
manifest.update(lastAppendExport='NSS160_V1_FROZEN', generatedAt=now.isoformat())
assert manifest['sources'][:2753] == prefix
(repo / 'source-manifest.json').write_text(dump(manifest), encoding='utf-8')
(repo / 'evidence/current-runtime.json').write_text(dump(runtime), encoding='utf-8')
time = now.astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
body = f'''# Athena NSS v1 技术闭环完成并冻结；真人体感未验

更新：{time}，北京时间。NSS159为起点，本次为最终有界收尾，停止新增自动实验。

**自动分类→单WAN NSS bulk/RT→真实CS2官方死斗＋现有Steam更新，完整20秒software→NSS→software已通过，ECM0→2→0。技术主线冻结；用户明确选择“目前无法接手，仅记录HUD”，因此不写`v1 functional acceptance complete`，严格的真人体感项保留未验。** 不再为这一项自动启动游戏、制造新负载或重复实验。

WAN5一条真实Steam TCP BULK与一条CS2 UDP RT，程序socket归属、同query实际分类、双向四tag、完整ct mark `0x50000`、NAT和WAN affinity正确，六次续租通过。四个NSS FQ-CoDel leaf均有真实包，RT上下行drop0；bulk下行drop15。RT队列零drop不能证明端到端零丢包。UP60（bulk59/RT1）/DOWN30（bulk29/RT1），其余fallback950；没有把整台电脑或五WAN一起加速。

| 最后真实负载窗口 | software A | NSS B | software A2 |
|---|---:|---:|---:|
| 秒数 / 帧数 | 20.05 / 41 | 20.05 / 41 | 20.03 / 41 |
| ECM accelerated_count | 0 | 2 | 0 |
| LAN4下行接口Mbps | 107.25 | 106.57 | 104.57 |
| softirq % | 29.33 | 26.96 | 25.90 |
| CPU busy % | 49.26 | 47.00 | 48.76 |
| time_squeeze / softnet drop | 25 / 0 | 19 / 0 | 12 / 0 |

本轮不宣称新CPU因果收益：B softirq并未低于A2。复用NSS128原七项可比条件已通过的约30Mbps上传证据：softirq10.034→5.246→10.393%，相对软件均值下降48.64%。不重复CPU门槛；该结论范围是历史单WAN受控短窗，不外推300Mbps或长期运行。

| 实际CS2 HUD稀疏截图 | ping ms | 下行jitter ms | 下行Loss % | 下行Miss % |
|---|---:|---:|---:|---:|
| software A | 11 | 1 | 2.2 | 2.7 |
| NSS B | 10 | 0 | 2.5 | 1.6 |
| 恢复后 | 11 | 0 | 0 | 0 |

截图在对应窗口内，时钟仅约2秒精度；A2 HUD缺失，无连续HUD遥测。软件路径更早出现15.2%下行Loss尖峰。NSS截图未显示明显额外恶化，未观察到断线或控制器异常；不能写零丢包、实际玩家无卡顿或完整真人验收通过。

**NSS159连续36个UDP echo缺口：known limitation，当前无已证实v1 blocker，未修复、未定位。** 唯一有界定位中的source6.31写前拒绝、端点SSH启动超时与自然WAN不匹配全部保留；最后自有夹具仅software运行53.94秒，UDP2442/2527，尾部待返回不能当稳定丢包。这不是新的NSS复现实验，不能解释原WAN3的连续缺口。没有证据建立NSS/firmware/gate/lease系统性中断或控制器损坏；按照用户收敛标准停止gap支线，不再增加tap或故障模型。若以后出现稳定复现或真实游戏受损的明确证据，才重开blocker。

内核gate、NSS158 native/QoS与实际二进制不变；只修复最终入口的有界程序socket读取及被误替换的历史NSS49字面路径，2137实际输入及冻结副本逐项SHA核验。checkpoint下载SHA/gzip、控制连接外PPID1独立回滚已在写前核验，payload73422/guardian8947满足原73728/9000上限，6/27/100/180秒与1MiB记录不放宽。原失败及早期客户端超时均保留。

实验及最终原完整审核通过，source1.67秒，常驻NSS68/31767/17139、config581b5d46…c791d7不变，五路健康；ECM关闭全零，无事务/stage/state/实验模块。两物理原mq＋四fq_codel及保护配置恢复；自有端点/防火墙恢复。现有Forza更新完成、Steam0bps，临时100Mbps设置已恢复为原不限速/空值，精确客户端守护在恢复后撤销；CS2已断开测试服并目视回主菜单。未购买、重装或新增游戏下载，未永久启用NSS控制器。

v1已知限制和v1.1/v2事项集中到BACKLOG。现有CAKE仅未加速流fallback/对照，不作为继续优化方向。**从现在起保持冻结，不开启NSS161+或重复准备；剩余真人体感仅等用户正常使用时确认，本次不要求继续挂机。**

证据：LINKS
'''
labels = [('主线', 'mainline'), ('真实指标', 'functional-metrics'), ('缺口判断', 'gap-decision'),
          ('历史CPU', 'historical-cpu-reuse'), ('恢复', 'final-audit'), ('客户端', 'client-restore'), ('失败', 'failures')]
for file in ['AGENTS.md', 'docs/STATE.md', 'docs/PLAN.md', 'docs/EXPERIMENT_LOG.md']:
    dest = repo / file
    pre = '../' if file.startswith('docs/') else ''
    links = '、'.join(f'[{label}]({pre}evidence/nss160-{name}.json)' for label, name in labels)
    dest.write_text(body.replace('LINKS', links) + '\n## NSS159及更早历史（不作为当前待办）\n\n' + dest.read_text(encoding='utf-8'), encoding='utf-8')
backlog = '''# v1 冻结后的已知限制与 v1.1 / v2

当前技术闭环完成，停止自动实验；真人体感由用户选择仅HUD而未验，不能伪写完整真人通过。

- 已知限制：NSS159连续36个echo缺口无位置/因果/稳定复现证明，未修复；只有明确v1使用损害才重新升级blocker。
- 稀疏CS2 HUD、缺失A2 HUD、软件原有Loss尖峰与没有真人主观反馈，限制体验结论。
- 仅单WAN一TCP BULK＋一UDP RT，有界UP60/DOWN30；实验后NSS关闭，常驻分类器及CAKE fallback保留。
- v1.1：正常用户体验确认；按真实需求考虑长期启用与支持范围。无需自动重放旧CPU/checkpoint/生命周期证明。
- v1.1/v2：第二WAN、五WAN共享预算、Wi-Fi、autorate、完整CAKE语义、ECN、多流公平、300Mbps长压、重启恢复、极端crash/故障注入/race、更多根因调查。均不是当前v1 blocker。
- bridge B-shaper、tc JSON、HTB dump、普通IFB/private MacVLAN直接挂NSS qdisc等兼容发现保留Issue/PR backlog，未提交上游。
- 历史BULK→BE精确撤销/新epoch重学已由NSS138/139/158证明；下方旧“待验”说法属于历史，不能据此继续实验。

## 旧支线记录（历史，不自动重开）

'''
dest = repo / 'docs/BACKLOG.md'
dest.write_text(backlog + dest.read_text(encoding='utf-8'), encoding='utf-8')
dest = repo / 'README.md'
dest.write_text('# Athena NSS v1 — frozen\n\n自动分类→单WAN双向NSS bulk/RT→真实CS2＋现有Steam更新的完整ABA已通过并恢复。技术闭环冻结；用户本次只允许记录HUD，真人体感未验。NSS159 echo缺口保留known limitation，不继续自动实验。详情见[STATE](docs/STATE.md)、[v1报告](reports/nss160-v1-report.html)、[限制及后续](docs/BACKLOG.md)。当前ECM关闭，未永久部署NSS控制器。\n\n## NSS159及更早历史\n\n' + dest.read_text(encoding='utf-8'), encoding='utf-8')
page = '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>Athena NSS v1 frozen</title><style>body{font:16px/1.8 system-ui;max-width:1000px;margin:36px auto;padding:24px;color:#182638;background:#f3f5f7}pre{white-space:pre-wrap;background:white;padding:25px}a{color:#1761a2}</style><body><h1>Athena NSS v1 · 技术闭环冻结</h1><pre>' + html.escape(body.replace('LINKS', '源码与脱敏证据见 GitHub STATE / BACKLOG')) + '</pre><a href="https://github.com/ZyPulse-zy/athena-nss-mainline/blob/main/docs/STATE.md">GitHub STATE</a></body></html>'
for dest in [w / 'outputs/nss160-v1-report.html', repo / 'reports/nss160-v1-report.html']:
    assert not dest.exists()
    dest.write_text(page, encoding='utf-8')
receipt = {'passed': True, 'sourcesAdded': len(sources), 'sourcesTotal': len(manifest['sources']),
           'actualBindings': 2137, 'old159RuntimeExactGitBytes': True, 'technicalMainlineFrozen': True,
           'humanSubjectiveAcceptance': None, 'fullV1HumanAcceptanceNotClaimed': True,
           'gapDecision': gap['decision'], 'noFurtherAutomaticExperiments': True}
with (r / 'export-v1-receipt.json').open('x', encoding='utf-8') as f:
    f.write(dump(receipt))
print(json.dumps(receipt))
