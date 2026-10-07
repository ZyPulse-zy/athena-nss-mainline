"""Publish the actual prewrite refusal, bounded fix, and partial UI closure."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import copy, hashlib, json, subprocess

w=Path(__file__).resolve().parents[2]; repo=w/'athena-nss-mainline'
base='e09c8cf4005a08613fc38b93130392522fb711d9'
case=w/'work/v30-normal/session-20261007005055-dbc327f6'
closure=w/'work/v31-normal/closure-20261007010353'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
dump=lambda x:json.dumps(x,ensure_ascii=False,indent=2)+'\n'
sha=lambda b:hashlib.sha256(b).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=repo)
assert git('rev-parse','HEAD').decode().strip()==base
assert not git('status','--porcelain')
old={}
for row in git('ls-tree','-r','-z',base,'--','code','evidence').split(b'\0'):
    if row:
        h,n=row.split(b'\t',1);old[n.decode()]=h.decode().split()[2]
old_bytes={p:sha((repo/p).read_bytes()) for p in old}
manifest=read(repo/'source-manifest.json');prefix=copy.deepcopy(manifest['sources']);assert len(prefix)==3878
q30=read(w/'work/v30-normal/entry-qualified.json');q31=read(w/'work/v31-normal/entry-qualified.json')
actual=read(case/'source-manifest-preaudit.json');assert len(actual)==2615
for f,h in actual.items():
    assert sha((w/f).read_bytes())==h,f
    assert (case/'frozen'/f).read_bytes()==(w/f).read_bytes(),f
for q in (q30,q31):
    assert q['passed'] and not q['hardwareExecuted'] and not q['normalApplicationFactoryHardwareAcceptance']
    for f,h in q['sourceManifest'].items():assert sha((w/f).read_bytes())==h,f
failure=read(case/'result.json');diagnosis=read(w/'work/v30-normal/refusal-analysis.json')
audit=read(w/'work/v30-normal/session-20261007005055-dbc327f6-after-audit.json')
baseline=read(case/'baseline-audit.json');models=read(w/'work/v31-normal/last-selection-qualified.json')
reader31=read(w/'work/v31-normal/real-reader-qualified.json')
reader30=json.loads(read(w/'work/v30-normal/normal-reader-process-private.json')['stdout'])
physical=read(closure/'physical-final.json');clients=read(closure/'client-process-closure.json');ui=read(closure/'client-ui-observations.json')
assert not failure['passed'] and failure['errors']==['AssertionError [ERR_ASSERTION]: Controlled exact pair changed after original full audit']
assert diagnosis['refusalBeforeCheckpoint'] and not diagnosis['anyCheckpointCreated'] and not diagnosis['anyDetachedStageStarted']
assert not diagnosis['slots']['tcp']['exactApplicationOwnedIdentityStillPresent']
assert diagnosis['slots']['udp']['exactApplicationOwnedIdentityStillPresent'] and diagnosis['slots']['tcp2']['exactApplicationOwnedIdentityStillPresent']
assert sha((case/'rejected-selection-frame-private.json').read_bytes())==diagnosis['frameSha256']==models['actualFrameSha256']
assert audit['passed'] and audit['queryAge']<6 and audit['ecmClosedAndZero'] and audit['protectedConfigurationUnchanged'] and audit['serviceEpochPinned']
assert baseline['configurationMatches'] and all(baseline['checks'].values()) and baseline['rawRulesetIdentical']
assert models['passed'] and models['modelOnly'] and models['checks']==14 and not models['hardwareExecuted']
assert reader30['actualCs2RtCandidates']==1 and reader30['actualSteamBulkCandidates']==24
assert reader31['readonly'] and reader31['actualCs2RtCandidates']==1 and reader31['actualSteamBulkCandidates']==0 and not reader31['nssAdmissionAllowed']
assert not (w/'work/v31-normal/one-session-attempt.json').exists()
assert not any(p.is_dir() and (p.name.startswith('session-') or p.name.startswith('pilot-aba-')) for p in (w/'work/v31-normal').iterdir())
assert physical['passed'] and physical['defaultQueueOptionsAndHandlesExact']
assert clients['passed'] and clients['ownedTestProcessesRemaining']==clients['cs2ProcessesRemaining']==clients['steamProcessesRemaining']==0
assert len(clients['guards'])==2 and all(x['naturalTimedExitPassed'] and x['readyBeforeDownload'] and x['deadlineSeconds']==180 for x in clients['guards'])
assert ui['currentRestoration']['downloadAndLimitRestoredBeforeGuardExit'] and not ui['currentRestoration']['originalUiRestorationComplete']
assert q31['inheritedBindings']==2615 and len(q31['sourceManifest'])==36
sources=list(dict.fromkeys([*q30['sourceManifest'],*q31['sourceManifest'],
 'work/v30-normal/analyze-refusal.mjs','work/v30-normal/application-watchdog.ps1',
 'work/v30-normal/start-application-guard.ps1','work/v30-normal/run-session.mjs',
 'work/v31-normal/read-physical-final.mjs','work/v31-normal/seal-closure.ps1',
 'work/v31-normal/publish-normal-entry.py']))
assert len(sources)==72
hashes={}
for rel in sources:
    assert 'private' not in Path(rel).name.lower() and Path(rel).suffix in ('.mjs','.lua','.py','.ps1','.json')
    data=(w/rel).read_bytes();dst=repo/'code'/rel;dst.parent.mkdir(parents=True,exist_ok=True)
    with dst.open('xb') as f:f.write(data)
    hashes[rel]=sha(data)
    manifest['sources'].append({'path':'code/'+rel,'workspaceSource':rel,'sha256':sha(data),'bytes':len(data),'role':'normal-application-prestage-selection-and-closure'})
manifest['lastNormalApplicationExport']='V31_PRESTAGE_TCP_SELECTION'
(repo/'source-manifest.json').write_text(dump(manifest),encoding='utf8')
def evidence(name,value):
    with (repo/'evidence'/name).open('x',encoding='utf8') as f:f.write(dump(value))
evidence('v30-normal-entry-qualification.json',q30)
evidence('v30-normal-refusal.json',{'trial':failure,'diagnosis':diagnosis,'actualReader':reader30,
 'actualFrozenInputsExact':2615,'checkpointCreated':False,'detachedStageStarted':False,'ecmOpened':False,
 'missingQualifiedProjectionDoesNotProveCtExit':True,'tcpLifetimeCauseEstablished':False,
 'originalFailureAndPrivateInputBytesPreserved':True})
evidence('v31-normal-entry-qualification.json',q31)
evidence('v31-last-selection-models.json',models)
evidence('v31-normal-inspect.json',{'actualReader':reader31,'fullControllerSessionStarted':False,
 'oneSessionAttemptFileCreated':False,'checkpointCreated':False,'detachedStageStarted':False,'ecmOpened':False,
 'clientDeadlineReset':False,'newGuardForRetryStarted':False,'declinedForNoBulkAndInsufficientRemainingClientTime':True,
 'factoryHardwareAcceptance':False,'subjectiveHumanAcceptance':False})
evidence('v31-normal-restoration.json',{'reusedOriginalFullAudit':audit,'protectedBaseline':baseline,
 'noRouterConfigurationWritesAfterThatAudit':True,'currentPhysicalQueues':physical,'clientProcessClosure':clients,
 'clientUiObservations':ui,'routerAndOwnedTestProcessClosurePassed':True,'originalClientUiRestorationComplete':False,
 'permanentNssDeployment':False,'newCpuCausalAcceptance':False,'normalFactoryHardwareAcceptance':False})
evidence('v31-normal-source-proof.json',{'passed':True,'baseCommit':base,'historicPrefixSources':len(prefix),
 'historicPrefixCanonicalSha256':sha(json.dumps(prefix,sort_keys=True,separators=(',',':')).encode()),
 'sourceHashes':hashes,'oldCodeAndEvidenceBlobsChecked':len(old),'oldCodeAndEvidenceUnmodified':True,
 'actualFailedTrialBoundInputsAndFrozenCopiesExact':2615,'v30Bindings':2615,'v31Bindings':2651,
 'unchangedDataPlaneAndImmutableCandidatePolicy':True,'oldQualifiedV30SourcesPreserved':True,
 'onlyPreDetachedStageHostTcpSelectionChanged':True,'noInstalledGateRetargeting':True,
 'rawCtNoncesCredentialsConfigurationsCheckpointsBinariesAndProcessCommandLinesExcluded':True,
 'originalFailuresPreservedLocally':True,'partialUiRestorationExplicitlyReported':True})
stamp=datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
report=f'''# 正常应用入口：写前拒绝、选流修正与当前终态

更新：北京时间 {stamp}。本次承接用户“继续”，实际使用已有 CS2 死斗及已排队的 Steam 更新。没有启动 NSS、checkpoint、detached stage、模块或新的加速代。正常应用多 WAN factory 和主观真人体验仍未验收；夜间 heartbeat 保持暂停。

## 实际结果

| 步骤 | 结果 | 范围 |
| --- | --- | --- |
| v30 正常应用会话 | Inferno 死斗、已有 Dead by Daylight 更新；程序归属读取为 1 个 CS2 RT、24 个 Steam BULK。完整审核后，原第一个 TCP 在合格应用候选中缺失，原 UDP 与第二 TCP 保持；入口写前拒绝 | 2615 项实际输入及源码副本逐字节冻结；没有 checkpoint、stage 或 ECM。缺少候选不能当成精确 CT 已退出 |
| v31 修正 | 固定原游戏 UDP，完整审核后选择当前应用 BULK；checkpoint 下载/SHA/gzip 后，按原 TCP 槽的 WAN、完整 mark、zone、NAT 地址再选当前 TCP，之后才形成不可变 owner/gate | 只改 host 的 pre-stage 选择；原 native/Lua/QoS/分类阈值、期限及 immutable candidate policy 保持。没有对已加速流换 tag 或重定向 gate |
| 修正验证 | 14 项模型使用实际拒绝帧；新选择接受与原 UDP、WAN 约束、错误 mark/分类/保护输入/tag 拒绝通过；原不可变 refinement 仍拒绝 TCP 变化。2651 绑定、61 相对依赖与源码语法通过 | 是离线修正资格，完整 factory 未在模型或硬件执行 |
| v31 本次正常负载 | Mirage 死斗、已有 PUBG 215.8 MB 更新，临时 8000 Kbps；只读识别 1 RT、0 合格 BULK，未配齐正常三流。独立客户端余量不足以完成完整 60 秒段 | 没有调用完整控制器或新 checkpoint/stage；没有重置 180 秒期限或再开负载重试 |

v30 软件段 HUD 见 ping12ms、上下行 loss0.0%、绿色 jitter 图；20ms只是图轴刻度。DBD 更新随后自然完成。v31 scoreboard 见 ping11ms，jitter/loss/Miss未显示。助手没有代替真人实际操作，因此这些只读观察既不是 NSS 体验收益，也不是主观真人验收。

## 恢复与未完成项

v30 拒绝后的原完整 audit 来源3.94秒，保护配置、服务 epoch、五 WAN 健康保持，ECM关闭全零；所有 baseline 检查和原 ruleset 对照通过。此后没有路由器配置写入。09:09新的两物理默认队列读取确认 wan/lan4 原 mq＋四 fq_codel 所有选项和 handle 一致。

两个独立客户端守护均在180秒自然到期，精确自有 CS2 和 Steam 退出，原 guard 和测试控制器零残留。PUBG 已在到期前暂停，界面网络/磁盘0bps；原 Steam 限速关闭已在界面恢复。未声称未启用的数字字段逐字节恢复。

**原 Steam UI 恢复未确认。** 重开先返回无可用窗口；按实际进程路径重开短暂出现登录窗口，捕获前已消失，后续进程/窗口库存为0。没有操作登录或输入凭据，原因未确定；客户端进程退出通过不能代替 UI 恢复通过。这项未完成状态保留，不能把本轮写成完整客户端或正常应用验收。

## 已成立范围与后续

沿用 v20 硬件证明：两 TCP BULK＋一 UDP RT 跨两个或三个 WAN、60秒/ECM3/20续租，六 tag/leaf、ct mark、NAT、WAN affinity 和恢复成立；五 WAN 上下行各18class/11leaf，DOWN18共享借用、UP60每WAN12硬上限、RT prio0/FQ-CoDel。没有新增五WAN同时fast path、长期常驻或CPU结论，历史CPU证据无需重测。

v31已冻结并受当次09:30截止约束；下一次正常使用须以新目录、新截止和实际输入绑定承接这项修正，不能编辑原冻结入口或复用过期授权。先恢复正常Steam客户端，再在自然配齐两不同WAN的真实Steam BULK与原CS2 RT时完成一次有界正常会话。无需挂机、新增游戏下载或重复原型/CPU实验；本次不再自动开始新硬件轮次。

证据：[v30拒绝](../evidence/v30-normal-refusal.json)、[v31资格](../evidence/v31-normal-entry-qualification.json)、[实际帧14模型](../evidence/v31-last-selection-models.json)、[本次只读条件](../evidence/v31-normal-inspect.json)、[终态与UI未完成](../evidence/v31-normal-restoration.json)、[源码保存](../evidence/v31-normal-source-proof.json)。
'''
with (repo/'docs/NORMAL_ENTRY_2026-10-07.md').open('x',encoding='utf8') as f:f.write(report)
head=f'''# 正常应用写前拒绝已定位并修正；factory验收仍待完成

更新：北京时间{stamp}。v30实际CS2＋已有Steam更新识别1RT/24BULK，完整审核后原第一TCP不在合格应用候选中，原UDP和第二TCP保持；checkpoint/stage/ECM前拒绝。2615实际输入和冻结源码逐字节保持，缺失候选不当CT退出证据。

v31只把TCP最终选择移到checkpoint下载/SHA/gzip后、detached stage前，固定原CS2及每TCP槽WAN/fullmark/zone/NAT地址；native/Lua/QoS/分类阈值与原immutable candidate policy不变。实际拒绝帧14模型、2651绑定/61相对依赖/语法通过；完整factory未在模型或硬件执行。Mirage死斗＋已有PUBG更新只读1RT/0BULK，客户端剩余时间不足，未调用完整控制器，不重置期限。

原完整恢复audit source3.94、保护配置/epoch/五WAN健康/ECM关闭全零；随后无router配置写入。09:09新两物理原mq＋四fq_codel全选项/handle一致。两180秒客户端守护自然退出、CS2/测试进程0；下载暂停和原限速关闭在到期前视觉确认。**Steam重开未形成稳定窗口，原UI恢复未确认，不能标完整客户端验收。** 原失败保留、未操作登录。没有新NSS/CPU/主观真人验收声明。

v20三流多WAN、五WAN队列与共享DOWN18/UP60每WAN12硬上限/RT优先级0的硬件结论保持。正常factory仍待一次自然配齐真实三流的有限会话；v31冻结截止不改，下一正常窗口用新目录/新绑定，先恢复SteamUI。本轮停止新增硬件实验，heartbeat继续暂停，不重放CPU/旧准备或新游戏下载。

详情：[正常入口报告](NORMAL_ENTRY_2026-10-07.md)、[拒绝](../evidence/v30-normal-refusal.json)、[14模型](../evidence/v31-last-selection-models.json)、[终态](../evidence/v31-normal-restoration.json)、[源码](../evidence/v31-normal-source-proof.json)。

## 以下保留原传输与夜间记录

'''
for rel in ('AGENTS.md','docs/STATE.md','docs/PLAN.md','docs/EXPERIMENT_LOG.md'):
    p=repo/rel;h=head
    if rel=='AGENTS.md':h=h.replace('(NORMAL_ENTRY_2026-10-07.md)','(docs/NORMAL_ENTRY_2026-10-07.md)').replace('../evidence/','evidence/')
    p.write_bytes(h.encode()+p.read_bytes())
p=repo/'README.md';intro='''# Athena NSS 多WAN / QoS 受控原型

三流跨WAN、五WAN队列映射和共享预算已硬件通过。正常应用入口本次在NSS前拒绝，选流时机已修正并通过实际帧14模型；当前NSS关闭，正常factory仍未硬件验收，Steam UI恢复未确认。见[STATE](docs/STATE.md)及[正常入口报告](docs/NORMAL_ENTRY_2026-10-07.md)。

## 以下保留历史交付

''';p.write_bytes(intro.encode()+p.read_bytes())
with (repo/'.gitattributes').open('a',encoding='utf8') as f:
    f.write('\n# Exact new normal-application Windows source paths.\n')
    for rel in sources:
        if b'\r\n' in (w/rel).read_bytes():f.write('/code/'+rel+' whitespace=cr-at-eol\n')
assert not git('diff','--name-only',base,'--','code','evidence')
assert all(sha((repo/p).read_bytes())==h for p,h in old_bytes.items())
print(json.dumps({'passed':True,'newSources':len(sources),'sourceHashes':len(manifest['sources']),
 'oldCodeAndEvidenceBlobsPreserved':len(old),'actualFrozenInputsExact':len(actual),
 'normalFactoryHardwareAcceptance':False,'originalSteamUiRestorationComplete':False}))
