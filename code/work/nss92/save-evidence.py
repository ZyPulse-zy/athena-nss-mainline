"""Archive measured NSS84-91 trials; all credentials and raw captures stay local."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,html
w=Path(__file__).resolve().parents[2];repo=w/'athena-nss-mainline'
sha=lambda b:hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def counters(raw):
 c={}
 for x in raw.get('nftables',[]):
  r=x.get('rule',{})
  for e in r.get('expr',[]):
   if 'counter'in e:c[r['comment'].split(':')[-1]]=e['counter']
 return c
spec=[(84,'20261005092927-19c76faf','initial-ack-and-pending'),(87,'20261005100412-54394880','client-status-rename-crash'),(88,'20261005101439-546037e0','second-snapshot-skew-and-pending'),(89,'20261005102717-95a82e4e','52-udp-return-missing'),(91,'20261005103412-0f877edb','matched-32'),(89,'20261005103839-6dab30d6','52-repeat-udp-return-missing')]
trials=[]
for n,suffix,label in spec:
 p=w/f'work/nss{n}/controlled-matched-aba-{suffix}';r=load(p/'last-record-private.json');result=load(p/'result.json');cp=load(p/'stage-checkpoint-verified.json');receipt=load(p/'stage-receipt-private.json');d=load(p/'stage-detached-private.json');undo=load(p/'stage-undo-verified.json');base=load(p/'baseline-audit.json');before=load(p.parent/(p.name+'-before-audit.json'));after=load(p.parent/(p.name+'-after-audit.json'));inputs=load(p/'source-manifest.json')
 assert cp['gzipVerified']and receipt['success']and receipt['rollbackBeforeFirstWrite']and receipt['pipeInodesVerified']and receipt['parentIdentityVerified']and d['identity']['ppid']==1
 assert all(undo.values())and base['configurationMatches']and all(base['checks'].values())and before['passed']and after['passed']and before['protectedConfigurationUnchanged']and after['protectedConfigurationUnchanged']
 assert all(sha((w/f).read_bytes())==h for f,h in inputs.items())
 t={'round':f'NSS{n}','name':label,'caseLocalPath':p.relative_to(w).as_posix(),'passed':result['passed'],'oneWan':load(p/'selected-private.json')['tcp']['wan'],'ecmOpened':'frontendOpenedAt'in r,'phases':[{k:x[k]for k in ['name','seconds','completed','sampleCount']if k in x}for x in r.get('phases',[])],'sourceInputs':len(inputs),'sourceManifestSha256':sha((p/'source-manifest.json').read_bytes()),'sourceInputsCurrentBytesMatchActualRun':True,'checkpointDownloadedShaAndGzipVerified':True,'independentOwnerSeconds':45,'guardianVerifiedBeforeFirstWrite':True,'guardianPpid':1,'rollback':undo,'baseline':base,'beforeFullAudit':before,'afterFullAudit':after,'originalResultSha256':sha((p/'result.json').read_bytes()),'originalRecordSha256':sha((p/'last-record-private.json').read_bytes()),'softwareTagCounters':{k:counters(v)for k,v in r.items()if isinstance(v,dict)and 'nftables'in v and 'tcp_post_up_total'in counters(v)},'rereads':r.get('tagCounterRereads',[]),'qosGroupMbps':60,'offeredTcpMbps':32 if n==91 else 52,'gameQualityConclusion':False}
 if (p/'actual-metrics.json').exists():t['metrics']=load(p/'actual-metrics.json')
 if(p/'actual-accelerated-state-proof.json').exists():t['acceleratedIdentityProof']=load(p/'actual-accelerated-state-proof.json')
 if n==87:
  clientdir=w/load(p/'controlled-client-private.json')['load']['dir'];err=(clientdir/'client-stderr-private.txt').read_text(encoding='utf-8')
  assert 'EPERM'in err and 'rename'in err;t['clientFailure']={'windowsStatusRenameEpermCaptured':True,'clientExitedBeforeEcmOpening':True,'projectionAbsenceAloneDoesNotProveCtExit':True,'completeSameSourceDiagnosticUnavailable':True,'rawErrorSha256':sha(err.encode())}
 trials.append(t)
assert len(trials)==6 and sum(t['passed']for t in trials)==1 and sum(t['ecmOpened']for t in trials)==1
matched=trials[4]['metrics'];ps=matched['phases'];tcp=[p['clientTcpMbps']for p in ps];soft=[p['softirqPercent']for p in ps];reduction=(1-soft[1]/((soft[0]+soft[2])/2))*100
assert matched['passed']and max(tcp)/min(tcp)<1.01 and all(p['udp']['unreturned']==0 for p in ps)and [p['acceleratedCounts']for p in ps]==[[0],[2],[0]]and 60<reduction<70
closures=[]
for n in [84,85,86,87,88,89,91]:
 for p in sorted(x for x in(w/f'work/nss{n}').glob('load-*')if x.is_dir()):
  fw=json.loads(load(p/'firewall-after-private.json')['stdout']);server=load(p/'server-closed-private.json');guard=load(p/'guard-result-private.json')
  assert fw['ownedRulesRemaining']==0 and fw['baselineRestored']and server['code']==0 and 'MainPID=0'in server['stdout']and 'ActiveState=inactive'in server['stdout']and 'LISTEN'not in server['stdout']and 'UNCONN'not in server['stdout']
  assert guard['passed']and guard['exactClientOnly']and guard['clientExitedBeforeDeadline']
  closures.append({'round':f'NSS{n}','loadLocalPath':p.relative_to(w).as_posix(),'temporaryFirewallRulesRemaining':0,'canonicalFirewallBaselineRestored':True,'ownedUnitInactiveMainPidZeroPortsClosed':True,'clientExited':True,'clientGuardPassed':True,'independentFirewallExpirySeconds':180,'independentClientDeadlineSeconds':210,'noExistingVpsServiceReplaced':True})
assert len(closures)==9
getter=load(w/'work/nss89/getter-qualified.json');status=load(w/'work/nss88/client-publication-qualified.json');qos=load(w/'work/nss84/qos-native-qualification.json');assert getter['passed']and getter['cases']==30 and status['passed']and status['cases']==3 and qos['passed']and len(qos['checks'])==7
final=load(w/'work/nss68/nss92-final-20261005-health.json');assert final['passed']and final['configurationMatches']and final['originalFullLockedAudit']and final['workerPid']==4859 and final['guardianPid']==17139
assert all(final[k]for k in ['ecmStoppedAndZero','noActiveTransaction','noStaging','noExperimentState','noExperimentalModule'])
capture88=load(w/'work/nss88/load-20261005101340-1aba2e28d4808e64/endpoint-capture-summary.json');capture89=load(w/'work/nss89/load-20261005102557-2986b51b6b64a4cf/endpoint-capture-summary.json')
assert capture88['authenticatedIncoming']==capture88['outgoingEchoes']==capture88['matchingClientRepliesAtRead']==249
assert capture89['authenticatedIncoming']==247 and capture89['outgoingEchoes']==246 and capture89['matchingClientRepliesAtRead']==33
oldpath=repo/'evidence/current-runtime.json';old=oldpath.read_bytes();assert load(oldpath)['round']=='NSS82';hist=repo/'evidence/nss82-runtime.json';assert not hist.exists();hist.write_bytes(old)
manifestpath=repo/'source-manifest.json';manifest=load(manifestpath);assert len(manifest['sources'])==1050;prefix=sha(json.dumps(manifest['sources'],sort_keys=True,separators=(',',':')).encode());sources=[]
allowed={84:['qos-physical.lua','qualify-qos-native.mjs'],85:['fast-path.lua','qualify-getter.mjs'],88:['qualify-client.mjs'],89:['controlled-session.mjs','read-controlled.mjs','match-controlled.mjs','current-audit-diagnostic.mjs','session-binding.mjs','payload.mjs','module-stage.mjs','fast-path.lua','tag-counter-audit.lua','qos-physical.lua','qualify-getter.mjs','calibrate-clock.mjs','analyze-controlled.py','capture-endpoint.mjs','client-watchdog.ps1'],91:['controlled-session.mjs','read-controlled.mjs','match-controlled.mjs','session-binding.mjs','payload.mjs','module-stage.mjs','analyze-controlled.py']}
for n,names in allowed.items():sources.extend(w/f'work/nss{n}/{name}'for name in names)
# Preserve only the generic publication function; SSH credentials/bootstrap stay private.
client=(w/'work/nss88/ssh-client.mjs').read_text(encoding='utf-8');a=client.index('function stamp()');b=client.index('function stop(',a);snippet=w/'work/nss92/status-publication.js';snippet.write_text('// Context supplied by the private controlled client.\n'+client[a:b],encoding='utf-8');sources.extend([snippet,Path(__file__).resolve()]);hashes={}
for p in sources:
 rel=p.relative_to(w).as_posix();dst=repo/'code'/rel;assert not dst.exists();dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dst);h=sha(p.read_bytes());assert h==sha(dst.read_bytes());hashes[rel]=h;manifest['sources'].append({'path':'code/'+rel,'workspaceSource':rel,'sha256':h,'bytes':p.stat().st_size,'role':'bounded-tag-observation-and-controlled-60Mbps-QoS-evidence'})
manifest['generatedAt']=datetime.now(timezone.utc).isoformat();manifest['lastAppendExport']='NSS92';dump(manifestpath,manifest)
dump(repo/'evidence/nss92-source-proof.json',{'round':'NSS92','sources':len(hashes),'sourceHashes':hashes,'historicPrefixSources':1050,'historicPrefixCanonicalSha256':prefix,'privateOwnedHostBootstrapExcluded':True,'completePrivateSourceInputsRetained':True,'fullSourceExportIsNotStandaloneTransportBootstrap':True,'notAdditionalProductionAdmission':True})
dump(repo/'evidence/nss92-trials.json',trials);dump(repo/'evidence/nss92-matched32.json',matched);dump(repo/'evidence/nss92-final-audit.json',final);dump(repo/'evidence/nss92-endpoint-closure.json',closures)
dump(repo/'evidence/nss92-tag-reader.json',{'nativeQualification':getter,'maximumRereadsPerGetter':1,'singleSnapshotEqualityOnlyFastPath':True,'monotonicAndCrossSnapshotOverlapRequired':True,'allWrongTagPacketAndByteCountersZeroRequired':True,'completeExactOwnedPolicyNormalizerUnchanged':True,'originalNativeSourceLifetimeAndFlowIdentityChecksUnchanged':True,'bidirectionalPositiveCountersBeforeEcmRequired':True,'initialMissingTrafficStillRefusedWithinOriginal1p2Seconds':True,'actual88FirstCounters':trials[2]['softwareTagCounters']['initialTagsFirst'],'actual88SecondCounters':trials[2]['softwareTagCounters']['initialTags'],'actual91TwoBoundaryBrackets':trials[4]['rereads'],'oldFailedResultsPreserved':True,'firmwareMisTagProved':False,'kernelBugProved':False,'upstreamSubmitted':False})
dump(repo/'evidence/nss92-load-observations.json',{'offered52MbpsUdpReturnUnstableBeforeEcm':True,'endpointTap88':capture88,'endpointTap89':capture89,'serverTransmitTapCorrectedFromIpOnlyToAllProtocols':True,'capture87NoTxWasInstrumentationLimitation':True,'absenceBeginsBeforeTagInstallation':True,'absencesAlsoAfterRollback':True,'localizationBetweenOwnedServerEgressAndClientReceive':True,'routerOrUpstreamOrWindowsRootCauseUnproved':True,'cs2LossMissNotMeasured':True,'prepareOnly85And86Runs':3,'prepareOnly85And86EcmOpened':False,'clientPublicationFixQualification':status,'actual87ClientEpermFailurePreserved':True,'postPatchRealEpermRecurrenceNotClaimed':True})
runtime={'round':'NSS92','checkedAt':final['observedAt'],'deploymentReference':'work/nss68/deployment-latest.json','classifierConfigSha256':final['configSha256'],'workerPid':4859,'guardianPid':17139,'publicationCandidateInstalled':True,'permanentClassifierChangedThisTurn':False,'nssPermanentlyEnabled':False,'nssOpenedThisTurn':True,'qualifiedExperimentalEntry':'work/nss91/controlled-session.mjs','qualifiedExperimentalEntryBoundInputs':trials[4]['sourceInputs'],'lastSuccessfulControlledLoadMbps':32,'lastAttempted52MbpsEntry':'work/nss89/controlled-session.mjs','controlledRealWanABACompleted':True,'matched32MbpsSoftirqBenefitSupported':True,'entryFullHighLoadForwardingQualified':False,'realHumanGameAcceptance':False,'audit':final,'endpointClosures':9,'historical82RuntimePreservedSha256':sha(old)};dump(oldpath,runtime)
main={'round':'NSS92','roundsCovered':['NSS84','NSS85','NSS86','NSS87','NSS88','NSS89','NSS91'],'observedAt':final['observedAt'],'permanentClassifierChanged':False,'productionFirmwareKernelChanged':False,'stageCases':6,'successfulCompleteABA':1,'scope':{'oneWanAtATime':True,'controlledTcpFlows':1,'controlledUdpFlows':1,'qosGroupMbps':60,'offeredTcpMbpsCases':[52,32]},'matched32':{'actualThroughputMatched':True,'matchedShortWindowSoftirqBenefitSupported':True,'relativeReductionAgainstMeanSoftwarePercent':reduction,'cpuBusyAuxiliaryOnly':True,'udpNoUnreturnedInAllThreeWindows':True,'leafDropsBothZero':True,'secondsPerPhase':[p['seconds']for p in ps]},'offered52':{'matchedABACompleted':False,'noEcmOpeningInTwoUpdatedGetterTrials':True,'udpReturnPathUnstable':True,'rootCauseUnproved':True,'notNssCpuBenefitEvidence':True},'qos':{'original20to60OnlyRateLiteralsChanged':True,'nativeOptionCases':7,'rateAccuracyAt60NotYetSaturationTested':True,'congestionFqAqmEcnHostFairnessDiffservAutorateNotRevalidatedAt60':True},'tagReader':{'targetRamCases':30,'twoActualSuccessfulBoundaryBrackets':True,'originalIncorrectAtomicEqualityAssumptionReplaced':True,'nativeGateFlowScopeAndLifetimesUnchanged':True},'clientStatusPublication':{'targetWindowsLocalCases':3,'transientEpermEbusyNoLongerKillTraffic':True,'otherIoFailuresRemainFatal':True},'finalAuditPassed':True,'endpointClosureCount':9,'humanCs2Acceptance':False,'highLoad300MbpsAcceptance':False,'secondWanEnabled':False,'upstreamSubmitted':False,'reportVerification':{'sourceValidated':True,'browserRendered':False}}
dump(repo/'evidence/nss92-mainline.json',main)
when=datetime.fromisoformat(final['observedAt'].replace('Z','+00:00')).astimezone().strftime('%Y-%m-%d %H:%M')
state=f'''# 当前状态

更新：{when}，北京时间。最新NSS92；常驻仍NSS68，所有NSS实验已撤销。

**60Mbps受控QoS预算下，真实32Mbps的一TCP＋低速UDP完成完整单WAN A→B→A2。客户端31.996/32.023/32.003Mbps，softirq15.19→4.97→14.43%，相对两段软件均值下降{reduction:.2f}%；UDP239/239、238/238、239/239，bulk/RT零丢弃。ECM0→2→0、NAT/PBR/WAN affinity和精确恢复通过。**

见 [汇总](../evidence/nss92-mainline.json)、[六次现场记录](../evidence/nss92-trials.json)、[32Mbps完整对照](../evidence/nss92-matched32.json)、[标签计数修正](../evidence/nss92-tag-reader.json)、[回程与客户端故障](../evidence/nss92-load-observations.json)、[终态审核](../evidence/nss92-final-audit.json)。

- 用户已允许工程以受控真实TCP/UDP推进；无需每轮开Steam/CS2。真人游戏保留为最后集中验收。永久分类器未改，4859/17139连续，config581b5d46…c791d7；终态source2.88秒通过原完整审核，ECM关闭全零，无事务/stage/state/实验模块。
- 主要QoS变量从20提高到60Mbps，bulk保障59Mbps、RT保障1Mbps，二者ceil60，默认fallback950；目标原生选项7案例通过。当前32Mbps没有压到60Mbps上限，不能声称60Mbps限速精度或拥塞/AQM/ECN已验收；上传仍是现有软件路径/未设NSS上传tag。
- 84/88多规则计数继续出现1包40/60/1500字节偏差，第二次也可偏差。89替换活动counter严格同瞬时相等假设：精确完整policy验证保持，错误tag/neighbor包和字节必须全零；最多重读一次，两帧所有total/expected需单调且交叉区间相交，学习前仍要真实双向包。30目标RAM案例包含真实88帧与错误字节、缺方向、倒退等反例；91现场两次边界重读成功。6秒来源/12秒native/45秒owner等未改。原失败保持。
- 87实际客户端在Windows status原子替换时EPERM退出，之后TCP不在分类投影。88对EPERM/EBUSY延后状态上报、数据连接继续，其它IO失败仍退出；3本地案例通过。实际后续没再次捕获EPERM，不冒充现场故障注入恢复。
- 52Mbps下当前UDP回程窗口不稳定：正确ETH_P_ALL端点tap曾249发出/249客户端收到；另一5秒247入、246发出、仅33客户端记录。缺包在安装tag前和撤销后也有。89两次使用新检查均因initial UDP-down为0，在原1.2秒内拒绝且不开放ECM；不能归因NSS，也不假定是52Mbps造成。根因暂定位在自有服务器egress至客户端接收之间，尚未区分上游/路由器/Windows。
- 六个stage各checkpoint下载/SHA/gzip、写前独立PPID1/45秒守护与完整恢复审核通过；九个负载端点FW180秒独立恢复、规则0、原全局基线恢复、临时unit/端口关闭、客户端/210秒精确守护退出。没有新游戏下载、游戏/HUD/UI、购买/卸载、固件/内核、生产分类器或五WAN/PBR改动。
- 可直接使用32Mbps已通过入口`work/nss91/controlled-session.mjs`（555实际绑定输入），52Mbps诊断入口`work/nss89/controlled-session.mjs`（533输入）。源码/完整输入按新case冻结，不能修改旧证据。原始CT/nonce/端点配置/凭据/checkpoint/模块仍私有；[旧82 runtime原字节](../evidence/nss82-runtime.json)保持。
- 下一步集中定位受控UDP回程缺包：优先只读关联服务器发出、路由器收/发和客户端接收；不能用没有回包的窗口评价RT QoS。随后同一60Mbps预算补52Mbps完整可比A/B/A2，再一次真人CS2＋正常下载验收。已经通过的分类器安装、30项计数检查、32Mbps闭环不重放；不扩第二WAN、共享预算、Wi-Fi或autorate。

## NSS82历史状态

'''
f=repo/'docs/STATE.md';f.write_text(state+f.read_text(encoding='utf-8'),encoding='utf-8')
plan='''# 下一步：定位52Mbps受控UDP回程，再完成高一档单WAN闭环

32Mbps相同负载下实际NSS CPU收益和自动bulk/RT映射已通过；原18Mbps结论也保留。当前唯一工程缺口是52Mbps窗口回包不稳定，见 [STATE](STATE.md)。

1. 不再重装分类器、重放准备或要求用户反复Steam/CS2。读实际68部署与原完整审核，保持新实例/新flow/新checkpoint/独立撤销。
2. 用自有受控端点的序列包只读定位server egress→router ingress/egress→client receive缺口；原87 IP-only tap看不到TX，须用已纠正的ETH_P_ALL。没有router tcpdump，不能把server发出当PC收到，也不能把丢包直接归因NSS或带宽。
3. 只改变一个负载或端点变量，保持60Mbps预算和已通过的89计数合同；入口91适用32Mbps、89适用52Mbps。缺少真实双向tag包继续在原期限内拒绝，不能靠放宽流范围或伪造指标通过。
4. 用同一TCP/UDP、单WAN、新checkpoint/独立45秒owner做software→NSS→software；记录真实客户端吞吐/softirq/squeeze/leaf/UDP。完整且吞吐可比后再评价52Mbps，当前32Mbps短窗66.41%不外推300Mbps或长期稳定。
5. 工程更高一档通过后，最后集中一次真人CS2＋正常下载HUD和体验验收；再评估单WAN常用运行方式。多WAN、共享预算、Wi-Fi、autorate、bridge shaper/ECN/HTB dump backlog后置。

## NSS82历史计划

'''
f=repo/'docs/PLAN.md';f.write_text(plan+f.read_text(encoding='utf-8'),encoding='utf-8')
f=repo/'AGENTS.md';s=f.read_text(encoding='utf-8');anchor='最新NSS82：';assert anchor in s
headline=f'最新NSS92：60Mbps组下32Mbps真实同WAN2 TCP/UDP完整A/B/A2、ECM0→2→0、正确bulk/RT/NAT/PBR/续租/撤销通过；31.996/32.023/32.003Mbps可比，softirq15.19/4.97/14.43%，相对软件均值降{reduction:.2f}%，UDP239/239、238/238、239/239，leaf drop0/0。活动counter观察改为最多一次单调/交叉范围重读、wrong tag包/字节0、完整policy与双向包保持；30 RAM与91两次实际边界通过，原TTL/native scope不变。87客户端EPERM退出故障保存，88容忍临时status共享冲突3案例，实际未再触发不称注入恢复。52窗口回程不稳，新getter两次initial down0写后/ECM前拒绝；server发出246/PC33，亦有249/249，根因未定，不归因NSS。6 checkpoint/独立45秒恢复，9端点180秒FW恢复、unit/端口/client退出。18:42原完整审核4859/17139/source2.88，常驻68不变、ECM关闭全零无残留。当前成功入口91/555、52诊断89/533；旧82 runtime原字节与原失败保持。下一步只定位UDP回程后补52Mbps可比闭环，再一次真人验收，不重装/重放/新游戏下载/扩WAN；STATE为准。\n\n'
f.write_text(s.replace(anchor,headline+anchor,1),encoding='utf-8')
f=repo/'README.md';f.write_text('# Athena NSS 主线\n\n最新 [NSS92单WAN32Mbps闭环](evidence/nss92-mainline.json)：60Mbps预算下，相同32Mbps真实TCP/UDP中softirq约下降66.4%，三段UDP全部返回、ECM0→2→0与恢复通过。52Mbps回程缺包根因未定，当前NSS已撤销、常驻68未改。先读 [状态](docs/STATE.md) 和 [计划](docs/PLAN.md)。\n\n'+f.read_text(encoding='utf-8'),encoding='utf-8')
f=repo/'docs/ARTIFACT_INDEX.md';f.write_text('# 证据索引\n\n## 当前NSS92\n\n- [实测汇总](../evidence/nss92-mainline.json)、[六次现场及失败](../evidence/nss92-trials.json)、[32Mbps可比对照](../evidence/nss92-matched32.json)。\n- [新计数合同](../evidence/nss92-tag-reader.json)、[回程/客户端观测](../evidence/nss92-load-observations.json)、[最终审核](../evidence/nss92-final-audit.json)、[九端点恢复](../evidence/nss92-endpoint-closure.json)、[源字节冻结](../evidence/nss92-source-proof.json)。\n- [当前运行](../evidence/current-runtime.json)、[旧82 runtime](../evidence/nss82-runtime.json)，本地报告`outputs/nss92-mainline-report.html`。\n\n'+f.read_text(encoding='utf-8'),encoding='utf-8')
f=repo/'docs/EXPERIMENT_LOG.md';f.write_text(f.read_text(encoding='utf-8')+f'''\n\n## 2026-10-05 NSS84–92：60Mbps组、计数观察根因与32Mbps可比闭环

- 主要QoS变量20→60Mbps，bulk59/RT1/ceil60，默认950、FQ-CoDel参数不变，实际source反向替换与旧字节相等，原生layout7例。52发送/1GiB/180秒客户端上限，45秒owner及原native/source期限保持。
- 84 ACK1包40字节＋UDP未返回，未执行A/ECM；85按精确ACK及pending做23RAM后，prep90%回包不达，86一轮8个自己TCP候选未同WAN、另一同WAN但缺最近回包；均未stage。87去掉冗余echo质量门槛后A仅2秒/5帧，TCP分类投影消失；实际客户端stderr是Windows EPERM status rename崩溃，完整同源CT诊断不可用，不能只按投影定CT退出。没有ECM。
- 88修客户端临时EPERM/EBUSY，3本地正负例，其它IO错误仍fatal；后来无实际EPERM复发不称现场注入恢复。被动tap改ETH_P_ALL，249入/249出/249客户端回包证明原87 IP-only零TX只是观察限制；后续initial先ACK偏差、重读又TCP-down偏差，UDPdown0，原失败保留且不开放ECM。
- 89按正确观察合同替换逐规则原子相等假设，最多1重读、total/expected两帧单调且交叉范围相交，wrong tag/neighbor包及字节0，原完整NFT policy及新flow/TTL/classifier/native gate不变；30目标RAM正负例含真实88两帧及缺方向仍拒绝。实际52两轮initial UDPdown为0在原1.2秒截止拒绝，均无A/ECM；一次端点5秒247入、246出、客户端只33，安装tag前及撤销后亦有缺包，原因未定。
- 91仅把发送52→32，60QoS和89fast字节不变，WAN2完整A5.01/B5.01/A25.01、各11帧、ECM0/2/0。客户端31.996/32.023/32.003Mbps，LAN4均33.57Mbps左右，softirq15.19/4.97/14.43%、busy28.81/15.93/30.03%，time_squeeze/softnet drop全0。两次A2边界计数bracket现场通过，2次确认renewal、精确retire、mark/NAT/affinity通过。
- 32Mbps相对软件均值softirq下降{reduction:.2f}%；UDP239/239、238/238、239/239，p95约198.39/198.06/198.39ms，为自有端点RTT而非CS2。B附近异步leaf bulk+14541包/+20675746字节、RT+242/+41140，drop0/0；未饱和60，因此不验收60准确限速、拥塞FQ/AQM/ECN或游戏收益。
- 六个实际stage各checkpoint/SHA/gzip、独立PPID1/45秒恢复和前后原完整保护审核通过；九个有限端点全部180秒FW基线恢复、0规则、临时unit/端口关闭、client/210秒精确守护退出。18:42原完整终态source2.88、worker4859/guardian17139连续，ECM关闭全零，无事务/stage/state/module，常驻68不变。
- 92封存实测/源码与旧82 runtime原字节；完整原始CT/nonce/端点凭据/checkpoint/模块/绑定留私有，无上游Issue/PR。下一步只定位52回程并补更高同負载闭环，最后一次真人CS2验收，不重装分类器/重复准备/新游戏/扩第二WAN。\n''',encoding='utf-8')
f=repo/'docs/ISSUE_TAG_COUNTER_SNAPSHOT.md';f.write_text(f.read_text(encoding='utf-8')+'''\n\n## NSS89–91更新：修正观察合同

见 [实际两帧和新合同](../evidence/nss92-tag-reader.json)。NSS88同一次initial读：先TCP-up expected多1包/60字节；第二次up相等而down expected又多1包/1500字节。错误tag仍0，证明一次重读后仍要求严格同瞬时相等会继续误拒绝活动流。UDPdown独立为0，不能被计数修正冒充为有双向流量。

本地文件`code/work/nss89/fast-path.lua`和`tag-counter-audit.lua`：每次live先由未改的normalizer验证完整自有NFT policy；counter数值非负整数、包/字节零状态一致，所有unexpected和neighbor包及字节0。第一帧exact equal可直接验证；skew时只再读1帧，total/expected各自单调、两帧交叉区间相交才接受观察。学习前仍需四方向正包，initial缺包仅按原1.2秒等候。native flow资格、ct identity/mark/NAT、来源/租期和默认拒绝不变。读数本身不授予加速。

30目标RAM案例覆盖实际88帧、wrong-tag byte-only、负数/缺counter/倒退/无重叠/缺方向；NSS91实际成功A2前后各一次bracket。52的两轮缺UDPdown继续拒绝，32Mbps完整A/B/A2和正确bulk/RT实际通过。这个已复现的问题属于本项目审计控制器假设，当前没有充分证据提交给Linux或NSS上游。\n''',encoding='utf-8')
headers='<tr><th>阶段</th><th>TCP Mbps</th><th>softirq</th><th>CPU busy</th><th>UDP回复/发送</th><th>RTT p95 ms</th><th>squeeze</th><th>ECM</th></tr>'
rows=''.join('<tr>'+''.join(f'<td>{html.escape(str(x))}</td>'for x in [p['phase'],f"{p['clientTcpMbps']:.3f}",f"{p['softirqPercent']:.2f}%",f"{p['busyPercent']:.2f}%",f"{p['udp']['received']}/{p['udp']['sent']}",f"{p['udp']['rttP95Ms']:.2f}",p['timeSqueezeDelta'],p['acceleratedCounts'][0]])+'</tr>'for p in ps)
report=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NSS92 · 32Mbps可比闭环</title><style>body{{font-family:system-ui,"Microsoft YaHei",sans-serif;background:#f2f5f7;color:#1c2f40;margin:0;line-height:1.75}}main{{max-width:1050px;margin:32px auto;padding:32px;background:white;border-radius:15px}}h1{{font-size:30px}}h2{{font-size:22px;margin-top:32px}}.lead{{background:#e9f5ed;padding:18px;border-left:4px solid #28774c}}table{{border-collapse:collapse;width:100%;font-size:14px}}td,th{{text-align:left;border-bottom:1px solid #dce3e8;padding:10px}}.scroll{{overflow:auto}}small{{color:#576674}}@media(max-width:700px){{main{{margin:12px;padding:18px}}}}</style><main><small>{when} 北京时间 · 常驻分类器未改 · 实验已完全撤销</small><h1>同32Mbps负载下，NSS softirq下降{reduction:.1f}%</h1><p class="lead">自动分类 → NSS bulk/RT leaf → 单WAN实际TCP/UDP闭环通过。三段真实TCP均约32Mbps，UDP全部返回；软件恢复后softirq回升，支持这次短窗口的转发收益。</p><h2>完整 software → NSS → software</h2><p>WAN2、同一TCP和UDP，真实常驻分类器判定BULK/RT；60Mbps组预算，bulk保障59Mbps、RT保障1Mbps并可借至60Mbps，默认fallback950Mbps。每段5.01秒/11帧，观察器一致。源/ct mark/NAT/出口粘性、两次native续租和精确撤销通过。</p><div class="scroll"><table>{headers}{rows}</table></div><p>B附近异步leaf：bulk +14541包 / 20675746字节，RT +242包 / 41140字节，均0丢弃。time_squeeze和softnet drop全0；时钟边界不确定约59.5ms已排除。RTT约198ms由自有远端路径构成，不是CS2 HUD jitter/loss/Miss。</p><h2>52Mbps仍有一个明确缺口</h2><p>两次使用已修检查的52Mbps窗口，UDP-down无实际包，在原1.2秒内拒绝，ECM没有开启。服务器tap曾249发出/249客户端收到，另一5秒246发出而客户端只33；缺包在安装标签前及撤销后也存在。尚未区分上游、路由器或Windows，不能认定由NSS或52Mbps本身造成，也没有52Mbps的CPU收益验收。</p><h2>两处测试代码故障已处理</h2><ul><li>活动NFT规则counter不是所有规则同瞬时快照。NSS88重读第二帧仍偏差。新观察只允许一次重读，前后counter单调且范围交叉，完整规则与错误tag包/字节0验证保留；缺双向包依然拒绝。30目标RAM案例和32Mbps实际两次边界通过。</li><li>NSS87客户端status文件原子替换在Windows遇EPERM退出。临时EPERM/EBUSY现在延后状态上报，数据连接继续；3本地案例通过，其它IO错误仍退出。没有伪称实际注入故障恢复。</li></ul><h2>恢复、证据和下一步</h2><p>六个实际stage各新checkpoint/SHA/gzip、独立PPID1/45秒守护与完整恢复通过；九个自有端点180秒FW基线恢复、规则0、临时unit/端口关闭、客户端及精确守护退出。原完整终态审核source2.88秒通过，4859/17139实例连续；ECM关闭全零，无事务/stage/state/module，常驻NSS68保持。没有游戏/Steam/UI/HUD、新下载、固件/内核、PBR或五WAN生产配置变化。</p><p>18Mbps旧短窗收益与本次32Mbps收益互相支持。60Mbps预算尚未被压满，因此其限速准确性、拥塞FQ/AQM/ECN、多流公平、DiffServ或autorate替代仍未验收，300Mbps/真人CS2/长期稳定也未证明。上传没有新的NSS QoS tag证明。</p><p>下一步只定位受控UDP回程并补52Mbps同负载闭环，然后一次集中真人CS2验收；不再重复分类器安装、准备检查或新游戏下载。源码与脱敏证据进入私有GitHub，完整原始CT/nonce/端点凭据/checkpoint/模块仍留本地，无上游提交。</p><small>HTML源与实测数据已校验，本轮未验证浏览器渲染。</small></main></html>'''
(w/'outputs/nss92-mainline-report.html').write_text(report,encoding='utf-8');assert '238/238'in report and '<title>NSS92'in report
print(json.dumps({'saved':True,'sourcesAppended':len(hashes),'totalSources':len(manifest['sources']),'stageCases':6,'completeSuccessfulABA':1,'endpointClosures':9,'relativeSoftirqReductionPercent':reduction,'report':'outputs/nss92-mainline-report.html'}))
