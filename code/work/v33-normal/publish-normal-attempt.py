"""Publish the actual pre-checkpoint refusal and separately proved restoration."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import copy, hashlib, json, subprocess

w = Path(__file__).resolve().parents[2]
repo = w / 'athena-nss-mainline'
r = w / 'work/v33-normal'
base = '25c63eed990ead33e0e3dd773b701640008832d9'
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
assert len(old) == 4534
old_bytes = {n: sha((repo / n).read_bytes()) for n in old}
manifest = read(repo / 'source-manifest.json')
prefix = copy.deepcopy(manifest['sources'])
assert len(prefix) == 3993
q = read(r / 'entry-qualified.json')
prep = read(r / 'prepare-receipt.json')
case = r / 'session-20261007025747-bf198fc4'
run = w / read(r / 'active-run-private.json')['directory']
closure = w / read(r / 'closure-pointer.json')['directory']
ui = read(r / 'client-ui-restored.json')
clients = read(closure / 'client-closure.json')
audit = read(r / 'v33-final-audit.json')
physical = read(closure / 'physical-final.json')
refusal = read(r / 'refusal-diagnosis.json')
local = read(r / 'local-refusal-summary.json')
process = read(run / 'controller-process.json')
result = read(case / 'result.json')
baseline = read(case / 'baseline-audit.json')
load = read(r / 'load-readiness-private/controlled-candidates-private.json')
download = read(r / 'download-resume-observed.json')
guard = read(closure / 'result.json')
bindings = read(case / 'source-manifest-preaudit.json')
assert q['passed'] and q['inheritedBindings'] == 2687
assert len(q['sourceManifest']) == 36 and len(bindings) == 2723
assert q['relativeDependenciesExist'] == 57 and q['noModelsReplayed']
assert q['unchangedDataPlaneAndImmutableCandidatePolicy'] and q['unchangedV31PreStageSelection']
assert not q['hardwareExecuted'] and not q['wholeFactoryModeled']
for name, digest in bindings.items():
    assert sha((w / name).read_bytes()) == digest, name
    assert sha((case / 'frozen' / name).read_bytes()) == digest, name
for name, digest in q['sourceManifest'].items():
    assert bindings[name] == digest and sha((w / name).read_bytes()) == digest, name
for name, digest in prep['oldHashes'].items():
    assert sha((w / name).read_bytes()) == digest, name
assert process['exitCode'] == 1 and process['error'] is None
error = 'AssertionError [ERR_ASSERTION]: Exact controlled socket pair changed before staging'
assert read(case / 'controller-error.json')['error'] == error
assert not result['passed'] and result['errors'] == [error]
assert refusal['selectedStillEligible'] == {'tcp': False, 'udp': True, 'tcp2': False}
assert refusal['sameWanOriginalGameAlternatives'] == 0
assert not any(refusal[k] for k in ('checkpointCreated', 'detachedStageStarted', 'nssStarted'))
assert not any(p.name.startswith(('stage-', 'pilot-aba-')) for p in case.iterdir())
assert local['passed'] and local['localFrozenInputOnly']
assert local['originalTcpSocketsStillOwned'] == {'tcp': True, 'tcp2': True}
assert local['originalWanSlotAlternatives'] == 0 and local['otherWanSlotAlternatives'] == 1
assert local['networkReads'] == local['routerWrites'] == 0
assert len(load['game']) == 1 and len(load['bulk']) == 9 and len(load['pairs']) == 1
assert download['gameConnectedBeforeDownload'] and download['guardReadyBeforeDownload']
assert not download['clientDeadlineReset'] and download['temporaryLimitKbps'] == 32000
assert baseline['configurationMatches'] and all(baseline['checks'].values())
assert clients['passed'] and clients['naturalTimedExitPassed'] and clients['deadlineSeconds'] == 180
assert clients['readyBeforeDownload'] and clients['guardProcessGone']
assert clients['ownedTestProcessesRemaining'] == clients['cs2ProcessesRemaining'] == 0
assert clients['fullControllerSessionStarted'] and not clients['cancelledAfterClientRestore']
assert guard['passed'] and guard['timedExitExecuted'] and not guard['originalClientUiRestored']
assert ui['passed'] and ui['downloadPaused'] and ui['downloadProgressPercent'] == 30
assert ui['networkBps'] == ui['diskBps'] == 0
assert not ui['downloadLimitEnabled'] and ui['downloadLimitValueClearedBeforeDisable']
assert ui['downloadRegionUnchanged'] and ui['bitsDisplayUnchanged']
assert ui['allowDownloadsDuringGameplayUnchanged'] and not ui['strictCumulativeDownloadDurationProven']
assert audit['passed'] and audit['queryAge'] < 6 and audit['ecmClosedAndZero']
assert audit['protectedConfigurationUnchanged'] and audit['serviceEpochPinned']
assert audit['allFiveHealthyWanBaseline'] and audit['exactOwnedNativeAudit']
assert physical['passed'] and physical['defaultQueueOptionsAndHandlesExact']

# Originals are retained; this new directory seals the actual inputs again by byte hash.
sealed = closure / 'sealed-attempt-inputs'
sealed.mkdir()
inputs = [r / n for n in (
    'client-before-observed.json', 'game-connected-observed.json',
    'download-resume-observed.json', 'controller-window-check.json',
    'client-ui-restored.json', 'refusal-diagnosis.json', 'local-refusal-summary.json',
    'one-session-attempt.json', 'active-run-private.json')]
inputs += [case / n for n in ('controller-error.json', 'result.json',
    'persistent-selection-private.json', 'source-manifest-preaudit.json')]
inputs += [run / n for n in ('controller-process.json', 'controller-stdout-private.txt',
    'controller-stderr-private.txt')]
frame_names = ('controlled-candidates-private.json', 'controlled-pc-raw-private.json',
    'normal-reader-process-private.json', 'pc-app-endpoints-private.json',
    'real-candidates-private.json', 'real-candidates-raw-private.json', 'real-reader-qualified.json')
inputs += [case / ('refusal-' + n) for n in frame_names]
inputs += [r / 'load-readiness-private' / n for n in frame_names]
assert len(inputs) == 30
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

sources = [*q['sourceManifest'], 'work/v33-normal/entry-qualified.json',
    'work/v33-normal/prepare-receipt.json', 'work/v33-normal/read-final-health.mjs',
    'work/v33-normal/read-physical-final.mjs', 'work/v33-normal/capture-client-closure.ps1',
    'work/v33-normal/diagnose-refusal.mjs', 'work/v33-normal/local-refusal-summary.mjs',
    'work/v33-normal/publish-normal-attempt.py']
assert len(sources) == len(set(sources)) == 44
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
        'sha256': sha(data), 'bytes': len(data),
        'role': 'actual-normal-application-precheckpoint-refusal-and-restoration'})
manifest['lastNormalApplicationAttemptExport'] = 'V33_ACTUAL_NORMAL_PRECHECKPOINT_REFUSAL'
(repo / 'source-manifest.json').write_text(dump(manifest), encoding='utf8')
def evidence(name, value):
    new_json(repo / 'evidence' / name, value)

evidence('v33-normal-entry-qualification.json', q)
public_refusal = copy.deepcopy(refusal)
public_refusal.pop('controllerCase')
public_refusal.update({'controllerFactoryInvoked': True, 'controllerExitCode': 1,
    'refusalMessage': error, 'loadBeforeController': {'actualCs2Rt': 1,
        'actualSteamBulk': 9, 'eligibleMultiWanTriples': 1},
    'localFrozenFrameComparison': local,
    'normalApplicationFactoryAcceptance': False,
    'classifierClassChangeCauseEstablished': False})
evidence('v33-normal-refusal.json', public_refusal)
evidence('v33-client-window.json', {
    'passedAsObservation': True, 'actualCs2DeathmatchConnectedBeforeDownload': True,
    'mapDuringWindow': 'Mirage', 'downloadTemporaryLimitKbps': 32000,
    'downloadSpeedObservedMbps': [32.9, 32.0],
    'guardReadyBeforeDownload': True, 'clientDeadlineSeconds': 180,
    'clientDeadlineReset': False, 'guardNaturalExactApplicationExitPassed': True,
    'guardExitObservedAt': guard['observedAt'],
    'hudSamples': [
        {'phase': 'software', 'roundTimeShown': '9:50', 'pingMsShown': 15,
         'lossDownPercentShown': 0.0, 'lossUpPercentShown': 0.0,
         'jitterChartsGreenObserved': True, 'numericJitterMeasuredMs': None,
         'missValueObserved': False},
        {'phase': 'software', 'roundTimeShown': '8:53', 'deathScreen': True,
         'pingMsShown': None, 'lossDownPercentShown': None,
         'lossUpPercentShown': None, 'missValueObserved': False},
        {'phase': 'software', 'roundTimeShown': '8:23', 'pingMsShown': 15,
         'lossDownPercentShown': 0.0, 'lossUpPercentShown': 0.0,
         'jitterChartsGreenObserved': True, 'numericJitterMeasuredMs': None,
         'missValueObserved': False}],
    'hudIsNssPhaseEvidence': False, 'subjectiveHumanExperienceAccepted': False,
    'startupAndRecoveryAutomaticDownloadResumptionObserved': True,
    'strictCumulative180SecondDownloadProofAvailable': False,
    'currentUiRestoration': ui,
    'fullNssFactoryAcceptance': False})
evidence('v33-normal-restoration.json', {'passed': True, 'readonlyRouterAudit': True,
    'fullAudit': audit, 'physicalQueues': physical, 'controllerBaselineRestoration': baseline,
    'clientProcessClosure': clients, 'clientUiSettingsRestoreConfirmed': True,
    'testDownloadPaused': True, 'originalDownloadLimitDisabled': True,
    'noRouterConfigurationWrites': True, 'newCheckpointStageOrNss': False,
    'normalFactoryHardwareAcceptance': False, 'humanExperienceAcceptance': False,
    'newCpuAcceptance': False, 'permanentNssDeployment': False,
    'noNewEndpointOrFixtureStarted': True,
    'strictCumulativeDownloadDurationNotProven': True,
    'originalGuardDidNotRestoreUi': True, 'laterManualUiRestorationProvedSeparately': True})
evidence('v33-normal-source-proof.json', {'passed': True, 'baseCommit': base,
    'historicPrefixSources': len(prefix),
    'historicPrefixCanonicalSha256': sha(json.dumps(prefix, sort_keys=True, separators=(',', ':')).encode()),
    'sourceHashes': hashes, 'oldCodeAndEvidenceBlobsChecked': len(old),
    'oldCodeAndEvidenceUnmodified': True, 'qualificationSourceCopiesExact': 36,
    'actualRuntimeBindingCopiesExact': len(bindings), 'privateInputsCopiedExact': len(private_hashes),
    'entryBindings': 2723, 'selectorModelsReused': 18, 'actualRefusalModelsReused': 14,
    'modelsReplayed': False, 'normalFactoryHardwareAcceptance': False,
    'currentSteamUiSettingsRestoreConfirmed': True,
    'previousV32AndV31DeadlineFailuresAndUiEvidenceUnmodified': True,
    'rawCtNoncesCredentialsConfigurationsCheckpointsBinariesAndProcessCommandLinesExcluded': True,
    'firstWindowDeadlineAndFailuresPreserved': True})

stamp = datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
report = f'''# 正常程序三流已识别；控制器在 NSS 写入前安全拒绝

更新：北京时间 {stamp}。v33已实际进入Mirage死斗，同时恢复已有Hades下载，约32Mbps。自动分类识别1条CS2 RT、9条Steam BULK及一组跨WAN三流，完整控制器确实被调用。**准备期间两条已选TCP不再合格，控制器在checkpoint、stage和ECM之前拒绝；普通应用NSS验收仍未通过。**

## 实际结果

| 项目 | 观察与结论 |
| --- | --- |
| 真实游戏与下载 | 游戏先连接，再启动新的独立180秒客户端守护、恢复限速32000Kbps的已有下载；原窗口未重置。没有购买、启动Hades或新增其它下载 |
| 自动分类 | 负载就绪帧1个实际CS2 RT、9个Steam BULK、一组两TCP不同WAN的三流；源与程序socket归属保留本地 |
| 控制器 | 退出1，原错误为 `Exact controlled socket pair changed before staging`。checkpoint、detached owner、stage、NSS模块和ECM均未开始，原失败/完整输入/2723绑定源码保存 |
| 原连接状态 | 拒绝帧中原UDP仍合格，两条已选TCP不合格；两条对应socket仍在Steam库存。原WAN槽合格替代0组，其它WAN槽有1组。这不能证明原CT退出、改类根因或NSS/固件故障，也不授权改已冻结WAN范围 |
| HUD | 软件阶段9:50和8:23见ping15ms、上/下loss0%，jitter图绿色。8:53死亡屏幕隐藏值保持未知。没有数值jitter、Miss值或真人体感确认；本次HUD不能作NSS B段游戏证明 |
| 客户端 | 原180秒守护自然执行精确应用退出，CS2/controller/guard零残留。守护到期时UI恢复尚未完成，后来手动重开Steam、暂停下载、清空32000并关闭限速，11:06视觉核实30%暂停、网络/磁盘0bps及原设置保持 |

Steam初次启动和手动重开恢复设置时都曾自动续传。这些片段没有累计时长测量，不能将守护退出写成严格180秒总下载证明。部分Hades内容留存且暂停；原失败、到期时UI未恢复及后来实际恢复分别保存。

## 最终恢复

11:01原完整只读audit通过：source1.24秒、native审核2 selectors，保护配置/服务epoch/五WAN健康保持，ECM关闭全零。11:02两物理wan/lan4的原mq＋四fq_codel全部选项和handle一致；客户端inventory证明CS2、controller、guard零残留。之后仅恢复Steam界面设置，没有router配置写入。

v33只改新目录引用和本次11:30截止；数据面、分类阈值及v31的选择合同保持。2687＋36＝2723绑定、57相对依赖/语法通过，18选择模型与14实际拒绝模型复用未重跑，完整factory没有在模型或硬件完成。本次30份实际输入按字节另存；资格36份及实际runtime2723绑定逐字节验证。v32/v31和全部旧code/evidence保持。

## 剩余边界

已成立的v20三流多WAN、五WAN队列映射、DOWN18共享借用、UP60每WAN12硬上限、RT prio0/FQ-CoDel硬件结论与历史CPU证据继续复用。正常下载TCP候选在准备期间变化，是当前正常入口仍未验收的具体边界；没有依据放宽准入、强行固定原TCP、改已冻结WAN范围或盲重试。本轮停止新生产实验；后续只处理有证据支持的正常入口准备顺序，再用新目录进行一次有限实际会话。五WAN同时fast path、长期常驻、更多故障/CPU/WiFi/ECN测试留后续，heartbeat继续暂停。

证据：[入口资格](../evidence/v33-normal-entry-qualification.json)、[实际拒绝](../evidence/v33-normal-refusal.json)、[客户端与HUD](../evidence/v33-client-window.json)、[终态](../evidence/v33-normal-restoration.json)、[源码保存](../evidence/v33-normal-source-proof.json)。
'''
with (repo / 'docs/NORMAL_ATTEMPT_2026-10-07.md').open('x', encoding='utf8') as f:
    f.write(report)
head = f'''# 正常程序已识别三流；NSS 写前拒绝，恢复通过

更新：北京时间{stamp}。v33实际Mirage死斗＋已有Hades约32Mbps，自动分类1CS2 RT/9Steam BULK/1跨WAN三流，完整控制器已调用。准备期间两条选中TCP不再合格，checkpoint/stage/模块/ECM前拒绝，普通应用NSS factory验收仍未完成。

失败帧保留：原UDP仍合格，两条TCP socket仍由Steam持有；原WAN槽合格替代0组，其它WAN槽1组。缺失合格候选不当CT退出或NSS故障，不能用新WAN替换已冻结参数。2723绑定/57依赖通过，18＋14模型复用未重跑；数据面与选择合同不变，旧v32/v31截止/源码/失败保持。

11:01原完整audit source1.24/native selectors2、五WAN健康/保护配置/epoch保持、ECM关闭全零；11:02两物理原mq＋四fq_codel全部选项/handle一致。原180秒客户端守护自然退出，CS2/controller/guard0；11:06手动恢复Steam原限速OFF/空数字、下载30%暂停0bps。初次启动和恢复重开曾自动续传，累计下载期限未测，不宣称严格180秒总量/时长。

软件HUD见ping15/loss上下0，数值jitter/Miss/真人体感未知，没有NSS B段。v20三流多WAN及高级QoS硬件和历史CPU继续复用；当前正常入口TCP在准备期间失去资格是具体未验边界，不放宽准入、不盲重试或扩五流。本轮停止新增生产实验，后续只修有证据支持的正常入口准备顺序，heartbeat保持暂停。

详情：[本轮报告](NORMAL_ATTEMPT_2026-10-07.md)、[实际拒绝](../evidence/v33-normal-refusal.json)、[终态](../evidence/v33-normal-restoration.json)、[源码](../evidence/v33-normal-source-proof.json)。

## 以下保留原正常入口与夜间记录

'''
for rel in ('AGENTS.md', 'docs/STATE.md', 'docs/PLAN.md', 'docs/EXPERIMENT_LOG.md'):
    p = repo / rel
    intro = head
    if rel == 'AGENTS.md':
        intro = intro.replace('(NORMAL_ATTEMPT_2026-10-07.md)', '(docs/NORMAL_ATTEMPT_2026-10-07.md)').replace('../evidence/', 'evidence/')
    p.write_bytes(intro.encode() + p.read_bytes())
p = repo / 'README.md'
p.write_bytes(('''# Athena NSS 多WAN / 高级QoS受控原型

三流跨WAN及五WAN队列/共享借用已在硬件证明。最新实际CS2＋Steam已配齐三流，但准备期间TCP不再合格，NSS写前安全拒绝，普通应用factory仍未验收。当前NSS关闭、下载暂停、原设置已恢复，见[STATE](docs/STATE.md)与[实际报告](docs/NORMAL_ATTEMPT_2026-10-07.md)。

## 以下保留历史交付

''').encode() + p.read_bytes())
with (repo / '.gitattributes').open('a', encoding='utf8') as f:
    f.write('\n# Preserve exact v33 Windows source bytes and inherited Lua whitespace.\n')
    for rel in sources:
        if b'\r\n' in (w / rel).read_bytes():
            f.write('/code/' + rel + ' whitespace=cr-at-eol\n')
    f.write('/code/work/v33-normal/fast-path.lua whitespace=cr-at-eol,-blank-at-eol\n')
assert not git('diff', '--name-only', base, '--', 'code', 'evidence')
assert all(sha((repo / n).read_bytes()) == digest for n, digest in old_bytes.items())
print(json.dumps({'passed': True, 'newSources': len(sources),
    'sourceHashes': len(manifest['sources']), 'oldCodeEvidenceBlobsPreserved': len(old),
    'actualRuntimeBindingsExact': len(bindings), 'privateInputCopiesExact': len(private_hashes),
    'controllerAttemptedAndRefusedBeforeNss': True, 'clientUiSettingsRestored': True,
    'normalFactoryHardwareAcceptance': False}))
