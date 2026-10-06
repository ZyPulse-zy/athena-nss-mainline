"""Publish explicit source allowlist and independently validated redacted results."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib,subprocess,copy
w=Path(__file__).resolve().parents[3];r=w/'work/nss154';repo=w/'athena-nss-mainline';base='701fe6dc8a810ef49c8e7d55b475aa1f24b14b61'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda b:hashlib.sha256(b).hexdigest()
def put(p,v):
    assert not p.exists(),str(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def ev(n,v):put(repo/f'evidence/nss154-{n}.json',v)
qualified=[read(r/f'entry-qualified{suffix}.json') for suffix in ['', '-v2','-v3']]
assert all(x['passed'] for x in qualified)
sources={k:v for q in qualified for k,v in q['sourceManifest'].items()}
actual=read(r/'entry-source-manifest-v3.json');assert len(actual)==1795 and len(sources)==43
for f,d in actual.items():assert sha((w/f).read_bytes())==sha((r/'frozen-qualified-inputs-v3'/f).read_bytes())==d
a=read(r/'run3/automatic-result.json');j=read(r/'run3/journal-private.json');assert a['passed'] and j['state']=='COMPLETE' and len(j['history'])==len(j['cases'])==2
first,second=j['history'];assert first['childNormalReceiptAbsent'] and first['proofOrigin']=='independent-parent-recovery-assessment'
assert first['selected']==second['selected'] and first['boot']==second['boot'] and first['producer']==second['producer']
for k in ['owner','tagOwner','frozenHash','checkpointName']:assert first[k]!=second[k]
assert second['firstSequence']>first['lastActiveSequence'] and all(x!=y for x,y in zip(first['nativeCis'],second['nativeCis']))
crash=read(r/'run3/supervisor-crash-private.json');resumed=read(r/'run3/resume-supervisor-result.json')
assert crash['passed'] and crash['exitCode'] is None and crash['terminationSignal']=='SIGTERM' and crash['ownedKillReturnedTrue'] and crash['subjectWasSupervisorItself'] and crash['noSeparateHostEpochChild']
assert crash['identity']['pid']==crash['pid'] and crash['identity']['exactExe'] and crash['identity']['exactOwnedScript']
assert resumed['passed'] and resumed['supervisorPid']!=crash['pid'] and resumed['originalSupervisorActuallyReplaced']
assert read(r/'run3/old-process-absence-private.json')['sameOriginalIdentityPresent'] is False
assert not (w/j['cases'][0]/'result.json').exists()
health=read(r/'v1-final-health.json');physical=read(r/'physical-final.json');endpoints=read(r/'endpoint-client-closure.json');recv=read(r/'receiver-closure.json');down=read(r/'download-receiver-closure.json')
assert all(v['passed'] for v in [health,physical,endpoints,recv,down])
assert health['ecmStoppedAndZero'] and health['queryAge']<6 and health['noStaging'] and health['noExperimentState'] and health['noExperimentalModule']
assert endpoints['previousLoadsChecked']==endpoints['ownedUnitsInactiveMainPidZero']==24 and endpoints['ownedClientOrGuardProcessesRemaining']==0
assert recv['exactOwnedReceiverAndTimeoutProcessesRemaining']==down['exactOwnedReceiverAndTimeoutProcessesRemaining']==0
trials=[]
for i,folder in enumerate(j['cases']):
    p=w/folder;record=read(p/('crash-last-record-private.json' if i==0 else 'last-record-private.json'));plan=read(p/'stage-plan-private.json');cp=read(p/'stage-checkpoint-verified.json');undo=read(p/'stage-undo-verified.json');receipt=read(p/'stage-receipt-private.json');detached=read(p/'stage-detached-private.json');inputs=read(p/'source-manifest-preaudit.json');metric=read(p/'lifecycle-metrics.json')
    assert len(inputs)==1795 and all(undo.values()) and cp['gzipVerified'] and receipt['rollbackBeforeFirstWrite'] and receipt['pipeInodesVerified'] and receipt['parentIdentityVerified'] and detached['identity']['ppid']==1
    for f,d in inputs.items():assert sha((w/f).read_bytes())==sha((p/'frozen'/f).read_bytes())==d
    assert record.get('error') is None and record['firmwareZeroAfterRetirement'] and record['dualPhysicalQueuesRestored'] and record['automaticLifecycleEpochCompleted']
    assert plan['qosCodeBytes']<=73728 and plan['execBytes']<=9000
    assert metric['direction']=='upload' and metric['tcpMetric']=='server-confirmed received bytes' and metric['causalCpuReductionPercent'] is None and not metric['cs2Acceptance']
    trials.append({'generation':i+1,'test':'supervisor-itself-crash-independent-completion' if i==0 else 'new-supervisor-from-disk-journal', 'passed':True,'wan':plan['selected']['tcp']['wan'],'observedEcmSequence':[0,2,0],'fourTagsFourFqCodelLeaves':True,'completeClassCtMarkNatWanAffinityCorrect':True,'sourceBindingsActual':1795,'payloadBytesActual':plan['qosCodeBytes'],'guardianExecBytesActual':plan['execBytes'],'checkpointDownloadedShaGzipVerified':True,'rollbackBeforeFirstWrite':True,'detachedParentPidOne':True,'nativeHardSeconds':27,'ownerMaxSeconds':100,'nativeRenewals':len(record['renewals']),'fullyRestored':True,'undo':undo,'metric':metric,'hostNormalCompletionReceiptPresent':i==1})
assert trials[0]['wan']==trials[1]['wan']
extras=['prepare-postchecks.py','health.mjs','read-final-physical.mjs','verify-all-endpoints.mjs','verify-receivers.mjs','verify-downloaders.mjs','calibrate-clock.mjs','analyze.py','reporting/export.py','reporting/verify-published.py','reporting/update-checker.py']
for n in extras:sources['work/nss154/'+n]=sha((r/n).read_bytes())
for f,d in sources.items():assert sha((w/f).read_bytes())==d and f.startswith('work/nss154/') and f.endswith(('.mjs','.py','.ps1','.lua')) and all(x not in f.lower() for x in ['private','credential','connect-router'])
manifest=read(repo/'source-manifest.json');prefix=copy.deepcopy(manifest['sources']);assert len(prefix)==2317 and manifest['lastAppendExport']=='NSS153'
oldruntime=subprocess.check_output(['git','show',base+':evidence/current-runtime.json'],cwd=repo);assert read(repo/'evidence/current-runtime.json')['round']=='NSS153';assert not (repo/'evidence/nss153-runtime.json').exists()
failures=[]
for run,cause in [('run1','Original read-only WAN prerequisite popen read returned nil; detailed independent repeat passed, root cause remains unproved'),('run2','Version generator changed a historical literal session-binding dependency to a nonexistent versioned path; corrected only in v3')]:
    failure=read(r/run/'automatic-result.json');assert not failure['passed'];journal=read(r/run/'journal-private.json');assert journal['state']=='READY' and not journal['history']
    failures.append({'case':run,'passed':False,'cause':cause,'originalPreserved':True,'beforeCheckpointAndNssStage':True,'supervisorActuallyKilled':False,'nssOrFirmwareFailure':False})
proof={'passed':True,'historicPrefixSources':2317,'historicPrefixCanonicalSha256':sha(json.dumps(prefix,sort_keys=True,separators=(',',':')).encode()),'historicManifestPrefixUnchanged':True,'sources':len(sources),'sourceHashes':sources,'actualBindings':1795,'privateCapabilityInputsBoundLocally':3,'privateCapabilityInputContentsExcluded':True,'originalRefusalSourcesKept':True,'nativeFactoryUnchanged':149,'permanentClassifierAndKernelGateUnchanged':True}
# No Git mutation until all actual records, source hashes and closure above pass.
(repo/'evidence/nss153-runtime.json').write_bytes(oldruntime)
for f,d in sorted(sources.items()):
    p=repo/'code'/f;assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True);b=(w/f).read_bytes();p.write_bytes(b)
    manifest['sources'].append({'path':'code/'+f,'workspaceSource':f,'sha256':d,'bytes':len(b),'role':'finite-supervisor-journal-restart-or-explicit-reporting'})
assert manifest['sources'][:2317]==prefix
manifest.update(lastAppendExport='NSS154',generatedAt=datetime.now(timezone.utc).isoformat(),privateDataExcluded=True,preservesOriginalSourceBytes=True)
(repo/'source-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
main={'round':'NSS154','passed':True,'observedAt':health['observedAt'],'actualSupervisorItselfCrashAndRestart':True,'newSupervisorReconstructedFromDiskJournal':True,'sameSocketCtMarkNatWanInSuccessor':True,'newQueryCheckpointOwnerKernelPinAndBothCis':True,'oldTerminalGateNeverReopened':True,'completedEpochs':2,'supervisorActuallyTerminatedDuringEcm2':True,'routerGuardianNotKilled':True,'separateHostEpochChildUsed':False,'routerRebootTested':False,'qualifiedController':'work/nss154/pilot-supervisor-v3.mjs','boundInputs':1795,'trials':trials,'nativeFactoryUnchanged':149,'sourceNativeOwnerSeconds':[6,27,100],'clientHardSeconds':180,'execRawBundleRecordBytes':[9000,65536,73728,1048576],'matchedCpuComparison':False,'cpuReductionConclusion':None,'realHumanGameAcceptance':False,'highLoad300MbpsAcceptance':False,'permanentNssControllerInstalled':False,'nssPermanentlyEnabled':False,'desktopOperated':False,'steamOrCs2Started':False,'dayHeartbeatActiveUntilBeijing':'2026-10-06T20:00:00+08:00','repositoryVisibility':'public','failuresPreserved':len(failures),'exportedSources':len(sources),'old153RuntimeRetainedSha256':sha(oldruntime),'finalAudit':health,'physicalRestore':physical,'endpointClosure':endpoints,'receiverClosure':recv,'downloadReceiverClosure':down}
for n,v in [('source-proof',proof),('qualification',{'versions':qualified,'actualBindings':1795,'passed':True}),('automatic-result',a),('trials',trials),('failures',failures),('final-audit',health),('physical-final',physical),('endpoint-client-closure',endpoints),('receiver-closure',recv),('download-receiver-closure',down),('mainline',main)]:ev(n,v)
runtime={'round':'NSS154','observedAt':health['observedAt'],'workerPid':health['workerPid'],'guardianPid':health['guardianPid'],'classifierConfigSha256':health['configSha256'],'classifierDeployment':'NSS68','qualifiedExperimentalController':main['qualifiedController'],'boundInputs':1795,'actualSupervisorItselfCrashAndRestart':True,'completedEpochs':2,'nssPermanentlyEnabled':False,'permanentNssControllerInstalled':False,'cpuConclusion':None,'realHumanGameAcceptance':False,'dayHeartbeatActiveUntilBeijing':main['dayHeartbeatActiveUntilBeijing'],'historical153RuntimePreservedSha256':sha(oldruntime),'audit':health,'physicalRootRestoreAudit':physical,'endpointClientClosureAudit':endpoints,'ownedReceiverClosureAudit':recv,'ownedDownloadReceiverClosureAudit':down,'repositoryVisibility':'public'}
(repo/'evidence/current-runtime.json').write_text(json.dumps(runtime,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
when=datetime.fromisoformat(health['observedAt'].replace('Z','+00:00')).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
rows='\n'.join('| %d | %d | %.2f | %.3f | %.3f | %d/%d | %d |'%(t['generation'],t['wan'],t['metric']['seconds'],t['metric']['serverConfirmedTcpUploadMbps'],t['metric']['softirqPercent'],t['metric']['udp']['received'],t['metric']['udp']['sent'],t['nativeRenewals']) for t in trials)
body=f'''# 监督器自身重启后从磁盘接管通过

更新：{when}，北京时间。最新NSS154；后台自有32Mbps上传＋小UDP，一健康WAN，未操作桌面/Steam/CS2。

**在ECM＝2时实际终止负责整个两代运行的监督器本身。路由器独立守护完成原20秒与恢复；新监督器从磁盘journal验证旧PID实例缺失和旧代完整恢复，再以新query/checkpoint/owner/kernel pin及两个新CI，在同socket/CT/完整mark/NAT/WAN完成下一代20秒。ECM0→2→0→2→0。**

| 代 | WAN | NSS秒 | 服务器确认上传Mbps | softirq % | UDP收/发 | 续租 |
|---|---:|---:|---:|---:|---:|---:|
{rows}

NSS153只杀控制子进程且父监督器存活；本轮杀直接执行epoch的监督器，没有单独的host epoch子控制器。外层测试harness只维持有界负载、触发精确终止和启动replacement，未代替恢复策略。新进程先验证checkpoint/receipt/journal哈希、原进程实例缺失、原CI/双向tag和独立恢复，再进入正常新代；原gate不重开、不强续。未测试路由器重启，未永久安装NSS服务。

1795个实际绑定及冻结副本匹配，native149 factory、常驻68分类器和内核gate不变；每代新checkpoint下载SHA/gzip和写前PPID1独立恢复，6/27/100/client180秒和9000/65536/73728/1MiB字节不变。2个journal schema接受模型与15个损坏记录拒绝是离线检查，未声称整套factory模型。首次popen读取nil、随后版本生成误改历史依赖均在checkpoint/stage前拒绝，原失败和源码保留；读取根因未证明，独立只读复查通过；第三版本修复确切依赖并补literal/relative存在性检查。

本轮没有同负载CPU对照，降幅null，UDP echo不作CS2 jitter/loss/Miss，也不是300Mbps或长期验收。终态原完整审核source{health['queryAge']:.2f}秒，常驻68/{health['workerPid']}/{health['guardianPid']}配置不变，ECM关闭全零、无事务/stage/state/模块，两物理原mq+四fq_codel精确恢复；24个有限端点/客户端及SSH负载进程关闭。WAN4既有down和四路failover保持。仓库按用户已明确的公开偏好保持public，153及旧runtime原Git字节保存。

按用户最新授权继续至今天北京时间20:00，heartbeat已启用；19:40收尾、19:50不新开生产实验。下一步真实自有TCP flow退出与自动收敛，然后单WAN可部署有界pilot；不扩WAN/共享预算/Wi-Fi/autorate，不用游戏下载维持准备。

证据：LINKS
'''
names=[('主线','mainline'),('两代实测','trials'),('入口','qualification'),('失败','failures'),('终态','final-audit'),('队列','physical-final'),('端点','endpoint-client-closure')]
for file in ['AGENTS.md','docs/STATE.md','docs/PLAN.md','docs/EXPERIMENT_LOG.md']:
    p=repo/file;prefix='../' if file.startswith('docs/') else '';links='、'.join(f'[{label}]({prefix}evidence/nss154-{name}.json)' for label,name in names);p.write_text(body.replace('LINKS',links)+'\n## NSS153及更早历史\n\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
p=repo/'README.md';p.write_text('# Athena NSS mainline\n\n最新[NSS154](evidence/nss154-mainline.json)：监督器自身被终止后，新进程从磁盘journal验证独立恢复并完成同连接新代重学。继续至20:00；先读[STATE](docs/STATE.md)。\n\n## NSS153及更早历史\n\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
page='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>NSS154 监督器重启接管</title><style>body{font:16px/1.8 system-ui;max-width:960px;margin:40px auto;padding:24px;color:#182638;background:#f3f5f7}pre{white-space:pre-wrap;background:white;padding:25px}a{color:#1761a2}</style><body><h1>NSS154 · 监督器自身重启接管通过</h1><pre>'+body.replace('LINKS','源码与脱敏证据见GitHub STATE').replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')+'</pre><p><a href="https://github.com/ZyPulse-zy/athena-nss-mainline/blob/main/docs/STATE.md">GitHub STATE</a></p></body></html>'
output=w/'outputs/nss154-mainline-report.html';assert not output.exists();output.write_text(page,encoding='utf-8');(repo/'reports/nss154-mainline-report.html').write_text(page,encoding='utf-8')
put(r/'reporting/export-receipt.json',{'passed':True,'sourcesAdded':len(sources),'sourceTotal':len(manifest['sources']),'old153RuntimeGitBytesPreserved':True,'privateInputsExcluded':True})
print(json.dumps({'passed':True,'sourcesAdded':len(sources),'sourcesTotal':len(manifest['sources']),'completedEpochs':2,'supervisorItselfRestartProved':True}))
