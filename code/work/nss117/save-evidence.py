"""Append one new upload hypothesis and its unchanged-entry retry."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json,subprocess,shutil,importlib.util
w=Path(__file__).resolve().parents[2];repo=w/'athena-nss-mainline';r=w/'work/nss117'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
spec=importlib.util.spec_from_file_location('collector',w/'work/nss101/collect-lifecycle.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
cases=sorted(p for p in(w/'work/nss116').glob('controlled-matched-aba-*')if(p/'result.json').exists());assert len(cases)==2
trials=[c.stage(p.relative_to(w).as_posix())for p in cases]
assert not trials[0]['passed']and not trials[0]['ecmOpened']and'publication changed during read'in trials[0]['error']
assert trials[1]['passed']and trials[1]['completeABA']
closures=[c.closure(load(w/f'work/nss{n}/load-reference-private.json')['dir'])for n in [116,117]]
final=load(r/'v1-final-health.json');physical=load(r/'physical-final.json');assert final['passed']and physical['passed']and final['ecmStoppedAndZero']
assert all(final[k]for k in ['originalFullLockedNativeAudit','unrelatedConfigurationMatches','noActiveTransaction','noStaging','noExperimentState','noExperimentalModule'])
proof=load(cases[1]/'actual-upstream-proof.json');m=trials[1]['metrics'];transient=load(cases[1]/'uplink-transient-analysis.json');assert proof['passed']and m['bulkDirection']=='upload'and m['localSubmittedBytesNotUsedForThroughput']and transient['passed']and transient['shaperActivityObserved']
qual=load(w/'work/nss116/entry-qualified.json');assert len(qual['checks'])==12 and qual['onlyBulkLoadDirectionChanged']and not qual['queueRatesChanged']and not qual['routerPayloadChanged']
old=(repo/'evidence/current-runtime.json').read_bytes();assert load(repo/'evidence/current-runtime.json')['round']=='NSS115';assert subprocess.check_output(['git','show','HEAD:evidence/current-runtime.json'],cwd=repo)==old
archive=repo/'evidence/nss115-runtime.json';assert not archive.exists();archive.write_bytes(old)
mp=repo/'source-manifest.json';manifest=load(mp);assert len(manifest['sources'])==1296;prefix=sha(json.dumps(manifest['sources'],sort_keys=True,separators=(',',':')).encode())
allowed={116:['prepare.py','upload-ack.mjs','upload-server.py','ssh-client.mjs','session-binding.mjs','qualify.mjs','controlled-session.mjs','current-audit-diagnostic.mjs','match-controlled.mjs','read-controlled.mjs','run.mjs','module-stage.mjs','payload.mjs','pack-lua.mjs','pack-guardian.mjs','compact-default-queues.mjs','uplink-tag-plan.mjs','parse-ecm-any-wan.mjs','fast-path.lua','module-stage-guardian.lua','qos-physical.lua','tag-normalizer.lua','failed-wan-owner.lua','declared-baseline.mjs','service-epoch.mjs'],117:['prepare-retry.py','retry-existing.mjs','prepare-analysis.py','analyze-long.py','calibrate-clock.mjs','prove-upstream.py','analyze-uplink-transient.py','health.mjs','read-final-physical.mjs','save-evidence.py']}
source_hashes={}
for n,names in allowed.items():
 for name in names:
  src=w/f'work/nss{n}/{name}';rel=src.relative_to(w).as_posix();dst=repo/'code'/rel;assert not dst.exists();dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);digest=sha(src.read_bytes());source_hashes[rel]=digest;manifest['sources'].append({'path':'code/'+rel,'workspaceSource':rel,'sha256':digest,'bytes':src.stat().st_size,'role':'server-confirmed-single-WAN-upload-QoS'})
manifest['generatedAt']=datetime.now(timezone.utc).isoformat();manifest['lastAppendExport']='NSS117';dump(mp,manifest)
freeze=r/'proof-v1/private-inputs';freeze.mkdir(parents=True,exist_ok=False);frozen={}
for n in [116,117]:
 for src in sorted((w/f'work/nss{n}').rglob('*')):
  if not src.is_file()or any(t in src.parts for t in ['proof-v1','frozen','frozen-qualified-inputs','__pycache__']):continue
  rel=src.relative_to(w);dst=freeze/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);frozen[rel.as_posix()]=sha(src.read_bytes());assert sha(dst.read_bytes())==frozen[rel.as_posix()]
dump(r/'private-input-freeze-index.json',frozen)
summary={'round':'NSS117','observedAt':final['observedAt'],'directionOnlyNewVariable':'upload','queueRatesUnchangedFrom114':True,'routerPayloadByteExactFrom114':True,'serverConfirmedReceivedBytesUsed':True,'firstPublicationCoherenceFailurePreserved':True,'unchangedEntryRetriedOnce':True,'successfulSingleWanABA':True,'oneWan':m['oneWan'],'entry':'work/nss116/controlled-session.mjs','boundInputs':825,'offeredUploadMbps':48,'nativeSessionSeconds':27,'independentOwnerSeconds':100,'phaseSeconds':20,'classifierMaximumLeaseSeconds':6,'newCpuComparisonAccepted':False,'uplinkCongestionLatencyAccepted':False,'humanCs2Acceptance':False,'highLoad300MbpsAcceptance':False,'fullCakeReplacementAccepted':False,'residentClassifierChanged':False,'nssPermanentlyEnabled':False,'allTemporaryEndpointsClosed':2,'secondWanSimultaneouslyAccelerated':False,'upstreamSubmitted':False,'reportVerification':{'sourceValidated':True,'browserRendered':False}}
source_proof={'round':'NSS117','historicPrefixSources':1296,'historicPrefixCanonicalSha256':prefix,'sources':len(source_hashes),'sourceHashes':source_hashes,'privateOwnedHostBootstrapExcluded':True,'privateArtifactsFrozen':len(frozen),'actualBindingTreesRetained':True}
summary['shaperActivityObserved']=True;summary['tcpRampCauseProved']=False
for name,value in {'mainline':summary,'trials':trials,'metrics':m,'uplink-proof':proof,'uplink-transient':transient,'qualification':qual['checks'],'endpoint-closure':closures,'final-audit':final,'physical-final':physical,'source-proof':source_proof}.items():dump(repo/f'evidence/nss117-{name}.json',value)
runtime={'round':'NSS117','checkedAt':physical['observedAt'],'deploymentReference':'work/nss68/deployment-latest.json','classifierConfigSha256':final['configSha256'],'workerPid':4859,'guardianPid':17139,'nssPermanentlyEnabled':False,'residentClassifierChangedThisTurn':False,'qualifiedExperimentalEntry':summary['entry'],'qualifiedExperimentalEntryBoundInputs':825,'currentNssAdmissionMustBeRefreshedBeforeWrite':True,'bulkDirection':'upload','serverConfirmedUploadMeasurement':True,'dualPhysicalQosHardwarePassed':True,'uplinkCongestionLatencyAccepted':False,'realHumanGameAcceptance':False,'newMatchedCpuComparisonAccepted':False,'audit':final,'physicalRootRestoreAudit':physical,'historical115RuntimePreservedSha256':sha(old),'nightContinuationUntilBeijing':'2026-10-06T10:00:00+08:00'};dump(repo/'evidence/current-runtime.json',runtime)
when=datetime.fromisoformat(final['observedAt'].replace('Z','+00:00')).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M');ps=m['phases'];speeds='/'.join(f"{p['whole']['clientTcpMbps']:.3f}"for p in ps);soft='/'.join(f"{p['whole']['softirqPercent']:.3f}"for p in ps);udp='、'.join(f"{p['whole']['udp']['received']}/{p['whole']['udp']['sent']}"for p in ps)
text=f'''更新：{when}，北京时间。最新NSS117；常驻68/config581b5d46…c791d7仍4859/17139，所有实验已撤销。

**双向QoS的实际上传路径也已完成：只改变自有同一SSH TCP的负载方向，原30/29/1队列、27秒native、100秒owner与20秒A/B/A2保持。单WAN{m['oneWan']}服务器确认上传{speeds}Mbps，ECM0→2→0、上下行四leaf、mark/NAT/affinity和精确恢复通过。**

见 [汇总](../evidence/nss117-mainline.json)、[实际两轮](../evidence/nss117-trials.json)、[上传指标](../evidence/nss117-metrics.json)、[上行leaf](../evidence/nss117-uplink-proof.json)、[关闭](../evidence/nss117-endpoint-closure.json)、[终态](../evidence/nss117-final-audit.json)。

- 首116因发布文件更新与读检查重合，在ECM开放前拒绝，双物理树完整恢复；117只用同一825项入口一次重试，没有放宽一致性/时间或重装分类器。原失败保留。新客户端明确按服务器已读stdin字节计数，不把本地write提交当吞吐；11解析边界与真实本地1MiB/EOF receiver共12项检查，和现场证据分开。
- 三段softirq{soft}%，UDP收/发{udp}；全量busy、squeeze、pps、RTT和异步leaf见原指标。B上传明显低于软件段，不能计算严格CPU收益，echo不是真人CS2。实际上行parent overlimits+{transient['uplinkParentAndLeafClassDelta']['8e00:50']['overlimits']}、bulk drop{transient['actualBulkLeafDrops']}、RT drop{transient['actualRtLeafDrops']}，证明shaper活动；B的四个5秒上传窗口{'/'.join(f'{v:.2f}'for v in transient['phaseBServerConfirmedTcpFiveSecondBinsMbps'])}Mbps持续回升，尚未稳在30Mbps。不能把这个短窗降速定为限速精度或根因证明；先前32/48MbpsCPU证据保留。
- 仍仅一个WAN、一TCP一UDP；上下行两个30Mbps组和默认950fallback未改，常驻发布upTag0不改。物理wan共用MacVLAN，未知flow拒绝；尚未保证全部EAPOL/其它业务在高负载树下的连续性、全套CAKE语义或五WANQoS。当前WAN4仍认证故障，自然四路PBR与学校策略保持。
- 两次stage各新checkpoint下载/SHA/gzip和独立100秒守护，两个端点独立FW180/客户端210秒恢复和端口关闭。最终原完整source{final['queryAge']:.2f}秒、ECM关闭全零、无事务/stage/state/模块，两物理根mq＋四fq_codel恢复；旧115 runtime原字节存档。源/实际绑定与私有原输入冻结，凭据/CT/nonce/配置/检查点/二进制不进Git。
- 下一步只把发送48降到32Mbps，维持30/29/1队列及所有期限，观察较小负载切换下B吞吐能否稳定及RT隔离；不先改预算。保持UI停用、不新下载/游戏、不扩WAN/WiFi/共享全局预算/autorate；最后集中一次真人验收。夜间继续至10:00，09:50停止新实验并完成报告、清理和推送后暂停本夜接续。
'''
p=repo/'docs/STATE.md';p.write_text('# 当前状态\n\n'+text+'\n## NSS115历史状态\n\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
p=repo/'docs/EXPERIMENT_LOG.md';head,tail=p.read_text(encoding='utf-8').split('\n',1);p.write_text(head+'\n\n## NSS116–117 · '+when+' · 服务器确认上传与双向leaf\n\n'+text+tail,encoding='utf-8')
p=repo/'AGENTS.md';head,tail=p.read_text(encoding='utf-8').split('\n',1);p.write_text(head+'\n\n最新NSS117：同825项116入口，仅负载方向改上传；首发布读取竞态在ECM前拒绝并恢复，117一次重试成功，原失败保留。单WAN'+str(m['oneWan'])+'三段各20秒/ECM0→2→0，服务器确认上传'+speeds+'Mbps，softirq'+soft+'，UDP'+udp+'，双向四leaf/完整mark/NAT/affinity和恢复通过；不从不同吞吐计算CPU，不是真人/300Mbps/完整CAKE或上行拥塞验收。常驻68/4859/17139/config不变、upTag0仍保持；队列30/29/1/默认950不变，6秒来源/27native/100owner不放宽。两个stage、两个端点均关闭，终态ECM全零无残留、双物理原mq/fq_codel恢复，WAN4仍down四路PBR，旧115 runtime逐字节保留。下一步只降发送48→32Mbps、维持队列及期限看吞吐切换与RT；不重装/重放/扩WAN/WiFi/共享预算/autorate/新下载/UI，最后一次真人。夜间到10:00，09:50后收尾并暂停本夜接续；STATE为准。\n\n'+tail,encoding='utf-8')
p=repo/'docs/PLAN.md';p.write_text('# 当前单WAN上传后续\n\nNSS117完成上传A/B/A2，实际parent overlimits与bulk drop已证明shaper活动，但B吞吐14.7→20.2Mbps回升，尚未稳定。下一步只降发送48→32Mbps；维持原30/29/1队列、默认950和全部期限，先定位吞吐切换及RT隔离，不先改预算。每次新flow/producer/checkpoint和独立撤销、新输入绑定、未知flow默认拒绝。保持常驻68与upTag0；不重装、扩WAN、共享全局预算、WiFi、autorate或桌面/新下载；最后一次集中真人。09:50起不新实验，完成终态和报告后暂停本夜接续。\n\n## NSS115历史计划\n\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
p=repo/'docs/ARTIFACT_INDEX.md';p.write_text('# 当前NSS117\n\n[汇总](../evidence/nss117-mainline.json) · [上传](../evidence/nss117-metrics.json) · [两轮](../evidence/nss117-trials.json) · [上行leaf](../evidence/nss117-uplink-proof.json) · [关闭](../evidence/nss117-endpoint-closure.json) · [终态](../evidence/nss117-final-audit.json) · [历史115 runtime](../evidence/nss115-runtime.json)。\n\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
dump(r/'export-receipt.json',{'passed':True,'newSources':len(source_hashes),'totalSources':len(manifest['sources']),'privateArtifacts':len(frozen),'uploadTcpMbps':speeds,'endpointsClosed':2});print(json.dumps({'exported':True,'sources':len(source_hashes),'totalSources':len(manifest['sources']),'uploadMbps':speeds}))
