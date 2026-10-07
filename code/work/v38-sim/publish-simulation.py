"""Publish the bounded owned game-packet simulation and preserve prior failures."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import copy,hashlib,json,subprocess

w=Path(__file__).resolve().parents[2];repo=w/'athena-nss-mainline';r=w/'work/v38-sim'
base='b44930338420b27366620413b45cee5824bd21db'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
dump=lambda v:json.dumps(v,ensure_ascii=False,indent=2)+'\n'
sha=lambda b:hashlib.sha256(b).hexdigest()
def git(*a):return subprocess.check_output(['git',*a],cwd=repo)
def new(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8') as f:f.write(dump(v))
assert git('rev-parse','HEAD').decode().strip()==base
assert not git('status','--porcelain')
old={n.decode():h.decode().split()[2] for row in git('ls-tree','-r','-z',base,'--','code','evidence').split(b'\0') if row for h,n in [row.split(b'\t',1)]}
old_bytes={n:sha((repo/n).read_bytes()) for n in old}
manifest=read(repo/'source-manifest.json');prefix=copy.deepcopy(manifest['sources']);assert len(prefix)==4083
pilot=w/read(r/'pilot-reference-private.json')['directory'];case=w/read(pilot/'case-reference-private.json')['dir'];closure=w/read(r/'closure-pointer.json')['directory']
hardware=read(r/'hardware-descriptive.json');result=read(pilot/'automatic-result.json');record=read(case/'last-record-private.json');baseline=read(case/'baseline-audit.json');undo=read(case/'stage-undo-verified.json')
audit=read(r/'v36-final-audit.json');physical=read(closure/'physical-final.json');clients=read(closure/'client-closure.json');ui=read(w/'work/v35-normal/client-restoration-observed.json')
assert result['passed'] and hardware['passed'] and hardware['actualHardware']
assert hardware['actualBoundInputs']==2979 and hardware['wanSet']==[3,5]
assert hardware['simultaneouslyAdmittedExactFlowCount']==3 and hardware['renewals']==20 and hardware['ecmCountsThroughoutB']==[3] and hardware['finalEcmCount']==0
assert hardware['phase']['seconds']==60 and hardware['sharedBudgetBorrowingObserved'] and hardware['bulkWithinSharedDownBudget']
assert hardware['rtLeafDrop']=={'down':0,'up':0}
assert hardware['rtEchoDuringInteriorB']['sent']==hardware['rtEchoDuringInteriorB']['returned']==2443 and hardware['rtEchoDuringInteriorB']['unreturned']==0
assert all(hardware['originalRecoveryFlags'].values()) and record['automaticLifecycleEpochCompleted'] and not record['abaCompleted']
assert baseline['configurationMatches'] and all(baseline['checks'].values()) and all(undo.values())
assert audit['passed'] and audit['queryAge']<6 and audit['ecmClosedAndZero'] and audit['protectedConfigurationUnchanged'] and audit['allFiveHealthyWanBaseline'] and audit['serviceEpochPinned']
assert physical['passed'] and physical['defaultQueueOptionsAndHandlesExact']
assert clients['passed'] and clients['ownedTestProcessesRemaining']==clients['cs2ProcessesRemaining']==0
assert len(clients['guards'])==2 and all(x['passed'] and x['clientExitedBeforeDeadline'] and x['exactClientOnly'] and x['originalClientSeconds']==180 and x['independentGuardSeconds']==210 for x in clients['guards'])
assert ui['passed'] and ui['directUiObserved'] and ui['temporaryRateLimitRemoved'] and ui['rateInputClearedBeforeToggle'] and ui['downloadStillPaused'] and ui['cs2ProcessesRemaining']==0
qualifications={scope:read(w/('work/'+scope+'/entry-qualified.json')) for scope in ['v35-normal','v36-sim','v37-sim','v38-sim']}
assert [len(q['sourceManifest']) for q in qualifications.values()]==[44,57,58,58]
assert [q['inheritedBindings'] for q in qualifications.values()]==[2762,2806,2863,2921]
bindings=read(pilot/'actual-entry-bindings.json');assert len(bindings)==2979
for f,h in bindings.items():
 assert sha((w/f).read_bytes())==h,f
 assert sha((pilot/'frozen'/f).read_bytes())==h,f
 assert sha((case/'frozen'/f).read_bytes())==h,f
for scope,q in qualifications.items():
 assert q['passed'] and not q['hardwareExecuted']
 for f,h in q['sourceManifest'].items():assert bindings[f]==h and sha((w/f).read_bytes())==h,f
 for f,h in read(w/('work/'+scope+'/prepare-receipt.json'))['oldHashes'].items():assert sha((w/f).read_bytes())==h,f

r36=w/'work/v36-sim';p36=w/read(r36/'pilot-reference-private.json')['directory'];l36=w/read(r36/'load-latest-private.json')['dir']
failure36=read(p36/'automatic-result.json');client36=read(l36/'result-private.json');close36=read(l36/'endpoint-retry-closure.json');matching36=read(l36/'matching-private.json')
assert not failure36['passed'] and client36['tcpChildren'][1]['bytes']==0
assert 'Connection timed out' in client36['errors'][0] and client36['seconds']<180
assert close36['passed'] and close36['ownedRulesRemaining']==0 and close36['baselineRestored'] and close36['exactOwnedEndpointClosed']
assert not list(r36.glob('session-*/stage-checkpoint-private.json')) and not list(r36.glob('session-*/last-record-private.json'))
r37=w/'work/v37-sim';p37=w/read(r37/'pilot-reference-private.json')['directory'];events37=read(p37/'driver-private.json')
assert not read(p37/'automatic-result.json')['passed'] and len(events37)==1 and events37[0]['code']==1
assert 'regular expression' in events37[0]['stderr'] and 'v36-sim' in events37[0]['stderr']
assert not (r37/'load-latest-private.json').exists()
l38=w/read(r/'load-latest-private.json')['dir'];client38=read(l38/'result-private.json');assert not client38['errors'] and client38['seconds']<=180 and all(x['attempt']==1 and x['connected'] for x in client38['tcpChildren'])
assert read(l38/'endpoint-retry-closure.json')['passed']
first_check=read(closure/'client-check-first-failure/failure.json');assert not first_check['passed'] and first_check['diagnosedAsBroadNamespaceFalsePositive']

sealed=closure/'sealed-simulation-inputs';sealed.mkdir();private_hashes={}
inputs=[pilot/n for n in ['automatic-result.json','actual-entry-bindings.json','driver-private.json','continuity-private.json','case-reference-private.json']]
inputs += [case/n for n in ['last-record-private.json','actual-accelerated-state-proof.json','selected-private.json','source-manifest-preaudit.json','post-checkpoint-controlled-receipt-private.json','post-checkpoint-class-leaf-map-proof.json','stage-checkpoint-private.json','stage-checkpoint-verified.json','stage-plan-private.json','stage-receipt-private.json','stage-undo-verified.json','baseline-audit.json','result.json']]
inputs += [l38/n for n in ['client-config-private.json','client-binding-private.json','result-private.json','guard-result-private.json','firewall-checkpoint-private.json','firewall-checkpoint-verified.json','firewall-receipt-private.json','endpoint-retry-closure.json']]
inputs += [p36/'automatic-result.json',p36/'driver-private.json',l36/'result-private.json',l36/'matching-private.json',l36/'endpoint-retry-closure.json',p37/'driver-private.json',p37/'automatic-result.json',w/'work/v35-normal/game-direct-launch-refusal-private.json',w/'work/v35-normal/client-restoration-observed.json',closure/'client-check-first-failure/owned-process-inventory-private.json',closure/'client-check-first-failure/capture-client-closure.ps1']
for i,p in enumerate(inputs):
 data=p.read_bytes();assert len(data)<=1048576,p.name;dest=sealed/(str(i).zfill(2)+'-'+p.name)
 with dest.open('xb') as f:f.write(data)
 assert dest.read_bytes()==data;private_hashes[str(dest.relative_to(closure)).replace('\\','/')]=sha(data)
new(closure/'sealed-simulation-inputs-private.json',private_hashes)

sources=[]
for scope,q in qualifications.items():sources += [*q['sourceManifest'],'work/'+scope+'/entry-qualified.json','work/'+scope+'/prepare-receipt.json']
sources += ['work/v38-sim/capture-client-closure.ps1','work/v38-sim/analyze-hardware.py','work/v38-sim/publish-simulation.py']
assert len(sources)==len(set(sources));hashes={}
for rel in sources:
 assert 'private' not in Path(rel).name.lower()
 data=(w/rel).read_bytes();dest=repo/'code'/rel;dest.parent.mkdir(parents=True,exist_ok=True)
 with dest.open('xb') as f:f.write(data)
 hashes[rel]=sha(data);manifest['sources'].append({'path':'code/'+rel,'workspaceSource':rel,'sha256':sha(data),'bytes':len(data),'role':'owned-simulated-multiwan-bounded-hardware-and-recovery'})
manifest['lastOwnedSimulationExport']='V38_SIMULATED_RT_TWO_WAN_HARDWARE_COMPLETE';(repo/'source-manifest.json').write_text(dump(manifest),encoding='utf8')
def evidence(n,v):new(repo/'evidence'/n,v)
for scope,q in qualifications.items():evidence(scope+'-entry-qualification.json',q)
evidence('v35-cancelled-normal-attempt.json',{'passedAsPreservedObservation':True,'qualifiedBindings':2806,'localRankingModels':10,'actualRouterRamProbeModels':7,'newNormalHardwareSessionStarted':False,'newCs2AttemptDirectLauncherVacRefused':True,'downloadWasNotResumed':True,'userStoppedCs2Testing':True,'temporarySteamLimitRestored':ui,'actualCs2SteamFactoryAccepted':False,'previousModelFailuresRetainedLocally':True})
evidence('v36-owned-transport-refusal.json',{'passedAsPreservedFailure':True,'fixtureActuallyStarted':True,'permanentClassifierObservedTcpBulk':1,'permanentClassifierObservedUdpRt':1,'secondTcpFirstPayloadBytes':0,'fixtureSecondsBeforeExit':client36['seconds'],'error':'Second owned SSH transport timed out before first payload; subsequent ownership read rejected the exited client','rootCauseEstablished':False,'checkpointStarted':False,'gateLoaded':False,'ecmOpened':False,'controllerOrFirmwareCauseEstablished':False,'originalErrorAndMatchingOutputRetained':True,'endpointRestoration':close36,'independentClientExitPassed':True,'notAnNssBPhase':True})
evidence('v37-local-namespace-refusal.json',{'passedAsPreservedFailure':True,'oldEscapedSessionNamespaceNotRebased':True,'rejectedBeforeRouterConnectionOrPcRead':True,'endpointOrFixtureStarted':False,'checkpointStarted':False,'gateLoaded':False,'ecmOpened':False,'originalQualifiedSourcesAndErrorRetained':True,'fixedInNewV38Namespace':True,'originalV37SourcesNotEdited':True})
evidence('v38-simulated-hardware.json',hardware)
evidence('v38-simulated-restoration.json',{'passed':True,'finalFullAudit':audit,'physicalQueues':physical,'clientClosure':clients,'stageUndo':undo,'protectedBaselineChecks':baseline['checks'],'protectedConfigurationMatches':baseline['configurationMatches'],'endpointRestoration':read(l38/'endpoint-retry-closure.json'),'steamTemporaryLimitRestored':True,'steamRemainedPausedAfterScriptTest':True,'firstClientReadFalsePositivePreserved':first_check,'onlyFailedReadonlyClientStepRecheckedOnce':True,'fullRouterAuditAndPhysicalQueuesNotRepeated':True,'noCs2TestAfterUserStop':True,'humanCs2Acceptance':False,'steamFactoryAcceptance':False,'newCpuAcceptance':False,'permanentNssDeployment':False,'heartbeatStillPaused':True})
evidence('v38-simulated-source-proof.json',{'passed':True,'baseCommit':base,'historicPrefixSources':len(prefix),'historicPrefixCanonicalSha256':sha(json.dumps(prefix,sort_keys=True,separators=(',',':')).encode()),'sourceHashes':hashes,'oldCodeAndEvidenceBlobsChecked':len(old),'oldCodeAndEvidenceUnmodified':True,'actualRuntimeBindingCopiesExact':2979,'privateInputsCopiedExact':len(private_hashes),'qualificationsFrozenExact':True,'v35RamProbeModelsReused':7,'v37BoundedAcquisitionPolicyChecksReused':6,'historicalCpuOrGapExperimentsRepeated':False,'actualAcquisitionRetriesInSuccessfulFixture':0,'transportTimeoutCauseFixedOrEstablished':False,'retryOnlyBeforeNssAdmission':True,'rawCtNoncesCredentialsConfigurationsCheckpointsBinariesAndProcessCommandLinesExcluded':True})

u=hardware['rtEchoDuringInteriorB'];rates=hardware['bulkDownMbps'];stamp=datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
report=f'''# 模拟实时流＋两条下载：跨 WAN NSS 短测通过

更新：北京时间 {stamp}。按用户最新要求停止 CS2 测试，改用自有脚本发送 128 字节双向 UDP，配合两条自有 TCP 下载。**本次在真实路由器上完成 WAN3/WAN5 的 60 秒 NSS 段、20 次续租和完整恢复。**

## 本次结果

- 原常驻自动分类器识别 TCP BULK / UDP RT / TCP BULK；TCP 分别走 WAN3、WAN5，UDP 走 WAN3。没有手工指定分类或改新连接 PBR。
- NSS 段三个确切连接同时加速，ECM 全窗为 3，退役后为 0；双向六个 tag、对应 bulk/RT leaf、完整 ct mark、NAT、WAN affinity 验证通过。
- 五 WAN 队列映射保持上下行各 18 class / 11 leaf；DOWN18 共享预算借用已观察，两个 bulk leaf 在附近异步计数窗口分别约 {rates['tcp']:.2f} / {rates['tcp2']:.2f} Mbps，合计 {hardware['bulkAggregateMbps']:.2f} Mbps。UP60 每 WAN12 硬上限及 RT prio0/FQ-CoDel保持。这里是两 WAN 上三流同时加速。
- 约 {u['interiorSeconds']:.2f} 秒的 NSS 内部窗口，2443 个 UDP 请求全部得到回包，RT 上下行 leaf drop 均为 0。回复统计到自有 fixture 结束；时钟映射不确定度 {u['offsetUncertaintySeconds']:.2f} 秒、两端保守排除边缘。RTT 中位 {u['rttMedianMs']:.2f} ms，P95 {u['rttP95Ms']:.2f} ms，P99 {u['rttP99Ms']:.2f} ms，P95 减中位约 {u['rttP95MinusMedianMs']:.2f} ms。

UDP 配置目标 50 包/秒，内部实际约 {u['sent']/u['interiorSeconds']:.1f} 包/秒；RTT包含自有海外端点路径，抖动描述来自脚本回包。它不提供 CS2 HUD 的 jitter/loss/Miss 或真人体感。TCP 提供负载目标为 24＋8＝32Mbps，附近异步 leaf 速率不作为长期限速精度或新 CPU 对照。

## 已保留的失败和修正

v35 的选择排序与失败帧保存已完成 10 本地 / 7 目标 RAM 模型，2806 绑定；用户停止 CS2 后没有运行新的普通应用 NSS 会话。直接启动游戏曾被 VAC 签名检查拒绝，未进服、未恢复下载；临时 Steam 32000Kbps 数值清空、限速关闭，原下载仍暂停。

v36 第一轮自有负载的第二条 SSH 下载首包为 0，约 {client36['seconds']:.2f} 秒后超时。第一 TCP 和 UDP 正常，原分类曾见一 BULK/一 RT；该轮在 checkpoint / gate / ECM 前结束，原错误、匹配帧、独立客户端退出与端点恢复全部保留。不能归因 NSS、固件或学校网络。

后续只给自有未准入 TCP 增加 8 秒首包等待、最多 3 次且总计前 30 秒内的连接取得；准备配对成功就冻结，已有 payload 或已准入阶段不自动重连，不延长 180 秒客户端期限，也不改防火墙来源。v37 本地新目录的转义路径漏改，连接前拒绝，原源码及错误保存；v38 对普通路径和正则转义一并接续，2979 实际绑定冻结。本次两 TCP 均第一次连接成功，新的重连分支未实际触发，不能宣称超时根因已修复。

## 完整恢复

独立撤销、模块卸载、tag 删除、两物理原队列、WAN/mwan3 与状态目录清理通过。最终原完整只读 audit source {audit['queryAge']:.2f} 秒、native selectors {audit['selectors']} 通过，五 WAN 健康、保护配置/服务 epoch 保持，ECM 关闭全零。wan/lan4 原 mq＋四 fq_codel 的全部选项和 handle 精确恢复。两个自有端点临时规则为 0、canonical 防火墙基线一致、确切端点关闭；客户端、controller、guard、SSH sender 均无残留，CS2为0，Steam保持暂停且限速恢复。

首次本机退出读取因宽泛目录匹配误把只读检查的父进程计入残留，原输出/源码已保留；核实不是 fixture、pilot 或 guard 后，仅重查这一失败的只读步骤一次通过。没有重跑 NSS 或完整网络审核。heartbeat保持暂停，未改电源计划。

## 后续范围

**受控模拟实时流的两 WAN NSS 功能验收通过。** v1及v20既有功能/CPU证据继续复用。本次只有一个 B 段，软件进入和结束恢复均通过；不把它写成新的 CPU A/B/A2、Steam正常应用factory或真人游戏验收。

后续主线可继续使用脚本模拟游戏包；不再把启动 CS2 当作继续测试的前提。本轮到此封存，不因未复现的 SSH 超时继续重试。五 WAN 同时 fast path、多流公平、长期/永久运行、Wi-Fi/autorate/ECN与其余高级QoS扩展留后续范围；当前没有永久启用 NSS。

证据：[硬件及回包](../evidence/v38-simulated-hardware.json)、[完整终态](../evidence/v38-simulated-restoration.json)、[源码保存](../evidence/v38-simulated-source-proof.json)、[首次传输失败](../evidence/v36-owned-transport-refusal.json)、[本地目录拒绝](../evidence/v37-local-namespace-refusal.json)。
'''
with (repo/'docs/SIMULATED_MULTIWAN_2026-10-07.md').open('x',encoding='utf8') as f:f.write(report)
intro=f'''# 模拟实时流跨 WAN NSS 验收通过，完整恢复

更新：北京时间{stamp}。用户已停止 CS2 测试，后续使用自有脚本模拟游戏包。v38 实际 TCP BULK/UDP RT/TCP BULK走 WAN3/WAN3/WAN5；原自动分类、60秒 NSS / ECM3 / 20续租、双向六tag与bulk/RT leaf / mark / NAT / affinity通过。DOWN18共享借用保持，附近两个bulk约{rates['tcp']:.2f}/{rates['tcp2']:.2f}Mbps；内部约{u['interiorSeconds']:.2f}秒发出2443 UDP，全部回包，RT上下leaf零drop，RTT中位/P95/P99约{u['rttMedianMs']:.2f}/{u['rttP95Ms']:.2f}/{u['rttP99Ms']:.2f}ms。是自有海外回包测量，非CS2 HUD/真人或新CPU证明。

新checkpoint下载SHA/gzip、原独立恢复写前通过；最终source{audit['queryAge']:.2f}/selectors{audit['selectors']}审核、五WAN健康/保护配置/epoch保持，ECM关闭全零，两物理原mq＋四fq_codel所有选项/handle、端点FW基线、客户端/guard/sender完整恢复。Steam原下载暂停/临时限速关闭，CS2为0。常驻仍NSS68原config；没有永久NSS。

v35已做10本地/7RAM选择与失败帧修正但普通程序factory未执行；v36第二自有SSH首包超时在NSS前退出，v37本地转义目录拒绝在连接前结束，原失败不改。v38只有8秒/最多3次/前30秒未准入自有TCP取得；成功轮均attempt1，超时根因未知。2979实际绑定冻结，重查一次本机只读退出检查的父进程误报；未重做网络/NSS/CPU/gap或五流。

**受控模拟实时流的两WAN功能验收已完成。** 既有v1/v20与CPU证据复用；以后直接用脚本推进，CS2不再是必需条件。本轮封存、heartbeat仍暂停，不主动开启新轮次；五WAN同时fast path/长期常驻/多流公平/WiFi/autorate/ECN保留后续范围。

详情：[本次报告](SIMULATED_MULTIWAN_2026-10-07.md)、[硬件](../evidence/v38-simulated-hardware.json)、[终态](../evidence/v38-simulated-restoration.json)。

## 以下保留历史记录

'''
for rel in ['AGENTS.md','docs/STATE.md','docs/PLAN.md','docs/EXPERIMENT_LOG.md']:
 p=repo/rel;text=intro
 if rel=='AGENTS.md':text=text.replace('(SIMULATED_MULTIWAN_2026-10-07.md)','(docs/SIMULATED_MULTIWAN_2026-10-07.md)').replace('../evidence/','evidence/')
 p.write_bytes(text.encode()+p.read_bytes())
p=repo/'README.md';p.write_bytes(('''# Athena NSS 多WAN / 高级QoS受控原型

最新脚本模拟实时流＋两条下载已完成 WAN3/WAN5 的60秒真实NSS和恢复，内部2443个UDP全部回包。后续使用模拟游戏包，CS2不再是测试前提。当前完整恢复、没有永久启用NSS，见[STATE](docs/STATE.md)与[实际报告](docs/SIMULATED_MULTIWAN_2026-10-07.md)。

## 以下保留历史交付

''').encode()+p.read_bytes())
with (repo/'.gitattributes').open('a',encoding='utf8') as f:
 f.write('\n# Preserve exact new owned-simulation sources, without rewriting historical evidence.\n')
 for rel in sources:
  if b'\r\n' in (w/rel).read_bytes():f.write('/code/'+rel+' whitespace=cr-at-eol\n')
 for scope in qualifications:f.write('/code/work/'+scope+'/fast-path.lua whitespace=cr-at-eol,-blank-at-eol\n')
assert not git('diff','--name-only',base,'--','code','evidence')
assert all(sha((repo/n).read_bytes())==h for n,h in old_bytes.items())
print(json.dumps({'passed':True,'newSources':len(sources),'sourceHashes':len(manifest['sources']),'oldCodeEvidenceBlobsPreserved':len(old),'actualRuntimeBindingsExact':2979,'privateInputCopiesExact':len(private_hashes),'simulatedMultiWanHardwarePassed':True,'cs2Acceptance':False,'firstRefusalsPreserved':True}))
