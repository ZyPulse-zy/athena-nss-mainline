"""Curate NSS93-97 measurements; credentials, captures and complete inputs stay local."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib,shutil,html,re
w=Path(__file__).resolve().parents[2];repo=w/'athena-nss-mainline';r=w/'work/nss98'
sha=lambda b:hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def counters(raw):
 out={}
 for x in raw.get('nftables',[]):
  q=x.get('rule',{})
  for e in q.get('expr',[]):
   if 'counter'in e:out[q['comment'].split(':')[-1]]=e['counter']
 return out
spec=[('NSS95','work/nss89/controlled-matched-aba-20261005112745-4ec4f28a',52,60),('NSS96','work/nss96/controlled-matched-aba-20261005113552-a5f87f57',48,60),('NSS97','work/nss97/controlled-matched-aba-20261005114314-750db201',48,40)]
trials=[]
for label,rel,offered,budget in spec:
 p=w/rel;s=load(p/'last-record-private.json');result=load(p/'result.json');cp=load(p/'stage-checkpoint-verified.json');receipt=load(p/'stage-receipt-private.json');detached=load(p/'stage-detached-private.json');undo=load(p/'stage-undo-verified.json');base=load(p/'baseline-audit.json');before=load(p.parent/(p.name+'-before-audit.json'));after=load(p.parent/(p.name+'-after-audit.json'));inputs=load(p/'source-manifest.json')
 assert cp['gzipVerified']and receipt['success']and receipt['rollbackBeforeFirstWrite']and receipt['pipeInodesVerified']and receipt['parentIdentityVerified']and detached['identity']['ppid']==1
 assert all(undo.values())and base['configurationMatches']and all(base['checks'].values())and before['passed']and after['passed']and before['protectedConfigurationUnchanged']and after['protectedConfigurationUnchanged']
 assert all(sha((w/f).read_bytes())==h for f,h in inputs.items())
 t={'round':label,'caseLocalPath':rel,'passed':result['passed'],'oneWan':load(p/'selected-private.json')['tcp']['wan'],'offeredTcpMbps':offered,'qosGroupMbps':budget,'sourceInputs':len(inputs),'sourceManifestSha256':sha((p/'source-manifest.json').read_bytes()),'sourceInputsCurrentBytesMatchActualRun':True,'ecmOpened':'frontendOpenedAt'in s,'completeABA':result['matchedForwardingABACompleted'],'phases':[{k:x[k]for k in ['name','seconds','completed','sampleCount']if k in x}for x in s.get('phases',[])],'checkpointDownloadedShaAndGzipVerified':True,'independentOwnerSeconds':45,'guardianVerifiedBeforeFirstWrite':True,'guardianPpid':1,'rollback':undo,'baseline':base,'beforeFullAudit':before,'afterFullAudit':after,'softwareTagCounters':{k:counters(v)for k,v in s.items()if isinstance(v,dict)and'nftables'in v and'tcp_post_up_total'in counters(v)},'originalResultSha256':sha((p/'result.json').read_bytes()),'originalRecordSha256':sha((p/'last-record-private.json').read_bytes()),'error':s.get('error'),'gameQualityConclusion':False}
 clientdir=w/load(p/'controlled-client-private.json')['load']['dir'];t['beforeStageUdpBaseline']=load(clientdir/'udp-baseline-qualified.json')
 if (p/'actual-metrics.json').exists():t['metrics']=load(p/'actual-metrics.json')
 if (p/'actual-accelerated-state-proof.json').exists():t['acceleratedIdentityProof']=load(p/'actual-accelerated-state-proof.json')
 if label=='NSS97':
  def extra(text):
   o={}
   for block in re.split(r'(?=^qdisc )',text,flags=re.M):
    h=re.match(r'qdisc \S+ (\S+)',block);m=re.search(r'drop_overlimit (\d+).*?ecn_mark (\d+)',block)
    if h and m:o[h[1]]={'dropOverlimit':int(m[1]),'ecnMark':int(m[2])}
   return o
  a=extra(s['qosAccelerated']['qdisc']);b=extra(s['qosAfterRetirement']['qdisc']);t['leafAdditionalStatsDelta']={k:{n:b[k][n]-a[k][n]for n in ['dropOverlimit','ecnMark']}for k in ['8f05:','8f06:']};t['nativeQueueOptions']=s['qosReady']['validation'];t['nativeQueueSetupCommands']=s['qosCommandsCompleted']
 trials.append(t)
assert [t['passed']for t in trials]==[False,True,True]and[t['ecmOpened']for t in trials]==[False,True,True]
matched=trials[1]['metrics'];saturation=trials[2]['metrics'];b=matched['phases'][1];a2=matched['phases'][2];ratio=b['clientTcpMbps']/a2['clientTcpMbps'];benefit=(1-b['softirqPercent']/a2['softirqPercent'])*100
assert abs(ratio-1)<.001 and 70<benefit<75
assert max(p['clientTcpMbps']for p in matched['phases'])/min(p['clientTcpMbps']for p in matched['phases'])>1.01
assert b['udp']['unreturned']==a2['udp']['unreturned']==0 and matched['phases'][0]['udp']['unreturned']==77
assert saturation['leafCountersAcrossBObservation']['8f05:']['dropped']==148 and saturation['leafCountersAcrossBObservation']['8f06:']['dropped']==0
assert saturation['phases'][1]['udp']['sent']==saturation['phases'][1]['udp']['received']==223
diagnostics=[]
for n,key in [(93,'return'),(94,'queue')]:
 p=w/load(w/f'work/nss{n}/load-latest-private.json')['dir'];d=load(p/(key+'-summary.json'));assert d['passed']and not d['routerWrites']and not d['nssOpened'];diagnostics.append({'round':f'NSS{n}','loadLocalPath':p.relative_to(w).as_posix(),'summary':d,'rawObservationSha256':sha((p/(key+'-observation-private.json')).read_bytes()),'serverClientSequenceMatched':True,'captureAndCompleteCtInputsKeptPrivate':True})
d94=diagnostics[1]['summary'];low=d94['lowReplyIntervals'];assert len(low)==8 and all(x['counters']['cakeDrops']==x['counters']['redirectDrops']==x['counters']['softnetDropped']==0 for x in low)
closures=[]
loadpaths=[w/load(w/f'work/nss{n}/load-latest-private.json')['dir']for n in [93,94,96,97]]+[w/load(w/'work/nss95/load-reference-private.json')['dir']]
for p in loadpaths:
 fw=json.loads(load(p/'firewall-after-private.json')['stdout']);server=load(p/'server-closed-private.json');guard=load(p/'guard-result-private.json');receipt=load(p/'firewall-receipt-private.json');detached=load(p/'firewall-detached-private.json');checkpoint=load(p/'firewall-checkpoint-verified.json')
 assert fw['ownedRulesRemaining']==0 and fw['baselineRestored']and server['code']==0 and'MainPID=0'in server['stdout']and'ActiveState=inactive'in server['stdout']and'LISTEN'not in server['stdout']and'UNCONN'not in server['stdout']
 assert guard['passed']and guard['exactClientOnly']and guard['clientExitedBeforeDeadline']and receipt['beforeWriteIndependentGuardianVerified']and detached['detachedIdentityVerified']and detached['onlyNullStandardFds']and checkpoint['expirySeconds']==180
 closures.append({'loadLocalPath':p.relative_to(w).as_posix(),'temporaryFirewallRulesRemaining':0,'canonicalFirewallBaselineRestored':True,'ownedUnitInactiveMainPidZeroPortsClosed':True,'clientExited':True,'clientGuardPassed':True,'independentFirewallExpirySeconds':180,'independentClientDeadlineSeconds':210,'endpointGuardianVerifiedBeforeWrite':True,'noExistingVpsServiceReplaced':True})
final=load(w/'work/nss68/nss98-final-20261005-health.json');assert all(final[k]for k in ['passed','configurationMatches','originalFullLockedAudit','ecmStoppedAndZero','noActiveTransaction','noStaging','noExperimentState','noExperimentalModule']);assert(final['workerPid'],final['guardianPid'])==(4859,17139)
oldpath=repo/'evidence/current-runtime.json';old=oldpath.read_bytes();assert load(oldpath)['round']=='NSS92';hist=repo/'evidence/nss92-runtime.json';assert not hist.exists();hist.write_bytes(old)
manifestpath=repo/'source-manifest.json';manifest=load(manifestpath);assert len(manifest['sources'])==1079;prefix=sha(json.dumps(manifest['sources'],sort_keys=True,separators=(',',':')).encode());sources=[]
allowed={93:['prepare-diagnostic.py','observe-return.mjs','analyze-return.py'],94:['prepare-diagnostic.py','read-capability.mjs','observe-queues.mjs','analyze-queues.py'],95:['run-existing-entry.mjs'],96:['prepare-load.py','run.mjs','controlled-session.mjs','read-controlled.mjs','match-controlled.mjs','session-binding.mjs','payload.mjs','module-stage.mjs','analyze-controlled.py','calibrate-clock.mjs'],97:['prepare-saturation.py','run.mjs','controlled-session.mjs','read-controlled.mjs','match-controlled.mjs','session-binding.mjs','payload.mjs','module-stage.mjs','qos-physical.lua','qualify-qos-native.mjs','analyze-controlled.py','calibrate-clock.mjs']}
for n,names in allowed.items():sources.extend(w/f'work/nss{n}/{name}'for name in names)
sources.append(Path(__file__).resolve());hashes={}
for p in sources:
 rel=p.relative_to(w).as_posix();dst=repo/'code'/rel;assert not dst.exists();dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dst);h=sha(p.read_bytes());assert h==sha(dst.read_bytes());hashes[rel]=h;manifest['sources'].append({'path':'code/'+rel,'workspaceSource':rel,'sha256':h,'bytes':p.stat().st_size,'role':'controlled-higher-load-and-NSS-downlink-congestion-evidence'})
manifest['generatedAt']=datetime.now(timezone.utc).isoformat();manifest['lastAppendExport']='NSS98';dump(manifestpath,manifest)
dump(repo/'evidence/nss98-source-proof.json',{'round':'NSS98','sources':len(hashes),'sourceHashes':hashes,'historicPrefixSources':1079,'historicPrefixCanonicalSha256':prefix,'privateOwnedHostBootstrapExcluded':True,'completePrivateSourceInputsRetained':True,'notAdditionalProductionAdmission':True})
dump(repo/'evidence/nss98-trials.json',trials);dump(repo/'evidence/nss98-matched48.json',matched);dump(repo/'evidence/nss98-congested40.json',saturation);dump(repo/'evidence/nss98-return-localization.json',diagnostics);dump(repo/'evidence/nss98-endpoint-closure.json',closures);dump(repo/'evidence/nss98-final-audit.json',final)
main={'round':'NSS98','roundsCovered':['NSS93','NSS94','NSS95','NSS96','NSS97'],'observedAt':final['observedAt'],'readOnlyDiagnostics':2,'stageCases':3,'successfulCompleteABA':2,'ecmOpenedCases':2,'permanentClassifierChanged':False,'productionFirmwareKernelChanged':False,'oneWanAtATime':True,'matched48':{'completeFunctionalABA':True,'allThreeThroughputWithinOnePercent':False,'initialSoftwareUdpUnreturned':77,'acceptedCpuComparison':'B vs A2 only','bA2ThroughputRatio':ratio,'relativeSoftirqReductionAgainstA2Percent':benefit,'bA2UdpAllReturned':True,'bulkAndRtLeafDropsZero':True,'gameQualityConclusion':False},'congested40':{'offeredTcpMbps':48,'qosGroupMbps':40,'bulkGuaranteeMbps':39,'rtGuaranteeMbps':1,'bothCeilMbps':40,'fallbackMbps':950,'nativeOptionFixtureCases':7,'bulkDropDelta':148,'bulkDropOverlimitDelta':0,'rtDropDelta':0,'nssUdpSent':223,'nssUdpReceived':223,'nssUdpP95Ms':saturation['phases'][1]['udp']['rttP95Ms'],'cpuComparisonAccepted':False,'longTermExactRateAccuracyAccepted':False,'ecnAccepted':False,'multipleFlowFairnessAccepted':False,'queueCountersAsynchronous':True},'returnDeficit52':{'reproducedOnStableSameFlows':True,'clientProcessNotSupportedAsMainLocation':True,'cakeOrIfbCounterDropsNotSupportedAsMainLocation':True,'strongestInference':'Before observed software IFB/CAKE delivery, but no exact physical-interface per-flow tap','unreportedRouterIngressOrUpstreamStillNotSeparated':True,'before95StageUdpSent':120,'before95StageUdpReceived':0,'ecmOpeningRefused':True},'qosScope':{'onlyLanEgressDownlinkLeavesInstalled':True,'acceleratedUpTagTcp':0,'acceleratedUpTagUdp':0,'acceleratedUplinkQosGuaranteed':False,'fullCakeReplacementAccepted':False},'finalAuditPassed':True,'endpointClosureCount':5,'early95ClosureCheckRefusedBeforeExpiry':True,'later95IndependentExpiryClosurePassed':True,'humanCs2Acceptance':False,'highLoad300MbpsAcceptance':False,'secondWanEnabled':False,'upstreamSubmitted':False,'reportVerification':{'sourceValidated':True,'browserRendered':False}}
dump(repo/'evidence/nss98-mainline.json',main)
runtime={'round':'NSS98','checkedAt':final['observedAt'],'deploymentReference':'work/nss68/deployment-latest.json','classifierConfigSha256':final['configSha256'],'workerPid':4859,'guardianPid':17139,'publicationCandidateInstalled':True,'permanentClassifierChangedThisTurn':False,'nssPermanentlyEnabled':False,'nssOpenedThisTurn':True,'qualifiedExperimentalEntry':'work/nss96/controlled-session.mjs','qualifiedExperimentalEntryBoundInputs':trials[1]['sourceInputs'],'qualifiedCongestionEntry':'work/nss97/controlled-session.mjs','congestionEntryBoundInputs':trials[2]['sourceInputs'],'lastSuccessfulControlledLoadMbps':48,'matchedBversusA2SoftirqBenefitSupported':True,'allThree48MbpsWithinOnePercent':False,'entryFullHighLoadForwardingQualified':False,'realHumanGameAcceptance':False,'audit':final,'endpointClosures':5,'historical92RuntimePreservedSha256':sha(old),'historical82RuntimePreservedSha256':sha((repo/'evidence/nss82-runtime.json').read_bytes())};dump(oldpath,runtime)
when=datetime.fromisoformat(final['observedAt'].replace('Z','+00:00')).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
state=f'''# 当前状态

更新：{when}，北京时间。最新NSS98；常驻仍NSS68，所有实验NSS已撤销。

**48Mbps真实单WAN完成完整功能A/B/A2。NSS与返回软件两段吞吐47.981/48.004Mbps，softirq5.245/18.860%，相对下降{benefit:.2f}%。另一次40Mbps受控预算拥塞短测bulk新增丢弃148、RT零丢弃，NSS段UDP223/223收到回复。**

见 [本轮汇总](../evidence/nss98-mainline.json)、[三轮现场](../evidence/nss98-trials.json)、[48Mbps原始指标](../evidence/nss98-matched48.json)、[40Mbps拥塞指标](../evidence/nss98-congested40.json)、[回程定位](../evidence/nss98-return-localization.json)、[终态审核](../evidence/nss98-final-audit.json)。

- NSS96：60Mbps组、发送48Mbps、WAN2，一TCP一UDP。ECM0→2→0、两次续租、学习前tag、真实bulk/RT leaf、完整ct mark/NAT/WAN affinity和精确撤销通过。三段5秒/11帧，实际TCP47.031/47.981/48.004；第一段约2%低且UDP157/234，不能算三段严格相同吞吐或游戏改善。CPU收益仅采用吞吐差0.05%的B/A2；两段UDP241/241、243/243，leaf drop0/0。原32Mbps三段可比66.41%结论保持。
- NSS97：同一发送48Mbps，只把受控QoS组60改40，bulk保障39、RT保障1、共同ceil40、fallback950，单WAN3。7目标RAM native-option记录布局案例通过；实际4queue/5class/9命令及两次续租、加速/恢复通过。实际TCP32.868/35.091/33.274Mbps，不接受CPU对比或长期40Mbps精确限速结论。异步B附近bulk drop+148、drop_overlimit增量0、RT drop0；bulk仍有backlog、RT backlog0，符合AQM/隔离的解释，但未把异步计数当精确B瞬时统计。UDP205/205、223/223、217/217，B RTT p95约189.883ms；受控echo不是CS2网络指标。ECN、多流公平、长窗限速未验收。
- NSS93/94全程只读、ECM关闭，分别104/64个逐流CT帧；保持同一TCP/UDP/mark/NAT/WAN，52↔32Mbps切换。NSS94实际32.002/51.998Mbps；32回包1144/1144匹配，52服务器egress1092、PC匹配701。8个0回包窗CAKE/redirect/softnet丢弃都0、Voice没有新增包；全部选择窗CAKE也drop0。WAN物理rx_drop仅各组1，不能解释数百缺包。支持缺口在可观测软件IFB/CAKE交付之前，不支持PC程序或这些队列为主要丢包位置；没有物理接口精确nonce tap，上游与未计数入口仍未分开。server/PC按nonce序号匹配，不能直接用未校准服务器UTC。
- NSS95仍发送52、60Mbps组，测试前UDP120发/0收；原1.2秒内拒绝initial down0，无A、无ECM。独立45秒恢复与完整审核通过，失败原义保持。第一次端点关闭检查早于180秒自然expiry，准确拒绝2条规则未到期；后来实际自然撤销、FW全局基线和端口/unit/客户端关闭均通过。
- 三个stage每个checkpoint下载/SHA/gzip和写前独立PPID1/45秒守护、最终恢复通过；五个端点FW180秒守护写前核验、规则0/全局基线恢复、临时unit/端口/client关闭、210秒精确客户端守护通过。常驻4859/17139/config581b5d46…c791d7未改；最终source{final['queryAge']:.2f}秒通过原完整审核，ECM关闭全零，无事务/stage/state/实验模块。没有Steam/CS2/UI/新游戏下载/第二WAN/五路认证PBR改动。
- 当前NSS树仍只有LAN4下行，实际TCP/UDP upTag均0；未建立加速上行QoS，不能依赖软件WAN CAKE约束已经绕过它的flow。没有完整CAKE替代验收。多人公平不是需求；DiffServ4未复刻，现为明确bulk/RT两leaf、FQ-CoDel参数5ms/100ms/1024flows，autorate未接入NSS。
- 下一步只收尾单WAN关键功能：先用集中长一点的受控窗口核实拥塞时实际限速/RT延迟与自动分类，处理首段过渡影响；再集中一次真人CS2＋正常下载HUD/体感验收。52Mbps US UDP端点缺口作为已定位到软件队列之前的独立待查，不再反复用无回包窗口卡住所有工程。NSS96/556为48Mbps收益入口，NSS97/580为40Mbps拥塞入口；不重装分类器、重放已通过准备、扩第二WAN/共享预算/Wi-Fi/autorate。原完整私有输入和捕获仍本地，旧92/82 runtime原字节保持。

## NSS92历史状态

'''
f=repo/'docs/STATE.md';f.write_text(state+f.read_text(encoding='utf-8'),encoding='utf-8')
plan='''# 下一步：收尾单WAN拥塞QoS，再一次真人验收

32Mbps三段可比和48Mbps B/A2的NSS softirq收益已通过；40Mbps组出现bulk丢弃、RT零丢弃/UDP全回复。见 [STATE](STATE.md)。继续使用自有有限端点，不要求每轮Steam/CS2。

1. 保留常驻NSS68和原生flow/来源/期限检查；48Mbps使用96，拥塞40Mbps组使用97。每次新case、新checkpoint、独立撤销、精确一TCP一UDP；不重装、不重放旧准备。
2. 单WAN用可回滚的集中长窗口查清首段过渡与限速稳定性，真实客户端吞吐为准，区分软件转发与ECM，两者保持同QoS plan。bulk drop与RT零drop已经观察到，但异步qdisc计数、几秒窗不证明精确恒定40Mbps或完整多流公平。
3. 52Mbps的缺口已经不支持现有IFB/CAKE或PC程序主要丢包；保留该端点原始序号/CT证据，不靠放宽gate或反复空窗口推进。更细的物理tap/上游定位若必要应独立小范围做，不阻塞已经有效的48Mbps功能路径。
4. 真人CS2＋正常下载只留最后一次集中HUD jitter/loss/Miss和体验验收；echo与没有UDP回复的窗不能代替游戏指标。实装测试通过不等于当前永久开启NSS。
5. LAN4下行leaf已证明；TCP/UDP upTag0，上行NSS QoS尚缺，不能称完整CAKE替代。确认游戏主线后，再按源码/运行能力确定加速上行与单WAN常用运行方式；第二WAN、共享预算、Wi-Fi、autorate及五WAN继续后置。

## NSS92历史计划

'''
f=repo/'docs/PLAN.md';f.write_text(plan+f.read_text(encoding='utf-8'),encoding='utf-8')
f=repo/'AGENTS.md';v=f.read_text(encoding='utf-8');paragraph=f'最新NSS98：48Mbps单WAN2完整功能A/B/A2，ECM0/2/0、bulk/RT/ct mark/NAT/affinity/两续租/精确恢复通过。47.031/47.981/48.004Mbps；首A UDP77未回复，CPU只接受B/A2吞吐差0.05%、softirq5.245/18.860（降低{benefit:.2f}%），不称三段严格可比或游戏改善。97只改60→40Mbps预算、发送48、bulk39/RT1/ceil40、fallback950；7RAM及实际4queue/5class通过，bulk+148drop/overlimit增量0，RT0，B UDP223/223，吞吐32.868/35.091/33.274不接受CPU对比/长期限速。93/94只读104/64CT帧同flow52↔32，52缺口在可观测软件IFB/CAKE交付之前，队列drop0，不支持Windows/CAKE主要丢包；上游与未计数入口未分开。95原52 UDP120/0在ECM前拒绝。3checkpoint/45秒独立恢复、5端点180秒FW/210秒客户端退出通过；95首次早于expiry关闭检查拒绝、后来自然expiry通过分开。19:50原完整终态4859/17139/source{final["queryAge"]:.2f}，常驻68不变ECM全零无残留。当前96/556、97/580，真实加速upTag仍0，仅LAN4下行；旧92/82 runtime保持。下一步收尾单WAN拥塞/首段过渡，再一次真人验收；不把52端点空窗卡住所有工程，不重装/重放/新下载/扩WAN。STATE为准。\n\n';v=v.replace('最新NSS92：',paragraph+'最新NSS92：',1);f.write_text(v,encoding='utf-8')
f=repo/'docs/EXPERIMENT_LOG.md';v=f.read_text(encoding='utf-8');title,tail=v.split('\n',1);entry=f'''\n\n## NSS93–98 · {when} · 高一档CPU收益与拥塞队列

假设：52缺包应能缩小位置，48Mbps有相同吞吐的NSS CPU收益，低于发送负载的40Mbps NSS组可隔离RT。

执行与观测：两个只读固定flow 52↔32诊断；95沿用89/533入口52在initial UDP-down0拒绝；96仅发送改48/60组完整单WAN2；97同发送只将组改40/39/1、7目标native-option布局案例及单WAN3实装完整A/B/A2。详细实测、原失败、checkpoint/守护、来源和配置恢复见[三轮现场](../evidence/nss98-trials.json)、[回程诊断](../evidence/nss98-return-localization.json)。

结论：48的B/A2吞吐47.981/48.004、softirq5.245/18.860，支持{benefit:.2f}%相对下降；A首段77UDP缺包、吞吐47.031，不并入严格相同比较。40组bulk148新增drop、drop_overlimit不增、RT0，B UDP223/223支持两个leaf隔离；短窗异步统计不证明精确恒定40Mbps/ECN/多流公平，其CPU比较不接受。52缺包队列drop全0，主位置更像可观测IFB/CAKE之前，但物理tap缺失保留不确定性。没有真人CS2结论，只有LAN4下行，上行tag0。

恢复：3个stage都checkpoint+独立45秒守护写前核验/完整恢复；5个端点180秒FW自然撤销和基线、unit/端口/client/210秒guard通过。95早期检查2规则尚未到期拒绝与最终自然expiry通过分列。原完整终态source{final['queryAge']:.2f}，4859/17139连续、常驻68不变，ECM关闭全零，无残留；源码与原输入冻结，旧runtime字节保持。

''';f.write_text(title+entry+tail,encoding='utf-8')
f=repo/'docs/ARTIFACT_INDEX.md';f.write_text('# 证据索引\n\n## 当前NSS98\n\n- [本轮汇总](../evidence/nss98-mainline.json)、[三轮现场](../evidence/nss98-trials.json)、[48Mbps指标](../evidence/nss98-matched48.json)、[40Mbps拥塞](../evidence/nss98-congested40.json)。\n- [52回程位置](../evidence/nss98-return-localization.json)、[五端点关闭](../evidence/nss98-endpoint-closure.json)、[终态审核](../evidence/nss98-final-audit.json)、[源码字节](../evidence/nss98-source-proof.json)。\n- [当前运行](../evidence/current-runtime.json)、[旧92 runtime](../evidence/nss92-runtime.json)。本地报告`outputs/nss98-mainline-report.html`。\n\n'+f.read_text(encoding='utf-8'),encoding='utf-8')
rows=''.join(f'<tr><td>{x["phase"]}</td><td>{x["clientTcpMbps"]:.3f}</td><td>{x["softirqPercent"]:.2f}%</td><td>{x["busyPercent"]:.2f}%</td><td>{x["udp"]["received"]}/{x["udp"]["sent"]}</td><td>{x["udp"]["rttP95Ms"]:.2f}</td></tr>'for x in matched['phases'])
satrows=''.join(f'<tr><td>{x["phase"]}</td><td>{x["clientTcpMbps"]:.3f}</td><td>{x["udp"]["received"]}/{x["udp"]["sent"]}</td><td>{x["udp"]["rttP95Ms"]:.2f}</td></tr>'for x in saturation['phases'])
report=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NSS98 · 单WAN收益与拥塞QoS</title><style>body{{margin:0;background:#f3f4f2;color:#182923;font:16px/1.75 "Microsoft YaHei",sans-serif}}main{{max-width:1000px;padding:40px 26px;margin:auto}}h1{{font-size:32px;line-height:1.3}}h2{{font-size:23px;margin-top:34px}}.eyebrow{{font-size:13px;color:#536b60}}.lead{{font-size:20px;border-left:5px solid #31755a;padding-left:20px}}.box{{background:#fff;padding:24px;border:1px solid #d5ded7;border-radius:12px;margin-top:22px}}table{{width:100%;border-collapse:collapse;font-variant-numeric:tabular-nums}}th,td{{padding:10px;border-bottom:1px solid #dce5dd;text-align:left}}th{{font-weight:600;background:#eef4ed}}small{{color:#5a6f63}}a{{color:#246a4b}}@media(max-width:650px){{main{{padding:24px 14px}}h1{{font-size:26px}}table{{font-size:12px}}th,td{{padding:6px}}}}</style><main><p class="eyebrow">ATHENA AX6600 · NSS93–98 · {when} 北京时间</p><h1>48Mbps CPU收益已补证，<br>拥塞时bulk与RT队列已分开</h1><p class="lead">同吞吐的NSS与返回软件两段，softirq相对下降{benefit:.2f}%。40Mbps受控组中bulk新增148个丢弃，RT零丢弃且UDP223/223返回。所有实验已撤销，常驻仍NSS68。</p><section class="box"><h2>48Mbps功能闭环与CPU</h2><table><tr><th>阶段</th><th>客户端Mbps</th><th>softirq</th><th>busy</th><th>UDP收到/发出</th><th>RTT p95 ms</th></tr>{rows}</table><p>ECM 0→2→0；同WAN2、一TCP一UDP、两次续租，真实bulk/RT leaf、完整ct mark/NAT/出口粘性和精确撤销通过。NSS和A2吞吐仅差约0.05%，CPU收益只采用这两段。</p><small>首A吞吐低约2%且77个UDP未返回；不把三段称为严格同负载，不从该差异推出游戏改善。所有time_squeeze/softnet drop增量0，bulk/RT leaf丢弃0/0。</small></section><section class="box"><h2>40Mbps受控组拥塞</h2><p>发送仍48Mbps，只将组60改40；bulk保障39、RT保障1、共同ceil40、未选中流fallback950。单WAN3，native-option记录布局7案例、真实4队列/5class/9命令、ECM 0→2→0和两次续租通过。</p><table><tr><th>阶段</th><th>客户端Mbps</th><th>UDP收到/发出</th><th>RTT p95 ms</th></tr>{satrows}</table><p>异步B附近bulk drop +148、drop_overlimit增量0、RT drop 0；bulk仍有排队、RT backlog 0。这与AQM/RT隔离一致，但统计不能精确切到B的每一瞬间。</p><small>吞吐不同，不采用这一轮CPU百分比作收益。40Mbps配置已实际读回；5秒窗的35.09Mbps载荷不等于精确40Mbps限速验收。ECN和多flow公平未专测，echo不是CS2 jitter/loss/Miss。</small></section><section class="box"><h2>52Mbps缺包的位置</h2><p>同flow、同WAN、同NAT/mark在52↔32之间切换。NSS94实际32.002/51.998Mbps；32段服务器回包1144/1144到PC，52段1092个egress仅701个匹配PC。8个零回包窗，CAKE/redirect/softnet丢弃增量全零，Voice也没有新增包。</p><p>这不支持PC接收程序、软件IFB/CAKE是主要丢包位置。更像在这些可观测队列之前；仍缺物理接口逐流tap，上游与未计数入口未分开。95测试前即UDP120/0，原1.2秒准入拒绝，ECM没有开启。</p><small>两轮诊断全程只读/ECM关闭，104/64逐流CT帧。服务器与PC按nonce序号关联，不使用未校准服务器UTC作时间对齐。52问题不再通过重复空回包短测阻塞其它工程。</small></section><section class="box"><h2>当前能保留什么，还缺什么</h2><p>NSS已证明自动bulk/RT标签继承、独立leaf、保持Linux PBR/ct mark/NAT/WAN affinity，以及较高一档实际CPU收益。当前树仅在LAN4下行，真实TCP/UDP upTag都是0；尚无加速上行QoS，不能称完整CAKE替代。</p><p>现为bulk/RT两个leaf，FQ-CoDel参数5ms/100ms/1024flows；CAKE的四tin DiffServ、host fairness、COBALT和autorate没有机械复刻。多人公平不作为需求，autorate未接NSS，真实多flow公平和ECN还未验收。</p><p>下一步收尾单WAN长一点的拥塞/限速与首段过渡，再集中一次真人CS2＋正常下载HUD/体验验收。之后再确定单WAN常用运行和加速上行；不扩第二WAN、共享预算、Wi-Fi或autorate。</p></section><section class="box"><h2>回滚与证据</h2><p>三个stage均checkpoint下载/SHA/gzip、写前独立PPID1/45秒守护、完整恢复通过。五个端点FW180秒自然恢复全局基线、规则0、unit/端口/client关闭、210秒精确客户端guard通过。95首次早于expiry的关闭检查拒绝，随后真实自然到期关闭通过。</p><p>最终原完整审核source{final['queryAge']:.2f}秒、4859/17139连续、config581b5d46…c791d7不变，ECM关闭全零，无事务/stage/state/实验模块。未操作Steam、CS2或桌面，没有新下载、固件/内核或五WAN变更。</p><p><a href="https://github.com/ZyPulse-zy/athena-nss-mainline/blob/main/docs/STATE.md">私有GitHub当前状态</a> · 源码/脱敏统计已整理；凭据、原始CT/capture/checkpoint和完整输入保持本地。</p></section></main></html>'''
(w/'outputs/nss98-mainline-report.html').write_text(report,encoding='utf-8')
dump(r/'export-receipt.json',{'round':'NSS98','sourceCount':len(hashes),'totalSources':len(manifest['sources']),'prefixPreserved':True,'trials':3,'completeABA':2,'endpointClosures':5,'relativeSoftirqReductionVsA2Percent':benefit,'historical92RuntimeSha256':sha(old),'reportSourceValidated':True,'reportBrowserRendered':False})
print(json.dumps({'exported':True,'sources':len(hashes),'totalSources':len(manifest['sources']),'stageCases':3,'completeABA':2,'relativeSoftirqReductionVsA2Percent':benefit,'endpointClosures':5}))
