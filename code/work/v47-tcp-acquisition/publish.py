"""Publish allowlisted v47 diagnosis and a single unchanged entry refusal/restoration."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import copy, hashlib, html, json, re, subprocess

w=Path(__file__).resolve().parents[2];t=Path(__file__).resolve().parent;repo=w/'athena-nss-mainline'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda b:hashlib.sha256(b).hexdigest()
dump=lambda x:json.dumps(x,ensure_ascii=False,indent=2)+'\n'
git=lambda *args:subprocess.check_output(['git','-C',str(repo),*args])
def new(p,x):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8') as f:f.write(dump(x))

base='98b5508779d4366dd8140db9b859d2e44954a0e9'
assert git('rev-parse','HEAD').decode().strip()==base and not git('status','--porcelain')
manifest=read(repo/'source-manifest.json');prefix=copy.deepcopy(manifest['sources']);assert len(prefix)==4959
old={name.decode():sha((repo/name.decode()).read_bytes()) for row in git('ls-tree','-r','-z',base,'--','code','evidence').split(b'\0') if row for _,name in [row.split(b'\t')]}
entry=w/'work/v45-early-acquisition';active=read(entry/'active-private.json');actual=w/active['runtimeRoot']
assert active['runtimeRoot']=='work/v45-run-20261007111504-9473cb52'
assert active['state']=='RESTORED' and active['restorationPassed'] and not active['hardwareCompleted'] and not (entry/'active-lock').exists()
assert read(t/'entry-exit-private.json')['code']==1 and read(t/'entry-attempt-once-private.json')['singleAttempt']
pilot=w/read(actual/'pilot-reference-private.json')['directory'];load=w/read(actual/'load-latest-private.json')['dir'];closure=w/read(actual/'closure-pointer.json')['directory']
driver=read(pilot/'driver-private.json');assert [e['code'] for e in driver]==[0,0,0,1,0]
assert not (pilot/'case-reference-private.json').exists() and not (pilot/'detached-owner-reference-private.json').exists()
client=read(load/'result-private.json');assert client['errors']==['Owned SSH tcp3 acquisition refused: No first payload within 8 seconds']
assert next(x['attempt'] for x in client['tcpChildren'] if x['slot']=='tcp3')==4
audit=json.loads((closure/'final-audit-stdout-private.txt').read_text().strip().splitlines()[-1]);physical=read(closure/'physical-final.json');endpoint=read(load/'endpoint-retry-closure.json');clients=read(closure/'client-closure.json')
assert audit['passed'] and audit['queryAge']<6 and audit['ecmClosedAndZero'] and audit['protectedConfigurationUnchanged'] and audit['allFiveHealthyWanBaseline']
assert physical['passed'] and physical['defaultQueueOptionsAndHandlesExact']
assert endpoint['passed'] and endpoint['ownedRulesRemaining']==0 and endpoint['baselineRestored'] and endpoint['exactOwnedEndpointClosed']
assert clients['passed'] and clients['ownedTestProcessesRemaining']==0 and not clients['clientDeadlineReset']
model=read(w/read(entry/'entry-model-latest-private.json')['receipt']);assert model['passed'] and len(model['checks'])==24 and model['sourceBindings']==3406
for rel,h in model['sourceHashes'].items():assert sha((w/rel).read_bytes())==h
q=read(actual/'entry-qualified.json');assert q['passed'] and q['actualBindings']==3406 and q['inheritedBindings']==3354 and len(q['sourceManifest'])==52
assert q['dataPlaneByteExact'] and q['classificationAndQosPolicyUnchanged']
bindings=read(pilot/'actual-entry-bindings.json');assert len(bindings)==3406
for rel,h in bindings.items():assert sha((w/rel).read_bytes())==h and (pilot/'frozen'/rel).read_bytes()==(w/rel).read_bytes()
for name in ['fast-path.lua','classifier.lua','classified-tags.lua','module-stage-guardian.lua','qos-physical.lua','wan-scope.lua','tag-normalizer.lua']:
 assert (actual/name).read_bytes()==(w/'work/v42-counter-window'/name).read_bytes()
diag=read(t/'diagnostic-summary.json');unit=read(t/'unit-log-summary.json');frozen=read(t/'frozen-acquisition-analysis.json')
assert diag['passed'] and diag['journalRows']==0 and unit['passed'] and unit['journalRows']==20 and unit['identifiers']==['sshd-session']
assert unit['logTermCounts']['Accepted publickey']==8 and unit['logTermCounts']['preauth']==4
assert unit['logTermCounts']['MaxStartups']==unit['logTermCounts']['penalty']==0
matching=read(load/'matching-private.json');frame=read(actual/'controlled-candidates-private.json');assert len(frame['pairs'])==0 and len(matching)==13 and matching[-1]['code']==1
retained_wans=sorted({x['wan'] for e in matching for x in e.get('acquisition',{}).get('retained',[])})
assert retained_wans==[1,3,4]
assert any(x.get('event')=='boundedAcquisitionRetry' and x.get('slot')=='tcp2' and x.get('attempt')==1 for x in frozen['events'])
timeline=[json.loads(s) for s in (load/'load-samples-private.jsonl').read_text().splitlines()]
first=next(x for x in timeline if x.get('tcpConnected'))
first_pids={slot:next(x['elapsed'] for x in timeline if x.get('tcpChildren') and next((c.get('ownerPid') for c in x['tcpChildren'] if c['slot']==slot),None)) for slot in ['tcp','tcp2','tcp3','tcp4']}
raw_unit=read(t/'unit-log-raw-private.json');journal=json.loads(raw_unit['stdout'])['rows']
terms=['Accepted publickey','Connection reset','Connection closed','session opened','session closed','preauth']
log_events=[{'elapsedFromV46ClientStart':round(int(x['__REALTIME_TIMESTAMP'])/1e6-1791369044.307,3),
             'categories':[s for s in terms if s.lower() in x.get('MESSAGE','').lower()]} for x in journal]
input_paths={'attempt':t/'entry-attempt-once-private.json','endpoint-preflight':t/'entry-preflight-raw-private.json',
 'original-tag-query':t/'endpoint-ssh-log-raw-private.json','correct-unit-query':t/'unit-log-raw-private.json',
 'v46-local-analysis':t/'frozen-acquisition-analysis.json','driver':pilot/'driver-private.json','actual-bindings':pilot/'actual-entry-bindings.json',
 'entry-result':actual/'entry-result-private.json','fixture-result':load/'result-private.json','fixture-timeline':load/'load-samples-private.jsonl',
 'matching':load/'matching-private.json','last-classification':actual/'controlled-candidates-private.json','final-audit':closure/'final-audit-stdout-private.txt',
 'physical':closure/'physical-final-raw-private.json','endpoint-closure':load/'endpoint-retry-closure.json','client-closure':closure/'client-closure.json'}
sealed=t/'sealed-inputs-private';sealed.mkdir();input_hashes={}
for role,p in input_paths.items():
 data=p.read_bytes();target=sealed/(role+p.suffix)
 with target.open('xb') as f:f.write(data)
 assert target.read_bytes()==data;input_hashes[role]=sha(data)
new(sealed/'manifest-private.json',input_hashes)
sources=set(q['sourceManifest'])|{p.relative_to(w).as_posix() for p in t.glob('*.py')}
indexed={x['workspaceSource']:x for x in manifest['sources']};new_sources={}
for rel in sorted(sources):
 data=(w/rel).read_bytes()
 if rel in indexed:assert sha(data)==indexed[rel]['sha256'];continue
 p=repo/'code'/rel;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb') as f:f.write(data)
 new_sources[rel]=sha(data);manifest['sources'].append({'path':'code/'+rel,'workspaceSource':rel,'sha256':sha(data),'bytes':len(data),'role':'v47-bounded-existing-ssh-log-diagnosis-and-single-unchanged-entry-refusal'})
attrs=[]
for rel in new_sources:
 data=(w/rel).read_bytes();opts=[]
 if b'\r\n' in data:opts.append('cr-at-eol')
 if re.search(rb'[ \t]+\r?$',data,re.M):opts.append('-blank-at-eol')
 if re.search(rb'(?:\r?\n){2,}$',data):opts.append('-blank-at-eof')
 if opts:attrs.append('/code/'+rel+' whitespace='+','.join(opts))
if attrs:
 p=repo/'.gitattributes';p.write_text(p.read_text()+'\n# Exact fresh v47 runtime source bytes.\n'+'\n'.join(attrs)+'\n',encoding='utf8')
ev={'boundedHistoricalDiagnostic':True,'firstSshdTagQueryRows':0,'resolvedUsingSameWindowUnitQuery':True,
 'journalRows':20,'journalIdentifier':'sshd-session','acceptedPublickeyRows':8,'preauthClosureRows':4,
 'sshLimitOrPenaltyCausationProved':False,'preciseFailedChildToServerLogMappingProved':False,'rootCauseProved':False,
 'sanitizedHistoricalLogEvents':log_events,'clientHadNoFirstPayload':True,'historicalTcp2InitialTimeoutAlsoObserved':True,
 'firstAllPayloadActuallyIncludedTcp2Retry':True,'sameV45QualifiedSourcesReused':True,'modelChecksReused':24,
 'modelSourceHashes':model['sourceHashes'],'actualBindings':3406,'inheritedBindings':3354,'sevenLuaByteExactV42':True,'limits':model['limits'],
 'fixtureAttempts':1,'driverEventCodes':[0,0,0,1,0],'failureCategory':'ROTATED_TCP3_ATTEMPT4_ORIGINAL_EIGHT_SECOND_FIRST_PAYLOAD_REFUSAL',
 'matchingReads':13,'lastFiveWanPairs':0,'lastTcpChildren':[{k:c[k] for k in ['slot','attempt','connected']} for c in client['tcpChildren']],
 'retainedWanSet':retained_wans,'tcp3WanAtFailureUnknown':True,'firstFourPidsSeconds':max(first_pids.values()),'firstAllPayloadSeconds':first['elapsed'],
 'clientSeconds':client['seconds'],'tcpPayloadBytes':client['tcpBytes'],'wholeSoftwareFixtureUdp':{'sent':client['udpSent'],'returned':client['udpReceived'],'notNssMeasurements':True},
 'nssCheckpointStarted':False,'nssStageStarted':False,'ecmOpened':False,'hardwareEntryIntegrationPassed':False,
 'transportAcquisitionFailureObservedAgain':True,'stableUnderlyingCauseProved':False,'v42HardwareAcceptanceRetained':True,
 'originalLimitsKept':True,'cs2OrSteamOperated':False,'newCpuAcceptance':False,'permanentNssDeployment':False,
 'residentTrialAuthorizedAfterEntryClosure':True,'residentTrialStarted':False,'noFurtherFixtureOpened':True,'inputSha256ByRole':input_hashes}
new(repo/'evidence/v47-tcp-acquisition.json',ev)
rest={'passed':True,'finalFullAudit':audit,'physicalQueues':physical,'endpointClosure':endpoint,
 'clientClosure':{k:clients[k] for k in ['passed','ownedTestProcessesRemaining','clientDeadlineReset','guards']},
 'state':'RESTORED','lockReleasedAfterProof':True,'original180SecondFirewallGuardianNaturalExpiryWaited':True,
 'nssNeverOpened':True,'heartbeatStillPaused':True,'classifierNss68Unchanged':True}
new(repo/'evidence/v47-restoration.json',rest)
new(repo/'evidence/v47-source-proof.json',{'passed':True,'historicPrefixSources':4959,'newSources':len(new_sources),'sourceHashes':new_sources,
 'runtimeSourceHashes':q['sourceManifest'],'actualBindingsFrozenExact':3406,'oldCodeEvidenceBlobsPreserved':len(old),
 'oldCodeEvidenceUnmodified':True,'privateInputsSealed':len(input_hashes),'inputSha256ByRole':input_hashes,
 'originalV45EntryAndV46EvidenceUnchanged':True,'exactPathAttributes':attrs})
manifest['generatedAt']=datetime.now(timezone.utc).isoformat();manifest['lastTransportAcquisitionExport']='V47_AUTH_PHASE_DIAGNOSIS_BOUNDED_ENTRY_REFUSED_RESTORED'
assert manifest['sources'][:4959]==prefix;(repo/'source-manifest.json').write_text(dump(manifest),encoding='utf8')
now=datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
body=f'''# TCP 载荷取得有界定位与一次入口验收

北京时间{now}。当前 v45 入口原24模型／3406绑定复用，未改分类、QoS、七份 Lua、PBR、8秒首包、30秒自然取得窗口、重试或字节上限；不操作 CS2／Steam。

## 已冻结 v46 失败的定位

原四路首次同时收到 payload 的10.71秒包括 tcp2 首次8秒无首包后的原有重试；不是四次初始握手全通过。首个 `sshd` 日志标签查询返回0行，随后只读同一45秒窗口的 SSH unit，实际得到20行 `sshd-session` 日志，其中8次公钥接受、4次认证前关闭／重置。服务器时钟读回与 PC 之间约-0.13至+2.63秒。

这些日志支持将调查范围留在 SSH 载荷取得阶段；没有证明 MaxStartups／penalty、NSS／firmware／gate／lease 是原因，也没有完成失败子进程到每一条服务器日志的精确对应。根因仍未知，不改服务器 SSH 限额、认证策略或学校策略。

## 本次唯一入口验收

用户要求继续后，新的只读检查确认原入口 RESTORED／无锁、端点端口和单位0，再执行一次同字节入口。初始四个 PID 约{ev['firstFourPidsSeconds']:.3f}秒齐备，四路 payload 首次齐备约{first['elapsed']:.2f}秒。TCP 原自然取得保留 WAN1／3／4；tcp3 轮换至第4候选后8秒没有首包，按原限制退出，13次匹配读后五 WAN pair0。

客户端实际{client['seconds']:.2f}秒，TCP payload {client['tcpBytes']}字节，软件 fixture UDP {client['udpSent']}发／{client['udpReceived']}返。没有 NSS checkpoint、owner、stage、模块或 ECM；没有 B 窗，不将停止边界 UDP 未返当作 NSS 丢包。**SSH 首包取得拒绝再次出现，完整可复用入口未验收；NSS 五 WAN 核心历史验收保持。** 本次不继续重开 fixture。

## 实际恢复

等待原180秒 FW 独立守护自然到期后，精确端点关闭、规则0、canonical基线通过；自有客户端／独立210秒 guard退出、残留0。最终完整审核 source{audit['queryAge']:.2f}秒／selectors{audit['selectors']}，五 WAN 健康、保护配置不变、ECM关闭全零。两物理wan／lan4原mq＋四fq_codel全部选项／handle一致，RESTORED／锁解除。NSS68分类器不变，heartbeat保持暂停。

v42 的五流60.01秒／ECM5／20续租、2373RT全返、十tag／leaf／完整mark／NAT／affinity与恢复继续复用；DOWN18共享借用、UP60每WAN12硬上限、RT prio0／FQ-CoDel保持。当前已知限制是测试载荷的 SSH／自然WAN取得，不能把它写成已证明的 NSS 数据面故障或已解决的问题。

用户对“入口完成后尝试常驻 NSS”的授权保留；前置入口闭环尚未通过，本次没有启动常驻试用。后续只处理有证据支持的连接取得改动，不重复核心／CPU证明或为配齐WAN无条件循环。

证据：[有界定位与入口](../evidence/v47-tcp-acquisition.json)、[完整恢复](../evidence/v47-restoration.json)、[源码](../evidence/v47-source-proof.json)、[当前入口](BOUNDED_MULTIWAN_ENTRY.md)。
'''
with (repo/'docs/V47_TCP_ACQUISITION_2026-10-07.md').open('x',encoding='utf8') as f:f.write(body)
lead=f'''# 最新状态：载荷取得拒绝再次出现，现网完整恢复

更新时间：北京时间{now}。有界只读定位得到原失败窗20行sshd-session日志；认证前关闭／重置与客户端未收首包同时出现，精确归属及根因未证明，未发现可证明限额／penalty因果的记录。原sshd标签0行与同窗口unit查找均保留。

一次同字节v45入口沿用24模型／3406绑定，初始四路payload约{first['elapsed']:.2f}秒齐备，保留TCP WAN1／3／4；tcp3第4候选原8秒首包超时，客户端{client['seconds']:.2f}秒结束，13次匹配读／五WAN pair0，NSS checkpoint／stage／ECM前拒绝。没有放宽期限／重试，不继续重开fixture，完整入口仍未通过。

原FW180秒自然到期、端点关闭／规则0／基线、自有进程0与最终审核通过：source{audit['queryAge']:.2f}／selectors{audit['selectors']}，五WAN健康／配置不变／ECM关闭全零，两物理原mq＋四fq_codel全部选项／handle一致，RESTORED／无锁。v42五WAN与高级QoS已验收范围保持，NSS68分类器不变，无CS2／Steam／新CPU，heartbeat暂停。

入口完成后尝试常驻NSS的用户授权保留；当前尚未达到该前置条件。SSH载荷取得限制保留，不升级为已证明的NSS／固件故障。详情：[本次记录](V47_TCP_ACQUISITION_2026-10-07.md)。

## 以下为已保留的授权与历史状态

'''
for name in ['docs/STATE.md','docs/PLAN.md','docs/EXPERIMENT_LOG.md','AGENTS.md']:
 p=repo/name;head=lead if name!='AGENTS.md' else lead.replace('(V47_TCP_ACQUISITION_2026-10-07.md)','(docs/V47_TCP_ACQUISITION_2026-10-07.md)')
 p.write_text(head+p.read_text(encoding='utf8'),encoding='utf8')
for name,head in {'README.md':'# Athena NSS 多WAN／高级QoS受控原型\n\nv42五WAN核心功能验收保持。最新有界入口仍被SSH首包取得拒绝，本轮没有NSS写入，已完整恢复。用户已授权入口完成后尝试常驻，前置入口闭环尚未通过。见[最新记录](docs/V47_TCP_ACQUISITION_2026-10-07.md)、[STATE](docs/STATE.md)。\n',
 'docs/BOUNDED_MULTIWAN_ENTRY.md':'# 当前入口：v45原字节，完整闭环仍待通过\n\n最新一次仍用`work/v45-early-acquisition/entry.mjs`的24模型／3406绑定；tcp3第4候选8秒无首包，NSS准入前退出并完整恢复。inspect／status／run／stop保持，勿把命令列表当作连续重试指令。常驻授权保留，尚未启动试用。见[最新记录](V47_TCP_ACQUISITION_2026-10-07.md)。\n'}.items():
 p=repo/name;p.write_text(head+'\n## 以下为历史状态\n\n'+p.read_text(encoding='utf8'),encoding='utf8')
checker=repo/'tools/check_repository.py';text=checker.read_text(encoding='utf8');needle="print(json.dumps({'passed':True,'filesChecked':count";assert text.count(needle)==1
checks='''if (root/'evidence/v47-tcp-acquisition.json').exists():
 a=json.loads((root/'evidence/v47-tcp-acquisition.json').read_text(encoding='utf8'));r=json.loads((root/'evidence/v47-restoration.json').read_text(encoding='utf8'));s=json.loads((root/'evidence/v47-source-proof.json').read_text(encoding='utf8'))
 assert manifest['lastTransportAcquisitionExport']=='V47_AUTH_PHASE_DIAGNOSIS_BOUNDED_ENTRY_REFUSED_RESTORED'
 assert a['boundedHistoricalDiagnostic'] and a['firstSshdTagQueryRows']==0 and a['resolvedUsingSameWindowUnitQuery'] and a['journalRows']==20 and a['journalIdentifier']=='sshd-session' and a['acceptedPublickeyRows']==8 and a['preauthClosureRows']==4
 assert a['sameV45QualifiedSourcesReused'] and a['modelChecksReused']==24 and a['actualBindings']==3406 and a['inheritedBindings']==3354 and a['fixtureAttempts']==1 and a['driverEventCodes']==[0,0,0,1,0] and a['matchingReads']==13 and a['lastFiveWanPairs']==0
 assert a['transportAcquisitionFailureObservedAgain'] and a['originalLimitsKept'] and a['v42HardwareAcceptanceRetained'] and a['noFurtherFixtureOpened'] and a['residentTrialAuthorizedAfterEntryClosure']
 assert not any(a[k] for k in ['rootCauseProved','stableUnderlyingCauseProved','sshLimitOrPenaltyCausationProved','preciseFailedChildToServerLogMappingProved','nssCheckpointStarted','nssStageStarted','ecmOpened','hardwareEntryIntegrationPassed','cs2OrSteamOperated','newCpuAcceptance','permanentNssDeployment','residentTrialStarted'])
 q=r['finalFullAudit'];e=r['endpointClosure'];c=r['clientClosure'];assert r['passed'] and q['passed'] and q['queryAge']<6 and q['ecmClosedAndZero'] and q['allFiveHealthyWanBaseline'] and q['protectedConfigurationUnchanged'] and r['physicalQueues']['defaultQueueOptionsAndHandlesExact'] and e['passed'] and e['ownedRulesRemaining']==0 and e['baselineRestored'] and e['exactOwnedEndpointClosed'] and c['passed'] and c['ownedTestProcessesRemaining']==0 and not c['clientDeadlineReset']
 assert s['passed'] and s['historicPrefixSources']==4959 and s['newSources']==len(s['sourceHashes']) and s['actualBindingsFrozenExact']==3406 and s['oldCodeEvidenceUnmodified'] and s['originalV45EntryAndV46EvidenceUnchanged']
 for group in [s['sourceHashes'],s['runtimeSourceHashes'],a['modelSourceHashes']]:
  for rel,digest in group.items():assert hashlib.sha256((root/'code'/rel).read_bytes()).hexdigest()==digest,rel
'''
checker.write_text(text.replace(needle,checks+needle),encoding='utf8')
for name,h in old.items():assert sha((repo/name).read_bytes())==h,name
new(t/'publication-candidate.json',{'passed':True,'base':base,'newSources':len(new_sources),'totalSources':len(manifest['sources']),
 'oldCodeEvidencePreserved':len(old),'hardwareEntryIntegrationPassed':False,'restorationPassed':True,'noResidentTrialStarted':True})
page=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Athena NSS — TCP载荷取得</title><style>body{{font:16px/1.75 system-ui,sans-serif;color:#17302a;background:#f5f7f5;max-width:900px;margin:40px auto;padding:0 24px}}main{{background:white;padding:32px;border-radius:16px}}h1{{font-size:28px;line-height:1.3}}table{{width:100%;border-collapse:collapse}}td,th{{padding:12px;border-bottom:1px solid #dce5df;text-align:left}}.ok{{color:#18734d}}.pending{{color:#966313}}a{{color:#1e6b4a}}</style><main><small>ATHENA NSS · {html.escape(now)}</small><h1>入口仍被首包取得拒绝<br><span class="ok">现网完整恢复</span></h1><p>五WAN与高级QoS核心验收保持；常驻试用授权已保留，入口前置条件尚未通过。</p><table><tr><th>事项</th><th>实际结果</th></tr><tr><td>原失败有界定位</td><td>20行SSH日志，认证前关闭／重置；根因及精确子进程对应仍未知</td></tr><tr><td>本次唯一入口</td><td>原24模型／3406绑定；初始四路payload约{first['elapsed']:.2f}秒齐备</td></tr><tr><td>自然WAN取得</td><td class="pending">保留WAN1／3／4，TCP3第4候选8秒首包超时</td></tr><tr><td>NSS checkpoint／stage／ECM</td><td>未开始；没有NSS B窗</td></tr><tr><td>完整恢复</td><td class="ok">source{audit['queryAge']:.2f}秒，五WAN健康，物理原队列一致，端点／自有进程零残留</td></tr></table><p>本轮不再重开fixture。没有修改PBR、认证、限额或期限，没有操作CS2／Steam，没有启用常驻NSS。</p><p><a href="../athena-nss-mainline/docs/V47_TCP_ACQUISITION_2026-10-07.md">完整记录</a> · <a href="../athena-nss-mainline/docs/STATE.md">当前STATE</a></p></main></html>'''
with (w/'outputs/nss47-entry-report.html').open('x',encoding='utf8') as f:f.write(page)
print(dump({'passed':True,'newSources':len(new_sources),'totalSources':len(manifest['sources']),'oldCodeEvidencePreserved':len(old),
 'hardwareEntryIntegrationPassed':False,'restorationPassed':True,'report':'outputs/nss47-entry-report.html'}))
