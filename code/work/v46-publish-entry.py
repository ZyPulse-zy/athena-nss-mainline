from pathlib import Path
from datetime import datetime, timezone, timedelta
import copy, hashlib, html, json, re, subprocess

w=Path(__file__).resolve().parents[1];repo=w/'athena-nss-mainline'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda b:hashlib.sha256(b).hexdigest()
dump=lambda v:json.dumps(v,ensure_ascii=False,indent=2)+'\n'
git=lambda *a:subprocess.check_output(['git','-C',str(repo),*a])
def new(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf8') as f:f.write(dump(v))
t=w/read(w/'work/v46-entry-resume-latest-private.json')['directory']
base='07001d7d60670094c684ab029332ef58b8411a4f'
assert git('rev-parse','HEAD').decode().strip()==base and not git('status','--porcelain')
manifest=read(repo/'source-manifest.json');prefix=copy.deepcopy(manifest['sources']);assert len(prefix)==4910
old={}
for row in git('ls-tree','-r','-z',base,'--','code','evidence').split(b'\0'):
    if row:
        _,name=row.split(b'\t');old[name.decode()]=sha((repo/name.decode()).read_bytes())
entry=w/'work/v45-early-acquisition';active=read(entry/'active-private.json');actual=w/active['runtimeRoot']
assert active['state']=='RESTORED' and active['restorationPassed'] and not active['hardwareCompleted'] and not (entry/'active-lock').exists()
assert read(t/'exit-private.json')['code']==1 and read(t/'continuation-intent-private.json')['singleContinuationAttempt']
pilot=w/read(actual/'pilot-reference-private.json')['directory'];load=w/read(actual/'load-latest-private.json')['dir'];closure=w/read(actual/'closure-pointer.json')['directory']
events=read(pilot/'driver-private.json');assert [e['code'] for e in events]==[0,0,0,1,0]
assert not (pilot/'case-reference-private.json').exists() and not (pilot/'detached-owner-reference-private.json').exists()
client=read(load/'result-private.json');assert client['seconds']<180 and client['errors']==['Owned SSH tcp3 acquisition refused: No first payload within 8 seconds']
summary=read(t/'summary-private.json');assert summary['firstAllFourPidsSeconds']<.1 and summary['firstAllFourPayloadSeconds']<12
audit=summary['finalAudit'];physical=summary['physical'];endpoint=summary['endpoint'];clients=summary['clients']
assert audit['passed'] and audit['queryAge']<6 and audit['ecmClosedAndZero'] and audit['allFiveHealthyWanBaseline'] and audit['protectedConfigurationUnchanged']
assert physical['passed'] and physical['defaultQueueOptionsAndHandlesExact']
assert endpoint['passed'] and endpoint['ownedRulesRemaining']==0 and endpoint['baselineRestored'] and endpoint['exactOwnedEndpointClosed']
assert clients['passed'] and clients['ownedTestProcessesRemaining']==0 and not clients['clientDeadlineReset']
model=read(w/read(entry/'entry-model-latest-private.json')['receipt']);assert model['passed'] and len(model['checks'])==24 and model['sourceBindings']==3406
for rel,h in model['sourceHashes'].items():assert sha((w/rel).read_bytes())==h
bindings=read(pilot/'actual-entry-bindings.json');assert len(bindings)==3406
for rel,h in bindings.items():assert sha((w/rel).read_bytes())==h and (pilot/'frozen'/rel).read_bytes()==(w/rel).read_bytes(),rel
q=read(actual/'entry-qualified.json');assert q['passed'] and q['actualBindings']==3406 and q['inheritedBindings']==3354 and len(q['sourceManifest'])==52
assert q['dataPlaneByteExact'] and q['classificationAndQosPolicyUnchanged']
for rel,h in q['sourceManifest'].items():assert sha((w/rel).read_bytes())==h
for name in ['fast-path.lua','classifier.lua','classified-tags.lua','module-stage-guardian.lua','qos-physical.lua','wan-scope.lua','tag-normalizer.lua']:
    assert (actual/name).read_bytes()==(w/'work/v42-counter-window'/name).read_bytes()
old_runtime=w/read(t/'continuation-intent-private.json')['oldRuntimeRoot']
old_public=read(repo/'evidence/v45-entry-startup.json');assert sha((old_runtime/'entry-result-private.json').read_bytes())==old_public['inputSha256ByRole']['entry-original-result']
prior_receipt=w/read(entry/'publication-pointer-private.json')['directory']/'published-night-receipt.json';prior=read(prior_receipt)
assert prior['passed'] and prior['commit']==base and prior['actualGitArchiveChecked'] and prior['remoteCommitMatched']
matching=read(t/'acquisition-summary.json');assert len(matching)==10 and matching[-1]['code']==1
assert any({'slot':'tcp3','attempt':3} in x['rotations'] for x in matching)
frame=read(actual/'controlled-candidates-private.json');assert len(frame['pairs'])==0
slots={slot:next((f['identity']['wan'] for f in frame['flows'] if f['identity']['protocolNumber']==6 and f['identity']['original']['sport']==sport),None) for slot,sport in frame['ownedTcpSlots'].items()}

sources=set(q['sourceManifest']);sources.update(['work/v46-resume-entry.py','work/v46-publish-entry.py'])
indexed={x['workspaceSource']:x for x in manifest['sources']};new_sources={}
for rel in sorted(sources):
    data=(w/rel).read_bytes()
    if rel in indexed:assert sha(data)==indexed[rel]['sha256'];continue
    p=repo/'code'/rel;p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb') as f:f.write(data)
    new_sources[rel]=sha(data);manifest['sources'].append({'path':'code/'+rel,'workspaceSource':rel,'sha256':sha(data),'bytes':len(data),'role':'v46-same-v45-entry-concurrent-startup-and-pre-nss-acquisition-refusal'})
inputs={'continuation-intent':t/'continuation-intent-private.json','driver':pilot/'driver-private.json','actual-bindings':pilot/'actual-entry-bindings.json','entry-result':actual/'entry-result-private.json','fixture-result':load/'result-private.json','fixture-timeline':load/'load-samples-private.jsonl','matching':load/'matching-private.json','last-classification':actual/'controlled-candidates-private.json','final-audit':closure/'final-audit-stdout-private.txt','physical-raw':closure/'physical-final-raw-private.json','endpoint-closure':load/'endpoint-retry-closure.json','client-closure':closure/'client-closure.json','prior-archive':prior_receipt}
sealed=t/'sealed-inputs-private';sealed.mkdir();sealed_hashes={}
for role,p in inputs.items():
    data=p.read_bytes();target=sealed/(role+p.suffix)
    with target.open('xb') as f:f.write(data)
    assert target.read_bytes()==data;sealed_hashes[role]=sha(data)
new(sealed/'manifest-private.json',sealed_hashes)
actual_ev={'sameV45QualifiedSourcesReused':True,'modelChecksReused':24,'modelSourceHashes':model['sourceHashes'],'actualBindings':3406,'inheritedBindings':3354,'sevenLuaByteExactV42':True,'limits':model['limits'],'entryContinuationAttempts':1,'fixtureAttempts':1,'driverEventCodes':[0,0,0,1,0],
 'concurrentStartupActuallyExecuted':True,'firstAllFourPidsSeconds':summary['firstAllFourPidsSeconds'],'firstAllFourPayloadSeconds':summary['firstAllFourPayloadSeconds'],'firstPidPublicationBySlotSeconds':summary['firstPidPublicationBySlotSeconds'],
 'failureCategory':'ROTATED_OWNED_TCP3_CANDIDATE_NO_FIRST_PAYLOAD_WITHIN_ORIGINAL_8_SECONDS','failureAfterNaturalWanDeduplicationRotations':True,'rootCauseProved':False,'furtherAdmissionStopped':True,'tcp3FinalAttempt':3,'tcp4FinalAttempt':4,'matchingReads':10,'lastFrameSourceAge':frame['sourceAge'],'lastFrameTcpBulk':len(frame['tcp']),'lastFrameUdpRt':len(frame['udp']),'lastObservedWanByOwnedSlot':slots,'fiveWanPairs':0,
 'clientSeconds':client['seconds'],'clientTcpPayloadBytes':client['tcpBytes'],'wholeFixtureUdp':{'sent':client['udpSent'],'returned':client['udpReceived'],'notNssMeasurements':True,'stopBoundaryOutstandingNotAttributedToNss':True},
 'checkpointStarted':False,'nssStageStarted':False,'ecmOpened':False,'hardwareEntryIntegrationPassed':False,'newCpuAcceptance':False,'cs2OrSteamOperated':False,'permanentNssDeployment':False,'v42HardwareAcceptanceRetained':True,'originalAcquisitionRetryRotationAndDeadlineLimitsKept':True,'originalV45FailureUnchanged':True,'inputSha256ByRole':sealed_hashes}
new(repo/'evidence/v46-entry-continuation.json',actual_ev)
new(repo/'evidence/v46-restoration.json',{'passed':True,'finalFullAudit':audit,'physicalQueues':physical,'endpointClosure':endpoint,'clientClosure':{'passed':clients['passed'],'ownedTestProcessesRemaining':clients['ownedTestProcessesRemaining'],'clientDeadlineReset':clients['clientDeadlineReset'],'guards':clients['guards']},'state':'RESTORED','lockReleasedAfterProof':True,'original180SecondFirewallGuardianNaturalExpiryWaited':True,'nssNeverOpened':True,'noAdditionalFixtureRetry':True,'heartbeatStillPaused':True,'classifierNss68Unchanged':True})
attributes=[]
for rel in new_sources:
    data=(w/rel).read_bytes();options=[]
    if b'\r\n' in data:options.append('cr-at-eol')
    if re.search(rb'[ \t]+\r?$',data,re.M):options.append('-blank-at-eol')
    if re.search(rb'(?:\r?\n){2,}$',data):options.append('-blank-at-eof')
    if options:attributes.append('/code/'+rel+' whitespace='+','.join(options))
if attributes:
    p=repo/'.gitattributes';p.write_text(p.read_text(encoding='utf8')+'\n# Exact fresh v46 runtime bytes; original v45 sources remain unchanged.\n'+'\n'.join(attributes)+'\n',encoding='utf8')
new(repo/'evidence/v46-source-proof.json',{'passed':True,'historicPrefixSources':4910,'newSources':len(new_sources),'sourceHashes':new_sources,'runtimeSourceHashes':q['sourceManifest'],'actualBindingsFrozenExact':3406,'oldCodeEvidenceBlobsChecked':len(old),'oldCodeEvidenceUnmodified':True,'privateInputsSealed':len(sealed_hashes),'inputSha256ByRole':sealed_hashes,'originalV45EntrySourcesAndFailureUnchanged':True,'exactPathAttributes':attributes,'noGlobalWhitespacePolicyChange':True})
manifest['generatedAt']=datetime.now(timezone.utc).isoformat();manifest['lastResumedEntryExport']='V46_CONCURRENT_STARTUP_PROVED_ROTATED_TCP_TIMEOUT_RESTORED'
assert manifest['sources'][:4910]==prefix;(repo/'source-manifest.json').write_text(dump(manifest),encoding='utf8')
now=datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
body=f'''# 同字节v45入口接续：并发启动已实测，完整整合未通过

北京时间{now}。端点只读已恢复连接、精确端口/单位零残留、原入口RESTORED后，本次复用原24模型/3406绑定的v45入口源字节，只接续一次自有四TCP＋模拟UDP，不重做离线准备和v42核心证明。

四个初始PID分别在0.076/0.079/0.083/0.087秒发布，四路第一次同时有payload在{summary['firstAllFourPayloadSeconds']:.2f}秒；并发启动已实际执行。v44历史全部PID齐备16.01秒，只作不同窗口的记录，不声称同负载CPU或固定收益。

原实际CIM/socket/CT/WAN核对发现重复WAN后，在原30秒取得窗内只替换自有tcp3/tcp4候选；tcp/tcp2实际WAN1/WAN5保持。第三条TCP的第3候选8秒没有首包，原重试上限拒绝，客户端在{client['seconds']:.2f}秒退出，最后分类读随退出失败。原driver codes为0/0/0/1/0，10次匹配读，最后完整五WAN pair为0。没有扩大重试、期限、流池、PBR或分类门槛。

TCP客户端payload {client['tcpBytes']}字节；全fixture UDP {client['udpSent']}发/{client['udpReceived']}返。没有NSS B段，停止边界的未返回包不归因NSS。没有NSS checkpoint、owner、stage或ECM；首包超时根因未知，不能归因firmware/gate/lease。**并发启动功能已得到现场证明，完整可复用NSS入口仍未验收。**

按原180秒FW守护自然到期后关闭精确端点，规则0/canonical基线与单位关闭通过。原客户端180秒/独立210秒guard保持，精确自有进程0。最终source {audit['queryAge']:.2f}秒/selectors{audit['selectors']}，五WAN健康/保护配置不变/ECM关闭全零，两物理wan/lan4原mq＋四fq_codel的全部选项/handle一致；RESTORED、锁解除。原v45失败、源码和报告保持，heartbeat仍暂停。

v42五WAN五流60.01秒/ECM5/20续租/2373RT全部返回、十tag/leaf/完整mark/NAT/affinity与恢复仍成立；DOWN18共享借用、UP60每WAN12硬上限、RT prio0/FQ-CoDel不变。没有操作CS2/Steam、新CPU测试或永久开启NSS。

当前限制是自然WAN去重与候选SSH首包取得失败，普通应用factory、长期/永久/全网仍未验收；v41计数差异和WiFi/autorate/ECN等后续边界保持。本次停止新增fixture，保留证据；下一项应针对实际候选首包取得条件，不继续为配WAN盲重试或重复已验收NSS数据面。

证据：[实际入口](../evidence/v46-entry-continuation.json)、[恢复](../evidence/v46-restoration.json)、[源码](../evidence/v46-source-proof.json)、[当前入口](BOUNDED_MULTIWAN_ENTRY.md)、[v42硬件](FIVE_WAN_SIMULATED_ACCEPTANCE_2026-10-07.md)。
'''
(repo/'docs/V46_ENTRY_CONTINUATION_2026-10-07.md').write_text(body,encoding='utf8')
header=f'''# 同字节v45入口接续：并发启动实测通过，候选首包超时，已恢复

更新：北京时间{now}。原v45提交`{base}`已push/archive通过4910源SHA/5577文件/1480链接。端点只读恢复连接后，只复用24模型/3406绑定的原v45源码接续一次，未重跑核心准备。四初始PID约0.087秒齐备、四路第一次同时payload约{summary['firstAllFourPayloadSeconds']:.2f}秒；并发启动已实测。

自然WAN去重替换tcp3/tcp4后，tcp3第3候选8秒无首包触发原上限，客户端{client['seconds']:.2f}秒退出；完整五WAN pair0，最后分类读随退出拒绝。没有NSS checkpoint/owner/stage/ECM，完整最新版入口整合仍未通过；根因未知，不归因NSS，不放宽PBR/期限/重试或盲重开fixture。全fixture UDP{client['udpSent']}/{client['udpReceived']}非NSS证据，边界未返不当NSS丢包。

原FW180秒自然到期后端点规则0/canonical基线/精确单位关闭通过，客户端与独立210秒guard退出、自有进程0。最终source{audit['queryAge']:.2f}/selectors{audit['selectors']}、五WAN健康/保护配置不变/ECM关闭全零，两物理原mq＋四fq_codel全部选项/handle一致，RESTORED/锁解除。旧v45失败/源码/报告原字节保持，常驻NSS68不变，heartbeat暂停，无CS2/Steam/新CPU/永久NSS。

v42五WAN高级QoS核心硬件验收保持。下一问题仅为候选首包取得条件，不自动重开fixture或重复NSS核心；自然取得限制、SSH超时、v41差异和普通应用factory未验保持。详情：[本次接续](V46_ENTRY_CONTINUATION_2026-10-07.md)、[入口使用](BOUNDED_MULTIWAN_ENTRY.md)。

## 以下保留原历史记录，旧“最新”按当时解读

'''
for name in ['docs/STATE.md','docs/PLAN.md','docs/EXPERIMENT_LOG.md','AGENTS.md']:
    p=repo/name;head=header
    if name=='AGENTS.md':head=head.replace('(V46_ENTRY_CONTINUATION_2026-10-07.md)','(docs/V46_ENTRY_CONTINUATION_2026-10-07.md)').replace('(BOUNDED_MULTIWAN_ENTRY.md)','(docs/BOUNDED_MULTIWAN_ENTRY.md)')
    p.write_text(head+p.read_text(encoding='utf8'),encoding='utf8')
for name,lead in {'README.md':'# Athena NSS 多WAN / 高级QoS受控原型\n\n五WAN核心硬件功能已验收。原v45入口本次并发启动已实测，但自然WAN去重后的TCP候选首包超时，NSS写前拒绝并完整恢复；完整最新入口尚未通过，没有永久部署。见[当前接续](docs/V46_ENTRY_CONTINUATION_2026-10-07.md)、[STATE](docs/STATE.md)。\n',
 'docs/BOUNDED_MULTIWAN_ENTRY.md':'# 当前入口：v45同字节候选，已实测并发启动\n\n本地仍为`work/v45-early-acquisition/entry.mjs`，原24模型/3406绑定不变，inspect/status/run/stop方式保持。新一次接续四PID0.087秒齐备、四路第一次同时payload10.71秒；自然WAN去重替换后TCP候选首包超时，NSS写前退出并完整恢复。完整入口尚未通过，勿为配齐WAN盲重试。见[实际接续](V46_ENTRY_CONTINUATION_2026-10-07.md)。\n',
 'docs/MULTI_WAN_QOS.md':'# 多WAN / 高级QoS当前交付范围\n\nv42五WAN60.01秒/ECM5/20续租、2373RT全回、十tag/leaf/mark/NAT/affinity与恢复保持。DOWN18共享借用、UP60每WAN12、RT prio0/FQ-CoDel不变。v45入口并发启动已实测，候选首包取得失败导致最新完整整合仍未通过；本次未开启NSS并已完整恢复，非永久/全网/长期交付。见[本次接续](V46_ENTRY_CONTINUATION_2026-10-07.md)。\n'}.items():
    p=repo/name;p.write_text(lead+'\n## 以下为历史状态\n\n'+p.read_text(encoding='utf8'),encoding='utf8')
checker=repo/'tools/check_repository.py';text=checker.read_text(encoding='utf8');needle="print(json.dumps({'passed':True,'filesChecked':count";assert text.count(needle)==1
checks='''if (root/'evidence/v46-entry-continuation.json').exists():
 a=json.loads((root/'evidence/v46-entry-continuation.json').read_text(encoding='utf8'));r=json.loads((root/'evidence/v46-restoration.json').read_text(encoding='utf8'));s=json.loads((root/'evidence/v46-source-proof.json').read_text(encoding='utf8'))
 assert manifest['lastResumedEntryExport']=='V46_CONCURRENT_STARTUP_PROVED_ROTATED_TCP_TIMEOUT_RESTORED'
 assert a['sameV45QualifiedSourcesReused'] and a['modelChecksReused']==24 and a['actualBindings']==3406 and a['inheritedBindings']==3354 and a['entryContinuationAttempts']==a['fixtureAttempts']==1 and a['driverEventCodes']==[0,0,0,1,0]
 assert a['concurrentStartupActuallyExecuted'] and 0<a['firstAllFourPidsSeconds']<.1 and 0<a['firstAllFourPayloadSeconds']<12 and a['failureAfterNaturalWanDeduplicationRotations'] and a['tcp3FinalAttempt']==3 and a['matchingReads']==10 and a['fiveWanPairs']==0
 assert a['originalAcquisitionRetryRotationAndDeadlineLimitsKept'] and a['originalV45FailureUnchanged'] and a['v42HardwareAcceptanceRetained'] and a['wholeFixtureUdp']['notNssMeasurements']
 assert not any(a[k] for k in ['rootCauseProved','checkpointStarted','nssStageStarted','ecmOpened','hardwareEntryIntegrationPassed','newCpuAcceptance','cs2OrSteamOperated','permanentNssDeployment'])
 q=r['finalFullAudit'];assert r['passed'] and q['passed'] and q['queryAge']<6 and q['allFiveHealthyWanBaseline'] and q['ecmClosedAndZero'] and q['protectedConfigurationUnchanged'] and r['physicalQueues']['defaultQueueOptionsAndHandlesExact']
 e=r['endpointClosure'];c=r['clientClosure'];assert e['passed'] and e['ownedRulesRemaining']==0 and e['baselineRestored'] and e['exactOwnedEndpointClosed'] and c['passed'] and c['ownedTestProcessesRemaining']==0 and not c['clientDeadlineReset']
 assert s['passed'] and s['historicPrefixSources']==4910 and s['newSources']==len(s['sourceHashes']) and s['oldCodeEvidenceUnmodified'] and s['actualBindingsFrozenExact']==3406 and s['originalV45EntrySourcesAndFailureUnchanged'] and s['noGlobalWhitespacePolicyChange']
 for entry in [s['sourceHashes'],s['runtimeSourceHashes'],a['modelSourceHashes']]:
  for rel,digest in entry.items():assert hashlib.sha256((root/'code'/rel).read_bytes()).hexdigest()==digest,rel
'''
checker.write_text(text.replace(needle,checks+needle),encoding='utf8')
for name,h in old.items():assert sha((repo/name).read_bytes())==h,name
new(t/'publication-candidate.json',{'passed':True,'newSources':len(new_sources),'totalSources':len(manifest['sources']),'oldCodeEvidencePreserved':len(old),'restorationPassed':True,'hardwareEntryIntegrationPassed':False})
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Athena NSS — 入口接续</title><style>body{font:16px/1.75 system-ui,sans-serif;color:#17302a;background:#f5f7f5;max-width:900px;margin:40px auto;padding:0 24px}main{background:white;padding:32px;border-radius:16px}h1{font-size:28px;line-height:1.3}table{width:100%;border-collapse:collapse}td,th{padding:12px;border-bottom:1px solid #dce5df;text-align:left}.ok{color:#18734d}.pending{color:#966313}a{color:#1e6b4a}</style><main><small>ATHENA NSS · '''+html.escape(now)+'''</small><h1>并发启动已现场验证<br><span class="ok">现网完整恢复</span></h1><p>五WAN高级QoS核心已由v42验收；最新版可复用入口仍未完成NSS闭环。</p><table><tr><th>事项</th><th>实际结果</th></tr><tr><td>同字节入口接续</td><td>原24模型 / 3406绑定复用</td></tr><tr><td>四个初始PID</td><td class="ok">约0.087秒齐备，四路首次同时payload约10.71秒</td></tr><tr><td>自然WAN去重</td><td class="pending">替换候选后TCP3第3候选首包超时，原上限拒绝</td></tr><tr><td>NSS checkpoint / stage / ECM</td><td>未开始</td></tr><tr><td>最终恢复</td><td class="ok">五WAN健康、ECM关闭全零、原物理队列一致、端点与自有客户端零残留</td></tr></table><p>没有操作CS2或Steam，没有扩大期限/PBR或永久开启NSS。候选首包取得失败根因未知，停止边界UDP未返不归因NSS。</p><p><a href="../athena-nss-mainline/docs/V46_ENTRY_CONTINUATION_2026-10-07.md">完整记录</a> · <a href="../athena-nss-mainline/docs/STATE.md">当前STATE</a></p></main></html>'''
with (w/'outputs/nss46-entry-report.html').open('x',encoding='utf8') as f:f.write(page)
print(dump({'passed':True,'sourceHashes':len(manifest['sources']),'newSources':len(new_sources),'oldCodeEvidencePreserved':len(old),'concurrentStartupActuallyExecuted':True,'hardwareEntryIntegrationPassed':False,'restorationPassed':True}))
