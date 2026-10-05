"""Append the actual four-WAN entry and dual physical NSS QoS evidence."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib,subprocess,shutil,importlib.util,html,re
w=Path(__file__).resolve().parents[2];repo=w/'athena-nss-mainline';r=w/'work/nss115'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
spec=importlib.util.spec_from_file_location('collector',w/'work/nss101/collect-lifecycle.py');collector=importlib.util.module_from_spec(spec);spec.loader.exec_module(collector)
cases={n:next(p for p in (w/f'work/nss{n}').glob('controlled-matched-aba-*')if p.is_dir()and(p/'result.json').exists())for n in [110,111,112,113,114]}
final=load(r/'v1-final-health.json');physical=load(r/'physical-final.json')
assert all(final[k]for k in ['passed','originalFullLockedNativeAudit','unrelatedConfigurationMatches','ecmStoppedAndZero','noActiveTransaction','noStaging','noExperimentState','noExperimentalModule'])
assert(final['workerPid'],final['guardianPid'])==(4859,17139)and physical['passed']
# Standard successful/failed-after-staging cases retain the original full audits.
trials=[collector.stage(cases[n].relative_to(w).as_posix())for n in [111,113,114]]
t110=load(cases[110]/'result.json');s110=load(cases[110]/'last-record-private.json');u110=load(cases[110]/'stage-undo-verified.json');cp110=load(cases[110]/'stage-checkpoint-verified.json');det110=load(cases[110]/'stage-detached-private.json');receipt110=load(cases[110]/'stage-receipt-private.json')
assert not t110['passed']and t110['matchedForwardingABACompleted']and all(u110.values())and s110['abaCompleted']and cp110['gzipVerified']and det110['identity']['ppid']==1 and receipt110['rollbackBeforeFirstWrite']
trials.insert(0,{'caseLocalPath':cases[110].relative_to(w).as_posix(),'passed':False,'completeABA':True,'functionalRuntimePassed':load(cases[110]/'functional-runtime-proof.json')['passed'],'metrics':load(cases[110]/'actual-long-metrics.json'),'originalStrictRecoveryRejected':True,'rejection':'Failed, unselected WAN4 procd running/PID changed naturally; original strict epoch rejected','stageUndoVerified':True,'latestDeclaredClosurePassed':load(w/'work/nss110/v2-final-health.json')['passed'],'originalOverallFailureNotReclassified':True,'checkpointDownloadedShaAndGzipVerified':True,'guardianVerifiedBeforeFirstWrite':True,'guardianPpid':1,'independentOwnerSeconds':100,'fixedNativeSessionSeconds':27,'classifierMaximumLeaseSeconds':6,'originalResultSha256':sha((cases[110]/'result.json').read_bytes())})
t112=load(cases[112]/'result.json');assert not t112['passed']and not (cases[112]/'stage-receipt-private.json').exists()and not(cases[112]/'last-record-private.json').exists()
trials.insert(2,{'caseLocalPath':cases[112].relative_to(w).as_posix(),'passed':False,'completeABA':False,'ecmOpened':False,'detachedStageStarted':False,'queueWrites':False,'checkpointCreatedAndVerified':load(cases[112]/'stage-checkpoint-verified.json')['gzipVerified'],'rejection':'Guardian transport exceeded original bound before starting detached stage','separateRecoveryRefusal':'WAN4 wrapper normally execs minieap; old script-only cmdline seal rejected','originalResultSha256':sha((cases[112]/'result.json').read_bytes())})
assert len(trials)==5 and sum(t['passed']for t in trials)==2
up=load(cases[114]/'actual-upstream-proof.json');assert up['passed']and up['bothUplinkLeavesAdvancedNearAcceleratedPhase']
trials[-1]['upstreamProof']=up
assert trials[-2]['error']and 'Unapproved setter'in trials[-2]['error']and not trials[-2]['ecmOpened']
s113=load(cases[113]/'last-record-private.json');trials[-2]['bothPhysicalQueuesConstructedAndRestoredBeforeEcm']=s113['dualPhysicalQueuesReady']and s113['dualPhysicalQueuesRestored']and s113['qosModuleUnloaded']
closures=[]
for n in [110,111,112,113,114]:
 p=Path(load(w/f'work/nss{n}/load-latest-private.json')['dir']);p=w/p
 if n!=110:closures.append(collector.closure(p.relative_to(w).as_posix()));continue
 fresh=load(w/'work/nss110/endpoint-closure-recheck.json');guard=load(p/'guard-result-private.json');client=load(p/'result-private.json');cp=load(p/'firewall-checkpoint-verified.json');receipt=load(p/'firewall-receipt-private.json');detached=load(p/'firewall-detached-private.json')
 assert fresh['passed']and guard['passed']and guard['exactClientOnly']and guard['clientExitedBeforeDeadline']and cp['expirySeconds']==180 and receipt['beforeWriteIndependentGuardianVerified']and detached['detachedIdentityVerified']and detached['onlyNullStandardFds']
 closures.append({'loadLocalPath':p.relative_to(w).as_posix(),'temporaryFirewallRulesRemaining':0,'canonicalFirewallBaselineRestored':True,'ownedUnitInactiveMainPidZeroPortsClosed':True,'clientExited':True,'clientGuardPassed':True,'independentFirewallExpirySeconds':180,'independentClientDeadlineSeconds':210,'endpointGuardianVerifiedBeforeWrite':True,'clientRunSeconds':client['seconds'],'clientErrors':client.get('errors',[]),'firstTwoSshClosureTimeoutsRetained':True,'separateReadOnlyClosureAfterOsDeadlinePassed':True})
q112=load(w/'work/nss112/entry-qualified.json');q113=load(w/'work/nss113/entry-qualified.json');q114=load(w/'work/nss114/entry-qualified.json');native=load(w/'work/nss112/qos-native-qualification.json');normalizer=load(w/'work/nss114/normalizer-qualification.json')
assert len(q112['checks'])==30 and len(native['checks'])==20 and len(q113['checks'])==21 and len(normalizer['checks'])==27
assert q112['payloadBytes']==73011 and q114['payloadBytes']==73293 and q114['maximumStagedBytes']==73728
for n in [111,113,114]:
 t=next(x for x in trials if x['caseLocalPath']==cases[n].relative_to(w).as_posix())
 assert t['sourceInputsCurrentAndFrozenMatch']and t['baseline']['configurationMatches']
# Freeze new private artifacts. Existing per-case exact input copies remain the
# authority; avoid duplicating those large historic prefix trees here.
freeze=r/'proof-v1/private-inputs';freeze.mkdir(parents=True,exist_ok=False);private_hashes={}
for n in range(110,116):
 for src in sorted((w/f'work/nss{n}').rglob('*')):
  if not src.is_file()or any(x in src.parts for x in ['proof-v1','frozen','frozen-qualified-inputs','__pycache__']):continue
  rel=src.relative_to(w);dst=freeze/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);private_hashes[rel.as_posix()]=sha(src.read_bytes());assert sha(dst.read_bytes())==private_hashes[rel.as_posix()]
dump(r/'private-input-freeze-index.json',private_hashes)
old=(repo/'evidence/current-runtime.json').read_bytes();assert load(repo/'evidence/current-runtime.json')['round']=='NSS109';assert subprocess.check_output(['git','show','HEAD:evidence/current-runtime.json'],cwd=repo)==old
archive=repo/'evidence/nss109-runtime.json';assert not archive.exists();archive.write_bytes(old)
mp=repo/'source-manifest.json';manifest=load(mp);assert len(manifest['sources'])==1187
prefix=sha(json.dumps(manifest['sources'],sort_keys=True,separators=(',',':')).encode())
common=['controlled-session.mjs','current-audit-diagnostic.mjs','session-binding.mjs','declared-baseline.mjs','service-epoch.mjs','match-controlled.mjs','read-controlled.mjs','run.mjs','module-stage.mjs']
allowed={110:[x for x in common if x!='service-epoch.mjs']+['prepare.py','qualify.mjs','health.mjs','closure-recheck.mjs','prepare-analysis.py','analyze-long.py','calibrate-clock.mjs'],111:common+['prepare.py','qualify.mjs','failed-wan-owner.lua','prepare-analysis.py','analyze-long.py','calibrate-clock.mjs'],112:common+['prepare-qos.py','prepare-entry.py','qualify.mjs','qos-physical.lua','qos-lifecycle-fixtures.lua','payload.mjs','pack-lua.mjs','uplink-tag-plan.mjs','parse-ecm-any-wan.mjs','fast-path.lua','module-stage-guardian.lua','measure-payload.mjs','read-uplink.mjs','inspect-auth-process.lua','inspect-auth-process.mjs','read-auth-wrapper.mjs'],113:common+['prepare.py','qualify.mjs','qos-physical.lua','payload.mjs','pack-lua.mjs','pack-guardian.mjs','compact-default-queues.mjs','preview-plan.mjs','failed-wan-owner.lua','uplink-tag-plan.mjs','parse-ecm-any-wan.mjs','fast-path.lua','module-stage-guardian.lua'],114:common+['prepare.py','qualify.mjs','qualify-normalizer.lua','tag-normalizer.lua','failed-wan-owner.lua','qos-physical.lua','payload.mjs','pack-lua.mjs','pack-guardian.mjs','compact-default-queues.mjs','uplink-tag-plan.mjs','parse-ecm-any-wan.mjs','fast-path.lua','module-stage-guardian.lua','prepare-analysis.py','analyze-long.py','calibrate-clock.mjs','prove-upstream.py'],115:['prepare-health.py','health.mjs','read-final-physical.mjs','keep-awake.ps1','save-evidence.py']}
sources={}
for n,names in allowed.items():
 assert len(names)==len(set(names))
 for name in names:
  src=w/f'work/nss{n}/{name}';rel=src.relative_to(w).as_posix();dst=repo/'code'/rel;assert not dst.exists();dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);digest=sha(src.read_bytes());assert sha(dst.read_bytes())==digest;sources[rel]=digest;manifest['sources'].append({'path':'code/'+rel,'workspaceSource':rel,'sha256':digest,'bytes':src.stat().st_size,'role':'scoped-four-WAN-admission-and-dual-physical-QoS'})
manifest['lastAppendExport']='NSS115';manifest['generatedAt']=datetime.now(timezone.utc).isoformat();dump(mp,manifest)
main={'round':'NSS115','coveredRounds':list(range(110,116)),'observedAt':final['observedAt'],'actualSingleWanStageCases':4,'preStageTransportRefusals':1,'completeFunctionalABA':3,'overallSuccessfulABA':2,'newDualPhysicalQosPassed':True,'dualPhysicalQosHardwareRound':114,'dualPhysicalQosOneWan':2,'actualAcceleratedCount':[0,2,0],'newQualifiedEntry':'work/nss114/controlled-session.mjs','newQualifiedEntryBoundInputs':793,'onlyOneTcpUdpPairAtATime':True,'physicalLan4DownlinkQosProven':True,'physicalWanUplinkLeafRoutingProven':True,'uplinkCongestionLatencyAccepted':False,'authEapolContinuityWhileQueueActiveAccepted':False,'newMatchedCpuComparisonAccepted':False,'earlier32And48CpuEvidenceRetained':True,'humanCs2Acceptance':False,'highLoad300MbpsAcceptance':False,'fullCakeReplacementAccepted':False,'residentClassifierChanged':False,'residentPublicationUpTagStillZero':True,'controlledUpTagDerivedFromActualBulkRtClass':True,'nssPermanentlyEnabled':False,'failedUnselectedWan4ProcessLifecycleScoped':True,'unknownRoutingChangesAllowed':False,'wan4AuthenticationRecovered':False,'allTemporaryEndpointsClosed':5,'uiOperated':False,'newSteamDownloadsStarted':False,'upstreamSubmitted':False,'originalFailuresPreserved':True,'nightContinuationUntilBeijing':'2026-10-06T10:00:00+08:00','reportVerification':{'sourceValidated':True,'browserRendered':False}}
source_proof={'round':'NSS115','sources':len(sources),'sourceHashes':sources,'historicPrefixSources':1187,'historicPrefixCanonicalSha256':prefix,'privateOwnedHostBootstrapExcluded':True,'privateFrozenArtifactFiles':len(private_hashes),'actualCaseSourceInputsAndHistoricFrozenTreesRetained':True,'notAdditionalProductionAdmission':True}
preparation={'qos20TargetRamCases':native,'qosEntry30Checks':q112['checks'],'planAndOwner21Checks':q113['checks'],'normalizer27TargetRamChecks':normalizer,'limitsUnchanged':{'execBytes':9000,'transportRawBytes':65536,'stagedCodeBytes':73728,'classifierLeaseSeconds':6,'nativeSessionSeconds':27,'independentOwnerSeconds':100},'payloadCapFirstRefusal':load(w/'work/nss112/payload-cap-first-rejection.json'),'singleMessageRamTransportRefusal':load(w/'work/nss112/transport-preparation-refused.json'),'threeTestHarnessErrorsRetained':True,'permanentSourceBytesNotChanged':True}
runtime={'round':'NSS115','checkedAt':physical['observedAt'],'deploymentReference':'work/nss68/deployment-latest.json','classifierConfigSha256':final['configSha256'],'workerPid':4859,'guardianPid':17139,'nssPermanentlyEnabled':False,'residentClassifierChangedThisTurn':False,'authRepairStillCommitted':True,'qualifiedExperimentalEntry':main['newQualifiedEntry'],'qualifiedExperimentalEntryBoundInputs':793,'currentNssAdmissionMustBeRefreshedBeforeWrite':True,'dualPhysicalQosHardwarePassed':True,'actualHardwareRound':114,'physicalWanUplinkLeafRoutingProven':True,'uplinkCongestionLatencyAccepted':False,'permanentClassifierPublicationUpTagZeroRetained':True,'realHumanGameAcceptance':False,'newMatchedCpuComparisonAccepted':False,'audit':final,'physicalRootRestoreAudit':physical,'historical109RuntimePreservedSha256':sha(old),'nightContinuationUntilBeijing':main['nightContinuationUntilBeijing']}
for name,value in {'mainline':main,'trials':trials,'uplink-proof':up,'preparation':preparation,'endpoint-closure':closures,'final-audit':final,'physical-final':physical,'source-proof':source_proof}.items():dump(repo/f'evidence/nss115-{name}.json',value)
dump(repo/'evidence/current-runtime.json',runtime)
when=datetime.fromisoformat(final['observedAt'].replace('Z','+00:00')).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
summary=f'''更新：{when}，北京时间。最新NSS115整理，实际双向硬件测试NSS114。常驻68/config581b5d46…c791d7仍4859/17139；实验全部撤销。

**首次完整证明：同一真实单WAN TCP＋UDP经ECM进入物理LAN4下行bulk/RT、物理wan上行bulk/RT四个NSS FQ-CoDel leaf。三段各20秒，ECM0→2→0，完整mark/NAT/WAN affinity正确、七次续租、两物理根及模块精确恢复。**

见 [汇总](../evidence/nss115-mainline.json)、[实际各轮](../evidence/nss115-trials.json)、[上行实测](../evidence/nss115-uplink-proof.json)、[端点关闭](../evidence/nss115-endpoint-closure.json)、[终态](../evidence/nss115-final-audit.json)、[物理队列恢复](../evidence/nss115-physical-final.json)。

- NSS110按声明auth修复与精确四WAN故障切换基线进入，WAN5完整功能A/B/A2；原整体恢复因未选中故障WAN4自然PID/running变化拒绝，失败仍保留。NSS111只允许该进程变化，其它路由、保护文件、服务仍严格相同；WAN5整体通过，实际此轮未触发新进程例外。111 TCP25.717/26.998/27.004Mbps，softirq9.706/0.876/11.881%，UDP840/840、909/909、835/835；为本轮观察，不新增完整高负载CPU或真人验收。
- NSS112新双向队列方案20目标RAM＋格式检查通过，完整包75489B先拒绝；仅删除单行源格式/注释后73011B，原73728B上限不变。一次现场guardian传输大小拒绝，checkpoint已核验但未启动stage/改队列。WAN4 procd脚本会正常exec到minieap，旧脚本argv假设产生独立拒绝；只读观察和受保护wrapper源码确认，未改认证。
- NSS113以原判定实际使用的队列字段缩小plan、保留counter原记录，原9000B传输不变；正常脚本或精确minieap argv/执行文件/PPID/start均校验，绝不输出账户参数。两物理树实际构建且恢复；旧normalizer仅允许下行标签，ECM前拒绝“Unapproved setter”，失败保持。113实际原完整恢复通过，并观察到未选中WAN4进程变化；这不等于WAN4认证恢复。
- NSS114只补四个明确class/direction writer的标签白名单和8e native alias，27目标RAM反例通过。单WAN2三段实际TCP26.378/26.998/25.884Mbps，softirq9.859/5.421/15.644%，time_squeeze全0；UDP868/868、933/933、866/866。下行bulk新增204drop、RT0；异步近B上行bulk/RT分别+36842/+923包，均0drop/backlog0。实际ECM TCP/UDP上下行tag、CT mark/NAT/WAN2正确，默认未知flow拒绝。不同吞吐和软件段差异不算新CPU收益，echo不是真人CS2。
- 两物理树各30Mbps组、bulk29/RT1、共同ceil30、默认950fallback。上行数据主要TCP ACK与小UDP，尚未证明上行拥塞限速/实时延迟、EAPOL在高负载队列下连续性或完整CAKE替代。物理wan被五MacVLAN共用，仅一对flow获加速；不是每个private WAN直接挂NSS qdisc，也不声称其它流完全没有经过新增physical root。
- 常驻发布upTag仍0；本次受控映射依据实际BULK/RT class在ECM学习前生成8e上行tag，未改永久分类器。新114入口793项必须每次重新读当前实例。既有32/48Mbps收益保留，真人/300Mbps/多WAN未验收；不要用完成的工程探针代替用户体验。
- 四个stage各checkpoint下载/SHA/gzip与控制连接外100秒owner，均精确清理；五个端点FW180/客户端210秒关闭。110两次SSH关闭查询超时原记录保留，独立只读复核最终基线/端口关闭。115原完整终态source{final['queryAge']:.2f}、ECM关闭全零、无事务/stage/state/模块；两物理根原mq＋四fq_codel确认。WAN4仍down，现有自动四路PBR不改。旧109 runtime原字节保存，完整私有CT/配置/nonce/检查点/凭据不进Git。
- 夜间继续到今天10:00；09:50停止新生产实验、整理终态。保持用户Esc后的UI停用，不新下载、不启动游戏、不提交上游。下一步只补单WAN上行压力/RT及自动映射缺口，之后一次集中真人验收；多WAN、共享预算、Wi-Fi、autorate和ECN backlog继续后置。
'''
p=repo/'docs/STATE.md';p.write_text('# 当前状态\n\n'+summary+'\n## NSS109历史状态\n\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
plan='''# 下一步：只补单WAN双向QoS缺口

NSS114真实四leaf路径已证明，见 [STATE](STATE.md)。无需重复CAKE调参或重新安装68分类器。

1. 继续114/793入口，每次新的flow/producer/checkpoint与独立撤销。只允许健康非WAN4、精确一TCP一UDP，学习前双向tag、完整ct mark/NAT/WAN affinity和持续六秒来源不变。
2. 先保持30/29/1队列与20秒三段期限，用同一自有SSH TCP连接的上行负载确认实际上传和RT路径。服务器确认收到的字节才能作为上传吞吐；客户端提交字节不等于交付。再根据实际容量一次只调整必要的上行受控预算，使拥塞能被NSS而非未知上游独占控制；不同时改方向与预算。
3. 当前物理wan共用五MacVLAN，default950进入该树的EAPOL/其它软件流需要有范围明确的连续性观察。不能把一对flow成功称所有业务保证；不改认证、PBR或学校策略。
4. 常驻upTag0尚未改；受控映射依真实class、明确leaf表和getter已成功。先决定消费者映射的最小长期形式；不要为了发布字段重装整套或长期开放未知flow。已加速改类仍精确撤销/重学。
5. 主线工程具备后，只集中一次真人CS2＋正常下载HUD/体感验收；echo不是CS2。第二WAN、共享预算、Wi-Fi、autorate、ECN/bridge/HTB backlog保持后置。
6. 夜间接续到10:00，09:50后不新开生产测试，完成独立恢复/端点/原完整审核与证据推送后暂停本夜接续；不需要用户逐步确认。

## NSS109历史计划

'''
p=repo/'docs/PLAN.md';p.write_text(plan+p.read_text(encoding='utf-8'),encoding='utf-8')
for file,title in [('EXPERIMENT_LOG.md',f'NSS110–115 · {when} · 四路准入与真实双向NSS leaf'),('ARTIFACT_INDEX.md','当前NSS115')]:
 p=repo/'docs'/file;v=p.read_text(encoding='utf-8')
 if file=='EXPERIMENT_LOG.md':head,tail=v.split('\n',1);v=head+'\n\n## '+title+'\n\n'+summary+tail
 else:v='# '+title+'\n\n[汇总](../evidence/nss115-mainline.json) · [五轮](../evidence/nss115-trials.json) · [上行](../evidence/nss115-uplink-proof.json) · [终态](../evidence/nss115-final-audit.json) · [源码](../evidence/nss115-source-proof.json) · [历史109 runtime](../evidence/nss109-runtime.json)。本地报告 outputs/nss115-mainline-report.html。\n\n'+v
 p.write_text(v,encoding='utf-8')
p=repo/'AGENTS.md';head,tail=p.read_text(encoding='utf-8').split('\n',1);p.write_text(head+'\n\n最新NSS115整理/实际114：单WAN2真实TCP+UDP、20秒A/B/A2/ECM0→2→0，物理LAN4下行8f05/06与wan上行8e05/06四leaf命中，mark/NAT/affinity/7续租/两根及模块恢复通过；TCP26.378/26.998/25.884，UDP868/868、933/933、866/866，下bulkdrop204/RT0，上bulk/RT+36842/+923包/0drop。不是真人/300Mbps/完整CAKE或上行拥塞验收；常驻upTag0不变、受控由真实class映射。114新入口793项，9000/65536/73728传输上限、6秒来源、27native/100owner不放宽。110原恢复拒绝保留，111整体通过；112传输写前拒绝/未stage，113两树建成却旧normalizer拒绝、ECM未开，全部原义保持。113只修procd脚本正常exec minieap的精确身份审核，未改认证；失败未选中WAN4PID变化单独允许，其它配置/路由/服务严格。四stage与五端点均清理，115终态4859/17139/source1.70、ECM关闭全零无残留，两物理默认根恢复，WAN4仍down四路自动PBR不改，旧109 runtime逐字节保留。下一步上行压力/RT与最小自动映射，之后一次集中真人；不扩WAN/共享预算/Wi-Fi/autorate、不重装/新下载/UI。夜间至10:00，09:50不新生产实验；STATE为准。\n\n'+tail,encoding='utf-8')
ps=trials[-1]['metrics']['phases'];rows=''.join(f'<tr><td>{x["phase"]}</td><td>{x["whole"]["clientTcpMbps"]:.3f}</td><td>{x["whole"]["softirqPercent"]:.3f}%</td><td>{x["whole"]["timeSqueezeDelta"]}</td><td>{x["whole"]["udp"]["received"]}/{x["whole"]["udp"]["sent"]}</td></tr>'for x in ps)
report=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NSS115 双向NSS QoS</title><style>body{{margin:0;background:#f4f4ee;color:#24352d;font:16px/1.8 "Microsoft YaHei",sans-serif}}main{{max-width:1000px;margin:auto;padding:32px 24px}}section{{background:#fff;padding:22px;border:1px solid #dbe1d8;border-radius:10px;margin:24px 0}}h1{{font-size:30px}}h2{{font-size:23px}}table{{width:100%;border-collapse:collapse;font-variant-numeric:tabular-nums}}th,td{{text-align:left;padding:8px;border-bottom:1px solid #ddd}}small{{color:#617166}}a{{color:#326649}}</style><main><small>ATHENA AX6600 · {when} 北京时间</small><h1>真实单WAN双向bulk/RT四leaf已打通</h1><p>ECM0→2→0，物理LAN4下行与物理wan上行分别进入NSS bulk、RT FQ-CoDel。三段各20秒，所有实验精确撤销。</p><section><h2>实际NSS114</h2><table><tr><th>阶段</th><th>TCP Mbps</th><th>softirq</th><th>squeeze</th><th>UDP收/发</th></tr>{rows}</table><p>七次续租、CT mark/NAT/WAN2正确；上下行tag均由实际ECM状态验证。近B异步上行bulk/RT新增36842/923包，均零drop；下行bulk drop204、RT零drop。上行主要ACK和小UDP，尚未形成上行拥塞。</p><p>不同吞吐与软件段差异使本轮不新增严格CPU收益结论。UDP echo不是CS2 jitter/loss/Miss；没有操作游戏或下载。</p></section><section><h2>为什么前两次双向尝试失败</h2><p>112在原传输大小检查前拒绝，未启动stage。113队列实际建成/恢复，但旧标签校验只允许下行值，ECM开放前拒绝。114仅补明确四方向writer白名单与native alias，27个目标RAM案例后才现场验证。未放宽9000/65536/73728字节或任何来源/回滚期限。</p><p>未选中故障WAN4的既有进程变化单独处理：受保护脚本正常exec到minieap，现核对精确argv、执行文件、PPID、start和procd，未改认证。WAN4仍down，学校策略和自动四路PBR保持。</p></section><section><h2>当前边界与夜间下一步</h2><p>常驻68/config不变、发布upTag仍0；受控mapper基于实际class生成上行tag。物理wan共用五MacVLAN，因此默认950fallback和EAPOL/其它软件流的连续性仍需明确验证，不能声称五路全部QoS已解决。两个受控组都是30/29/1，尚未接autorate或完整DiffServ4，不要求host fairness。</p><p>下一步只测试自有同一TCP的上行压力与RT、然后最小自动映射。真人CS2留最后集中一次；不扩WAN/共享预算/Wi-Fi/autorate，不新下载或操作桌面。夜间继续到10:00，09:50停止新生产实验并收尾。</p><p>终态source{final['queryAge']:.2f}，ECM关闭全零、无事务/stage/state/模块，两物理根原mq+四fq_codel恢复，五个端点独立关闭。完整私有输入留本地，旧109 runtime字节不变。</p><a href="https://github.com/ZyPulse-zy/athena-nss-mainline/blob/main/docs/STATE.md">仓库当前状态</a><p><small>报告源码核验，未作浏览器渲染验收；失败、模拟和硬件证据分开。</small></p></section></main></html>'''
out=w/'outputs/nss115-mainline-report.html';assert not out.exists();out.write_text(report,encoding='utf-8')
dump(r/'export-receipt.json',{'passed':True,'newSources':len(sources),'totalSources':len(manifest['sources']),'privateFrozenArtifacts':len(private_hashes),'actualDualQosPassed':True,'endpointsClosed':len(closures),'old109RuntimePreservedSha256':sha(old),'browserRendered':False})
print(json.dumps({'exported':True,'newSources':len(sources),'totalSources':len(manifest['sources']),'privateFrozenArtifacts':len(private_hashes),'hardwareFourLeavesPassed':True}))
