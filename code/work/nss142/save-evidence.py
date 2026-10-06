"""Publish the scheduled read-only morning closure; preserve all older evidence."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib, json, subprocess

w = Path(__file__).resolve().parents[2]
repo = w / 'athena-nss-mainline'
r = w / 'work/nss142'

def load(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def sha(b):
    return hashlib.sha256(b).hexdigest()

def dump(p, value):
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

final = load(r / 'v1-final-health.json')
physical = load(r / 'physical-final.json')
receiver = load(r / 'receiver-closure.json')
endpoints = load(r / 'endpoint-client-closure.json')
bindings = load(r / 'prepared-bindings-final.json')
inheritance = load(r / 'inherited-readers.json')
failure = load(r / 'tool-call-v1-rejection.json')
assert all(v['passed'] for v in [final, physical, receiver, endpoints, bindings, inheritance])
assert final['ecmStoppedAndZero'] and final['noActiveTransaction'] and final['noStaging'] and final['noExperimentState'] and final['noExperimentalModule']
assert final['originalFullLockedNativeAudit'] and final['unrelatedConfigurationMatches'] and final['exactWan4AutomaticFailoverProved']
assert not final['allFiveWanHealthy'] and not final['wan4Up'] and not final['wan4Ipv4Present']
assert endpoints['previousLoadsChecked'] == endpoints['ownedUnitsInactiveMainPidZero'] == 7
assert endpoints['temporaryFirewallRulesRemaining'] == endpoints['ownedClientOrGuardProcessesRemaining'] == receiver['exactOwnedReceiverAndTimeoutProcessesRemaining'] == 0
assert bindings['boundInputs'] == 1385 and bindings['currentAndPreviouslyFrozenInputsExact'] and not bindings['modelsReplayed']
assert failure['originalFailurePreserved'] and not failure['nestedToolsDispatched'] and not failure['productionWrites']
checked = datetime.fromisoformat(final['observedAt'].replace('Z', '+00:00'))
assert datetime(2026, 10, 6, 1, 40, tzinfo=timezone.utc) <= checked < datetime(2026, 10, 6, 2, 0, tzinfo=timezone.utc)

old = subprocess.check_output(['git', 'show', 'HEAD:evidence/current-runtime.json'], cwd=repo)
assert json.loads(old)['round'] == 'NSS141'
assert subprocess.check_output(['git', 'status', '--porcelain'], cwd=repo).strip() == b''
archive = repo / 'evidence/nss141-runtime.json'
assert not archive.exists()
archive.write_bytes(old)

manifest = load(repo / 'source-manifest.json')
assert len(manifest['sources']) == 1885
prefix = sha(json.dumps(manifest['sources'], sort_keys=True, separators=(',', ':')).encode())
names = ['health.mjs', 'read-final-physical.mjs', 'verify-receivers.mjs', 'verify-endpoints.mjs', 'verify-bound-inputs.mjs', 'save-evidence.py', 'verify-published.py']
hashes = {}
for name in names:
    src = r / name
    assert src.is_file() and 'private' not in name
    b = src.read_bytes()
    rel = src.relative_to(w).as_posix()
    dst = repo / 'code' / rel
    assert not dst.exists()
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(b)
    hashes[rel] = sha(b)
    manifest['sources'].append({'path': 'code/' + rel, 'workspaceSource': rel, 'sha256': sha(b), 'bytes': len(b), 'role': 'scheduled-readonly-morning-closure'})
manifest['generatedAt'] = datetime.now(timezone.utc).isoformat()
manifest['lastAppendExport'] = 'NSS142'
dump(repo / 'source-manifest.json', manifest)

snapshot = r / 'local-evidence-private'
snapshot.mkdir(exist_ok=False)
inputs = {}
for src in sorted(r.iterdir()):
    if not src.is_file():
        continue
    b = src.read_bytes()
    (snapshot / src.name).write_bytes(b)
    inputs[src.relative_to(w).as_posix()] = sha(b)
dump(r / 'local-evidence-index-private.json', inputs)

summary = {
    'round': 'NSS142', 'observedAt': final['observedAt'], 'morningClosureAfterBeijing0940': True,
    'readonlyOnly': True, 'originalFullLockedNativeAuditPassed': True, 'bothPhysicalRootsExact': True,
    'previousEndpointLoadsChecked': 7, 'endpointsAndClientsClosed': True, 'ownedSshReceiversRemaining': 0,
    'preparedRealEntry': 'work/nss140/real-session.mjs', 'preparedBindings': 1385,
    'currentAndPreviouslyFrozenInputsExact': True, 'residentClassifierChanged': False, 'residentUpTagZeroUnchanged': True,
    'productionWrites': False, 'checkpointOrStageStarted': False, 'ecmOpened': False,
    'modelsReplayed': False, 'newHardwareAbaProof': False, 'newCpuComparison': False,
    'humanCs2Acceptance': False, 'steamDownloadOperated': False, 'desktopOperated': False,
    'nssPermanentlyEnabled': False, 'fullCakeReplacementAccepted': False,
    'knownWan4AuthenticationFailureStillPresent': True, 'existingFourWanAutomaticFailoverExact': True,
    'localToolSyntaxRejectionPreserved': True, 'historicEvidenceAndFailuresKept': True,
    'pauseThisNightHeartbeatImmediatelyAfterPublishedArchiveVerification': True,
    'nightAuthorizationEndsBeijing': '2026-10-06T10:00:00+08:00',
    'nextStep': 'One concentrated awake human CS2 and existing bulk download test through the prepared single-WAN entry, with fresh admission, checkpoint and independent rollback.',
    'reportVerification': {'sourceValidated': True, 'browserRendered': False}
}
proof = {
    'round': 'NSS142', 'historicPrefixSources': 1885, 'historicPrefixCanonicalSha256': prefix,
    'sources': len(hashes), 'sourceHashes': hashes, 'localArtifactsFrozen': len(inputs),
    'oldNss141RuntimeRetainedExactSha256': sha(old), 'preparedBindings': 1385,
    'preparedInputsCurrentAndPreviouslyFrozenMatch': True,
    'privateHostBootstrapExcluded': True, 'credentialsCtNoncesConfigurationCheckpointsAndBinariesExcluded': True,
    'originalFailuresKept': True
}
evidence = {'mainline': summary, 'final-audit': final, 'physical-final': physical,
            'receiver-closure': receiver, 'endpoint-client-closure': endpoints,
            'prepared-bindings': bindings, 'inherited-readers': inheritance,
            'failures': [failure], 'source-proof': proof}
for name, value in evidence.items():
    dump(repo / f'evidence/nss142-{name}.json', value)
runtime = json.loads(old)
runtime.update({'round': 'NSS142', 'checkedAt': final['observedAt'], 'workerPid': final['workerPid'],
                'guardianPid': final['guardianPid'], 'audit': final, 'physicalRootRestoreAudit': physical,
                'endpointClientClosureAudit': endpoints, 'ownedSshReceiverClosureAudit': receiver,
                'morningReadonlyClosureCompleted': True, 'newCpuComparisonAcceptedThisTurn': False,
                'realHumanGameAcceptance': False, 'historical141RuntimePreservedSha256': sha(old),
                'pauseNightHeartbeatAfterPublicationRequired': True})
dump(repo / 'evidence/current-runtime.json', runtime)

when = checked.astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
text = f'''更新：{when}，北京时间。NSS142为本夜最后一次只读收尾，常驻仍NSS68/config581b5d46…c791d7，worker{final['workerPid']}、guardian{final['guardianPid']}。实验已经撤销，ECM保持关闭全零。

**晨间完整核验通过：自动分类器身份、原完整保护审核、两处物理队列、自有测试端点和客户端均已核验。140真人入口的1385项实际输入仍与既有冻结副本逐字节一致。此轮只封存终态，没有重新试装、开启NSS、运行负载或操作桌面。**

见 [晨间汇总](../evidence/nss142-mainline.json)、[完整审核](../evidence/nss142-final-audit.json)、[物理队列](../evidence/nss142-physical-final.json)、[端点与客户端](../evidence/nss142-endpoint-client-closure.json)、[输入绑定](../evidence/nss142-prepared-bindings.json)、[失败记录](../evidence/nss142-failures.json)。

- 原完整来源年龄{final['queryAge']:.2f}秒，动态selectors{final['selectors']}由原native ownership审核验证；配置、服务、PBR/ct mark/NAT/连接粘性保护不变。无事务/stage/state/实验模块，物理wan与lan4原mq＋四fq_codel的options/handles精确匹配。
- 七个既有有限负载的端点全部inactive/MainPID0；TCP/UDP端口关闭，临时规则0、七个canonical防火墙基线一致；Windows精确自有路径匹配的客户端/guard和自有SSH receiver均0残留。只读确认，不发送stop、不改防火墙。
- WAN4仍认证down且无IPv4，既有四路健康权重100/100/100/0/100及300桶四路各75保持；未主动认证、重启或修改校园策略。
- 139真实同CT自动BULK→BE精确撤销及新代重学仍为历史硬件证据；128约30Mbps受控上传可比短窗softirq相对低48.64%仍为历史性能证据。140新整合版本完整A/B/A2、真人CS2、300Mbps主下载、长期运行及完整CAKE替代均尚未验收。本轮没有新增CPU或游戏结论。
- 晨间第一次批量调用在本地JavaScript语法解析即被拒绝，未派发检查/连接路由器；失败原样保留后修正调用，随后完整检查通过。不覆盖141及更早被冻结证据。
- 本夜工作在发布检查、推送和实际Git archive读回后结束，立即暂停athena-nss；10:00授权截止，之后不新开生产实验，临时keep-awake自到期，不改电源计划。
- 用户醒来后只集中一次：用140默认inspect确认真人CS2 UDP与已有正常下载的Steam BULK TCP同一健康WAN，再获取新分类/kernel pin/checkpoint和独立owner，做三段各20秒software→NSS→software。记录jitter/loss/Miss/体感及softirq/squeeze/吞吐；若改类，精确撤销、结束旧代，新epoch重进，中断不能算完整ABA。继续仅一TCP＋一UDP，不扩第二WAN/共享预算/WiFi/autorate/ECN。
'''
for name, title in [('STATE.md', '# 当前状态'), ('PLAN.md', '# 下一步：一次集中真人验收'), ('EXPERIMENT_LOG.md', '# NSS142 · 晨间只读收尾')]:
    p = repo / 'docs' / name
    p.write_text(title + '\n\n' + text + '\n## NSS141及更早历史\n\n' + p.read_text(encoding='utf-8'), encoding='utf-8')
p = repo / 'AGENTS.md'
p.write_text('# 接续此研究\n\n最新NSS142：09:40后晨间只读完整终态、两物理根、七端点与客户端/SSH receiver关闭核验全部通过；140准备入口1385当前/旧冻结输入精确相同，没有重跑模型/生产写入/ECM/负载/UI。常驻68/'+str(final['workerPid'])+'/'+str(final['guardianPid'])+'、upTag0/config不变；WAN4仍down，既有四路failover精确不变。首次本地调用语法拒绝原记录保留，141 runtime原Git字节归档，旧证据不改。发布archive验证后立即暂停本夜heartbeat，10点后不新实验，临时keep-awake自到期。下一步用户醒来一次集中真人CS2＋已有下载的140单WAN三段20秒闭环；140整合完整ABA尚未执行，139撤销/重学和128约30Mbps CPU仅历史实测，不扩WAN/不新下载/不重复准备。以STATE开头为准。\n\n## NSS141及更早历史\n\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
p = repo / 'README.md'
p.write_text('# Athena NSS 主线\n\n最新 [NSS142晨间终态](evidence/nss142-mainline.json)：完整保护/两物理根/七端点/客户端收尾通过，常驻68且ECM关闭；140最后真人入口1385输入未变，整合版完整A/B/A2仍待一次集中真人验收。夜间任务在发布校验后暂停，10:00后不新实验。以 [STATE](docs/STATE.md) 与 [PLAN](docs/PLAN.md) 开头为准。\n\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
p = repo / 'docs/ARTIFACT_INDEX.md'
p.write_text('# NSS142晨间只读收尾\n\n'+''.join(f'- [NSS142 {k}](../evidence/nss142-{k}.json)\n'for k in evidence)+'\n'+p.read_text(encoding='utf-8'),encoding='utf-8')

attributes = repo / '.gitattributes'
attributes.write_text(attributes.read_text(encoding='utf-8')+'\n# Keep the archived NSS141 runtime in the exact published Git bytes.\n/evidence/nss141-runtime.json -text\n', encoding='utf-8')
checker = repo / 'tools/check_repository.py'
before = checker.read_text(encoding='utf-8')
needle = "rt141=json.loads((root/'evidence/current-runtime.json').read_text())"
assert before.count(needle) == 1
after = before.replace(needle, "rt141=json.loads((root/'evidence/nss141-runtime.json').read_text())")
anchor = "print(json.dumps({'passed':True,'filesChecked':count"
assert after.count(anchor) == 1
added = '''proof142=json.loads((root/'evidence/nss142-source-proof.json').read_text())
assert proof142['historicPrefixSources']==1885 and proof142['sources']==7 and len(manifest['sources'])>=1892
assert proof142['historicPrefixCanonicalSha256']==hashlib.sha256(json.dumps(manifest['sources'][:1885],sort_keys=True,separators=(',',':')).encode()).hexdigest()
assert len(proof142['sourceHashes'])==7 and proof142['preparedBindings']==1385 and proof142['preparedInputsCurrentAndPreviouslyFrozenMatch']and proof142['privateHostBootstrapExcluded']and proof142['credentialsCtNoncesConfigurationCheckpointsAndBinariesExcluded']and proof142['originalFailuresKept']
for source,digest in proof142['sourceHashes'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==digest
x142=json.loads((root/'evidence/nss142-mainline.json').read_text());rt142=json.loads((root/'evidence/current-runtime.json').read_text())
assert x142['round']==rt142['round']=='NSS142'and x142['preparedBindings']==rt142['preparedRealEntryBoundInputs']==1385
assert all(x142[k]for k in ['morningClosureAfterBeijing0940','readonlyOnly','originalFullLockedNativeAuditPassed','bothPhysicalRootsExact','endpointsAndClientsClosed','currentAndPreviouslyFrozenInputsExact','residentUpTagZeroUnchanged','knownWan4AuthenticationFailureStillPresent','existingFourWanAutomaticFailoverExact','localToolSyntaxRejectionPreserved','historicEvidenceAndFailuresKept','pauseThisNightHeartbeatImmediatelyAfterPublishedArchiveVerification'])
assert not any(x142[k]for k in ['residentClassifierChanged','productionWrites','checkpointOrStageStarted','ecmOpened','modelsReplayed','newHardwareAbaProof','newCpuComparison','humanCs2Acceptance','steamDownloadOperated','desktopOperated','nssPermanentlyEnabled','fullCakeReplacementAccepted'])
assert x142['previousEndpointLoadsChecked']==7 and x142['ownedSshReceiversRemaining']==0
assert rt142['historical141RuntimePreservedSha256']==proof142['oldNss141RuntimeRetainedExactSha256']==hashlib.sha256((root/'evidence/nss141-runtime.json').read_bytes()).hexdigest()
assert rt142['morningReadonlyClosureCompleted']and rt142['currentNssAdmissionMustBeRefreshedBeforeWrite']and not rt142['preparedRealEntryHardwareAbaTested']and not rt142['nssPermanentlyEnabled']and not rt142['realHumanGameAcceptance']and not rt142['newCpuComparisonAcceptedThisTurn']
assert all(rt142['audit'][k]for k in ['passed','readonly','originalFullLockedNativeAudit','unrelatedConfigurationMatches','exactWan4AutomaticFailoverProved','ecmStoppedAndZero','noActiveTransaction','noStaging','noExperimentState','noExperimentalModule'])and not rt142['audit']['allFiveWanHealthy']
assert all(rt142['physicalRootRestoreAudit'][k]for k in ['passed','readonly','physicalWanOriginalMqFourFqCodelRestored','lan4OriginalMqFourFqCodelRestored','defaultQueueOptionsAndHandlesExact'])
end142=json.loads((root/'evidence/nss142-endpoint-client-closure.json').read_text());assert end142==rt142['endpointClientClosureAudit']and end142['passed']and end142['readonly']and end142['previousLoadsChecked']==end142['ownedUnitsInactiveMainPidZero']==7 and end142['allSevenCanonicalFirewallBaselinesMatch']and end142['tcpAndUdpPortsClosed']and end142['clientProcessesMatchedByExactOwnedLoadPaths']and end142['temporaryFirewallRulesRemaining']==end142['ownedClientOrGuardProcessesRemaining']==0 and not end142['remoteWrites']and not end142['productionWrites']and not end142['desktopOperated']
assert json.loads((root/'evidence/nss142-receiver-closure.json').read_text())['exactOwnedReceiverAndTimeoutProcessesRemaining']==0
bind142=json.loads((root/'evidence/nss142-prepared-bindings.json').read_text());assert bind142['passed']and bind142['boundInputs']==1385 and bind142['currentAndPreviouslyFrozenInputsExact']and not bind142['modelsReplayed']and not bind142['routerConnected']and not bind142['productionWrites']and not bind142['newHardwareAbaProof']
reader142=json.loads((root/'evidence/nss142-inherited-readers.json').read_text());assert reader142['passed']and reader142['readOnlyReaders']and len(reader142['files'])==3
for f in reader142['files']:
 old=(root/'code/work/nss141'/f['file']).read_bytes();new=(root/'code/work/nss142'/f['file']).read_bytes()
 assert f['namespaceOnlyChange']and hashlib.sha256(old).hexdigest()==f['priorSha256']and hashlib.sha256(new).hexdigest()==f['sha256']and new.replace(b'work/nss142',b'work/nss141')==old
fail142=json.loads((root/'evidence/nss142-failures.json').read_text());assert len(fail142)==1 and not fail142[0]['passed']and fail142[0]['originalFailurePreserved']and not fail142[0]['nestedToolsDispatched']and not fail142[0]['routerAuditStarted']and not fail142[0]['productionWrites']
'''
checker.write_text(after.replace(anchor, added + anchor), encoding='utf-8')

body = f'''<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NSS142 晨间终态</title><style>body{{max-width:880px;margin:40px auto;padding:0 24px;font:16px/1.8 system-ui;background:#f7f8fa;color:#202832}}h1{{font-size:28px}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #d8e0e8;padding:10px;text-align:left}}</style><h1>NSS142：夜间工作收尾</h1><p>{when}，北京时间。完整只读核验通过，实验已撤销，常驻自动分类器保留；NSS仍为受控实验状态，尚未长期启用。</p><table><tr><th>核验项</th><th>实际结果</th></tr><tr><td>路由器保护与分类器</td><td>原完整审核通过；source {final['queryAge']:.2f}秒，动态selectors {final['selectors']}由native审核验证</td></tr><tr><td>队列与实验状态</td><td>两处原mq＋四fq_codel精确匹配；ECM关闭全零，无事务或实验残留</td></tr><tr><td>端点与客户端</td><td>七个自有端点inactive、端口关闭、临时规则0；客户端/guard/SSH receiver零残留</td></tr><tr><td>真人入口</td><td>140入口1385项输入与原冻结副本完全一致；未重跑模型或硬件闭环</td></tr><tr><td>已知故障</td><td>WAN4仍认证down，现有四路自动failover不变</td></tr></table><p>已证明的主要进展：自动class映射NSS双向bulk/RT leaf；真实改类后精确撤销，保持同CT/NAT/WAN并用新epoch重学；约30Mbps受控上传短窗softirq相对下降48.64%。这些分别属于既有硬件和性能证据。</p><p><strong>仍待一次集中真人CS2＋已有正常下载内容验收。</strong>140整合版本完整software→NSS→software、300Mbps主下载、长期运行和完整CAKE替代尚未通过。本轮没有新的CPU或游戏体验结论。</p><p>第一次本地批量调用语法拒绝已原样保留，修正后才执行检查。旧源、runtime与失败不覆盖。发布检查、推送及实际Git archive读回完成后立即暂停本次夜间任务，10:00后不开始新实验。</p></html>'''
(w / 'outputs/nss142-mainline-report.html').write_text(body, encoding='utf-8')
print(json.dumps({'preparedPublication': True, 'appendedSources': len(hashes), 'totalSources': len(manifest['sources']), 'old141RuntimePreservedExactGitBytes': True, 'productionWrites': False}))
