from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib,subprocess,copy
w=Path(__file__).resolve().parents[2];repo=w/'athena-nss-mainline';root=w/'work/v41-five-sim';base='160903758531cae545663a125775eed92f22d540'
sha=lambda b:hashlib.sha256(b).hexdigest();read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));dump=lambda v:json.dumps(v,ensure_ascii=False,indent=2)+'\n'
def new(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8') as f:f.write(dump(v))
def git(*a):return subprocess.check_output(['git','-C',str(repo),*a])
assert git('rev-parse','HEAD').decode().strip()==base and not git('status','--porcelain')
manifest=read(repo/'source-manifest.json');prefix=list(manifest['sources']);assert len(prefix)==4423
old={};old_bytes={}
for row in git('ls-tree','-r','-z',base,'--','code','evidence').split(b'\0'):
 if row:
  header,name=row.split(b'\t');old[name.decode()]=header.decode().split()[2];old_bytes[name.decode()]=sha((repo/name.decode()).read_bytes())
assert len(old)==4992
closure=w/read(root/'closure-pointer.json')['directory'];audit=read(root/'v41-final-audit.json');physical=read(closure/'physical-final.json');clients=read(closure/'client-closure.json')
assert audit['passed'] and audit['queryAge']<6 and audit['ecmClosedAndZero'] and audit['protectedConfigurationUnchanged'] and audit['allFiveHealthyWanBaseline']
assert physical['passed'] and physical['defaultQueueOptionsAndHandlesExact'] and clients['passed'] and clients['ownedTestProcessesRemaining']==clients['cs2ProcessesRemaining']==0
q=read(root/'entry-qualified.json');pilot=w/read(root/'pilot-reference-private.json')['directory'];load=w/read(root/'load-latest-private.json')['dir'];terminal=read(root/'terminal-descriptive.json');case=next(x for x in root.glob('session-*')if x.is_dir()and(x/'last-record-private.json').exists())
assert q['passed'] and not q['hardwareExecuted'] and terminal['actualFiveWanInitialHit'] and not terminal['fiveWanSixtySecondAcceptance']
assert terminal['sameQueryCompleteDiagnosis'] and terminal['ctAndFullMarkNatWanUnchanged'] and terminal['udpRemainedRtAdmitted'] and all(terminal['restoration'].values())
assert not read(pilot/'automatic-result.json')['passed'] and not read(case/'result.json')['passed']
bindings=read(pilot/'actual-entry-bindings.json');assert len(bindings)==3303 and read(case/'source-manifest-preaudit.json')==bindings
for rel,h in bindings.items():assert sha((w/rel).read_bytes())==sha((pilot/'frozen'/rel).read_bytes())==sha((case/'frozen'/rel).read_bytes())==h,rel
endpoint=read(load/'endpoint-retry-closure.json');guard=read(load/'guard-result-private.json');transport=read(load/'result-private.json');assert transport['errors']==[]
assert endpoint['passed'] and endpoint['ownedRulesRemaining']==0 and endpoint['baselineRestored'] and endpoint['exactOwnedEndpointClosed']
assert guard['passed'] and guard['exactClientOnly'] and guard['clientExitedBeforeDeadline']
plan=read(case/'stage-plan-private.json');assert plan['qosCodeBytes']<=73728 and plan['execBytes']<=9000
checkpoint=read(case/'stage-checkpoint-verified.json');assert checkpoint['gzipVerified'] and sha((case/'stage-checkpoint-config-private.tar.gz').read_bytes())==checkpoint['sha256']
inputs=[pilot/'actual-entry-bindings.json',pilot/'driver-private.json',pilot/'automatic-result.json',load/'client-config-private.json',load/'client-binding-private.json',load/'result-private.json',load/'matching-private.json',load/'guard-result-private.json',load/'endpoint-retry-closure.json',root/'controlled-candidates-private.json',root/'terminal-descriptive.json']
inputs += [case/(name+'.json') for name in ['last-record-private','selected-private','persistent-selection-private','post-checkpoint-controlled-receipt-private','post-checkpoint-class-leaf-map-proof','stage-plan-private','stage-checkpoint-verified','stage-detached-private','stage-receipt-private','stage-undo-verified','controller-error','result','baseline-audit','source-manifest-preaudit','source-manifest']]
sealed=closure/'sealed-inputs-private';sealed.mkdir();private_hashes={}
for i,p in enumerate(inputs):
 data=p.read_bytes();assert len(data)<=1048576,p.name;dest=sealed/(str(i).zfill(2)+'-'+p.name)
 with dest.open('xb') as f:f.write(data)
 assert dest.read_bytes()==data;private_hashes[dest.name]=sha(data)
new(closure/'sealed-inputs-private.json',private_hashes)
sources=[*q['sourceManifest'],'work/v41-five-sim/entry-qualified.json','work/v41-five-sim/prepare-receipt.json','work/v41-five-sim/describe-terminal.mjs','work/v41-five-sim/analyze-hardware.py','work/v41-five-sim/publish-terminal.py','work/v41-five-sim/local-progress-first-failure.json','work/v41-five-sim/description-first-failure/describe-terminal.mjs','work/v41-five-sim/description-first-failure/failure.json'];assert len(sources)==len(set(sources))
hashes={}
for rel in sources:
 assert 'private' not in Path(rel).name.lower();data=(w/rel).read_bytes();dest=repo/'code'/rel;dest.parent.mkdir(parents=True,exist_ok=True)
 with dest.open('xb') as f:f.write(data)
 hashes[rel]=sha(data);manifest['sources'].append({'path':'code/'+rel,'workspaceSource':rel,'sha256':sha(data),'bytes':len(data),'role':'five-wan-initial-hardware-hit-and-authenticated-class-retirement'})
# Preserve prior historical markers; the new attempt has its own result marker.
manifest['lastFiveWanHardwareAttemptExport']='V41_FIVE_WAN_INITIAL_HIT_CLASS_RETIREMENT';(repo/'source-manifest.json').write_text(dump(manifest),encoding='utf8')
public=copy.deepcopy(terminal)
for p in public['initialFiveFlowProof']['proof'].values():p.pop('serial')
public['fixture']={'seconds':transport['seconds'],'deliveredTcpBytes':transport['tcpBytes'],'clientErrors':transport['errors'],'tcpAttempts':{c['slot']:c['attempt']for c in transport['tcpChildren']},'targetCombinedMbps':32,'combinedCreditBytes':65536,'udpBytes':128,'targetUdpPps':50,'clientMaximumSeconds':180,'independentGuardSeconds':210,'naturalAcquisitionSeconds':30,'cs2OrSteamOperated':False}
public['actualEncodedSizes']={'bundleBytes':plan['qosCodeBytes'],'execBytes':plan['execBytes'],'bundleMaximumBytes':73728,'execMaximumBytes':9000,'recordMaximumBytes':1048576}
new(repo/'evidence/v41-five-initial-hit.json',public);new(repo/'evidence/v41-five-qualification.json',q);new(repo/'evidence/v41-acquisition-models.json',read(root/'acquisition-model-qualified.json'))
new(repo/'evidence/v41-five-restoration.json',{'passed':True,'finalFullAudit':audit,'physicalQueues':physical,'clientClosure':clients,'endpointRestoration':endpoint,'stageUndo':terminal['restoration'],'protectedBaselineChecks':read(case/'baseline-audit.json')['checks'],'downloadedCheckpointShaAndGzipVerified':True,'independentUndoBeforeWriteVerified':True,'heartbeatStillPaused':True,'cs2OrSteamOperated':False,'newCpuAcceptance':False,'fiveWanSixtySecondAcceptance':False,'permanentNssDeployment':False})
new(repo/'evidence/v41-five-source-proof.json',{'passed':True,'baseCommit':base,'historicPrefixSources':len(prefix),'historicPrefixCanonicalSha256':sha(json.dumps(prefix,sort_keys=True,separators=(',',':')).encode()),'sourceHashes':hashes,'oldCodeAndEvidenceBlobsChecked':len(old),'oldCodeAndEvidenceUnmodified':True,'actualRuntimeBindingsFrozenExact':3303,'pilotAndCaseBindingsAndFrozenCopiesExact':True,'privateInputsCopiedExact':len(private_hashes),'productionFailureAndOriginalRecordPreserved':True,'localDescriptionFailurePreservedAndCorrected':True,'fiveSlotNativeControlCtAndRamEvidenceReused':True,'classificationNativeAndQosBytesUnchangedFromV24':True,'rawCtNoncesCredentialsConfigsCheckpointsBinariesAndCommandLinesExcluded':True})
stamp=datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
rates={s:public['qosLeafSnapshots']['down']['values'][s]['nearbyDescriptiveMbps']for s in ['tcp','tcp2','tcp3','tcp4']}
report=f'''# 五 WAN 首次同时命中；分类变化触发精确恢复

更新：北京时间 {stamp}。**五个不同 WAN 的四条 TCP BULK＋一条 UDP RT 已实际进入 NSS，ECM=5；60 秒维持验收未通过。** 模拟流测试没有操作 CS2 或 Steam。既有 v38 两 WAN / v20 多 WAN与高级 QoS、历史 CPU 证据继续保留。

## 本次推进

v40 保存的 10 次读取约21秒，每次只轮换第一条重复 WAN 的 TCP，且须等四条全部 BULK。v41 在前30秒自然连接取得阶段处理所有当前重复槽位，利用已核验的自有 TCP 传输 WAN 元数据筛选；仍须原永久分类器明确判为 BULK、UDP为已准入 RT、五个 WAN不同，才能冻结并进入原控制器。PC读取携带同一次进程身份，变更/缺失时不猜测WAN；整批命令先校验再启动，旧已完成命令保持无操作。没有修改 Linux PBR、分类阈值、NSS gate或QoS。

11个针对新策略的本地检查通过；历史完整帧用于模型，不能授权新现场。3303实际绑定及pilot/控制器原源码副本逐字节冻结，复用五槽编译与63控制/68CT/14RAM，不重跑历史CPU或旧准备。本次11次自然读取取得 TCP WAN2/4/5/3＋UDP WAN1；第三 TCP 取得第4个自然候选，其它TCP为第1个。没有对不同随机WAN分配声称可比提速。

新checkpoint下载SHA/gzip和控制连接外独立恢复在写前核验；实际bundle {plan['qosCodeBytes']} / exec {plan['execBytes']}字节符合原73728/9000上限。随后五条精确流实测加速，双向十tag、上下leaf、完整ct mark、NAT、WAN affinity以及LAN4/bridge路径通过。

## 60 秒窗口未通过的确切条件

B段持续 {public['phase']['seconds']:.2f} 秒，6次保存采样均为ECM5，续租0次。下一分类query完整同源帧确认四TCP均仍存在，CT/zone/完整mark/WAN/双向tuple全部匹配；四条均变为BE/cooldown，报告速率约1506–1689Kbps，低于原2000Kbps BULK阈值。UDP保持RT/interactive及预算准入。投影缺失没有被解释为CT退出。

控制器停止新学习、结束旧代、撤下五条精确流及tag，并恢复软件路径。原本请求60秒，实际提前退出，因此 `automaticLifecycleEpochCompleted=false`，原控制器失败和完整记录保留，**不能把短时命中写成60秒或长期验收**。

附近 {public['qosLeafSnapshots']['down']['nearbyAsynchronousWindowSeconds']:.2f} 秒的下行leaf计数显示四TCP约{rates['tcp']:.2f}/{rates['tcp2']:.2f}/{rates['tcp3']:.2f}/{rates['tcp4']:.2f}Mbps，合计{public['bulkLeafAggregateNearbyMbps']:.2f}Mbps；共享DOWN18和UP60每WAN12队列合同保持，UDP上下leaf均零drop。这些窗口与分类计数窗口不同，尚不能据此认定NSS统计反馈错误或精确根因；不作为新的CPU、端到端零loss、CS2/HUD或真人证明。

## 恢复与下一边界

最终原完整只读audit source {audit['queryAge']:.2f} 秒，五WAN健康、原保护配置与epoch保持、ECM关闭全零。wan/lan4原mq＋四fq_codel所有选项和handle精确一致，实验gate/stage/state/模块零残留。端点独立到期后规则0、canonical FW基线一致、确切端点关闭，原client/guard/controller/sender全部退出。常驻NSS68原config保持、heartbeat仍暂停，电源计划未改。

已新增的证明是五WAN同时NSS启动及十tag/leaf/CT/NAT/affinity；未解决的是五流带宽共享期间的BULK分类维持边界。后续只针对这项实际失败，先核对当前真实计数窗口与分类反馈，再决定有证据的修正；不放宽分类或期限，不强行把BE当BULK，不盲重跑五流，也不回到CS2测试。长期常驻、多流公平、WiFi/autorate/ECN不在本轮。

离线报告检查首次假定checkpoint有`passed`字段而拒绝，原源码/失败保存；改为验证实际gzip字段和下载文件SHA后通过。没有修改原运行记录或重跑生产实验。

证据：[五WAN实际命中与提前撤销](../evidence/v41-five-initial-hit.json)、[终态恢复](../evidence/v41-five-restoration.json)、[源码保存](../evidence/v41-five-source-proof.json)、[先前两WAN60秒](SIMULATED_MULTIWAN_2026-10-07.md)。
'''
with (repo/'docs/FIVE_WAN_INITIAL_HIT_2026-10-07.md').open('x',encoding='utf8') as f:f.write(report)
intro=f'''# 五 WAN 首次同时 NSS 命中；60 秒维持未通过，完整恢复

更新：北京时间{stamp}。v41使用自有四TCP＋模拟UDP，原自动分类自然取得TCP WAN2/4/5/3＋UDP WAN1；新checkpoint下载SHA/gzip与独立守护写前通过，五条实际NSS/ECM5、双向十tag/leaf/ct mark/NAT/affinity已取得。B仅{public['phase']['seconds']:.2f}秒/6采样/0续租，不能标60秒验收。

同query完整帧证明四TCP仍同CT/mark/NAT/WAN，但类变BE/cooldown、约1506–1689Kbps；UDP仍RT。附近leaf四bulk合计{public['bulkLeafAggregateNearbyMbps']:.2f}Mbps但计数窗不同，统计反馈精确根因未证实。控制器按原改类规则停止新学习并结束旧代；失败/完整帧/3303实际绑定原字节保留，不强续租或改tag，不把投影缺失当CT退出。

最终audit source{audit['queryAge']:.2f}、五WAN健康/保护配置/epoch保持/ECM关闭全零；两物理原mq＋四fq_codel全选项/handle，独立端点FW基线与client/controller/guard/sender零残留通过。常驻NSS68原config、heartbeat暂停；没有CS2/Steam操作或新CPU/长期声明。

**已有v38两WAN60秒和v20高级QoS保持；五WAN60秒维持仍未通过。** 下一步只处理已观测的五流BULK分类维持边界，先核对计数窗再决定修正；不盲重试、不放宽阈值/期限、不中途强制改类。详情：[本次报告](FIVE_WAN_INITIAL_HIT_2026-10-07.md)。

## 以下保留历史记录

'''
for rel in ['AGENTS.md','docs/STATE.md','docs/PLAN.md','docs/EXPERIMENT_LOG.md']:
 p=repo/rel;text=intro.replace('(FIVE_WAN_INITIAL_HIT_2026-10-07.md)','(docs/FIVE_WAN_INITIAL_HIT_2026-10-07.md)')if rel=='AGENTS.md'else intro;p.write_bytes(text.encode()+p.read_bytes())
p=repo/'README.md';p.write_bytes(('''# Athena NSS 多WAN / 高级QoS受控原型

最新五WAN已同时进入NSS，四TCP改类后按规则完整恢复；60秒维持验收仍未通过。已有两WAN/三流与高级QoS硬件结论保持，见[STATE](docs/STATE.md)和[五WAN实际命中报告](docs/FIVE_WAN_INITIAL_HIT_2026-10-07.md)。

## 以下保留历史交付

''').encode()+p.read_bytes())
attrs=[]
with (repo/'.gitattributes').open('a',encoding='utf8') as f:
 f.write('\n# Preserve exact new five-WAN acquisition and original data-plane bytes.\n')
 for rel in sources:
  if b'\r\n'in(w/rel).read_bytes():attrs.append('/code/'+rel+' whitespace=cr-at-eol')
 attrs+=['/code/work/v41-five-sim/fast-path.lua whitespace=cr-at-eol,-blank-at-eol','/code/work/v41-five-sim/endpoint-firewall-guardian.py whitespace=cr-at-eol,-blank-at-eof']
 for a in attrs:f.write(a+'\n')
new(repo/'evidence/v41-frozen-whitespace.json',{'passedAsPreservedSourcePolicy':True,'exactPathAttributes':attrs,'frozenDataPlaneBytesUnmodifiedFromV24':True,'noGlobalWhitespacePolicyChange':True})
assert not git('diff','--name-only',base,'--','code','evidence');assert all(sha((repo/n).read_bytes())==h for n,h in old_bytes.items())
print(json.dumps({'passed':True,'newSources':len(sources),'sourceHashes':len(manifest['sources']),'oldCodeEvidenceBlobsPreserved':len(old),'privateInputsCopiedExact':len(private_hashes),'actualFiveWanInitialHit':True,'fiveWanSixtySecondAcceptance':False,'fullRestoration':True}))
