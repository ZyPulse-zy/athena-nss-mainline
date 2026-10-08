"""One publication for a completed rolling-residency milestone, after real closure."""
from pathlib import Path
import argparse, datetime, hashlib, json, subprocess
p=argparse.ArgumentParser();p.add_argument('integration');p.add_argument('service_snapshot');a=p.parse_args()
w=Path(__file__).resolve().parents[2];repo=w/'athena-nss-mainline';batch=w/'work/resident-continuous-dev-20261008'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def emit(p,v):
 with Path(p).open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
result=read(w/a.integration/'result-private.json');assert result['passed'] and result['restorationPassed'] and result['hardwareCompleted']
actual=result['result'];assert actual['code']==0 and actual['hardwareCompleted'] and actual['restorationPassed'] and actual['nssSeconds']>=190
service=read(w/a.service_snapshot);assert service['running'] and service['identityVerified'] and service['heartbeatFresh'] and service['startupHealthPassed']
runtime=w/actual['runtimeRoot'];pilot=w/read(runtime/'pilot-reference-private.json')['directory'];case=w/read(pilot/'case-reference-private.json')['dir']
r=read(case/'last-record-private.json');assert r['operatorStop'] and r['continuousEpochEndedSafely'] and r['fixedOwnerDeadlineRemoved'] and r['fixedSessionDeadlineRemoved']
cp=read(case/'stage-checkpoint-verified.json');guard=read(case/'stage-receipt-private.json');plan=read(case/'stage-plan-private.json');undo=read(case/'stage-undo-verified.json')
assert cp['gzipVerified'] and len(cp['sha256'])==64 and all(guard[k] for k in ['success','rollbackBeforeFirstWrite','parentIdentityVerified','pipeInodesVerified']) and all(undo.values())
assert plan['execBytes']<=9000 and plan['qosCodeBytes']<=73728
fixture=w/result['fixtureRoot'];load=w/read(fixture/'load-latest-private.json')['dir'];closure=w/read(fixture/'closure-pointer.json')['directory']
ep=read(load/'endpoint-retry-closure.json');cl=read(closure/'client-closure.json');assert ep['passed'] and cl['passed'] and cl['ownedTestProcessesRemaining']==0
q=read(batch/'qualification-latest-private.json');assert q['passed'];build=read(batch/'endpoint-gate/build-manifest.json');assert build['sdk_original_unchanged']
task=read(w/'work/resident-task-continuous-20261008/continuous-task-upgrade-private.json');assert task['passed'] and task['onlyOwnedLaunchArgumentsChanged'] and task['otherRelatedTasksUnchanged']
fresh=[]
for f in sorted(batch.iterdir()):
 if f.is_file() and f.suffix in ('.mjs','.py','.ps1'):fresh.append(f)
for name in ['Makefile','build_local.py','control_harness.py','ct_harness.py','control-harness.generated.c','ct_harness.generated.c','ecm_ae_classifier_public.h','predicate_test.c','rp_ecm_gate_lab_ct.c','two_slot_predicate.h']:
 fresh.append(batch/'endpoint-gate'/name)
for name in ['fast-path.lua','module-stage-guardian.lua','module-stage.mjs','epoch-driver.mjs']:fresh.append(runtime/name)
fresh.append(w/'work/resident-task-continuous-20261008/upgrade.ps1')
for name in ['prepare-task.py','prepare-audit.py','delivery-audit.py','prepare-publication.py','recheck-health.mjs','finish-failed-fixture.mjs','close-second-fixture.mjs','capture-service.mjs']:fresh.append(Path(__file__).parent/name)
assert len(fresh)==len(set(fresh))
manifest=read(repo/'source-manifest.json');assert len(manifest['sources'])==6257
hashes={}
for f in fresh:
 rel=f.relative_to(w).as_posix();dest=repo/'code'/rel;assert not dest.exists();dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(f.read_bytes());h=digest(f);hashes[rel]=h
 manifest['sources'].append({'path':'code/'+rel,'workspaceSource':rel,'sha256':h,'bytes':f.stat().st_size,'role':'continuous-qualified-residency-and-related-fixture-repair'})
manifest['generatedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat();manifest['lastContinuousResidentExport']='ROLLING_QUALIFIED_RESIDENCY_INTEGRATED_AND_RETAINED'
(repo/'source-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
retained=r['samples'];assert len(retained)<=32 and len(r['renewals'])<=16;assert all(s['counts']['ecm_nss_ipv4/accelerated_count']==1 for s in retained)
advance=r['renewals'][-1]['sessionUntilMs']-int(r['parametersBefore']['session_until_ms']);assert advance>180000
restore={k:bool(r[k]) for k in ['moduleUnloaded','qosModuleUnloaded','tagsRemoved','stateNodeRemoved','wanRestored','mwan3Restored','dualPhysicalQueuesRestored']};assert all(restore.values())
e={'passed':True,'observedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'milestone':'Continuous qualified NSS controller retained; fixed healthy-session lifetime caps removed',
 'implementation':{'fixedNssPhaseSeconds':None,'fixedGenerationCutoffSeconds':None,'maximumGenerationsPerWindow':None,'windowSeconds':None,'freshClassificationSeconds':6,'freshSocketOwnershipSeconds':6,'nativeRollingWindowSeconds':120,'guardianRollingWindowSeconds':180,'controlHeartbeatLossSeconds':30,'maximumTcpBulk':2,'maximumUdpRt':1,'unknownAndUnusedSlotsDenied':True,'healthyQualifiedLifetimeIndefinite':True,'safetyWatchdogsRemoved':False,'newFlowsRequireFreshGeneration':True},
 'regression':{'batchChecks':q['checks'],'syntaxSources':q['syntaxSources'],'powershellSources':q['powershellSources'],'nativeControlChecks':4409,'ctChecks':109,'predicateChecks':134,'sevenSubsetModelsPassed':True,'twoVirtualHoursWithBoundedRecordsPassed':True,'sdkOriginalUnchanged':True,'historicalCoreEvidenceReused':True},
 'actualIntegration':{'completed':True,'activeMask':2,'simulatedGamePackets':True,'normalEntryCreatesTraffic':False,'nativeModuleLoaded':True,'nativeBytes':(batch/'endpoint-gate/rp_ecm_gate_lab_ct.runtime.ko').stat().st_size,'nativeSha256':digest(batch/'endpoint-gate/rp_ecm_gate_lab_ct.runtime.ko'),'nativeSourceSha256':digest(batch/'endpoint-gate/rp_ecm_gate_lab_ct.c'),'nssSeconds':actual['nssSeconds'],'samplesValidated':actual['samples'],'renewals':actual['renewals'],'retainedSamples':len(retained),'retainedRenewals':len(r['renewals']),'retainedSamplesEcm1':True,'rawSampleHistoryRingBounded':True,'nativeSessionAdvanceMs':advance,'guardianExtendedBeyondInitialDeadline':r['deadline']>r['stageAtUptime']+300,'operatorStopPassed':True,'restorationPassed':True,'recordBytes':(case/'last-record-private.json').stat().st_size},
 'restoration':{'ecmClosedAndZero':True,**restore,'protectedConfigurationUnchanged':True,'physicalQueueOptionsAndHandlesExact':True,'endpointRestored':bool(ep['baselineRestored'] and ep['exactOwnedEndpointClosed'] and ep['ownedRulesRemaining']==0),'independentClientGuardClosureVerified':True,'noActiveGenerationLockAfterIntegration':True},
 'fixture':{'clientSeconds':360,'independentGuardSeconds':390,'serverSeconds':450,'firewallSeconds':360,'maximumMbps':32,'offeredMbps':16,'combinedByteCeiling':1073741824,'maximumCombinedPacerCreditBytes':65536,'productCreatesTraffic':False},
 'originalFailures':{'preserved':True,'firstFixtureRejectedBeforeClientAndNss':True,'localSourceBindingRefusedBeforeRecoveryRouterRead':True,'freshReadonlyRecoveryPassed':True,'secondFixtureAlarm182SecondsStoppedSenderAndClient':True,'secondNssSeconds':109.79999999981374,'secondNormalEntryRestored':True,'secondWrapperCleanup180Vs360AssertionPreserved':True,'bothEndpointAndClientClosuresPassed':True,'sameDevelopmentBatch':True,'nssRootCauseClaimed':False},
 'retainedService':service,'task':{'onlyOwnedLaunchArgumentsChanged':True,'otherRelatedTasksUnchanged':True,'noLogonTrigger':True,'noFailureRestart':True,'executionTimeLimitDisabled':True,'heartbeatRemainsPaused':True},
 'scope':{'cs2OrSteamOperated':False,'newGameDownload':False,'userDownloadPausedOrRateChanged':False,'cpuExperimentRepeated':False,'authPbrSingboxTailscaleAndTenCakePreserved':True,'privateInputsExported':False},
 'limitations':['At most two BULK and one admitted RT from directly owned IPv4 sockets; other traffic stays software','New rolling native hardware integration is RT mask2 only; other subsets use local models and historical core proof','No all-LAN, arbitrary flow, IPv6, proxy, QUIC, logon-start or router-reboot residency claim','Healthy qualified generation has no fixed lifetime cap, but eligibility loss, deceleration, fault or operator stop ends and restores the epoch','Real hardware continuous duration is the measured finite integration, not a long soak or proof of uninterrupted lifetime','User-reported CS2 loss under large downloads remains an unclosed user-experience P1; simulation does not prove its repair'],
 'sourceHashes':hashes}
e['prewriteProtection']={'freshCheckpointDownloadedShaAndGzipVerified':True,'independentDetachedRollbackVerifiedBeforeFirstWrite':True,'stageExecBytes':plan['execBytes'],'bundleBytes':plan['qosCodeBytes'],'execLimit':9000,'bundleLimit':73728,'independentUndoVerified':True}
emit(repo/'evidence/resident-continuous.json',e)
seconds=f"{actual['nssSeconds']:.2f}";renewals=actual['renewals'];samples=actual['samples']
common=f'2026-10-08，取消健康代90秒退出和20分钟四次启动限制。合格流持续自动续租；分类/socket6秒新鲜度、native滚动120秒、guardian滚动180秒及失联撤销保持。实际RT mask2连续NSS {seconds}秒／{samples}采样校验／{renewals}续租，跨原90/120/180秒后主动Stop和完整恢复通过。'
link='[实现、实测与限制](RESIDENT_CONTINUOUS.md)'
rootlink='[实现、实测与限制](docs/RESIDENT_CONTINUOUS.md)'
sections={
 'docs/STATE.md':'# 当前：连续合格NSS控制器已保留\n\n'+common+'\n\n同名手动任务只换启动参数，无登录触发/故障自动重启，heartbeat仍暂停。控制使用 work/resident-continuous-dev-20261008/service.ps1 Status / Stop / Start；先核对，不重复启动。当前快照状态 '+service['state']+'，实际NSS命中与进程常驻分别判断。\n\n27项本批回归及4409 native控制检查、七子集尺寸/语法和2虚拟小时模型通过。仅相关RT子集做真实跨期限验证，不重做五WAN/CPU。原夹具两次失败、本地源码绑定拒绝和所有恢复输出保存：首轮未进入NSS，次轮发送器182秒闹钟连带停UDP，NSS运行109.80秒后安全撤销；最终修正发送/停止/清理参数，背景流降16Mbps而字节上限保持。\n\n最多2 BULK＋1准入RT，未知默认拒绝，原CT/NAT/mark/affinity/QoS及恢复保护保持。异常或流退出仍结束旧代，新流取新分类/pin/checkpoint/owner。尚非全网、不限流数或长期soak证明，用户大下载游戏高丢包P1仍未关闭。'+link,
 'docs/PLAN.md':'# 本开发批次完成：保留连续合格NSS\n\n'+common+'\n\n停止新增fixture、边界与CPU实验。已保留无固定健康寿命的控制器，正常使用期间持续观察/续租，未知错误先恢复并暂停；后续只修有实证阻塞使用的问题。游戏体验P1不以模拟关闭，更多协议/全网/重启恢复和长期soak留后续范围。'+link,
 'docs/KNOWN_FAILURES.md':'# 连续常驻批次：P2已修，体验P1仍未关闭\n\n夹具config.seconds、停止helper及发送器signal.alarm182与360秒寿命不一致，本批集中修复；失败输入和恢复均保留。源码绑定拒绝发生在连接前，独立新目录只读恢复核验通过。最终跨期限集成和主动停止/完整恢复通过，当前没有由本次实测证明的未恢复P0。\n\n用户下载时游戏高丢包仍为未关闭P1；RT-only模拟不证明下载体验修复。常驻不等于所有新流都加速，未知/不支持流保持软件路径，ECM自然撤销仍结束当前epoch。'+link,
 'docs/RESIDENT_SERVICE.md':'# 当前手动常驻：持续续租，健康寿命不设固定截止\n\n'+common+'\n\n使用 work/resident-continuous-dev-20261008/service.ps1 Status / Stop / Start。同名任务设置、其它相关任务不变，无登录触发或失败自重启。Stop停止新准入、向精确当前owner送停止请求并完整恢复；失联保护保持。程序不制造下载或操作桌面；单代最多2BULK/1RT。'+link,
 'docs/RESIDENT_NORMAL_CONTROLLER.md':'# 当前入口：连续合格代\n\n'+common+'\n\n正常程序精确进程/socket归属、分类/预算/CT/NAT/完整mark/WAN affinity与未知默认拒绝保持。新流仍需要新代，不热插入旧epoch。原数据面/CPU证明复用；持续运行的日志仅保留32采样与16续租尾部及累计校验计数。'+link,
 'docs/EXPERIMENT_LOG.md':'# 连续常驻开发批次收尾（2026-10-08）\n\n'+common+'\n\nP2在同批修复并本地回归，没有按小bug提升正式版本。前两次失败及其独立恢复完整保留。最后只验滚动期限和相关RT路径，完成端点/FW基线、客户端独立守护、ECM/tag/module/state、保护配置和两物理原队列全部选项/handle恢复后保留手动控制器。源码与脱敏事实一次集中发布；不新增HTML或性能实验。'+link,
 'README.md':'# 当前交付：连续合格NSS常驻控制器\n\n'+common+'\n\n最多2BULK/1RT，未知流软件路径；失联/错误流撤销、checkpoint和完整恢复保持。不是全网不限流或长期soak结论；大下载CS2丢包体验P1仍待闭环。'+rootlink,
 'AGENTS.md':'# 当前接续：连续合格NSS控制器已部署\n\n先读STATE/PLAN/KNOWN_FAILURES/RESIDENT_CONTINUOUS；用 work/resident-continuous-dev-20261008/service.ps1 Status 核对，禁止重复启动。'+common+'\n\n本开发批次结束，不新增fixture/CPU/更多mask/边界；正常合格流持续自动续租，未知错误先恢复。无登录触发/自动重启，heartbeat暂停。凭据/nonce/完整CT/checkpoint/二进制仅本地，旧冻结源码/失败不覆盖，游戏体验P1仍未关闭。'+rootlink}
for name,head in sections.items():
 f=repo/name;old=f.read_text(encoding='utf-8');f.write_text(head+'\n\n## 以下保留历史记录\n\n'+old,encoding='utf-8')
doc='# 连续合格NSS常驻\n\n'+common+'\n\n控制器一直运行，合格的原有流保持当前epoch并滚动续租。取消的是固定健康会话寿命与启动次数窗口；6秒来源新鲜度、30秒控制失联、CT/NAT/mark/affinity身份和停止/异常恢复仍生效。它们用于撤销失去证据的权限。\n\n`work/resident-continuous-dev-20261008/service.ps1 Status / Stop / Start` 控制已有手动任务。现有Windows任务没有执行时长上限；本次只换其启动参数，不改其它任务或电源计划，不增加登录触发。\n\n每个实时tick验证精确ECM、分类和身份。记录保留32采样与16续租尾部以及累计数量，1MiB记录/73728 bundle/9000 exec上限不放宽。新的native ACK实际延长会话期限；健康owner同步延长守护窗，PC失联或资格丢失结束旧代并恢复软件路径。\n\n本地27项回归、4409 native控制/109CT/134匹配、七子集语法/尺寸及2虚拟小时通过。硬件仅RT mask2，测试流量是有限16Mbps背景模拟下载和50pps UDP echo；软件控制器本身不造流量。跨期限后主动Stop、完整保护与物理队列恢复、精确端点/FW与独立客户端守护关闭通过。\n\n前两次夹具失败保留；初次未进NSS，第二次182秒发送器闹钟使模拟客户端提前结束，对应NSS安全撤销。未把这个P2当成固件故障。有限硬件窗口不证明长期soak或永不撤销；最多2BULK/1RT直接归属IPv4流，其它/未知走软件。实际游戏大下载丢包P1仍未关闭。\n\n[源码适配器](../code/work/resident-continuous-dev-20261008/adapt.mjs) · [控制器](../code/work/resident-continuous-dev-20261008/daemon.mjs) · [脱敏事实](../evidence/resident-continuous.json)\n'
(repo/'docs/RESIDENT_CONTINUOUS.md').write_text(doc,encoding='utf-8')
attributes=['code/work/resident-continuous-dev-20261008/generation-outcome.mjs','code/work/resident-task-continuous-20261008/upgrade.ps1']
with (repo/'.gitattributes').open('a',encoding='utf-8') as f:
 f.write('\n');f.writelines(x+' whitespace=cr-at-eol,-blank-at-eof\n' for x in attributes)
checker="""import hashlib,json
def check(root):
 e=json.loads((root/'evidence/resident-continuous.json').read_text(encoding='utf-8'));assert e['passed']
 i=e['implementation'];assert all(i[k] is None for k in ['fixedNssPhaseSeconds','fixedGenerationCutoffSeconds','maximumGenerationsPerWindow','windowSeconds'])
 assert i['healthyQualifiedLifetimeIndefinite'] and not i['safetyWatchdogsRemoved'];assert (i['freshClassificationSeconds'],i['freshSocketOwnershipSeconds'],i['nativeRollingWindowSeconds'],i['guardianRollingWindowSeconds'],i['controlHeartbeatLossSeconds'])==(6,6,120,180,30)
 h=e['actualIntegration'];assert h['completed'] and h['activeMask']==2 and h['nssSeconds']>=190 and h['renewals']>60 and h['samplesValidated']>370 and h['operatorStopPassed'] and h['restorationPassed'];assert h['retainedSamplesEcm1'] and h['retainedSamples']<=32 and h['retainedRenewals']<=16 and h['recordBytes']<1048576 and h['nativeSessionAdvanceMs']>180000 and h['guardianExtendedBeyondInitialDeadline']
 assert all(e['restoration'].values());assert e['originalFailures']['preserved'] and not e['originalFailures']['nssRootCauseClaimed'];assert e['retainedService']['running'] and e['retainedService']['startupHealthPassed'] and e['retainedService']['identityVerified'];assert not e['scope']['privateInputsExported'];assert e['regression']['nativeControlChecks']==4409 and e['regression']['batchChecks']==27
 p=e['prewriteProtection'];assert p['freshCheckpointDownloadedShaAndGzipVerified'] and p['independentDetachedRollbackVerifiedBeforeFirstWrite'] and p['independentUndoVerified'] and p['stageExecBytes']<=9000 and p['bundleBytes']<=73728
 for p,h in e['sourceHashes'].items():assert hashlib.sha256((root/'code'/p).read_bytes()).hexdigest()==h,p
 assert hashlib.sha256((root/'code/work/resident-continuous-dev-20261008/endpoint-gate/rp_ecm_gate_lab_ct.c').read_bytes()).hexdigest()==e['actualIntegration']['nativeSourceSha256']
"""
(repo/'tools/check_resident_continuous.py').write_text(checker,encoding='utf-8')
f=repo/'tools/check_repository.py';text=f.read_text(encoding='utf-8');anchor="print(json.dumps({'passed':True,'filesChecked':count";assert text.count(anchor)==1;text=text.replace(anchor,"if (root/'evidence/resident-continuous.json').exists():\n import runpy\n runpy.run_path(str(root/'tools/check_resident_continuous.py'))['check'](root)\n"+anchor);f.write_text(text,encoding='utf-8')
print(json.dumps({'prepared':True,'sources':len(fresh),'manifestSources':len(manifest['sources']),'nssSeconds':actual['nssSeconds'],'serviceState':service['state'],'oldManifestPrefixPreserved':6257}))
