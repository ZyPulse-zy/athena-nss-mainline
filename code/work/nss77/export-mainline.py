"""Append reviewed NSS69-77 sources and curated facts; preserve historical bytes."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, re, shutil, html

ws=Path(__file__).resolve().parents[2];repo=ws/'athena-nss-mainline'
read=lambda p:json.loads((ws/p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
def write(p,t):p.write_text(t,encoding='utf-8',newline='\n')

allowed={
69:'build-closed-wait.mjs build-entry.mjs client-watchdog.ps1 core-guard-phase.lua current-audit-diagnostic.mjs diagnose-payload.mjs module-stage.mjs qualify-phase.mjs read-real-candidates.mjs real-session.mjs record-candidates.mjs session-binding.mjs stat-eof-fixtures.lua phase-qualified.json entry-qualified.json',
70:'build-reserve.mjs client-watchdog-900.ps1 client-watchdog.ps1 current-audit-diagnostic.mjs fast-path.lua module-stage.mjs payload.mjs qualify-closed-wait.mjs read-real-candidates.mjs real-session.mjs record-candidates.mjs session-binding.mjs closed-wait-qualified.json change-contract.json entry-qualified.json',
71:'build-validity.mjs classifier.lua current-audit-diagnostic.mjs module-stage.mjs qualify-reserve.mjs read-real-candidates.mjs real-session.mjs record-candidates.mjs session-binding.mjs reserve-qualified.json change-contract.json entry-qualified.json',
72:'build-observation-diagnostic.mjs classifier.lua client-watchdog.ps1 current-audit-diagnostic.mjs fast-path.lua module-stage.mjs payload.mjs qualify-validity.mjs read-real-candidates.mjs real-session.mjs record-candidates.mjs session-binding.mjs validity-qualified.json change-contract.json entry-qualified.json',
73:'classifier.lua client-watchdog.ps1 current-audit-diagnostic.mjs diagnostic-helper.lua fast-path.lua module-stage.mjs payload.mjs qualify-diagnostic.mjs read-real-candidates.mjs real-session.mjs record-candidates.mjs session-binding.mjs diagnostic-qualified.json change-contract.json entry-qualified.json',
74:'build-persistent-entry.mjs client-watchdog.ps1 current-audit-diagnostic.mjs persistent-pair.mjs qualify-persistent-entry.mjs read-real-candidates.mjs real-session.mjs record-candidates.mjs session-binding.mjs change-contract.json entry-qualified.json',
75:'build-checkpoint-entry.mjs refinement.mjs qualify-checkpoint-entry.mjs module-stage.mjs real-session.mjs session-binding.mjs current-audit-diagnostic.mjs record-candidates.mjs read-real-candidates.mjs client-watchdog.ps1 change-contract.json entry-qualified.json',
76:'build-getter-order.mjs qualify-getter-order.mjs fast-path.lua payload.mjs module-stage.mjs real-session.mjs current-audit-diagnostic.mjs record-candidates.mjs read-real-candidates.mjs session-binding.mjs client-watchdog.ps1 change-contract.json entry-qualified.json',
77:'build-initial-reserve.mjs qualify-initial-reserve.mjs fast-path.lua payload.mjs module-stage.mjs real-session.mjs current-audit-diagnostic.mjs record-candidates.mjs read-real-candidates.mjs session-binding.mjs client-watchdog.ps1 change-contract.json entry-qualified.json export-mainline.py'}
manifest=json.loads((repo/'source-manifest.json').read_text(encoding='utf-8'))
assert len(manifest['sources'])==868
historic_source_sha=hashlib.sha256(json.dumps(manifest['sources'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
current=repo/'evidence/current-runtime.json';history=repo/'evidence/nss68-runtime.json'
assert json.loads(current.read_text())['round']=='NSS68'
assert not history.exists();shutil.copyfile(current,history)
sources={};frozen=ws/'work/nss77/proof-export-v1/code';assert not frozen.exists()
for n,names in allowed.items():
    for name in names.split():
        assert 'private'not in name
        source=f'work/nss{n}/{name}';p=ws/source;assert p.is_file(),source
        dst=frozen/source;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dst)
        digest=sha(p);assert sha(dst)==digest;sources[source]=digest
        target=repo/'code'/source;assert not target.exists();target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(dst,target)
        manifest['sources'].append({'path':'code/'+source,'workspaceSource':source,'sha256':digest,'bytes':p.stat().st_size,'role':'reviewed-experiment-source-or-qualification-not-live-proof'})
proof={'round':'NSS69-77','sources':len(sources),'sourceHashes':sources,'historicPrefixSources':868,'historicPrefixCanonicalSha256':historic_source_sha,'notAdditionalProductionAdmission':True,'rawConnectionCredentialsCapturesAndBinariesExcluded':True}
save(ws/'work/nss77/source-proof.json',proof);save(repo/'evidence/nss77-source-proof.json',proof)

cases=[(68,'20261005035144-b351a48d','Optional process stat parser assertion; exact EOF/PID not captured'),
 (69,'20261005040745-4bf24064','Stale classifier observation during closed core wait'),
 (70,'20261005043204-feb23804','Obsolete extra setup reserve refused'),
 (71,'20261005043704-753d726e','Too late to renew; B stopped after 1.56 seconds'),
 (72,'20261005045247-ad21b8f1','Selected flow not admitted after opening; exact slot unknown'),
 (73,'20261005050652-25e46c2d','Application pair changed before staging'),
 (73,'20261005051307-9b2bd6cc','Same-source complete frame lacks selected TCP; UDP retained'),
 (74,'20261005052526-2a557970','Persistent TCP still disappeared during passive preparation'),
 (75,'20261005055326-7c434615','Tag counter read consumed final source learning reserve'),
 (76,'20261005061223-b1352de6','Initial readiness accepted age 2.94s; next pair read refused')]
def cpu(s):return list(map(int,s.splitlines()[0].split()[1:9]))
def softnet(s,k):return sum(int(line.split()[k],16)for line in s.splitlines())
def metrics(samples):
    a,b=samples[0],samples[-1];seconds=b['uptime']-a['uptime'];x,y=cpu(a['cpu']),cpu(b['cpu']);d=[v-u for u,v in zip(x,y)];total=sum(d)
    lan0,lan1=a['interfaces']['lan4'],b['interfaces']['lan4'];wan=next(k for k in a['interfaces']if k.startswith('rpwan'));w0,w1=a['interfaces'][wan],b['interfaces'][wan]
    return {'seconds':round(seconds,3),'frames':len(samples),'lan4Mbps':round((lan1['tx_bytes']-lan0['tx_bytes'])*8/seconds/1e6,3),'lan4Pps':round((lan1['tx_packets']-lan0['tx_packets'])/seconds,2),'wanRxMbps':round((w1['rx_bytes']-w0['rx_bytes'])*8/seconds/1e6,3),'cpuBusyPercent':round((total-d[3]-d[4])*100/total,3),'softirqPercent':round(d[6]*100/total,3),'timeSqueezeDelta':softnet(b['softnet'],2)-softnet(a['softnet'],2),'softnetDroppedDelta':softnet(b['softnet'],1)-softnet(a['softnet'],1),'acceleratedCounts':sorted({s['counts']['ecm_nss_ipv4/accelerated_count']for s in samples}),'observerCostIncluded':True}
trials=[]
for n,suffix,reason in cases:
    rel=f'work/nss{n}/real-matched-aba-{suffix}';p=ws/rel;r=read(rel+'/result.json');record=read(rel+'/last-record-private.json')if(p/'last-record-private.json').exists()else{}
    sel=read(rel+'/selected-private.json')if(p/'selected-private.json').exists()else read(rel+'/selected-preaudit-private.json')
    phases=[]
    for phase in record.get('phases',[]):
        samples=[s for s in record.get('samples',[])if s['phase']==phase['name']]
        if len(samples)>=2:phases.append({'name':phase['name'],'complete':phase.get('completed',False),**metrics(samples)})
    audit=read(rel+'/baseline-audit.json')if(p/'baseline-audit.json').exists()else{}
    after_path=ws/f'work/nss{n}/real-matched-aba-{suffix}-after-audit.json';native_after=json.loads(after_path.read_text())if after_path.exists()else{}
    cp=read(rel+'/stage-checkpoint-verified.json')if(p/'stage-checkpoint-verified.json').exists()else None
    stage=read(rel+'/stage-receipt-private.json')if(p/'stage-receipt-private.json').exists()else None
    undo=read(rel+'/stage-undo-verified.json')if(p/'stage-undo-verified.json').exists()else None
    restored={k:record.get(k,False)for k in ['qosRestored','qosModuleUnloaded','wanRestored','mwan3Restored','stateNodeRemoved']}
    trials.append({'round':f'NSS{n}','case':suffix,'passed':r['passed'],'completeABA':r['matchedForwardingABACompleted'],'failureCategory':reason,'wan':sel['udp']['wan'],'fullMark':sel['udp']['mark'],'initialMarkNatAndWanPairConsistent':sel['udp']['wan']==sel['tcp']['wan']and sel['udp']['mark']==sel['tcp']['mark']and sel['udp']['reply']['dst']==sel['tcp']['reply']['dst'],'phases':phases,'ecmFrontendOpened':bool(record.get('newNssPermit')),'acceleratedCountTwoObserved':any(2 in x['acceleratedCounts']for x in phases),'checkpointVerified':bool(cp),'independentStageBeforeWriteVerified':bool(stage and all(stage.get(k)for k in ['success','rollbackBeforeFirstWrite','parentIdentityVerified','pipeInodesVerified'])),'stageUndo':undo,'restore':restored,'protectedBaselineMatches':audit.get('configurationMatches',False),'rawRulesetIdentical':audit.get('rawRulesetIdentical',False),'fullRecoveryAudit':native_after,'bulkRtLeafBenefitClaimed':False,'humanExperienceClaimed':False,'cpuBenefitClaimed':False})
final=read('work/nss68/nss77-final-user-stop-health.json');assert final['passed']and final['ecmStoppedAndZero']and final['noStaging']
qualification={str(n):{'boundInputs':(257 if n==68 else [268,279,289,301,314,323,333,344,355][n-69]),'liveStageAttempted':n<=76,'newNativeCases':(15 if n==69 else 4 if n==70 else 7 if n==71 else 10 if n==72 else 7 if n==73 else 0 if n in(74,75)else 9)}for n in range(69,78)}
client={'computerUseStoppedByPhysicalEscape':True,'noFurtherComputerUseAfterStop':True,'taskGuardWithdrawn':read('work/nss76/client-window/user-stop-cleanup.json'),'nss75RestoredAndGuardCancelled':read('work/nss75/client-restored.json'),'nss75GuardReceipt':read('work/nss75/client-window/result.json'),'nss73NaturalGuard':read('work/nss73/client-window/result.json'),'nss74NaturalGuard':read('work/nss74/client-window/result.json'),'nss70NaturalReceiptMissing':True,'steamExistingRedDeadRedemption2DownloadCompletedAtLastUi':True,'finalValidationStillRunningAtLastUi':True,'latestFinalUiRestoreClaimed':False,'assistantIdleOfficialDeathmatch':True,'humanExperience':False,'newAcquiredGameNotLaunched':True,'purchaseOrUninstall':False}
data={'round':'NSS77','observedAt':final['observedAt'],'deploymentReference':final['deploymentReference'],'classifierConfigSha256':final['configSha256'],'candidateWorkerSha256':'40169ce6c8e866cc989c651b24d435777bc422bf10f67c58f5e9ab033e7f3828','permanentClassifierChangedThisTurn':False,'trials':trials,'qualification':qualification,'latestExperimentalEntry':'work/nss77/real-session.mjs','latestBoundInputs':355,'latestCandidateLiveTested':False,'latestCandidateRamChecks':9,'latestCandidateFullFastPathSyntaxCompiled':True,'knownReasons':{'selectedTcpAbsentInSameSourceCompleteFrameObserved':[73,74],'absenceProvesConntrackExit':False,'nss75RemainingSourceSecondsAfterGetter':2.68,'nss75OriginalRequiredSeconds':3,'nss75GetterAndResampleElapsedSeconds':0.45,'nss76InitialSourceAgeSeconds':2.94,'nss77MaximumInitialSourceAgeSeconds':1.65,'nss76GetterNowBeforeFinalClassifierProof':True,'nativeSixSecondExpiryAnd45SecondOwnerUnchanged':True},'client':client,'finalAudit':final,'conclusions':{'ecmAndTwoLeavesPreviouslyProvedBy49And56':True,'partialTwoFlowAccelerationObservedThisTurn':True,'completeMatchedABAThisTurn':False,'wholeRouterCpuBenefitProved':False,'humanCs2ImprovementProved':False,'latestCandidateHighLoadQualified':False,'secondWanExpansionAllowed':False,'upstreamSubmitted':False}}
save(ws/'outputs/nss77-mainline-observations.json',data);save(repo/'evidence/nss77-mainline.json',data);save(repo/'evidence/nss77-final-audit.json',final)
runtime={'round':'NSS77','checkedAt':final['observedAt'],'deploymentReference':final['deploymentReference'],'classifierConfigSha256':final['configSha256'],'workerPid':final['workerPid'],'guardianPid':final['guardianPid'],'publicationCandidateInstalled':True,'permanentClassifierChangedThisTurn':False,'nssPermanentlyEnabled':False,'qualifiedExperimentalEntry':data['latestExperimentalEntry'],'qualifiedExperimentalEntryBoundInputs':355,'entryPreparationQualified':True,'entryFullHighLoadForwardingQualified':False,'audit':final,'finalClosure':{'passed':all(final[k]for k in ['passed','ecmStoppedAndZero','noActiveTransaction','noStaging','noExperimentState','noExperimentalModule'])},'completePerformanceAndGameAcceptance':False,'requiresLiveRevalidation':True,'historical68RuntimePreservedSha256':sha(history),'computerUseStoppedByUser':True,'clientTaskGuardWithdrawn':client['taskGuardWithdrawn']['passed'],'clientFinalUiRestored':False}
save(current,runtime);manifest.update(lastAppendExport='NSS69-77',generatedAt=datetime.now(timezone.utc).isoformat(),privateDataExcluded=True);save(repo/'source-manifest.json',manifest)

rows=[]
for t in trials:
    phase=' / '.join(f"{x['name']} {x['seconds']}s{' (未完成)'if not x['complete']else''}, {x['lan4Mbps']}Mbps"for x in t['phases'])or'未取得测量阶段'
    rows.append(f"| {t['round']} | {phase} | {t['failureCategory']} | {'原完整恢复通过'if t['fullRecoveryAudit'].get('passed')else'见终态审核'} |")
table='| 轮次 | 实际阶段/负载 | 停止原因 | 恢复 |\n|---|---|---|---|\n'+'\n'.join(rows)+'\n'
brief='最新NSS77：常驻仍为NSS68/config581b5d46…c791d7。真实CS2/Steam现场已跑至NSS76；71实际ECM=2但B仅1.56秒，无完整A/B/A2或收益验收。73/74同源完整帧确认选中TCP缺失，UDP保留；75把最终TCP选择移到checkpoint后，完成A5.06秒后标签读耗时消耗学习余量；76初始ready在age2.94秒通过，后续pair/标签准备所需余量不一致。77只收紧初始准备age<1.65秒，继承76先读getter再做最终分类证明；355绑定/9目标RAM/完整fast语法通过，未现场试77。所有已stage轮次checkpoint和独立45秒守护，最终14:21原完整审核通过，4859/17139、ECM关闭全零、无事务/stage/state/模块。用户物理Esc停止桌面操作，已停止UI并撤下精确客户端guard，不声称本轮最终UI恢复。既有RDR2下载完成、最后UI仍验证文件；不再新下载/重装/重放/扩WAN。下一步只用77做一次集中同负载闭环，先实测资格再解释收益。'
for p in [repo/'AGENTS.md',ws/'AGENTS.md']:
    text=p.read_text(encoding='utf-8');anchor='- 最新NSS68'if p==ws/'AGENTS.md'else'最新NSS68';assert anchor in text
    write(p,text.replace(anchor,('- 'if p==ws/'AGENTS.md'else'')+brief+'\n\n'+anchor,1))
state=f'''更新：2026-10-05 14:21，北京时间。最新为NSS77；以下68及更早为历史。

**真实连接和两类加速的功能历史证明仍成立，当前瓶颈是控制器准备时间与分类有效期不一致。本轮只有部分B，完整同负载闭环仍未通过。最新修正已完成目标RAM检查，尚未现场测试。**

见 [实际轮次](../evidence/nss77-mainline.json)、[终态原完整审核](../evidence/nss77-final-audit.json)、[新源码](../evidence/nss77-source-proof.json)。

- 常驻仍是 `work/nss68/deployment-latest.json`，配置 `{final['configSha256']}`。本轮没有重装分类器或改变生产配置；worker4859/guardian17139，14:21 source1.89秒、ECM关闭零计数，无事务、暂存、state或实验模块。
- NSS71真实A5.17秒、B1.56秒，ECM2；B未达五秒并因续租过晚停止，无A2。LAN4约336/326Mbps、softirq52.03/50.17%、squeeze38/5，窗口长度不同，不是CPU收益。
- 73/74失败帧里选中Steam TCP不在同源完整分类快照，游戏UDP仍身份/mark/NAT/WAN/tag正确。不是已证明CT消失或分类器故障。75把最终精确TCP选择移至checkpoint下载与编译之后、独立stage之前，原游戏连接和单WAN范围固定。
- 75软件A5.06秒/11帧完成，最后学习余量2.68秒不满足3秒。76把耗时getter移至最终分类证明之前，保留六秒source/native、3秒学习、1.2/1.5秒core、20Mbps和45秒owner；实际失败发生在更早initial ready通过age2.94秒之后，未到A。
- 77只修正initial ready准备预算为age<1.65秒，使后续原标签age<2秒门槛有余量。355项绑定，9目标RAM检查和完整fast语法通过；IO/时钟/分类器模拟，**没有77现场stage/加速证明**。76的getter顺序也没有取得新的实际B证明。
- 本轮本地测试生成错误均保留原raw，修正之后才核验；不作为源码/内核缺陷。69可选stat EOF仅夹具复现，原现场没有具体EOF/PID，不能判定现场根因。
- 客户端通过官方死斗产生真实UDP，助手闲置，未取得真人体感。HUD有保存但不完整对应B，条件显示隐藏值不能记为零。75下载暂停与菜单/HUD恢复单独通过；最后76下载已完成、验证文件仍运行。用户物理Esc停止桌面操作，已停止UI并撤下精确任务guard，不能声称76最终菜单/HUD已恢复。
- 原68 runtime按字节保存，新增{len(sources)}份白名单源，累计{len(manifest['sources'])}。原始CT、端点、截图、checkpoint、凭据和二进制均留本地；没有提交上游Issue/PR。

## NSS68历史

'''
p=repo/'docs/STATE.md';write(p,'# 当前状态\n\n'+state+p.read_text(encoding='utf-8').removeprefix('# 当前状态\n\n'))
plan='''# 下一步：仅完成修正后的单WAN真实闭环

当前355项入口为 `work/nss77/real-session.mjs`，常驻仍NSS68。77仅准备/目标RAM检查通过，未现场试用。见 [STATE](STATE.md)。

1. 用户恢复桌面操作后，先读当前部署和原完整保护审核，读取当前游戏/现有Steam真实流；不重装、不重放旧准备、不再找新游戏维持准备。当前下载已经完成，不能拿0bps当高负载。
2. 用77实际验证initial来源预算与76学习前getter顺序，checkpoint/独立45秒owner、一WAN一TCP一UDP、20Mbps保持。若无真实同WAN持续配对，不写NSS；不把RAM通过当现场资格。
3. 一次完整A/B/A2，记真实flow身份、leaf计数、ct mark/NAT/WAN affinity、CPU/softirq/time_squeeze、吞吐、HUD。选中TCP只能在stage之前最终选择，现有gate不重定向；阶段中退出必须精确撤销。
4. 对比总负载、单WAN和受控份额，解释五秒观察器开销、客户端HUD滚动值及非真人闲置边界。没有完整可比结果不声称改善，不扩第二WAN/共享预算/Wi-Fi/autorate。
5. 用户物理Esc停止Computer Use后，不能再次操作游戏/Steam；已撤下此次客户端关机guard，不把它当UI恢复证明。新的客户端窗口要单独绑定实例和撤销期限。

## NSS68历史计划

'''
p=repo/'docs/PLAN.md';write(p,plan+p.read_text(encoding='utf-8'))
p=repo/'docs/EXPERIMENT_LOG.md';write(p,p.read_text(encoding='utf-8')+'\n## 2026-10-05 NSS69–77：真实配对、部分加速和准备顺序定位\n\n'+state.split('见 [实际轮次]')[1].split('## NSS68历史')[0].join(['见 [实际轮次]',''])+'\n'+table+'\n')
p=repo/'README.md';text=p.read_text(encoding='utf-8');write(p,text.split('\n',1)[0]+'\n\n最新 [NSS77](evidence/nss77-mainline.json)：真实CS2/Steam部分加速，完整闭环未通过；已定位并修正准备余量不一致，最新候选355项/目标RAM通过但未现场试用。当前ECM关闭且恢复审核通过。先读 [STATE](docs/STATE.md) 和 [PLAN](docs/PLAN.md)。下方68及更早是历史。\n\n'+text.split('\n',1)[1])
p=repo/'docs/ARTIFACT_INDEX.md';write(p,'# 证据索引\n\n## 当前NSS77\n\n- [实测轮次](../evidence/nss77-mainline.json)、[终态审核](../evidence/nss77-final-audit.json)、[新源冻结](../evidence/nss77-source-proof.json)。\n- [当前运行](../evidence/current-runtime.json)、[NSS68 runtime原字节](../evidence/nss68-runtime.json)。\n\n'+p.read_text(encoding='utf-8').removeprefix('# 证据索引\n\n'))
write(repo/'docs/ISSUE_PROC_STAT_OPTIONAL_READ.md','''# 可选进程stat解析：潜在兼容Issue，尚未提交

原NSS68现场在可选`/proc/<pid>/stat`格式断言125处失败，但没有记录具体PID或原始读取结果。不能直接确认现场由EOF造成，更不能称内核缺陷。

NSS69对可选枚举的空/消失/格式不完整stat跳过，guard本身仍严格读取PID/start/argv，未完整的child不准入。15目标RAM检查中旧实现9失败，新实现只有3个预期guard拒绝；完整语法和实际只读scan通过。200ms出生、HZ100、4096枚举边界不变。

对应本地 [helper](../code/work/nss69/core-guard-phase.lua) 与 [最小夹具](../code/work/nss69/stat-eof-fixtures.lua)。它是本项目helper边界；只有取得现场原始stat/身份和对应上游代码版本后，才考虑上游Issue/PR。未提交。\n''')

checker=repo/'tools/check_repository.py';text=checker.read_text(encoding='utf-8');text=text.replace("x68=json.loads((root/'evidence/nss68-mainline.json').read_text());l68=json.loads((root/'evidence/current-runtime.json').read_text())","x68=json.loads((root/'evidence/nss68-mainline.json').read_text());l68=json.loads((root/'evidence/nss68-runtime.json').read_text())")
extra='''assert len(manifest['sources'])>868
proof77=json.loads((root/'evidence/nss77-source-proof.json').read_text())
assert hashlib.sha256(json.dumps(manifest['sources'][:868],sort_keys=True,separators=(',',':')).encode()).hexdigest()==proof77['historicPrefixCanonicalSha256']
assert len(manifest['sources'])==868+proof77['sources']
for source,digest in proof77['sourceHashes'].items():assert hashlib.sha256((root/'code'/source).read_bytes()).hexdigest()==digest
x77=json.loads((root/'evidence/nss77-mainline.json').read_text());rt77=json.loads((root/'evidence/current-runtime.json').read_text())
assert x77['latestBoundInputs']==355 and x77['latestCandidateRamChecks']==9 and not x77['latestCandidateLiveTested']
assert len(x77['trials'])==10 and sum(t['independentStageBeforeWriteVerified']for t in x77['trials'])==9
assert all(t['protectedBaselineMatches']for t in x77['trials'])
for t in x77['trials']:
    assert not t['completeABA'] and not t['cpuBenefitClaimed'] and not t['humanExperienceClaimed']
    if t['independentStageBeforeWriteVerified']:assert t['checkpointVerified'] and all(t['stageUndo'].values()) and all(t['restore'].values())
assert sum(t['acceleratedCountTwoObserved']for t in x77['trials'])==1
assert x77['knownReasons']['nativeSixSecondExpiryAnd45SecondOwnerUnchanged']
assert x77['client']['computerUseStoppedByPhysicalEscape'] and x77['client']['taskGuardWithdrawn']['passed']
assert not x77['client']['latestFinalUiRestoreClaimed']
assert rt77['round']=='NSS77' and not rt77['entryFullHighLoadForwardingQualified'] and not rt77['nssPermanentlyEnabled']
assert rt77['finalClosure']['passed'] and rt77['audit']['configurationMatches'] and rt77['audit']['originalFullLockedAudit']
assert rt77['historical68RuntimePreservedSha256']==hashlib.sha256((root/'evidence/nss68-runtime.json').read_bytes()).hexdigest()
'''
assert "assert len(manifest['sources'])==868"in text;text=text.replace("assert len(manifest['sources'])==868",extra);write(checker,text)

body='''本轮到NSS77。常驻分类器仍为NSS68，最后原完整审核通过，ECM关闭、实验全部撤销。

实际CS2与Steam连接已经出现。NSS71实际两条加速连接，但B仅1.56秒，没有完整A/B/A2；不能据此称CPU或游戏改善。本轮定位到选中TCP在准备中消失，以及两处准备余量不一致。最新候选将getter移至最终分类证明前，并为初始标签发布保留真实准备时间；355项绑定和目标RAM检查通过，尚未现场试77。

用户物理Esc停止桌面操作后，已停止操作游戏/Steam、撤下精确客户端定时关闭。现有RDR2网络下载已完成，最后界面仍在验证文件；不声称最终菜单/HUD恢复。

下一步只需用77集中完成一次同负载单WAN闭环。没有新下载、旧准备重放、重装或扩WAN计划。报告保留失败和恢复证据，旧历史按原字节保留。
'''
write(ws/'outputs/nss77-mainline-report.html','<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>NSS77 主线记录</title><style>body{max-width:980px;margin:48px auto;padding:0 24px;background:#f4f6f8;color:#152233;font:17px/1.8 system-ui}article{background:white;border:1px solid #dce2e8;border-radius:12px;padding:32px}h1{font-size:28px}table{width:100%;border-collapse:collapse;font-size:14px}td,th{padding:10px;border:1px solid #dce2e8;text-align:left}p{margin:16px 0}</style><article><h1>NSS77：准备顺序修正完成，完整闭环未验收</h1>'+''.join('<p>'+html.escape(p)+'</p>'for p in body.strip().split('\n\n'))+'<h2>实际轮次</h2><table><thead><tr><th>轮次</th><th>实际阶段</th><th>停止原因</th><th>恢复</th></tr></thead><tbody>'+''.join('<tr><td>'+t['round']+'</td><td>'+html.escape(' / '.join(f"{x['name']} {x['seconds']}s，{x['lan4Mbps']}Mbps"for x in t['phases'])or'无测量阶段')+'</td><td>'+html.escape(t['failureCategory'])+'</td><td>保护配置恢复</td></tr>'for t in trials)+'</tbody></table><p>原始截图、连接、凭据与checkpoint仅在本地；HTML源已生成，未进行浏览器渲染验收。</p></article></html>')
print(json.dumps({'passed':True,'sourcesAppended':len(sources),'totalSources':len(manifest['sources']),'trials':len(trials),'stages':sum(t['independentStageBeforeWriteVerified']for t in trials),'report':'outputs/nss77-mainline-report.html'}))
