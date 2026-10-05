"""Export measured NSS79-82 results; private transports/captures remain local."""
from pathlib import Path
import hashlib, html, json, shutil
from datetime import datetime, timezone

workspace = Path(__file__).resolve().parents[2]
repo = workspace / 'athena-nss-mainline'
sha = lambda b: hashlib.sha256(b).hexdigest()
def load(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(p, o): p.write_text(json.dumps(o, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

specs = [
    (79, '20261005082039-3f566989', 'matched-18', None),
    (80, '20261005083215-42856ea1', 'finite-byte-cap', 'Selected TCP exited at the finite 450 MiB cap before learning; same-source full classifier lacked TCP and retained UDP.'),
    (80, '20261005083817-5c29bbab', 'final-ack-skew', 'All three phases ran, but the final software tag getter rejected one TCP ACK counter skew; the original overall failure is retained.'),
    (81, '20261005085132-37b5571a', 'initial-down-skew', 'Initial software tag getter rejected one 1500-byte TCP-down counter skew before phase A; no ECM opening.'),
    (82, '20261005090050-aec227ca', 'saturated-32', None),
]
def counters(raw):
    out = {}
    for x in raw.get('nftables', []):
        rule = x.get('rule', {})
        for e in rule.get('expr', []):
            if 'counter' in e: out[rule['comment'].split(':')[-1]] = e['counter']
    return out

trials = []
for n, suffix, name, reason in specs:
    p = workspace / f'work/nss{n}/controlled-matched-aba-{suffix}'
    r = load(p/'last-record-private.json')
    result = load(p/'result.json')
    cp = load(p/'stage-checkpoint-verified.json')
    receipt = load(p/'stage-receipt-private.json')
    detach = load(p/'stage-detached-private.json')
    undo = load(p/'stage-undo-verified.json')
    baseline = load(p/'baseline-audit.json')
    before = load(p.parent/(p.name+'-before-audit.json'))
    after = load(p.parent/(p.name+'-after-audit.json'))
    assert cp['gzipVerified'] and receipt['success'] and receipt['rollbackBeforeFirstWrite']
    assert detach['identity']['ppid'] == 1 and receipt['pipeInodesVerified'] and receipt['parentIdentityVerified']
    assert all(undo.values()) and baseline['configurationMatches'] and all(baseline['checks'].values())
    assert before['passed'] and after['passed'] and before['exactOwnedNativeAudit'] and after['exactOwnedNativeAudit']
    assert before['protectedConfigurationUnchanged'] and after['protectedConfigurationUnchanged']
    manifest = load(p/'source-manifest.json')
    assert all(sha((workspace/f).read_bytes()) == h for f,h in manifest.items())
    tag_reads = {}
    for k,v in r.items():
        if isinstance(v, dict) and 'nftables' in v:
            c = counters(v)
            if 'tcp_post_up_total' in c: tag_reads[k] = c
    t = {
        'round': f'NSS{n}', 'name': name, 'caseLocalPath': p.relative_to(workspace).as_posix(),
        'passed': result['passed'], 'reason': reason, 'oneWan': load(p/'selected-private.json')['tcp']['wan'],
        'ecmOpened': 'frontendOpenedAt' in r,
        'phases': [{k:x[k] for k in ['name','seconds','sampleCount','completed'] if k in x} for x in r['phases']],
        'sourceInputs': len(manifest), 'sourceManifestSha256': sha((p/'source-manifest.json').read_bytes()),
        'sourceInputsCurrentBytesMatchActualRun': True,
        'checkpointDownloadedShaAndGzipVerified': True, 'independentOwnerSeconds': 45,
        'guardianPpid': 1, 'guardianVerifiedBeforeFirstWrite': True,
        'checkpointSha256': cp['sha256'], 'rollback': undo, 'baseline': baseline,
        'beforeFullAudit': before, 'afterFullAudit': after,
        'softwareTagCounters': tag_reads, 'rereads': r.get('tagCounterRereads', []),
        'originalResultSha256': sha((p/'result.json').read_bytes()),
        'originalRecordSha256': sha((p/'last-record-private.json').read_bytes()),
        'gameQualityConclusion': False, 'highLoad300MbpsConclusion': False,
    }
    if (p/'actual-metrics.json').exists(): t['metrics'] = load(p/'actual-metrics.json')
    if (p/'actual-accelerated-state-proof.json').exists():
        proof = load(p/'actual-accelerated-state-proof.json')
        t['acceleratedIdentityProof'] = proof
        assert proof['passed'] and proof['connectionCount'] == 2
    trials.append(t)

matched, saturated = trials[0]['metrics'], trials[-1]['metrics']
assert matched['passed'] and saturated['passed']
assert all(x['seconds'] >= 5 and x['sampleCount'] == 11 for m in [matched,saturated] for x in m['phases'])
assert all([x['acceleratedCounts'] for x in m['phases']] == [[0],[2],[0]] for m in [matched,saturated])
tcp = [x['clientTcpMbps'] for x in matched['phases']]
assert max(tcp)/min(tcp) < 1.01
soft = [x['softirqPercent'] for x in matched['phases']]
reduction = (1-soft[1]/((soft[0]+soft[2])/2))*100
assert 50 < reduction < 60
assert saturated['leafCountersAcrossBObservation']['8f05:']['dropped'] == 143
assert saturated['leafCountersAcrossBObservation']['8f06:']['dropped'] == 0
assert saturated['phases'][1]['udp']['unreturned'] == 0

final = load(workspace/'work/nss68/nss82-final-20261005-health.json')
assert final['passed'] and final['configurationMatches'] and final['originalFullLockedAudit']
assert final['workerPid'] == 4859 and final['guardianPid'] == 17139
assert all(final[k] for k in ['ecmStoppedAndZero','noActiveTransaction','noStaging','noExperimentState','noExperimentalModule'])
load_dir = workspace/'work/nss82/load-20261005085940-ecb94cf94ba8b7bf'
firewall = json.loads(load(load_dir/'firewall-after-private.json')['stdout'])
server = load(load_dir/'server-closed-private.json')
client = load(load_dir/'result-private.json'); guard = load(load_dir/'guard-result-private.json')
assert firewall['ownedRulesRemaining'] == 0 and firewall['baselineRestored']
assert 'MainPID=0' in server['stdout'] and 'ActiveState=inactive' in server['stdout']
assert guard['passed'] and guard['exactClientOnly'] and guard['clientExitedBeforeDeadline']
endpoint_closed = {
    'temporaryFirewallRulesRemaining': 0, 'canonicalFirewallBaselineRestored': True,
    'ownedUnitInactiveMainPidZeroPortsClosed': True, 'clientExited': True,
    'clientGuardPassed': True, 'clientReachedFiniteByteCeilingAfterMeasurement': True,
    'clientFinalErrors': client['errors'], 'wholeSessionUdpIsNotPhaseLoss': True,
    'noExistingVpsServiceReplaced': True,
}
ack = load(workspace/'work/nss82/ack-qualified.json')
entry = load(workspace/'work/nss82/entry-qualified.json')
assert ack['passed'] and ack['cases'] == 17 and ack['strictGetterRetained']

oldpath = repo/'evidence/current-runtime.json'; old = oldpath.read_bytes()
assert load(oldpath)['round'] == 'NSS78'
history = repo/'evidence/nss78-runtime.json'; assert not history.exists(); history.write_bytes(old)
manifest_path = repo/'source-manifest.json'; manifest = load(manifest_path)
assert len(manifest['sources']) == 992
prefix = sha(json.dumps(manifest['sources'], sort_keys=True, separators=(',',':')).encode())
common = ['controlled-session.mjs','read-controlled.mjs','current-audit-diagnostic.mjs','session-binding.mjs',
    'client.py','client-watchdog.ps1','server.py','endpoint-firewall-guardian.py','discover-peer.py',
    'probe-peer.py','match-controlled.mjs','calibrate-clock.mjs','analyze-controlled.py']
sources = []
for n in [79,80,81,82]:
    names = common + (['fast-path.lua','payload.mjs','module-stage.mjs','qualify-ack.mjs'] if n>=81 else [])
    for name in names:
        f = workspace/f'work/nss{n}/{name}'
        if f.exists(): sources.append(f)
sources.append(Path(__file__).resolve())
hashes = {}
for f in sources:
    rel = f.relative_to(workspace).as_posix(); dst = repo/'code'/rel
    assert not dst.exists(); dst.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(f,dst)
    digest = sha(f.read_bytes()); assert digest == sha(dst.read_bytes()); hashes[rel] = digest
    manifest['sources'].append({'path':'code/'+rel,'workspaceSource':rel,'sha256':digest,
        'bytes':len(f.read_bytes()),'role':'controlled-real-WAN-test-and-measured-evidence'})
manifest['generatedAt'] = datetime.now(timezone.utc).isoformat(); manifest['lastAppendExport'] = 'NSS82'
dump(manifest_path, manifest)
sourceproof = {
    'round':'NSS82','sources':len(hashes),'sourceHashes':hashes,'historicPrefixSources':992,
    'historicPrefixCanonicalSha256':prefix,'privateOwnedHostBootstrapExcluded':True,
    'completePrivateSourceInputsRetained':True,'fullSourceExportIsNotStandaloneTransportBootstrap':True,
    'notAdditionalProductionAdmission':True,
}
dump(repo/'evidence/nss82-source-proof.json',sourceproof)
dump(repo/'evidence/nss82-final-audit.json',final)
dump(repo/'evidence/nss82-trials.json',trials)
dump(repo/'evidence/nss82-matched18.json',matched)
dump(repo/'evidence/nss82-saturated32.json',saturated)
dump(repo/'evidence/nss82-endpoint-closure.json',endpoint_closed)
dump(repo/'evidence/nss82-tag-reader.json',{
    'actual80FinalAckCounters':trials[2]['softwareTagCounters']['tagsAfterA2'],
    'actual81InitialDownCounters':trials[3]['softwareTagCounters']['initialTags'],
    'actual82BeforeLearningFirstCounters':trials[4]['softwareTagCounters']['tagsBeforeFirst'],
    'actual82BeforeLearningSecondCounters':trials[4]['softwareTagCounters']['tagsBefore'],
    'nativeQualification':ack,'candidate':{k:v for k,v in entry.items() if k!='sourceManifest'},
    'oneRereadAtAllFiveGetterSites':True,'secondGetterOriginalStrictPredicatesRetained':True,
    'actual82RereadUsedTcpDownPredicate':True,'actual82AckPredicateLiveUseClaimed':False,
    'allUnexpectedCountersZeroInRecordedFrames':True,'secondSnapshotPassed':True,
    'firmwareMisTagProved':False,'kernelBugProved':False,'upstreamSubmitted':False,
})
evidence = {
    'round':'NSS82','roundsCovered':['NSS79','NSS80','NSS81','NSS82'], 'observedAt':final['observedAt'],
    'hypothesis':'A real controlled automatically classified TCP/UDP pair can enter NSS bulk/RT leaves with correct NAT/PBR and measurable forwarding savings.',
    'method':'Existing authenticated owned-host SSH TCP and nonce-authenticated 128-byte bidirectional UDP; no game or Steam required for engineering.',
    'permanentClassifierChanged':False,'productionFirmwareKernelChanged':False,
    'residentDeployment':'work/nss68/deployment-latest.json','classifierConfigSha256':final['configSha256'],
    'scope':{'oneWanAtATime':True,'controlledTcpFlows':1,'controlledUdpFlows':1,'qosGroupMbps':20,
        'bulkRateMbps':19,'rtRateMbps':1,'rtCanBorrowToMbps':20,'defaultFallbackMbps':950,
        'nssFqCodelTargetMs':5,'intervalMs':100,'bulkLimitPackets':256,'rtLimitPackets':128,
        'originalClassificationAndCoreAndNativeLeaseDeadlinesUnchanged':True},
    'stageCases':len(trials),'successfulCompleteABA':sum(t['passed'] for t in trials),
    'matched18':{'actualTcpMbps':tcp,'softirqPercent':soft,'relativeReductionAgainstMeanSoftwarePercent':reduction,
        'matchedShortWindowSoftirqBenefitSupported':True,'timeSqueezeAllZero':True},
    'saturated32':{'offeredTcpMbps':32,'actualClientTcpMbps':[p['clientTcpMbps'] for p in saturated['phases']],
        'actualThroughputMatched':False,'cpuBenefitAcceptance':False,'bulkBObservationDrops':143,
        'rtBObservationDrops':0,'udpBReplies':213,'udpBSent':213},
    'preWriteLocalFailures':{'esmWindowsPathRequiredFileUri':True,'sshGCrLfParserFixed':True,
        'expectedFastHashLfVsActualCrLfCorrectedBeforeStage':True,'noNssWriteFromTheseFailures':True},
    'endpointPreparation':{'aliyunRawPortsUnreachable':True,'sgRawPortsUnreachable':True,
        'dallasTcpUdpNaturalPbrInitiallyDifferentWan':True,'dallasRawTcpAbout1MbpsWasBE':True,
        'workingBulkUsesExistingOwnedSgSshService':True,'routerPbrPolicyUnchanged':True,
        'unprovenUpstreamPortDropCauseNotDeclaredFixed':True},
    'conclusions':{'realAutoClassifierToNssLeafPathProved':True,'correctPbrCtMarkNatWanAffinityProved':True,
        'matchedShortWindowSoftirqBenefitSupported':True,'bulkCongestionAndRtQueueIsolationObserved':True,
        'exactRatePrecisionProved':False,'multiFlowFairnessProved':False,'ecnProved':False,
        'highLoad300MbpsBenefitProved':False,'cs2JitterLossMissProved':False,'realHumanExperienceProved':False,
        'generalLongTermStabilityProved':False,'upstreamSubmitted':False},
    'caveats':['Each A/B/A2 window is about 5 seconds with a common observer.',
        'WAN netdev NSS statistics are batched; aligned client bytes are the throughput comparison.',
        'The 32 Mbps sender offer is not 32 Mbps achieved; measured phase throughput is retained.',
        'NSS leaf statistics are asynchronous observations spanning B, not exact per-phase dequeue counts.',
        'Low-rate UDP echo RTT/unreturned counts are not CS2 jitter/loss/Miss.',
        'CAKE per-tin packet statistics were not sampled per phase; its ten configurations were restored.',
        'No host fairness, DiffServ tin semantics or autorate replacement is proved by this two-leaf test.'],
    'finalState':final,'endpointClosure':endpoint_closed,
    'reportVerification':{'sourceValidated':True,'browserRendered':False},
}
dump(repo/'evidence/nss82-mainline.json',evidence)
runtime = {
    'round':'NSS82','checkedAt':final['observedAt'],'deploymentReference':final['deploymentReference'],
    'classifierConfigSha256':final['configSha256'],'workerPid':4859,'guardianPid':17139,
    'publicationCandidateInstalled':True,'permanentClassifierChangedThisTurn':False,
    'nssPermanentlyEnabled':False,'nssOpenedThisTurn':True,
    'qualifiedExperimentalEntry':'work/nss82/controlled-session.mjs','qualifiedExperimentalEntryBoundInputs':405,
    'controlledRealWanABACompleted':True,'matched18MbpsSoftirqBenefitSupported':True,
    'entryFullHighLoadForwardingQualified':False,'realHumanGameAcceptance':False,
    'audit':final,'finalClosure':{'passed':True},'endpointClosure':endpoint_closed,
    'requiresLiveRevalidation':True,'historical78RuntimePreservedSha256':sha(old),
    'next':'Use the controlled owner at higher single-WAN budget, then one concentrated real CS2 acceptance. No recurring Steam downloads.',
}
dump(oldpath,runtime)

now = datetime.fromisoformat(final['observedAt'].replace('Z','+00:00')).astimezone(timezone(__import__('datetime').timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
state = f'''# 当前状态

更新：{now}，北京时间。最新NSS82；常驻仍NSS68，实验NSS均已撤销。

**受控真实TCP＋UDP完成两次完整单WAN A→B→A2。相同约18Mbps的客户端吞吐下，softirq为9.65→4.31→9.48%，相对两段软件均值下降54.97%。32Mbps发送负载下bulk丢弃143、RT零丢弃，NSS段UDP213/213收到回复。工程闭环已通过，300Mbps和真人CS2收益尚未验收。**

见 [实测汇总](../evidence/nss82-mainline.json)、[五个现场案例](../evidence/nss82-trials.json)、[相同18Mbps对照](../evidence/nss82-matched18.json)、[32Mbps拥塞观察](../evidence/nss82-saturated32.json)、[终态审核](../evidence/nss82-final-audit.json)。

- 用户新授权：工程调试使用自有端点的受控真实TCP＋低速UDP，不再把Steam下载和CS2对局作为每轮硬前提。真人CS2保留为最后集中游戏指标/体验验收，不把echo当游戏指标。
- 永久分类器未改、未重装。4859/17139连续；config581b5d46…c791d7，原完整审核source1.15秒通过。ECM关闭全零，无事务/stage/state/实验模块；保护配置、认证、PBR、NAT、十个生产队列恢复。
- 79在WAN5、82在WAN2分别成功，均一次只有一个WAN、一TCP一UDP；不是两WAN同时扩大。真实自动BULK/RT分类、学习前tag、firmware bulk/RT tag、ct mark/NAT/出口粘性、续租、精确撤销与0→2→0均通过。
- 32Mbps轮A/B/A2实际吞吐14.90/17.16/18.08Mbps，不同负载，不能引用其CPU降幅作收益。所有time_squeeze和softnet drop增量0；短窗不能证明高负载稳定。
- 80一次TCP达到450MiB有限上限提前退出；另一次完整三段但末尾ACK计数差1包/60字节拒绝。81初始计数差1包/1500字节拒绝。82统一在五个getter位置只允许一次这两种精确偏差重读，第二次原严格getter必须通过。实际82用了TCP-down分支；ACK新分支仅17项目标RAM通过，不冒充现场触发。原失败保留。
- 自有UDP端点独立180秒防火墙恢复基线、临时规则0、服务已退出/端口关闭；客户端达到字节上限后退出，独立精确guard通过。没有新游戏下载、购买/卸载、桌面/HUD改动。原始端点连接、密钥、nonce、CT、checkpoint和完整实际输入留本地。
- 下一步直接提高单WAN受控预算、验证更接近实际WAN速率的同负载收益与拥塞行为；之后集中一次真人CS2验收。不要再重装分类器、重放旧准备或同时扩第二WAN/共享预算/Wi-Fi/autorate。

## NSS78历史

'''
statepath=repo/'docs/STATE.md'; previous=statepath.read_text(encoding='utf-8').split('\n',2)[2];statepath.write_text(state+previous,encoding='utf-8')
plan='''# 下一步：提高单WAN受控带宽，再一次真人验收

NSS79/82已完成受控真实连接工程闭环和18Mbps可比softirq对照。新的用户授权允许以自有端点TCP/UDP推进工程，不必等待游戏或反复Steam下载；见 [STATE](STATE.md)。

1. 使用当前NSS82受控入口，读实际部署/原完整审核/端点归属/真实socket；不要复用旧流、旧producer或过期owner。
2. 新目录里只提高单WAN受控组带宽这一主要QoS变量，发送负载明确记录。当前20Mbps是已验证试验值，不是假定的永久上限；变更先做目标语法/参数验证，再新checkpoint＋独立45秒撤销。继续精确一TCP一UDP，不改PBR，不开放未知流。
3. 保持学习前标签、ct mark/NAT/出口和6秒来源/12秒native session等期限；加速中改类仍须精确撤销再学习。计数精确偏差仅一次重读，第二次原严格检查不通过就撤销。
4. 直接测完整同流A/B/A2；以客户端真实吞吐判断可比，记录softirq/time_squeeze/pps/RTT/未返回和bulk/RT leaf计数。发送速率不等于实际吞吐，WAN NSS计数批量更新不作客户端速率替代。
5. 工程带宽测试通过后，仅集中一次真实CS2＋正常下载，记录真实HUD jitter/loss/Miss和体感。受控UDP不是真人验收。最后再评估单WAN常用配置；第二WAN、共享预算、Wi-Fi、autorate仍在后面。

## NSS78历史计划

'''
planpath=repo/'docs/PLAN.md';planpath.write_text(plan+planpath.read_text(encoding='utf-8'),encoding='utf-8')
ag=repo/'AGENTS.md';text=ag.read_text(encoding='utf-8');anchor='最新NSS78：'
assert anchor in text
newag='最新NSS82：用户已接受工程用自有端点受控TCP＋低速UDP，Steam/CS2只留最后集中体验验收。79/82完整单WANA/B/A2、ECM0→2→0、真实自动bulk/RT leaf、mark/NAT/affinity及恢复通过；18Mbps实际吞吐可比，softirq9.65→4.31→9.48%，约54.97%相对降幅，只是短窗。82发送32Mbps、实测14.90/17.16/18.08不匹配，不验收其CPU；bulk丢弃143、RT0、B UDP213/213回复。80字节上限退出及ACK1包60字节拒绝、81初始down1包1500字节拒绝原失败保留；82所有五个getter只对精确两种偏差重读一次、第二次仍原严格检查，实际触发down分支，ACK仅17RAM不称现场。5 checkpoint/独立45秒全恢复；17:05原完整审核4859/17139/source1.15通过，常驻68/config不变，ECM关闭全零，无残留。端点FW180秒独立恢复、规则0、临时unit/端口/客户端已退出；完整实际输入和端点凭据留本地。下一步直接提高单WAN受控预算，不重装/重放/新游戏下载/扩第二WAN；真人CS2和300Mbps尚未验收。STATE为准。\n\n'
ag.write_text(text.replace(anchor,newag+anchor,1),encoding='utf-8')
readme=repo/'README.md';text=readme.read_text(encoding='utf-8');readme.write_text('# Athena NSS 主线\n\n最新 [NSS82受控工程闭环](evidence/nss82-mainline.json)：两次完整单WAN A/B/A2通过；同18Mbps负载softirq约下降55%，32Mbps发送负载bulk拥塞而RT队列零丢弃。当前NSS已撤销、常驻NSS68未改。工程无需反复开Steam/CS2，下一步直接更高单WAN受控带宽，真人游戏只留最后集中验收。先读 [状态](docs/STATE.md) 和 [计划](docs/PLAN.md)。下方旧结论为历史。\n\n'+text,encoding='utf-8')
index=repo/'docs/ARTIFACT_INDEX.md';text=index.read_text(encoding='utf-8');index.write_text('# 证据索引\n\n## 当前NSS82\n\n- [实测汇总](../evidence/nss82-mainline.json)、[五次现场/失败保留](../evidence/nss82-trials.json)、[18Mbps可比对照](../evidence/nss82-matched18.json)、[32Mbps拥塞观察](../evidence/nss82-saturated32.json)。\n- [计数偏差与重读](../evidence/nss82-tag-reader.json)、[终态原完整审核](../evidence/nss82-final-audit.json)、[端点独立恢复](../evidence/nss82-endpoint-closure.json)、[新源字节冻结](../evidence/nss82-source-proof.json)。\n- [当前运行](../evidence/current-runtime.json)、[旧78 runtime原字节](../evidence/nss78-runtime.json)；本地报告`outputs/nss82-mainline-report.html`。\n\n'+text,encoding='utf-8')
log=repo/'docs/EXPERIMENT_LOG.md';text=log.read_text(encoding='utf-8');text+='''

## 2026-10-05 NSS79–82：受控真实TCP/UDP与完整工程闭环

- 用户接受以自有端点受控TCP/UDP做工程，不再每轮等待Steam/CS2。公开新端口连通性准备失败保留：Aliyun/SG raw端口不可达，Dallas TCP/UDP初始PBR不同WAN；约1Mbps TCP被原分类器归BE，未强行BULK。最终复用自有SG既有已认证SSH TCP＋自有Dallas nonce等长UDP；自然尝试自己的socket端口找到同WAN，不改路由器PBR/系统服务。
- 79同WAN5、TCP真实17.996/17.989/17.990Mbps，三段各5秒/11帧；ECM0→2→0，softirq9.65/4.31/9.48%、busy25.08/20.60/27.33，squeeze/drop均0。bulk/RT分别+9798/+271包、队列drop0/0；UDP未返回5/4/8，不是CS2指标。支持当前短窗18Mbps软件转发softirq改善，不能外推300Mbps或长期稳定。
- 80第一次TCP450MiB有限上限后退出，A完成但学习前同源完整帧TCP缺失，UDP保留；无B。第二次三段均完成、ECM0→2→0，但A2最后软件NFT total/expected差一个60字节ACK，错误tag计数全0，原overall失败不改。bulk/RT drop69/0；实际吞吐13.66/18.03/17.33，不验收CPU。
- 81最初本地expected SHA把LF字符串与实际CRLF文件混用，写前失败；改为实际字节SHA后新stage在initial getter出现down1包/1500字节偏差，无A/ECM。两个不同位置证据提示多规则counter dump不同时刻；不是已证明firmware误标或内核缺陷。
- 82只统一五个getter的精确一次重读，允许原down1包1500字节或新up ACK1包60字节；所有其它计数需一致/错误tag与neighbor全0，第二次仍原严格getter。17项原生ACK正负案例通过；现场只触发down分支，第二次一致。完整payload目标编译/SHA与原transport大小限制保留。
- 82在WAN2同一TCP/UDP跑完整5.00/5.01/5.02秒、各11帧；ECM0→2→0、正确bulk/RT tag、mark0x20000/NAT/出口、1次续租、精确撤销。发送32Mbps，实际14.90/17.16/18.08，不同吞吐不作CPU收益；softirq11.73/7.24/18.12、busy30.39/22.81/35.95、squeeze0。B观察bulk+8990包/drop143、RT+262/drop0；UDP203/203、213/213、203/202，p95约205.64/205.25/204.86ms，为自有端点RTT而非游戏。
- 五个现场stage各新checkpoint下载/SHA/gzip、独立PPID1/45秒owner写前核验，最后全部保护配置/完整原审核恢复通过。17:05常驻4859/17139、config581b5d46…c791d7/source1.15；ECM关闭全零，无事务/stage/state/模块。临时端点180秒FW独立恢复与客户端guard通过，临时端口已关闭，无生产VPS服务替换、游戏/Steam/UI/HUD改动。
- 新源码与脱敏聚合证据进私有仓库；完整原始CT、nonce、连接/凭据、checkpoint、模块、实际绑定输入仍留本地。旧78 runtime原字节保存。不提交上游；下一步直接提高单WAN受控带宽，再最后集中真人验收，不重装/重放旧准备或同时扩多WAN。
''';log.write_text(text,encoding='utf-8')

def rows(m):
    return ''.join('<tr>'+''.join(f'<td>{html.escape(str(v))}</td>' for v in [p['phase'],f"{p['clientTcpMbps']:.2f}",f"{p['interfaces']['lan4']['mbps']:.2f}",f"{p['busyPercent']:.2f}%",f"{p['softirqPercent']:.2f}%",p['timeSqueezeDelta'],f"{p['udp']['received']}/{p['udp']['sent']}",f"{p['udp']['rttP95Ms']:.2f}"])+'</tr>' for p in m['phases'])
header='<tr><th>阶段</th><th>客户端 TCP Mbps</th><th>LAN4 Mbps</th><th>busy</th><th>softirq</th><th>squeeze</th><th>UDP 回复/发送</th><th>RTT p95 ms</th></tr>'
report=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NSS82 · 受控工程闭环</title>
<style>body{{font-family:system-ui,"Microsoft YaHei",sans-serif;background:#f3f5f8;color:#182838;margin:0;line-height:1.7}}main{{max-width:1080px;margin:35px auto;padding:30px;background:white;border-radius:16px}}h1{{font-size:30px}}h2{{font-size:21px;margin-top:35px}}.lead{{padding:18px;background:#eaf5ee;border-left:4px solid #29764b}}table{{border-collapse:collapse;width:100%;font-size:14px}}th,td{{border-bottom:1px solid #dce2e8;padding:10px;text-align:left}}.scroll{{overflow:auto}}small{{color:#526274}}code{{background:#edf0f4;padding:2px 4px}}@media(max-width:700px){{main{{margin:12px;padding:18px}}}}</style>
<main><small>{now} 北京时间 · 实际测量 NSS79–82 · 实验已撤销</small><h1>自动分类 → NSS bulk/RT 队列：工程闭环已通过</h1>
<p class="lead">相同约18Mbps负载下，softirq从9.65%降至4.31%，恢复软件后回到9.48%。拥塞轮中bulk队列丢弃143、RT队列零丢弃，NSS段UDP213/213回复。工程调试不再依赖反复开Steam和CS2。</p>
<h2>相同负载的 A → B → A2</h2><p>A、A2为软件转发，B为ECM/NSS；同一TCP、UDP、WAN5，相同20Mbps QoS组和观察器，每段约5秒。ECM为0→2→0，TCP/UDP实际由常驻分类器判定BULK/RT，正确进入8f05/8f06 FQ-CoDel leaf。ct mark、NAT、PBR出口保持。</p><div class="scroll"><table>{header}{rows(matched)}</table></div><p>两段软件softirq均值9.57%，B为4.31%，相对下降54.97%。这是短窗18Mbps实测证据；time_squeeze全0，不能证明300Mbps高负载或长期稳定。</p>
<h2>32Mbps发送负载：测试限速和队列隔离</h2><p>仍是20Mbps受控组，bulk保障19Mbps、RT保障1Mbps并可借用到20Mbps，默认fallback950Mbps。一次只测试WAN2的一TCP一UDP，不改五WAN负载均衡。</p><div class="scroll"><table>{header}{rows(saturated)}</table></div><p>B观察bulk +8990包、drop143；RT +262包、drop0。leaf计数为异步B附近观测，不等同于严格五秒dequeue；发送32Mbps也不等于实际吞吐。三段实际吞吐不同，因此不以本轮CPU降幅验收收益。</p>
<h2>失败记录与修正</h2><ul><li>80第一次：TCP达到450MiB有限字节上限后退出，学习前精确TCP不在同源完整分类帧，UDP保留；没有开放NSS。</li><li>80第二次：三段都完成，但最后软件tag计数差一个ACK（1包/60字节）；错误标签计数全零，原失败保留。</li><li>81：初始软件计数差一个TCP-down包（1500字节），尚未执行A；恢复通过。单独的LF/CRLF预期SHA错误在写前修正，不是内核缺陷。</li><li>82：五个getter位置统一至多一次精确偏差重读；第二次必须通过原严格检查，错误tag或其它偏差直接拒绝。17项原生ACK案例通过；现场实际使用原down偏差分支，第二次一致。</li></ul>
<h2>恢复与当前配置</h2><p>五个现场stage各有新checkpoint下载/SHA/gzip核验，独立PPID1的45秒owner写前就绪；全部精确撤销和原完整保护审核通过。常驻NSS68未改，worker4859/guardian17139连续。最终source1.15秒、ECM关闭零计数，无事务/stage/state/实验模块；认证、PBR、NAT、sing-box、Tailscale和十个生产队列保持。</p><p>临时自有端点防火墙独立180秒恢复原基线，临时规则0、服务退出/端口关闭；客户端有限字节上限退出，精确客户端guard通过。没有新游戏下载、购买/卸载、桌面/HUD操作。完整私有源、CT/nonce/凭据/checkpoint留本地，脱敏证据和可读源码进入私有GitHub仓库。</p>
<h2>已证明与仍待验证</h2><p>已证明实际LAN→NAT→PBR→单WAN private MacVLAN的TCP/UDP能被ECM加速并进入正确NSS bulk/RT leaf；限速、拥塞丢弃和RT队列隔离有实际证据。自有UDP RTT约190–205ms受远端路径影响，不是CS2 jitter/loss/Miss。未证明精确限速误差、多流公平、ECN、host fairness、DiffServ或autorate替代；CAKE各tin未做分段包计数采样。</p><p>下一步直接提高单WAN受控预算，取得更接近实际WAN速率的同负载收益；再做一次集中真人CS2验收。多WAN共享预算、Wi-Fi、autorate随后评估。当前没有长期打开生产NSS。</p><small>HTML源与数据已校验；本轮未验证浏览器渲染。</small></main></html>'''
out=workspace/'outputs/nss82-mainline-report.html';out.write_text(report,encoding='utf-8')
assert '<title>NSS82' in report and '213/213' in report and '54.97%' in report
print(json.dumps({'saved':True,'newSources':len(hashes),'totalSources':len(manifest['sources']),
    'completeSuccessfulABAs':2,'preservedStagedCases':5,'softirqRelativeReductionPercent':reduction,
    'report':str(out),'privateBootstrapExcluded':True},ensure_ascii=False))
