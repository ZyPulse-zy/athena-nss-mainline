from pathlib import Path
from datetime import datetime, timezone, timedelta
import copy, hashlib, json, subprocess

w=Path(__file__).resolve().parents[2];repo=w/'athena-nss-mainline';root=w/'work/v43-bounded-entry'
base='c2319000d8963996edf3e3270efdf412c4204979'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda b:hashlib.sha256(b).hexdigest()
dump=lambda v:json.dumps(v,ensure_ascii=False,indent=2)+'\n'
git=lambda *a:subprocess.check_output(['git','-C',str(repo),*a])
def new(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8')as f:f.write(dump(v))
assert git('rev-parse','HEAD').decode().strip()==base and not git('status','--porcelain')
manifest=read(repo/'source-manifest.json');prefix=copy.deepcopy(manifest['sources']);assert len(prefix)==4540
old={}
for row in git('ls-tree','-r','-z',base,'--','code','evidence').split(b'\0'):
 if row:
  header,name=row.split(b'\t');old[name.decode()]=(header.decode().split()[2],sha((repo/name.decode()).read_bytes()))
assert len(old)==5121
model_file=w/read(root/'entry-model-latest-private.json')['receipt'];model=read(model_file)
assert model['passed'] and len(model['checks'])==13 and model['modelOnly'] and not model['trafficGenerated'] and not model['routerWrites'] and not model['hardwareExecuted']
assert model['sourceBindings']==3405
for rel,digest in model['sourceHashes'].items():assert sha((w/rel).read_bytes())==digest,rel
generated=w/model['modelRuntimeRoot'];q=read(generated/'entry-qualified.json');assert q['actualBindings']==3405 and q['dataPlaneByteExact'] and q['classificationAndQosPolicyUnchanged']
for rel,digest in q['sourceManifest'].items():assert sha((w/rel).read_bytes())==digest,rel
for name in ['fast-path.lua','classifier.lua','classified-tags.lua','module-stage-guardian.lua','qos-physical.lua','wan-scope.lua','tag-normalizer.lua']:
 assert (generated/name).read_bytes()==(w/'work/v42-counter-window'/name).read_bytes(),name
platform_file=sorted(root.glob('platform-*-private.json'))[-1];platform=read(platform_file)
assert platform['exitCode']==1 and not platform['routerWrites'] and not platform['trafficGenerated'] and 'Get-CimInstance' in platform['stderr']
assert not (root/'active-lock').exists() and not (root/'active-private.json').exists()
assert not (generated/'one-session-attempt.json').exists()
mock=read(generated/'load-latest-private.json');assert mock['dir']==model['modelRuntimeRoot']+'/load-model' and mock['clientPid']==111
assert read(w/mock['dir']/'result-private.json')['modelOnly']
assert read(root/'publication-first-failure/failure.json')['commitChainStopped']
correction=read(root/'initial-model-freeze/model-coverage-correction.json');assert correction['originalExtendedCutoffLabelWasNotSufficientEvidence']
sources=['entry.mjs','materialize.mjs','check-model.mjs','platform-preflight.mjs','publish.py','publish-repaired.py','publication-first-failure/failure.json','initial-model-freeze/entry.mjs','initial-model-freeze/materialize.mjs','initial-model-freeze/check-model.mjs','initial-model-freeze/entry-model-qualified.json','initial-model-freeze/resume-read-failures.json','initial-model-freeze/model-coverage-correction.json']
source_hashes={};exact_crlf_attributes=[]
for name in sources:
 p=root/name;rel=p.relative_to(w).as_posix();b=p.read_bytes();target=repo/'code'/rel;target.parent.mkdir(parents=True,exist_ok=True)
 with target.open('xb')as f:f.write(b)
 source_hashes[rel]=sha(b);manifest['sources'].append({'path':'code/'+rel,'workspaceSource':rel,'sha256':sha(b),'bytes':len(b),'role':'bounded-reusable-entry-and-startup-refusal'})
 if b'\r\n' in b:exact_crlf_attributes.append('/code/'+rel+' whitespace=cr-at-eol')
if exact_crlf_attributes:
 p=repo/'.gitattributes';p.write_text(p.read_text(encoding='utf8')+'\n# Preserve byte-exact v43 local model and refusal record endings.\n'+'\n'.join(exact_crlf_attributes)+'\n',encoding='utf8')
inputs={'revised-model':model_file,'generated-source-qualification':generated/'entry-qualified.json','original-model':root/'initial-model-freeze/entry-model-qualified.json','platform-refusal':platform_file,'refused-entry-output':root/'entry-run-process-private.txt','revised-model-output':root/'model-revised-process-private.txt'}
sealed={};sealed_dir=root/'sealed-inputs-private';sealed_dir.mkdir()
for role,p in inputs.items():
 b=p.read_bytes();dest=sealed_dir/(role+p.suffix)
 with dest.open('xb')as f:f.write(b)
 assert dest.read_bytes()==b;sealed[role]=sha(b)
new(sealed_dir/'manifest-private.json',sealed)
e={'passedAsEntrySoftwareQualification':True,'modelChecks':model['checks'],'modelCheckCount':13,'modelSourceHashes':model['sourceHashes'],'actualGeneratedBindings':3405,'inheritedBindings':3354,'generatedQualifiedSourceCount':len(q['sourceManifest']),'sevenDataPlaneSourcesExactV42':True,'classificationQosAndLeasePolicyUnchanged':True,'limits':model['limits'],'defaultInspectExecuted':True,'defaultInspectTrafficGenerated':False,'defaultInspectRouterWrites':False,'defaultInspectIsNotLiveAudit':True,'statusAfterRefusal':'IDLE','startupAttempt':{'attempted':True,'exitCode':1,'category':'WINDOWS_CIM_PROCESS_IDENTITY_UNAVAILABLE','refusedBeforeFixtureOrRouterConnection':True,'activeLedgerCreated':False,'activeLockCreated':False,'newHardwareExecuted':False,'checkpointStarted':False,'nssStageStarted':False,'trafficGenerated':False,'routerWrites':False},'firstNineCheckModelPreserved':True,'originalCutoffCaseHadInsufficientCoverage':True,'revisedCutoffCasesUseValidNamespaceAndFailureMessage':True,'stopOnlyControlsOwnedClientAndStopsNextAdmission':True,'stopIsNotImmediateHardwareRecoveryClaim':True,'automaticNewEpochOrDaemon':False,'cs2OrSteamOperated':False,'newCpuAcceptance':False,'newHardwareEntryAcceptance':False,'permanentNssDeployment':False,'hardwareBasis':'v42','originalV41LimitationStillOpen':True,'firstPublicationFailurePreserved':True,'modelSyntheticClientPointerNotMistakenForProduction':True,'rawPlatformAndOutputEvidenceLocalOnly':True,'privateInputSha256ByRole':sealed}
new(repo/'evidence/v43-bounded-entry.json',e)
proof={'passed':True,'historicPrefixSources':4540,'newSources':len(sources),'sourceHashes':source_hashes,'oldCodeAndEvidenceBlobsChecked':len(old),'oldCodeAndEvidenceUnmodified':True,'privateInputsCopiedExact':len(sealed),'initialModelSourcesAndRefusalPreserved':True,'noProductionExperimentRepeated':True,'exactNewCrLfAttributes':exact_crlf_attributes,'noGlobalWhitespacePolicyChange':True}
new(repo/'evidence/v43-bounded-source-proof.json',proof)
manifest['generatedAt']=datetime.now(timezone.utc).isoformat();manifest['lastBoundedEntryExport']='V43_REUSABLE_ENTRY_MODELS_COMPLETE_STARTUP_REFUSED_BEFORE_NETWORK';assert manifest['sources'][:4540]==prefix
(repo/'source-manifest.json').write_text(dump(manifest),encoding='utf8')
report='''# 可复用的有界多 WAN 入口

当前已接入四个命令：`inspect`（默认）、`status`、`run`、`stop`。入口沿用 v42 的四条自有 TCP 下载＋一条模拟 UDP 实时流，以及已验收的五 WAN 数据面。默认预览只核对本地源码和既有验收依据，不产生流量，不连接路由器，也不代表新的现网健康审核。

```powershell
& 'C:/Users/lishu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe' 'work/v43-bounded-entry/entry.mjs' inspect
& 'C:/Users/lishu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe' 'work/v43-bounded-entry/entry.mjs' status
& 'C:/Users/lishu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe' 'work/v43-bounded-entry/entry.mjs' run
& 'C:/Users/lishu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe' 'work/v43-bounded-entry/entry.mjs' stop
```

命令从本工作区执行，依赖本地保存的已绑定源码、原部署资料和 SSH 连接；公开仓库包含白名单源码和脱敏证据，凭据、完整运行输入、checkpoint 和模块留在本地。这是一次显式触发、到期恢复的受控入口，不是永久开启 NSS 的服务。

## 运行与停止

`run` 先检查 Windows 的进程身份和 socket 查询能力，再创建独占锁和新的运行目录。每次从 v42 冻结源产生独立副本；模型生成的实际源绑定为3354原绑定＋51新绑定＝3405。七份 Lua 数据面、分类、QoS、tag、guardian 源与 v42 字节相同。新运行只改变本地命名空间、有限启动截止和停止请求检查。

后续仍由原自动分类和 Linux PBR 取得五个不同 WAN 的四 BULK＋一 RT，原 tuple / CT / 完整 mark / NAT / WAN affinity 冻结后不替换。每次生产写前仍需新的 checkpoint 下载/SHA/gzip 与控制连接外独立恢复核验；原 60秒 B / source6 / kernel90最大120 / owner180 / client180 / guard210、32Mbps负载、DOWN18 / UP60每WAN12、各字节上限保持。

`stop` 只向本次命名空间写入停止意图和同 session 的自有客户端控制，不强杀控制器、不直接改现网 tag。它阻止下一次准入，并停止自有发送；NSS 撤销与恢复继续由原控制器和独立 guardian 完成。收到停止请求不等于恢复审核已经通过。`status` 显示本地入口记录，不能代替新网络审核。恢复未确认时独占锁保留，禁止自动开启下一代。

## 本次实际验证

修订后的13项模型检查和默认预览通过，包括命名空间、恢复余量、完整/缺失进程身份、同session停止与已结束客户端不重启。首版9项输出保留；其中“延长截止拒绝”用错了命名空间，不能单独证明截止检查，已改为合法命名空间和明确失败信息的用例。没有覆盖旧输出。

实际启动返回1：当前执行环境无法查询 Windows CIM 进程身份。入口在创建独占锁、运行记录、负载、SSH/router连接、checkpoint或NSS stage前拒绝，原输出仅保存在本地；状态为IDLE。本次没有新的硬件会话，不能标完整新入口现场通过。后续先取得可完成原进程身份核验的执行条件，再只补一次该入口整合会话，保持原安全检查。

封存脚本首次误将模型里的虚拟客户端指针当作真实负载而拒绝，发生在源码复制与提交之前。原源码及失败已保存；修正为验证虚拟样例身份后继续，没有新开网络测试。

v42 的五 WAN 五流60.01秒 / 121个ECM5采样 / 20续租、2373模拟UDP全部返回和完整恢复结论保持。v41分类计数差异继续保留为已知限制，不称已修复。本次没有 CS2 / Steam操作、新CPU、长期或永久部署声明。

源码：[入口](../code/work/v43-bounded-entry/entry.mjs)、[副本和绑定](../code/work/v43-bounded-entry/materialize.mjs)、[进程检查](../code/work/v43-bounded-entry/platform-preflight.mjs)。证据：[本次软件检查与启动拒绝](../evidence/v43-bounded-entry.json)、[源码保存](../evidence/v43-bounded-source-proof.json)、[v42硬件验收](FIVE_WAN_SIMULATED_ACCEPTANCE_2026-10-07.md)。
'''
(repo/'docs/BOUNDED_MULTIWAN_ENTRY.md').write_text(report,encoding='utf8')
now=datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
header=f'''# 多 WAN 可复用入口已接入；现场启动写前拒绝

更新：北京时间{now}。v43新增默认inspect/status/run/stop入口，复用v42五WAN已验收数据面。13模型和默认inspect通过，模型3405绑定=原3354+51；七Lua原字节、分类/QoS/lease/恢复与字节上限保持。新命名空间/独占锁/同session停止支持显式一次运行，不自动连续新代或常驻。

实际run因当前Windows CIM进程身份不可读返回1，在独占锁、记录、负载、SSH/router/checkpoint/stage之前拒绝，状态IDLE；没有新硬件验收或现网写入。原首版9模型及其中不足以证明cutoff的错误用例已保存，修订13项用合法命名空间验证。失败与原输出本地保留，没有为了检查重开fixture。

v42五WAN60.01秒/ECM5/20续租/2373UDP全返回与完整恢复保持；v41计数差异仍known limitation，不重做CPU或旧核心证明。下一步只在能读取原进程身份的执行条件下补一次新入口整合，继续模拟UDP，不启动CS2/Steam；长期、永久、全网、WiFi/autorate/ECN留后续。heartbeat仍暂停。

详情：[可复用入口](BOUNDED_MULTIWAN_ENTRY.md)。

## 以下保留历史记录

'''
for name in ['docs/STATE.md','docs/PLAN.md','docs/EXPERIMENT_LOG.md','AGENTS.md']:
 p=repo/name;text=header.replace('(BOUNDED_MULTIWAN_ENTRY.md)','(docs/BOUNDED_MULTIWAN_ENTRY.md)')if name=='AGENTS.md'else header;p.write_text(text+p.read_text(encoding='utf8'),encoding='utf8')
p=repo/'README.md';p.write_text('# Athena NSS 多WAN / 高级QoS受控原型\n\n五WAN硬件验收保持，新增可复用的默认预览、状态、一次运行和停止入口。软件检查通过；当前Windows进程身份读取条件不足，实际启动写前拒绝，没有新现场验收。见[入口使用与边界](docs/BOUNDED_MULTIWAN_ENTRY.md)和[STATE](docs/STATE.md)。\n\n## 以下保留历史交付\n\n'+p.read_text(encoding='utf8'),encoding='utf8')
(repo/'docs/MULTI_WAN_QOS.md').write_text('''# 多 WAN NSS 与高级 QoS的实际边界

| 能力 | 当前证据 |
|---|---|
| 五个不同 WAN 的四 TCP BULK＋一 UDP RT 同时 NSS | v42实际60.01秒、121次ECM5采样、20续租，完整恢复 |
| 五WAN双向RT/BULK队列与完整mark/NAT/affinity | 每方向18class / 11leaf；v42双向十tag命中 |
| 共享下行预算与空闲份额借用 | DOWN18，每WAN保障3可借用至18；v42四bulk附近异步窗口合16.70Mbps |
| 上行预算与RT优先级 | UP60、每WAN12硬上限；RT保障1Mbps / prio0 / FQ-CoDel |
| 自有模拟UDP实时流 | v42保守内部窗口2373发送 / 2373返回，RT双向leaf零drop；不是CS2 HUD或真人体验 |
| 可复用的一次运行／停止入口 | v43软件模型13项、默认inspect通过；实际启动在Windows CIM身份检查处写前拒绝，新入口现场整合未通过 |
| 全网、永久NSS、长期常驻 | 尚未交付；当前加速五条精确CT，其余保留软件fallback |

Linux PBR决定新连接，已选CT/完整mark/NAT/WAN保持。已加速流改类或退出结束旧代，重新分类、pin/checkpoint/owner后才重学，不能强续旧代或直接换tag。v41发生过四BULK变BE/cooldown；v42未复现，准确原因和长期频率未知，保留已知限制。

default950保持未选物理fallback，原IFB/CAKE、MiniEAP、学校策略、sing-box和Tailscale不变。NSS用分层预算、优先级与leaf FQ-CoDel处理选中流，未复刻CAKE的全部host公平、diffserv4、COBALT或autorate。target5ms是队列配置，不是互联网RTT保证。历史CPU证据复用，本轮无新CPU因果结论。

下一步只补可复用入口在支持原Windows身份查询条件下的一次有界整合；后续仍用模拟游戏包。正常应用factory、扩大精确流池、连续新代和长期部署、WiFi/autorate/ECN留后续，不能从模拟有界验收推成已交付。

详见[五WAN硬件验收](FIVE_WAN_SIMULATED_ACCEPTANCE_2026-10-07.md)、[可复用入口](BOUNDED_MULTIWAN_ENTRY.md)、[当前状态](STATE.md)。
''',encoding='utf8')
p=repo/'tools/check_repository.py';text=p.read_text(encoding='utf8');needle="print(json.dumps({'passed':True,'filesChecked':count";assert text.count(needle)==1
checks='''if (root/'evidence/v43-bounded-entry.json').exists():
 e=json.loads((root/'evidence/v43-bounded-entry.json').read_text(encoding='utf8'));s=json.loads((root/'evidence/v43-bounded-source-proof.json').read_text(encoding='utf8'))
 assert manifest['lastBoundedEntryExport']=='V43_REUSABLE_ENTRY_MODELS_COMPLETE_STARTUP_REFUSED_BEFORE_NETWORK'
 assert e['passedAsEntrySoftwareQualification'] and e['modelCheckCount']==len(e['modelChecks'])==13 and e['actualGeneratedBindings']==3405 and e['inheritedBindings']==3354
 assert e['generatedQualifiedSourceCount']==51 and e['sevenDataPlaneSourcesExactV42'] and e['classificationQosAndLeasePolicyUnchanged']
 assert e['defaultInspectExecuted'] and not e['defaultInspectTrafficGenerated'] and not e['defaultInspectRouterWrites'] and e['defaultInspectIsNotLiveAudit'] and e['statusAfterRefusal']=='IDLE'
 t=e['startupAttempt'];assert t['attempted'] and t['exitCode']==1 and t['category']=='WINDOWS_CIM_PROCESS_IDENTITY_UNAVAILABLE' and t['refusedBeforeFixtureOrRouterConnection']
 assert not any(t[k] for k in ['activeLedgerCreated','activeLockCreated','newHardwareExecuted','checkpointStarted','nssStageStarted','trafficGenerated','routerWrites'])
 assert (e['limits']['source'],e['limits']['client'],e['limits']['phase'],e['limits']['bundle'],e['limits']['exec'],e['limits']['record'])==(6,180,60,73728,9000,1048576)
 assert e['firstNineCheckModelPreserved'] and e['originalCutoffCaseHadInsufficientCoverage'] and e['revisedCutoffCasesUseValidNamespaceAndFailureMessage']
 assert e['stopOnlyControlsOwnedClientAndStopsNextAdmission'] and e['stopIsNotImmediateHardwareRecoveryClaim'] and e['originalV41LimitationStillOpen']
 assert not any(e[k] for k in ['automaticNewEpochOrDaemon','cs2OrSteamOperated','newCpuAcceptance','newHardwareEntryAcceptance','permanentNssDeployment'])
 assert s['passed'] and s['historicPrefixSources']==4540 and s['newSources']==len(s['sourceHashes'])==13 and s['oldCodeAndEvidenceBlobsChecked']==5121 and s['oldCodeAndEvidenceUnmodified'] and s['privateInputsCopiedExact']==6
 assert s['initialModelSourcesAndRefusalPreserved'] and s['noProductionExperimentRepeated'] and e['firstPublicationFailurePreserved'] and e['modelSyntheticClientPointerNotMistakenForProduction']
 for rel,digest in s['sourceHashes'].items():assert hashlib.sha256((root/'code'/rel).read_bytes()).hexdigest()==digest,rel
 for rel,digest in e['modelSourceHashes'].items():assert hashlib.sha256((root/'code'/rel).read_bytes()).hexdigest()==digest,rel
 code=(root/'code/work/v43-bounded-entry/entry.mjs').read_text(encoding='utf8');assert code.index('platformPreflight();')<code.index('fs.mkdirSync(lock)')<code.index('materialize(runtimeRoot,')
 correction=json.loads((root/'code/work/v43-bounded-entry/initial-model-freeze/model-coverage-correction.json').read_text(encoding='utf8'));assert correction['preserved'] and correction['originalExtendedCutoffLabelWasNotSufficientEvidence'] and correction['originalSourceAndOutputUnmodified']
'''
p.write_text(text.replace(needle,checks+needle),encoding='utf8')
for name,(_,digest)in old.items():assert sha((repo/name).read_bytes())==digest,name
new(root/'publication-candidate.json',{'passed':True,'newSources':len(sources),'historicSourcePrefix':len(prefix),'oldCodeAndEvidenceBlobsUnchanged':len(old),'modelCheckCount':13,'startupRefusedBeforeNetwork':True,'newHardwareAcceptance':False})
print(dump({'passed':True,'newSources':len(sources),'totalSources':len(manifest['sources']),'oldCodeAndEvidenceBlobsUnchanged':len(old),'newHardwareAcceptance':False}))
