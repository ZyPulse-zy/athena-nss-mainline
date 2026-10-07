from pathlib import Path
from datetime import datetime, timezone, timedelta
import copy, hashlib, html, json, re, subprocess

w=Path(__file__).resolve().parents[2];repo=w/'athena-nss-mainline';root=w/'work/v44-bounded-entry'
base='b0a3c47965ba7d0113b592f4049a2893005ee946'
sha=lambda b:hashlib.sha256(b).hexdigest()
def read(p):
    data=p.read_bytes()
    return json.loads(data.decode('utf16' if data.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8-sig'))
dump=lambda v:json.dumps(v,ensure_ascii=False,indent=2)+'\n'
git=lambda *args:subprocess.check_output(['git','-C',str(repo),*args])
def new(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf8') as f:f.write(dump(v))
assert git('rev-parse','HEAD').decode().strip()==base and not git('status','--porcelain')
manifest=read(repo/'source-manifest.json');prefix=copy.deepcopy(manifest['sources']);assert len(prefix)==4553
old={}
for row in git('ls-tree','-r','-z',base,'--','code','evidence').split(b'\0'):
    if row:
        head,name=row.split(b'\t');old[name.decode()]=sha((repo/name.decode()).read_bytes())
assert len(old)==5136

failed43=w/'work/v43-run-20261007090613-69b7cd24'
pilot43=w/read(failed43/'pilot-reference-private.json')['directory']
events43=read(pilot43/'driver-private.json')
assert len(events43)==1 and events43[0]['code']==1 and 'input did not match the regular expression' in events43[0]['stderr']
assert not (failed43/'load-latest-private.json').exists() and not (pilot43/'case-reference-private.json').exists()
source43=(failed43/'current-audit-diagnostic.mjs').read_text(encoding='utf8')
assert source43.index('assert.match(caseDir,')<source43.index('await connectRouter()')
initial=w/read(root/'prior-refusal-readonly-pointer-private.json')['runtimeRoot']
initial_proof=read(initial/'prior-local-refusal-confirmed-private.json');assert initial_proof['passed']
actual=w/'work/v44-run-20261007092055-97375ff9'
pilot=w/read(actual/'pilot-reference-private.json')['directory']
events=read(pilot/'driver-private.json');assert len(events)==5 and [e['code'] for e in events]==[0,0,0,1,0]
assert 'Natural five-WAN acquisition window ended' in events[3]['stderr']
assert not (pilot/'case-reference-private.json').exists() and not (pilot/'detached-owner-reference-private.json').exists()
original_result=read(actual/'entry-result-private.json');assert original_result['state']=='RESTORATION_UNCONFIRMED' and not original_result['hardwareCompleted']
closure_failed=w/read(actual/'closure-pointer.json')['directory']
assert 'EEXIST' in (closure_failed/'final-audit-stderr-private.txt').read_text(encoding='utf8')
load=w/read(actual/'load-latest-private.json')['dir'];client=read(load/'result-private.json')
frame=read(actual/'controlled-candidates-private.json')
assert len(frame['pairs'])==0 and len(frame['tcp'])==4 and len(frame['udp'])==1
assert [f['decision']['class'] for f in frame['tcp']]==['BULK']*4
assert frame['udp'][0]['decision']['class']=='RT' and len(client['errors'])==0 and client['seconds']<180
assert [f['identity']['wan'] for f in frame['tcp']]==[1,1,2,4] and frame['udp'][0]['identity']['wan']==3
endpoint=read(load/'endpoint-retry-closure.json');clients=read(closure_failed/'client-closure.json')
assert endpoint['passed'] and endpoint['ownedRulesRemaining']==0 and endpoint['baselineRestored'] and endpoint['exactOwnedEndpointClosed']
assert clients['passed'] and clients['ownedTestProcessesRemaining']==0
restored=w/read(root/'restoration-readonly-pointer-private.json')['runtimeRoot']
closure=w/read(restored/'closure-pointer.json')['directory'];end=read(closure/'restoration-confirmed-private.json')
assert end['passed'] and end['readonly'] and end['noFixtureReopened'] and end['originalFailuresUnchanged']
audit=end['fullAudit'];physical=end['physicalQueues']
assert audit['passed'] and audit['queryAge']<6 and audit['ecmClosedAndZero'] and audit['protectedConfigurationUnchanged'] and audit['allFiveHealthyWanBaseline']
assert physical['defaultQueueOptionsAndHandlesExact'] and end['ownedPriorNodeCount']==0
ledger=read(root/'active-private.json');assert ledger['state']=='RESTORED' and ledger['restorationPassed'] and not (root/'active-lock').exists()
assert ledger['errors']==original_result['errors'] and ledger['hardwareCompleted']==False
assert sha((actual/'entry-result-private.json').read_bytes())==end['originalResultSha256']

model_path=w/read(root/'entry-model-latest-private.json')['receipt'];model=read(model_path)
candidate=w/'work/v44-unique-label-entry';candidate_model_path=w/read(candidate/'entry-model-latest-private.json')['receipt'];candidate_model=read(candidate_model_path)
assert model['passed'] and model['modelOnly'] and len(model['checks'])==15
assert candidate_model['passed'] and candidate_model['modelOnly'] and len(candidate_model['checks'])==17
assert model['sourceBindings']==candidate_model['sourceBindings']==3405
assert not candidate_model['trafficGenerated'] and not candidate_model['routerWrites'] and not candidate_model['hardwareExecuted']
inspect=read(candidate/'inspect-stdout-private.txt');assert inspect['passed'] and not inspect['routerWrites'] and not inspect['trafficGenerated']
assert not (candidate/'active-private.json').exists() and not (candidate/'active-lock').exists()
for m in [model,candidate_model]:
    for rel,digest in m['sourceHashes'].items():assert sha((w/rel).read_bytes())==digest,rel
prior_archive=read(root.parent/'v43-bounded-entry/resumed-20261007T090313649858Z/published-night-receipt.json')
assert prior_archive['passed'] and prior_archive['commit']==base and prior_archive['remoteCommitMatched'] and prior_archive['actualGitArchiveChecked']

# Both attempted supervisors already captured every actual bound input. Verify the held copies.
frozen_counts={}
for name,p in [('v43-local-refusal',pilot43),('v44-acquisition-refusal',pilot)]:
    bindings=read(p/'actual-entry-bindings.json');assert len(bindings)==3405
    for rel,digest in bindings.items():
        data=(w/rel).read_bytes();assert sha(data)==digest and (p/'frozen'/rel).read_bytes()==data,rel
    frozen_counts[name]=len(bindings)

sources=set();runtime_sets={};lua_names=['fast-path.lua','classifier.lua','classified-tags.lua','module-stage-guardian.lua','qos-physical.lua','wan-scope.lua','tag-normalizer.lua']
for r in [failed43,initial,actual,restored]:
    q=read(r/'entry-qualified.json');assert q['passed'] and q['actualBindings']==3405 and q['dataPlaneByteExact'] and q['classificationAndQosPolicyUnchanged']
    assert len(q['sourceManifest'])==51 and q['inheritedBindings']==3354
    for rel,digest in q['sourceManifest'].items():assert sha((w/rel).read_bytes())==digest,rel
    for name in lua_names:assert (r/name).read_bytes()==(w/'work/v42-counter-window'/name).read_bytes(),name
    runtime_sets[r.relative_to(w).as_posix()]={'sourceHashes':q['sourceManifest'],'actualBindings':3405,'inheritedBindings':3354,'sevenLuaByteExactV42':True}
    sources.update(q['sourceManifest'])
for r,names in [(root,['prepare-repaired.py','repair-preparation.json','confirm-prior-local-refusal.mjs','run-once.py','restoration-readonly.mjs','prepare-unique-label.py','publish.py']),
                (candidate,['entry.mjs','materialize.mjs','check-model.mjs','platform-preflight.mjs','preparation.json'])]:
    sources.update((r/n).relative_to(w).as_posix() for n in names)
indexed={x['workspaceSource']:x for x in manifest['sources']};new_sources={}
for rel in sorted(sources):
    p=w/rel;data=p.read_bytes()
    if rel in indexed:
        assert sha(data)==indexed[rel]['sha256'];continue
    target=repo/'code'/rel;target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('xb') as f:f.write(data)
    new_sources[rel]=sha(data)
    manifest['sources'].append({'path':'code/'+rel,'workspaceSource':rel,'sha256':sha(data),'bytes':len(data),'role':'v44-bounded-entry-local-repair-refusal-and-readonly-restoration'})

inputs={
 'v43-resumed-publication':root.parent/'v43-bounded-entry/resumed-20261007T090313649858Z/published-night-receipt.json',
 'v43-supervisor-refusal':failed43/'entry-supervisor-raw-private.json',
 'v43-original-result':failed43/'entry-result-private.json','v43-actual-bindings':pilot43/'actual-entry-bindings.json',
 'v43-readonly-confirmation':initial/'prior-local-refusal-confirmed-private.json',
 'v44-models':model_path,'v44-supervisor-events':pilot/'driver-private.json',
 'v44-actual-bindings':pilot/'actual-entry-bindings.json','v44-original-result':actual/'entry-result-private.json',
 'v44-final-audit-failure':closure_failed/'final-audit-stderr-private.txt','v44-client-result':load/'result-private.json',
 'v44-last-classification-frame':actual/'controlled-candidates-private.json','v44-endpoint-closure':load/'endpoint-retry-closure.json',
 'v44-client-closure':closure_failed/'client-closure.json','v44-original-ledger':closure/'original-ledger-private.json',
 'v44-readonly-restoration':closure/'restoration-confirmed-private.json','unique-label-models':candidate_model_path,
 'unique-label-inspect':candidate/'inspect-stdout-private.txt','local-summary-bom-read-error':root/'summary-bom-read-error-private.json'}
sealed=root/'sealed-inputs-private';sealed.mkdir();sealed_hashes={}
for role,p in inputs.items():
    data=p.read_bytes();dest=sealed/(role+p.suffix)
    with dest.open('xb') as f:f.write(data)
    assert dest.read_bytes()==data;sealed_hashes[role]=sha(data)
new(sealed/'manifest-private.json',sealed_hashes)

new(repo/'evidence/v43-resumed-local-refusal.json',{
 'originalPublicationNowPushedAndArchiveChecked':True,'publicationCommit':base,
 'publishedSourceHashes':prior_archive['sourceHashesChecked'],'archiveSha256':prior_archive['archiveSha256'],
 'windowsIdentityReadableInResumedEnvironment':True,'entryAttemptPassed':False,'actualBindings':3405,
 'failureCategory':'LOCAL_ESCAPED_NAMESPACE_TRAILING_SEPARATOR_MISSING','refusedBeforeRouterConnectionAndFixture':True,
 'checkpointStarted':False,'nssStageStarted':False,'trafficGenerated':False,'originalFailurePreserved':True,
 'separatorFixedOnlyInNewV44Sources':True,'readonlyConfirmationPassedBeforeOldLockRelease':True,
 'originalRuntimeAndResultUnchanged':True,'newHardwareAcceptance':False,
 'inputSha256ByRole':{k:v for k,v in sealed_hashes.items() if k.startswith('v43-')}})
new(repo/'evidence/v44-bounded-entry.json',{
 'entryHardwareIntegrationPassed':False,'entryModelChecksPassed':True,'modelCount':15,'modelChecks':model['checks'],
 'modelSourceHashes':model['sourceHashes'],'actualBindings':3405,'inheritedBindings':3354,
 'separatorRegressionFixed':True,'sevenLuaByteExactV42':True,'classificationQosLeaseAndLimitsUnchanged':True,
 'limits':model['limits'],'fixtureAttemptCount':1,'ownTcpAndSimulatedUdpOnly':True,
 'actualLastFrame':{'sourceAge':frame['sourceAge'],'tcpClasses':['BULK']*4,'udpClasses':['RT'],
                   'tcpWanSetInSlotOrder':[1,1,2,4],'udpWan':3,'fiveDistinctWanPairs':0},
 'failureCategory':'NATURAL_FIVE_WAN_ACQUISITION_WINDOW_ENDED','acquisitionSecondsLimit':30,
 'failedBeforeNssCheckpointAndStage':True,'checkpointStarted':False,'nssStageStarted':False,'ecmOpened':False,
 'caseCreated':False,'controllerOwnerCreated':False,'classifiedAbsenceNotTreatedAsCtExit':True,
 'clientRuntimeSeconds':client['seconds'],'clientTcpPayloadBytes':client['tcpBytes'],'clientErrors':len(client['errors']),
 'clientUdpWholeFixture':{'sent':client['udpSent'],'returned':client['udpReceived'],
                         'notNssMeasurements':True,'stopBoundaryOutstandingRepliesNotAttributedToNss':True},
 'clientDeadlineNotReset':True,'noPbrOrClassificationThresholdChange':True,'noBlindFixtureRetry':True,
 'originalFinalAuditCategory':'LOCAL_EXISTING_GLOBAL_PUBLICATION_OUTPUT','originalFinalAuditPassed':False,
 'readonlySupplementPassed':True,'restorationState':'RESTORED','originalResultState':'RESTORATION_UNCONFIRMED',
 'originalResultAndErrorsUnchanged':True,'newHardwareAcceptance':False,'newCpuAcceptance':False,
 'cs2OrSteamOperated':False,'permanentNssDeployment':False,
 'v42HardwareAcceptanceStillValid':True,'v41KnownLimitationStillOpen':True,
 'inputSha256ByRole':{k:v for k,v in sealed_hashes.items() if k.startswith('v44-')}})
new(repo/'evidence/v44-restoration.json',{
 'passed':True,'readonlySupplementAttempts':1,'originalSupervisorExitCode':1,'originalFinalAuditExitCode':1,
 'originalFailuresPreserved':True,'uniqueAuditOutputLabel':end['uniqueAuditLabel'],'finalFullAudit':audit,
 'physicalQueues':physical,'endpointClosure':endpoint,'clientClosure':clients,'ownedEntryProcessesRemaining':0,
 'alreadyPassedEndpointAndClientEvidenceReused':True,'noFixtureReopened':True,'nssNeverOpenedThisAttempt':True,
 'activeLockReleasedOnlyAfterProof':True,'mutableLedgerState':'RESTORED','originalRuntimeResultState':'RESTORATION_UNCONFIRMED',
 'heartbeatStillPaused':True,'classifierNss68Unchanged':True,'cs2OrSteamOperated':False,'permanentNssDeployment':False})
new(repo/'evidence/v44-unique-label-candidate.json',{
 'passedAsSoftwareCandidate':True,'modelOnly':True,'modelCount':17,'modelChecks':candidate_model['checks'],
 'sourceHashes':candidate_model['sourceHashes'],'sourceBindings':3405,'inheritedBindings':3354,
 'runtimeNamespaceAddedToFinalAuditLabel':True,'twoNewOutputIsolationRegressions':True,
 'sharedPublicationHelperUnchanged':True,'separatorRepairRetained':True,'sevenLuaAndPolicyUnchanged':True,
 'defaultInspectExecuted':True,'trafficGenerated':False,'routerWrites':False,'hardwareExecuted':False,
 'newLiveEntryAcceptance':False,'candidateRoot':'work/v44-unique-label-entry','inputSha256ByRole':{k:v for k,v in sealed_hashes.items() if k.startswith('unique-label-')}})

# Preserve frozen line endings using only exact new source paths, as done for prior exports.
attributes=[]
for rel in new_sources:
    data=(w/rel).read_bytes();options=[]
    if b'\r\n' in data:options.append('cr-at-eol')
    if re.search(rb'[ \t]+\r?$',data,re.M):options.append('-blank-at-eol')
    if re.search(rb'(?:\r?\n){2,}$',data):options.append('-blank-at-eof')
    if options:attributes.append('/code/'+rel+' whitespace='+','.join(options))
if attributes:
    p=repo/'.gitattributes';p.write_text(p.read_text(encoding='utf8')+'\n# Preserve exact new v44 frozen source bytes and local failure records.\n'+'\n'.join(attributes)+'\n',encoding='utf8')
new(repo/'evidence/v44-source-proof.json',{
 'passed':True,'historicPrefixSources':4553,'newSources':len(new_sources),'sourceHashes':new_sources,
 'runtimeSourceSets':runtime_sets,'originalCodeAndEvidenceBlobsChecked':len(old),'oldCodeAndEvidenceUnmodified':True,
 'twoActualBindingSetsFrozenExact':frozen_counts,'privateInputsCopiedExact':len(sealed_hashes),
 'inputSha256ByRole':sealed_hashes,'originalV43AndV44FailuresPreserved':True,
 'candidateNeverUsedForTraffic':True,'modelSyntheticClientPointerNotMistakenForProduction':True,
 'exactPathAttributes':attributes,'noGlobalWhitespacePolicyChange':True})
manifest['generatedAt']=datetime.now(timezone.utc).isoformat()
manifest['lastBoundedEntryRepairExport']='V44_LOCAL_REPAIRS_ACQUISITION_REFUSED_READONLY_RESTORED'
assert manifest['sources'][:4553]==prefix
(repo/'source-manifest.json').write_text(dump(manifest),encoding='utf8')

now=datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
report=f'''# 有界入口整合：准入前退出，恢复已确认

北京时间{now}。用户恢复执行权限后，原v43提交`{base}`已推送并实际Git archive校验，4553源SHA / 5209文件 / 1442链接通过；原3290份v1/v1.1 code/evidence保持。没有修改凭据或Git配置。

v43恢复后的首次入口因本地命名空间替换漏掉尾部分隔符，在SSH和负载前拒绝。原失败保留；v44只修复该分隔符并增加两项回归检查，15模型通过。一次只读确认健康和物理默认队列后才解除原锁。

## 唯一一次实际流量窗口

v44自有四TCP＋模拟UDP运行{client['seconds']:.2f}秒，TCP客户端payload {client['tcpBytes']}字节、客户端错误0。最后实际分类source age {frame['sourceAge']:.2f}秒：

| 槽 | 自动分类 | WAN |
|---|---|---|
| TCP1 | BULK | 1 |
| TCP2 | BULK | 1 |
| TCP3 | BULK | 2 |
| TCP4 | BULK | 4 |
| UDP | RT | 3 |

五WAN要求没有满足，原30秒自然取得窗口结束即拒绝，未调用NSS checkpoint、owner、stage或ECM；没有NSS B段。这是取得前提的失败，不能归为NSS/firmware或分类失效。没有改PBR、分类门槛、期限或再开fixture。全fixture UDP {client['udpSent']}发 / {client['udpReceived']}返只作软件窗口记录；停止边界待返回包不归因NSS，不代替v42内部B窗口2373/2373。

## 恢复与已证实的本地修复

端点关闭、精确规则0/FW基线和客户端退出已通过。原最终审核在共享`nss122`输出的固定`v44-final`名称处遇到EEXIST；先前只读确认已使用这个名字。原错误和RESTORATION_UNCONFIRMED结果原字节保留。

随后只在新目录补一次失败的只读健康及两物理队列步骤，使用唯一label：source {audit['queryAge']:.2f}秒 / selectors {audit['selectors']}，五WAN健康、保护配置不变、ECM关闭全零；wan/lan4原mq＋四fq_codel所有选项与handle一致，自有入口进程0。已通过的端点/客户端证据复用，未重开流量。只有证明齐全后才将可变入口ledger标RESTORED并解除锁；原失败结果未改写为通过。

`work/v44-unique-label-entry`已把最后审核label绑定完整新runtime命名空间，增加两项实际生成输出隔离回归，17模型和默认inspect通过。七Lua数据面、分类/QoS/期限/字节上限保持。**这是软件候选，未运行新硬件会话；完整可复用入口现场验收仍未通过。** 本轮完成封存，不因自然WAN分布继续盲重试。

v42的五WAN五流60.01秒、121次ECM5、20续租、2373模拟UDP全部回包、完整十tag/leaf/CT/mark/NAT/affinity及恢复仍成立。v41计数差异仍known limitation；旧CPU和v1证据复用，本次不新增CPU、CS2/Steam、永久/全网/长期声明。heartbeat保持暂停。

已知限制：自然PBR在30秒内可能配不齐五WAN；偶发SSH取得超时；v41分类计数差异根因未知；普通应用factory和最新输出隔离候选尚未现场验收。连续新代、长期/永久/全网、WiFi/autorate/ECN留v1.1/v2，不自动新增实验。

证据：[实际入口](../evidence/v44-bounded-entry.json)、[完整恢复](../evidence/v44-restoration.json)、[修订候选](../evidence/v44-unique-label-candidate.json)、[源与冻结](../evidence/v44-source-proof.json)、[v43原本地拒绝](../evidence/v43-resumed-local-refusal.json)、[v42验收](FIVE_WAN_SIMULATED_ACCEPTANCE_2026-10-07.md)。
'''
(repo/'docs/BOUNDED_ENTRY_INTEGRATION_2026-10-07.md').write_text(report,encoding='utf8')
header=f'''# v44入口准入前退出，已完整恢复；五WAN硬件验收保持

更新：北京时间{now}。执行权限恢复后，原v43提交`{base}`已推送并实际archive读回，4553源SHA/5209文件/1442链接。v43首次恢复尝试因本地路径替换漏尾部分隔符，在连接/fixture前拒绝；新v44分隔符修复15模型通过，旧失败不改。

唯一一次v44自有四TCP＋模拟UDP实际{client['seconds']:.2f}秒，分类4BULK/1RT，TCP WAN1/1/2/4、UDP WAN3。原30秒自然取得窗口结束，未配齐五WAN，在NSS checkpoint/owner/stage/ECM前退出；客户端错误0，没有NSS B或新硬件验收，不放宽PBR/期限、不盲重试。

端点规则0/FW基线与客户端退出通过。最终audit固定label与先前只读记录冲突EEXIST，原失败保留；只在新目录补一次失败只读步骤，source{audit['queryAge']:.2f}/selectors{audit['selectors']}、五WAN健康/配置不变/ECM关闭全零、两物理原mq＋四fq_codel选项/handle和自有进程0通过。可变ledger RESTORED，原RESTORATION_UNCONFIRMED结果原字节保留。

新`work/v44-unique-label-entry`以完整新runtime隔离最终输出，17模型/默认inspect通过，没有新流量；完整可复用入口现场验收仍未通过。v42五WAN60.01秒/ECM5/20续租/2373UDP全回与高级QoS功能验收保持；v41差异仍known limitation。常驻NSS68未改，无CS2/Steam、新CPU或永久部署，heartbeat仍暂停。

本轮封存，不自动开启新实验。自然取得未配齐是有界前提限制；最新入口候选待有新可执行条件时的一次整合，不强行重试。详情：[入口整合报告](BOUNDED_ENTRY_INTEGRATION_2026-10-07.md)、[入口使用](BOUNDED_MULTIWAN_ENTRY.md)。

## 以下为原历史记录，旧“未推送”和“权限不可用”只对应当时状态

'''
for name in ['docs/STATE.md','docs/PLAN.md','docs/EXPERIMENT_LOG.md','AGENTS.md']:
    p=repo/name;text=header
    if name=='AGENTS.md':text=text.replace('(BOUNDED_ENTRY_INTEGRATION_2026-10-07.md)','(docs/BOUNDED_ENTRY_INTEGRATION_2026-10-07.md)').replace('(BOUNDED_MULTIWAN_ENTRY.md)','(docs/BOUNDED_MULTIWAN_ENTRY.md)')
    p.write_text(text+p.read_text(encoding='utf8'),encoding='utf8')
p=repo/'README.md';p.write_text('''# Athena NSS 多WAN / 高级QoS受控原型

五WAN硬件功能验收保持。可复用入口已补本地分隔符和输出隔离：17模型、默认inspect通过；唯一实际流量窗口未自然配齐五WAN，在NSS写前拒绝并完整恢复，最新入口现场验收仍未通过。原v43推送和归档已补齐。见[本次整合](docs/BOUNDED_ENTRY_INTEGRATION_2026-10-07.md)、[入口使用](docs/BOUNDED_MULTIWAN_ENTRY.md)和[STATE](docs/STATE.md)。

## 以下保留历史交付，旧状态按当时记录解读

'''+p.read_text(encoding='utf8'),encoding='utf8')
p=repo/'docs/BOUNDED_MULTIWAN_ENTRY.md';p.write_text('''# 可复用的有界多 WAN 入口：最新软件候选

当前推荐的本地预览与状态候选是`work/v44-unique-label-entry/entry.mjs`，命令仍为默认inspect / status / run / stop。17项模型与默认inspect通过；run和stop的完整现场闭环尚未通过。本轮停止新增流量，勿把以下命令清单理解为自动重试计划。

```powershell
& 'C:/Users/lishu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe' 'work/v44-unique-label-entry/entry.mjs' inspect
& 'C:/Users/lishu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe' 'work/v44-unique-label-entry/entry.mjs' status
```

未来明确一次run仍需要本地已绑定源、部署资料和SSH；在原30秒自然取得期限内必须配齐五WAN，未知默认拒绝。原60秒B、source6/kernel90最大120/owner180/client180/guard210/server250和各字节预算保持，写前仍需新checkpoint下载/SHA/gzip与独立恢复。恢复未确认保留锁，禁止下一代。stop只控制同session自有发送和下一次准入；收到请求不等于硬件恢复已通过。

v43固定命名空间替换漏分隔符和v44固定审核label冲突均有实际本地失败证据；最新候选保留分隔符，并将最终label绑定完整新runtime。没有改分类、QoS、七Lua数据面或共享publication helper。v44唯一实际流量窗4BULK/1RT，但TCP WAN1/1/2/4＋UDP WAN3未配齐，NSS写前退出；一次新目录只读补核验确认完整恢复。见[本次完整记录](BOUNDED_ENTRY_INTEGRATION_2026-10-07.md)、[17模型候选](../evidence/v44-unique-label-candidate.json)。

## 以下保留v43原软件与失败记录，旧权限描述仅对应当时

'''+p.read_text(encoding='utf8'),encoding='utf8')
p=repo/'docs/MULTI_WAN_QOS.md';p.write_text('''# 多 WAN / 高级 QoS 当前交付范围

v42五WAN五流60.01秒/ECM5/20续租及双向十tag、leaf、完整mark/NAT/affinity和恢复已成立。DOWN18共享借用、UP60每WAN12硬上限、RT prio0/FQ-CoDel保持。数据面本轮原字节不改，历史CPU证据复用。

可复用入口最新软件候选v44输出隔离17模型/默认inspect通过。唯一实际入口4BULK/1RT未在原30秒自然配齐五WAN，NSS写前拒绝并完整恢复；完整最新入口现场验收仍未通过。不从模型或有界v42验收推成全网、永久、长期交付，不盲重试或强改PBR取得资格。

自然取得限制、v41计数差异、偶发SSH取得超时和普通应用factory未验保留后续；WiFi/autorate/ECN、连续新代/扩大流池、长期部署留v1.1/v2。见[本次入口整合](BOUNDED_ENTRY_INTEGRATION_2026-10-07.md)。

## 以下保留前次能力描述，最新入口状态以上文为准

'''+p.read_text(encoding='utf8'),encoding='utf8')

checker=repo/'tools/check_repository.py';text=checker.read_text(encoding='utf8')
needle="print(json.dumps({'passed':True,'filesChecked':count";assert text.count(needle)==1
checks='''if (root/'evidence/v44-bounded-entry.json').exists():
 a=json.loads((root/'evidence/v44-bounded-entry.json').read_text(encoding='utf8'))
 r=json.loads((root/'evidence/v44-restoration.json').read_text(encoding='utf8'))
 c=json.loads((root/'evidence/v44-unique-label-candidate.json').read_text(encoding='utf8'))
 s=json.loads((root/'evidence/v44-source-proof.json').read_text(encoding='utf8'))
 p=json.loads((root/'evidence/v43-resumed-local-refusal.json').read_text(encoding='utf8'))
 assert manifest['lastBoundedEntryRepairExport']=='V44_LOCAL_REPAIRS_ACQUISITION_REFUSED_READONLY_RESTORED'
 assert a['entryModelChecksPassed'] and a['modelCount']==len(a['modelChecks'])==15 and a['actualBindings']==3405 and a['inheritedBindings']==3354
 assert a['fixtureAttemptCount']==1 and a['failureCategory']=='NATURAL_FIVE_WAN_ACQUISITION_WINDOW_ENDED' and a['acquisitionSecondsLimit']==30
 f=a['actualLastFrame'];assert f['sourceAge']<6 and f['tcpClasses']==['BULK']*4 and f['udpClasses']==['RT'] and f['tcpWanSetInSlotOrder']==[1,1,2,4] and f['udpWan']==3 and f['fiveDistinctWanPairs']==0
 assert not any(a[k] for k in ['entryHardwareIntegrationPassed','checkpointStarted','nssStageStarted','ecmOpened','caseCreated','controllerOwnerCreated','newHardwareAcceptance','newCpuAcceptance','cs2OrSteamOperated','permanentNssDeployment'])
 assert a['noBlindFixtureRetry'] and a['noPbrOrClassificationThresholdChange'] and a['restorationState']=='RESTORED' and a['originalResultState']=='RESTORATION_UNCONFIRMED' and a['originalResultAndErrorsUnchanged']
 assert a['clientErrors']==0 and a['clientRuntimeSeconds']<180 and a['clientUdpWholeFixture']['notNssMeasurements'] and a['v42HardwareAcceptanceStillValid']
 assert r['passed'] and r['readonlySupplementAttempts']==1 and r['originalFailuresPreserved'] and r['noFixtureReopened'] and r['activeLockReleasedOnlyAfterProof']
 q=r['finalFullAudit'];assert q['passed'] and q['queryAge']<6 and q['ecmClosedAndZero'] and q['protectedConfigurationUnchanged'] and q['allFiveHealthyWanBaseline']
 assert r['physicalQueues']['defaultQueueOptionsAndHandlesExact'] and r['clientClosure']['ownedTestProcessesRemaining']==0 and r['ownedEntryProcessesRemaining']==0
 e=r['endpointClosure'];assert e['passed'] and e['ownedRulesRemaining']==0 and e['baselineRestored'] and e['exactOwnedEndpointClosed']
 assert c['passedAsSoftwareCandidate'] and c['modelOnly'] and c['modelCount']==len(c['modelChecks'])==17 and c['sourceBindings']==3405 and c['runtimeNamespaceAddedToFinalAuditLabel'] and c['twoNewOutputIsolationRegressions']
 assert c['sharedPublicationHelperUnchanged'] and c['sevenLuaAndPolicyUnchanged'] and c['defaultInspectExecuted'] and not any(c[k] for k in ['hardwareExecuted','routerWrites','trafficGenerated','newLiveEntryAcceptance'])
 assert s['passed'] and s['historicPrefixSources']==4553 and s['newSources']==len(s['sourceHashes']) and s['originalCodeAndEvidenceBlobsChecked']==5136 and s['oldCodeAndEvidenceUnmodified']
 assert s['twoActualBindingSetsFrozenExact']=={'v43-local-refusal':3405,'v44-acquisition-refusal':3405} and s['originalV43AndV44FailuresPreserved'] and s['candidateNeverUsedForTraffic'] and s['noGlobalWhitespacePolicyChange']
 for entry in [a['modelSourceHashes'],c['sourceHashes'],s['sourceHashes']]:
  for rel,digest in entry.items():assert hashlib.sha256((root/'code'/rel).read_bytes()).hexdigest()==digest,rel
 for runtime,value in s['runtimeSourceSets'].items():
  assert value['actualBindings']==3405 and value['sevenLuaByteExactV42'] and len(value['sourceHashes'])==51
  for rel,digest in value['sourceHashes'].items():assert hashlib.sha256((root/'code'/rel).read_bytes()).hexdigest()==digest,rel
  for name in ['fast-path.lua','classifier.lua','classified-tags.lua','module-stage-guardian.lua','qos-physical.lua','wan-scope.lua','tag-normalizer.lua']:
   assert (root/'code'/runtime/name).read_bytes()==(root/'code/work/v42-counter-window'/name).read_bytes(),name
 for attr in s['exactPathAttributes']:assert attr.startswith('/code/work/') and attr in (root/'.gitattributes').read_text(encoding='utf8')
 assert p['originalPublicationNowPushedAndArchiveChecked'] and p['refusedBeforeRouterConnectionAndFixture'] and p['readonlyConfirmationPassedBeforeOldLockRelease'] and p['originalRuntimeAndResultUnchanged']
'''
checker.write_text(text.replace(needle,checks+needle),encoding='utf8')
for name,digest in old.items():assert sha((repo/name).read_bytes())==digest,name
new(root/'publication-candidate.json',{'passed':True,'newSources':len(new_sources),'totalSources':len(manifest['sources']),
 'originalCodeAndEvidenceBlobsUnchanged':len(old),'privateInputsSealed':len(sealed_hashes),
 'originalV43PublicationRecovered':True,'v44NssHardwareAcceptance':False,'restorationPassed':True,'candidateModelChecks':17})
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Athena NSS — 入口整合</title><style>body{font:16px/1.75 system-ui,sans-serif;color:#17302a;background:#f5f7f5;max-width:900px;margin:40px auto;padding:0 24px}main{background:white;padding:32px;border-radius:16px}h1{font-size:28px;line-height:1.3}h2{font-size:20px;margin-top:30px}table{border-collapse:collapse;width:100%}td,th{padding:12px;border-bottom:1px solid #dce5df;text-align:left}.ok{color:#18734d}.pending{color:#966313}small{color:#62746a}a{color:#1e6b4a}</style><main><small>ATHENA NSS · '''+html.escape(now)+'''</small><h1>入口准入前退出<br><span class="ok">完整恢复已确认</span></h1><p>五WAN核心硬件功能仍采用v42已验收证据。本次只补可复用入口整合，未开启NSS。</p><table><tr><th>事项</th><th>结果</th></tr><tr><td>原v43发布</td><td class="ok">已推送并实际归档读回</td></tr><tr><td>本次自动分类</td><td>4 TCP BULK + 1 UDP RT</td></tr><tr><td>自然WAN分布</td><td class="pending">TCP 1 / 1 / 2 / 4，UDP 3；30秒期限内未配齐</td></tr><tr><td>NSS checkpoint / stage / ECM</td><td>均未开始</td></tr><tr><td>最终健康与恢复</td><td class="ok">五WAN健康、ECM关闭全零、物理队列原选项一致、端点与自有进程零残留</td></tr><tr><td>最新输出隔离候选</td><td>17模型 / 默认inspect通过；现场整合未验收</td></tr></table><h2>本轮边界</h2><p>自有脚本模拟实时UDP，没有操作CS2或Steam。原失败保留；不放宽期限/PBR，不盲重试，不新增CPU、永久或长期声明。</p><p><a href="../athena-nss-mainline/docs/BOUNDED_ENTRY_INTEGRATION_2026-10-07.md">完整记录</a> · <a href="../athena-nss-mainline/docs/STATE.md">当前STATE</a></p></main></html>'''
out=w/'outputs/nss44-entry-report.html'
with out.open('x',encoding='utf8') as f:f.write(page)
print(dump({'passed':True,'newSources':len(new_sources),'sourceHashes':len(manifest['sources']),
 'oldCodeEvidenceUnchanged':len(old),'candidateModels':17,'restorationPassed':True,'newNssHardwareAcceptance':False}))
