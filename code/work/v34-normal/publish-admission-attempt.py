"""Publish one actual owner-admission refusal and its independently checked recovery."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import copy, hashlib, json, subprocess

w = Path(__file__).resolve().parents[2]
repo = w / 'athena-nss-mainline'
r = w / 'work/v34-normal'
base = 'f08bf08f58d28a7a4c9edae53df3d536acb43a1d'
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
dump = lambda v: json.dumps(v, ensure_ascii=False, indent=2) + '\n'
sha = lambda b: hashlib.sha256(b).hexdigest()
def git(*args):
    return subprocess.check_output(['git', *args], cwd=repo)
def new_json(p, value):
    with p.open('x', encoding='utf8') as f:
        f.write(dump(value))

assert git('rev-parse', 'HEAD').decode().strip() == base
assert not git('status', '--porcelain')
old = {}
for row in git('ls-tree', '-r', '-z', base, '--', 'code', 'evidence').split(b'\0'):
    if row:
        header, name = row.split(b'\t', 1)
        old[name.decode()] = header.decode().split()[2]
assert len(old) == 4583
old_bytes = {n: sha((repo / n).read_bytes()) for n in old}
manifest = read(repo / 'source-manifest.json')
prefix = copy.deepcopy(manifest['sources'])
assert len(prefix) == 4037
q, prep = read(r / 'entry-qualified.json'), read(r / 'prepare-receipt.json')
models = read(r / 'prepared-selection-qualified.json')
cases = [p for p in r.glob('session-*') if (p / 'controller-error.json').exists()]
assert len(cases) == 1
case = cases[0]
closure = w / read(r / 'closure-pointer.json')['directory']
run = w / read(r / 'active-run-private.json')['directory']
ui, clients = read(r / 'client-ui-restored.json'), read(closure / 'client-closure.json')
audit, physical = read(r / 'v34-final-audit.json'), read(closure / 'physical-final.json')
diag = read(r / 'admission-diagnosis.json')
process, result = read(run / 'controller-process.json'), read(case / 'result.json')
baseline, record = read(case / 'baseline-audit.json'), read(case / 'last-record-private.json')
undo = read(case / 'stage-undo-verified.json')
load = read(r / 'load-readiness-private/controlled-candidates-private.json')
guard, hud = read(closure / 'result.json'), read(r / 'controller-window-check.json')
download = read(r / 'download-resume-observed.json')
bindings = read(case / 'source-manifest-preaudit.json')
assert q['passed'] and q['inheritedBindings'] == 2723
assert len(q['sourceManifest']) == 39 and len(bindings) == 2762
assert q['relativeDependenciesExist'] == 61 and q['newPreparationModels'] == 13
assert not q['historicalModelsReplayed'] and not q['hardwareExecuted'] and not q['wholeFactoryModeled']
assert q['onlyReadPreparationAndInitialSelectionOrderChanged']
assert q['dataPlaneAndImmutableCandidatePolicyUnchanged'] and q['postCheckpointWanMarkNatAndOriginalGameScopeUnchanged']
for name, digest in bindings.items():
    assert sha((w / name).read_bytes()) == digest, name
    assert sha((case / 'frozen' / name).read_bytes()) == digest, name
for name, digest in q['sourceManifest'].items():
    assert bindings[name] == digest and sha((w / name).read_bytes()) == digest, name
for name, digest in prep['oldHashes'].items():
    assert sha((w / name).read_bytes()) == digest, name
assert models['passed'] and models['checks'] == 13 and models['modelOnly']
assert models['nativePrerequisitesModeledOnly'] and not models['hardwareExecuted']
assert process['exitCode'] == 1 and process['error'] is None
assert not result['passed'] and len(result['errors']) == 1
assert 'Initial admission refused:' in result['errors'][0] and 'Selected class is not admitted' in result['errors'][0]
assert diag['passed'] and diag['localExistingInputsOnly'] and diag['networkReads'] == diag['routerWrites'] == 0
assert diag['lastPostCheckpointSelectedClasses'] == {'tcp': 'BULK', 'udp': 'RT', 'tcp2': 'BULK'}
assert diag['selectedWanSet'] == [1, 2, 5] and diag['preparedNativeWanCount'] == 5
assert all(diag[k] for k in ['initialWanFreezeAfterNativePreparationPassed', 'postCheckpointSelectionPassed', 'checkpointCreated', 'checkpointDownloadedShaAndGzipVerified', 'detachedStageStarted', 'independentUndoBeforeFirstWrite'])
assert not any(diag[k] for k in ['initialOwnerProbeSucceeded', 'initialOwnerFullClassifierSnapshotCaptured', 'exactAbsentSlotAndClassChangeCauseEstablished', 'firmwareFaultEstablished', 'nssGateModuleLoaded', 'ecmPermitGranted', 'fastPathMeasurementStarted', 'wholeFactoryAcceptance', 'installedGateRetargeted'])
assert diag['initialOwnerProbeCount'] == 1 and diag['classifierSnapshotRecords'] == 0
assert record['newNssPermit'] is False and record['moduleLoaded'] is False and record['gateComplete'] is False
assert all(record[k] for k in ['qosRestored', 'qosModuleUnloaded', 'dualPhysicalQueuesRestored', 'wanRestored', 'mwan3Restored', 'stateNodeRemoved'])
assert all(undo.values())
assert len(load['game']) == 1 and len(load['bulk']) == 11 and len(load['pairs']) == 1
assert download['originalGuardReadyBeforeResume'] and not download['guardDeadlineExtended']
assert download['temporarySteamLimitKbps'] == 32000 and download['boundedDownloadSeconds'] == 180
assert baseline['configurationMatches'] and all(baseline['checks'].values())
assert clients['passed'] and clients['naturalTimedExitPassed'] and clients['deadlineSeconds'] == 180
assert clients['readyBeforeDownload'] and clients['guardProcessGone'] and clients['fullControllerSessionStarted']
assert clients['ownedTestProcessesRemaining'] == clients['cs2ProcessesRemaining'] == 0
assert guard['passed'] and guard['timedExitExecuted'] and not guard['originalClientUiRestored']
assert ui['passed'] and ui['downloadPaused'] and ui['downloadProgressPercent'] == 48
assert ui['networkBps'] == ui['diskBps'] == 0 and not ui['downloadLimitEnabled']
assert ui['downloadLimitValueClearedBeforeDisable'] and ui['recoveryAutoResumeOutsideOriginalGuard']
assert not ui['strictCumulativeDownloadDurationProven']
assert hud['noNssBPhaseOccurred'] and not hud['humanExperienceVerified'] and not hud['continuousTelemetryProven']
assert hud['observations'][1]['valuesHidden'] and hud['observations'][1]['pingMs'] is None
assert audit['passed'] and audit['queryAge'] < 6 and audit['ecmClosedAndZero']
assert audit['protectedConfigurationUnchanged'] and audit['serviceEpochPinned'] and audit['allFiveHealthyWanBaseline']
assert physical['passed'] and physical['defaultQueueOptionsAndHandlesExact']

# All actual inputs remain local, with new exact copies rather than edits to frozen evidence.
sealed = closure / 'sealed-attempt-inputs'
sealed.mkdir()
inputs = [r / n for n in ['client-before-observed.json', 'game-connected-observed.json',
    'download-resume-observed.json', 'controller-window-check.json', 'client-ui-restored.json',
    'admission-diagnosis.json', 'one-session-attempt.json', 'active-run-private.json']]
inputs += [case / n for n in ['controller-error.json', 'result.json', 'last-record-private.json',
    'persistent-selection-private.json', 'final-selection-before-wan-freeze-private.json',
    'selected-private.json', 'post-checkpoint-controlled-receipt-private.json',
    'source-manifest-preaudit.json', 'stage-checkpoint-private.json', 'stage-checkpoint-verified.json',
    'stage-plan-before-encode-private.json', 'stage-plan-private.json', 'stage-receipt-private.json']]
inputs += [run / n for n in ['controller-process.json', 'controller-stdout-private.txt', 'controller-stderr-private.txt']]
frame_names = ['controlled-candidates-private.json','controlled-pc-raw-private.json','normal-reader-process-private.json',
    'pc-app-endpoints-private.json','real-candidates-private.json','real-candidates-raw-private.json','real-reader-qualified.json']
inputs += [case / ('last-post-checkpoint-' + n) for n in frame_names]
inputs += [r / 'load-readiness-private' / n for n in frame_names]
private_hashes = {}
for index, original in enumerate(inputs):
    data = original.read_bytes()
    assert len(data) <= 1048576, original.name
    dest = sealed / (f'{index:02d}-' + original.name)
    with dest.open('xb') as f:
        f.write(data)
    assert dest.read_bytes() == data
    private_hashes[str(dest.relative_to(closure)).replace('\\', '/')] = sha(data)
new_json(closure / 'sealed-attempt-inputs-private.json', private_hashes)

sources = [*q['sourceManifest'], 'work/v34-normal/entry-qualified.json', 'work/v34-normal/prepare-receipt.json',
    'work/v34-normal/read-final-health.mjs', 'work/v34-normal/read-physical-final.mjs',
    'work/v34-normal/capture-client-closure.ps1', 'work/v34-normal/diagnose-admission.mjs',
    'work/v34-normal/publish-admission-attempt.py']
assert len(sources) == len(set(sources)) == 46
hashes = {}
for rel in sources:
    assert 'private' not in Path(rel).name.lower()
    data = (w / rel).read_bytes()
    dest = repo / 'code' / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open('xb') as f:
        f.write(data)
    hashes[rel] = sha(data)
    manifest['sources'].append({'path': 'code/' + rel, 'workspaceSource': rel,
        'sha256': sha(data), 'bytes': len(data), 'role': 'actual-normal-owner-admission-refusal-and-recovery'})
manifest['lastNormalAdmissionAttemptExport'] = 'V34_POSTCHECKPOINT_OWNER_ADMISSION_REFUSAL'
(repo / 'source-manifest.json').write_text(dump(manifest), encoding='utf8')
def evidence(name, value):
    new_json(repo / 'evidence' / name, value)

evidence('v34-normal-entry-qualification.json', q)
evidence('v34-prepared-selection-model.json', models)
public_diag = copy.deepcopy(diag)
public_diag.pop('privateInputSha256')
public_diag.update({'controllerFactoryInvoked': True, 'controllerExitCode': 1,
    'normalApplicationFactoryAcceptance': False, 'temporaryPhysicalQosConfigured': bool(record['qosConfigured']),
    'independentUndoCompleted': True, 'actualClassAtFailedOwnerProbeUnknown': True})
evidence('v34-admission-refusal.json', public_diag)
evidence('v34-client-window.json', {
    'passedAsObservation': True, 'actualCs2DeathmatchConnectedBeforeDownload': True, 'mapDuringWindow': 'Cache',
    'downloadTemporaryLimitKbps': 32000, 'downloadSpeedObservedMbps': [33.4, 32.0],
    'guardReadyBeforeDownload': True, 'clientDeadlineSeconds': 180, 'clientDeadlineReset': False,
    'guardNaturalExactApplicationExitPassed': True, 'guardExitObservedAt': guard['observedAt'],
    'hudObservations': hud, 'hudIsNssPhaseEvidence': False, 'subjectiveHumanExperienceAccepted': False,
    'recoveryAutomaticDownloadResumptionObserved': True, 'strictCumulative180SecondDownloadProofAvailable': False,
    'currentUiRestoration': ui, 'fullNssFactoryAcceptance': False})
evidence('v34-normal-restoration.json', {'passed': True, 'readonlyFinalRouterAudit': True,
    'fullAudit': audit, 'physicalQueues': physical, 'controllerBaselineRestoration': baseline,
    'stageUndo': undo, 'clientProcessClosure': clients, 'clientUiSettingsRestoreConfirmed': True,
    'testDownloadPaused': True, 'originalDownloadLimitDisabled': True,
    'newCheckpointAndIndependentStageActuallyStarted': True, 'temporaryPhysicalQosActuallyConfigured': bool(record['qosConfigured']),
    'productionGateLoaded': False, 'ecmLearningOpened': False,
    'noRouterConfigurationWritesAfterRecoveryAudit': True,
    'normalFactoryHardwareAcceptance': False, 'humanExperienceAcceptance': False, 'newCpuAcceptance': False,
    'permanentNssDeployment': False, 'noNewEndpointOrFixtureStarted': True,
    'strictCumulativeDownloadDurationNotProven': True,
    'originalGuardDidNotRestoreUi': True, 'laterManualUiRestorationProvedSeparately': True})
evidence('v34-normal-source-proof.json', {'passed': True, 'baseCommit': base, 'historicPrefixSources': len(prefix),
    'historicPrefixCanonicalSha256': sha(json.dumps(prefix, sort_keys=True, separators=(',', ':')).encode()),
    'sourceHashes': hashes, 'oldCodeAndEvidenceBlobsChecked': len(old), 'oldCodeAndEvidenceUnmodified': True,
    'qualificationSourceCopiesExact': 39, 'actualRuntimeBindingCopiesExact': len(bindings),
    'privateInputsCopiedExact': len(private_hashes), 'entryBindings': 2762, 'newPreparationModels': 13,
    'historicalSelectorModelsReused': 18, 'historicalActualRefusalModelsReused': 14, 'historicalModelsReplayed': False,
    'onlyInitialNativePreparationAndSelectionOrderChanged': True, 'originalPostCheckpointSelectionContractPreserved': True,
    'normalFactoryHardwareAcceptance': False, 'currentSteamUiSettingsRestoreConfirmed': True,
    'previousV33AndAllEarlierDeadlineFailuresAndEvidenceUnmodified': True,
    'rawCtNoncesCredentialsConfigurationsCheckpointsBinariesAndProcessCommandLinesExcluded': True})

stamp = datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
report = f'''# 正常程序通过 checkpoint 后选择；owner 准入拒绝，恢复通过

更新：北京时间 {stamp}。v34已实际进入Cache死斗新回合，再以独立180秒客户端守护恢复已有Hades下载，临时限速32Mbps。自动分类识别1条CS2 RT、11条Steam BULK及一组跨WAN三流。**先前准备时冻结TCP的阻塞已越过，但独立owner最终分类准入拒绝，没有NSS B段或普通程序factory验收。**

## 本次推进与实际边界

原完整audit后，先读取现有候选WAN的原native前置条件，再从最新实际分类和程序socket中选定TCP与WAN范围；保持原CS2身份。只读准备覆盖5个候选WAN，不表示五WAN同时NSS。13项本地模型仅针对这一顺序，native前置条件是模型数据；旧18＋14模型、硬件数据面及post-checkpoint原WAN/full mark/NAT合同保持，未重复旧测试。资格2723＋39＝2762绑定、61相对依赖；default inspect已实际运行且0游戏/0下载/0pair/no writes。

实际选中WAN1/2/5上的两TCP BULK＋一UDP RT。新checkpoint已下载并通过SHA/gzip检查；checkpoint后的最新分类仍为BULK/RT/BULK，原CS2及冻结WAN合同通过。独立owner在第一生产写前就绪，暂存上传完成，临时物理QoS确实配置。随后initial alignment第一次探测报`Selected class is not admitted`，owner拒绝继续：gate模块未加载、ECM未放行、没有60秒NSS测量。

本地诊断只复核已有文件，未增加远端查询或重试。最后PC帧属于checkpoint后选择，不能当作失败时owner分类帧；owner失败时未保存完整分类快照，确切缺失slot/改类根因未知。缺失准入候选不能当CT退出或firmware故障。原错误、checkpoint、guard、完整私有输入和2762份实际绑定来源保持。

## 客户端及 HUD

Cache正常死斗回合先连接，9:46的软件HUD见ping15ms、上下loss0%；下载后7:56和7:30画面也见ping15ms、上下loss0、绿色网络图。8:27未显示的数值保持未知。没有数值jitter/Miss、连续遥测或用户本人体验确认，全部是软件阶段，不能写成NSS游戏质量通过。

下载实际UI约32–33.4Mbps。11:48在原守护期限内暂停到34%/网络磁盘0bps，并清空32000、关闭限速；原守护11:49自然精确退出CS2/Steam。后来为恢复Steam界面重开时又自动续传，见327.2Mbps，已立即再次暂停，11:51视觉确认48%/网络磁盘0bps、原限速OFF及区域/bit显示/游戏中下载设置保持。这段在原守护之外，**累计严格180秒/720MB不成立**；原guard从未重置，自动续传片段如实保留，不能用进程退出替代UI恢复。

## 完整恢复及后续

独立stage已经精确撤销：自身目录/状态目录消失、guard结束、gate和QoS模块消失、WAN/mwan3及两物理队列恢复。11:51最终原完整audit source{audit['queryAge']:.2f}秒、native selectors2通过，保护配置/服务epoch/五WAN健康保持、ECM关闭全零；wan/lan4原mq＋四fq_codel的所有选项和handle精确一致。CS2、controller、guard零残留；Steam恢复为可用暂停状态。

v20受控三流跨WAN、五WAN队列映射、DOWN18共享借用、UP60每WAN12硬上限、RT prio0/FQ-CoDel及NSS128历史CPU证据继续复用。本轮只有新的正常入口准备/准入结果，不是多WAN数据面失败，也不是正常程序NSS验收通过。剩余具体边界是checkpoint后选择到owner准入间的正常下载资格变化；本轮不放宽准入、不盲重试，不增加tap或新的验收条件。后续只处理已证实影响正常入口的这一步，并先保证恢复启动不会突破下载窗口；五WAN同时fast path、长期/永久运行和其它高级支线继续留后续，heartbeat保持暂停。

证据：[入口资格](../evidence/v34-normal-entry-qualification.json)、[13模型](../evidence/v34-prepared-selection-model.json)、[实际准入拒绝](../evidence/v34-admission-refusal.json)、[客户端/HUD](../evidence/v34-client-window.json)、[终态](../evidence/v34-normal-restoration.json)、[源码保存](../evidence/v34-normal-source-proof.json)。
'''
with (repo / 'docs/NORMAL_ADMISSION_2026-10-07.md').open('x', encoding='utf8') as f:
    f.write(report)
head = f'''# checkpoint 后三流选择通过；owner 最终准入拒绝，已完整恢复

更新：北京时间{stamp}。v34实际Cache死斗＋已有Hades临时32Mbps，自动分类1CS2 RT/11Steam BULK/1跨WAN三流。准备native后才冻结TCP/WAN，新checkpoint下载SHA/gzip及后续BULK/RT/BULK选择通过；独立owner/暂存/物理QoS实际执行，但首次owner准入报`Selected class is not admitted`。gate模块未加载、ECM未放行、NSS B段和正常程序factory未验收。

13新顺序模型/2762绑定/61依赖通过，18＋14历史模型和v20数据面保持。最后PC帧是checkpoint后选择，不是失败时owner分类；owner完整失败帧缺失，具体slot/改类原因未知，不能推成CT退出或固件故障。原失败、checkpoint/守护/来源按字节保存，旧v33及全部历史code/evidence不改。

11:51完整audit source{audit['queryAge']:.2f}/selectors2、五WAN健康/保护配置/epoch保持、ECM关闭全零；两物理原mq＋四fq_codel全部选项/handle恢复、stage/state/模块及实验进程零残留。原180客户端guard自然退出；Steam后来手动恢复，下载48%暂停0bps、原限速OFF/数字清空。重开又自动续传，累计严格180秒/720MB不成立。

软件HUD可见ping15/loss上下0、绿色网络图；数值jitter/Miss/真人体感未知。v20三流多WAN、高级QoS及历史CPU证据复用；下一步只解决已证实的正常下载选择到owner准入边界，并封住恢复启动的下载窗口。当前不放宽准入、不盲重试/扩五流，heartbeat保持暂停。

详情：[本轮报告](NORMAL_ADMISSION_2026-10-07.md)、[准入拒绝](../evidence/v34-admission-refusal.json)、[终态](../evidence/v34-normal-restoration.json)、[源码](../evidence/v34-normal-source-proof.json)。

## 以下保留原正常入口及历史记录

'''
for rel in ['AGENTS.md', 'docs/STATE.md', 'docs/PLAN.md', 'docs/EXPERIMENT_LOG.md']:
    p = repo / rel
    intro = head
    if rel == 'AGENTS.md':
        intro = intro.replace('(NORMAL_ADMISSION_2026-10-07.md)', '(docs/NORMAL_ADMISSION_2026-10-07.md)').replace('../evidence/', 'evidence/')
    p.write_bytes(intro.encode() + p.read_bytes())
p = repo / 'README.md'
p.write_bytes(('''# Athena NSS 多WAN / 高级QoS受控原型

三流跨WAN及五WAN队列/共享借用已经硬件证明。最新真实CS2＋Steam进入checkpoint后的三流选择和独立暂存，但owner最终分类准入拒绝，正常程序factory仍未验收。当前完整恢复、NSS关闭、下载暂停，见[STATE](docs/STATE.md)与[实际报告](docs/NORMAL_ADMISSION_2026-10-07.md)。

## 以下保留历史交付

''').encode() + p.read_bytes())
with (repo / '.gitattributes').open('a', encoding='utf8') as f:
    f.write('\n# Preserve exact frozen v34 source bytes; attributes apply only to new paths.\n')
    for rel in sources:
        if b'\r\n' in (w / rel).read_bytes():
            f.write('/code/' + rel + ' whitespace=cr-at-eol\n')
    f.write('/code/work/v34-normal/fast-path.lua whitespace=cr-at-eol,-blank-at-eol\n')
assert not git('diff', '--name-only', base, '--', 'code', 'evidence')
assert all(sha((repo / n).read_bytes()) == digest for n, digest in old_bytes.items())
print(json.dumps({'passed': True, 'newSources': len(sources), 'sourceHashes': len(manifest['sources']),
    'oldCodeEvidenceBlobsPreserved': len(old), 'actualRuntimeBindingsExact': len(bindings),
    'privateInputCopiesExact': len(private_hashes), 'actualIndependentStageStarted': True,
    'ecmLearningOpened': False, 'clientUiSettingsRestored': True, 'normalFactoryHardwareAcceptance': False}))
