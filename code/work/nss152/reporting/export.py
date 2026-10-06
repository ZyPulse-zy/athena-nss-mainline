"""Append curated sources and redacted operational evidence; old Git blobs remain frozen."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import json,hashlib,copy,subprocess,html
w=Path(__file__).resolve().parents[3];repo=w/'athena-nss-mainline';r=w/'work/nss152';base='0b0b23c48b7e828701f6f7780522c4becf64592c'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda b:hashlib.sha256(b).hexdigest()
def put(p,v):
    p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists(),str(p)
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def evidence(n,v):put(repo/('evidence/nss152-'+n+'.json'),v)

a=read(w/'work/nss151/run-v5/automatic-result.json');history=read(w/'work/nss151/run-v5/transition-history-private.json')
assert a['passed'] and a['completedEpochs']==2 and len(history['history'])==2
assert a['actualClassChangeAutomaticallyRetired'] and a['sameSocketCtMarkNatWan']
first,second=[w/x['output'] for x in history['experiments']]
crash=read(r/'run-v4/independent-crash-result.json');assert crash['passed'];third=w/crash['caseDir']
assert crash['originalControllerKilledDuringEcm2'] and crash['restoredWithoutManualRouterUndo']
assert not (third/'result.json').exists()
health=read(r/'v1-final-health.json');physical=read(r/'physical-final.json');endpoints=read(r/'endpoint-client-closure.json');receiver=read(r/'receiver-closure.json');download=read(r/'download-receiver-closure.json')
assert all(v['passed'] for v in [health,physical,endpoints,receiver,download])
assert health['ecmStoppedAndZero'] and health['queryAge']<6 and health['noStaging'] and health['noExperimentState'] and health['noExperimentalModule']
assert endpoints['previousLoadsChecked']==20 and endpoints['ownedClientOrGuardProcessesRemaining']==0
assert receiver['exactOwnedReceiverAndTimeoutProcessesRemaining']==download['exactOwnedReceiverAndTimeoutProcessesRemaining']==0
trials=[]
for n,p,record,bound in [(1,first,'last-record-private.json',1678),(2,second,'last-record-private.json',1678),(3,third,'crash-last-record-private.json',1725)]:
    raw=read(p/record);plan=read(p/'stage-plan-private.json');checkpoint=read(p/'stage-checkpoint-verified.json');undo=read(p/'stage-undo-verified.json');receipt=read(p/'stage-receipt-private.json');detached=read(p/'stage-detached-private.json');inputs=read(p/'source-manifest-preaudit.json')
    assert len(inputs)==bound and all(undo.values()) and checkpoint['gzipVerified']
    assert receipt['rollbackBeforeFirstWrite'] and receipt['parentIdentityVerified'] and receipt['pipeInodesVerified'] and detached['identity']['ppid']==1
    for f,d in inputs.items():assert sha((w/f).read_bytes())==sha((p/'frozen'/f).read_bytes())==d
    assert raw.get('error') is None and raw['firmwareZeroAfterRetirement'] and raw['dualPhysicalQueuesRestored']
    trials.append({'test':['real-class-transition','automatic-successor','controller-crash-independent-recovery'][n-1],
      'passed':True,'wan':plan['selected']['tcp']['wan'],'observedEcmSequence':[0,2,1,0] if n==1 else [0,2,0],
      'fullMarkNatWanAffinityCorrect':True,'actualTagsAndFqCodelLeaves':4,'sourceBindingsActual':bound,
      'payloadBytesActual':plan['qosCodeBytes'],'guardianExecBytesActual':plan['execBytes'],
      'checkpointDownloadedShaGzipVerified':True,'independentRollbackBeforeFirstWrite':True,'detachedParentPidOne':True,
      'unchangedQoS':True,'nativeHardSeconds':27,'ownerMaxSeconds':100,'successGraceSeconds':5,
      'nativeRenewals':len(raw['renewals']),'firmwareZeroAndAllOriginalStateRestored':True,'undo':undo,
      'metric':read(p/'lifecycle-metrics.json') if n>1 else None})
    assert plan['qosCodeBytes']<=73728 and plan['execBytes']<=9000
c=read(first/'last-record-private.json');full=c['actualReclassification']['evidence']['completeSelected'];remaining=read(first/'actual-remaining-udp-proof.json');both=read(first/'actual-accelerated-state-proof.json')
assert c['classChangeTestCompleted'] and c['actualReclassification']['affected']==['tcp']
assert full['sameSourceCompleteFrame'] and full['sameAdmissionFrame'] and full['afterRejectionOnly'] and not full['scanTruncated']
assert full['slots']['tcp']['class']=='BE' and full['slots']['tcp']['reason']=='cooldown' and full['slots']['udp']['class']=='RT'
assert remaining['connectionCount']==1 and remaining['proof']['udp']['serial']==both['proof']['udp']['serial']
assert all(history['history'][0][k]!=history['history'][1][k] for k in ['owner','tagOwner','frozenHash','checkpointName'])
assert history['history'][0]['selected']==history['history'][1]['selected']
assert all(x!=y for x,y in zip(history['history'][0]['nativeCis'],history['history'][1]['nativeCis']))
classproof={'passed':True,'realApplicationPause':True,'originalTcpSocketAndCtStayedPresent':True,'tcpClassBefore':'BULK','tcpClassAfter':'BE','reason':'cooldown','sameQueryCompleteActualClassEvidence':True,'onlyTcpAffected':True,'projectionAbsenceNotTreatedAsCtExit':True,'learningStoppedBeforeTcpCloseAndDrain':True,'targetTcpCiAbsentIndependentlyVerified':True,'originalUdpCiAndRtDualTagsPreserved':True,'cpuBarrierNotFirmwareAck':True,'noTagChangeBeforeWithdrawal':True,'oldEpochClosedAndFullyRestored':True,'newQueryCheckpointOwnerPinAndBothCis':True,'sameSocketCtMarkNatWanInSuccessor':True,'oldTerminalGateNeverReopened':True,'nativeBudgetsUnchanged':[6,27,100]}
crashproof={k:v for k,v in crash.items() if k not in ['caseDir']};crashproof.update(controllerIsExperimentalPcController=True,permanentClassifierNotKilled=True,routerServiceNotKilled=True,noManualRouterRollbackDuringRecovery=True)
failures=[
 {'case':'151-initial-qualifier','cause':'Literal import/source checker applied to generator or non-module files; scoped to executable modules','beforeProductionStage':True},
 {'case':'151-v1','cause':'Escaped audit namespace still referenced the preceding directory; rejected before connecting/loading','beforeProductionStage':True},
 {'case':'151-v2-preparation','cause':'Windows default text decoding rejected UTF-8 generator input; partial original outputs preserved and exact completion checked','beforeProductionStage':True},
 {'case':'151-v2-runtime','cause':'Missing local uplink-capability alias; unintended old audit basename alias also found before checkpoint','beforeProductionStage':True,'endpointLoadStarted':True},
 {'case':'151-v3-static','cause':'Launcher and exact closer unit prefixes differed; discovered before traffic','beforeProductionStage':True},
 {'case':'151-v3-v4-checkers','cause':'Negative assertion text treated as a dependency, then checker expected one capability namespace for both wrappers; original failures kept','beforeProductionStage':True},
 {'case':'151-v4-runtime','cause':'Readonly audit reused a write-exclusive evidence label; EEXIST refusal; fixed with unique case labels','beforeProductionStage':True},
 {'case':'152-initial-static','cause':'State node path is derived by native setup and not serialized in the plan; baseline receipt name mismatch; checked before load','beforeProductionStage':True},
 {'case':'152-v2-static','cause':'Passive-ready marker and bare observation root still referenced the earlier namespace; found before load','beforeProductionStage':True},
 {'case':'152-v3-runtime','cause':'Supervisor counted audit files as experiment directories and refused before killing the controller; child completed its normal 20-second epoch and exact recovery','beforeProductionStage':False,'controllerKilled':False,'normalChildEpochSucceeded':True}]
for f in failures:f.update(passed=False,originalPreserved=True,notAnEstablishedNssKernelOrFirmwareDefect=True)
first_attempt=read(r/'run-v3/independent-crash-result.json');assert not first_attempt['passed'] and not first_attempt['controllerKilled']
oldcase=[p for p in r.glob('automatic-epoch-*') if p.is_dir() and (p/'result.json').exists()]
assert len(oldcase)==1 and read(oldcase[0]/'result.json')['passed'] and read(oldcase[0]/'stage-undo-verified.json')['moduleAbsent']
sources={}
for round_,versions in [(151,['','-v2','-v3','-v4','-v5']),(152,['','-v2','-v3','-v4'])]:
    for v in versions:
        q=read(w/f'work/nss{round_}/entry-qualified{v}.json');assert q['passed']
        for f,d in q['sourceManifest'].items():
            assert f.startswith(('work/nss151/','work/nss152/')) and f.endswith(('.mjs','.py','.lua','.ps1'))
            assert sha((w/f).read_bytes())==d;sources[f]=d
extras=['work/nss151/prepare-postchecks.py','work/nss151/verify-all-endpoints.mjs','work/nss151/verify-downloaders.mjs','work/nss151/verify-receivers.mjs','work/nss151/calibrate-clock.mjs','work/nss152/prepare-postchecks.py','work/nss152/verify-all-endpoints.mjs','work/nss152/verify-downloaders.mjs','work/nss152/verify-receivers.mjs','work/nss152/calibrate-clock.mjs','work/nss152/prepare-analysis.py','work/nss152/analyze.py','work/nss152/reporting/export.py','work/nss152/reporting/verify-published.py']
for f in extras:assert f not in sources;sources[f]=sha((w/f).read_bytes())
manifest=read(repo/'source-manifest.json');assert manifest['lastAppendExport']=='NSS150';prefix=copy.deepcopy(manifest['sources']);assert len(prefix)==2148
old_runtime=subprocess.check_output(['git','show',base+':evidence/current-runtime.json'],cwd=repo)
assert read(repo/'evidence/current-runtime.json')['round']=='NSS150' and not (repo/'evidence/nss150-runtime.json').exists()
# Every validation above is read-only. Repository mutation begins only here.
(repo/'evidence/nss150-runtime.json').write_bytes(old_runtime)
for f,d in sorted(sources.items()):
    assert all(x not in f.lower() for x in ['private','credential','connect-router']);target=repo/'code'/f;assert not target.exists();target.parent.mkdir(parents=True,exist_ok=True);b=(w/f).read_bytes();target.write_bytes(b)
    manifest['sources'].append({'path':'code/'+f,'workspaceSource':f,'sha256':d,'bytes':len(b),'role':'exact-class-change-controller-crash-or-explicit-reporting-source'})
assert manifest['sources'][:2148]==prefix
manifest.update(lastAppendExport='NSS152',generatedAt=datetime.now(timezone.utc).isoformat(),privateDataExcluded=True,preservesOriginalSourceBytes=True)
(repo/'source-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
proof={'passed':True,'historicPrefixSources':2148,'sources':len(sources),'sourceHashes':sources,'historicPrefixCanonicalSha256':sha(json.dumps(prefix,sort_keys=True,separators=(',',':')).encode()),'historicManifestPrefixUnchanged':True,'actual151Bindings':1678,'actual152Bindings':1725,'privateCapabilityInputsBoundLocally':3,'privateCapabilityInputContentsExcluded':True,'originalFailureSourcesKept':True,'nativeFactoriesUnchanged':[138,149],'permanentClassifierAndKernelGateUnchanged':True}
evidence('source-proof',proof);evidence('trials',trials);evidence('class-transition',classproof);evidence('controller-crash',crashproof);evidence('automatic-result',a);evidence('failures',failures)
for n,v in [('final-audit',health),('physical-final',physical),('endpoint-client-closure',endpoints),('receiver-closure',receiver),('download-receiver-closure',download)]:evidence(n,v)
main={'round':'NSS152','passed':True,'observedAt':health['observedAt'],'actualAutomaticClassTransitionAndRelearningPassed':True,'actualControllerCrashIndependentRecoveryPassed':True,'actual151Bindings':1678,'actual152Bindings':1725,'nativeFactoriesUnchanged':[138,149],'qualified151Controller':'work/nss151/run-v5.mjs','qualified152Controller':'work/nss152/crash-controller-v4.mjs','classTransition':classproof,'controllerCrash':crashproof,'trials':trials,'failuresPreserved':len(failures),'exportedSources':len(sources),'finalAudit':health,'physicalRestore':physical,'endpointClosure':endpoints,'receiverClosure':receiver,'downloadReceiverClosure':download,'old150RuntimeRetainedSha256':sha(old_runtime),'matchedCpuComparison':False,'cpuReductionConclusion':None,'realHumanGameAcceptance':False,'highLoad300MbpsAcceptance':False,'permanentNssControllerInstalled':False,'nssPermanentlyEnabled':False,'desktopOperated':False,'steamOrCs2Started':False,'nightHeartbeatRemainsPaused':True,'sourceNativeOwnerSeconds':[6,27,100],'clientHardSeconds':180,'execRawBundleRecordBytes':[9000,65536,73728,1048576]}
evidence('mainline',main)
runtime={'round':'NSS152','observedAt':health['observedAt'],'workerPid':health['workerPid'],'guardianPid':health['guardianPid'],'classifierConfigSha256':health['configSha256'],'classifierDeployment':'NSS68','actualAutomaticClassTransitionAndRelearningPassed':True,'actualControllerCrashIndependentRecoveryPassed':True,'qualifiedExperimentalController':'work/nss152/crash-controller-v4.mjs','boundInputs':1725,'nssPermanentlyEnabled':False,'permanentNssControllerInstalled':False,'cpuConclusion':None,'realHumanGameAcceptance':False,'nightHeartbeatRemainsPaused':True,'historical150RuntimePreservedSha256':sha(old_runtime),'audit':health,'physicalRootRestoreAudit':physical,'endpointClientClosureAudit':endpoints,'ownedReceiverClosureAudit':receiver,'ownedDownloadReceiverClosureAudit':download}
(repo/'evidence/current-runtime.json').write_text(json.dumps(runtime,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
when=datetime.fromisoformat(health['observedAt'].replace('Z','+00:00')).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
metrics=[t['metric'] for t in trials if t['metric']]
rows='\n'.join('| %s | %d | %.2f | %.3f | %.3f | %d/%d | %d |'%(t['test'],t['wan'],t['metric']['seconds'],t['metric']['serverConfirmedTcpUploadMbps'],t['metric']['softirqPercent'],t['metric']['udp']['received'],t['metric']['udp']['sent'],t['nativeRenewals'])for t in trials if t['metric'])
body=f'''# 自动改类重学与控制进程中断恢复已实测

更新：{when}，北京时间。最新 NSS152，包含 NSS151 自动改类闭环。仅后台自有有界 TCP 上传＋小 UDP，没有桌面、Steam、CS2 操作。

**真实 BULK→BE 只撤销 TCP CI，ECM2→1，原 UDP CI/RT双向tag保持；旧代完整恢复后，同socket/CT自动取得新query/checkpoint/owner/pin和两个新CI并运行20秒。另一次在ECM2时实际终止精确自有PC控制进程，路由器独立守护仍完成20秒、续租、精确撤销与完整恢复。**

| 测试 | WAN | NSS观测秒 | 服务器确认上传Mbps | softirq % | UDP收/发 | 续租 |
|---|---:|---:|---:|---:|---:|---:|
{rows}

这些是生命周期和控制中断恢复实测；没有新的同负载CPU因果对照，降幅为null。UDP echo不是CS2 jitter/loss/Miss。未部署长期NSS控制器，未验收300Mbps或真人游戏；没有杀常驻分类器/路由服务，也没有放宽6/27/100秒及字节上限。

版本拼接中的本地路径/标记/检查器错误均保留。首次中断测试把审计文件误计为目录，在kill前拒绝；其原控制器仍完成正常20秒及恢复，不能算中断恢复成功。随后修正只枚举目录，并实际执行一次kill证明。分类器/内核gate/原138及149factory均未改。

终态常驻NSS68/config581b5d46…c791d7、{health['workerPid']}/{health['guardianPid']}、publication upTag0不变；完整原审核source{health['queryAge']:.2f}秒，ECM关闭全零，无事务/stage/state/模块，两物理wan/lan4原mq+四fq_codel精确恢复。20个已有有限负载端点/客户端与自有SSH发送/接收器关闭，WAN4既有认证down和四路failover保持。heartbeat仍暂停。

下一步是单WAN有限常驻supervisor试运行，继续一TCP BULK＋一UDP RT、fresh owner和独立恢复，处理真实改类/退出和控制器restart；通过后才考虑延长运行、多flow或第二WAN。真人体验只在用户方便时集中一次，不要求持续挂游戏、重复Steam下载。

证据：LINKS
'''
names=[('主线','mainline'),('改类','class-transition'),('中断','controller-crash'),('实际轮次','trials'),('失败','failures'),('终态','final-audit'),('物理根','physical-final'),('端点','endpoint-client-closure')]
for file in ['AGENTS.md','docs/STATE.md','docs/PLAN.md','docs/EXPERIMENT_LOG.md']:
    p=repo/file;prefix_='../' if file.startswith('docs/') else '';links='、'.join(f'[{label}]({prefix_}evidence/nss152-{name}.json)'for label,name in names)
    old=p.read_text(encoding='utf-8');p.write_text(body.replace('LINKS',links)+'\n## NSS150及更早历史\n\n'+old,encoding='utf-8')
p=repo/'README.md';old=p.read_text(encoding='utf-8');p.write_text('# Athena NSS mainline\n\n最新 [NSS152](evidence/nss152-mainline.json)：真实改类自动撤销/新代重学和精确PC控制进程中断后的路由器独立恢复通过。后台自有TCP/UDP，无需游戏或下载；所有实验已恢复，长期/300Mbps/真人仍未验收。先读 [STATE](docs/STATE.md) 与 [PLAN](docs/PLAN.md)。\n\n## NSS150及更早历史\n\n'+old,encoding='utf-8')
tablerows=''.join('<tr><td>%s</td><td>%d</td><td>%.2f</td><td>%.3f</td><td>%.3f</td><td>%d/%d</td></tr>'%(html.escape(t['test']),t['wan'],t['metric']['seconds'],t['metric']['serverConfirmedTcpUploadMbps'],t['metric']['softirqPercent'],t['metric']['udp']['received'],t['metric']['udp']['sent'])for t in trials if t['metric'])
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NSS152 改类与中断恢复实测</title><style>body{font:16px/1.8 system-ui,"Microsoft YaHei",sans-serif;background:#f3f5f7;color:#182638;margin:0}main{max-width:1000px;margin:40px auto;padding:32px;background:white;border-radius:14px}h1{line-height:1.3}table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}td,th{border-bottom:1px solid #dce3eb;padding:10px;text-align:left}.ok{background:#e8f6ef;padding:18px;border-left:4px solid #16845c}.note{background:#fff4df;padding:18px}code{overflow-wrap:anywhere}a{color:#1761a2}@media(max-width:650px){main{margin:0;padding:18px}table{font-size:13px}td,th{padding:5px}}</style><main><p>Athena AX6600 · NSS151–152</p><h1>自动改类重学和控制中断恢复已实测</h1><p class="ok">TCP从BULK变BE → 只撤销该TCP CI，原UDP RT保持 → 旧代完整恢复 → 同socket/CT、mark/NAT/WAN以新query、checkpoint、owner、pin和CI自动重学。另一次在ECM＝2时实际终止自有PC控制进程，路由器独立守护完成20秒、续租及精确恢复。</p><table><thead><tr><th>测试</th><th>WAN</th><th>秒</th><th>上传Mbps</th><th>softirq %</th><th>UDP收/发</th></tr></thead><tbody>'''+tablerows+'''</tbody></table><p class="note">有限生命周期和中断恢复证明，尚未常驻部署。没有新的CPU因果对照；自有UDP echo不代表CS2 jitter/loss/Miss。未验收300Mbps、长期稳定或真人体验。</p><h2>失败与修复</h2><p>本地版本拼接中的路径、端点标记和检查器错误均保留。第一次中断测试在kill前因误计审计文件为目录而拒绝；原子进程正常完成20秒并恢复。修正只枚举目录后才得到实际中断恢复证明。没有修改常驻分类器或内核gate，没有扩大6/27/100秒和字节限额。</p><h2>最终状态</h2><p>ECM关闭全零，无事务、stage、state、实验模块；wan/lan4原mq+四fq_codel恢复。20个有限端点/客户端和自有SSH负载进程关闭。常驻NSS68和四路failover不变，WAN4既有认证down未干预。</p><h2>下一步</h2><p>单WAN有限常驻supervisor试运行，验证实际退出与restart；再考虑多flow/第二WAN。无需持续挂游戏或反复下载。NSS承担主要数据面QoS的方向保持，CAKE作为fallback/对照。</p><p><a href="https://github.com/ZyPulse-zy/athena-nss-mainline/blob/main/docs/STATE.md">GitHub STATE</a></p></main></html>'''
(w/'outputs/nss152-mainline-report.html').write_text(page,encoding='utf-8');(repo/'reports/nss152-mainline-report.html').write_text(page,encoding='utf-8')
put(r/'reporting/export-receipt.json',{'passed':True,'sourcesAdded':len(sources),'sourceTotal':len(manifest['sources']),'old150RuntimeGitBytesPreserved':True,'rawCtNoncesCredentialsCheckpointsBinariesExcluded':True})
print(json.dumps({'passed':True,'sourcesAdded':len(sources),'sourcesTotal':len(manifest['sources']),'actualClassTransition':True,'actualControllerCrash':True,'old150RuntimePreserved':True}))
