"""Publish the actual readonly closure; preserve all prior source and evidence bytes."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import copy, hashlib, json, subprocess

w = Path(__file__).resolve().parents[2]
repo = w / 'athena-nss-mainline'
base = '5386ab1ad5be8de061b65161ecdb35948fcc802a'
run = w / 'work/morning-20261007/run-20261006234137-d2fdcbc7'
physical = w / 'work/morning-20261007/read-physical-20261006234137-d2fdcbc7.mjs'
read = lambda p: json.loads(p.read_text(encoding='utf8'))
dump = lambda x: json.dumps(x, ensure_ascii=False, indent=2) + '\n'
sha = lambda b: hashlib.sha256(b).hexdigest()

def git(*args):
    return subprocess.check_output(['git', *args], cwd=repo)

assert git('rev-parse', 'HEAD').decode().strip() == base
assert not git('status', '--porcelain')
assert datetime.now(timezone.utc) < datetime(2026, 10, 7, tzinfo=timezone.utc)
result = read(run / 'morning-final.json')
assert result['passed'] and result['readonly'] and not result['productionExperimentsStarted']
assert result['fullAudit']['protectedConfigurationUnchanged'] and result['fullAudit']['ecmClosedAndZero']
assert result['fullAudit']['allFiveHealthyWanBaseline'] and not result['fullAudit']['nssAdmissionAllowed']
assert result['fullAudit']['queryAge'] < 6
assert result['physicalQueues']['defaultQueueOptionsAndHandlesExact']
assert result['endpointClosure']['knownOwnedUnitsChecked'] == 17
assert result['endpointClosure']['canonicalFirewallBaselineMatched']
assert result['endpointClosure']['temporaryFirewallRulesRemaining'] == 0
assert result['endpointClosure']['tcpAndUdpEndpointPortsClosed']
assert not result['endpointClosure']['remoteWrites']
assert result['clientClosure']['knownNightFixtureNamespacesChecked'] == 16
assert result['clientClosure']['ownedClientControllerGuardOrSenderProcessesRemaining'] == 0
events = read(run / 'run-processes-private.json')
assert len(events) == 4 and all(e['code'] == 0 for e in events)

# Git identities and original bytes are checked before any append.
old = {}
for row in git('ls-tree', '-r', '-z', base, '--', 'code', 'evidence').split(b'\0'):
    if row:
        header, name = row.split(b'\t', 1)
        old[name.decode()] = header.decode().split()[2]
for name, oid in old.items():
    b = (repo / name).read_bytes()
    assert hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest() == oid, name
manifest = read(repo / 'source-manifest.json')
prefix = copy.deepcopy(manifest['sources'])
assert len(prefix) == 3863
hashes = {}
for p in [Path(__file__).resolve(), physical]:
    rel = p.relative_to(w).as_posix()
    b = p.read_bytes()
    dst = repo / 'code' / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    with dst.open('xb') as f:
        f.write(b)
    hashes[rel] = sha(b)
    manifest['sources'].append({'path': 'code/' + rel, 'workspaceSource': rel,
                               'sha256': sha(b), 'bytes': len(b),
                               'role': 'readonly-morning-final-closure'})
(repo / 'source-manifest.json').write_text(dump(manifest), encoding='utf8')

def evidence(name, value):
    with (repo / 'evidence' / name).open('x', encoding='utf8') as f:
        f.write(dump(value))

# This is the fresh sanitized summary, not the raw SSH / CT / process record.
with (repo / 'evidence/morning-final.json').open('xb') as f:
    f.write((run / 'morning-final.json').read_bytes())
evidence('morning-final-source-proof.json', {
    'passed': True, 'baseCommit': base, 'historicPrefixSources': len(prefix),
    'historicPrefixCanonicalSha256': sha(json.dumps(prefix, sort_keys=True, separators=(',', ':')).encode()),
    'sourceHashes': hashes, 'oldCodeAndEvidenceUnmodified': True,
    'oldCodeAndEvidenceBlobsChecked': len(old),
    'actualReadonlyProcessExitCodes': [e['code'] for e in events],
    'rawProcessSshCtCredentialsAndCheckpointsExcluded': True,
    'morningSummarySha256': sha((run / 'morning-final.json').read_bytes()),
    'localReadCorrection': {
        'originalReadFailed': True, 'requestedPath': 'athena-nss-mainline/manifest.json',
        'originalExitCode': 1, 'originalError': 'Cannot find path because it does not exist.',
        'correctedPath': 'athena-nss-mainline/source-manifest.json',
        'originalToolTranscriptRetained': True, 'productionAuditAffected': False
    }
})

stamp = datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
report = f'''# Athena NSS 夜间多 WAN / QoS 交付范围与晨间收尾

更新时间：北京时间 {stamp}。本夜生产实验已结束，07:41最后一次只读核验全部通过。没有在晨间重新打开 fixture、NSS、Steam 或 CS2；没有生产配置写入。

## 已证明的范围

| 项目 | 实际证据 | 结论边界 |
| --- | --- | --- |
| 多 WAN 加速 | v16/v19/v20：两 TCP BULK＋一 UDP RT，自然跨两个或三个 WAN；B 60秒、ECM=3、20次续租 | 三条精确连接的有界硬件原型 |
| 双向分类和连接粘性 | 六 tag、上下行 bulk/RT leaf、完整 ct mark、NAT、WAN affinity 正确 | Linux 新连接 PBR 保持，NSS 不重新负载均衡 |
| 五 WAN QoS 映射 | v20 上下行各18 HTB class、11 FQ-CoDel leaf，RT prio0、BULK prio1 | 五 WAN 队列覆盖；不是五 WAN 同时 fast path |
| 共享下行预算 | DOWN18，每 WAN 保障3、ceil18可借用；两 bulk 6.72/8.28Mbps、合14.99Mbps，超过保障且在总预算内 | 观察到空闲份额借用；未证明长期精度或满载吞吐 |
| 上行与实时流 | UP60，每 WAN12硬上限；RT双向leaf drop0；v20 B内部自有echo2434/2434返回 | 小 UDP echo 不是 CS2 jitter/loss/Miss 或真人体感 |
| 恢复 | 实验结束恢复软件路径、原队列、模块、端点、FW和客户端；本次晨间重新只读确认 | NSS 当前关闭，尚未永久部署 |

CPU收益复用历史可比证据：NSS128约30Mbps上传，softirq 10.034%→5.246%→10.393%，原七项可比条件成立、NSS短窗相对低48.64%。本夜没有重新追CPU门槛，也不把该数值当成新多WAN、300Mbps或长期性能结论。

## 晨间实际终态

- 07:41:48完整收尾通过，原完整审核来源年龄1.29秒；五WAN健康，保护配置/auth/manifest保持，ECM关闭全零，无NSS准入。
- 两物理wan/lan4原mq＋各四fq_codel，所有默认选项和handle精确一致。
- 17个本夜自有端点单位均已退出、MainPID=0；临时FW规则0、原canonical防火墙基线一致、TCP/UDP测试端口关闭。
- 16个本机fixture namespace中，自有client/controller/guard/sender进程零残留。
- 四个实际只读步骤退出码均0。原准备记录“晨间未执行”保持历史原字节，新结果另存，不覆盖旧证明。

## 未完成与已知限制

1. 五WAN同时加速未验。五槽模块仅完成同6.18.44编译、源码/模型/RAM资格，从未加载硬件。v21..24五次负载前提失败及v27首TCP8.008秒超时全部在NSS前，原失败保留；不能归因NSS/固件，raw TCP问题根因仍未知。
2. v26正常应用入口已接Steam/CS2实际socket归属，18模型/46依赖/2586绑定通过，数据面沿用v20；现场inspect为0游戏/0下载/0pair。新整合factory未硬件验收，不能称正常应用或真人体验已通过。
3. 控制器仍为有界会话。真实BULK→BE时结束耦合旧代并恢复；连续新代、多流常驻、路由器重启恢复尚未交付。
4. 当前未覆盖全网，也没有完整CAKE公平性/diffserv/autorate/ECN复刻、Wi-Fi或300Mbps长期压力结论。
5. 常驻自动分类器仍NSS68/config581b5d46…c791d7；软件CAKE承担当前流量及fallback。

## 下一步

下一正常使用时做一次v26有限正常应用会话即可，不要求长期挂机。五流fixture的TCP前提问题先保留为独立后续事项，有新证据才继续；不盲重试、扩FW或修改学校/认证策略。长期连续代和扩大加速池另行规划。夜间自动任务在本次报告检查、提交、推送、实际Git archive验证后暂停；08:00后不自动开启新实验。

证据：[晨间真实核验](../evidence/morning-final.json)、[追加源码与保存边界](../evidence/morning-final-source-proof.json)、[v20硬件](../evidence/v20-five-hardware.json)、[v26正常入口](../evidence/v26-progress.json)、[v27原失败](../evidence/v27-raw-prerequisite.json)。
'''
with (repo / 'docs/NIGHT_REPORT_2026-10-07.md').open('x', encoding='utf8') as f:
    f.write(report)
head = f'''# 夜间多 WAN / 高级 QoS 受控原型完成；晨间恢复核验通过

更新：北京时间{stamp}。07:41最后只读核验全部通过：原完整audit来源1.29秒、五WAN健康/保护配置保持/ECM关闭全零；两物理原mq＋四fq_codel所有选项和handle一致；17个自有端点退出、FW原基线一致/临时规则0/端口关闭；16个本机fixture namespace测试进程零残留。本次无生产实验或远端写入，原冻结源码/失败/证据保持。

本夜交付的受控范围：两TCP BULK＋一UDP RT跨两个或三个WAN，60秒/ECM3/20续租、六双向tag/leaf及ct mark/NAT/affinity正确；五WAN队列映射、DOWN18共享借用、UP60每WAN12硬上限、RT prio0/FQ-CoDel在硬件成立。**五WAN同时fast path、v26正常应用整合factory和长期常驻仍未验。** 当前NSS关闭、常驻分类器NSS68/config581b5d46…c791d7与软件fallback保持。

v27 raw TCP首包超时发生在checkpoint/stage/ECM前，原失败保留、根因未知，不盲重试或扩FW/学校策略。下一次正常使用只做一次v26有限应用会话，不要求挂机；五流前提问题和长期连续代进入后续。本夜结束新增实验，检查/提交/推送/实际archive后暂停heartbeat，08:00后不自动实验。

详情：[晨间交付报告](NIGHT_REPORT_2026-10-07.md)、[实际终态](../evidence/morning-final.json)、[源码保存](../evidence/morning-final-source-proof.json)。

## 以下保留原始夜间记录

'''
for name in ['AGENTS.md', 'docs/STATE.md', 'docs/PLAN.md', 'docs/EXPERIMENT_LOG.md']:
    p = repo / name
    h = head
    if name == 'AGENTS.md':
        h = h.replace('(NIGHT_REPORT_2026-10-07.md)', '(docs/NIGHT_REPORT_2026-10-07.md)').replace('../evidence/', 'evidence/')
    p.write_text(h + p.read_text(encoding='utf8'), encoding='utf8')
p = repo / 'README.md'
intro = '''# Athena NSS 多 WAN / 高级 QoS 受控原型

三流跨WAN、五WAN队列映射、共享下行预算借用和RT优先级已在硬件通过，晨间恢复核验全部正常。当前NSS关闭，五WAN同时加速、正常应用新factory和长期常驻尚未验收。见[晨间报告](docs/NIGHT_REPORT_2026-10-07.md)及[STATE](docs/STATE.md)。

## 以下保留 v1 和历史记录

'''
p.write_text(intro + p.read_text(encoding='utf8'), encoding='utf8')
for name, oid in old.items():
    b = (repo / name).read_bytes()
    assert hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest() == oid, name
print(json.dumps({'passed': True, 'actualMorningAuditPublished': True,
                  'newSources': len(hashes), 'totalSources': len(manifest['sources']),
                  'oldCodeAndEvidenceBlobsPreserved': len(old), 'productionWrites': False}))
