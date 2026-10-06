"""Publish one host integration delivery; leave frozen v1 data untouched."""
from pathlib import Path
import copy, hashlib, json, subprocess

w = Path(__file__).resolve().parents[2]
r = w / 'work/v11'
repo = w / 'athena-nss-mainline'
base = '1751b58f5890385d2f2cb0235bd9928feeb86fff'
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
sha = lambda b: hashlib.sha256(b).hexdigest()
dump = lambda v: json.dumps(v, ensure_ascii=False, indent=2) + '\n'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()==base
assert not subprocess.check_output(['git','status','--porcelain'],cwd=repo)
q = read(r/'service-qualified.json')
assert q['passed'] and q['oneSessionPerEnable'] and q['nativeSourcesUnchanged']
assert q['inheritedV1Bindings']==2137 and q['totalBoundInputs']==2151
for file,digest in q['sourceManifest'].items(): assert sha((w/file).read_bytes())==digest,file
calls = read(r/'smoke-calls-private.json')
started = json.loads(calls['start']['output'])
observed = json.loads(calls['observed']['output'])
stop = json.loads(calls['stop']['output'])
runtime = read(r/'runtime/status.json')
assert started['workerPid']==observed['workerPid']==runtime['workerPid']
assert calls['duplicate']['exit_code']==1
assert 'An owned invocation already exists' in calls['duplicate']['output']
assert observed['phase']=='WAITING_FOR_NORMAL_GAME_AND_DOWNLOAD'
assert observed['gameFlows']==observed['bulkFlows']==observed['sessionsStarted']==0
assert stop['stopPending'] and runtime['phase']=='STOPPED_NO_NSS_SESSION' and runtime['finished']
assert not (r/'runtime/active.json').exists()
assert not runtime['routerExperimentStarted'] and runtime['sessionsStarted']==0
health=read(w/'work/nss160/v3-final-health.json')
assert health['passed'] and health['queryAge']<6 and health['allFiveWanHealthy']
for key in ['ecmStoppedAndZero','noActiveTransaction','noStaging','noExperimentState','noExperimentalModule']:
    assert health[key]
manifest=read(repo/'source-manifest.json'); prefix=copy.deepcopy(manifest['sources'])
assert len(prefix)==2805 and manifest['lastAppendExport']=='NSS160_V1_FROZEN'
old_paths={v['path'] for v in prefix}
exports=[]
for p in sorted(r.iterdir()):
    if p.is_file() and p.suffix in ['.mjs','.py','.ps1','.cmd','.md']: exports.append(p)
for file in q['sourceManifest']:
    p=w/file
    if 'code/'+file not in old_paths and not p.is_relative_to(r): exports.append(p)
source_hashes={}
for src in exports:
    rel=src.relative_to(w).as_posix(); target='code/'+rel
    assert target not in old_paths
    data=src.read_bytes(); dest=repo/target;dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open('xb') as f:f.write(data)
    manifest['sources'].append({'path':target,'workspaceSource':rel,'sha256':sha(data),'bytes':len(data),
        'role':'v11-bounded-host-start-stop-integration-no-native-change'})
    source_hashes[rel]=sha(data)
manifest['lastAppendExport']='V11_BOUNDED_ENTRY'
(repo/'source-manifest.json').write_text(dump(manifest),encoding='utf-8')
def evidence(name,data):
    with (repo/'evidence'/('v11-'+name+'.json')).open('x',encoding='utf-8') as f:f.write(dump(data))
live={'passed':True,'startedAt':started['updatedAt'],'lastReadonlyObservation':observed['lastReadonlyObservation'],
    'stopCompletedAt':runtime['updatedAt'],'realWindowsBackgroundWorkerStarted':True,
    'duplicateInvocationRefused':True,'stopRequestObserved':True,'activeAdmissionFileRemoved':True,
    'finalPhase':runtime['phase'],'sessionsStarted':0,'routerExperimentStarted':False,
    'actualGameFlows':0,'actualSteamBulkFlows':0,'noDesktopOrDownloadOperation':True,
    'newHardwareNssSessionExecuted':False,'oneSessionPerEnable':True,'permanentNssDeployment':False}
evidence('live-start-stop',live); evidence('package-qualification',q);evidence('current-health',health)
source_proof={'passed':True,'sourceHashes':source_hashes,'historicManifestPrefixUnchanged':True,
    'historicPrefixSources':len(prefix),'historicPrefixCanonicalSha256':sha(json.dumps(prefix,sort_keys=True,separators=(',',':')).encode()),
    'oldV1RuntimeUnchanged':True,'frozenV1EvidenceUnchanged':True,'newRouterSideLua':False}
evidence('source-proof',source_proof)
delivery={'version':'v1.1 bounded host entry','observedAt':runtime['updatedAt'],
    'baseV1Commit':base,'v1Frozen':True,'strictHumanV1AcceptanceStillUnverified':True,
    'readiness':'HOST_ENTRY_PACKAGED_AND_REAL_IDLE_START_STOP_VERIFIED',
    'threeCommandsDelivered':['start','stop','status'],'waitWindowSeconds':600,'nativeHardSeconds':27,
    'kernelMaximumSessionSeconds':30,'ownerRollbackSeconds':100,'oneSessionPerEnable':True,
    'normalTrafficOnlyNoFixtureOrForcedDesktop':True,'reusesProvenSingleB20SecondLifecycle':True,
    'checkpointAndIndependentRollbackBeforeEveryEpoch':True,'newIntegratedHardwareSessionExecuted':False,
    'newCpuOrGameExperienceConclusion':False,'permanentNssDeployment':False,
    'noNewGapOrCpuOrFaultInjectionExperiment':True,'automationRemainsPaused':True,
    'historicalLimitsUnchanged':True,'hostCases':11,'liveStartStop':live,'health':health,
    'nextStep':'One normal-use single-WAN invocation, then deliberate renewable-session extension; no further v1 experiments'}
evidence('entry-delivery',delivery)
text='''# v1.1 单 WAN 有界启停入口已交付

更新：2026-10-07 00:04，北京时间。用户要求一次推进交付，复用 v1 历史证据，不新增 NSS161 实验编号或重新打开 gap/CPU/故障注入支线。

本次将后台启用、状态、停止、真实程序 socket/自动分类、单 WAN bulk/RT 映射、独立 checkpoint/回滚和原完整恢复审核集中接入 `work/v11/`。一启用最多等正常流十分钟，只执行一段约20秒 NSS 后恢复退出；等待阶段只读，不启动桌面/游戏或制造下载。没有改新的路由器 Lua、gate 二进制或常驻分类器。

**现场后台启动→无实际游戏/下载流而只读等待→拒绝重复启动→停止退出通过。NSS 未开启、没有生产实验写入。** 11个新增 host 调度案例通过；真实历史应用帧 payload73325字节与原 single-B builder 完全相等，复用2137历史绑定、总2151。这些是 host/历史整合检查，**不是新入口整段NSS硬件验收**；旧单段生命周期硬件证据保留。

新的原完整只读审核source5.03秒通过，五WAN健康，NSS68/31767/17139/config581b5d46…c791d7不变；ECM关闭全零，无事务/stage/state/实验模块。后台停止后零实验会话、本地准入锁已撤销。没有重新验证已有 checkpoint/rollback 故障路径；未来每次实际会话仍由既有入口创建新 checkpoint 并确认独立回滚。

实际限制：内核 session 最长30秒，当前控制器27秒/有效段约20秒。因此这是有界启停入口，**不是常驻 NSS 或全电脑加速**。停止禁止新准入，已有独立会话按原期限恢复，不强杀守护；未核验恢复时保留本地准入锁。新入口首次整段硬件执行留到正常使用，之后只推进单WAN可持续试用，不再复刻 v1 验收。

源码：[入口说明](../code/work/v11/README.md)、[后台控制](../code/work/v11/service.mjs)、[单段会话](../code/work/v11/session.mjs)。证据：[交付](../evidence/v11-entry-delivery.json)、[新增校验](../evidence/v11-package-qualification.json)、[实际启停](../evidence/v11-live-start-stop.json)、[现网健康](../evidence/v11-current-health.json)。v1原 `current-runtime.json` 是冻结快照，保持原字节；本次状态以本段和新交付证据为准。

## 已冻结 v1 与更早历史

'''
for name in ['STATE.md','PLAN.md']:
    p=repo/'docs'/name;p.write_text(text+p.read_text(encoding='utf-8'),encoding='utf-8')
p=repo/'AGENTS.md';p.write_text(text.replace('../code/','code/').replace('../evidence/','evidence/')+p.read_text(encoding='utf-8'),encoding='utf-8')
p=repo/'docs/EXPERIMENT_LOG.md';p.write_text(text+p.read_text(encoding='utf-8'),encoding='utf-8')
p=repo/'docs/BACKLOG.md';p.write_text('''# v1.1 当前交付边界

单 WAN host 启停入口已交付，真实空闲启停验证通过。下一项只为新入口的一次正常使用会话，以及解除30秒 session 上限后可持续单WAN试用；未开始改gate/常驻部署。v1 gap、更多CPU门槛、五WAN/Wi-Fi/共享预算/ECN/极端恢复均不重开为当前验收。

'''+p.read_text(encoding='utf-8'),encoding='utf-8')
p=repo/'tools/check_repository.py';checker=p.read_text(encoding='utf-8')
old="assert manifest['lastAppendExport']=='NSS160_V1_FROZEN'"
assert checker.count(old)==1
checker=checker.replace(old,"assert manifest['lastAppendExport'] in ['NSS160_V1_FROZEN','V11_BOUNDED_ENTRY']")
end="print(json.dumps({'passed':True,'filesChecked':count"
assert checker.count(end)==1
extra="""if manifest['lastAppendExport']=='V11_BOUNDED_ENTRY':
 v11=json.loads((root/'evidence/v11-entry-delivery.json').read_text(encoding='utf-8'))
 pq11=json.loads((root/'evidence/v11-package-qualification.json').read_text(encoding='utf-8'))
 live11=json.loads((root/'evidence/v11-live-start-stop.json').read_text(encoding='utf-8'))
 sp11=json.loads((root/'evidence/v11-source-proof.json').read_text(encoding='utf-8'))
 assert v11['v1Frozen'] and v11['oneSessionPerEnable'] and v11['automationRemainsPaused']
 assert not v11['permanentNssDeployment'] and not v11['newIntegratedHardwareSessionExecuted']
 assert pq11['passed'] and pq11['nativeSourcesUnchanged'] and pq11['noNewRouterSideLua']
 assert pq11['inheritedV1Bindings']==2137 and pq11['totalBoundInputs']==2151 and pq11['hostCases']==11
 assert live11['passed'] and live11['sessionsStarted']==0 and not live11['routerExperimentStarted']
 assert live11['duplicateInvocationRefused'] and live11['activeAdmissionFileRemoved']
 assert live11['finalPhase']=='STOPPED_NO_NSS_SESSION'
 assert sp11['historicPrefixSources']==2805 and sp11['oldV1RuntimeUnchanged']
 assert sp11['historicPrefixCanonicalSha256']==hashlib.sha256(json.dumps(manifest['sources'][:2805],sort_keys=True,separators=(',',':')).encode()).hexdigest()
 for src,digest in {**sp11['sourceHashes'],**pq11['sourceManifest']}.items():
  assert hashlib.sha256((root/'code'/src).read_bytes()).hexdigest()==digest,src
"""
p.write_text(checker.replace(end,extra+end),encoding='utf-8')
with (r/'publication-export.json').open('x',encoding='utf-8') as f:f.write(dump({'passed':True,'newSources':len(exports),
    'prefixSources':len(prefix),'sources':len(manifest['sources']),'oldV1RuntimeUnchanged':True}))
print(dump({'passed':True,'newSources':len(exports),'sources':len(manifest['sources']),'noProductionExperiment':True}))
