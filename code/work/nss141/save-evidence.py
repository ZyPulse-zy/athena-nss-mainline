"""Publish offline real-entry integration without relabeling it as hardware acceptance."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json,shutil,subprocess
w=Path(__file__).resolve().parents[2];repo=w/'athena-nss-mainline';r=w/'work/nss141';entry=w/'work/nss140'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
qual=load(entry/'entry-qualified.json');fast=load(entry/'fast-qualified.json');ready=load(entry/'real-session-readiness.json');reader=load(entry/'real-reader-qualified.json');size=load(r/'entry-size-review.json');final=load(r/'v1-final-health.json');physical=load(r/'physical-final.json');receiver=load(r/'receiver-closure.json')
assert qual['passed']and fast['passed']and fast['checks']==10 and fast['actualHardwareTestThisVersion']is False and qual['inheritedBoundInputs']==1340 and len(qual['sourceManifest'])==45
assert ready['mode']=='inspect'and not ready['routerWrites']and not ready['trafficGenerated']and not ready['nssPermissionGranted']and ready['sameWanPairs']==0
assert size['passed']and size['packetProtocolFieldsValidated']and all(x['qosBundleFitsOriginal73728']and x['guardianFitsOriginal9000']for x in size['cases'])
assert final['passed']and final['ecmStoppedAndZero']and physical['passed']and receiver['passed']and receiver['exactOwnedReceiverAndTimeoutProcessesRemaining']==0
node='C:/Users/lishu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
command="import fs from'node:fs';import{verifyPreparation}from'./work/nss140/session-binding.mjs';const p=verifyPreparation();process.stdout.write(JSON.stringify(p.sourceManifest));"
bound=json.loads(subprocess.check_output([node,'--input-type=module','-e',command],cwd=w,text=True));assert len(bound)==1385
freeze=r/'prepared-inputs-private';freeze.mkdir(exist_ok=False)
for f,h in bound.items():
 b=(w/f).read_bytes();assert sha(b)==h
 target=freeze/f;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b);assert sha(target.read_bytes())==h
dump(r/'prepared-bindings-private.json',bound)
old=(repo/'evidence/current-runtime.json').read_bytes();assert load(repo/'evidence/current-runtime.json')['round']=='NSS139'and subprocess.check_output(['git','show','HEAD:evidence/current-runtime.json'],cwd=repo)==old
archive=repo/'evidence/nss139-runtime.json';assert not archive.exists();archive.write_bytes(old)
manifest=load(repo/'source-manifest.json');assert len(manifest['sources'])==1832;prefix=sha(json.dumps(manifest['sources'],sort_keys=True,separators=(',',':')).encode());hashes={}
allowed={140:[Path(f).name for f in qual['sourceManifest']],141:['prepare-audits.py','health.mjs','read-final-physical.mjs','verify-receivers.mjs','measure-entry-size-v1.mjs','measure-entry-size-v2.mjs','measure-entry-size.mjs','save-evidence.py']}
for n,names in allowed.items():
 for name in names:
  assert 'private'not in name and Path(name).suffix in ['.mjs','.py','.lua','.ps1']
  src=w/f'work/nss{n}'/name;rel=src.relative_to(w).as_posix();b=src.read_bytes();target=repo/'code'/rel;assert not target.exists();target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b);hashes[rel]=sha(b)
  manifest['sources'].append({'path':'code/'+rel,'workspaceSource':rel,'sha256':sha(b),'bytes':len(b),'role':'final-real-entry-offline-integration-and-readonly-health'})
manifest['generatedAt']=datetime.now(timezone.utc).isoformat();manifest['lastAppendExport']='NSS141';dump(repo/'source-manifest.json',manifest)
inputs={};snap=r/'local-evidence-private';snap.mkdir(exist_ok=False)
for base in [entry,r]:
 for src in sorted(base.rglob('*')):
  if not src.is_file()or any(x in ['prepared-inputs-private','local-evidence-private','__pycache__']or x.startswith('published-')for x in src.parts):continue
  rel=src.relative_to(w);b=src.read_bytes();target=snap/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b);inputs[rel.as_posix()]=sha(b)
dump(r/'local-evidence-index-private.json',inputs)
failures=[{'stage':'first-default-inspect-preparation','passed':False,'routerConnectionStarted':False,'checkpointOrStageStarted':False,'ecmOpened':False,'originalPreserved':True,'reason':'Byte-equality assertion incorrectly included the temporary namespace of guardian placeholders; corrected only to permit this exact namespace substitution. Expanded guardian source remains identical.','actualRecord':load(entry/'default-inspect-v1-rejection.json')},
 {'stage':'first-size-model','passed':False,'routerConnectionStarted':False,'checkpointOrStageStarted':False,'ecmOpened':False,'originalPreserved':True,'reason':size['v1UnusableReason'],'originalReportedPassedButModelInvalid':load(r/'entry-size-review-v1.json')['passed'],'originalOutputRetainedSha256':sha((r/'entry-size-review-v1.json').read_bytes())},
 {'stage':'identifier-compactor-candidates','passed':False,'routerConnectionStarted':False,'checkpointOrStageStarted':False,'ecmOpened':False,'originalPreserved':True,'reason':'Quoted-literal conservation and property-name checks rejected two local alias candidates before they replaced the final source.'},
 {'stage':'combined-whole-factory-model-transport','passed':False,'routerConnectionStarted':False,'checkpointOrStageStarted':False,'ecmOpened':False,'originalPreserved':True,'reason':'Two combined model commands exceeded unchanged 9000-byte transport cap before execution. Full factory syntax and only new observe/retire branches were later checked separately; whole factory ABA was not executed.'}]
summary={'round':'NSS141','preparedEntryRound':140,'observedAt':final['observedAt'],'preparedBindings':1385,'inheritedBindings':1340,'newEntryBindings':45,'realEntryIntegrated':True,'readonlyDefaultInspectExecuted':True,'currentRealGameCandidates':ready['actualGameCandidates'],'currentRealBulkCandidates':ready['actualBulkCandidates'],'currentSameWanPairs':0,'newObserveRetireTargetRamChecks':10,'applicationFilterTargetRamChecks':10,'ownershipNodeRejections':8,'historicalFullFrameMappingReplayOnly':True,'fullFactorySyntaxCompiled':True,'wholeFactoryAbaExecutedThisRound':False,'newVersionHardwareAbaPassed':False,'newCpuComparison':False,'humanCs2Acceptance':False,'productionWrites':False,'checkpointOrStageStarted':False,'ecmOpened':False,'residentClassifierChanged':False,'residentUpTagZeroUnchanged':True,'partialClassChangeNeverCompletesAba':True,'freshCheckpointAndNewEpochRequiredAfterClassChange':True,'sourceMaximumSeconds':6,'nativeMaximumSeconds':27,'ownerMaximumSeconds':100,'packetBundleBytes':qual['payloadBytes'],'guardianExecBytes':qual['guardianExecBytes'],'originalByteAndDeadlineCapsKept':True,'nssPermanentlyEnabled':False,'fullCakeReplacementAccepted':False,'uiOperated':False,'newDownloadStarted':False,'upstreamSubmitted':False,'reportVerification':{'sourceValidated':True,'browserRendered':False}}
source={'round':'NSS141','historicPrefixSources':1832,'historicPrefixCanonicalSha256':prefix,'sources':len(hashes),'sourceHashes':hashes,'preparedInputsCurrentAndFrozenMatch':True,'preparedBindings':len(bound),'localArtifactsFrozen':len(inputs),'oldNss139RuntimeRetainedExactSha256':sha(old),'privateHostBootstrapExcluded':True,'originalFailuresKept':True}
qualification={k:v for k,v in qual.items()if k!='sourceManifest'};qualification['newEntrySourceHashes']=qual['sourceManifest'];qualification['oldInputsRetainedOnlyLocally']=True
evidence={'mainline':summary,'entry-qualification':qualification,'fast-qualification':fast,'readonly-readiness':ready,'readonly-reader':reader,'size-review':size,'failures':failures,'receiver-closure':receiver,'final-audit':final,'physical-final':physical,'source-proof':source}
for k,v in evidence.items():dump(repo/f'evidence/nss141-{k}.json',v)
runtime={'round':'NSS141','checkedAt':final['observedAt'],'deploymentReference':'work/nss68/deployment-latest.json','classifierConfigSha256':final['configSha256'],'workerPid':final['workerPid'],'guardianPid':final['guardianPid'],'nssPermanentlyEnabled':False,'residentClassifierChangedThisTurn':False,'qualifiedExperimentalEntry':'work/nss138/controlled-session.mjs','qualifiedExperimentalEntryBoundInputs':1340,'preparedRealEntry':'work/nss140/real-session.mjs','preparedRealEntryBoundInputs':1385,'preparedRealEntryHardwareAbaTested':False,'currentNssAdmissionMustBeRefreshedBeforeWrite':True,'audit':final,'physicalRootRestoreAudit':physical,'physicalClassChangeRetirementAcceptedFrom139':True,'freshEpochRelearningSameCtAcceptedFrom139':True,'realHumanGameAcceptance':False,'newCpuComparisonAcceptedThisTurn':False,'historical139RuntimePreservedSha256':sha(old),'nightContinuationUntilBeijing':'2026-10-06T10:00:00+08:00'};dump(repo/'evidence/current-runtime.json',runtime)
when=datetime.fromisoformat(final['observedAt'].replace('Z','+00:00')).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
text=f'''更新：{when}，北京时间。最新NSS141整理、140入口离线整合；常驻NSS68/config581b5d46…c791d7，worker{final['workerPid']}、guardian{final['guardianPid']}。本轮没有生产试装，ECM保持关闭。

**已经把139实测的改类精确撤销接入最后真人入口。学习前按完整实际class映射双向bulk/RT tag；保留程序连接归属和完整CT/mark/NAT/query/leaf/lease证据。若B段发生受支持的真实BULK→BE，停止新学习、核验完整同query证据、精确撤销TCP CI并检查原UDP，再结束旧代；该次中断不能算完整A/B/A2，也不会在旧代强续或改tag。重新学习必须重新进入入口，取得新分类/kernel pin/checkpoint/owner。**

见 [整合汇总](../evidence/nss141-mainline.json)、[入口资格](../evidence/nss141-entry-qualification.json)、[新增撤销检查](../evidence/nss141-fast-qualification.json)、[只读现网](../evidence/nss141-readonly-readiness.json)、[终态](../evidence/nss141-final-audit.json) 与 [失败](../evidence/nss141-failures.json)。

- `work/nss140/real-session.mjs` 默认只读inspect，显式aba才可实验。当前1385项绑定含原138的1340项和原真人77的全部355项；45新输入当前及本地冻结逐字节匹配。真实默认inspect已运行，无游戏/下载对，未创建checkpoint/stage/开放ECM。
- 新fast完整目标RAM语法通过，仅新增observe/retire分支10项模型执行；程序归属Lua过滤10项RAM和8项Node拒绝、1份历史完整分类帧映射通过。旧138真实生命周期及128可比CPU是历史实测；**140新整合版本完整factory A/B/A2未在模型或硬件跑过，不能把分支检查写成真人验收。**
- 正常测量保留三段各20秒、同观察器/同QoS与完整mark/NAT/affinity检查。仅一健康WAN、一TCP BULK＋一UDP RT；UP60/DOWN30、bulk29/RT1、fallback950保持。来源6秒/native27秒/owner100秒、9000/65536/73728字节及1MiB读上限不放宽；有效渲染73574字节、guardian8907，另三份仅尺寸模型73575/73417/73588均在上限内。实际新输入仍须现场编码检查，尺寸模型不授权flow。
- 原140第一次默认inspect因临时placeholder命名的字节相等断言拒绝，发生在PC读取及路由器连接之前；43份首资格源码已冻结，只允许该确切namespace替换，展开guardian不变。第一尺寸模型漏protocol、保留额外TCP neighbor并报告错误尺寸，原输出虽标passed仍明确作无效证据保留；修正后校验实际protocol。两次combined模型命令过大写前拒绝、两个alias候选被文字/属性检查拒绝，也未隐藏。
- 原完整终态source{final['queryAge']:.2f}、动态selectors{final['selectors']}由native审核验证；ECM关闭全零，无事务/stage/state/模块，两物理mq＋四fq_codel和自有SSH receiver零残留。WAN4仍down，既有四路failover与认证/代理/Tailscale不动。未操作UI/下载/对局；没有新CPU或游戏体验结论。
- 最后集中真人窗：用户醒来后用已有正常待下载内容和真人CS2，不购买/重装/新增下载；先只读确认同WAN精确pair，再新checkpoint与独立owner并核验后做20秒A/B/A2。记录HUD jitter/loss/Miss/体感及softirq/squeeze/吞吐；下载负载不匹配或窗口中断就分开报告功能和性能。随后才讨论长期NSS策略与扩WAN。睡眠期间仅保存准备，09:50晨间收尾、10点前暂停本夜heartbeat，不重复CPU/试装/广泛准备。
'''
for name,header in [('STATE.md','# 当前状态'),('PLAN.md','# 下一步：最后集中真人验收'),('EXPERIMENT_LOG.md','# 最新实验')]:
 p=repo/'docs'/name;before=p.read_text(encoding='utf-8');p.write_text(header+'\n\n'+text+'\n## NSS139历史\n\n'+before,encoding='utf-8')
p=repo/'AGENTS.md';p.write_text('# 接续此研究\n\n最新NSS141：140最后真人入口已离线整合，1385绑定/原355全部继承，完整class/程序tuple/双向tag保留，新增撤销10RAM/程序过滤10RAM及8Node，默认inspect现场0pair/no writes。正常20秒A/B/A2；受支持BE改类先stop新学习、完整同query→仅TCP CI撤销/原UDP核验，再结束旧代，不能作为完整ABA，必须新分类/pin/checkpoint/owner重进。140整合factory完整ABA未执行，139实测和128 CPU只继承历史。6/27/100及字节上限不变；初断言/无效尺寸模型/alias/过大模型命令原失败冻结。常驻68/'+str(final['workerPid'])+'/'+str(final['guardianPid'])+'不改，终态ECM全零无残留/两根/receiver恢复，WAN4down四路不动。最后真人留醒来集中一次，不UI/新下载/CPU重复/扩WAN，09:50晨间收尾10点前暂停本夜；STATE为准。\n\n## NSS139及更早历史\n\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
p=repo/'README.md';p.write_text('# Athena NSS 主线\n\n最新 [NSS141真人入口准备](evidence/nss141-mainline.json)：真实改类撤销与新代重学已在 [NSS139](evidence/nss139-class-lifecycle.json)通过，现已并入最后集中真人入口并完成必要离线/只读核验。常驻68、ECM关闭；140整合版本完整A/B/A2和真人验收尚未执行。以 [STATE](docs/STATE.md) 与 [PLAN](docs/PLAN.md) 开头为准，下方旧摘要仅历史。\n\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
p=repo/'docs/ARTIFACT_INDEX.md';p.write_text('# NSS141最后真人入口准备\n\n'+''.join(f'- [NSS141 {k}](../evidence/nss141-{k}.json)\n'for k in evidence)+'\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
body='''<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NSS141 主线报告</title><style>body{max-width:920px;margin:40px auto;padding:0 24px;font:16px/1.8 system-ui;background:#f7f8fa;color:#202832}h1{font-size:28px}p,li{margin:12px 0}strong{color:#194566}table{border-collapse:collapse;width:100%}td,th{border:1px solid #d8e0e8;padding:10px;text-align:left}</style><h1>NSS141：最后真人入口已整合</h1><p>真实TCP自动退出下载类后的精确撤销与新代重学，已在NSS139证明。本轮将它接入真人测试入口，继续保留完整分类来源、连接身份和程序归属。</p><p><strong>本轮只有离线及只读验证，没有试装、开启加速或操作游戏。</strong>整合版本完整A/B/A2尚未执行，不能当作真人或CPU收益验收。</p><table><tr><th>项目</th><th>实际结果</th></tr><tr><td>新增改类分支</td><td>10项RAM模型通过；完整fast语法通过</td></tr><tr><td>程序归属与完整身份</td><td>10项Lua RAM、8项Node拒绝及历史完整帧映射通过</td></tr><tr><td>入口</td><td>1385项绑定；默认只读已跑通，当前没有游戏下载对</td></tr><tr><td>恢复状态</td><td>ECM全零、无实验残留、两物理根恢复，接收器零残留</td></tr></table><p>20秒software→NSS→software使用同QoS和观察器。B段改类时精确撤销并结束旧代，必须用新分类、新pin、新checkpoint与独立owner重新进入；中断不会记为完整对照。</p><p>第一次placeholder断言失败、无效尺寸模型和本地别名/传输失败均已保留。来源6秒、native27秒、owner100秒和全部字节上限保持。</p><p>用户醒来后集中一次真人CS2＋已有下载内容，记录jitter/loss/Miss/体感、softirq、squeeze和吞吐。夜间不操作桌面或新增下载；09:50收尾，10点前暂停夜间任务。</p></html>'''
(w/'outputs/nss141-mainline-report.html').write_text(body,encoding='utf-8')
print(json.dumps({'preparedPublication':True,'appendedSources':len(hashes),'totalSources':len(manifest['sources']),'preparedBindings':len(bound),'old139RuntimePreserved':True,'productionWrites':False}))
