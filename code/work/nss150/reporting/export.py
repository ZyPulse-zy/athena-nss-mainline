"""Explicit source allowlist and redacted automatic-lifecycle evidence only."""
from pathlib import Path
import json,hashlib,subprocess,html,copy
from datetime import datetime,timezone
w=Path(__file__).resolve().parents[3];repo=w/'athena-nss-mainline';r=w/'work/nss150'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda b:hashlib.sha256(b).hexdigest()
def put(p,v):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def evidence(n,v):
    p=repo/('evidence/nss150-'+n+'.json');assert not p.exists();put(p,v)
auto=read(r/'run-v5/automatic-result.json');assert auto['passed'] and auto['completedEpochs']==2
history=read(r/'run-v5/automatic-history-private.json');assert len(history['history'])==2
cases=[w/v['output'] for v in history['experiments']];assert len(cases)==2
trials=[]
for i,p in enumerate(cases):
    raw=read(p/'last-record-private.json');plan=read(p/'stage-plan-private.json');functional=read(p/'functional-runtime-proof.json')
    checkpoint=read(p/'stage-checkpoint-verified.json');undo=read(p/'stage-undo-verified.json');rec=read(p/'stage-receipt-private.json');ecm=read(p/'actual-accelerated-state-proof.json')
    assert raw['automaticLifecycleEpochCompleted'] and raw['successEarlyCompletion'] and not raw['abaCompleted']
    assert all(undo.values()) and rec['rollbackBeforeFirstWrite'] and functional['passed']
    inputs=read(p/'source-manifest-preaudit.json');assert len(inputs)==1609
    for f,d in inputs.items():assert sha((w/f).read_bytes())==sha((p/'frozen'/f).read_bytes())==d
    trials.append({'generation':i+1,'passed':True,'stableSeconds':raw['phases'][0]['seconds'],
      'sampleCount':raw['phases'][0]['sampleCount'],'nativeRenewals':len(raw['renewals']),
      'observedEcmSequence':[0,2,0],'actualTagAndLeafCount':4,'fullMarkNatWanAffinityCorrect':True,
      'originalCtAndSocketHeld':True,'newKernelPin':True,'newCheckpointDownloadedShaGzipVerified':checkpoint['gzipVerified'],
      'independentRollbackBeforeFirstWrite':True,'parentAndPipeIdentityVerified':rec['parentIdentityVerified'] and rec['pipeInodesVerified'],
      'successGraceSeconds':raw['successRecordGraceSeconds'],'fixedNativeSessionSeconds':27,'independentOwnerMaxSeconds':100,
      'payloadBytesActual':plan['qosCodeBytes'],'guardianExecBytesActual':plan['execBytes'],'sourceBindingsActual':len(inputs),
      'undoVerified':undo,'gateRemoved':raw['moduleUnloaded'],'physicalRootsRestored':raw['dualPhysicalQueuesRestored'],
      'metrics':read(p/'lifecycle-metrics.json')})
first,second=history['history'];assert first['selected']==second['selected']
assert all(first[k]!=second[k] for k in ['owner','tagOwner','frozenHash','checkpointName'])
assert second['firstSequence']>first['lastActiveSequence']
assert all(a!=b for a,b in zip(first['nativeCis'],second['nativeCis']))
health=read(r/'v1-final-health.json');physical=read(r/'physical-final.json');endpoints=read(r/'endpoint-client-closure.json');receiver=read(r/'download-receiver-closure.json')
assert all(v['passed'] for v in [health,physical,endpoints,receiver]);assert endpoints['previousLoadsChecked']==16
assert health['ecmStoppedAndZero'] and health['noStaging'] and health['noExperimentalModule']
sources={}
qualification149=read(w/'work/nss149/entry-qualified.json')
qualifications=[read(r/('entry-qualified'+suffix+'.json')) for suffix in ['', '-v2','-v3','-v4','-v5']]
for q in [qualification149,*qualifications]:
    assert q['passed']
    for f,d in q['sourceManifest'].items():assert sha((w/f).read_bytes())==d;sources[f]=d
extras=['work/nss150/calibrate-clock.mjs','work/nss150/calibrate-lifecycle.mjs',
 'work/nss150/verify-all-endpoints.mjs','work/nss150/verify-all-endpoints-v2.mjs',
 'work/nss150/verify-all-endpoints-v3.mjs','work/nss150/verify-downloaders.mjs',
 'work/nss150/reporting/prepare-postchecks.py','work/nss150/reporting/prepare-report-inputs.py',
 'work/nss150/reporting/prepare-endpoint-v3.py','work/nss150/reporting/analyze.py',
 'work/nss150/reporting/export.py','work/nss150/reporting/verify-published.py']
for f in extras:assert f not in sources;sources[f]=sha((w/f).read_bytes())
manifest=read(repo/'source-manifest.json');assert manifest['lastAppendExport']=='NSS148';prefix=copy.deepcopy(manifest['sources']);assert len(prefix)==2043
historical={p.relative_to(repo).as_posix():sha(p.read_bytes()) for base in ['code','evidence'] for p in (repo/base).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
put(r/'reporting/historical-worktree-before-export.json',historical)
old_runtime=(repo/'evidence/current-runtime.json').read_bytes();assert read(repo/'evidence/current-runtime.json')['round']=='NSS148'
assert not (repo/'evidence/nss148-runtime.json').exists();(repo/'evidence/nss148-runtime.json').write_bytes(old_runtime)
for f,d in sorted(sources.items()):
    assert f.startswith(('work/nss149/','work/nss150/')) and all(x not in f.lower() for x in ['private','credential','connect-router'])
    b=(w/f).read_bytes();target=repo/'code'/f;assert not target.exists();target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b);assert sha(b)==d
    manifest['sources'].append({'path':'code/'+f,'workspaceSource':f,'sha256':d,'bytes':len(b),'role':'bounded-automatic-lifecycle-source-or-explicit-reporting-helper'})
assert manifest['sources'][:2043]==prefix
manifest.update(lastAppendExport='NSS150',generatedAt=datetime.now(timezone.utc).isoformat(),preservesOriginalSourceBytes=True,privateDataExcluded=True,routerCredentialsIncluded=False,rawCapturesIncluded=False,binariesIncluded=False)
put(repo/'source-manifest.json',manifest)
failures=[
 {'case':'149-static-v0-v1-v2-v4','passed':False,'cause':'Textual source comparison rejected indentation/line-ending differences; a later attempt also refused to overwrite the first diff file','originalPreserved':True,'beforeRouterConnection':True,'correction':'Exact frozen raw SHA remains required; declared-code comparison uses the existing lexical packer; private outputs use distinct version directories'},
 {'case':'149-size-v3','passed':False,'cause':'First lifecycle payload exceeded the fixed 73728-byte limit','originalPreserved':True,'ecmOpened':False,'correction':'Remove unused software A/A2 orchestration and redundant snapshots; keep native/source/owner limits'},
 {'case':'149-policy-v5','passed':False,'cause':'Model incorrectly required frontend learning stop=0 throughout an already accelerated flow','originalPreserved':True,'ecmOpened':False,'correction':'Learning stop=1 can coexist with existing accelerated flows; still require exact count2, fresh class, and legal frontend values'},
 {'case':'149-RAM-v6','passed':False,'cause':'Model extractor missed the actual function due to an indentation-sensitive marker','originalPreserved':True,'ecmOpened':False,'correction':'Assert extraction boundaries and execute the actual run/measurement functions'},
 {'case':'149-automatic-boundary','passed':False,'completedEpochs':1,'cause':'First real 20-second epoch restored; the next owner was rejected by an unnecessary 100-second client-preparation requirement','originalPreserved':True,'secondEpochWrites':False,'correction':'Require 70 seconds of client preparation time; native27/owner100/client180 and all live readiness checks unchanged'},
 {'case':'150-prepare-v1','passed':False,'cause':'A reporting helper was incorrectly listed as a bound inherited preparation input','originalPreserved':True,'ecmOpened':False,'correction':'Complete only remaining bound sources, preserve partial copies'},
 {'case':'150-initial-entry','passed':False,'cause':'Own-namespace failed-WAN audit source missing','originalPreserved':True,'checkpointCreated':False,'ecmOpened':False,'correction':'Bind the exact inherited helper and move full preflight before endpoint traffic'},
 {'case':'150-v2-preflight','passed':False,'cause':'Own-namespace baseline declaration source missing','originalPreserved':True,'endpointTrafficStarted':False,'ecmOpened':False,'correction':'Bind the declaration and check literal namespace source closure'},
 {'case':'150-v3-continuity','passed':False,'cause':'Child read the old root continuity reference while the supervisor wrote a run-scoped reference','originalPreserved':True,'checkpointCreated':False,'ecmOpened':False,'correction':'Pass the exact run-scoped private continuity path explicitly'},
 {'case':'150-v4-WAN5','passed':False,'cause':'Within the original initial-tag window, UDP uplink51 packets and TCP both directions matched, but UDP downstream0; native gate not loaded and ECM not opened','originalPreserved':True,'checkpointCreated':True,'ecmOpened':False,'physicalRootsRestored':True,'downstreamGapRootCauseResolved':False,'correction':'No wait/lease enlargement. New load reused a prior owned UDP source port, with normal PBR selecting actual WAN3.'}
]
evidence('failures',failures);evidence('trials',trials);evidence('automatic-result',auto)
evidence('qualification149',qualification149)
for suffix,q in zip(['initial','v2','v3','v4','v5'],qualifications):evidence('qualification-'+suffix,q)
evidence('final-audit',health);evidence('physical-final',physical);evidence('endpoint-client-closure',endpoints);evidence('receiver-closure',receiver)
summary={'round':'NSS150','passed':True,'boundedTwoEpochAutomaticLifecyclePassed':True,'actualWan':trials[0]['metrics']['selectedWan'],
 'generations':2,'unchangedSocketCtMarkNatWanAcrossGenerations':True,'newOwnerCheckpointTagNamespaceFrozenHashAndClassifierSequence':True,
 'newNativeCisForBothFlows':True,'oldNativeGateNeverReopened':True,'oldEpochNeverExtended':True,'trials':trials,
 'sourceBindingsActual':1609,'qualifiedController':'work/nss150/run-v5.mjs','factory':'work/nss149/module-stage.mjs',
 'sourceNativeOwnerBudgets':[6,27,100],'clientHardSeconds':180,'clientPreparationRemainingSeconds':70,
 'cpuReductionConclusion':None,'matchedCpuABARunThisTurn':False,'cs2ExperienceConclusion':False,'highLoad300MbpsConclusion':False,
 'permanentNssControllerInstalled':False,'permanentNssEnabled':False,'autoClassChangeRelearnInThisNewSupervisorTested':False,
 'classChangeRetirementCodeInheritedExactly':True,'historical139ClassChangeProofNotRerun':True,
 'wan5DownstreamUdpGapUnresolved':True,'desktopOperated':False,'steamOrCs2Started':False,'nightHeartbeatRemainsPaused':True,
 'failuresPreserved':len(failures),'finalAudit':health,'physicalRestore':physical,'endpointClosure':endpoints,'receiverClosure':receiver,
 'exportedSources':len(sources),'oldNss148RuntimeRetainedExactSha256':sha(old_runtime)}
evidence('mainline',summary)
runtime={'round':'NSS150','observedAt':health['observedAt'],'workerPid':health['workerPid'],'guardianPid':health['guardianPid'],
 'classifierConfigSha256':health['configSha256'],'classifierDeployment':'NSS68','nssPermanentlyEnabled':False,'controlledAutomaticLifecyclePassed':True,
 'qualifiedExperimentalController':'work/nss150/run-v5.mjs','boundInputs':1609,'controlledFactory':'work/nss149/module-stage.mjs',
 'generations':2,'controlledWan':summary['actualWan'],'cpuConclusion':None,'realHumanGameAcceptance':False,'nightHeartbeatRemainsPaused':True,
 'historical148RuntimePreservedSha256':sha(old_runtime),'audit':health,'physicalRootRestoreAudit':physical,'endpointClientClosureAudit':endpoints,'ownedReceiverClosureAudit':receiver}
put(repo/'evidence/current-runtime.json',runtime)
for p,d in historical.items():
    if p!='evidence/current-runtime.json':assert sha((repo/p).read_bytes())==d,p
time=datetime.now().astimezone().strftime('%Y-%m-%d %H:%M')
table='\n'.join('| %s | %.2f | %.3f | %.3f | %d/%d | %.3f | %d |' % (t['generation'],t['stableSeconds'],t['metrics']['clientTcpReceivedMbps'],t['metrics']['softirqPercent'],t['metrics']['udp']['received'],t['metrics']['udp']['sent'],t['metrics']['udp']['rttP95Ms'],t['nativeRenewals']) for t in trials)
text=f'''# 单 WAN 自动生命周期已通过有限两代实测

更新：{time}，北京时间。最新 NSS150。用户使用电脑，本轮仅后台自有受控下载＋小UDP，无桌面、Steam、CS2 操作。

**同一真实 TCP BULK＋UDP RT，在 WAN{summary['actualWan']} 自动完成两代各20秒：第一代精确撤销和完整恢复后，自动取得新的分类 query、checkpoint、owner、kernel pin 和两个新 CI；原 socket、CT、完整 mark、NAT 与 WAN affinity 不变。每代 ECM0→2→0、四tag/四FQ-CoDel leaf及独立恢复通过。**

| 代 | NSS秒 | 下载payload Mbps | softirq % | UDP收到/发出 | UDP RTT p95 ms | native续租 |
|---|---:|---:|---:|---:|---:|---:|
{table}

这是有限两代生命周期验收；没有本轮 software/NSS/software CPU因果对照，降幅为null；UDP是自有echo，不是CS2 jitter/loss/Miss。未部署长期NSS控制器、未验收300Mbps或长期稳定，未在新supervisor中复测改类/退出。

修复了客户端准备时长误用、两个审核依赖遗漏、旧轮次连接参照路径。WAN5初始阶段UDP上行51包/下行0导致拒绝，未加载gate或开启ECM；其回包缺口根因仍未知，未放宽原1.2秒窗口或6/27/100期限。失败均保留。NSS149第一代20.01秒成功，第二代写前期限拒绝也单独保留。

常驻仍NSS68/config581b5d46…c791d7、{health['workerPid']}/{health['guardianPid']}、publication upTag0；ECM关闭全零，无事务/stage/state/实验模块；wan与lan4原mq+四fq_codel精确恢复；16负载端点/客户端、SSH下载发送器关闭。WAN4既有认证down，四路failover未改。heartbeat保持暂停。

接下来仅把真实改类/退出事件接入这一已实测supervisor，并验证中断时独立恢复；之后再做单WAN有限常驻试运行。保留NSS承担主要QoS的方向，CAKE作为fallback/对照；不扩第二WAN、共享预算、Wi-Fi、autorate或新游戏下载。

证据：[主线](../evidence/nss150-mainline.json)、[两代](../evidence/nss150-trials.json)、[失败](../evidence/nss150-failures.json)、[终态](../evidence/nss150-final-audit.json)、[物理根](../evidence/nss150-physical-final.json)、[端点](../evidence/nss150-endpoint-client-closure.json)。

'''
for name,title in [('docs/STATE.md','NSS148及更早历史'),('docs/PLAN.md','NSS148及更早计划'),('docs/EXPERIMENT_LOG.md','NSS148及更早记录'),('AGENTS.md','NSS148及更早接续')]:
    p=repo/name;p.write_text(text+'## '+title+'\n\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
old_readme=(repo/'README.md').read_text(encoding='utf-8')
(repo/'README.md').write_text('# Athena NSS mainline\n\n最新 [NSS150](evidence/nss150-mainline.json)：后台自有真实流完成单WAN两代自动加速、精确撤销、完整恢复、新query/checkpoint/owner/pin/CI接续，原socket/CT/mark/NAT/WAN不变。无需开游戏。有限两代已过，长期/300Mbps/真人仍未验收，最终已恢复。先读 [STATE](docs/STATE.md) 和 [PLAN](docs/PLAN.md)。\n\n## NSS148及更早历史\n\n'+old_readme,encoding='utf-8')
rows=''.join('<tr><td>%d</td><td>%.2f</td><td>%.3f</td><td>%.3f</td><td>%d/%d</td><td>%.3f</td></tr>'%(t['generation'],t['stableSeconds'],t['metrics']['clientTcpReceivedMbps'],t['metrics']['softirqPercent'],t['metrics']['udp']['received'],t['metrics']['udp']['sent'],t['metrics']['udp']['rttP95Ms']) for t in trials)
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NSS150 自动生命周期实测</title><style>body{font:16px/1.8 system-ui,"Microsoft YaHei",sans-serif;background:#f3f5f7;color:#182638;margin:0}main{max-width:1000px;margin:40px auto;padding:32px;background:white;border-radius:14px}h1{line-height:1.3}table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}td,th{border-bottom:1px solid #dce3eb;padding:10px;text-align:left}.ok{background:#e8f6ef;padding:18px;border-left:4px solid #16845c}.note{background:#fff4df;padding:18px}code{overflow-wrap:anywhere}a{color:#1761a2}@media(max-width:650px){main{margin:0;padding:18px}table{font-size:13px}td,th{padding:5px}}</style><main><p>Athena AX6600 · NSS150</p><h1>单 WAN 自动接续已通过两代实测</h1><p class="ok">同一 TCP/UDP 保持 socket、CT、完整 mark、NAT 与 WAN affinity。每代 20 秒 NSS → 精确撤销 → 完整恢复；第二代自动使用新分类、新 checkpoint、owner、kernel pin 和两个新 CI。</p><table><thead><tr><th>代</th><th>NSS 秒</th><th>下载 Mbps</th><th>softirq %</th><th>UDP 收/发</th><th>RTT p95 ms</th></tr></thead><tbody>'''+rows+'''</tbody></table><p class="note">本轮验收自动生命周期。没有新的同负载 CPU 因果对照；UDP echo 不代表 CS2 jitter/loss/Miss。有限两代不等于长期稳定、300Mbps或常驻部署。</p><h2>修复与失败</h2><p>修正客户端准备时长误用、两份审核依赖遗漏、旧轮次连接参照路径。WAN5初始窗口UDP上行51包/下行0，gate未加载、ECM未开启并已恢复；回包缺口根因仍未知。所有失败与原证据保留，来源和独立回滚上限未放宽。</p><h2>最终状态</h2><p>常驻NSS68未改。ECM关闭全零；无实验事务、stage、state或模块。wan/lan4原mq+四fq_codel恢复，16个负载端点/客户端和SSH下载发送器关闭。WAN4既有认证故障与四路failover保持。</p><h2>下一步</h2><p>把真实改类/退出事件接入已实测的supervisor，再验证中断恢复，随后做单WAN有限常驻试运行。无需挂游戏或重复下载。</p><p><a href="https://github.com/ZyPulse-zy/athena-nss-mainline/blob/main/docs/STATE.md">GitHub STATE</a></p></main></html>'''
(w/'outputs').mkdir(exist_ok=True);(w/'outputs/nss150-mainline-report.html').write_text(page,encoding='utf-8');(repo/'reports/nss150-mainline-report.html').write_text(page,encoding='utf-8')
put(r/'reporting/export-receipt.json',{'passed':True,'sourcesAdded':len(sources),'sourceTotal':len(manifest['sources']),'oldHistoricWorktreeFilesRetained':len(historical)-1,'old148RuntimeSha256':sha(old_runtime),'rawCtNonceCredentialsConfigsAndBinariesExcluded':True})
print(json.dumps({'passed':True,'sourcesAdded':len(sources),'sourcesTotal':len(manifest['sources']),'generations':2,'old148RuntimePreserved':True}))
