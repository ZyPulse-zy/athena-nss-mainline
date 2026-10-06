"""Publish an explicit source allowlist and redacted controlled-test evidence.

No network, desktop, router mutation, or raw connection/configuration export.
All earlier source and evidence bytes are retained. Operational binding is
independent of this publication script.
"""
from pathlib import Path
import copy
import hashlib
import json
from datetime import datetime, timezone

w = Path(__file__).resolve().parents[2]
repo = w / 'athena-nss-mainline'
out = w / 'work/nss148'
case = w / 'work/nss147/controlled-matched-aba-20261006030739-426623cb'


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def sha(b):
    return hashlib.sha256(b).hexdigest()


def dump(p, v):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(v, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def new_evidence(name, v):
    p = repo / ('evidence/nss148-' + name + '.json')
    assert not p.exists(), 'Do not overwrite new or frozen evidence'
    dump(p, v)


manifest_path = repo / 'source-manifest.json'
manifest = read(manifest_path)
assert manifest['lastAppendExport'] == 'NSS142'
prefix = copy.deepcopy(manifest['sources'])
assert len(prefix) == 1892
old_runtime = (repo / 'evidence/current-runtime.json').read_bytes()
assert read(repo / 'evidence/current-runtime.json')['round'] == 'NSS142'
assert not (repo / 'evidence/nss142-runtime.json').exists()

historical_hashes = {}
for base in ['code', 'evidence']:
    for p in (repo / base).rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts:
            historical_hashes[p.relative_to(repo).as_posix()] = sha(p.read_bytes())
dump(out / 'historic-files-before-export.json', historical_hashes)

quals = {n: read(w / f'work/nss{n}/entry-qualified.json') for n in range(143, 149)}
assert all(q['passed'] for q in quals.values())
assert quals[147]['actualFacadeIncluded']
assert quals[148]['sameTestedNss147Factory']
result = read(case / 'result.json')
functional = read(case / 'functional-runtime-proof.json')
raw = read(case / 'last-record-private.json')
metrics = read(case / 'actual-download-metrics.json')
assert result['passed'] and functional['passed'] and raw['abaCompleted']
assert len(raw['samples']) == 123 and len(raw['renewals']) == 7
assert not metrics['comparabilityAccepted']
assert metrics['softirqRelativeReductionPercent'] is None
assert metrics['comparisonChecks']['sameFlowFunctionalABA']

# Actual operational source binding must match the actual frozen experiment,
# not an old passing qualification or a publication manifest.
actual_inputs = read(case / 'source-manifest-preaudit.json')
assert len(actual_inputs) == 1518
for source, digest in actual_inputs.items():
    assert sha((w / source).read_bytes()) == digest
    assert sha((case / 'frozen' / source).read_bytes()) == digest

health = read(w / 'work/nss147/v2-final-health.json')
physical = read(w / 'work/nss147/physical-final.json')
endpoints = read(w / 'work/nss147/endpoint-client-closure.json')
receivers = read(w / 'work/nss147/download-receiver-closure.json')
ready = read(out / 'real-session-readiness.json')
reader = read(out / 'real-reader-qualified.json')
assert health['passed'] and physical['passed'] and endpoints['passed'] and receivers['passed']
assert ready['mode'] == 'inspect' and not ready['routerWrites']
assert not ready['trafficGenerated'] and not ready['openFrontend']
assert not ready['nssPermissionGranted']
assert endpoints['ownedUnitsInactiveMainPidZero'] == 11

# Curated operational sources only. Never enumerate raw inputs for export.
source_hashes = {}
sources_by_round = {}
for n, q in quals.items():
    sources_by_round[str(n)] = len(q['sourceManifest'])
    for source, digest in q['sourceManifest'].items():
        assert source.startswith(f'work/nss{n}/')
        assert sha((w / source).read_bytes()) == digest
        source_hashes[source] = digest
extra_sources = [
    'work/nss147/analyze-download.py',
    'work/nss147/analyze-download-v2.py',
    'work/nss147/calibrate-clock.mjs',
    'work/nss147/verify-downloaders.mjs',
    'work/nss147/verify-all-endpoints.mjs',
    'work/nss148/save-evidence.py',
    'work/nss148/verify-published.py',
]
for source in extra_sources:
    assert source not in source_hashes
    source_hashes[source] = sha((w / source).read_bytes())
for source, digest in sorted(source_hashes.items()):
    assert all(x not in source.lower() for x in ['private', 'credential', 'connect-router'])
    b = (w / source).read_bytes()
    target = repo / 'code' / source
    assert not target.exists(), 'No frozen source overwrite'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b)
    assert sha(target.read_bytes()) == digest
    n = source.split('/')[1]
    role = ('controlled-test-analysis-or-closure' if source in extra_sources else
            'qualified-source-with-original-failed-attempts-retained')
    manifest['sources'].append({
        'path': 'code/' + source, 'workspaceSource': source, 'sha256': digest,
        'bytes': len(b), 'role': n + '-' + role,
    })
assert manifest['sources'][:len(prefix)] == prefix
manifest.update({'lastAppendExport': 'NSS148',
                 'generatedAt': datetime.now(timezone.utc).isoformat(),
                 'preservesOriginalSourceBytes': True,
                 'routerCredentialsIncluded': False, 'rawCapturesIncluded': False,
                 'binariesIncluded': False, 'privateDataExcluded': True})
dump(manifest_path, manifest)
(repo / 'evidence/nss142-runtime.json').write_bytes(old_runtime)

receipt = read(case / 'stage-receipt-private.json')
checkpoint = read(case / 'stage-checkpoint-verified.json')
plan = read(case / 'stage-plan-private.json')
undo = read(case / 'stage-undo-verified.json')
baseline = read(case / 'baseline-audit.json')
trial = {
    'round': 'NSS147', 'passed': True, 'controlledRealWanPair': True,
    'realCs2SteamPair': False, 'oneWan': 5, 'tcpClass': 'BULK', 'udpClass': 'RT',
    'newCheckpointDownloadedShaAndGzipVerified': checkpoint['gzipVerified'],
    'independentRollbackVerifiedBeforeFirstWrite': receipt['rollbackBeforeFirstWrite'],
    'detachedOwnerParentAndPipeIdentityVerified': receipt['parentIdentityVerified'] and receipt['pipeInodesVerified'],
    'guardianExecBytesActual': plan['execBytes'], 'packetBundleBytesActual': plan['qosCodeBytes'],
    'sourceMaximumSeconds': 6, 'nativeMaximumSeconds': 27, 'ownerMaximumSeconds': 100,
    'recordReadMaximumBytes': 1048576, 'sourceBindingsActualAndFrozen': len(actual_inputs),
    'frames': len(raw['samples']), 'nativeRenewals': len(raw['renewals']),
    'phases': [{'name': p['name'], 'seconds': p['seconds'], 'samples': p['sampleCount'],
                'completed': p['completed'],
                'acceleratedCounts': sorted(set(s['counts']['ecm_nss_ipv4/accelerated_count']
                    for s in raw['samples'][p['sampleStart']-1:p['sampleEnd']]))}
               for p in raw['phases']],
    'actualFourEcmTagsVerified': metrics['actualDualEcmTagsVerified'],
    'pbrFullCtMarkNatWanAffinityVerified': metrics['pbrCtMarkNatWanAffinityVerified'],
    'allFourFqCodelLeavesHavePackets': all(v['packets'] > 0 for d in metrics['leafDeltasAcrossBNearbyAsyncSnapshots'].values() for v in d.values()),
    'freshSourceAndIdentityCheckedInSoftwarePhases': True,
    'ecmStoppedAndAllCountsZeroRequiredBeforeClosedComparison': True,
    'activeNativeLeaseAndRenewalStillStrict': True,
    'terminalReclassificationBodyUnchangedFrom140': True,
    'explicitEarlyRetirementAndFirmwareZero': raw['explicitEarlyRetirement'] and raw['firmwareZeroAfterRetirement'],
    'fullProtectedBaselineRestored': baseline['configurationMatches'],
    'bothPhysicalRootsRestored': raw['dualPhysicalQueuesRestored'],
    'exactStageStateModuleRemovalVerified': all(undo.values()),
    'humanGameAcceptance': False, 'strictCpuComparabilityAccepted': False,
    'fullCakeReplacementAccepted': False, 'nssPermanentlyEnabled': False,
}
assert trial['packetBundleBytesActual'] <= 73728 and trial['guardianExecBytesActual'] <= 9000
assert trial['explicitEarlyRetirementAndFirmwareZero']
assert all(trial[k] for k in ['fullProtectedBaselineRestored', 'bothPhysicalRootsRestored', 'exactStageStateModuleRemovalVerified'])

# Preserve original unsuccessful outcomes, including failed immediate audit,
# separately from a later successful original full-health check.
failures = [
    {'round': 143, 'kind': 'real-candidate-command-size', 'passed': False,
     'execBytes': 9311, 'maximumExecBytes': 9000, 'tcpSockets': 23, 'udpSockets': 82,
     'packedCandidateExecBytes': 9203, 'compactSocketExecBytes': 9175,
     'candidateOnlyAdapterExecBytes': 6551, 'originalPolicyTokenStreamUnchanged': True,
     'checkpointOrStageStarted': False, 'ecmOpened': False, 'originalPreserved': True},
    {'round': 143, 'kind': 'client-guard-before-first-ui-effect', 'passed': False,
     'firstGuardFailed': True, 'firstUiClickDispatchedAfterFailedGuardCheck': True,
     'downloadResumeWasNotProvenGuardedBeforeEffect': True,
     'subsequentV2GuardVerifiedAndExpiredNaturally': True,
     'physicalEscStoppedUi': True, 'finalUiRestoreClaimed': False, 'originalPreserved': True},
    {'round': 144, 'kind': 'missing-local-audit-dependencies', 'passed': False,
     'files': ['failed-wan-owner.lua', 'declared-baseline.mjs'],
     'checkpointOrStageStarted': False, 'ecmOpened': False,
     'endpointAndLaterOriginalFullHealthClosed': True, 'originalPreserved': True},
    {'round': 145, 'kind': 'closed-software-phase-old-epoch-expiry', 'passed': False,
     'stageStarted': True, 'newCheckpointAndIndependentRollbackBeforeWrite': True,
     'softwareSamples': 10, 'acceleratedCounts': [0], 'ecmOpened': False,
     'twentySecondSoftwarePhaseComparedToInitialSixSecondEpoch': True,
     'exactRestoreAndFullRecoveryAuditPassed': True, 'originalPreserved': True},
    {'round': 146, 'kind': 'top-adapter-dropped-closed-argument', 'passed': False,
     'stageStarted': True, 'newCheckpointAndIndependentRollbackBeforeWrite': True,
     'softwareSamples': 10, 'acceleratedCounts': [0], 'rejectionReason': 'epoch expired',
     'affectedSlots': ['tcp', 'udp'], 'ecmOpened': False,
     'immediateRecoveryBaselineAuditPassed': False,
     'immediateRecoveryAuditError': 'Original ownership instance assertion failed',
     'subsequentOriginalFullHealthAuditPassed': True,
     'preciseUndoVerified': True, 'originalPreserved': True},
    {'round': 146, 'kind': 'strict-mapper-model-input', 'passed': False,
     'historicalRenderedClassifierKeyOutsideCanonicalInput': True,
     'beforeRouterConnection': True, 'routerWrites': False, 'originalPreserved': True},
    {'round': 146, 'kind': 'whole-factory-ram-model-too-large', 'passed': False,
     'rawBytes': 27611, 'beforeRouterConnection': True, 'routerWrites': False,
     'wholeFactoryModelNotRun': True, 'originalPreserved': True},
    {'round': 146, 'kind': 'combined-phase-model-too-large', 'passed': False,
     'rawBytes': 18722, 'beforeRouterConnection': True, 'routerWrites': False,
     'modelNotRun': True, 'originalPreserved': True},
    {'round': 146, 'kind': 'phase-model-helper-separator', 'passed': False,
     'completeConsumerCasesAlreadyPassed': 8, 'phaseModelParseFailed': True,
     'routerWrites': False, 'originalPreserved': True},
    {'round': 145, 'kind': 'read-only-process-search-matched-own-shell', 'passed': False,
     'noDestructiveOperation': True, 'correctedExactPriorPidCheckPassed': True, 'originalPreserved': True},
    {'round': 147, 'kind': 'analysis-unobserved-field', 'passed': False,
     'field': 'observation.checkSeconds', 'hardwareExperimentRerun': False,
     'failedOriginalSourceRetained': True,
     'correctedDurationIsNullAndObservedFalse': True, 'originalPreserved': True},
]
for n in [144, 145, 146]:
    c = next(p for p in (w / f'work/nss{n}').glob('controlled-matched-aba-*') if p.is_dir())
    assert not read(c / 'result.json')['passed']
    assert read(w / f'work/nss{n}/v1-final-health.json')['passed']
    if n >= 145:
        assert read(c / 'stage-receipt-private.json')['rollbackBeforeFirstWrite']
        assert read(c / 'stage-checkpoint-verified.json')['gzipVerified']
        assert all(read(c / 'stage-undo-verified.json').values())

mapping = {
    'round': 'NSS148', 'controlledHardwareAbaRound': 147, 'realPreparedEntryRound': 148,
    'residentDeploymentRound': 68, 'residentClassifierChanged': False,
    'desktopOperatedThisBackgroundTest': False, 'steamOrCs2OperatedThisBackgroundTest': False,
    'backgroundOwnedTcpAndUdpUsed': True, 'controlledHardwareAbaPassed': True,
    'sourceBindingsActualAndFrozen': 1518, 'preparedRealEntryBindings': 1527,
    'preparedRealWrapperHardwareAbaPassed': False, 'realDefaultInspectExecuted': True,
    'residentUpTagZeroUnchanged': True, 'actualClassToFourTagsAndFourLeaves': True,
    'pbrFullCtMarkNatWanAffinityUnchanged': True, 'rollbackAndAllEndpointsClosed': True,
    'newCpuComparisonAccepted': False, 'humanCs2Acceptance': False,
    'highLoad300MbpsAcceptance': False, 'longTermAcceptance': False,
    'fullCakeReplacementAccepted': False, 'productionNssPermanentlyEnabled': False,
    'upstreamNssDefectClaimed': False, 'upstreamSubmitted': False,
    'harnessBugRootCauseProved': True, 'oldNativeEpochOnlyBypassedWhenBothFrontendsStoppedAndEcmAllZero': True,
    'sourceAndActiveNativeDeadlinesNotWidened': True, 'originalFailuresKept': True,
    'nightHeartbeatRemainsPaused': True,
}
new_evidence('mainline', mapping)
new_evidence('trial', trial)
new_evidence('metrics', metrics)
new_evidence('failures', failures)
new_evidence('controlled-entry-qualification', quals[147])
new_evidence('real-entry-qualification', quals[148])
new_evidence('readonly-readiness', ready)
new_evidence('readonly-reader', reader)
new_evidence('final-audit', health)
new_evidence('physical-final', physical)
new_evidence('endpoint-client-closure', endpoints)
new_evidence('receiver-closure', receivers)
new_evidence('candidate-reader-size', read(w / 'work/nss143/candidate-adapter-size-proof.json'))
new_evidence('client-safety-failure', read(w / 'work/nss143/client-safety-qualification.json'))
proof = {
    'round': 'NSS148', 'historicPrefixSources': len(prefix),
    'historicPrefixCanonicalSha256': sha(json.dumps(prefix, sort_keys=True, separators=(',', ':')).encode()),
    'sources': len(source_hashes), 'sourcesByRound': sources_by_round,
    'sourceHashes': source_hashes, 'additionalAnalysisAndPublicationSources': extra_sources,
    'sourceBindingsActualAndFrozenMatch': True, 'boundInputsInActualControlledCase': 1518,
    'realPreparedBoundInputs': 1527,
    'oldNss142RuntimeRetainedExactSha256': sha(old_runtime),
    'privateHostBootstrapExcluded': True, 'credentialsCtNoncesConfigurationCheckpointsAndBinariesExcluded': True,
    'historicFilesExceptCurrentRuntimeAllBytesRetained': True, 'originalFailuresKept': True,
    'wholeFactoryRamAbaNotClaimed': True, 'actualWholeFactoryHardwareAbaPassed': True,
}
new_evidence('source-proof', proof)
runtime = {
    'round': 'NSS148', 'checkedAt': health['observedAt'],
    'deploymentReference': 'work/nss68/deployment-latest.json',
    'classifierConfigSha256': health['configSha256'],
    'workerPid': health['workerPid'], 'guardianPid': health['guardianPid'],
    'residentClassifierChangedThisTurn': False, 'nssPermanentlyEnabled': False,
    'qualifiedExperimentalEntry': 'work/nss147/controlled-session.mjs',
    'qualifiedExperimentalEntryBoundInputs': 1518,
    'controlledExperimentalFactoryHardwareAbaPassed': True,
    'preparedRealEntry': 'work/nss148/real-session.mjs',
    'preparedRealEntryBoundInputs': 1527, 'preparedRealEntryHardwareAbaTested': False,
    'currentNssAdmissionMustBeRefreshedBeforeWrite': True,
    'audit': health, 'physicalRootRestoreAudit': physical, 'endpointClientClosureAudit': endpoints,
    'ownedReceiverClosureAudit': receivers, 'latestRealReadonlyInspect': ready,
    'physicalClassChangeRetirementAcceptedFrom139': True,
    'freshEpochRelearningSameCtAcceptedFrom139': True,
    'realHumanGameAcceptance': False, 'newCpuComparisonAcceptedThisTurn': False,
    'historical142RuntimePreservedSha256': sha(old_runtime),
    'nightHeartbeatRemainsPaused': True, 'noDesktopOrSteamCs2NeededForControlledEngineering': True,
    'newAdmissionRequiredForAnyFutureExperiment': True,
    'softwarePhasesMayIgnoreOldAdmissionEpochOnlyWithStoppedZeroEcm': True,
    'activeNativeLeaseStillMaximumSeconds': 27,
}
dump(repo / 'evidence/current-runtime.json', runtime)

section = """更新：2026-10-06 11:17，北京时间。最新NSS148整理／147实测。用户正在使用电脑，本轮采用自有端点后台受控下载＋小UDP，没有启动或操作Steam/CS2、桌面或新增游戏。常驻仍NSS68/config581b5d46…c791d7、worker31657/guardian17139，全部实验已撤销。

**修复了20秒软件对照误用旧6秒准入epoch的测试程序缺陷。147真实单WAN5、一TCP BULK＋一UDP RT完成三段各20.01秒、123帧、ECM0→2→0和7次native续租；实际四tag/四FQ-CoDel leaf、完整PBR/ct mark/NAT/WAN affinity及精确恢复通过。**

见 [汇总](../evidence/nss148-mainline.json)、[实测轮次](../evidence/nss148-trial.json)、[完整指标](../evidence/nss148-metrics.json)、[失败记录](../evidence/nss148-failures.json)、[受控入口资格](../evidence/nss148-controlled-entry-qualification.json)、[真人入口资格](../evidence/nss148-real-entry-qualification.json)、[只读现网](../evidence/nss148-readonly-readiness.json)、[完整终态](../evidence/nss148-final-audit.json)、[物理队列](../evidence/nss148-physical-final.json)、[端点关闭](../evidence/nss148-endpoint-client-closure.json)。

| 指标 | software A | NSS B | software A2 |
|---|---:|---:|---:|
| 实际下载payload Mbps | 26.681 | 26.971 | 25.442 |
| softirq % | 17.549 | 3.008 | 8.061 |
| CPU busy % | 34.171 | 18.820 | 25.983 |
| time_squeeze / softnet drop | 0 / 0 | 0 / 0 | 0 / 0 |
| UDP echo 收到/发出 | 863/864 | 873/875 | 824/838 |
| UDP RTT p95 ms | 192.725 | 191.813 | 192.785 |
| 其它WAN RX＋TX Mbps | 3.556 | 2.650 | 2.028 |

- 功能闭环通过；严格CPU可比条件未通过，因为用户正常上网的背景流量超过原0.5Mbps/0.25Mbps范围。保存原七项判定、comparability=false和降幅null，不从以上原始softirq给出正式降幅，不要求用户停网重复追阈值。UDP echo未返回和RTT变化是受控端点数据，不能充当CS2 loss/jitter/Miss。
- B附近异步leaf计数：下bulk＋48,285包/drop379，下RT＋922包/drop0；上bulk＋39,640包/drop0，上RT＋888包/drop0。支持真实加速流进入独立可控队列、RT leaf在这轮无自身丢弃，不能据此证明精确长期限速、游戏体验或把bulk drop都归因FQ/AQM。DOWN30/bulk29/RT1，UP60/bulk59/RT1/default950保持；软件A/A2也保留相同实验队列，比较的是软件转发和fast path。
- 原140完整ABA此前从未跑过；145在A约4.5秒即旧6秒epoch过期拒绝，146虽修内层却漏顶层facade参数，仍在ECM前拒绝。147只在两frontend已stop、全部ECM计数0的软件段比较中跳过旧准入epoch截止；当前source/完整class/CT/producer严格，活动B的27秒native及续租/100秒owner不改，支持改类的精确撤销体不改。146即时恢复审核另有instance断言失败；随后原完整终态通过，两份结果分开保留。
- 147实际factory完整硬件ABA通过；目标RAM仅8个完整Consumer案例＋9个实际compare/phase/facade案例，模型显式mock inspector，未声称整个factory在RAM执行。实际payload73,685/guardian8,899字节，原9000/65536/73728及1MiB边界不放宽；1518项实际绑定与冻结副本精确匹配。
- 143真人候选读取因23TCP＋82UDP使命令9311>9000写前拒绝，两个压缩候选仍超限。最终只裁剪候选可见性reader中无用操作API，原inspect/readContext/candidates token stream不变；同历史输入6551，真实新读取6483。上一轮第一次UI点击发生在guard失败之后，不能声称下载始终提前受guard保护；后来v2验证及自然到期/物理Esc记录保留，本轮没有任何UI。
- 144漏两个本地审核依赖、145/146失败、146三个模型资格/尺寸拒绝及helper语法失败、147未观测checkSeconds分析失败全部保留。新分析将该时长写null/observed=false，没有伪造持续时间，也没有为分析重跑硬件。
- 已将147实测factory接回148真人入口，保留Steam TCP/CS2 UDP程序socket归属、checkpoint后最终选择、精确单WAN gate和改类撤销。1527绑定，默认inspect已真实只读运行，0pair/no writes。这个wrapper的完整真人ABA仍未执行；不再推荐有已知完整软件段缺陷的140入口。
- 每轮stage有新checkpoint下载/SHA/gzip和控制连接外独立PPID1 owner写前证明；成功147精确早退恢复，最终source4.59秒、selectors4由原native ownership审核验证，ECM关闭全零、无事务/stage/state/模块，两物理wan/lan4原mq＋四fq_codel的options/handles精确恢复。11个已有自有负载unit inactive/MainPID0，canonical防火墙匹配、临时规则/端口/客户端/guard/SSH发送器0残留。WAN4原认证down和四路failover不变，未主动认证或改校园策略。
- 阶段判定：单WAN自动class→NSS双向bulk/RT功能和真实改类撤销／新代重学已证明；受控上传128约30Mbps可比短窗CPU是历史证据。当前版本下载功能已证明，300Mbps主下载、长期、多WAN、ECN、真人CS2体验和完整CAKE替代尚未验收。夜间heartbeat维持暂停。继续工程可以用后台受控负载；真人体验只留用户方便时一次集中验证，不要求持续挂机，不扩第二WAN/共享预算/WiFi/autorate。
"""
for name, title in [('docs/STATE.md', '# NSS148 · 后台单WAN闭环已通过'),
                    ('docs/PLAN.md', '# 下一步：按阶段验收，不要求持续挂游戏'),
                    ('docs/EXPERIMENT_LOG.md', '# NSS143–148 · 修复软件对照段并完成后台下载闭环')]:
    p = repo / name
    old = p.read_text(encoding='utf-8')
    p.write_text(title + '\n\n' + section + '\n## NSS142及更早历史\n\n' + old, encoding='utf-8')
agents = repo / 'AGENTS.md'
old = agents.read_text(encoding='utf-8')
agents.write_text("""# 接续此研究

最新NSS148整理／147实测：用户使用电脑，不操作UI/Steam/CS2。自有32Mbps有界下载＋小UDP，单WAN5三段20.01秒/123帧、ECM0/2/0、四tag/四leaf/完整mark/NAT/affinity/7续租/精确恢复通过。下载26.681/26.971/25.442，softirq17.549/3.008/8.061；背景3.556/2.650/2.028违反原可比条件，comparison=false/降幅null，UDP不作CS2。下bulkdrop379/两RTdrop0，非300/真人/长期/完整CAKE验收。147修闭软件段旧epoch过期并补顶facade传参：只能stop且ECM全零时跳过旧6秒准入截止；当前source/class/CT仍严，active27/owner100不改。145/146 ECM前失败和146即时instance恢复审核失败／后续成功分开保留。1518实际绑定冻结精确、payload73685/actualguardian8899；8consumer+9phase RAM分项，不称整个factory RAM。148真人wrapper用147已实测factory/143精简visibility reader，1527项/defaultinspect现场0pair/no writes，真人wrapper完整ABA未执行。1439311/9203/9175>9000失败及首UIguard失败后点击保存；144漏审核依赖、146资格/模型尺寸/语法、147分析缺字段均保存。常驻68/config581b5d46…c791d7/31657/17139/upTag0不变，最终ECM全零无残留/两根精确恢复，11端点/客户端/SSH sender关闭，WAN4down四路failover保持。142 runtime归档原字节，heartbeat保持暂停，不扩WAN/共享预算/WiFi/autorate/新游戏下载。工程可继续后台自有受控测试；最后真人只在用户方便时一次，不重复CPU门槛、不重装classifier。以STATE开头为准。

## NSS142及更早历史

""" + old, encoding='utf-8')
readme = repo / 'README.md'
old = readme.read_text(encoding='utf-8')
readme.write_text("""# Athena NSS mainline

最新 [NSS148](evidence/nss148-mainline.json)：修复测试程序的软件段旧epoch错误，147自有后台下载单WAN完整20秒A/B/A2、ECM0/2/0、双向四tag/四FQ-CoDel leaf及恢复通过。无需启动游戏或Steam。背景负载变化使本轮严格CPU对比未通过；不称真人CS2/300Mbps/长期验收。148真人入口使用已实测147 factory，默认只读已运行；实验均撤销，常驻68不变。先读 [STATE](docs/STATE.md)、[PLAN](docs/PLAN.md)。

## NSS142及更早历史

""" + old, encoding='utf-8')
index = repo / 'docs/ARTIFACT_INDEX.md'
index.write_text("""# 最新证据：NSS148整理／147后台实测

- [状态](STATE.md)、[计划](PLAN.md)、[失败记录](../evidence/nss148-failures.json)
- [汇总](../evidence/nss148-mainline.json)、[完整实测](../evidence/nss148-trial.json)、[实际指标](../evidence/nss148-metrics.json)
- [源白名单及历史保留](../evidence/nss148-source-proof.json)、[软件段缺陷修复](ISSUE_CONTROLLED_ABA_EPOCH.md)
- [终态](../evidence/nss148-final-audit.json)、[物理队列](../evidence/nss148-physical-final.json)、[端点关闭](../evidence/nss148-endpoint-client-closure.json)
- [下一次真人入口](../code/work/nss148/real-session.mjs)，默认仅inspect；[只读结果](../evidence/nss148-readonly-readiness.json)

## 历史索引

""" + index.read_text(encoding='utf-8'), encoding='utf-8')
issue = """# 本地测试程序：20秒软件对照误用6秒准入epoch

范围：本私有仓库的实验harness，尚不是qca-nss-ecm或固件缺陷，未提交上游。

最小复现：原140 fast-path的A段要求20秒，Consumer.compareEpoch每帧同时核验当前完整分类和初始6秒epoch截止。即使分类源持续刷新、CT/class/PBR未变，A约4.5秒/10帧后仍拒绝，ECM从未开放。145实测失败；146内层增closed参数，但A.compareObserved顶facade未转发，实测rejectedComparison.reason仍为epoch expired，影响TCP和UDP。

修改：147 classifier.lua的Consumer.compareEpoch只在显式closed时略过旧初始epoch截止，out.compareObserved及顶facade完整转发closed。fast-path.observe只在未active时先stopped核验双方frontend与全部计数0；当前完整source/class/CT/producer检查继续严格，活动NSS native截止和续租不变。记录拒绝比较结果供定位。真实BULK→BE精准撤销逻辑保持，不能以该开关重新开放terminal gate。

证据：8个完整Consumer及9个实际phase/compare/facade目标RAM分项通过，明确mock inspector，不称整个factory RAM验证；147完整硬件三段20.01秒/123帧、ECM0→2→0、7续租和精确恢复通过。对应 [失败](../evidence/nss148-failures.json)、[轮次](../evidence/nss148-trial.json)、[实际源码](../code/work/nss147/classifier.lua) 和 [fast-path](../code/work/nss147/fast-path.lua)。148仅接回同一已实测factory；真人wrapper完整ABA尚未跑过。

相关独立问题：143候选读取命令9311>9000，只精简visibility reader且保持原policy token；144漏本地审核依赖；146立即恢复审核instance断言失败，后来完整终态通过。它们和原失败分开保留，不以147成功覆盖。
"""
(repo / 'docs/ISSUE_CONTROLLED_ABA_EPOCH.md').write_text(issue, encoding='utf-8')

rows = ''
for p in metrics['phases']:
    v = p['whole']
    rows += ('<tr><th>' + p['phase'] + '</th><td>' + f"{v['clientTcpReceivedMbps']:.3f}" +
             '</td><td>' + f"{v['softirqPercent']:.3f}%" + '</td><td>' + f"{v['busyPercent']:.3f}%" +
             '</td><td>' + str(v['udp']['received']) + '/' + str(v['udp']['sent']) +
             '</td><td>' + f"{v['udp']['rttP95Ms']:.3f}" + '</td><td>0 / 0</td></tr>')
html = """<!doctype html><html lang="zh-CN"><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>NSS148 后台单WAN验收</title><style>
body{font:16px/1.75 system-ui,"Microsoft YaHei",sans-serif;margin:0;background:#f4f6f8;color:#182334}
main{max-width:1000px;margin:40px auto;padding:34px;background:white;border-radius:16px}
h1{font-size:30px;margin:0 0 8px}h2{font-size:22px;margin-top:32px}.meta{color:#536174}
.ok{background:#e5f4ed;padding:18px;border-radius:8px}.limit{background:#fff3de;padding:18px;border-radius:8px}
table{width:100%;border-collapse:collapse;font-variant-numeric:tabular-nums}th,td{text-align:left;border-bottom:1px solid #dfe5ed;padding:10px}
a{color:#1c579c}li{margin:8px 0}code{background:#f0f2f6;padding:2px 4px}@media(max-width:700px){main{margin:0;padding:20px}table{font-size:13px}th,td{padding:7px}}
</style><main><h1>后台受控闭环已完成</h1><p class="meta">NSS148整理 · NSS147实测 · 2026-10-06 · 单WAN5 · 无桌面/Steam/CS2操作</p>
<p class="ok">一条自有TCP下载＋一条低速UDP已完成software→NSS→software，各20.01秒。
ECM 0→2→0；学习前自动class正确，bulk/RT分别进入独立NSS FQ-CoDel leaf。
完整PBR/ct mark/NAT/WAN affinity、7次续租和精确恢复通过。</p>
<h2>实际观测</h2><table><tr><th>阶段</th><th>下载Mbps</th><th>softirq</th><th>busy</th><th>UDP收到/发出</th><th>RTT p95 ms</th><th>squeeze/drop</th></tr>""" + rows + """</table>
<p class="limit">这是功能验收。其它WAN背景流量3.556→2.650→2.028 Mbps，不满足原严格CPU对照条件，因此正式相对降幅留空。
UDP echo不是CS2 jitter/loss/Miss；本轮不声称真人体验、300Mbps、长期或五WAN验收。</p>
<h2>队列与恢复</h2><p>附近异步快照：下bulk＋48,285包/drop379，下RT＋922包/drop0；上bulk＋39,640包/drop0，上RT＋888包/drop0。
真实RT流进入独立leaf且本轮该leaf无自身丢弃。bulk丢弃不等于已证明AQM效果或上游全路径丢包原因，异步计数也不是精确长期限速证明。</p>
<p>DOWN30/bulk29/RT1，UP60/bulk59/RT1，未选中fallback950。每次stage前新checkpoint及独立PPID1超时撤销核验。
最终ECM关闭全零，无事务/stage/state/实验模块，两物理原mq＋四fq_codel精确恢复；
11个已有自有负载及Windows客户端/guard、SSH发送器均关闭，防火墙基线匹配。常驻分类器68与原配置保持，WAN4既有认证故障仍存在。</p>
<h2>此次修复了什么</h2><p>原完整20秒软件段误比较初始6秒学习凭证，导致约4.5秒提前拒绝。
145失败后146内层修复仍漏顶facade传参；147补全传参后完整硬件ABA通过。
只在两frontend已停止且ECM全零的软件段略过旧epoch截止；当前分类来源/身份仍核验，活动NSS的27秒native lease和100秒owner均未放宽。
8个完整Consumer和9个目标RAM分项通过；整个factory RAM未执行，硬件实际完整执行已通过。</p>
<p>失败全部保留：143超长候选命令及首UI guard失效后点击、144本地依赖缺失、145/146软件段拒绝、146立即恢复instance审核失败和后续通过、模型尺寸/语法问题、147未观测字段分析失败。
这些是本地实验harness问题，不宣称NSS上游缺陷，也没有提交Issue/PR。</p>
<h2>当前阶段和下一步</h2><p>单WAN自动分类→NSS双向bulk/RT、受控完整闭环与历史真实改类撤销／新epoch重学已证明。
修复后的factory已接回148真人入口，默认inspect真实只读运行0pair/no writes。
可以继续后台工程测试，无需用户挂机；真人体验只留方便时一次。
本轮没有长期开放ECM，也没有把全部软件CAKE替换成NSS。第二WAN/共享预算/WiFi/autorate继续后置，夜间heartbeat保持暂停。</p>
<p><a href="https://github.com/ZyPulse-zy/athena-nss-mainline/blob/main/docs/STATE.md">仓库状态</a> ·
<a href="https://github.com/ZyPulse-zy/athena-nss-mainline/blob/main/docs/ISSUE_CONTROLLED_ABA_EPOCH.md">缺陷最小复现与修复</a></p></main></html>"""
(w / 'outputs/nss148-mainline-report.html').write_text(html, encoding='utf-8')
(repo / 'reports/nss148-mainline-report.html').write_text(html, encoding='utf-8')

for path, digest in historical_hashes.items():
    if path == 'evidence/current-runtime.json':
        continue
    assert sha((repo / path).read_bytes()) == digest, 'Frozen file changed: ' + path
dump(out / 'export-precheck.json', {
    'passed': True, 'newSources': len(source_hashes), 'totalSources': len(manifest['sources']),
    'old142RuntimeExact': sha((repo / 'evidence/nss142-runtime.json').read_bytes()) == sha(old_runtime),
    'historicFilesExactExceptCurrentRuntime': True, 'actual1518BindingsFrozenExact': True,
    'controlledHardwareABA': True, 'strictCpuComparisonAccepted': False,
    'humanGameAcceptance': False, 'desktopOperated': False,
})
print(json.dumps(read(out / 'export-precheck.json')))
