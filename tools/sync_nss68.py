"""Export only reviewed sources and sanitized NSS68 evidence; preserve old bytes."""
from pathlib import Path
import argparse,json,hashlib,shutil
from datetime import datetime,timezone
ap=argparse.ArgumentParser();ap.add_argument('workspace',type=Path);workspace=ap.parse_args().workspace.resolve()
root=Path(__file__).resolve().parents[1]
read=lambda p:json.loads((workspace/p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(path,obj):(root/path).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
history=root/'evidence/nss67-runtime.json';current=root/'evidence/current-runtime.json'
if not history.exists():
    assert json.loads(current.read_text(encoding='utf-8'))['round']=='NSS67';shutil.copyfile(current,history)
assert json.loads(history.read_text(encoding='utf-8'))['round']=='NSS67'
proof=read('work/nss68/source-proof-v1.json');assert proof['sources']==23 and proof['candidateRetainedAtEnd']
manifest=json.loads((root/'source-manifest.json').read_text(encoding='utf-8'));items={x['path']:x for x in manifest['sources']}
for source,expected in proof['sourceHashes'].items():
    src=workspace/source;frozen=workspace/'work/nss68/proof-v1/code'/src.name
    assert sha(src)==sha(frozen)==expected and 'private' not in src.name
    dst=root/'code'/source;dst.parent.mkdir(parents=True,exist_ok=True);key=dst.relative_to(root).as_posix()
    if key in items:assert items[key]['sha256']==expected
    shutil.copyfile(frozen,dst);items[key]={'path':key,'workspaceSource':source,'sha256':expected,'bytes':src.stat().st_size,'role':proof['role']}
data=read('outputs/nss68-mainline-observations.json');entry=read('work/nss68/entry-qualified.json');audit=data['finalState']['protectedAudit']
assert data['candidateRetainedAtEnd'] and data['retention']['remoteCommittedReceiptVerified'] and not data['nssOpenedThisTurn']
assert data['entry']['boundInputs']==257 and data['workerLifecycle']['naturalRestartObserved'] and audit['passed']
save('evidence/nss68-mainline.json',data);save('evidence/nss68-source-proof.json',proof);save('evidence/nss68-entry-binding.json',entry);save('evidence/nss68-final-audit.json',audit)
runtime={'round':'NSS68','checkedAt':audit['observedAt'],'deploymentReference':data['deploymentReference'],'classifierConfigSha256':data['classifierConfigSha256'],'candidateWorkerSha256':data['candidateWorkerSha256'],
 'audit':{**audit,'protectedConfigurationUnchanged':audit['configurationMatches'],'exactOwnedNativeAudit':audit['originalFullLockedAudit'],'ecmClosedAndZero':audit['ecmStoppedAndZero']},
 'finalClosure':{'passed':all(data['finalState'][k]for k in ['noActiveTransaction','noStage','noExperimentalModule','noState','ecmClosedAndZero'])},
 'workerPid':audit['workerPid'],'guardianPid':audit['guardianPid'],'publicationCandidateInstalled':True,'candidateEntryBindingCreated':True,'permanentClassifierChangedThisTurn':True,'nssOpenedThisTurn':False,
 'qualifiedExperimentalEntry':'work/nss68/real-session.mjs','qualifiedExperimentalEntryBoundInputs':257,'entryPreparationQualified':True,'entryFullHighLoadForwardingQualified':False,'entryReadOnlyPrewriteAndRecoveryQualified':True,
 'naturalWorkerRestartObservedThisTurn':True,'sameWorkerSinceRetainedInstallation':False,'sameWorkerAcrossLatestEntryAudits':True,
 'nssPermanentlyEnabled':False,'completePerformanceAndGameAcceptance':False,'steamDownloadControlledThisTurn':True,'clientDownloadFinallyPaused':True,'gameStartedThisTurn':False,'realHumanMetricsAvailable':False,
 'above300MbpsPublicationObservedThisTurn':False,'historical67Above300MbpsPublicationObserved':True,'generalLongTermStabilityProved':False,'requiresLiveRevalidation':True,'historical67RuntimePreservedSha256':sha(history)}
save('evidence/current-runtime.json',runtime)
manifest.update({'sources':list(items.values()),'lastAppendExport':'NSS68','generatedAt':datetime.now(timezone.utc).isoformat(),'privateDataExcluded':True});save('source-manifest.json',manifest)
assert len(items)==868
brief="最新NSS68（下方67及更早为历史）：publication候选32,019字节已实际保留，部署work/nss68/deployment-latest.json、config581b5d46…c791d7；workerSHA40169c…3828。checkpoint下载/SHA/gzip、独立180秒守护写前核验，原完整审核和远端commit读回通过；本轮没有新自然回滚，复用66/67证据。四模块不变，47/49旧引用原字节不覆盖。新入口work/nss68/real-session.mjs原241+16=257项，17新绑定检查通过，消费者/原完整审核/stage同一明确committed部署；现场只读准入source1.46和恢复1.26通过，未执行新的NSS stage或ECM放行。17138自然退出：10:32:50 tc child cleanup未获证明，apply256/4.35秒，先于下载，TC监督与47同字节；自动恢复23634/17139，长期稳定未验收，不能归因JSON或下载。现有黎明杀机恢复界面瞬时312后回暂停，真实4秒2.879Mbps/425pps；审核0.587Mbps，不是高负载证明。下载已暂停0bps、360秒客户端守护观察暂停后取消；未开CS2/新下载/购买/卸载，无HUD/真人或CPU收益。10:37原完整终态source3.24通过，ECM关闭全零，无事务/stage/state/模块。23新源/累计868，12私有运行输入及257绑定输入冻结，旧67runtime原字节保持。下一步直接集中真人CS2+现有Steam单WAN同负载A/B/A2，每轮读新实例；不重装/重放/扩WAN。STATE为准。"
for p in [workspace/'AGENTS.md',root/'AGENTS.md']:
    text=p.read_text(encoding='utf-8');anchor='- 最新NSS66–67'if p==workspace/'AGENTS.md'else'最新NSS66–67'
    assert anchor in text
    insertion=('- 'if p==workspace/'AGENTS.md'else'')+brief+'\n'+(''if p==workspace/'AGENTS.md'else'\n')
    if '最新NSS68'not in text:text=text.replace(anchor,insertion+anchor,1)
    p.write_text(text,encoding='utf-8',newline='\n')
state='''更新：2026-10-05，北京时间。最新为NSS68；下方67及更早为历史。

**发布候选已实际长期保留，新的257项入口已经绑定同一个committed部署，现场原完整准入/恢复审核通过。NSS仍关闭；真人同负载闭环尚未验收。**

见 [本轮实测](../evidence/nss68-mainline.json)、[新入口绑定](../evidence/nss68-entry-binding.json)、[终态审核](../evidence/nss68-final-audit.json) 和 [调用位置](PUBLICATION_ENTRY_HANDOFF.md)。

- 当前部署 `work/nss68/deployment-latest.json`，config `581b5d46c9d3772ccd94f5f36510bccf665899f210c43b4deaa5155067c791d7`，32,019字节worker SHA `40169ce6c8e866cc989c651b24d435777bc422bf10f67c58f5e9ab033e7f3828`。旧47/49引用只作历史，未覆盖。
- 一个checkpoint下载/SHA/gzip，独立480秒stage和180秒生产undo写前核验；原完整持锁审核source2.49通过后远端commit、配置/worker/pointer读回验证，候选留驻，常驻健康守护保留。本轮没有再测自然180秒撤销；66/67自然恢复证明保持。只按owner/inode取消已提交后的passive stage。
- 入口 `work/nss68/real-session.mjs` 原241项全部保留，新16项、共257，17绑定检查通过。分类读取、原完整审核、stage共同使用新committed部署；原Lua消费者、stage/payload与1/2/6/9秒、200ms child、20Mbps、一TCP一UDP、45秒owner均不变。实际只读准入source1.46秒、同producer恢复审核1.26通过，未运行新NSS stage，不能称高负载gate已验收。
- 10:32:50–52候选17138自然退出，日志为 `tc child cleanup not proved`，apply256、4.35秒。原47相同TC监督代码也有历史apply失败；该次发生在本轮恢复下载之前。只有边界证据，没有具体tc命令、child PID和阻塞栈，不能归因发布改动、下载或内核。自动恢复后23634/17139，最新准入/恢复同producer，长期稳定未验收。见 [监督记录](ISSUE_TC_SUPERVISION.md)。
- 现有暂停的黎明杀机恢复，界面瞬时312Mbps后回到暂停；真实4秒仅2.879Mbps/425pps、busy34.91/softirq7.46/squeeze0；实际审核窗0.587Mbps，未形成300Mbps对照。没有CS2、HUD、真人或NSS CPU收益。暂停原因未确认，不称助手主动暂停；观察到暂停和0bps才取消独立360秒客户端守护。
- 10:37:28原完整终态审核source3.24通过，ECM关闭全零，无事务/stage/state/实验模块，五WAN认证/PBR/NAT/十个生产qdisc与保护配置保持。23份白名单源累计868，12份完整私有运行输入和257绑定输入冻结；旧67runtime原字节保留。
- 下一步直接使用新68入口做一次集中真人CS2+现有下载同TCP/UDP、单WAN可比A/B/A2。新轮次先读实际worker/guardian/producer；实验期间producer更换必须拒绝并精确恢复。不要再试装相同publication、重放旧准备、装新游戏或扩WAN。

## NSS66–67历史

'''
sp=root/'docs/STATE.md';s=sp.read_text(encoding='utf-8');sp.write_text('# 当前状态\n\n'+state+s.removeprefix('# 当前状态\n\n'),encoding='utf-8',newline='\n')
plan='''# 下一步：直接集中真实CS2＋现有下载单WAN闭环

NSS68已保留候选并绑定新入口，17检查与现场原完整准入/恢复审核通过。当前23634/17139、ECM关闭全零。无需重复publication试装或旧准备。见 [状态](STATE.md)。

1. 读实际 `work/nss68/deployment-latest.json`，核验原完整持锁审核、guardian、producer、保护配置和无残留。旧47/49/过期trial仅是历史，不能当现网引用。
2. 只使用 `work/nss68/real-session.mjs` 与一次真实CS2＋已有黎明杀机下载。原241+16共257输入和全部原来源/owner/流量门槛保持；没有当前真实同WAN配对即不stage或放行，不能用合成流授予资格。
3. 新checkpoint和独立45秒owner，记录software→NSS→software三段相同TCP/UDP和WAN，实际bulk/RT leaf、ct mark/NAT/affinity、加速0→2→0；producer在实验中变化即拒绝、撤销、重新学习，不能复用旧帧。
4. 同窗口HUD jitter/loss/Miss与真人体验、LAN4/单WAN/受控份额、softirq/time_squeeze/吞吐均完整并可比后才判断收益。助手观战和低负载读数不是真人验收。未通过前不扩第二WAN/共享预算/Wi-Fi/autorate。
5. 本轮自然tc回收失败保存诊断；命令/child PID/阻塞栈缺失，不扩大时限或旁路守护。若再次发生在目标短测内，先精确恢复并定位本项目监督边界，保持主线。

## NSS67历史计划

'''
pp=root/'docs/PLAN.md';pp.write_text(plan+pp.read_text(encoding='utf-8'),encoding='utf-8',newline='\n')
handoff=root/'docs/PUBLICATION_ENTRY_HANDOFF.md';handoff.write_text('# NSS68：实际部署与统一入口绑定已完成\n\n`work/nss68/deployment-latest.json` 是当前committed引用，worker/config/pointer实际读回和原完整审核已验证。新 `read-real-candidates.mjs`、`current-audit-diagnostic.mjs`、`module-stage.mjs` 和调度hint统一调用 [部署校验](../code/work/nss68/deployment-binding.mjs)。旧47/49与过期67trial保持历史，不能替代新引用。\n\n原241+16共257输入、17新验证、现场原完整准入与恢复检查通过。新NSS stage未执行；高负载 gate、完整可比A/B/A2与真人收益仍未验收。见 [NSS68](../evidence/nss68-mainline.json)。\n\n## NSS67接续问题历史\n\n'+handoff.read_text(encoding='utf-8'),encoding='utf-8',newline='\n')
idx=root/'docs/ARTIFACT_INDEX.md';idx.write_text('# 证据索引\n\n## 当前：NSS68\n\n- [实际保留与自然恢复记录](../evidence/nss68-mainline.json)、[当前运行](../evidence/current-runtime.json)、[终态原审核](../evidence/nss68-final-audit.json)。\n- [257项入口绑定](../evidence/nss68-entry-binding.json)、[23份白名单源码](../evidence/nss68-source-proof.json)、[接续位置](PUBLICATION_ENTRY_HANDOFF.md)。\n- [NSS67 runtime原字节](../evidence/nss67-runtime.json)保持。新入口和保留已完成，真实高负载NSS A/B/A2尚未完成。\n\n'+idx.read_text(encoding='utf-8').removeprefix('# 证据索引\n\n'),encoding='utf-8',newline='\n')
rd=root/'README.md';r=rd.read_text(encoding='utf-8');rd.write_text(r.replace('# Athena NSS Mainline\n','# Athena NSS Mainline\n\n最新 [NSS68](evidence/nss68-mainline.json)：发布候选已实际保留，新257项入口与现场完整准入/恢复审核通过。ECM仍关闭，记录一次自动恢复的tc回收失败；真实同负载真人CS2＋Steam闭环仍待完成。先读 [STATE](docs/STATE.md)、[PLAN](docs/PLAN.md)，下面67及更早为历史。\n',1)if r.startswith('# Athena NSS Mainline')else r.split('\n',1)[0]+'\n\n最新 [NSS68](evidence/nss68-mainline.json)：发布候选已实际保留，新257项入口与完整准入/恢复审核通过；ECM关闭。记录一次自然tc回收失败与自动恢复，真人同负载闭环未验收。先读 [STATE](docs/STATE.md)、[PLAN](docs/PLAN.md)，下面67及更早为历史。\n\n'+r.split('\n',1)[1],encoding='utf-8',newline='\n')
log=root/'docs/EXPERIMENT_LOG.md'
with log.open('a',encoding='utf-8',newline='\n')as f:f.write('\n## 2026-10-05 NSS68：实际保留、统一部署入口与原完整现场审核\n\n'+'见 [本轮实测]'+state.split('见 [本轮实测]')[1].split('## NSS66–67历史')[0].replace('(../evidence','(../evidence')+'\n')
issue=root/'docs/ISSUE_TC_SUPERVISION.md'
with issue.open('a',encoding='utf-8',newline='\n')as f:f.write('''\n## NSS68自然故障补充（非新最小复现）

2026-10-05 10:32:50，保留发布候选worker17138的apply子进程在TCCommand.run中触发“tc child cleanup not proved; outer mutation must terminate”；10:32:52外层rawStatus256/4.35秒。原代码2秒命令、0.15秒TERM和0.85秒KILL回收仍未得到reaped证明，因此原逻辑拒绝并退出，procd随后恢复23634，guardian17139连续。配置和所有保护/ECM终态审核通过。

该次发生在10:34恢复下载之前。NSS68候选与47的整个TCCommand监督片段字节相同，47在08:37也有另一次apply256，但后者是另一断言，不能合并为同根因。publication JSON成本优化不能据此判定为故障原因，也没有证据指向NSS或内核缺陷。

当前缺失具体tc argv/child PID、waitpid中间状态及阻塞栈，不能给出新的可靠最小复现或提交上游。下一次若自然复现，应在既有边界内保留这些诊断，而不是放宽2/6秒或清理证明。该发现不授权新生产改动。见 [实际证据](../evidence/nss68-mainline.json)。
''')
checker=root/'tools/check_repository.py';t=checker.read_text(encoding='utf-8');old="new67=json.loads((root/'evidence/nss67-mainline.json').read_text());latest=json.loads((root/'evidence/current-runtime.json').read_text())";assert old in t
t=t.replace(old,"new67=json.loads((root/'evidence/nss67-mainline.json').read_text());latest=json.loads((root/'evidence/nss67-runtime.json').read_text())")
marker="print(json.dumps({'passed':True,'filesChecked':count"
checks="""x68=json.loads((root/'evidence/nss68-mainline.json').read_text());l68=json.loads((root/'evidence/current-runtime.json').read_text())
assert l68['round']=='NSS68' and x68['candidateRetainedAtEnd'] and l68['publicationCandidateInstalled']
assert l68['deploymentReference']=='work/nss68/deployment-latest.json' and l68['classifierConfigSha256']==x68['classifierConfigSha256']
assert l68['candidateEntryBindingCreated'] and l68['qualifiedExperimentalEntryBoundInputs']==257
assert x68['entry']['baseInputs']==241 and x68['entry']['overlayInputs']==16 and x68['entry']['checks']==17
assert not x68['entry']['nativeGateStagingExecutedThisTurn'] and not l68['nssOpenedThisTurn']
assert x68['retention']['remoteCommittedReceiptVerified'] and x68['retention']['checkpointCount']==1
assert x68['retention']['productionUndoSeconds']==180 and x68['retention']['stageGuardianSeconds']==480
assert not x68['retention']['newNaturalUndoTrialClaimed'] and x68['workerLifecycle']['naturalRestartObserved']
assert x68['workerLifecycle']['applyRawStatus']==256 and x68['workerLifecycle']['tcSupervisorByteIdenticalToPrevious47']
assert l68['finalClosure']['passed'] and l68['audit']['passed'] and l68['audit']['ecmClosedAndZero']
assert l68['historical67RuntimePreservedSha256']==hashlib.sha256((root/'evidence/nss67-runtime.json').read_bytes()).hexdigest()
assert x68['actualTrafficWindow']['lan4Mbps']<300 and not x68['actualTrafficWindow']['qualifiedHighLoad']
assert all(not x68['conclusions'][k]for k in ['wholeRouterCpuBenefitProved','realHumanExperienceProved','completeMatchedABACompleted','generalLongTermStabilityProved','upstreamSubmitted'])
assert len(manifest['sources'])==868
"""
assert marker in t;checker.write_text(t.replace(marker,checks+marker,1),encoding='utf-8',newline='\n')
print(json.dumps({'exported':True,'newCuratedSources':23,'totalCuratedSources':len(items),'history67Sha256':sha(history),'rawPrivateDataCopied':False}))
