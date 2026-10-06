"""Seal the real download trial and final evening health; preserve every old blob."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib,subprocess,copy,html
w=Path(__file__).resolve().parents[2];r=w/'work/nss159';repo=w/'athena-nss-mainline';even=w/'work/nss158/evening-20261006'
base='c28ee23cd45cf89a079c6f1345705e8971c4beb7'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda b:hashlib.sha256(b).hexdigest()
dump=lambda x:json.dumps(x,ensure_ascii=False,indent=2)+'\n'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()==base
manifest=read(repo/'source-manifest.json');prefix=copy.deepcopy(manifest['sources']);assert len(prefix)==2687 and manifest['lastAppendExport']=='NSS158'
oldruntime=subprocess.check_output(['git','show',base+':evidence/current-runtime.json'],cwd=repo);assert read(repo/'evidence/current-runtime.json')['round']=='NSS158'
health=read(even/'v3-final-health.json');physical=read(even/'physical-final.json');end=read(even/'endpoint-client-closure-v1.json');recv=read(even/'receiver-closure.json');down=read(even/'download-receiver-closure.json')
recovery=read(even/'v3-wan4-recovery-proof.json')
assert recovery['passed'] and recovery['tenRecoveryRampStepsReproduced'] and recovery['onlyThreeWan4DhcpRulesRestored']
assert health['wan4Up'] and health['wan4Ipv4Present'] and health['allFiveWanHealthy'] and health['exactWan4AutomaticRecoveryProved']
assert (even/'v1-final-failure-private.json').exists() and (even/'v2-final-failure-private.json').exists()
assert all(x['passed'] for x in [health,physical,end,recv,down])
assert datetime.fromisoformat(health['observedAt'].replace('Z','+00:00'))>=datetime(2026,10,6,11,40,tzinfo=timezone.utc)
assert health['queryAge']<6 and health['ecmStoppedAndZero'] and all(health[k] for k in ['noActiveTransaction','noStaging','noExperimentState','noExperimentalModule'])
assert end['previousLoadsChecked']==end['ownedUnitsInactiveMainPidZero']==48
assert end['temporaryFirewallRulesRemaining']==end['ownedClientOrGuardProcessesRemaining']==recv['exactOwnedReceiverAndTimeoutProcessesRemaining']==down['exactOwnedReceiverAndTimeoutProcessesRemaining']==0
p=r/'pilot-aba-20261006111840-56b833d97421713c';assert read(p/'automatic-result.json')['passed']
d=w/Path(read(p/'case-reference-private.json')['dir']);result=read(d/'result.json');record=read(d/'last-record-private.json');metric=read(d/'actual-long-metrics.json');comparison=read(d/'same-load-comparison.json');gap=read(d/'udp-gap-analysis.json');inspection=read(d/'renewal-source-inspection.json')
assert result['passed'] and result['matchedForwardingABACompleted'] and record['abaCompleted'] and record['firmwareZeroAfterRetirement']
assert [x['acceleratedCounts'] for x in metric['phases']]==[[0],[2],[0]] and all(20<=x['whole']['seconds']<21.5 for x in metric['phases'])
assert metric['direction']=='download' and metric['tcpMetric']=='application received payload bytes' and not metric['downlinkMainlyAckAndSmallUdp']
assert metric['nativeRenewals']==7 and metric['oneWan']==3
assert gap['sent']==884 and gap['received']==848 and gap['unreturned']==36 and gap['missingRunLengths']==[36]
assert not gap['lossLocationProven'] and not gap['causedByNssProven'] and not gap['realTimeQualityAccepted']
assert gap['bulkDownFqCodelDropDelta']==370 and gap['rtDownFqCodelDropDelta']==gap['rtUpFqCodelDropDelta']==0
assert comparison['passed'] and not comparison['comparabilityAccepted'] and comparison['softirqRelativeReductionPercent'] is None and sum(comparison['checks'].values())==5
assert inspection['compiledGateSourceHashVerified'] and inspection['shortAdmitFalseThenDeadlineUpdateThenAdmitTrueOnSuccess'] and not inspection['rootCauseProven'] and not inspection['kernelGateModified']
cp=read(d/'stage-checkpoint-verified.json');receipt=read(d/'stage-receipt-private.json');detached=read(d/'stage-detached-private.json');plan=read(d/'stage-plan-private.json');undo=read(d/'stage-undo-verified.json');baseline=read(d/'baseline-audit.json');inputs=read(d/'source-manifest.json')
assert len(inputs)==2086 and cp['gzipVerified'] and all(undo.values()) and baseline['configurationMatches']
assert receipt['rollbackBeforeFirstWrite'] and receipt['pipeInodesVerified'] and receipt['parentIdentityVerified'] and detached['identity']['ppid']==1
assert plan['qosCodeBytes']==73428 and plan['execBytes']==8947
for f,h in inputs.items():assert sha((w/f).read_bytes())==sha((d/'frozen'/f).read_bytes())==h
ecm=read(d/'actual-accelerated-state-proof.json');mapping=read(d/'post-checkpoint-class-leaf-map-proof.json');assert ecm['passed'] and ecm['connectionCount']==2 and mapping['mappingByActualClass']
for v in ecm['proof'].values():assert v['accelerated'] and v['natCorrect'] and v['fromLan4'] and v['fromBridgeLan']
assert ecm['proof']['tcp']['wanAffinity']==ecm['proof']['udp']['wanAffinity']==3 and ecm['proof']['tcp']['ctMark']==ecm['proof']['udp']['ctMark']
flowproof={'passed':True,'wan':3,'linuxPbrCtMarkNatWanAffinityCorrect':True,'tcpBulkUdpRtFourTagsCorrect':True,'fourFqCodelLeavesHavePackets':True,'connectionCount':2,'wholeAbaEcmCounts':[0,2,0],'fullPrivateInputsAndFrozenCopiesHashChecked':True,'bindings':2086,'checkpointDownloadedShaGzipVerified':True,'independentPpidOneRollbackVerifiedBeforeWrite':True,'payloadBytes':73428,'guardianExecBytes':8947,'allOriginalRestoreChecks':undo,'noGlobalConntrackFlush':True,'classifierKernelGateAndQosSourceUnchanged':True}
qs=[read(r/f'entry-qualified{s}.json') for s in ['', '-v2','-v3','-v4']]
for q in qs:
    assert q['passed'] and not q['productionExecution'] and q['fixturePolicyCases']==24
    for f,h in q['sourceManifest'].items():assert sha((w/f).read_bytes())==h
failures=[{'case':'qualifier-v1','reason':'Scanner mistook quoted replacement text for an import; no connection/write','originalSourcesAndFailurePreserved':True,'routerNssWrites':False},
 {'case':'pilot-20261006111153','reason':'Old audit directory regex refused before connection/endpoint/checkpoint/stage','originalSourcesAndFailurePreserved':True,'routerNssWrites':False},
 {'case':'pilot-20261006111253','reason':'Namespace substitution changed an inherited literal NSS49 audit filename; matched download pair but no router checkpoint/stage','originalSourcesAndFailurePreserved':True,'routerNssWrites':False},
 {'case':'first-endpoint-closure','reason':'Old unit regex refused before cleanup connection; independent expiry then exact corrected helper confirmed baseline and endpoint closed','independentExpiryAndCorrectedExactClosurePassed':True,'originalSourcesAndFailurePreserved':True},
 {'case':'current-download-rt-quality','reason':'36 consecutive authenticated UDP echo sequences unreturned in NSS B; software A/A2 full return; location and causation unresolved','functionalAbaPassed':True,'qualityAccepted':False,'originalSourcesAndFailurePreserved':True},
 {'case':'evening-four-wan-assertion','reason':'WAN4 naturally recovered; the old rigid four-WAN audit refused read-only closure. Original failure retained; unchanged-controller ten-step exact 300-bucket recovery replay verified','routerNssWrites':False,'originalSourcesAndFailurePreserved':True},
 {'case':'evening-dhcp-model-v1','reason':'First recovery model assumed subnet normalization and original insertion order; actual DHCP rule contains host/prefix and is appended among equal priorities. Exact removal leaves previous four-WAN rules byte-identical; corrected strict lease-derived three-rule model passed','routerNssWrites':False,'originalSourcesAndFailurePreserved':True}]
first=r/'pilot-aba-20261006111253-8d2638382a834c74';assert not read(first/'automatic-result.json')['passed'] and (first/'endpoint-closure-error-private.json').exists()
firstref=w/Path(read(first/'case-reference-private.json')['dir']);assert not (firstref/'stage-receipt-private.json').exists()
loads=sorted(x for x in r.glob('load-*') if x.is_dir());assert len(loads)==2
fixture=[]
for load in loads:
    cfg=read(load/'client-config-private.json');status=read(load/'result-private.json');fr=read(load/'firewall-receipt-private.json');final=read(load/'firewall-after-private.json');closed=read(load/'server-closed-private.json');assert cfg['seconds']==180 and cfg['mbps']==32 and cfg['bulkDirection']=='download'
    assert not status['errors'] and fr['beforeWriteIndependentGuardianVerified'] and fr['applied'] and len(fr['rules'])==2
    fv=json.loads(final['stdout']);assert final['code']==closed['code']==0 and fv['ownedRulesRemaining']==0 and fv['baselineRestored']
    assert 'MainPID=0' in closed['stdout'] and 'ActiveState=inactive' in closed['stdout']
    fixture.append({'clientSeconds':status['seconds'],'receivedApplicationBytes':status['tcpBytes'],'confirmedOldSendersClosedBeforeNext':status['confirmedOldSendersClosed'],'clientErrors':status['errors'],'onlyOneRemoteSenderAtATime':status['onlyOneRemoteSenderAtATime'],'fixedUdpAndMaximumEightTcpPorts':True,'offeredMbps':32,'globalCreditBytes':65536,'client180AndGuard210Seconds':True,'authenticatedSshRemote185SecondTimeout':True,'exactTwoTemporaryFirewallRulesIndependent180ExpiryVerifiedBeforeWrite':True,'firewallAndEndpointRestored':True})
existing={x['workspaceSource'] for x in prefix};sources={}
for f in r.iterdir():
    if f.is_file() and f.suffix in ['.mjs','.py','.lua','.ps1'] and not any(t in f.name.lower() for t in ['private','credential','connect-router']):sources[f.relative_to(w).as_posix()]=sha(f.read_bytes())
for f in (w/'work/nss158').glob('evening-*.mjs'):sources[f.relative_to(w).as_posix()]=sha(f.read_bytes())
f=w/'work/nss158/prepare-evening.py';sources[f.relative_to(w).as_posix()]=sha(f.read_bytes())
assert not existing.intersection(sources)
proof={'passed':True,'historicPrefixSources':2687,'historicPrefixCanonicalSha256':sha(json.dumps(prefix,sort_keys=True,separators=(',',':')).encode()),'historicManifestPrefixUnchanged':True,'old158RuntimeExactGitBytes':True,'sourceHashes':sources,'sources':len(sources),'actualInputBindings':2086,'actualInputsAndFrozenCopiesVerified':True,'privateDataExcluded':True,'frozenFailureSourcesUnchanged':True}
main={'round':'NSS159','passed':True,'status':'DOWNLOAD_FUNCTIONAL_ABA_PASSED_RT_ECHO_GAP_UNRESOLVED_CPU_COMPARABILITY_FAILED','observedAt':health['observedAt'],'functionalTwentySecondDownloadABA':True,'downloadFlowDataRatherThanAck':True,'downloadMetrics':metric,'downloadComparison':comparison,'udpGap':gap,'renewalSourceInspection':inspection,'flowAndRollbackProof':flowproof,'fixtureTrials':fixture,'failuresPreserved':failures,'realTimeQualityAccepted':False,'cpuConclusion':None,'qualifiedExperimentalController':'work/nss159/pilot-supervisor-v4.mjs','boundInputs':2086,'permanentNssEnabled':False,'permanentControllerInstalled':False,'humanCs2Acceptance':False,'highLoad300MbpsAcceptance':False,'desktopOperated':False,'schoolPolicyPbrCtMarkNatAffinityUnchanged':True,'sourceNativeOwnerClientSeconds':[6,27,100,180],'execRawBundleRecordBytes':[9000,65536,73728,1048576],'sourcesAdded':len(sources),'repositoryVisibility':'public','prior158RuntimeSha256':sha(oldruntime),'eveningAudit':health,'physicalRestore':physical,'endpointClosure':end,'ownedReceiverClosure':recv,'ownedDownloadSenderClosure':down,'nextStep':'Capture authenticated UDP at owned endpoint and PC wire, correlate exact firmware CI/renewal while holding the same bounded download; do not change the kernel lease based on temporal coincidence'}
runtime={'round':'NSS159','observedAt':health['observedAt'],'classifierDeployment':'NSS68','workerPid':health['workerPid'],'guardianPid':health['guardianPid'],'classifierConfigSha256':health['configSha256'],'qualifiedExperimentalController':main['qualifiedExperimentalController'],'boundInputs':2086,'integratedClassRetireRelearnHistorical158Passed':True,'functionalTwentySecondDownloadABA':True,'realTimeQualityAccepted':False,'cpuComparabilityAccepted':False,'cpuConclusion':None,'realHumanGameAcceptance':False,'nssPermanentlyEnabled':False,'permanentNssControllerInstalled':False,'repositoryVisibility':'public','autonomyDeadlineBeijing':'2026-10-06T20:00:00+08:00','historical158RuntimePreservedSha256':sha(oldruntime),'audit':health,'physicalRootRestoreAudit':physical,'endpointClientClosureAudit':end,'ownedReceiverClosureAudit':recv,'ownedDownloadReceiverClosureAudit':down}
now=datetime.fromisoformat(health['observedAt'].replace('Z','+00:00')).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
body=f'''# 真实下行功能闭环通过，实时质量仍有明确缺口

更新：{now}，北京时间。NSS159；本日20:00授权的晚间收尾。后台自有下载＋小UDP，没有操作桌面/Steam/CS2。

**新整合控制器已在WAN3完成三段各20秒software→NSS→software，ECM0→2→0。实际下载数据进入bulk leaf，小UDP进入RT leaf；TCP/UDP双向四tag、PBR/完整ct mark/NAT/WAN affinity、七次续租和完整独立恢复通过。** 复用NSS158 native/payload/stage原字节，只换有界下载夹具和精确输入命名空间。

| 指标 | software A | NSS B | software A2 |
|---|---:|---:|---:|
| 客户端实际收到下载 Mbps | 25.676 | 26.856 | 25.672 |
| softirq % | 14.289 | 6.245 | 12.962 |
| CPU busy % | 28.832 | 20.035 | 28.273 |
| UDP收/发 | 856/856 | 848/884 | 850/850 |
| UDP echo RTT p95 ms | 194.847 | 194.836 | 194.843 |
| time_squeeze / softnet drop | 0/0 | 0/0 | 0/0 |

**实时质量未通过：NSS B有连续36个echo未返回，位于B第10.976–11.840秒，约4.07%；两个软件段完整返回。** bulk下行FQ-CoDel异步计数drop370，RT上下行drop0；这证明bulk队列实际工作，但RT drop0不能证明端到端交付。第11.01秒有一次成功续租，时间重叠不是因果。已核对与实际二进制绑定的gate源码：成功续租短暂admit=false、更新期限再true，没有显式firmware drain；.5秒计数全程ECM2仍不能排除更短事件。没有端点逐包TX与PC线级捕获，不把未返回定位到NSS或上游，也不贸然修改lease/gate。

**CPU可比性仍5/7，降幅null。** 其它WAN背景0.933/1.640/2.340Mbps违反原上限与波动条件；保持原条件。观察到softirq下降，不能把本轮写成新的因果收益。UDP echo不是CS2 jitter/loss/Miss，没有300Mbps、真人、长期或永久NSS部署验收。NSS158上传与真实改类精确CI撤销/新代重学证明按原字节保存。

夹具仅一自有SSH sender32Mbps/64KiB credit，严格接收旧sender STOP/退出0才启动下一条自己的TCP，最多8端口；UDP固定，Linux自然PBR，没有强制WAN。两次实际夹具均独立FW180秒/OS250秒、PC180秒与210秒guard、SSH185秒timeout并恢复。当前2086绑定/实际冻结输入逐项SHA核验，checkpoint下载SHA/gzip、写前PPID1恢复，payload73428/guardian8947满足73728/9000；原source6/native27/owner100/client180与1MiB记录不放宽。

旧目录regex、继承NSS49依赖误替换和旧端点unit regex三个真实入口/恢复检查失败均保留。前两次router checkpoint/NSS stage前拒绝；首个endpoint helper在连接前拒绝，独立到期后正确精确helper确认恢复。补充实际静态literal依赖检查，旧不完整资格声明保留并明确失效范围；没有覆盖失败或修改冻结证据。

晚间原完整审核source{health['queryAge']:.2f}秒，NSS68/{health['workerPid']}/{health['guardianPid']}健康、配置不变；ECM关闭全零，无事务/stage/state/实验模块。两物理原mq+四fq_codel，48历史/新端点与自有接收/发送器、PC客户端/guard均退出，所有FW基线一致。WAN4自然恢复：原控制器十步恢复权重和全部300桶精确重现，五路各60桶；仅恢复三条由实际DHCP租约派生的WAN4规则。旧四路断言拒绝及首个DHCP模型错误均保留，未主动认证或修改路由。常驻分类器与CAKE fallback保留，本轮未长期启用NSS。

下一步只定位这次受控下行UDP缺口：自有端点与PC同步逐包观测，关联firmware CI与续租；定位后再集中真人CS2验证。先不扩第二WAN/共享预算/WiFi/autorate，不重复CPU门槛，不为等待负载下载新游戏。本日到此封存，完成检查/推送/实际archive后暂停heartbeat。

证据：LINKS
'''
evidence={'mainline':main,'source-proof':proof,'qualification':qs,'download-metrics':metric,'download-comparison':comparison,'udp-gap':gap,'renewal-source-inspection':inspection,'flow-rollback':flowproof,'fixture-trials':fixture,'failures':failures,'evening-final-audit':health,'wan4-natural-recovery':recovery,'evening-physical-final':physical,'evening-endpoint-client-closure':end,'evening-receiver-closure':recv,'evening-download-sender-closure':down}
planned={repo/f'evidence/nss159-{n}.json':dump(x).encode('utf-8') for n,x in evidence.items()};planned[repo/'evidence/nss158-runtime.json']=oldruntime
for f,h in sorted(sources.items()):
    b=(w/f).read_bytes();assert sha(b)==h;planned[repo/'code'/f]=b
    manifest['sources'].append({'path':'code/'+f,'workspaceSource':f,'sha256':h,'bytes':len(b),'role':'bounded-download-functional-aba-rt-gap-and-evening-closure'})
for dest in planned:assert not dest.exists(),str(dest)
for dest,b in planned.items():dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b)
manifest.update(lastAppendExport='NSS159',generatedAt=datetime.now(timezone.utc).isoformat(),privateDataExcluded=True,preservesOriginalSourceBytes=True)
assert manifest['sources'][:2687]==prefix
(repo/'source-manifest.json').write_text(dump(manifest),encoding='utf-8');(repo/'evidence/current-runtime.json').write_text(dump(runtime),encoding='utf-8')
labels=[('主线','mainline'),('下行数据','download-metrics'),('可比性','download-comparison'),('UDP缺口','udp-gap'),('续租源码核查','renewal-source-inspection'),('恢复','flow-rollback'),('失败','failures'),('晚间审核','evening-final-audit'),('端点','evening-endpoint-client-closure')]
for file in ['AGENTS.md','docs/STATE.md','docs/PLAN.md','docs/EXPERIMENT_LOG.md']:
    dest=repo/file;pre='../' if file.startswith('docs/') else '';links='、'.join(f'[{a}]({pre}evidence/nss159-{b}.json)' for a,b in labels)
    dest.write_text(body.replace('LINKS',links)+'\n## NSS158及更早历史\n\n'+dest.read_text(encoding='utf-8'),encoding='utf-8')
dest=repo/'README.md';dest.write_text('# Athena NSS mainline\n\n最新[NSS159](evidence/nss159-mainline.json)：真实下行三段功能通过，NSS段36个UDP echo未返回，实时质量仍待定位；晚间全部恢复。先读[STATE](docs/STATE.md)。\n\n## NSS158及更早历史\n\n'+dest.read_text(encoding='utf-8'),encoding='utf-8')
page='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>NSS159 主线</title><style>body{font:16px/1.8 system-ui;max-width:980px;margin:40px auto;padding:24px;color:#182638;background:#f3f5f7}pre{white-space:pre-wrap;background:white;padding:25px}a{color:#1761a2}</style><body><h1>NSS159 · 下行闭环与实时缺口</h1><pre>'+html.escape(body.replace('LINKS','源码与脱敏证据见GitHub STATE'))+'</pre><a href="https://github.com/ZyPulse-zy/athena-nss-mainline/blob/main/docs/STATE.md">GitHub STATE</a></body></html>'
for dest in [w/'outputs/nss159-mainline-report.html',repo/'reports/nss159-mainline-report.html']:assert not dest.exists();dest.write_text(page,encoding='utf-8')
with (r/'export-receipt.json').open('x',encoding='utf-8') as f:f.write(dump({'passed':True,'sourcesAdded':len(sources),'sourcesTotal':len(manifest['sources']),'actualBindings':2086,'old158RuntimeExactGitBytes':True,'downloadFunctionalABAPassed':True,'realTimeQualityAccepted':False,'cpuComparabilityAccepted':False,'eveningFullClosurePassed':True}))
print(json.dumps(read(r/'export-receipt.json')))
