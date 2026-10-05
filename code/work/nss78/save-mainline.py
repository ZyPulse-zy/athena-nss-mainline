"""Export only the new read-only diagnostic and reviewed aggregate evidence."""
from pathlib import Path
import hashlib, json, shutil
from datetime import datetime, timezone

workspace = Path(__file__).resolve().parents[2]
local = workspace / 'work/nss78'
repo = workspace / 'athena-nss-mainline'
sha = lambda b: hashlib.sha256(b).hexdigest()
load = lambda p: json.loads(p.read_text(encoding='utf-8'))
def dump(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

summary = load(local / 'readiness-summary.json')
before = load(workspace / 'work/nss68/nss78-start-20261005-health.json')
after = load(workspace / 'work/nss68/nss78-after-timing-20261005-health.json')
readiness = load(workspace / 'work/nss77/real-session-readiness.json')
assert before['passed'] and after['passed'] and summary['ecmStoppedAndZero']
assert before['workerPid'] == after['workerPid'] == summary['workerPid']
assert before['guardianPid'] == after['guardianPid'] == summary['guardianPid']
assert readiness['actualGameCandidates'] == readiness['actualBulkCandidates'] == 0
assert not readiness['routerWrites'] and not readiness['nssPermissionGranted']
timeline = load(local / 'readiness-timing-private.json')
samples = timeline['samples']
assert len(samples) == summary['samples'] and len(samples) > 0
publications = list({s['sequence']: s for s in samples}.values())
intervals = [b['queryStarted']-a['queryStarted'] for a, b in zip(publications, publications[1:])]
assert sum(s['initialAgeEligible'] for s in samples) == summary['initialAgeEligible']

current_path = repo / 'evidence/current-runtime.json'
old = current_path.read_bytes()
assert load(current_path)['round'] == 'NSS77'
history = repo / 'evidence/nss77-runtime.json'
assert not history.exists(), 'Refuse to overwrite frozen history'
history.write_bytes(old)
manifest_path = repo / 'source-manifest.json'
manifest = load(manifest_path)
assert len(manifest['sources']) == 990
prefix_hash = sha(json.dumps(manifest['sources'], sort_keys=True, separators=(',', ':')).encode())
source_hashes = {}
for name in ['measure-readiness.mjs', 'save-mainline.py']:
    source = local / name
    destination = repo / 'code/work/nss78' / name
    destination.parent.mkdir(parents=True, exist_ok=True)
    assert not destination.exists()
    shutil.copyfile(source, destination)
    digest = sha(source.read_bytes())
    assert sha(destination.read_bytes()) == digest
    relative = f'work/nss78/{name}'
    source_hashes[relative] = digest
    manifest['sources'].append({'path': 'code/'+relative, 'workspaceSource': relative,
        'sha256': digest, 'bytes': source.stat().st_size, 'role': 'readonly-timing-diagnostic-no-admission'})
manifest['generatedAt'] = datetime.now(timezone.utc).isoformat()
manifest['lastAppendExport'] = 'NSS78'
dump(manifest_path, manifest)
dump(repo / 'evidence/nss78-source-proof.json', {'round': 'NSS78', 'sources': 2,
    'sourceHashes': source_hashes, 'historicPrefixSources': 990,
    'historicPrefixCanonicalSha256': prefix_hash, 'notAdditionalProductionAdmission': True,
    'privateConnectionAndCapturesExcluded': True, 'originalEntryBoundInputsUnchanged': 355})

audit_keys = ['passed', 'observedAt', 'readonly', 'configurationMatches', 'deploymentReference',
    'configSha256', 'workerPid', 'guardianPid', 'originalFullLockedAudit', 'selectors',
    'queryAge', 'sequence', 'ecmStoppedAndZero', 'noActiveTransaction', 'noStaging',
    'noExperimentState', 'noExperimentalModule', 'serviceEpochPinned', 'nssAdmissionAllowed']
safe_audit = {k: after[k] for k in audit_keys}
dump(repo / 'evidence/nss78-final-audit.json', safe_audit)
evidence = {'round': 'NSS78', 'observedAt': after['observedAt'],
    'hypothesis': 'The unchanged NSS77 initial source-age budget has observable windows in the current resident publication cadence.',
    'changes': {'routerConfigurationWrites': False, 'nssStage': False, 'ecmOpened': False,
        'productionQdiscWrites': False, 'permanentClassifierChanged': False, 'experimentalEntryChanged': False},
    'load': {'steamNetworkBpsAtUi': 0, 'steamDiskBpsAtUi': 0, 'pendingLargeSteamDownloadsAtUi': 0,
        'existingRdr2DownloadCompleted': True, 'cs2MenuVisible': True,
        'actualApplicationGameCandidates': 0, 'actualApplicationBulkCandidates': 0,
        'sameWanPairs': 0, 'trafficGenerated': False, 'highLoad': False},
    'timing': summary, 'queryIntervalsSeconds': intervals,
    'classificationFlowCounts': {'minimum': min(s['flowCount'] for s in samples),
        'maximum': max(s['flowCount'] for s in samples)},
    'interpretation': {'timingWindowsObservedAtLightLoad': True,
        'selectedPairAdmissionVerified': False, 'nss77LiveForwardingTested': False,
        'completeMatchedABACompleted': False, 'cpuOrSoftirqBenefitProved': False,
        'cs2JitterLossMissMeasured': False, 'highLoadBudgetProved': False,
        'jointFreshSamplesAreNotAdmission': True},
    'rollback': {'requiredForRouterMutation': False, 'reason': 'No router mutation was performed.',
        'newRollbackTestClaimed': False, 'originalFullAuditBeforeAndAfterPassed': True},
    'finalAudit': safe_audit, 'nextEntry': 'work/nss77/real-session.mjs', 'boundInputs': 355}
dump(repo / 'evidence/nss78-mainline.json', evidence)
dump(local / 'mainline-observations.json', evidence)
runtime = {'round': 'NSS78', 'checkedAt': after['observedAt'],
    'deploymentReference': after['deploymentReference'], 'classifierConfigSha256': after['configSha256'],
    'workerPid': after['workerPid'], 'guardianPid': after['guardianPid'],
    'publicationCandidateInstalled': True, 'permanentClassifierChangedThisTurn': False,
    'nssPermanentlyEnabled': False, 'nssOpenedThisTurn': False,
    'qualifiedExperimentalEntry': 'work/nss77/real-session.mjs', 'qualifiedExperimentalEntryBoundInputs': 355,
    'entryPreparationQualified': True, 'entryFullHighLoadForwardingQualified': False,
    'audit': safe_audit, 'finalClosure': {'passed': True},
    'completePerformanceAndGameAcceptance': False, 'requiresLiveRevalidation': True,
    'historical77RuntimePreservedSha256': sha(old),
    'currentRealApplicationPairVisible': False, 'clientDownloadNetworkBpsObserved': 0,
    'newClientDownloadStarted': False, 'clientHudChangedThisTurn': False,
    'previousTurnClientFinalRestoreStillUnproved': True}
dump(current_path, runtime)

state = '''# 当前状态

更新：2026-10-05 14:56，北京时间。最新记录为NSS78只读诊断；实验入口仍是NSS77，常驻仍NSS68。

**轻载下已直接观察到NSS77需要的准备时间窗口。当前Steam下载完成、CS2在菜单，没有真实同WAN连接对；没有新的NSS写入或A/B。下一步只做一次真实有负载的77闭环，不再重复准备。**

见 [本轮诊断](../evidence/nss78-mainline.json)、[终态审核](../evidence/nss78-final-audit.json)、[两份新增源码](../evidence/nss78-source-proof.json)。

- 16.08秒、154次读取、6个实际分类发布。发布延迟0.27–0.32秒，查询间隔2.99–3.01秒；64次来源age<1.65秒，82次age<2秒。分类快照只有1–3条，不能外推到300Mbps负载。
- 7次观察到core sleep出生age≤200ms，其中2次同时满足初始来源预算；只是时间重叠，不是完整身份、分类、mark/NAT或真实gate准入证明。
- 新的两次原完整审核通过，常驻4859/17139、config581b5d46…c791d7未变。14:56:23 source3.67秒，ECM关闭全零，无事务/stage/state/实验模块。
- Steam队列无待下载大文件，RDR2完成，网络/磁盘均0bps；游戏菜单可见，实际0游戏候选/0Steam bulk/0同WAN对。本轮仅显示Steam窗口，没有新增下载、启动对局或改HUD。前一轮Esc后的完整客户端恢复仍未补证，当前菜单观察不覆盖旧记录。
- 未调用77的aba；355项绑定和已完RAM证明保持，不重放。没有CPU/softirq、time_squeeze或真人游戏收益结论，也没有新增回滚试验。
- 原77 runtime原字节冻结，新增2份白名单源码、累计992。原始运行数据、core-guard原文和桌面内容留本地，未提交上游Issue/PR。

## NSS77历史

'''
old_state = (repo / 'docs/STATE.md').read_text(encoding='utf-8')
assert old_state.startswith('# 当前状态\n')
(repo / 'docs/STATE.md').write_text(state+old_state[len('# 当前状态\n'):].lstrip(), encoding='utf-8')
plan = '''# 下一步：直接用NSS77完成真实单WAN闭环

最新为NSS78轻载只读时序诊断，实验入口355项不变；见 [STATE](STATE.md)。

1. 每次读当前部署、原完整审核和真实应用连接；当前下载已完成。复用今后正常待下载内容，不重下已完成游戏、不找新游戏维持准备。
2. 有持续的真实CS2 UDP及Steam TCP同WAN配对时，直接运行77入口。新checkpoint、独立45秒撤销、一WAN一TCP一UDP、20Mbps及原所有期限保持；无配对不写NSS。
3. 完整A/B/A2后核对相同flow、bulk/RT leaf、mark/NAT/WAN affinity、总/单WAN/受控份额，再解释softirq、time_squeeze、吞吐和实际HUD。轻载时序观察不授予加速资格。
4. 不重装分类器、重放旧资格或扩第二WAN/共享预算。若77失败，针对实际失败帧定位，不再同时扩展候选变量。
5. 本轮用户“继续”后只读观察客户端。若再次物理Esc停止Computer Use，立即停止当轮应用输入；任何新的下载/对局窗口须另设客户端期限与精确恢复。

## NSS77历史计划

'''
plan_path = repo / 'docs/PLAN.md'
plan_path.write_text(plan+plan_path.read_text(encoding='utf-8'), encoding='utf-8')
agents_path = repo / 'AGENTS.md'
agents = agents_path.read_text(encoding='utf-8')
marker = '最新NSS77：'
assert marker in agents
agents = agents.replace(marker, '最新NSS78：仅只读时序诊断，入口仍77/355项、常驻仍68。16.08秒/154次/6个发布，64次age<1.65，发布延迟0.27–0.32、周期2.99–3.01；快照仅1–3条，不是高负载资格。当前Steam下载完成0bps、CS2菜单、0真实同WAN对，无77 stage/ECM放行/A/B或收益。14:56原完整审核通过4859/17139、source3.67、ECM关闭全零，无事务/stage/state/模块。原77runtime原字节留存，2新源/累计992。下一步只用77做一次有真实负载的集中闭环，不重装/重放/新游戏下载/扩WAN；轻载时间重叠不当准入。下方77及更早是历史。\n\n'+marker, 1)
agents_path.write_text(agents, encoding='utf-8')
readme_path = repo / 'README.md'
readme = readme_path.read_text(encoding='utf-8')
readme = readme.replace('# Athena NSS 主线记录\n', '# Athena NSS 主线记录\n\n最新 [NSS78](evidence/nss78-mainline.json)：轻载准备窗口已实测存在；目前无真实游戏/下载对，未开启NSS。入口仍NSS77，下一步直接集中闭环。现网原完整审核通过。下方77及更早为历史。\n', 1)
readme_path.write_text(readme, encoding='utf-8')
index_path = repo / 'docs/ARTIFACT_INDEX.md'
index = index_path.read_text(encoding='utf-8').replace('# 证据索引\n', '# 证据索引\n\n## 当前NSS78\n\n- [只读时序诊断](../evidence/nss78-mainline.json)、[终态审核](../evidence/nss78-final-audit.json)、[新增源码](../evidence/nss78-source-proof.json)。\n- [当前运行](../evidence/current-runtime.json)、[原77 runtime原字节](../evidence/nss77-runtime.json)。入口保持77；轻载诊断不授予准入。\n', 1)
index_path.write_text(index, encoding='utf-8')
with (repo / 'docs/EXPERIMENT_LOG.md').open('a', encoding='utf-8') as file:
    file.write('\n\n## 2026-10-05 14:56 — NSS78只读准备时序\n\n'+state.split('见 [本轮诊断]')[1].split('## NSS77历史')[0].replace('(../evidence/', '(../evidence/'))

html = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>NSS78：准备窗口实测</title><style>body{max-width:900px;margin:42px auto;padding:0 22px;background:#f6f7f5;color:#20302b;font:17px/1.8 system-ui,sans-serif}article{background:white;border:1px solid #dce4de;border-radius:18px;padding:28px}h1{font-size:28px;margin:0 0 18px}h2{font-size:21px}table{border-collapse:collapse;width:100%}td,th{padding:9px 12px;text-align:left;border-bottom:1px solid #e1e7e2}.status{color:#315b49;background:#edf5ef;padding:12px 16px;border-radius:10px}small{color:#64736b}a{color:#326550}</style><article><small>2026-10-05 · 北京时间14:56 · 现网只读</small><h1>准备时间窗口已测到，尚无新的加速对照</h1><p class="status">常驻NSS68正常，实验入口仍为NSS77。Steam下载已完成，CS2在菜单；本轮没有开启ECM或修改生产配置。</p><h2>这次做了什么</h2><p>读取现有分类结果及core守护的睡眠实例，记录发布节奏和年龄；测量前后各做一次原完整保护审核。没有选定连接、打标签、挂队列或生成测试流量。</p><table><tr><th>实际观测</th><th>结果</th></tr><tr><td>观察窗口</td><td>16.08秒；154次采样；6次分类发布</td></tr><tr><td>查询到发布延迟</td><td>0.27–0.32秒</td></tr><tr><td>相邻查询间隔</td><td>2.99–3.01秒</td></tr><tr><td>满足初始age&lt;1.65秒</td><td>64 / 154次</td></tr><tr><td>满足标签age&lt;2秒</td><td>82 / 154次</td></tr><tr><td>fresh core出生与初始年龄同时满足</td><td>2次，仅时间重叠</td></tr><tr><td>快照规模</td><td>1–3条；轻载</td></tr><tr><td>真实游戏/Steam/同WAN连接对</td><td>0 / 0 / 0</td></tr></table><h2>能说明什么</h2><p>轻载时NSS77的初始时间预算具有实际窗口，支持继续使用该入口。上述数字没有验证真实连接身份或NSS资格，也不能预测300Mbps下的发布延迟。</p><p>本轮CPU、softirq、time_squeeze、吞吐A/B及游戏jitter/loss/Miss均未测试，不能声称改善。此前部分加速证明与失败记录保持原义。</p><h2>终态与下一步</h2><p>14:56:23原完整审核通过，worker4859 / guardian17139，source age3.67秒。配置一致，ECM关闭全零，无事务、stage、state或实验模块。没有路由器变更，因此没有新增checkpoint或回滚试验。</p><p>下一次有持续的真实CS2＋现有Steam下载时，直接用NSS77完成单WAN software→NSS→software。保持独立45秒撤销、精确两条flow及20Mbps范围；先取得完整可比数据，再判断收益。</p><p><a href="../athena-nss-mainline/docs/STATE.md">仓库当前状态</a> · <a href="../athena-nss-mainline/evidence/nss78-mainline.json">脱敏实际观测</a></p></article></html>'''
(workspace / 'outputs/nss78-mainline-report.html').write_text(html, encoding='utf-8')
print(json.dumps({'passed': True, 'newSources': 2, 'totalSources': len(manifest['sources']),
    'report': 'outputs/nss78-mainline-report.html', 'routerWrites': False}))
