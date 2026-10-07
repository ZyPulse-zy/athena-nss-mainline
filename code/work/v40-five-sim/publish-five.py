from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib,subprocess
w=Path(__file__).resolve().parents[2];repo=w/'athena-nss-mainline';root=w/'work/v40-five-sim';base='897d2878face83cb1e380cd420826584437ba392'
sha=lambda b:hashlib.sha256(b).hexdigest();read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));dump=lambda v:json.dumps(v,ensure_ascii=False,indent=2)+'\n'
def new(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8') as f:f.write(dump(v))
def git(*a):return subprocess.check_output(['git','-C',str(repo),*a])
assert git('rev-parse','HEAD').decode().strip()==base
assert not git('status','--porcelain'), 'Publish only after current clean base is verified'
manifest=read(repo/'source-manifest.json');prefix=list(manifest['sources']);assert len(prefix)==4311
old={};old_bytes={}
for row in git('ls-tree','-r','-z','--full-tree',base,'--','code','evidence').split(b'\0'):
 if not row:continue
 head,path=row.split(b'\t');name=path.decode();old[name]=head.decode().split()[2];old_bytes[name]=sha((repo/name).read_bytes())
closure=w/read(root/'closure-pointer.json')['directory'];audit=read(root/'v40-final-audit.json');physical=read(closure/'physical-final.json');clients=read(closure/'client-closure.json')
assert audit['passed'] and audit['queryAge']<6 and audit['ecmClosedAndZero'] and audit['protectedConfigurationUnchanged'] and audit['allFiveHealthyWanBaseline']
assert physical['passed'] and physical['defaultQueueOptionsAndHandlesExact'] and clients['passed'] and clients['ownedTestProcessesRemaining']==clients['cs2ProcessesRemaining']==0
qualifications={s:read(w/'work'/s/'entry-qualified.json') for s in ['v39-five-sim','v40-five-sim']};runs={};private_hashes={};sealed=closure/'sealed-five-inputs-private';sealed.mkdir()
for scope,expected in [('v39-five-sim',3206),('v40-five-sim',3254)]:
 rr=w/'work'/scope;q=qualifications[scope];pilot=w/read(rr/'pilot-reference-private.json')['directory'];load=w/read(rr/'load-latest-private.json')['dir'];bindings=read(pilot/'actual-entry-bindings.json');assert len(bindings)==expected
 for rel,h in bindings.items():assert sha((w/rel).read_bytes())==h and sha((pilot/'frozen'/rel).read_bytes())==h,rel
 automatic=read(pilot/'automatic-result.json');assert not automatic['passed'];assert not (pilot/'case-reference-private.json').exists()
 assert not any(rr.glob('session-*/stage-checkpoint-private.json')) and not any(rr.glob('session-*/stage-receipt-private.json'))
 transport=read(load/'result-private.json');endpoint=read(load/'endpoint-retry-closure.json');guard=read(load/'guard-result-private.json')
 assert endpoint['passed'] and endpoint['ownedRulesRemaining']==0 and endpoint['baselineRestored'] and endpoint['exactOwnedEndpointClosed']
 assert guard['passed'] and guard['exactClientOnly'] and guard['clientExitedBeforeDeadline']
 frame=read(rr/'controlled-candidates-private.json');tw=sorted(x['identity']['wan'] for x in frame['tcp']);uw=sorted(x['identity']['wan'] for x in frame['udp'])
 runs[scope]={'passedAsPreservedAttempt':True,'actualRuntimeBindings':expected,'fixtureSeconds':transport['seconds'],'deliveredTcpBytes':transport['tcpBytes'],'fourTcpTransportsEstablished':all(c['bytes']>0 for c in transport['tcpChildren']),'tcpChildAttempts':{c['slot']:c['attempt'] for c in transport['tcpChildren']},'clientErrors':transport['errors'],'lastEligibleTcpWans':tw,'lastEligibleUdpWans':uw,'finalEligibleFiveWanPairs':len(frame['pairs']),'udpRequestsDuringSoftwareFixture':transport['udpSent'],'udpRepliesBeforeClientStop':transport['udpReceived'],'edgePendingRepliesNotDeclaredPacketLoss':True,'nssStarted':False,'checkpointStarted':False,'gateLoaded':False,'ecmOpened':False,'endpointRestoration':endpoint,'independentClientExitPassed':True}
 inputs=[pilot/'actual-entry-bindings.json',pilot/'driver-private.json',pilot/'automatic-result.json',load/'client-config-private.json',load/'client-binding-private.json',load/'result-private.json',load/'matching-private.json',load/'guard-result-private.json',load/'endpoint-retry-closure.json',rr/'controlled-candidates-private.json']
 for p in inputs:
  data=p.read_bytes();assert len(data)<=1048576,p.name;dest=sealed/(scope+'-'+p.name)
  with dest.open('xb') as f:f.write(data)
  assert dest.read_bytes()==data;private_hashes[str(dest.relative_to(closure)).replace('\\','/')]=sha(data)
new(closure/'sealed-five-inputs-private.json',private_hashes)
assert runs['v39-five-sim']['clientErrors']==['AssertionError [ERR_ASSERTION]: Natural TCP acquisition is closed']
assert not runs['v40-five-sim']['clientErrors'] and runs['v40-five-sim']['finalEligibleFiveWanPairs']==0
assert runs['v40-five-sim']['lastEligibleTcpWans']==[2,3,3,4] and runs['v40-five-sim']['lastEligibleUdpWans']==[2]
sources=[]
for scope,q in qualifications.items():sources += [*q['sourceManifest'],'work/'+scope+'/entry-qualified.json','work/'+scope+'/prepare-receipt.json']
sources += ['work/v39-five-sim/prepare-analysis.py','work/v39-five-sim/analyze-hardware.py','work/v40-five-sim/prepare-analysis.py','work/v40-five-sim/analyze-hardware.py','work/v40-five-sim/prepare-closure.py','work/v40-five-sim/capture-all-owned-closure.ps1','work/v40-five-sim/publish-five.py']
for scope,names in [('v39-five-sim',['qualify-entry.mjs','session-binding.mjs','failure.json']),('v40-five-sim',['qualify-entry.mjs','native-client.mjs','failure.json'])]:sources += ['work/'+scope+'/qualification-first-failure/'+n for n in names]
assert len(sources)==len(set(sources));hashes={}
for rel in sources:
 assert 'private' not in Path(rel).name.lower();data=(w/rel).read_bytes();dest=repo/'code'/rel;dest.parent.mkdir(parents=True,exist_ok=True)
 with dest.open('xb') as f:f.write(data)
 hashes[rel]=sha(data);manifest['sources'].append({'path':'code/'+rel,'workspaceSource':rel,'sha256':sha(data),'bytes':len(data),'role':'bounded-five-wan-prerequisite-refusal-and-owned-control-fix'})
manifest['lastFiveWanSimulationAttemptExport']='V40_NATURAL_FIVE_WAN_PREREQUISITE_REFUSAL';(repo/'source-manifest.json').write_text(dump(manifest),encoding='utf8')
for scope,q in qualifications.items():new(repo/'evidence'/(scope+'-entry-qualification.json'),q)
new(repo/'evidence/v40-five-prerequisite.json',{'passedAsPreservedObservation':True,'attempts':runs,'v39CompletedControlMessageIncorrectlyRecheckedAfterDeadline':True,'fixedInFreshV40NamespaceOnly':True,'v40ClientStayedHealthyUntilControllerStop':True,'v40NaturalDistinctWanPrerequisiteRefused':True,'fiveWanConcurrentHardwareAcceptance':False,'nativeOrFirmwareFailureEstablished':False,'routingOrClassifierThresholdChanged':False,'furtherFixtureAttemptsStopped':True,'noCs2OrSteamOperation':True})
new(repo/'evidence/v40-five-restoration.json',{'passed':True,'finalFullAudit':audit,'physicalQueues':physical,'clientClosure':clients,'endpointRestoration':{scope:v['endpointRestoration'] for scope,v in runs.items()},'newCheckpointStageOrNss':False,'noRouterConfigurationWrites':True,'heartbeatStillPaused':True,'newCpuAcceptance':False,'fiveWanConcurrentAcceptance':False,'permanentNssDeployment':False})
new(repo/'evidence/v40-five-source-proof.json',{'passed':True,'baseCommit':base,'historicPrefixSources':len(prefix),'historicPrefixCanonicalSha256':sha(json.dumps(prefix,sort_keys=True,separators=(',',':')).encode()),'sourceHashes':hashes,'oldCodeAndEvidenceBlobsChecked':len(old),'oldCodeAndEvidenceUnmodified':True,'actualRuntimeBindingsFrozenExact':{'v39-five-sim':3206,'v40-five-sim':3254},'privateInputsCopiedExact':len(private_hashes),'qualificationFailuresPreserved':True,'fiveSlotCompileControlCtAndRamEvidenceReused':True,'allNewAttemptsEndedBeforeNss':True,'rawCtNoncesCredentialsConfigurationsCheckpointsBinariesAndProcessCommandLinesExcluded':True})
stamp=datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M');report=f'''# 五 WAN 模拟流前提短测：安全拒绝，旧命令处理已修正

更新：北京时间 {stamp}。继续使用自有 TCP 下载和模拟实时 UDP；没有启动 CS2、操作 Steam 或新增游戏下载。**本次未形成五个不同 WAN 的合格连接，未开始 NSS。** 已通过的 v38 两 WAN、v20 多 WAN / QoS 和历史 CPU 结论保持。

四条自有 TCP 各目标 8Mbps，总 32Mbps，信用合计 64KiB；UDP 为 128 字节、目标 50pps。只在准入前自然取得连接，沿用 Linux PBR，固定 180 秒客户端和 210 秒独立守护；新轮换只允许前 30 秒、原每槽最多 8 个自然候选。配齐后冻结，未来生产写仍需新 checkpoint 下载 SHA/gzip 和独立恢复确认。

## 实际结果与修正

v39 四条 TCP 均已有 payload，但约 {runs['v39-five-sim']['fixtureSeconds']:.3f} 秒退出。客户端把已处理的旧轮换命令反复当作新请求，在 30 秒截止处误触发拒绝。原绑定/源码/输出保留，没有 checkpoint、模块或 ECM。

v40 只把已完成的控制命令处理为无操作。新请求仍受原截止和冻结状态保护，不重置客户端期限、不改源过滤或路由。四条 TCP 保持健康，运行约 {runs['v40-five-sim']['fixtureSeconds']:.3f} 秒，共收到 {runs['v40-five-sim']['deliveredTcpBytes']} 字节。最后实际合格 TCP 走 WAN2/3/3/4、UDP 走 WAN2，有重复 WAN、缺 WAN1/5；前提检查拒绝，控制器随后停止负载。客户端错误为 0。**这是一次针对已确认缺陷的复测；没有继续盲重试自然配对。**

五槽原生模块与 QoS / 分类 / 压缩 payload 沿用 v24 确切字节，复用已有同内核编译、63控制 / 68CT / 14RAM证据；本轮始终未加载五槽模块。首次资格检查发现 v38 清单并未包含全部五流分支，连接前拒绝，随后显式合并两个各自校验的依赖；3206 / 3254实际绑定及运行副本保存。v40 准备时混合换行字节被错误归一化，资格检查拒绝；原失败源码保留，按原字节和唯一控制块替换更正后通过。

## 终态

最终原完整只读 audit source {audit['queryAge']:.2f} 秒，五 WAN 健康、保护配置与服务 epoch 保持，ECM关闭全零，无实验 gate/stage/state。wan / lan4 原 mq＋四 fq_codel 所有选项和 handle 精确一致。两个自有端点独立到期后临时规则为0、canonical FW原基线一致、确切端点关闭；原客户端独立退出证明及本机 controller / guard / sender零残留通过。heartbeat仍暂停，电源计划未改。

## 保留结论

已交付范围仍为真实两/三 WAN 上三条精确流及五 WAN 的队列覆盖、共享 DOWN18借用 / UP60每 WAN12硬上限 / RT优先级。五 WAN同时 fast path尚未通过；本次拒绝发生于资格配对，没有 NSS / firmware 故障证据，也不增加 CPU、长期常驻或真人体验声明。下一步应解决有界自然连接取得效率，再做一次配齐后的五槽硬件验证；本次不通过放宽期限或改 PBR碰运气。

证据：[前提拒绝及修正](../evidence/v40-five-prerequisite.json)、[完整终态](../evidence/v40-five-restoration.json)、[源码保存](../evidence/v40-five-source-proof.json)、[已通过的两 WAN](SIMULATED_MULTIWAN_2026-10-07.md)。
'''
with (repo/'docs/FIVE_WAN_SIMULATION_2026-10-07.md').open('x',encoding='utf8') as f:f.write(report)
intro=f'''# 五 WAN 模拟前提有界拒绝，控制命令修正已封存

更新：北京时间{stamp}。按用户“继续”推进五 WAN 同时 NSS，使用自有四 TCP＋模拟 UDP，不操作 CS2 / Steam。v39已完成轮换命令在30秒后被重复检查导致客户端退出；v40新目录仅修正旧命令无操作，四 TCP健康、错误0，但实际分类 WAN2/3/3/4＋UDP WAN2未满足五个不同 WAN，准入前拒绝。两轮均无checkpoint/stage/模块/ECM放行，不归因NSS/固件，不再盲重试或改PBR/门槛/期限。

3206/3254实际绑定冻结，五槽编译/63控制/68CT/14RAM旧证据复用；两次资格失败的原输出与源码保存。最后只读原audit source{audit['queryAge']:.2f}、五WAN健康/保护配置/epoch保持/ECM关闭全零；两物理原mq＋四fq_codel全部选项/handle、两个端点FW基线与原客户端独立退出/零残留完整通过。

**v38两WAN模拟功能验收及v20高级QoS已通过的范围保持；五WAN同时fast path尚未通过。** 常驻仍NSS68原config，无永久NSS；heartbeat保持暂停。后续仍用模拟包，不以CS2作为测试前提。详情：[本次报告](FIVE_WAN_SIMULATION_2026-10-07.md)。

## 以下保留历史记录

'''
for rel in ['AGENTS.md','docs/STATE.md','docs/PLAN.md','docs/EXPERIMENT_LOG.md']:
 p=repo/rel;text=intro.replace('(FIVE_WAN_SIMULATION_2026-10-07.md)','(docs/FIVE_WAN_SIMULATION_2026-10-07.md)') if rel=='AGENTS.md' else intro;p.write_bytes(text.encode()+p.read_bytes())
p=repo/'README.md';p.write_bytes(('''# Athena NSS 多WAN / 高级QoS受控原型

两WAN模拟实时流硬件已通过；最新五WAN前提短测在NSS前安全拒绝，修正了已完成轮换命令重复检查问题。完整恢复、未永久启用NSS，见[STATE](docs/STATE.md)与[五WAN短测报告](docs/FIVE_WAN_SIMULATION_2026-10-07.md)。

## 以下保留历史交付

''').encode()+p.read_bytes())
attrs=[]
with (repo/'.gitattributes').open('a',encoding='utf8') as f:
 f.write('\n# Keep exact five-WAN prerequisite source bytes; exceptions are inherited and path specific.\n')
 for rel in sources:
  if b'\r\n' in (w/rel).read_bytes():attrs.append('/code/'+rel+' whitespace=cr-at-eol')
 for scope in qualifications:
  attrs += ['/code/work/'+scope+'/fast-path.lua whitespace=cr-at-eol,-blank-at-eol','/code/work/'+scope+'/endpoint-firewall-guardian.py whitespace=cr-at-eol,-blank-at-eof']
 for a in attrs:f.write(a+'\n')
new(repo/'evidence/v40-frozen-whitespace.json',{'passedAsPreservedSourcePolicy':True,'exactPathAttributes':attrs,'frozenGuardBytesUnmodifiedFromV24':True,'noGlobalWhitespacePolicyChange':True,'previousV38ExactBytePolicyAppliedOnlyToFreshPaths':True})
assert not git('diff','--name-only',base,'--','code','evidence')
assert all(sha((repo/n).read_bytes())==h for n,h in old_bytes.items())
print(json.dumps({'passed':True,'newSources':len(sources),'sourceHashes':len(manifest['sources']),'oldCodeEvidenceBlobsPreserved':len(old),'privateInputsCopiedExact':len(private_hashes),'newNssHardwareExecuted':False,'oldCompletedCommandDefectFixed':True,'fiveWanAcceptance':False}))
