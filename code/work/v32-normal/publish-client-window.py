"""Publish source identity and the actual bounded client window, not factory acceptance."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import copy, hashlib, json, subprocess

w=Path(__file__).resolve().parents[2];repo=w/'athena-nss-mainline';r=w/'work/v32-normal'
base='2eb9d50e2519733b43f1ece3abf00c6d31b217f0'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
dump=lambda v:json.dumps(v,ensure_ascii=False,indent=2)+'\n'
sha=lambda b:hashlib.sha256(b).hexdigest()
def git(*a):return subprocess.check_output(['git',*a],cwd=repo)
assert git('rev-parse','HEAD').decode().strip()==base
assert not git('status','--porcelain')
old={}
for row in git('ls-tree','-r','-z',base,'--','code','evidence').split(b'\0'):
    if row:
        h,n=row.split(b'\t',1);old[n.decode()]=h.decode().split()[2]
old_bytes={n:sha((repo/n).read_bytes()) for n in old}
manifest=read(repo/'source-manifest.json');prefix=copy.deepcopy(manifest['sources'])
assert len(prefix)==3950
q=read(r/'entry-qualified.json');prep=read(r/'prepare-receipt.json')
closure=Path(read(r/'first-window-closure-pointer.json')['directory'])
ui=read(closure/'client-ui-observations.json');clients=read(closure/'client-closure.json')
audit=read(r/'v32-final-audit.json');physical=read(closure/'physical-final.json')
assert q['passed'] and not q['hardwareExecuted'] and not q['wholeFactoryModeled']
assert q['inheritedBindings']==2651 and len(q['sourceManifest'])==36 and q['noModelsReplayed']
assert q['unchangedDataPlaneAndImmutableCandidatePolicy'] and q['unchangedV31PreStageSelection']
for name,h in q['sourceManifest'].items():
    assert sha((w/name).read_bytes())==h,name
    assert (closure/'frozen-sources'/name).read_bytes()==(w/name).read_bytes(),name
for name,h in prep['oldHashes'].items():assert sha((w/name).read_bytes())==h,name
for name,h in ui['privateInputHashes'].items():assert sha((closure/name).read_bytes())==h,name
assert clients['passed'] and clients['naturalTimedExitPassed'] and clients['deadlineSeconds']==180
assert clients['guardProcessGone'] and clients['ownedTestProcessesRemaining']==clients['cs2ProcessesRemaining']==0
assert not clients['fullControllerSessionStarted'] and not ui['newNssSessionStarted']
assert ui['currentUiRestoration']['uiSettingsRestoreConfirmed'] and ui['currentUiRestoration']['hadesPaused']
assert ui['currentUiRestoration']['networkBps']==ui['currentUiRestoration']['diskBps']==0
assert not ui['currentUiRestoration']['steamDownloadLimitEnabled']
assert not ui['steamRelaunchForRestoration']['strictCumulative180SecondDownloadProofAvailable']
assert ui['steamRelaunchForRestoration']['automaticDownloadResumptionObserved']
assert audit['passed'] and audit['queryAge']<6 and audit['ecmClosedAndZero'] and audit['protectedConfigurationUnchanged']
assert audit['serviceEpochPinned'] and audit['allFiveHealthyWanBaseline']
assert physical['passed'] and physical['defaultQueueOptionsAndHandlesExact']
assert not (r/'one-session-attempt.json').exists() and not (r/'active-run-private.json').exists()
assert not any(p.name.startswith('pilot-aba-') for p in r.iterdir())
sources=[*q['sourceManifest'],'work/v32-normal/entry-qualified.json','work/v32-normal/prepare-receipt.json',
 'work/v32-normal/seal-client-window.ps1','work/v32-normal/seal-first-observations.py',
 'work/v32-normal/read-final-health.mjs','work/v32-normal/read-physical-final.mjs',
 'work/v32-normal/publish-client-window.py']
assert len(sources)==len(set(sources))==43
hashes={}
for rel in sources:
    assert 'private' not in Path(rel).name.lower()
    data=(w/rel).read_bytes();dest=repo/'code'/rel;dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open('xb') as f:f.write(data)
    hashes[rel]=sha(data)
    manifest['sources'].append({'path':'code/'+rel,'workspaceSource':rel,'sha256':sha(data),'bytes':len(data),'role':'normal-application-bounded-window-and-readonly-closure'})
manifest['lastBoundedApplicationExport']='V32_STEAM_RECOVERY_AND_BOUNDED_WINDOW'
(repo/'source-manifest.json').write_text(dump(manifest),encoding='utf8')
def evidence(name,v):
    with (repo/'evidence'/name).open('x',encoding='utf8') as f:f.write(dump(v))
public_ui=copy.deepcopy(ui);public_ui.pop('privateInputHashes')
evidence('v32-normal-entry-qualification.json',q)
evidence('v32-client-window.json',public_ui)
evidence('v32-normal-restoration.json',{'passed':True,'readonly':True,'fullAudit':audit,
 'physicalQueues':physical,'clientProcessClosure':clients,
 'clientUiSettingsRestoreConfirmed':True,'testDownloadPaused':True,
 'originalDownloadLimitDisabled':True,'noRouterConfigurationWrites':True,
 'newNssSessionStarted':False,'normalFactoryHardwareAcceptance':False,
 'humanExperienceAcceptance':False,'newCpuAcceptance':False,'permanentNssDeployment':False,
 'noNewEndpointOrFixtureStarted':True,'automaticResumeDuringManualUiRestorationPreserved':True,
 'strictCumulativeDownloadDurationNotProven':True})
evidence('v32-normal-source-proof.json',{'passed':True,'baseCommit':base,
 'historicPrefixSources':len(prefix),'historicPrefixCanonicalSha256':sha(json.dumps(prefix,sort_keys=True,separators=(',',':')).encode()),
 'sourceHashes':hashes,'oldCodeAndEvidenceBlobsChecked':len(old),'oldCodeAndEvidenceUnmodified':True,
 'qualificationSourceCopiesExact':36,'privateInputsCopiedExact':len(ui['privateInputHashes']),
 'entryBindings':2687,'selectorModelsReused':18,'actualRefusalModelsReused':14,'modelsReplayed':False,
 'normalFactoryHardwareAcceptance':False,'currentSteamUiSettingsRestoreConfirmed':True,
 'previousV31PartialUiEvidenceUnmodified':True,
 'rawCtNoncesCredentialsConfigurationsCheckpointsBinariesAndProcessCommandLinesExcluded':True,
 'firstWindowDeadlineAndFailuresPreserved':True})
stamp=datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
report=f'''# 正常应用窗口：Steam 恢复、限时下载与真实终态

更新：北京时间 {stamp}。本轮承接用户要求继续推进，并取得一次 Hades 家庭库限时下载许可。Steam 已恢复可用，Hades 下载真实达到约 32Mbps，原 180 秒独立客户端守护自然退出。**正常应用 NSS factory 尚未执行；没有新增 checkpoint、stage、模块加载、ECM、CPU 或真人体验验收。**

## 实際结果

| 项目 | 实际证据与结论 |
| --- | --- |
| Steam 恢复 | 当前已登录且界面可用。之前两次 c0000005/ntdll.dll 启动失败原记录保留，原因未定；本次成功重开不等于长期崩溃问题已修复 |
| 入口接续 | v31 的 pre-stage TCP 选择原义保持；新目录仅改引用路径、本次 10:45 截止和客户端临时 32Mbps 描述。2651＋36＝2687 绑定、57 相对依赖/语法通过，复用既有 18 选择模型及 14 实际拒绝帧模型；未重跑模型或完整 factory |
| 默认 inspect | 在启动游戏/下载前现场只读 0 游戏、0 BULK、0 pair；没有 router 配置写入。这不是负载期间的自动分类证明 |
| 正常下载 | 获用户明确许可后，Hades 选 D 盘、保持快捷方式选项不变，未购买或启动 Hades。界面见 1%/31.9Mbps，临时限速 32000Kbps；PUBG 原更新先前自然完成，Crosshair X 小更新保持已安排 |
| 游戏连接 | Defusal Group Alpha 死斗第一次被 remote host 关闭，发生在 NSS 启动前，根因未知。原守护内只再匹配一次，最后见搜索 00:01；之后未观测到实际连接结果或 jitter/loss/Miss HUD，不能标游戏正常或归因 NSS |
| 客户端期限 | 原守护 180 秒自然到期，精确自有 CS2/Steam 退出，guard/controller/CS2 零残留，未重置期限。重新打开 Steam 作设置恢复时下载自动续传，随后经 UI 暂停，最后网络/磁盘 0bps，下载量显示540.5MB/5% |

**必须区分守护退出和下载总时长。** 守护证明的是这一测试窗口的精确应用退出；手动重开 Steam 的自动续传已保留，未测累计下载秒数，因此不能写成“累计下载严格不超过180秒”。重新打开时先暂停下载，再清空本轮数字、关闭限速，视觉核实原 bit/s 显示、游戏时允许下载和下载地区保持。Hades 部分内容保留，未启动、购买或删除其它内容。

## 当前终态

10:09 的原完整只读 audit 通过，source1.60秒、native审核4 selectors，保护配置/服务epoch/五WAN健康保持，ECM关闭全零；两物理 wan/lan4 的原 mq＋四 fq_codel 所有选项及 handle 一致。没有新端点、fixture、生产配置或 NSS 会话。本轮36份资格源码、11份原始本地输入和完整守护结果已按新目录保存。

当前 Steam UI 设置已恢复，Hades 已暂停，CS2 和本轮测试守护已退出。前一轮 v31 的“原UI未恢复”仍作为当时的真实证据保存，本次新观察单独补充。

## 剩余主线

已成立的 v20 三流多WAN/五WAN队列/DOWN18共享借用/UP60每WAN12硬上限/RT prio0/FQ-CoDel硬件结果和历史CPU结果继续复用。剩余只做一次正常应用 factory：先确认 CS2 已连接，再在新的明确下载许可窗口内开启已暂停内容、独立客户端守护、真实程序三流选择、新 checkpoint下载/SHA/gzip及控制连接外恢复写前核验，随后有界NSS/恢复。下一下载窗口的许可尚待用户回答，不延长原守护或盲重试五流。夜间 heartbeat 保持暂停。

证据：[入口资格](../evidence/v32-normal-entry-qualification.json)、[客户端实际窗口](../evidence/v32-client-window.json)、[终态](../evidence/v32-normal-restoration.json)、[源码保存](../evidence/v32-normal-source-proof.json)。
'''.replace('実際','实际')
with (repo/'docs/NORMAL_WINDOW_2026-10-07.md').open('x',encoding='utf8') as f:f.write(report)
head=f'''# Steam 已恢复；普通应用 NSS 验收尚未完成

更新：北京时间{stamp}。v32承接用户继续推进及一次Hades家庭库限时下载许可，实际约32Mbps；死斗首次被remote host关闭，原180秒守护内只再匹配一次，最终连接/HUD和负载中的程序分类未取得。完整NSS factory、checkpoint/stage/ECM均未启动，不能标硬件/真人验收通过。

新入口2687绑定、57相对依赖/语法通过，数据面及v31的pre-stage TCP选择不变，18＋14模型复用未重跑。旧v31截止/源码/失败保持。本次原180秒客户端守护自然退出，CS2/controller/guard零残留；Steam重开恢复设置时自动续传，随后UI暂停至0bps，显示540.5MB/5%。原限速关闭、空数字、bit/s/游戏中下载/地区保持已视觉核实；累计下载秒数未测，不宣称严格180秒总下载证明。

10:09最后只读原完整audit source1.60/native selectors4、五WAN健康/保护配置/epoch保持、ECM关闭全零；两物理原mq＋四fq_codel全部选项/handle一致。当前Steam可用、下载暂停；v31当时UI未恢复证据单独保留。

v20三流多WAN与五WAN队列/共享借用/RT优先级硬件结果继续复用，普通应用factory仍待一次实际会话。先确认死斗已连接，再开始新的明确下载许可窗口；原180秒期限不重置，续传许可尚待回答。没有新增五WAN同时fast path、长期常驻、CPU或真人体验声明。heartbeat继续暂停。

详情：[本轮报告](NORMAL_WINDOW_2026-10-07.md)、[实际窗口](../evidence/v32-client-window.json)、[终态](../evidence/v32-normal-restoration.json)、[源码](../evidence/v32-normal-source-proof.json)。

## 以下保留原正常入口与夜间记录

'''
for rel in ('AGENTS.md','docs/STATE.md','docs/PLAN.md','docs/EXPERIMENT_LOG.md'):
    p=repo/rel;intro=head
    if rel=='AGENTS.md':intro=intro.replace('(NORMAL_WINDOW_2026-10-07.md)','(docs/NORMAL_WINDOW_2026-10-07.md)').replace('../evidence/','evidence/')
    p.write_bytes(intro.encode()+p.read_bytes())
p=repo/'README.md';intro='''# Athena NSS 多WAN / QoS 受控原型

三流跨WAN和五WAN队列/共享预算已有硬件证明。本次Steam恢复可用、限时下载与客户端退出完成；死斗连接问题发生在NSS前，普通应用factory尚未执行。当前NSS关闭、下载暂停，见[STATE](docs/STATE.md)和[实际窗口报告](docs/NORMAL_WINDOW_2026-10-07.md)。

## 以下保留历史交付

''';p.write_bytes(intro.encode()+p.read_bytes())
with (repo/'.gitattributes').open('a',encoding='utf8') as f:
    f.write('\n# Preserve exact v32 Windows bytes and inherited frozen Lua whitespace.\n')
    for rel in sources:
        if b'\r\n' in (w/rel).read_bytes():f.write('/code/'+rel+' whitespace=cr-at-eol\n')
    f.write('/code/work/v32-normal/fast-path.lua whitespace=cr-at-eol,-blank-at-eol\n')
assert not git('diff','--name-only',base,'--','code','evidence')
assert all(sha((repo/n).read_bytes())==h for n,h in old_bytes.items())
print(json.dumps({'passed':True,'newSources':len(sources),'sourceHashes':len(manifest['sources']),
 'oldCodeEvidenceBlobsPreserved':len(old),'clientUiSettingsRestoreConfirmed':True,
 'normalFactoryHardwareAcceptance':False,'nextDownloadAuthorizationPending':True}))
