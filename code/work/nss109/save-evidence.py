"""Append passive sequence localization and the declared auth repair honestly."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib,subprocess,shutil,importlib.util,html
w=Path(__file__).resolve().parents[2];repo=w/'athena-nss-mainline';root=w/'work/nss109'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
spec=importlib.util.spec_from_file_location('collector',w/'work/nss101/collect-lifecycle.py');collector=importlib.util.module_from_spec(spec);spec.loader.exec_module(collector)
closures=[collector.closure(load(w/f'work/nss{n}/load-latest-private.json')['dir'])for n in [108,109]]
final=load(root/'v3-final-health.json');repair=load(w/'work/nss108/auth-repair-latest-private.json');qual=load(w/'work/nss108/auth-qualification.json');path=load(root/'path-localization.json');cleanup=load(root/'tap-cleanup.json');late=load(root/'late-auth-private.json');failover=load(root/'v3-wan4-failover-proof.json')
assert final['passed']and final['originalFullLockedNativeAudit']and final['unrelatedConfigurationMatches']and final['ecmStoppedAndZero']and not final['nssAdmissionAllowed']and not final['allFiveWanHealthy']
assert all(final[k]for k in ['noActiveTransaction','noStaging','noExperimentState','noExperimentalModule'])
assert repair['committed']and repair['independent180SecondRollbackVerifiedBeforeWrite']and not repair['authenticatorRestarted']and not repair['naturalRollbackTested']
assert qual['originalMissingPidExitCode']==1 and not qual['originalMissingPidBranchReached']and len(qual['checks'])==6
assert path['totalEligibleRequests']==484 and path['totalMissingBeforeEarliestRouterTap']==19 and path['routerSoftwareQueueMissingObserved']==0
assert late['latestRecovery']['result']==0 and not late['up']and not late['ipv4Present']
# Retain exact new sources and private run inputs locally. No secret, binary,
# manifest contents, nonce, credential or checkpoint is copied to the Git repo.
private=root/'proof-v1/private-inputs';private.mkdir(parents=True,exist_ok=False)
private_hashes={}
for n in [108,109]:
 for src in sorted((w/f'work/nss{n}').rglob('*')):
  if not src.is_file()or 'proof-v1'in src.parts or '__pycache__'in src.parts:continue
  rel=src.relative_to(w);dst=private/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);private_hashes[rel.as_posix()]=sha(src.read_bytes());assert sha(dst.read_bytes())==private_hashes[rel.as_posix()]
dump(root/'private-input-freeze-index.json',private_hashes)
old=(repo/'evidence/current-runtime.json').read_bytes();assert load(repo/'evidence/current-runtime.json')['round']=='NSS107';assert subprocess.check_output(['git','show','HEAD:evidence/current-runtime.json'],cwd=repo)==old
archive=repo/'evidence/nss107-runtime.json';assert not archive.exists();archive.write_bytes(old)
manifest_path=repo/'source-manifest.json';manifest=load(manifest_path);assert len(manifest['sources'])==1155
prefix=sha(json.dumps(manifest['sources'],sort_keys=True,separators=(',',':')).encode())
allowed={108:['qualify-auth.mjs','auth-before.sh','auth-candidate.sh','install-auth-repair.mjs','complete-auth-repair.mjs','status-auth.mjs','read-auth-latest.mjs','download-auth-logs.mjs','auth-keywords.py','udp-path-tap.c','test-path-filter.py','stage-path-tap.mjs','capture-path.mjs'],109:['udp-path-tap.c','stage-path-tap.mjs','capture-path.mjs','run-diagnostic.mjs','analyze-path.py','cleanup-taps.mjs','final-health.mjs','failover-baseline.mjs','diagnose-closure-drift.py','failover-nonbucket-diff.py','read-script-inventory.mjs','read-failover-sources.mjs','read-health-controller-status.mjs','late-auth-status.mjs','health-controller.lua','pbr-ensure.sh','save-evidence.py']}
sources={}
for n,names in allowed.items():
 for name in names:
  src=w/f'work/nss{n}/{name}';rel=src.relative_to(w).as_posix();dst=repo/'code'/rel;assert not dst.exists();dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);digest=sha(src.read_bytes());assert sha(dst.read_bytes())==digest;sources[rel]=digest
  manifest['sources'].append({'path':'code/'+rel,'workspaceSource':rel,'sha256':digest,'bytes':src.stat().st_size,'role':'passive-RT-sequence-localization-and-scoped-auth-recovery'})
manifest['generatedAt']=datetime.now(timezone.utc).isoformat();manifest['lastAppendExport']='NSS109';dump(manifest_path,manifest)
auth={k:v for k,v in repair.items()if k not in ['id','localDir','checkpoint','stagePath']};auth['qualification']=qual;auth['latestNaturalRecoveryRequest']={**late['latestRecovery'],'authenticationSucceeded':False};auth['missingPidBranchActuallyReachedInNaturalRetryProved']=False
initial_capture=next((w/'work/nss108/load-20261005164437-2dfc18e426e4a114').glob('path-*-router-raw-private.json'));raw=load(initial_capture);cap=json.loads(raw['stdout'].strip().splitlines()[-1]);assert cap['socketDrops']==160 and not cap['passed']
instrument={'firstCaptureAccepted':False,'firstCaptureSocketDrops':160,'firstCaptureExitCode':raw['code'],'firstRouterRawSha256':sha(initial_capture.read_bytes()),'firstServerCompletedCaptureRetained':False,'firstServerInterruptedOnRouterFailure':True,'correctedOnlySocketSubscriptionOrder':True,'receiveEnabledAfterSocketFilterInstalled':True,'qualifiedNewCaptures':2,'qualifiedCaptureDrops':[0,0],'hostParserCases':6,'targetParserCases':6,'wslAfPacketKernelTestSupported':False,'actualRouterAfPacketAndBpfVerified':True,'noPromiscuousOrTcOrInterfaceChange':True,'captureMaximumSeconds':12,'shellMaximumSeconds':14,'independentStageCleanupSeconds':480,'failedUncompressedManifestStageBeforeProductionMutation':True,'successfulRepairInputsRetained':True,'firstUncompressedInstallerVariantPreRunFrozen':False,'rawDynamicNativeFilterTextComparisonRefusalPreserved':True,'originalNativeOwnershipAuditStillRequired':True}
source_proof={'round':'NSS109','sources':len(sources),'sourceHashes':sources,'historicPrefixSources':1155,'historicPrefixCanonicalSha256':prefix,'privateOwnedHostBootstrapExcluded':True,'successfulRepairAndCaptureCurrentSourcesAndPrivateInputsRetained':True,'privateInputCount':len(private_hashes),'prewriteUncompressedInstallerVariantNotClaimedFrozen':True,'firstInterruptedServerCaptureNotClaimedComplete':True,'notAdditionalProductionAdmission':True}
main={'round':'NSS109','observedAt':final['observedAt'],'routerSequenceCapturePassed':True,'eligibleRequests':484,'missingBeforeEarliestRouterLinuxTap':19,'missingInObservedRouterDownstreamChain':0,'routerPhysicalNicVsUpstreamSeparated':False,'authenticationRecoveryPidBugFixed':True,'wan4AuthenticationRecovered':False,'fourWanAutomaticFailoverExactSourceModelPassed':True,'nssOpenedThisTurn':False,'newMatchedABA':False,'newCpuComparisonAccepted':False,'sameWanCongestionComparison':False,'tcpBulkWan':3,'udpRtWan':2,'previous32And48CpuEvidenceRetained':True,'humanCs2Acceptance':False,'highLoad300MbpsAcceptance':False,'fullCakeReplacementAccepted':False,'onlyLan4DownlinkQosProvenHistorically':True,'acceleratedUplinkQosGuaranteed':False,'residentClassifierChanged':False,'nssPermanentlyEnabled':False,'temporaryEndpointsClosed':2,'independentRollbackAndStageCleanupVerifiedBeforeWrite':True,'old107RuntimeExactBytesArchived':True,'upstreamSubmitted':False,'reportVerification':{'sourceValidated':True,'browserRendered':False}}
for name,value in {'mainline':main,'path-localization':path,'auth-repair':auth,'instrumentation':instrument,'wan4-failover':failover,'endpoint-closure':closures,'stage-cleanup':cleanup,'final-audit':final,'source-proof':source_proof}.items():dump(repo/f'evidence/nss109-{name}.json',value)
runtime={'round':'NSS109','checkedAt':final['observedAt'],'deploymentReference':'work/nss68/deployment-latest.json','classifierConfigSha256':final['configSha256'],'workerPid':4859,'guardianPid':17139,'nssPermanentlyEnabled':False,'residentClassifierChangedThisTurn':False,'authRecoverySourceChangedAndCommitted':True,'authRecoverySha256':repair['newAuthSha256'],'protectedManifestSha256':repair['newManifestSha256'],'historicalQualifiedExperimentalEntry':'work/nss105/controlled-session.mjs','historicalQualifiedExperimentalEntryBoundInputs':662,'currentNssAdmissionQualified':False,'historicalEntryMustAdoptDeclaredAuthRepairAndActualFailoverBaselineBeforeWrite':True,'automaticWanAffinityOwner':'Existing Linux PBR health controller','wan4Up':False,'allFiveWanHealthy':False,'newCpuComparisonAccepted':False,'realHumanGameAcceptance':False,'audit':final,'historical107RuntimePreservedSha256':sha(old),'historical98RuntimePreservedSha256':sha((repo/'evidence/nss98-runtime.json').read_bytes()),'historical92RuntimePreservedSha256':sha((repo/'evidence/nss92-runtime.json').read_bytes()),'historical82RuntimePreservedSha256':sha((repo/'evidence/nss82-runtime.json').read_bytes())};dump(repo/'evidence/current-runtime.json',runtime)
when=datetime.fromisoformat(final['observedAt'].replace('Z','+00:00')).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
summary=f'''更新：{when}，北京时间。最新NSS109；常驻仍68/config581b5d46…c791d7，ECM关闭全零，无实验残留。

**两次实际8秒nonce/序号捕获定位到：484个请求均到服务器并发出echo；路由器最早Linux物理接口tap只见465个，之后private WAN→IFB→bridge→LAN→PC全部465个相同，链内缺包零。19/484（约3.93%）缺口在server软件TX→router最早Linux tap之间；上游链路与网卡接收早期尚未分开。**

见 [序号证据](../evidence/nss109-path-localization.json)、[认证修复](../evidence/nss109-auth-repair.json)、[自然故障切换](../evidence/nss109-wan4-failover.json)、[捕获器边界](../evidence/nss109-instrumentation.json)、[关闭](../evidence/nss109-endpoint-closure.json)、[终态](../evidence/nss109-final-audit.json)。

- 首窗236发/227收，后窗248发/238收；内部窗口裁掉首1秒/尾2秒，使用最终PC日志和确切nonce序号，不假定服务器/路由器UTC同步。对应TCP44.407/47.999Mbps、UDP p95约209.51/209.35ms。自动分类实际TCP BULK WAN3、UDP RT WAN2：这是软件路径定位，非同WAN拥塞对照；没有NSS leaf、同窗CPU/softirq/squeeze或真人CS2新验收。
- NSS108首次捕获自身drops160、退出2，不能作缺包定位；其server捕获被异常中断，不称完整保留。109只修socket接收顺序：protocol0→socket filter→bind ETH_P_ALL，两次实际drops0、九接口方向可见。host/目标解析同6例通过；WSL不支持AF_PACKET的实际socket测试失败，未把它称通过。helper本身最多12秒、外部14秒，checkpoint和独立480秒临时目录清理先于上传；108观察到到期后自然消失、109owner/inode核验后取消。
- 写前发现WAN4认证进程无PID，旧恢复脚本set -e让jsonfilter缺失字段的退出1跳过空PID分支。真实最小复现与6目标RAM结构案例通过，只改PID读取为校验ubus结构的Lua；保护清单仅更新对应一行。checkpoint下载/SHA/gzip、独立180秒撤销写前验证，原完整native审核、单独SSH和其它运行配置核验后保留。没有主动重启认证/接口，本轮未做新的自然180秒回滚。写后原始动态tc文字比较失败保留，随后用原完整ownership审核验证动态selector。
- 现有watchdog在修复后一次自然恢复请求返回0，但WAN4仍认证失败/接口down，无IPv4；不称五WAN恢复。原健康控制器权重[100,100,100,0,100]，300桶按实际源码严格复现为四路各75桶，仅60个旧WAN4桶重派、healthy移除WAN4、3个WAN4 DHCP路由规则消失，固定ct mark规则保留。是既有故障切换，非实验写PBR。原全5WAN旧快照严格审核的拒绝保留；本轮对声明修复和精确自动切换后的其它配置/原完整native审核通过，不是新的NSS入口资格。
- 终态worker4859/guardian17139/source{final['queryAge']:.2f}，ECM stop1/所有count0，无事务/stage/state/实验模块。两个端点FW180秒独立恢复、client210秒退出、unit/端口关闭均通过；凭据/实际端点配置/CT/nonce/二进制/检查点/完整清单留本地。
- 历史32Mbps约66.41%与48Mbps B/A2约72.19% softirq收益保持；本轮没有加速写入/新收益/真人指标。仅LAN4下行/upTag0的缺口保持。旧107/98/92/82 runtime逐字节保留。下一步回到实际四路基线下的单WAN入口和NSS QoS预算/关键上行，不再用这两窗约4%缺包要求反复调整CAKE；最后一次集中真人验收，不扩WAN/Wi-Fi/autorate/共享全局预算。
'''
for name in ['STATE.md','PLAN.md','ARTIFACT_INDEX.md']:
 p=repo/'docs'/name;previous=p.read_text(encoding='utf-8')
 if name=='STATE.md':text='# 当前状态\n\n'+summary+'\n## NSS107历史状态\n\n'+previous
 elif name=='PLAN.md':text='''# 下一步：接回单WAN NSS QoS主线

NSS109两次捕获已缩小约4%受控echo缺口的位置，见 [STATE](STATE.md)。现有软件队列链内没有对应缺包；此echo不能代表真人CS2，上游与网卡早期仍未区分。

1. 保留68分类器与已修复auth PID读取，沿既有认证/学校政策恢复WAN4；不改凭据、不重复强制认证、不触发五路重启。对实际健康四路采用明确前置epoch并绑定声明的auth/manifest修复及300桶自然故障切换，不能把原105旧入口的历史资格视为当下准入，也不能覆盖旧冻结证明。
2. 尽快回到已通过的单WAN bulk/RT工程闭环：选健康WAN、真实一TCP一UDP同WAN，学习前tag/ct mark/NAT/WAN affinity精确，期限和默认拒绝不变。只验证未完成的同WAN预算与NSS关键上行范围；已有CPU收益不反复重做轻载准备。
3. 19个缺包不支持发生在已观测software IFB/CAKE或PC接收链；别以修改CAKE或放宽ECM入口解决这个外部缺口。额外网卡早期/上游定位列为非阻塞证据，不扩扫描、改学校网络政策或用未知端点。
4. 工程条件具备后只集中一次真人CS2＋正常下载，采真实HUD jitter/loss/Miss与体验；当前未完成真人验收、300Mbps或完整CAKE替代，实际upTag0仍需说明。
5. 多WAN、共享全局预算、Wi-Fi、autorate、ECN/bridge/HTB backlog仍后置，不新下载或重装维持准备。

## NSS107历史计划

'''+previous
 else:text='# 当前NSS109\n\n[汇总](../evidence/nss109-mainline.json) · [序号](../evidence/nss109-path-localization.json) · [修复](../evidence/nss109-auth-repair.json) · [故障切换](../evidence/nss109-wan4-failover.json) · [终态](../evidence/nss109-final-audit.json) · [源码](../evidence/nss109-source-proof.json) · [历史107 runtime](../evidence/nss107-runtime.json)。本地报告 outputs/nss109-mainline-report.html。\n\n'+previous
 p.write_text(text,encoding='utf-8')
p=repo/'docs/EXPERIMENT_LOG.md';head,tail=p.read_text(encoding='utf-8').split('\n',1);p.write_text(head+f'\n\n## NSS108–109 · {when} · 精确UDP路径定位与认证恢复修复\n\n'+summary+tail,encoding='utf-8')
p=repo/'AGENTS.md';head,tail=p.read_text(encoding='utf-8').split('\n',1);p.write_text(head+'\n\n最新NSS109：两次实际8秒捕获484请求/484serverTX，router最早Linux tap465，之后private WAN/IFB/bridge/LAN/PC均465，19缺口前于tap，上游与NIC早期未分开。TCP44.407/47.999Mbps，BULK WAN3/RT WAN2，非同WAN/NSS/CPU/真人验收。首108自身capture drops160拒绝且server提前中断保留；109先filter后接收两次drops0。auth-recover PID缺失set-e故障仅查询修复并保留，checkpoint/180秒独立撤销/SSH/native审核，保护manifest一行改变；自然恢复请求后返回0但WAN4仍down，不称认证恢复。既有健康控制器[100,100,100,0,100]的300桶严格源码模型通过，四路75/75/75/0/75，旧全5WAN审核拒绝保留。终态4859/17139/config不变，ECM关闭全零、无残留，两端点关闭；旧107/98/92/82 runtime保持。105/662仅历史资格，新写前须绑定声明auth修复和实际四路基线。下一步接回单WANNSS预算/关键上行与最终一次真人，不扩WAN/共享预算/新下载/重装；STATE为准。\n\n'+tail,encoding='utf-8')
issue=repo/'docs/issues/auth-recover-missing-pid.md';issue.parent.mkdir(exist_ok=True);issue.write_text('''# auth-recover.sh：PID字段缺失导致恢复提前退出

仓库：本私有项目；目标文件 `/root/router-project/scripts/auth-recover.sh`。不是已证明的Linux/ECM/NSS上游缺陷，未提交上游。

触发：procd实例不运行，service list返回实例对象但没有pid。旧脚本在set -e下把jsonfilter结果赋给pid；字段缺失时退出1，跳过随后已有的空PID分支。

最小复现（无认证动作）：

```sh
set -eu
pid=$(printf '%s' '{"router-project-minieap":{"instances":{"wan4":{"running":false}}}}' | jsonfilter -e '@["router-project-minieap"].instances.wan4.pid')
printf 'EMPTY_BRANCH_REACHED:%s\\n' "$pid"
```

实际目标shell退出1，未打印EMPTY_BRANCH_REACHED。修复只将PID查询换成原生ubus/Lua结构校验，允许pid缺失，查询/结构错误仍失败。6目标RAM案例覆盖有效PID、缺PID、缺实例、错误PID、缺instances、缺服务；不是实际认证成功证明。

实际安装有checkpoint与独立180秒撤销，保护清单只更新目标一行；单独SSH、源码SHA、其它配置和原完整native ownership审核通过后commit。未主动重启认证或接口，未测试本轮自然180秒撤销。后续watchdog一次自然恢复请求返回0；WAN4仍认证失败/down，学校账户/上游认证原因未定，不能把修脚本称为认证恢复。

证据：[修复和资格](../../evidence/nss109-auth-repair.json)、[源码](../../evidence/nss109-source-proof.json)、[终态](../../evidence/nss109-final-audit.json)。
''',encoding='utf-8')
table=''.join(f'<tr><td>{i+1}</td><td>{t["tcpActualMbps"]:.3f}</td><td>{t["counts"]["serverEgress"]}</td><td>{t["counts"]["physicalWanDown"]}</td><td>{t["counts"]["lanDown"]}</td><td>{t["counts"]["pcReceived"]}</td><td>{t["socketDrops"]}</td></tr>'for i,t in enumerate(path['trials']))
report=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NSS109 UDP缺包定位</title><style>body{{margin:0;background:#f4f4ee;color:#25352e;font:16px/1.8 "Microsoft YaHei",sans-serif}}main{{max-width:1000px;margin:auto;padding:35px 24px}}section{{background:#fff;padding:24px;border:1px solid #dadfd7;border-radius:10px;margin:24px 0}}h1{{font-size:30px}}h2{{font-size:23px}}table{{width:100%;border-collapse:collapse;font-variant-numeric:tabular-nums}}th,td{{text-align:left;padding:8px;border-bottom:1px solid #ddd}}small{{color:#617166}}a{{color:#326649}}@media(max-width:700px){{main{{padding:20px 10px}}th,td{{font-size:12px;padding:4px}}}}</style><main><small>ATHENA AX6600 · {when} 北京时间</small><h1>缺包位置已缩小到路由器最早捕获点之前</h1><p>两轮484个请求全部到服务器并发出echo；465个回包进入路由器最早Linux物理接口tap，之后全部交付电脑。观察到的内部软件路径没有再少包。</p><section><h2>实际序号对齐</h2><table><tr><th>窗</th><th>TCP Mbps</th><th>服务器发</th><th>WAN tap</th><th>LAN发</th><th>PC收</th><th>捕获drop</th></tr>{table}</table><p>每轮capture约8秒，按路由器上行中央1–6秒的有效nonce序号取交集；使用最终PC日志，避免边界在途包。两轮丢9和10，约3.81%和4.03%。private WAN、IFB、bridge、LAN与PC收到的序号集合严格相同。</p><p>实际BULK TCP在WAN3、RT UDP在WAN2，不是同WAN拥塞或NSS A/B。UDP echo p95约209.5ms是远端路径指标，不是CS2。没有同步CPU/softirq/time_squeeze或CAKE/NSS tin的新比较。</p></section><section><h2>能得出的结论</h2><p>在这两窗中，缺口位于server软件TX捕获到router最早Linux物理tap之间，不支持现有IFB/CAKE链或电脑接收是缺口位置。仍不能区分上游链路、网卡/驱动更早丢弃，也不能由server软件TX直接证明线缆实际发送。</p><p>捕获器只记录精确端点/UDP端口/nonce序号，无注入、混杂模式、tc、路由或接口更改。初版自身drop160已拒绝，改成protocol0→安装socket filter→bind ETH_P_ALL后，两轮drop0。<a href="https://www.man7.org/linux/man-pages/man7/packet.7.html">Linux packet(7)</a>说明了protocol0、bind启用接收、PACKET_OUTGOING和packet statistics的这些观测边界。</p></section><section><h2>WAN4认证故障与修复边界</h2><p>写前已有WAN4进程无PID。旧auth-recover脚本的set-e使jsonfilter缺PID的退出1提前终止。真实最小复现和6目标RAM案例验证后，仅替换PID读取；checkpoint、SHA/gzip、180秒独立撤销写前验证，保护清单仅改变对应一行，原完整native审核及独立SSH通过后保留。</p><p>没有主动重启认证/接口，也没有本轮新的自然180秒回滚。后续原watchdog自然恢复请求返回0，但WAN4仍认证失败/down，无IPv4，不能称认证恢复。既有健康控制器按源码精确转为四路各75桶，WAN4的60桶重派；三条WAN4 DHCP规则消失，固定ct mark规则保留。</p></section><section><h2>终态和主线</h2><p>分类器68仍4859/17139/config581b5d46…c791d7，source{final['queryAge']:.2f}秒。ECM关闭全零，无事务/stage/state/实验模块。两个端点独立FW180秒恢复、client210秒退出、unit/端口关闭。初版临时目录在独立到期后已消失，新版按owner/inode核验后清理。</p><p>终态通过的是声明auth修复与源码模型已证明的自然故障切换之后，其它配置及原完整native ownership审核；旧全5WAN严格审核失败仍保留，不是新NSS写入资格。105/662历史入口须对齐这些实际前置状态后再用。</p><p>下一步回到单WANbulk/RT入口、预算和关键上行；不再把这两窗约4%缺包当作CAKE调参目标。既有32/48Mbps可比softirq收益保持，本轮没有新CPU、真人CS2或300Mbps结论，实际upTag0/完整CAKE替代尚未通过。最终体验只集中一次，不用长期挂Steam/CS2。</p><p><a href="https://github.com/ZyPulse-zy/athena-nss-mainline/blob/main/docs/STATE.md">私有仓库最新状态</a></p><small>报告源码核验；未通过浏览器渲染验收。完整端点配置/nonce/CT/凭据/二进制/检查点/清单保持私有。</small></section></main></html>'''
output=w/'outputs/nss109-mainline-report.html';assert not output.exists();output.write_text(report,encoding='utf-8')
dump(root/'export-receipt.json',{'passed':True,'sources':len(sources),'totalSources':len(manifest['sources']),'historic1155PrefixPreserved':True,'privateFrozenFiles':len(private_hashes),'old107RuntimeSha256':sha(old),'eligibleRequests':484,'missingBeforeEarliestLinuxTap':19,'browserRendered':False})
print(json.dumps({'exported':True,'sources':len(sources),'totalSources':len(manifest['sources']),'privateFrozenFiles':len(private_hashes),'endpointsClosed':2}))
