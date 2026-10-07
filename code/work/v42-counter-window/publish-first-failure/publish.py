from pathlib import Path
from datetime import datetime, timezone, timedelta
import copy, gzip, hashlib, json, subprocess

w = Path(__file__).resolve().parents[2]
repo = w / 'athena-nss-mainline'
root = w / 'work/v42-counter-window'
base = '4c873669cc05799a444f8462217a17e42516b2d9'
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha = lambda b: hashlib.sha256(b).hexdigest()
dump = lambda v: json.dumps(v, ensure_ascii=False, indent=2) + '\n'
git = lambda *a: subprocess.check_output(['git', '-C', str(repo), *a])

def new(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x', encoding='utf8') as f:
        f.write(dump(value))

assert git('rev-parse', 'HEAD').decode().strip() == base
assert not git('status', '--porcelain')
manifest = read(repo / 'source-manifest.json')
prefix = copy.deepcopy(manifest['sources'])
assert len(prefix) == 4480
old = {}
old_bytes = {}
for row in git('ls-tree', '-r', '-z', base, '--', 'code', 'evidence').split(b'\0'):
    if row:
        header, name = row.split(b'\t'); old[name.decode()] = header.decode().split()[2]
        old_bytes[name.decode()] = sha((repo / name.decode()).read_bytes())
assert len(old) == 5055

pilot = w / read(root / 'pilot-reference-private.json')['directory']
case = w / read(pilot / 'case-reference-private.json')['dir']
closure = w / read(root / 'closure-pointer.json')['directory']
endpoint_dir = w / read(root / 'endpoint-readonly-recheck-pointer.json')['directory']
hardware = read(root / 'hardware-descriptive.json')
audit = read(root / 'v42-final-audit.json')
physical = read(closure / 'physical-final.json')
clients = read(closure / 'client-closure.json')
endpoint = read(endpoint_dir / 'summary.json')
record = read(case / 'last-record-private.json')
assert hardware['passed'] and hardware['fiveWanBoundedHardwareAcceptance']
assert hardware['rtEchoDuringInteriorB']['unreturned'] == 0 and hardware['rtLeafDrop'] == {'down': 0, 'up': 0}
assert hardware['wanSet'] == [1, 2, 3, 4, 5] and hardware['renewals'] == 20
assert 'terminalStateRead' not in record and 'terminalInvalidation' not in record
assert record['qosRestored'] and record['qosModuleUnloaded']
assert audit['passed'] and audit['queryAge'] < 6 and audit['ecmClosedAndZero']
assert audit['protectedConfigurationUnchanged'] and audit['allFiveHealthyWanBaseline']
assert physical['passed'] and physical['defaultQueueOptionsAndHandlesExact']
assert clients['passed'] and clients['ownedTestProcessesRemaining'] == 0
assert endpoint['passed'] and endpoint['readonly'] and endpoint['ownedRulesRemaining'] == 0
assert endpoint['baselineRestored'] and endpoint['exactOwnedEndpointClosed']
assert read(pilot / 'automatic-result.json')['passed'] and read(case / 'result.json')['passed']
failed_close = read(pilot / 'endpoint-closure-error-private.json')
events = read(pilot / 'driver-private.json')
assert events[-1]['file'].endswith('/close-endpoint.mjs') and events[-1]['code'] == 1
assert 'Owned SSH transport closed 255' in events[-1]['stderr'] and 'timed out' in events[-1]['stderr']
assert not events[-1]['stdout']
checkpoint = read(case / 'stage-checkpoint-verified.json')
checkpoint_bytes = (case / 'stage-checkpoint-config-private.tar.gz').read_bytes()
assert checkpoint['gzipVerified'] and sha(checkpoint_bytes) == checkpoint['sha256']
gzip.decompress(checkpoint_bytes)
plan = read(case / 'stage-plan-private.json')
assert plan['qosCodeBytes'] == 73138 < 73728 and plan['execBytes'] == 8799 < 9000
assert hardware['nativeRecordBytes'] == 634752 < 1048576
detached = read(case / 'stage-detached-private.json')
assert detached['sameBoot'] and detached['identity']
bindings = read(pilot / 'actual-entry-bindings.json')
assert len(bindings) == 3354
for location in (pilot, case):
    local_bindings = read(location / ('actual-entry-bindings.json' if location == pilot else 'source-manifest-preaudit.json'))
    assert local_bindings == bindings
    for rel, digest in bindings.items():
        data = (w / rel).read_bytes()
        assert sha(data) == digest and (location / 'frozen' / rel).read_bytes() == data, rel
assert read(case / 'source-manifest.json') == bindings

q = read(root / 'entry-qualified.json')
private_analysis = {'work/v42-counter-window/analyze-v41-window.py', 'work/v42-counter-window/v41-aligned-window.json'}
sources = [p for p in q['sourceManifest'] if p not in private_analysis]
sources += ['work/v42-counter-window/' + n for n in ('prepare-receipt.json', 'entry-qualified.json',
             'recheck-endpoint-readonly.mjs', 'one-endpoint-readonly-recheck.json', 'analyze-hardware.py',
             'local-read-path-failures.json', 'publish.py')]
# The full qualification document contains hashes and relative source names only.
assert len(sources) == len(set(sources))
hashes = {}
for rel in sources:
    data = (w / rel).read_bytes(); hashes[rel] = sha(data)
    target = repo / 'code' / rel; target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('xb') as f:
        f.write(data)
    manifest['sources'].append({'path': 'code/' + rel, 'workspaceSource': rel, 'sha256': hashes[rel],
        'bytes': len(data), 'role': 'five-wan-sixty-second-owned-simulation-and-complete-restoration'})
assert manifest['sources'][:4480] == prefix
manifest['generatedAt'] = datetime.now(timezone.utc).isoformat()
manifest['lastFiveWanBoundedHardwareExport'] = 'V42_FIVE_WAN_SIMULATED_FUNCTIONAL_ACCEPTANCE_COMPLETE'
(repo / 'source-manifest.json').write_text(dump(manifest), encoding='utf8')

sealed = root / 'sealed-inputs-private'
sealed.mkdir()
inputs = {
 'record': case / 'last-record-private.json', 'selected': case / 'selected-private.json',
 'postCheckpointReceipt': case / 'post-checkpoint-controlled-receipt-private.json',
 'checkpoint': case / 'stage-checkpoint-config-private.tar.gz', 'checkpointVerification': case / 'stage-checkpoint-verified.json',
 'stagePlan': case / 'stage-plan-private.json', 'independentGuardian': case / 'stage-detached-private.json',
 'controllerResult': case / 'result.json', 'baselineAudit': case / 'baseline-audit.json',
 'before': case / 'before-private.json', 'after': case / 'after-private.json',
 'actualBindings': pilot / 'actual-entry-bindings.json', 'supervisorEvents': pilot / 'driver-private.json',
 'originalClosureFailure': pilot / 'endpoint-closure-error-private.json',
 'endpointRecheckRaw': endpoint_dir / 'raw-private.json', 'clientConfig': w / read(root / 'load-latest-private.json')['dir'] / 'client-config-private.json',
 'clientSamples': w / read(root / 'load-latest-private.json')['dir'] / 'load-samples-private.jsonl',
 'udpSamples': w / read(root / 'load-latest-private.json')['dir'] / 'udp-samples-private.jsonl',
 'clientResult': w / read(root / 'load-latest-private.json')['dir'] / 'result-private.json',
 'clientGuard': w / read(root / 'load-latest-private.json')['dir'] / 'guard-result-private.json',
 'physicalRaw': closure / 'physical-final-raw-private.json', 'processInventory': closure / 'owned-process-inventory-private.json'
}
input_hashes = {}
for label, p in inputs.items():
    data = p.read_bytes(); input_hashes[label] = sha(data)
    with (sealed / (label + '.private')).open('xb') as f:
        f.write(data)
    assert (sealed / (label + '.private')).read_bytes() == data
new(sealed / 'manifest-private.json', input_hashes)

public_hw = copy.deepcopy(hardware)
public_hw['encodedBundleBytes'] = plan['qosCodeBytes']
public_hw['guardianExecBytes'] = plan['execBytes']
public_hw['diagnosticTerminalReadExecuted'] = False
public_hw['v41ClassificationRetirementNotReproducedThisRun'] = True
public_hw['v41GapFixedClaimed'] = False
public_hw['supervisorClosureTransportFailed'] = True
public_hw['closureReadonlyRecheckPassed'] = True
new(repo / 'evidence/v42-five-wan-hardware.json', public_hw)
aligned = read(root / 'v41-aligned-window.json')
old_input_hashes = aligned.pop('inputSha256')
assert len(old_input_hashes) == 3
aligned['inputSha256ByRole'] = dict(zip(('postCheckpointReceipt', 'lastRecord', 'clientSamples'), old_input_hashes.values()))
new(repo / 'evidence/v42-v41-window-alignment.json', aligned)
new(repo / 'evidence/v42-five-wan-restoration.json', {'passed': True, 'finalFullAudit': audit, 'physicalQueues': physical,
    'clientClosure': clients, 'endpointReadonlyRecheck': endpoint, 'originalNssRecoveryFlags': hardware['originalRecoveryFlags'],
    'qosRestored': record['qosRestored'], 'qosModuleUnloaded': record['qosModuleUnloaded'],
    'originalSupervisorExitCode': 1, 'originalClosureFailureCategory': 'SSH_CONNECT_TIMEOUT_BEFORE_REMOTE_COMMAND',
    'originalFailurePreserved': True, 'readonlyRecheckAttempts': 1,
    'checkpointDownloadedShaGzipVerifiedBeforeWrite': True, 'independentGuardianBeforeWriteVerified': True,
    'cs2OrSteamOperated': False, 'userApplicationsNotClosedByFixtureCleanup': True, 'heartbeatStillPaused': True,
    'permanentNssDeployment': False, 'newCpuAcceptance': False})
new(repo / 'evidence/v42-five-wan-qualification.json', {'passed': True, 'hardwareExecutedAtQualification': False,
    'actualBindings': 3354, 'qualifiedSources': len(q['sourceManifest']), 'sourceManifest': {p: h for p, h in q['sourceManifest'].items() if p not in private_analysis},
    'twoOfflineAnalysisFilesKeptLocalToExcludePrivateRunPaths': True,
    'dataPlaneAndClassifierPolicyUnchanged': True, 'fastPathOnlyAddsReadTimingAndProtectedTerminalRead': True,
    'terminalReadMaximumExtraReads': 1, 'terminalReadAfterStopNewLearning': True, 'terminalBranchHardwareExecuted': False,
    'sourceSeconds': 6, 'clientSeconds': 180, 'fixtureGuardSeconds': 210, 'phaseSeconds': 60,
    'combinedTcpMbps': 32, 'combinedCreditBytes': 65536,
    'nativeRuntimeSha256': q['nativeRuntimeSha256'], 'priorNativeControlChecksReused': q['priorNativeControlChecksReused'],
    'priorNativeCtChecksReused': q['priorNativeCtChecksReused'], 'priorTargetRamChecksReused': q['priorTargetRamChecksReused']})
new(repo / 'evidence/v42-five-wan-source-proof.json', {'passed': True, 'baseCommit': base, 'historicPrefixSources': 4480,
    'sourceHashes': hashes, 'oldCodeAndEvidenceBlobsChecked': len(old), 'oldCodeAndEvidenceUnmodified': True,
    'actualRuntimeBindingsFrozenExact': 3354, 'pilotAndCaseBindingsAndFrozenCopiesExact': True,
    'privateInputsCopiedExact': len(input_hashes), 'frozenV41FailureAndAllHistoricSourcesPreserved': True,
    'privateOnlyOfflineAnalysisFilesExcludedFromCode': 2,
    'rawCtNoncesCredentialsConfigsCheckpointsBinariesAndCommandLinesExcluded': True})

stamp = datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
udp = hardware['rtEchoDuringInteriorB']
rates = hardware['bulkDownMbps']
report = f'''# 五 WAN 模拟功能验收完成

更新：北京时间 {stamp}。**自有四条 TCP BULK 和一条模拟 UDP RT 在五个不同 WAN 同时进入 NSS，并完成一次有界 60.01 秒窗口、121 次 ECM5 采样和 20 次续租。** 双向十 tag / bulk、RT leaf / 完整 ct mark / NAT / WAN affinity 及软件恢复通过。本轮没有操作 CS2 或 Steam。

## 实际数据与高级 QoS

实际分配：TCP WAN2、TCP2 WAN3、TCP3 WAN4、TCP4 WAN5，UDP WAN1。所有新连接仍由 Linux PBR 自然分配，冻结后没有替换 WAN、tuple、CT 或 tag。实际五槽 native 与 v24 相同，准入来自原 NSS68 永久自动分类器，BULK 2000 Kbps 门槛、RT 预算和 source6 / kernel90最大120 / owner180 / client180 期限没有放宽。

五 WAN 上下行各18 class / 11 leaf、RT prio0 / FQ-CoDel 的原硬件队列合同保持。共享下行18 Mbps，四条 TCP 的附近异步 leaf 窗口约 {rates['tcp']:.2f}/{rates['tcp2']:.2f}/{rates['tcp3']:.2f}/{rates['tcp4']:.2f} Mbps，合计 {hardware['bulkAggregateMbps']:.2f} Mbps；超过各 WAN 3 Mbps 保证份额的共享借用已观察到。上行共享60 Mbps、每WAN12 Mbps硬上限的实际配置和 native 选项已验证，未宣称本轮分别压满五WAN上行或长期公平性。

约 {udp['interiorSeconds']:.2f} 秒的保守内部窗口发出 {udp['sent']} 个认证 UDP echo，{udp['returned']} 个在整份 fixture 中返回，未返回0；跨设备映射不确定性约 {udp['offsetUncertaintySeconds']:.2f} 秒，窗口边缘各排除1秒。RTT中位/P95/P99约 {udp['rttMedianMs']:.2f}/{udp['rttP95Ms']:.2f}/{udp['rttP99Ms']:.2f} ms，P95减中位约 {udp['rttP95MinusMedianMs']:.2f} ms，RT上下 leaf 零drop。这是自有海外服务器的模拟包测量，不是 CS2 HUD jitter/Miss、真人体验或新CPU收益。

## v41 异常的有限判断

先对齐已有 v41 记录：query1767→1768的finished窗口为3.01秒，PC时钟区间不确定性0.82秒，原四个socket/进程实例未变；客户端stdout交付的保守速率下限约2.57/2.31/3.44/2.48 Mbps，而原完整分类帧为BE/cooldown、1.51–1.69 Mbps。进一步排除两次CT读取时段后，三条流的保守下限仍高于2000 Kbps，另一条不足以作此判断。SSH管道缓冲未被pacer credit限制证明，因此没有把这些数值当作精确线速或已证实的固件同步根因。

本次只在既有fast path增加初始ECM读时间，以及停止新学习后、撤销前最多一次受保护的现有ECM状态读取；没有增加tap、抓包、分类器安装或阈值调整。完整60秒内没有再次触发v41改类，终止诊断分支未执行，原分类/改类拒绝和恢复规则保持。

**v41原失败未删除、未称已修复；本次未复现使其不再阻止这次有界五WAN模拟功能验收。** 它保留为已知限制：五流进入NSS时曾发生BULK→BE/cooldown提前退出，准确根因与长期发生频率未知；原控制器会拒绝续租并结束旧代。一次60秒成功不能证明长期可靠性，永久常驻推广仍需后续证据。没有为追求完整根因继续开启轮次。

## 写前安全与完整恢复

3354实际绑定及pilot/控制器完整源码副本逐字节冻结，历史五槽63控制/68CT/14RAM与CPU证据复用，未重做旧准备。新checkpoint已下载、SHA/gzip核验，控制连接外独立恢复在写前证明。实际bundle73138 / guardian exec8799 / 记录634752字节，均在原73728/9000/1MiB上限内。

NSS控制器正常结束并恢复，原完整baseline检查通过。随后监督器的端点关闭SSH连接超时，退出码1、原stderr和失败保留；没有远端关闭命令成功执行的证据。已过原独立端点最大期限后，只做一次新目录只读重查，确认精确服务MainPID0、端口45817/45818关闭、临时规则0、canonical FW基线一致。

最终完整审核source {audit['queryAge']:.2f} 秒 / selectors {audit['selectors']}，五WAN健康，原保护配置/服务epoch保持，ECM关闭全零、无实验gate/stage/state/模块。wan和lan4原mq＋四fq_codel全部选项/handle精确恢复，自有client/controller/guard/sender零残留。自有客户端独立提前退出证明通过；用户独立应用未被清理。常驻NSS68原config、heartbeat暂停，电源计划未改。

## 交付范围与后续

已完成的是**五 WAN 的五条精确流、一次60秒NSS维持及既有高级QoS共享预算的受控功能验收**。已有v38两WAN / v20多WAN与历史CPU证据保留。普通用户全网、永久NSS、长期运行、五WAN多流公平、不同应用负载和极端故障恢复尚未验收；WiFi、autorate、ECN仍在后续范围。本轮结束新增生产实验。

已知非阻塞问题进入后续清单：v41进入窗口分类计数差异；自有SSH连接偶发首包/控制连接超时；正常应用factory尚未验收。后续先复用已成立的核心证据，只有新问题明确影响选定使用目标时才继续修复或新开有界验证。

证据：[五WAN硬件](../evidence/v42-five-wan-hardware.json)、[终态和原SSH失败](../evidence/v42-five-wan-restoration.json)、[v41窗口对齐](../evidence/v42-v41-window-alignment.json)、[源码保存](../evidence/v42-five-wan-source-proof.json)、[v41原失败](FIVE_WAN_INITIAL_HIT_2026-10-07.md)。
'''
with (repo / 'docs/FIVE_WAN_SIMULATED_ACCEPTANCE_2026-10-07.md').open('x', encoding='utf8') as f:
    f.write(report)
intro = f'''# 五 WAN 模拟功能验收完成，完整恢复

更新：北京时间{stamp}。v42自有四TCP BULK＋模拟UDP RT自然走TCP WAN2/3/4/5＋UDP WAN1，实际NSS五流60.01秒/121采样ECM5/20续租、双向十tag/leaf/完整ct mark/NAT/affinity通过。共享DOWN18附近四bulk合计16.70Mbps，UP60每WAN12硬上限/RT prio0/FQ-CoDel保持；内部57.06秒2373 UDP全部回包、RT上下leaf零drop，RTT中位/P95/P99约196.47/198.68/200.36ms。不是CS2/HUD/真人、新CPU或长期常驻证明。

v41原BE/cooldown退出和全部旧证据不改。对齐后PC交付与分类计数有差异，但SSH缓冲/计时限制使精确同步根因仍未知；本次没有修改分类、没有复现该退出，最多一次终止计数读取分支未执行。该问题保留known limitation/follow-up，不妨碍本次有界功能验收，不称已修复。

3354实际绑定、fresh checkpoint SHA/gzip和原独立恢复写前通过，bundle73138/exec8799/record634752在原上限内。NSS正常完整恢复后，端点关闭SSH超时导致监督器退出1，原失败保留；原独立期限后一次仅只读新目录重查确认精确服务/端口关闭、规则0/FW基线一致。最后完整audit source1.12/selectors6，五WAN健康、保护配置/epoch/ECM关闭全零；两物理原mq＋四fq_codel全选项/handle、自有进程全部退出。常驻NSS68原config、heartbeat暂停，无CS2/Steam操作。

**五WAN五流60秒与高级QoS受控功能验收完成，本轮停止新增实验。** 已知v41进入窗计数差异/偶发SSH取得超时/普通应用factory未验收留后续；不将本次等同全网、永久或长期部署。详情：[本次报告](FIVE_WAN_SIMULATED_ACCEPTANCE_2026-10-07.md)。

## 以下保留历史记录

'''
for rel in ('AGENTS.md', 'docs/STATE.md', 'docs/PLAN.md', 'docs/EXPERIMENT_LOG.md'):
    p = repo / rel
    text = intro.replace('(FIVE_WAN_SIMULATED_ACCEPTANCE_2026-10-07.md)', '(docs/FIVE_WAN_SIMULATED_ACCEPTANCE_2026-10-07.md)') if rel == 'AGENTS.md' else intro
    p.write_bytes(text.encode() + p.read_bytes())
p = repo / 'README.md'
p.write_bytes(('''# Athena NSS 多WAN / 高级QoS受控原型

五WAN五条精确流已完成一次60秒NSS维持及高级QoS受控功能验收，并完整恢复。模拟UDP内部窗口2373包全部返回；这不代表全网、永久或长期部署。见[STATE](docs/STATE.md)、[本次报告](docs/FIVE_WAN_SIMULATED_ACCEPTANCE_2026-10-07.md)。

## 以下保留历史交付

''').encode() + p.read_bytes())
attrs = []
with (repo / '.gitattributes').open('a', encoding='utf8') as f:
    f.write('\n# Exact new bounded five-WAN diagnostic and original data-plane source bytes.\n')
    for rel in sources:
        if b'\r\n' in (w / rel).read_bytes():
            attrs.append('/code/' + rel + ' whitespace=cr-at-eol')
    attrs += ['/code/work/v42-counter-window/fast-path.lua whitespace=cr-at-eol,-blank-at-eol',
              '/code/work/v42-counter-window/endpoint-firewall-guardian.py whitespace=cr-at-eol,-blank-at-eof']
    for a in attrs:
        f.write(a + '\n')
new(repo / 'evidence/v42-frozen-whitespace.json', {'passedAsPreservedSourcePolicy': True,
    'exactPathAttributes': attrs, 'originalDataPlaneBytesPreservedExceptQualifiedReadOnlyRecordAddition': True,
    'noGlobalWhitespacePolicyChange': True})
assert not git('diff', '--name-only', base, '--', 'code', 'evidence')
assert all(sha((repo / n).read_bytes()) == h for n, h in old_bytes.items())
print(json.dumps({'passed': True, 'newSources': len(sources), 'sourceHashes': len(manifest['sources']),
    'historicBlobsPreserved': len(old), 'privateInputsCopiedExact': len(input_hashes),
    'fiveWanSixtySecondFunctionalAcceptance': True, 'originalClosureFailurePreserved': True, 'fullRestoration': True}))
