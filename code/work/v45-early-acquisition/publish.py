from pathlib import Path
from datetime import datetime, timezone, timedelta
import copy, hashlib, html, json, re, subprocess

w=Path(__file__).resolve().parents[2];repo=w/'athena-nss-mainline';root=w/'work/v45-early-acquisition'
base='f3a4287094633477487682ff137465c9b1fcbc66'
sha=lambda b:hashlib.sha256(b).hexdigest()
def read(p):
    data=p.read_bytes()
    return json.loads(data.decode('utf16' if data.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8-sig'))
dump=lambda v:json.dumps(v,ensure_ascii=False,indent=2)+'\n'
git=lambda *args:subprocess.check_output(['git','-C',str(repo),*args])
def new(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf8') as f:f.write(dump(v))
assert git('rev-parse','HEAD').decode().strip()==base and not git('status','--porcelain')
manifest=read(repo/'source-manifest.json');prefix=copy.deepcopy(manifest['sources']);assert len(prefix)==4757
old={}
for row in git('ls-tree','-r','-z',base,'--','code','evidence').split(b'\0'):
    if row:
        _,name=row.split(b'\t');old[name.decode()]=sha((repo/name.decode()).read_bytes())

model_path=w/read(root/'entry-model-latest-private.json')['receipt'];model=read(model_path)
assert model['passed'] and model['modelOnly'] and len(model['checks'])==24 and model['sourceBindings']==3406
assert not model['hardwareExecuted'] and not model['routerWrites'] and not model['trafficGenerated']
for rel,h in model['sourceHashes'].items():assert sha((w/rel).read_bytes())==h,rel
inspect=read(root/'inspect-stdout-private.txt');assert inspect['passed'] and not inspect['trafficGenerated'] and not inspect['routerWrites']
idle=read(root/'prior-owned-idle-private.json');assert idle['passed'] and idle['ownedPriorNodes']==0
assert read(root/'single-integrated-attempt-private.json')['attemptedExactlyOnce']
assert read(root/'integrated-exit-private.json')['code']==1
active=read(root/'active-private.json');actual=w/active['runtimeRoot']
assert active['state']=='RESTORED' and active['restorationPassed'] and not active['hardwareCompleted'] and not (root/'active-lock').exists()
result=read(actual/'entry-result-private.json');assert result['state']=='RESTORED' and result['supervisorExitCode']==1
pilot=w/read(actual/'pilot-reference-private.json')['directory'];events=read(pilot/'driver-private.json')
assert [e['code'] for e in events]==[0,1] and 'port 22 timed out' in events[1]['stderr']
assert not (actual/'load-latest-private.json').exists() and not (pilot/'case-reference-private.json').exists() and not (pilot/'detached-owner-reference-private.json').exists()
partial=list(actual.glob('load-*'));assert len(partial)==1 and partial[0].is_dir()
assert not (partial[0]/'server-checkpoint-private.json').exists() and not (partial[0]/'server-deadline-private.json').exists()
assert not (partial[0]/'client-config-private.json').exists() and not (partial[0]/'launch-receipt.json').exists()
starter=(actual/'start-dallas.mjs').read_text(encoding='utf8')
assert starter.index("checkpoint=await ssh('ss -H -lntup")<starter.index("await ssh('systemd-run")<starter.index("save('client-config-private'")
closure=w/read(actual/'closure-pointer.json')['directory'];audit=read(closure/'final-audit-stdout-private.txt');physical=read(closure/'physical-final.json')
assert audit['passed'] and audit['queryAge']<6 and audit['ecmClosedAndZero'] and audit['protectedConfigurationUnchanged'] and audit['allFiveHealthyWanBaseline']
assert physical['passed'] and physical['defaultQueueOptionsAndHandlesExact']
diagnostic=read(root/'endpoint-diagnostic-summary.json');assert diagnostic['onlyOneDiagnostic'] and diagnostic['endpointReadbackPassed'] and diagnostic['localOwnedFixtureNodes']==0 and not diagnostic['fixtureReopened']
assert diagnostic['remoteSummary']['ownedEndpointPortRows']==diagnostic['remoteSummary']['currentEntryUnitRows']==0
assert sha((root/'endpoint-diagnostic-raw-private.json').read_bytes())==diagnostic['rawSha256']
prior_archive=read(w/'work/v44-bounded-entry/publication-20261007T093903-d9945c61/published-night-receipt.json')
assert prior_archive['passed'] and prior_archive['commit']==base and prior_archive['remoteCommitMatched'] and prior_archive['actualGitArchiveChecked']

bindings=read(pilot/'actual-entry-bindings.json');assert len(bindings)==3406
for rel,h in bindings.items():
    data=(w/rel).read_bytes();assert sha(data)==h and (pilot/'frozen'/rel).read_bytes()==data,rel
runtime_roots=[actual,w/model['modelRuntimeRoot']]
for p in sorted((w/'work').glob('v45-run-*/entry-qualified.json')):
    q=read(p)
    if p.parent in runtime_roots:continue
    if q['sourceManifest'].get('work/v45-early-acquisition/check-model.mjs')==model['sourceHashes']['work/v45-early-acquisition/check-model.mjs']:
        runtime_roots.append(p.parent)
assert len(runtime_roots)==3
sources=set();runtime_sets={}
lua_names=['fast-path.lua','classifier.lua','classified-tags.lua','module-stage-guardian.lua','qos-physical.lua','wan-scope.lua','tag-normalizer.lua']
for r in runtime_roots:
    q=read(r/'entry-qualified.json');assert q['passed'] and q['actualBindings']==3406 and len(q['sourceManifest'])==52 and q['inheritedBindings']==3354
    assert q['dataPlaneByteExact'] and q['classificationAndQosPolicyUnchanged']
    for rel,h in q['sourceManifest'].items():assert sha((w/rel).read_bytes())==h,rel
    for name in lua_names:assert (r/name).read_bytes()==(w/'work/v42-counter-window'/name).read_bytes(),name
    sources.update(q['sourceManifest'])
    runtime_sets[r.relative_to(w).as_posix()]={'sourceHashes':q['sourceManifest'],'actualBindings':3406,'inheritedBindings':3354,'sevenLuaByteExactV42':True,'fixtureTrafficGenerated':False}
sources.update((root/name).relative_to(w).as_posix() for name in ['preparation.json','run-once.py','diagnose-endpoint-readonly.mjs','publish.py'])
sources.add('work/v45-prepare-early-acquisition.py')
failure_dir=root/'model-refusal-202610071758'
failure=read(failure_dir/'failure.json');assert not failure['passed'] and failure['beforeFixtureAndSsh']
sources.update((failure_dir/name).relative_to(w).as_posix() for name in ['check-model-original.mjs','failure.json'])

# Correct the previous report label from its existing actual owned socket mapping.
old_runtime=w/'work/v44-run-20261007092055-97375ff9';frame=read(old_runtime/'controlled-candidates-private.json')
old_public=read(repo/'evidence/v44-bounded-entry.json')
assert sha((old_runtime/'controlled-candidates-private.json').read_bytes())==old_public['inputSha256ByRole']['v44-last-classification-frame']
slot_rows=[]
for slot in ['tcp','tcp2','tcp3','tcp4']:
    found=[f for f in frame['tcp'] if f['identity']['original']['sport']==frame['ownedTcpSlots'][slot]]
    assert len(found)==1;f=found[0];slot_rows.append({'slot':slot,'class':f['decision']['class'],'wan':f['identity']['wan']})
assert [x['wan'] for x in slot_rows]==[4,2,1,1] and all(x['class']=='BULK' for x in slot_rows)
assert [x['identity']['wan'] for x in frame['tcp']]==[1,1,2,4] and frame['udp'][0]['identity']['wan']==3

indexed={x['workspaceSource']:x for x in manifest['sources']};new_sources={}
for rel in sorted(sources):
    data=(w/rel).read_bytes()
    if rel in indexed:assert sha(data)==indexed[rel]['sha256'];continue
    p=repo/'code'/rel;p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb') as f:f.write(data)
    new_sources[rel]=sha(data)
    manifest['sources'].append({'path':'code/'+rel,'workspaceSource':rel,'sha256':sha(data),'bytes':len(data),'role':'v45-earlier-owned-acquisition-candidate-and-preload-ssh-refusal'})
inputs={'models':model_path,'default-inspect':root/'inspect-stdout-private.txt','prior-idle':root/'prior-owned-idle-private.json',
        'entry-original-result':actual/'entry-result-private.json','supervisor-events':pilot/'driver-private.json','actual-bindings':pilot/'actual-entry-bindings.json',
        'supervisor-original-output':actual/'entry-supervisor-raw-private.json','final-audit':closure/'final-audit-stdout-private.txt',
        'physical-options':closure/'physical-final-raw-private.json','physical-result':closure/'physical-final.json',
        'endpoint-readonly-raw':root/'endpoint-diagnostic-raw-private.json','endpoint-readonly-summary':root/'endpoint-diagnostic-summary.json',
        'local-process-readback':root/'endpoint-diagnostic-local-idle-raw-private.json','prior-published-archive':w/'work/v44-bounded-entry/publication-20261007T093903-d9945c61/published-night-receipt.json',
        'prior-v44-frame':old_runtime/'controlled-candidates-private.json','first-model-refusal':failure_dir/'failure.json'}
sealed=root/'sealed-inputs-private';sealed.mkdir();sealed_hashes={}
for role,p in inputs.items():
    data=p.read_bytes();target=sealed/(role+p.suffix)
    with target.open('xb') as f:f.write(data)
    assert target.read_bytes()==data;sealed_hashes[role]=sha(data)
new(sealed/'manifest-private.json',sealed_hashes)
new(repo/'evidence/v45-entry-startup.json',{
 'softwareQualificationPassed':True,'modelCount':24,'modelChecks':model['checks'],'modelSourceHashes':model['sourceHashes'],
 'actualBindings':3406,'inheritedBindings':3354,'limits':model['limits'],'sevenLuaByteExactV42':True,
 'sameFourInitialTcpChildrenStartConcurrently':True,'earlyReadinessIsOnlyFourUniqueOwnedPids':True,
 'finalFirstPayloadCimSocketCtClassAndFiveWanSelectionUnchanged':True,'originalAcquisitionDeadlineNotReset':True,
 'originalTcpRetryAndRotationPolicyUnchanged':True,'classificationQosAndAllSafetyCapsUnchanged':True,
 'previousV44SerialStartupSeconds':{'allPids':16.0071,'allFirstPayload':18.8794},
 'defaultInspectExecuted':True,'firstModelAssertionFailurePreserved':True,'firstModelFailureWasWrongErrorLiteral':True,
 'entryAttemptCount':1,'fixtureAttemptCount':0,'failureCategory':'ENDPOINT_CONTROL_SSH_CONNECTION_TIMEOUT_BEFORE_ENDPOINT_CREATION',
 'driverEventCodes':[0,1],'endpointRemoteCheckpointCreated':False,'endpointCreated':False,'clientCreated':False,
 'checkpointStarted':False,'nssStageStarted':False,'ecmOpened':False,'entryHardwareIntegrationPassed':False,
 'earlyStartupHardwareExecuted':False,'exactOneReadonlyEndpointDiagnostic':True,'endpointReadbackRecovered':True,
 'sshRootCauseProved':False,'sshTimeoutClaimedFixed':False,'newFixtureRetryPerformed':False,
 'restorationState':'RESTORED','originalFailureRetained':True,'newCpuAcceptance':False,'cs2OrSteamOperated':False,
 'permanentNssDeployment':False,'v42HardwareAcceptanceRetained':True,'v41KnownLimitationStillOpen':True,
 'inputSha256ByRole':sealed_hashes})
new(repo/'evidence/v45-restoration.json',{
 'passed':True,'finalFullAudit':audit,'physicalQueues':physical,'originalFinalAuditLabelUnique':True,
 'endpointNeverCreatedThisEntry':True,'endpointReadonlyReadback':diagnostic['remoteSummary'],
 'clientNeverCreatedThisEntry':True,'ownedEntryFixtureNodesRemaining':0,'sameEntryNoReadonlySupplementNeeded':True,
 'activeLockReleasedAfterProof':True,'mutableLedgerState':'RESTORED','hardwareCompleted':False,
 'noFixtureReopened':True,'heartbeatStillPaused':True,'classifierNss68Unchanged':True,'permanentNssDeployment':False})
new(repo/'evidence/v44-slot-order-correction.json',{
 'existingFrozenFrameReadOnly':True,'priorFrameSha256':sealed_hashes['prior-v44-frame'],
 'originalPublicV44RecordUnchanged':True,'incorrectFieldLabel':'tcpWanSetInSlotOrder',
 'originalValuesWereNativeArrayOrder':[1,1,2,4],'correctOwnedSlotRows':slot_rows,'udpWan':3,
 'correctedByExactOwnedLocalSocketPortMapping':True,'completeTupleStayedLocal':True,
 'v44NoFiveWanPairAndPreNssRefusalConclusionUnchanged':True,'noNewTraffic':True})
attributes=[]
for rel in new_sources:
    data=(w/rel).read_bytes();options=[]
    if b'\r\n' in data:options.append('cr-at-eol')
    if re.search(rb'[ \t]+\r?$',data,re.M):options.append('-blank-at-eol')
    if re.search(rb'(?:\r?\n){2,}$',data):options.append('-blank-at-eof')
    if options:attributes.append('/code/'+rel+' whitespace='+','.join(options))
if attributes:
    p=repo/'.gitattributes';p.write_text(p.read_text(encoding='utf8')+'\n# Keep exact new v45 source and original model-refusal bytes.\n'+'\n'.join(attributes)+'\n',encoding='utf8')
new(repo/'evidence/v45-source-proof.json',{
 'passed':True,'historicPrefixSources':4757,'newSources':len(new_sources),'sourceHashes':new_sources,
 'runtimeSourceSets':runtime_sets,'oldCodeAndEvidenceBlobsChecked':len(old),'oldCodeAndEvidenceUnmodified':True,
 'actualBindingSetFrozenExact':3406,'privateInputsCopiedExact':len(sealed_hashes),'inputSha256ByRole':sealed_hashes,
 'modelSyntheticClientPointerNotMistakenForProduction':True,'onlyOneEntryAttempt':True,'noFixtureTrafficGenerated':True,
 'originalV44FailureAndReportUnchanged':True,'exactPathAttributes':attributes,'noGlobalWhitespacePolicyChange':True})
manifest['generatedAt']=datetime.now(timezone.utc).isoformat()
manifest['lastEarlyAcquisitionExport']='V45_SOFTWARE_READY_PRELOAD_SSH_REFUSED_RESTORED'
assert manifest['sources'][:4757]==prefix
(repo/'source-manifest.json').write_text(dump(manifest),encoding='utf8')
now=datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
report=f'''# v45 提前取得入口：软件检查通过，端点连接前置失败

北京时间{now}。本次接续用户“继续”，只修改四条自有TCP的初始启动时序和取得阶段的进程就绪条件；没有操作CS2、Steam或下载游戏。v42五WAN高级QoS的已有硬件功能证据保留。

## 改动及验证

原v44逐条等待首包后再启动下一条TCP，四个PID齐备约16.01秒，四条首包齐备约18.88秒；原30秒自然取得窗口的有效观察时间因此缩短。v45让相同四条初始SSH连接同时启动，四个唯一自有PID发布后可提前进行原CIM/socket/真实CT/WAN核对。进程就绪只允许提前观察；最终进入NSS仍需四条真实BULK、一条已准入RT、四条首包、五个不同WAN、完整身份/mark/NAT/affinity及原checkpoint/独立恢复。

24项入口模型与默认inspect通过，3406绑定=原3354+52。七Lua、原32Mbps/64KiB、180秒客户端/210守护/250端点、30秒取得/8候选及source6/kernel90最大120/owner180和各字节上限保持。首次模型断言误用了另一文件的错误文本，原失败代码和记录保留后更正；没有现场流量。

## 唯一一次实际入口

原完整前置审核通过。端点控制SSH随后连接超时（exit255），在第一条只读端点checkpoint命令返回前退出。本地只创建了准备目录；无端点checkpoint/deadline、远端服务、防火墙写、客户端配置/launch、负载指针、NSS checkpoint/owner/stage/ECM。**实际入口尝试1次，fixture流量0次；新启动时序的现场作用尚未验证，完整可复用入口验收仍未通过。**

只做一次失败相关的只读端点诊断，SSH已能连接，精确端口占用0、本次单位0，自有fixture进程0。不能因此宣称SSH超时已修复或确定根因；没有重新开启fixture碰运气。

## 最终状态

本次入口直接完成最终审核，无额外恢复补轮：source {audit['queryAge']:.2f}秒 / selectors {audit['selectors']}，五WAN健康、保护配置不变、ECM关闭全零；wan/lan4原mq＋四fq_codel的全部选项/handle一致。独占锁解除，ledger RESTORED。常驻NSS68/config不变，heartbeat继续暂停，没有永久部署。

## 前次报告标注更正

v44旧记录字段`tcpWanSetInSlotOrder:[1,1,2,4]`实际是native数组顺序。用同一冻结完整帧的自有socket本地端口映射，真实槽顺序为TCP1 WAN4、TCP2 WAN2、TCP3 WAN1、TCP4 WAN1，UDP WAN3。原证据和报告字节保持；本页和新更正证据说明标注错误。未配齐五WAN和NSS写前退出的原结论不变，不是WAN affinity变化。

## 使用范围与后续

五WAN核心功能继续采用v42实测：60.01秒、ECM5、20续租、2373/2373模拟RT回包、十tag/leaf/CT/mark/NAT/affinity和完整恢复；DOWN18共享借用、UP60每WAN12硬上限、RT prio0/FQ-CoDel。v45是有界显式入口的软件候选，尚未证明自动整合稳定或长期/永久/全网可用。新一次整合须有新的可执行条件和用户授权；不自动开新轮，不放宽取得期限/认证/PBR。v41计数差异、偶发SSH连接超时、自然WAN未配齐及普通应用factory未验保留为限制；连续新代、长期部署、WiFi/autorate/ECN仍在v1.1/v2。

证据：[入口](../evidence/v45-entry-startup.json)、[终态](../evidence/v45-restoration.json)、[v44标注更正](../evidence/v44-slot-order-correction.json)、[源码与冻结](../evidence/v45-source-proof.json)、[入口使用](BOUNDED_MULTIWAN_ENTRY.md)、[v42硬件](FIVE_WAN_SIMULATED_ACCEPTANCE_2026-10-07.md)。
'''
(repo/'docs/V45_EARLY_ACQUISITION_2026-10-07.md').write_text(report,encoding='utf8')
header=f'''# v45提前取得候选通过，端点SSH写前拒绝；完整恢复

更新：北京时间{now}。原v44发布`{base}`已实际archive读回4757源SHA/5419文件/1462链接。v45同样四条TCP同时启动、四个唯一PID发布后提前核对，24模型/默认inspect/3406绑定通过；最终首包、CIM/socket/CT、4BULK＋1RT、五WAN及全部原期限/恢复条件保持，七Lua原字节。

唯一入口尝试在端点控制SSH连接超时处退出，第一条只读端点checkpoint未返回，无端点/FW/client、fixture/NSS checkpoint/owner/stage/ECM。原失败保留；一次失败相关只读诊断恢复连接，端口/本次单位/自有fixture进程0；不能据此宣称SSH已修复。没有盲重开fixture，新启动时序尚未现场验证，完整可复用入口验收仍未通过。

本次最终审核直接通过：source{audit['queryAge']:.2f}/selectors{audit['selectors']}，五WAN健康/保护配置不变/ECM关闭全零，两物理原mq＋四fq_codel所有选项/handle一致，RESTORED/锁解除。常驻NSS68不变，无CS2/Steam、新CPU或永久部署，heartbeat保持暂停。

更正v44旧字段标注：原TCP WAN1/1/2/4是native数组顺序，冻结socket映射的真实槽顺序为4/2/1/1、UDP3；原失败/证据/报告不改，五WAN未齐与写前拒绝结论保持。v42五WAN60.01秒/ECM5/20续租/2373RT全回的核心硬件证明继续成立。

本轮封存，不自动新增实验。新的显式整合需新可执行条件；SSH连接超时、自然取得限制、v41计数差异和普通应用未验仍记录为已知限制。详情：[本次记录](V45_EARLY_ACQUISITION_2026-10-07.md)、[入口使用](BOUNDED_MULTIWAN_ENTRY.md)。

## 以下保留历史记录；旧“最新”仅代表当时

'''
for name in ['docs/STATE.md','docs/PLAN.md','docs/EXPERIMENT_LOG.md','AGENTS.md']:
    p=repo/name;text=header
    if name=='AGENTS.md':text=text.replace('(V45_EARLY_ACQUISITION_2026-10-07.md)','(docs/V45_EARLY_ACQUISITION_2026-10-07.md)').replace('(BOUNDED_MULTIWAN_ENTRY.md)','(docs/BOUNDED_MULTIWAN_ENTRY.md)')
    p.write_text(text+p.read_text(encoding='utf8'),encoding='utf8')
for name,lead in {
 'README.md':'''# Athena NSS 多WAN / 高级QoS受控原型

五WAN核心硬件功能已验收。v45有界入口的软件检查24项通过，实际入口因端点SSH连接超时在任何fixture或NSS写前退出；完整恢复，最新入口现场整合尚未通过。没有操作CS2/Steam，没有永久开启NSS。见[本次进展](docs/V45_EARLY_ACQUISITION_2026-10-07.md)、[STATE](docs/STATE.md)。
''',
 'docs/BOUNDED_MULTIWAN_ENTRY.md':'''# 可复用的有界入口：v45提前取得软件候选

当前本地候选`work/v45-early-acquisition/entry.mjs`，命令仍为默认inspect / status / run / stop。24模型、默认inspect和实际最终恢复通过；唯一run在端点控制SSH连接超时处写前退出，未生成fixture流量，新启动时序尚未现场验证。核心五WAN数据面已由v42验收；完整最新入口整合仍未通过，勿自动盲重试。

```powershell
& 'C:/Users/lishu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe' 'work/v45-early-acquisition/entry.mjs' inspect
& 'C:/Users/lishu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe' 'work/v45-early-acquisition/entry.mjs' status
```

同样四条初始自有TCP并发启动，四个唯一自有PID发布后提前观察实际WAN；最终四首包、CIM/socket/CT完整身份、4BULK＋1RT、五WAN、source6/原30秒取得和checkpoint/独立恢复保持。60秒B、kernel90最大120/owner180/client180/guard210/server250、32Mbps/64KiB和所有字节预算不变。stop只控制同session自有发送与下一准入，恢复未确认不得重开。

已保留v44唯一最终label修复。旧v44 WAN列表是native数组顺序，真实自有槽为4/2/1/1、UDP3；原记录不改，见[本次记录与更正](V45_EARLY_ACQUISITION_2026-10-07.md)。
''',
 'docs/MULTI_WAN_QOS.md':'''# 多 WAN / 高级 QoS 当前交付范围

v42五WAN五流60.01秒/ECM5/20续租、2373/2373模拟RT回包、十tag/leaf/完整mark/NAT/affinity与恢复已验收。DOWN18共享借用、UP60每WAN12硬上限、RT prio0/FQ-CoDel保持，本次七Lua原字节。

v45入口的24模型/默认inspect通过；实际run因端点SSH连接超时写前退出，fixture和NSS均未启动，最终完整恢复。并发取得候选尚未现场验证，完整可复用入口尚未验收。偶发SSH超时、自然WAN未齐、v41计数差异及普通程序factory未验仍是限制；永久、长期、全网、连续新代、WiFi/autorate/ECN留后续。见[本次记录](V45_EARLY_ACQUISITION_2026-10-07.md)。
'''}.items():
    p=repo/name;p.write_text(lead+'\n## 以下保留历史描述，当前状态以上文为准\n\n'+p.read_text(encoding='utf8'),encoding='utf8')
checker=repo/'tools/check_repository.py';text=checker.read_text(encoding='utf8')
needle="print(json.dumps({'passed':True,'filesChecked':count";assert text.count(needle)==1
checks='''if (root/'evidence/v45-entry-startup.json').exists():
 a=json.loads((root/'evidence/v45-entry-startup.json').read_text(encoding='utf8'))
 r=json.loads((root/'evidence/v45-restoration.json').read_text(encoding='utf8'))
 c=json.loads((root/'evidence/v44-slot-order-correction.json').read_text(encoding='utf8'))
 s=json.loads((root/'evidence/v45-source-proof.json').read_text(encoding='utf8'))
 assert manifest['lastEarlyAcquisitionExport']=='V45_SOFTWARE_READY_PRELOAD_SSH_REFUSED_RESTORED'
 assert a['softwareQualificationPassed'] and a['modelCount']==len(a['modelChecks'])==24 and a['actualBindings']==3406 and a['inheritedBindings']==3354
 assert a['entryAttemptCount']==1 and a['fixtureAttemptCount']==0 and a['driverEventCodes']==[0,1]
 assert a['failureCategory']=='ENDPOINT_CONTROL_SSH_CONNECTION_TIMEOUT_BEFORE_ENDPOINT_CREATION'
 assert a['earlyReadinessIsOnlyFourUniqueOwnedPids'] and a['finalFirstPayloadCimSocketCtClassAndFiveWanSelectionUnchanged'] and a['originalAcquisitionDeadlineNotReset']
 assert a['classificationQosAndAllSafetyCapsUnchanged'] and a['originalFailureRetained'] and a['firstModelAssertionFailurePreserved'] and a['v42HardwareAcceptanceRetained']
 assert not any(a[k] for k in ['endpointRemoteCheckpointCreated','endpointCreated','clientCreated','checkpointStarted','nssStageStarted','ecmOpened','entryHardwareIntegrationPassed','earlyStartupHardwareExecuted','sshRootCauseProved','sshTimeoutClaimedFixed','newFixtureRetryPerformed','newCpuAcceptance','cs2OrSteamOperated','permanentNssDeployment'])
 assert a['exactOneReadonlyEndpointDiagnostic'] and a['endpointReadbackRecovered'] and a['restorationState']=='RESTORED'
 assert r['passed'] and r['endpointNeverCreatedThisEntry'] and r['clientNeverCreatedThisEntry'] and r['ownedEntryFixtureNodesRemaining']==0 and r['noFixtureReopened'] and r['activeLockReleasedAfterProof']
 q=r['finalFullAudit'];assert q['passed'] and q['queryAge']<6 and q['ecmClosedAndZero'] and q['allFiveHealthyWanBaseline'] and q['protectedConfigurationUnchanged']
 assert r['physicalQueues']['defaultQueueOptionsAndHandlesExact'] and r['endpointReadonlyReadback']['ownedEndpointPortRows']==r['endpointReadonlyReadback']['currentEntryUnitRows']==0
 assert c['existingFrozenFrameReadOnly'] and c['originalPublicV44RecordUnchanged'] and c['originalValuesWereNativeArrayOrder']==[1,1,2,4] and [x['wan'] for x in c['correctOwnedSlotRows']]==[4,2,1,1] and c['udpWan']==3
 assert c['correctedByExactOwnedLocalSocketPortMapping'] and c['v44NoFiveWanPairAndPreNssRefusalConclusionUnchanged'] and c['noNewTraffic']
 assert s['passed'] and s['historicPrefixSources']==4757 and s['newSources']==len(s['sourceHashes']) and s['oldCodeAndEvidenceUnmodified'] and s['actualBindingSetFrozenExact']==3406 and s['noFixtureTrafficGenerated'] and s['noGlobalWhitespacePolicyChange']
 for entry in [a['modelSourceHashes'],s['sourceHashes']]:
  for rel,digest in entry.items():assert hashlib.sha256((root/'code'/rel).read_bytes()).hexdigest()==digest,rel
 for runtime,value in s['runtimeSourceSets'].items():
  assert value['actualBindings']==3406 and value['inheritedBindings']==3354 and len(value['sourceHashes'])==52 and value['sevenLuaByteExactV42'] and not value['fixtureTrafficGenerated']
  for rel,digest in value['sourceHashes'].items():assert hashlib.sha256((root/'code'/rel).read_bytes()).hexdigest()==digest,rel
  for name in ['fast-path.lua','classifier.lua','classified-tags.lua','module-stage-guardian.lua','qos-physical.lua','wan-scope.lua','tag-normalizer.lua']:
   assert (root/'code'/runtime/name).read_bytes()==(root/'code/work/v42-counter-window'/name).read_bytes(),name
'''
checker.write_text(text.replace(needle,checks+needle),encoding='utf8')
for name,h in old.items():assert sha((repo/name).read_bytes())==h,name
new(root/'publication-candidate.json',{'passed':True,'baseCommit':base,'newSources':len(new_sources),'totalSources':len(manifest['sources']),
 'oldCodeAndEvidenceUnchanged':len(old),'privateInputsSealed':len(sealed_hashes),'entryHardwareIntegrationPassed':False,'restorationPassed':True})
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Athena NSS — v45 入口进展</title><style>body{font:16px/1.75 system-ui,sans-serif;color:#17302a;background:#f5f7f5;max-width:900px;margin:40px auto;padding:0 24px}main{background:white;padding:32px;border-radius:16px}h1{font-size:28px;line-height:1.3}h2{font-size:20px;margin-top:30px}table{border-collapse:collapse;width:100%}td,th{padding:12px;border-bottom:1px solid #dce5df;text-align:left}.ok{color:#18734d}.pending{color:#966313}small{color:#62746a}a{color:#1e6b4a}</style><main><small>ATHENA NSS · '''+html.escape(now)+'''</small><h1>四路提前启动已接入<br><span class="ok">现网完整恢复</span></h1><p>五WAN高级QoS核心仍采用v42已验收的硬件证据。最新可复用入口的完整现场闭环尚未通过。</p><table><tr><th>事项</th><th>结果</th></tr><tr><td>启动改进</td><td>相同四TCP并发启动，PID齐备后提前核对WAN；最终分类和首包条件保持</td></tr><tr><td>离线入口检查</td><td class="ok">24模型、默认inspect、3406绑定通过</td></tr><tr><td>唯一实际入口</td><td class="pending">端点SSH连接超时，创建端点/客户端之前退出</td></tr><tr><td>本次fixture / NSS</td><td>均未启动，改进效果尚未现场验证</td></tr><tr><td>最终核验</td><td class="ok">五WAN健康、ECM关闭全零、物理队列原选项一致、端点与自有进程零残留</td></tr></table><h2>已有能力与限制</h2><p>v42已实测五WAN、四BULK＋一RT、60秒NSS、20续租和2373/2373模拟RT回包。本次没有操作CS2或Steam，未永久开启NSS。偶发SSH连接超时与自然WAN取得限制仍保留。</p><h2>前次标注更正</h2><p>v44旧TCP 1/1/2/4为native数组顺序；同一冻结socket映射的真实槽顺序是4/2/1/1、UDP3。原五WAN未齐和写前退出结论不变，旧证据保持。</p><p><a href="../athena-nss-mainline/docs/V45_EARLY_ACQUISITION_2026-10-07.md">完整记录</a> · <a href="../athena-nss-mainline/docs/STATE.md">当前STATE</a></p></main></html>'''
out=w/'outputs/nss45-entry-report.html'
with out.open('x',encoding='utf8') as f:f.write(page)
print(dump({'passed':True,'newSources':len(new_sources),'sourceHashes':len(manifest['sources']),'oldCodeEvidenceUnchanged':len(old),'models':24,'restorationPassed':True,'entryHardwareIntegrationPassed':False}))
