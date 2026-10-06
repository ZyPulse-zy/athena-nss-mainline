"""Publish only new allowlisted sources and redacted runtime assertions."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib,subprocess,copy,html
w=Path(__file__).resolve().parents[3];r=w/'work/nss153';repo=w/'athena-nss-mainline';base='81017d2c962712cb2d11817020436a7b9faa5238'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda b:hashlib.sha256(b).hexdigest()
def put(p,v):
    assert not p.exists(),str(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def ev(n,v):put(repo/f'evidence/nss153-{n}.json',v)
q=read(r/'entry-qualified.json');actual=read(r/'entry-source-manifest.json');assert q['passed'] and q['inheritedBindings']==1725 and len(actual)==1752
for f,d in actual.items():assert sha((w/f).read_bytes())==sha((r/'frozen-qualified-inputs'/f).read_bytes())==d
a=read(r/'run1/automatic-result.json');hist=read(r/'run1/history-private.json');assert a['passed'] and a['completedEpochs']==len(hist['history'])==len(hist['cases'])==2
first,second=hist['history'];assert first['childNormalReceiptAbsent'] and first['proofOrigin']=='independent-parent-recovery-assessment'
assert first['selected']==second['selected'] and first['boot']==second['boot'] and first['producer']==second['producer']
for k in ['owner','tagOwner','frozenHash','checkpointName']:assert first[k]!=second[k]
assert second['firstSequence']>first['lastActiveSequence'] and all(x!=y for x,y in zip(first['nativeCis'],second['nativeCis']))
crash=read(r/'run1/controller-crash-private.json');assert crash['passed'] and crash['exitCode'] is None and crash['terminationSignal']=='SIGTERM' and crash['ownedKillReturnedTrue']
assert crash['ownedSpawnProcessOnly'] and crash['routerGuardianNotKilled'] and crash['controllerCleanupNotExecuted'] and crash['identity']['pid']==crash['pid']
first_dir=w/hist['cases'][0];assert not (first_dir/'result.json').exists()
health=read(r/'v1-final-health.json');physical=read(r/'physical-final.json');endpoints=read(r/'endpoint-client-closure.json');recv=read(r/'receiver-closure.json');down=read(r/'download-receiver-closure.json')
assert all(v['passed'] for v in [health,physical,endpoints,recv,down])
assert health['ecmStoppedAndZero'] and health['queryAge']<6 and health['noStaging'] and health['noExperimentState'] and health['noExperimentalModule']
assert endpoints['previousLoadsChecked']==endpoints['ownedUnitsInactiveMainPidZero']==21 and endpoints['ownedClientOrGuardProcessesRemaining']==0
assert recv['exactOwnedReceiverAndTimeoutProcessesRemaining']==down['exactOwnedReceiverAndTimeoutProcessesRemaining']==0
trials=[]
for i,folder in enumerate(hist['cases']):
    p=w/folder;record=read(p/('crash-last-record-private.json' if i==0 else 'last-record-private.json'));plan=read(p/'stage-plan-private.json');cp=read(p/'stage-checkpoint-verified.json');undo=read(p/'stage-undo-verified.json');receipt=read(p/'stage-receipt-private.json');detached=read(p/'stage-detached-private.json');inputs=read(p/'source-manifest-preaudit.json');metric=read(p/'lifecycle-metrics.json')
    assert len(inputs)==1752 and all(undo.values()) and cp['gzipVerified'] and receipt['rollbackBeforeFirstWrite'] and receipt['pipeInodesVerified'] and receipt['parentIdentityVerified'] and detached['identity']['ppid']==1
    for f,d in inputs.items():assert sha((w/f).read_bytes())==sha((p/'frozen'/f).read_bytes())==d
    assert record.get('error') is None and record['firmwareZeroAfterRetirement'] and record['dualPhysicalQueuesRestored'] and record['automaticLifecycleEpochCompleted']
    assert plan['qosCodeBytes']<=73728 and plan['execBytes']<=9000
    assert metric['direction']=='upload' and metric['tcpMetric']=='server-confirmed received bytes' and metric['causalCpuReductionPercent'] is None and not metric['cs2Acceptance']
    trials.append({'generation':i+1,'test':'owned-child-controller-crash-independent-completion' if i==0 else 'automatic-successor-after-child-crash', 'passed':True,'wan':plan['selected']['tcp']['wan'],'observedEcmSequence':[0,2,0],'fourTagsFourFqCodelLeaves':True,'completeClassCtMarkNatWanAffinityCorrect':True,'sourceBindingsActual':1752,'payloadBytesActual':plan['qosCodeBytes'],'guardianExecBytesActual':plan['execBytes'],'checkpointDownloadedShaGzipVerified':True,'rollbackBeforeFirstWrite':True,'detachedParentPidOne':True,'nativeHardSeconds':27,'ownerMaxSeconds':100,'nativeRenewals':len(record['renewals']),'fullyRestored':True,'undo':undo,'metric':metric,'hostNormalCompletionReceiptPresent':i==1})
assert trials[0]['wan']==trials[1]['wan']
visibility=read(r/'repository-public-corrected.json');assert visibility['passed'] and visibility['afterVisibility']=='public' and visibility['correctedNss152VisibilityMistake']
sources=dict(q['sourceManifest'])
extras=['prepare-postchecks.py','health.mjs','read-final-physical.mjs','verify-all-endpoints.mjs','verify-receivers.mjs','verify-downloaders.mjs','calibrate-clock.mjs','analyze.py','restore-public.py','reporting/export.py','reporting/verify-published.py']
for n in extras:sources['work/nss153/'+n]=sha((r/n).read_bytes())
for n in ['supervisor.mjs','recovery-policy.mjs','policy-checks.mjs','qualify.mjs']:sources['work/nss153/prequalification-v1/'+n]=sha((r/'prequalification-v1'/n).read_bytes())
for f,d in sources.items():assert sha((w/f).read_bytes())==d and f.startswith('work/nss153/') and f.endswith(('.mjs','.py','.ps1','.lua')) and all(x not in f.lower() for x in ['private','credential','connect-router'])
manifest=read(repo/'source-manifest.json');prefix=copy.deepcopy(manifest['sources']);assert len(prefix)==2275 and manifest['lastAppendExport']=='NSS152'
oldruntime=subprocess.check_output(['git','show',base+':evidence/current-runtime.json'],cwd=repo);assert read(repo/'evidence/current-runtime.json')['round']=='NSS152'
assert not (repo/'evidence/nss152-runtime.json').exists()
failures=[{'case':'prepare-v1','cause':'Optional nonexistent client.mjs/client-guard.ps1 copied before dependency inventory; partial output preserved'}, {'case':'prepare-v2','cause':'Optional non-SSH client.py also absent; the initial diagnostic filename suggestion was invalid; exact refused branch retained'}, {'case':'parent-policy-v1','cause':'Legacy Windows child close code was null without an explicit signal; new controller now records code, signal and kill-return observation; legacy missing-signal receipt is refused'}, {'case':'qualifier-v1','cause':'Fresh SSH client namespace omitted its bounded-pacer dependency; refused before connection and dependency copied with exact qualified bytes'}]
for f in failures:f.update(passed=False,originalPreserved=True,beforeConnectionAndProductionWrites=True,notKernelOrNssFirmwareFailure=True)
proof={'passed':True,'historicPrefixSources':2275,'historicPrefixCanonicalSha256':sha(json.dumps(prefix,sort_keys=True,separators=(',',':')).encode()),'historicManifestPrefixUnchanged':True,'sources':len(sources),'sourceHashes':sources,'actualBindings':1752,'privateCapabilityInputsBoundLocally':3,'privateCapabilityInputContentsExcluded':True,'originalRefusalSourcesKept':True,'nativeFactoryUnchanged':149,'permanentClassifierAndKernelGateUnchanged':True}
# Repository mutation starts after all runtime/source/evidence checks above.
(repo/'evidence/nss152-runtime.json').write_bytes(oldruntime)
for f,d in sorted(sources.items()):
    p=repo/'code'/f;assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True);b=(w/f).read_bytes();p.write_bytes(b)
    manifest['sources'].append({'path':'code/'+f,'workspaceSource':f,'sha256':d,'bytes':len(b),'role':'finite-child-crash-automatic-recovery-or-explicit-reporting'})
assert manifest['sources'][:2275]==prefix
manifest.update(lastAppendExport='NSS153',generatedAt=datetime.now(timezone.utc).isoformat(),privateDataExcluded=True,preservesOriginalSourceBytes=True)
(repo/'source-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for n,v in [('source-proof',proof),('qualification',q),('automatic-result',a),('trials',trials),('failures',failures),('repository-visibility-correction',visibility),('final-audit',health),('physical-final',physical),('endpoint-client-closure',endpoints),('receiver-closure',recv),('download-receiver-closure',down)]:ev(n,v)
main={'round':'NSS153','passed':True,'observedAt':health['observedAt'],'actualChildControllerCrashThenAutomaticRelearning':True,'sameSocketCtMarkNatWanInSuccessor':True,'newQueryCheckpointOwnerKernelPinAndBothCis':True,'oldTerminalGateNeverReopened':True,'completedEpochs':2,'controllerActuallyTerminatedDuringEcm2':True,'routerGuardianNotKilled':True,'parentSupervisorStayedAlive':True,'routerRebootOrParentSupervisorCrashTested':False,'qualifiedController':'work/nss153/supervisor.mjs','boundInputs':1752,'trials':trials,'nativeFactoryUnchanged':149,'sourceNativeOwnerSeconds':[6,27,100],'clientHardSeconds':180,'execRawBundleRecordBytes':[9000,65536,73728,1048576],'matchedCpuComparison':False,'cpuReductionConclusion':None,'realHumanGameAcceptance':False,'highLoad300MbpsAcceptance':False,'permanentNssControllerInstalled':False,'nssPermanentlyEnabled':False,'desktopOperated':False,'steamOrCs2Started':False,'nightHeartbeatRemainsPaused':True,'repositoryVisibilityCorrectedToUserRequestedPublic':True,'failuresPreserved':len(failures),'exportedSources':len(sources),'old152RuntimeRetainedSha256':sha(oldruntime),'finalAudit':health,'physicalRestore':physical,'endpointClosure':endpoints,'receiverClosure':recv,'downloadReceiverClosure':down}
ev('mainline',main)
runtime={'round':'NSS153','observedAt':health['observedAt'],'workerPid':health['workerPid'],'guardianPid':health['guardianPid'],'classifierConfigSha256':health['configSha256'],'classifierDeployment':'NSS68','qualifiedExperimentalController':main['qualifiedController'],'boundInputs':1752,'actualChildControllerCrashThenAutomaticRelearning':True,'completedEpochs':2,'nssPermanentlyEnabled':False,'permanentNssControllerInstalled':False,'cpuConclusion':None,'realHumanGameAcceptance':False,'nightHeartbeatRemainsPaused':True,'historical152RuntimePreservedSha256':sha(oldruntime),'audit':health,'physicalRootRestoreAudit':physical,'endpointClientClosureAudit':endpoints,'ownedReceiverClosureAudit':recv,'ownedDownloadReceiverClosureAudit':down,'repositoryVisibility':'public'}
(repo/'evidence/current-runtime.json').write_text(json.dumps(runtime,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
when=datetime.fromisoformat(health['observedAt'].replace('Z','+00:00')).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
rows='\n'.join('| %d | %d | %.2f | %.3f | %.3f | %d/%d | %d |'%(t['generation'],t['wan'],t['metric']['seconds'],t['metric']['serverConfirmedTcpUploadMbps'],t['metric']['softirqPercent'],t['metric']['udp']['received'],t['metric']['udp']['sent'],t['nativeRenewals']) for t in trials)
body=f'''# 控制子进程中断后自动新代重学通过

更新：{when}，北京时间。最新 NSS153。用户不用电脑，直接以后台自有32Mbps上传＋小UDP完成单WAN测试；没有桌面、Steam、CS2操作。

**WAN{trials[0]['wan']}同一TCP BULK＋UDP RT：ECM=2时实际终止精确自有PC控制子进程，路由器独立守护继续20秒并恢复；仍在运行的父监督器自动取得新分类query/checkpoint/owner/kernel pin和两个新CI，同socket/CT/完整mark/NAT/WAN完成第二代20秒并恢复。ECM0→2→0→2→0。**

| 代 | WAN | NSS秒 | 服务器确认上传Mbps | softirq % | UDP收/发 | native续租 |
|---|---:|---:|---:|---:|---:|---:|
{rows}

这是有限两代控制子进程中断接管证明。父监督器未被杀，未测试路由器重启；未长期安装NSS服务，未验收300Mbps或真人CS2。没有本轮software/NSS/software CPU因果对照，降幅null；UDP echo不是CS2 jitter/loss/Miss。CAKE仅作为未加速流fallback/对照，NSS主数据面QoS方向保持。

1752个实际入口绑定及冻结副本匹配；每代都有新checkpoint下载SHA/gzip与写前PPID1独立恢复，原149factory/常驻分类器/内核gate不变。6/27/100/client180秒、9000/65536/73728/1MiB字节不变。控制终止同时记录null退出码和SIGTERM信号；缺显式信号的历史记录在新政策中拒绝。14个新增拒绝检查与模型终止字段上的历史native记录重放只是离线政策检查，不是整个factory模型或新硬件证据。四项本地生成/政策/依赖拒绝原样保留。

终态原完整审核source{health['queryAge']:.2f}秒，常驻NSS68/config581b5d46…c791d7、{health['workerPid']}/{health['guardianPid']}；ECM关闭全零，无事务/stage/state/模块，wan与lan4原mq+四fq_codel精确恢复。全部21个有限端点/客户端及自有SSH负载进程关闭。WAN4既有认证down和四路failover保持，heartbeat仍暂停。

仓库设置纠正：用户在2026-10-05另一聊天已明确要求此仓库公开；NSS152按旧“私有仓库”说明改回private是误操作。本轮核验owner/admin后只恢复public，其它检查设置不变。旧NSS152实际操作收据保留，以本纠正为当前意图和状态。凭据、完整CT/nonce/配置/checkpoint/二进制仍不加入Git。

下一步把有限监督器收敛为单WAN可部署pilot，先处理监督器自身restart和受控流退出，再决定有界较长运行；不扩第二WAN/共享预算/Wi-Fi/autorate，不重复下载和真人准备。

证据：LINKS
'''
names=[('主线','mainline'),('两代实测','trials'),('入口','qualification'),('失败','failures'),('终态','final-audit'),('队列','physical-final'),('端点','endpoint-client-closure'),('仓库设置纠正','repository-visibility-correction')]
for file in ['AGENTS.md','docs/STATE.md','docs/PLAN.md','docs/EXPERIMENT_LOG.md']:
    p=repo/file;prefix='../' if file.startswith('docs/') else '';links='、'.join(f'[{label}]({prefix}evidence/nss153-{name}.json)' for label,name in names);p.write_text(body.replace('LINKS',links)+'\n## NSS152及更早历史\n\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
p=repo/'README.md';p.write_text('# Athena NSS mainline\n\n最新[NSS153](evidence/nss153-mainline.json)：自有控制子进程中断后，独立恢复及同连接自动新代重学通过；单WAN有限两代，所有实验已撤销。仓库按用户最新设置要求恢复public。先读[STATE](docs/STATE.md)与[PLAN](docs/PLAN.md)。\n\n## NSS152及更早历史\n\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
table=''.join('<tr><td>%d</td><td>%d</td><td>%.2f</td><td>%.3f</td><td>%.3f</td><td>%d/%d</td><td>%d</td></tr>'%(t['generation'],t['wan'],t['metric']['seconds'],t['metric']['serverConfirmedTcpUploadMbps'],t['metric']['softirqPercent'],t['metric']['udp']['received'],t['metric']['udp']['sent'],t['nativeRenewals']) for t in trials)
page='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NSS153 控制中断后自动重学</title><style>body{font:16px/1.8 system-ui,"Microsoft YaHei",sans-serif;background:#f3f5f7;color:#182638;margin:0}main{max-width:960px;margin:35px auto;padding:30px;background:white;border-radius:14px}table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}td,th{border-bottom:1px solid #dce3eb;padding:9px;text-align:left}.ok{background:#e8f6ef;padding:18px;border-left:4px solid #16845c}.note{background:#fff4df;padding:18px}a{color:#1761a2}@media(max-width:650px){main{margin:0;padding:16px}table{font-size:12px}td,th{padding:4px}}</style></head><body><main><p>Athena AX6600 · NSS153</p><h1>控制子进程中断后自动恢复和新代重学通过</h1><p class="ok">ECM＝2时终止精确自有PC控制子进程 → 路由器独立守护继续20秒、续租与精确恢复 → 父监督器自动以新query/checkpoint/owner/kernel pin和两个新CI，在同socket/CT/mark/NAT/WAN完成第二代20秒。ECM 0→2→0→2→0。</p><table><thead><tr><th>代</th><th>WAN</th><th>秒</th><th>上传Mbps</th><th>softirq %</th><th>UDP收/发</th><th>续租</th></tr></thead><tbody>'''+table+'''</tbody></table><p class="note">有限两代实际接管；父监督器未被杀，未测试路由器重启，未长期部署或验收300Mbps/真人CS2。没有本轮CPU因果对照，UDP echo不能代表CS2 loss/jitter/Miss。</p><h2>终态</h2><p>ECM关闭全零，无事务、stage、state或实验模块；两个物理根恢复，21个有限端点/客户端和自有SSH负载进程关闭。常驻分类器、完整PBR/ct mark/NAT/WAN affinity和四路failover保持。</p><h2>检查与纠正</h2><p>1752项实际绑定。每代新checkpoint和控制连接外PPID1独立恢复；原分类器/内核gate/149 factory和6/27/100/180秒及字节上限不变。本地生成/政策/依赖拒绝均保存。Windows终止信号实际记录，null退出码单独不授权恢复。仓库按用户已明确的公开要求恢复public，纠正NSS152误用旧说明造成的private设置，旧收据保留。</p><h2>下一步</h2><p>收敛单WAN可部署pilot，处理父监督器restart和受控流退出，再做有界较长运行。暂不扩WAN/共享预算/Wi-Fi/autorate。</p><p><a href="https://github.com/ZyPulse-zy/athena-nss-mainline/blob/main/docs/STATE.md">GitHub STATE</a></p></main></body></html>'''
out=w/'outputs/nss153-mainline-report.html';assert not out.exists();out.write_text(page,encoding='utf-8');(repo/'reports/nss153-mainline-report.html').write_text(page,encoding='utf-8')
put(r/'reporting/export-receipt.json',{'passed':True,'sourcesAdded':len(sources),'sourceTotal':len(manifest['sources']),'old152RuntimeGitBytesPreserved':True,'rawCtNoncesCredentialsCheckpointsBinariesExcluded':True})
print(json.dumps({'passed':True,'sourcesAdded':len(sources),'sourcesTotal':len(manifest['sources']),'completedEpochs':2,'old152RuntimePreserved':True}))
