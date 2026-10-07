"""Freeze repaired transport, the successful reusable entry and bounded resident refusals."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import copy, hashlib, html, json, re, subprocess

w=Path(__file__).resolve().parents[2];t=Path(__file__).resolve().parent;repo=w/'athena-nss-mainline'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda b:hashlib.sha256(b).hexdigest()
dump=lambda v:json.dumps(v,ensure_ascii=False,indent=2)+'\n'
git=lambda *a:subprocess.check_output(['git','-C',str(repo),*a])
def fresh(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8') as f:f.write(dump(v))
base='c6fa792a6e10adc21be0d770400c4bb6e7332bc1'
assert git('rev-parse','HEAD').decode().strip()==base and not git('status','--porcelain')
manifest=read(repo/'source-manifest.json');prefix=copy.deepcopy(manifest['sources']);assert len(prefix)==5010
old={n.decode():sha((repo/n.decode()).read_bytes()) for row in git('ls-tree','-r','-z',base,'--','code','evidence').split(b'\0') if row for _,n in [row.split(b'\t',1)]}
roots=['v48-ssh-phase','v49-handshake-diagnosis','v50-compact-handshake','v51-compact-entry','v52-udp-preflight','v53-control-framing','v54-owned-control','v55-resident-trial','v56-control-bootstrap','v57-resident-bootstrap','v58-resident-timeout']
runtime_map={'v51':'work/v51-run-20261007121048-dc58268e','v52':'work/v52-run-20261007123445-10660faa','v54':'work/v54-run-20261007124710-037185ff','v55':'work/v55-run-20261007130044-e8a5e1d6','v57':'work/v57-run-20261007132518-89cdd084','v58':'work/v58-run-20261007133308-5456c702'}
entries={'v51':'v51-compact-entry','v52':'v52-udp-preflight','v54':'v54-owned-control','v55':'v55-resident-trial','v57':'v57-resident-bootstrap','v58':'v58-resident-timeout'}
sources=set();models={};inputs={};results={};runtime_hashes={}
def keep(role,path):
 data=path.read_bytes();inputs[role]={'path':path,'sha256':sha(data)}
def validated(group):
 for rel,h in group.items():
  assert sha((w/rel).read_bytes())==h,rel;sources.add(rel)
for name in roots:
 r=w/'work'/name
 for p in r.iterdir():
  if p.is_file() and p.suffix in ['.mjs','.py','.ps1'] and 'private' not in p.name:sources.add(p.relative_to(w).as_posix())
 for dn in ['failed-model-v1','model-source-v1','model-source-v2','model-source-v3']:
  d=r/dn
  if d.exists():
   for p in d.iterdir():
    if p.is_file() and p.suffix in ['.mjs','.py','.ps1'] and 'private' not in p.name:sources.add(p.relative_to(w).as_posix())
 pointer=r/'entry-model-latest-private.json'
 if pointer.exists():
  m=read(w/read(pointer)['receipt']);assert m['passed'];validated(m['sourceHashes']);keep(name+'-model',w/read(pointer)['receipt'])
  models[name]={'passed':True,'checks':len(m['checks']),'sourceBindings':m['sourceBindings'],'sourceHashes':m['sourceHashes'],'hardwareExecuted':False}
for version,rel in runtime_map.items():
 r=w/rel;e=w/'work'/entries[version];a=read(e/'active-private.json');assert a['runtimeRoot']==rel and a['state']=='RESTORED' and a['restorationPassed'] and not (e/'active-lock').exists()
 q=read(r/'entry-qualified.json');assert q['passed'] and q['inheritedBindings']==3354;validated(q['sourceManifest']);runtime_hashes[version]=q['sourceManifest']
 p=w/read(r/'pilot-reference-private.json')['directory'];c=w/read(r/'closure-pointer.json')['directory']
 driver=read(p/'driver-private.json');audit=json.loads((c/'final-audit-stdout-private.txt').read_text().strip().splitlines()[-1]);physical=read(c/'physical-final.json')
 assert audit['passed'] and audit['queryAge']<6 and audit['ecmClosedAndZero'] and audit['protectedConfigurationUnchanged'] and audit['allFiveHealthyWanBaseline']
 assert physical['passed'] and physical['defaultQueueOptionsAndHandlesExact']
 keep(version+'-entry-original',r/'entry-result-private.json');keep(version+'-active-final',e/'active-private.json');keep(version+'-driver',p/'driver-private.json');keep(version+'-audit',c/'final-audit-stdout-private.txt');keep(version+'-physical',c/'physical-final-raw-private.json')
 binding=read(p/'actual-entry-bindings.json');assert len(binding)==q['actualBindings']
 for f,h in binding.items():assert sha((w/f).read_bytes())==h and (p/'frozen'/f).read_bytes()==(w/f).read_bytes(),f
 keep(version+'-bindings',p/'actual-entry-bindings.json')
 row={'state':'RESTORED','restorationPassed':True,'hardwareCompleted':a['hardwareCompleted'],'actualBindings':q['actualBindings'],'driverCodes':[x['code'] for x in driver],'finalFullAudit':audit,'physicalQueues':physical,'lockRemoved':True}
 lp=r/'load-latest-private.json'
 if lp.exists():
  load=w/read(lp)['dir'];client=read(load/'result-private.json');clients=read(c/'client-closure.json');assert clients['passed'] and clients['ownedTestProcessesRemaining']==0 and not clients['clientDeadlineReset']
  endpoint=load/'endpoint-retry-closure.json'
  if not endpoint.exists():
   if version=='v55':endpoint=w/'work/v56-control-bootstrap/endpoint-closure.json'
   else:
    raw=read(r/'entry-endpoint-readonly-recheck-raw-private.json');assert raw['code']==0;endpoint=r/'entry-endpoint-readonly-recheck-raw-private.json'
  ev=read(endpoint);ev=json.loads(ev['stdout']) if 'stdout' in ev else ev;assert ev['passed'] and ev['ownedRulesRemaining']==0 and ev['baselineRestored'] and ev['exactOwnedEndpointClosed']
  row['endpointClosure']=ev;row['clientClosure']={k:clients[k] for k in ['passed','ownedTestProcessesRemaining','clientDeadlineReset']};row['fixture']={k:client[k] for k in ['seconds','tcpBytes','udpSent','udpReceived','errors']}
  row['fixture']['tcpChildren']=[{k:x[k] for k in ['slot','attempt','connected','bytes']} for x in client['tcpChildren']]
  for role,path in [('fixture-result',load/'result-private.json'),('fixture-timeline',load/'load-samples-private.jsonl'),('endpoint',endpoint),('client-closure',c/'client-closure.json'),('last-classification',r/'controlled-candidates-private.json')]:
   if path.exists():keep(version+'-'+role,path)
  if (load/'matching-private.json').exists():
   match=read(load/'matching-private.json');row['matchingReads']=len(match);row['lastMatchingSummary']=json.loads(match[-1]['stdout']) if match[-1]['code']==0 else None
   row['lastAcquisition']=match[-1].get('acquisition');keep(version+'-matching',load/'matching-private.json')
 else:
  assert version=='v52';endpoint=r/'load-20261007123502-a21991933ce1a5b2/unacknowledged-launch-audit.json';ev=read(endpoint);assert ev['passed'];row.update(endpointRecoveryFollowup=ev,noClientLaunched=True,originalPrematureWrapperInferenceRetained=True);keep(version+'-late-launch-audit',endpoint)
 case=p/'case-reference-private.json'
 if case.exists():
  d=w/read(case)['dir'];record=read(d/'last-record-private.json');result=read(d/'result.json');assert result['passed'] and result['automaticLifecycleEpochCompleted']
  phase=record['phases'];assert len(phase)==1 and phase[0]['name']=='B';samples=[x for x in record['samples'] if x['phase']=='B'];assert samples and all(x['counts']['ecm_nss_ipv4/accelerated_count']==5 for x in samples)
  flags=['moduleUnloaded','qosModuleUnloaded','qosRestored','wanRestored','dualPhysicalQueuesRestored','stateNodeRemoved','automaticPacketTagsCompleted','firmwareZeroAfterRetirement']
  assert all(record[k] is True for k in flags)
  continuity=read(p/'continuity-private.json');wans={slot:f['wan'] for slot,f in continuity['selected'].items()};assert set(wans.values())=={1,2,3,4,5}
  row['hardware']={'passed':True,'phase':{k:phase[0][k] for k in ['name','seconds','sampleCount','requestedSeconds','completed']},'renewals':len(record['renewals']),'allBSamplesEcmFive':True,'selectedWanBySlot':wans,'originalClassificationAndQosPolicyKept':True,'restorationFlags':{k:record[k] for k in flags},'softwareComparison':False,'humanGameAcceptance':False,'newCpuAcceptance':False,'permanentNssDeployment':False}
  for role,path in [('nss-result',d/'result.json'),('nss-record',d/'last-record-private.json'),('continuity',p/'continuity-private.json'),('owner',p/'detached-owner-reference-private.json')]:keep(version+'-'+role,path)
 else:assert not (p/'detached-owner-reference-private.json').exists();row['nssCheckpointOrStageStarted']=False
 results[version]=row
assert results['v54']['hardwareCompleted'] and 60<=results['v54']['hardware']['phase']['seconds']<=61.5 and results['v54']['hardware']['renewals']==20
assert all(not results[x]['hardwareCompleted'] for x in ['v51','v52','v55','v57','v58'])
assert results['v58']['fixture']['errors']==[] and results['v58']['lastMatchingSummary']['tcpBulk']==3 and results['v58']['lastMatchingSummary']['udpRt']==1
assert sorted(x['wan'] for x in results['v58']['lastAcquisition']['retained'])==[1,2,4,5]
assert read(w/'work/v55-run-20261007130044-e8a5e1d6/entry-result-private.json')['state']=='RESTORATION_UNCONFIRMED'
assert read(w/'work/v56-control-bootstrap/ledger-repair.json')['originalResultRetained']
diagnostics={}
for name in ['v49-handshake-diagnosis','v50-compact-handshake','v53-control-framing','v56-control-bootstrap']:
 p=w/'work'/name/'summary.json';assert p.exists();diagnostics[name]=read(p);keep(name+'-summary',p)
boot=diagnostics['v56-control-bootstrap'];assert boot['passed'] and any(x['bootstrap'] and x['wan']==5 and x['passed'] and x['ctMatched'] and x['localSocketMatched'] for x in boot['probes'])
route_files=sorted(t.glob('route-check-*.json'));route=[read(p) for p in route_files if 'failure' not in p.name];assert len(route)==1 and route[0]['passed'] and route[0]['nodeCases']==11 and route[0]['ramCases']==9
keep('v58-route-check',next(p for p in route_files if 'failure' not in p.name))
for r in roots:
 for p in (w/'work'/r).glob('*failure*private.json'):keep(r+'-'+p.stem,p)
sealed=t/'sealed-inputs-private';sealed.mkdir();input_hashes={}
for role,value in inputs.items():
 data=value['path'].read_bytes();assert sha(data)==value['sha256'];target=sealed/(role+value['path'].suffix)
 with target.open('xb') as f:f.write(data)
 input_hashes[role]=value['sha256']
fresh(sealed/'manifest-private.json',input_hashes)
indexed={x['workspaceSource']:x for x in prefix};new_sources={};attrs=[]
for rel in sorted(sources):
 data=(w/rel).read_bytes();digest=sha(data)
 if rel in indexed:assert digest==indexed[rel]['sha256'];continue
 assert Path(rel).suffix in ['.lua','.mjs','.py','.ps1','.json','.c'] and not any(x in Path(rel).name for x in ['private','credential','connect-router'])
 dest=repo/'code'/rel;dest.parent.mkdir(parents=True,exist_ok=True)
 with dest.open('xb') as f:f.write(data)
 new_sources[rel]=digest;manifest['sources'].append({'path':'code/'+rel,'workspaceSource':rel,'sha256':digest,'bytes':len(data),'role':'reusable-five-wan-entry-repair-and-bounded-resident-prerequisite-results'})
 opts=[]
 if b'\r\n' in data:opts.append('cr-at-eol')
 if re.search(rb'[ \t]+\r?$',data,re.M):opts.append('-blank-at-eol')
 if re.search(rb'(?:\r?\n){2,}$',data):opts.append('-blank-at-eof')
 if opts:attrs.append('/code/'+rel+' whitespace='+','.join(opts))
if attrs:
 p=repo/'.gitattributes';p.write_text(p.read_text()+'\n# Exact repaired-entry and retained failed model bytes.\n'+'\n'.join(attrs)+'\n',encoding='utf8')
evidence={'passed':True,'reusableEntryHardwareCompleted':True,'residentNinetySecondHardwareCompleted':False,'residentTrialStartedAsFixtureOnly':True,'latestState':'RESTORED','models':models,'runtimeResults':results,'controlDiagnostics':diagnostics,'routeAcquisitionVerification':{k:route[0][k] for k in ['passed','nodeCases','ramCases','fullLuaSyntaxPassed','routerWrites','trafficGenerated']},'originalV55UnconfirmedResultRetained':True,'v55EndpointRecoveryFollowupPassed':True,'sourceFreshnessSeconds':6,'clientSeconds':180,'ownerSeconds':180,'nativeMaximumSeconds':120,'naturalAcquisitionSeconds':30,'firstPayloadSeconds':8,'slotMaximumAttempts':8,'mtuRootCauseProved':False,'permanentNssDeployment':False,'cs2OrSteamOperated':False,'newCpuAcceptance':False,'heartbeatStillPaused':True,'classifierNss68Unchanged':True,'sourceHashesByRuntime':runtime_hashes,'inputSha256ByRole':input_hashes}
fresh(repo/'evidence/v58-entry-repair-resident.json',evidence)
fresh(repo/'evidence/v58-source-proof.json',{'passed':True,'historicPrefixSources':5010,'newSources':len(new_sources),'sourceHashes':new_sources,'oldCodeEvidenceUnmodified':True,'oldCodeEvidenceBlobsPreserved':len(old),'actualRuntimeBindingsFrozenExact':{k:v['actualBindings'] for k,v in results.items()},'privateInputsSealed':len(input_hashes),'inputSha256ByRole':input_hashes,'exactPathAttributes':attrs})
manifest['generatedAt']=datetime.now(timezone.utc).isoformat();manifest['lastEntryRepairExport']='V54_ENTRY_COMPLETE_V58_RESIDENT_PREREQUISITE_REFUSED_RESTORED';assert manifest['sources'][:5010]==prefix
(repo/'source-manifest.json').write_text(dump(manifest),encoding='utf8')
now=datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M');h=results['v54']['hardware'];a=results['v58']['finalFullAudit']
body=f'''# 可复用五 WAN 入口完成；常驻候选尚未进入 NSS

北京时间{now}。用户要求遇到程序错误继续修复，入口完成后尝试可撤销常驻 NSS 的授权保持。继续使用四条自有 TCP 和模拟 UDP，不操作 CS2／Steam。

## 已完成的入口闭环

v54 实际入口以3421绑定进入五 WAN NSS：四 TCP BULK走WAN1／2／4／5，UDP RT走WAN3；B {h['phase']['seconds']:.2f}秒、121采样、全部ECM5、20续租。新 checkpoint 下载/SHA/gzip与原独立恢复写前通过，七份 Lua 为v42原字节。进入、租约、退出、完整恢复均通过，**可复用入口硬件闭环已完成**。这替代旧STATE“入口未通过”的当前结论；历史失败原字节保留。

TCP载荷取得采用仅限自有SSH子进程的紧凑算法offer。v49实测IPQoS=none在WAN5仍失败，未采用；v50小探针未覆盖WAN5，单独不构成WAN5证明。v51实际三个WAN5 TCP收到载荷并持续传输，四首包约2.59—2.69秒。v51软件UDP1928发／0返，未进入NSS；后来增加三个实际载体同tuple的UDP20包预检，v54各20／20通过。

修复了端点写请求未获确认时丢失清理指针的问题：在systemd／FW写前保存启动意图，再以原250秒服务／180秒FW独立期限和精确单位／端口／规则基线判断恢复。v52原wrapper过早推断无端点的结果保留；随后独立只读精确服务／端口缺席证明通过。

## 控制传输与候选取得修复

控制SSH改用短启动命令，将原dispatcher的确切解压字节和后续帧放入同一256字节／20ms串行stdin队列；认证、全局SSH、8秒连接与20秒命令限制不变。v56实际本地socket原端口到CT匹配，WAN5短启动渠道16KiB输入完整通过；同批旧渠道也通过，**未证明MTU根因或排除所有偶发SSH问题**。v53以远端NAT端口匹配本地CT的诊断未取得WAN归属，不把它当WAN5证明。

自然取得现在从已核实PID／socket的实际CT读取WAN，提前轮换重复WAN；Linux PBR／mark／NAT不写，路由归属不授予BULK资格。最终仍需要四实际BULK＋已准入RT。复用路由器控制连接，CIM身份与源帧每次重新读取；15秒单次读取、30秒自然轮换、最多8候选、8秒首包保持。v57小数timeout导致Node写前拒绝，v58已取整修复；修正版9模型／3424绑定、11归属模型／9 RAM和完整Lua语法通过。最初Lua字符串转义、RAM测试长括号和model指针EEXIST失败与输入均保留，未将其标为硬件证明。

## 本次常驻候选的实际范围和结果

候选只将固定B从60改为90秒，native hard由90改为原已存在的最大120秒；source6／owner180／client180／guard210／server250和字节上限不变。六份其它Lua、native、分类／QoS／失效撤销不变，**不能称七Lua全字节相同**。这是一代有退出的router detached controller候选，尚无长期、永久或自动连续新代部署。

v55因缺WAN2，在NSS checkpoint／stage前退出；端点控制与首只读清理超时原失败保留，v56只读精确规则0／FW基线／单位端口关闭证明补齐，原UNCONFIRMED结果不改，仅可变ledger修正RESTORED。

v57因timeout参数类型错误在NSS前退出；修复后v58实际连接已走TCP WAN2／1／4／5和UDP WAN3，但34次分类读最后只有3BULK＋1RT，第四TCP不在准入投影中。全fixture客户端错误0。该缺失不能当作CT退出或真实BE改类证据，也未证明是NSS／firmware故障。原窗口结束，未开始NSS checkpoint／owner／stage／ECM，**90秒常驻硬件验收未通过**。不强制改类／tag或放宽期限，也不为配齐资格无条件重开fixture。

## 最后恢复和下一步

所有本轮实际会话均最终RESTORED／锁解除。最新完整audit source{a['queryAge']:.2f}秒／selectors{a['selectors']}，五WAN健康、保护配置不变、ECM关闭全零、两物理原mq＋四fq_codel全部选项／handle一致，端点规则0／基线和客户端残留0。NSS68分类器原配置保持，heartbeat暂停。

当前可用成果是显式一次的五WAN60秒入口闭环；常驻控制器仍是未进入NSS的90秒候选。保留的问题是自然候选／分类投影取得、偶发控制SSH、历史v41进入窗计数差异、普通应用factory未验及长期／永久常驻。后续只依据实际缺失分类的完整同query证据修复或接入常驻控制，不重复五WAN核心、CPU或真人游戏验收。

证据：[入口与候选结果](../evidence/v58-entry-repair-resident.json)、[源码与保留证明](../evidence/v58-source-proof.json)、[入口用法](BOUNDED_MULTIWAN_ENTRY.md)。
'''
doc=repo/'docs/ENTRY_REPAIR_RESIDENT_2026-10-07.md'
with doc.open('x',encoding='utf8') as f:f.write(body)
lead=f'''# 最新状态：五 WAN 入口闭环完成；常驻候选已修复程序错误，资格不足退出并恢复

更新：北京时间{now}。v54真实可复用入口3421绑定，四TCP BULK WAN1／2／4／5＋UDP RT WAN3，NSS B60.01秒／121采样／ECM5／20续租与完整恢复通过。旧入口未通过的记录为历史，当前入口闭环已完成。

仅自有SSH紧凑offer／控制短启动传输、写前启动意图和精确清理、提前实际CT自然WAN取得与整数timeout已接续修复。v58修正版9模型／3424绑定、11归属模型／9RAM／完整Lua语法通过；现网NSS68分类器不改。认证／PBR／mark／NAT／学校策略、source6／owner180／client180与全部原字节上限保持。

90秒常驻候选只改fast固定窗口与native原最大120秒，六份其它Lua／native／分类／QoS不变。v55自然配对未齐、v57timeout类型拒绝、v58实际五WAN连接已齐但仅3BULK＋1RT，均在NSS checkpoint／stage前退出；90秒常驻硬件尚未通过，没有永久／长期NSS。缺失投影不当真实改类或CT退出，不能硬放行；不无条件重开fixture。

原失败与v55 UNCONFIRMED结果保持，后续精确端点只读证明已补齐。最后完整source{a['queryAge']:.2f}／selectors{a['selectors']}，五WAN健康／ECM关闭全零／保护配置不变，两物理原队列全部选项与handle、端点基线与自有进程0通过，RESTORED／无锁。无CS2／Steam、新CPU或新增下载；heartbeat仍暂停。用户常驻授权持续有效，后续只修有完整同query证据支持的问题，再完成常驻控制器的有界试用。

详情：[本次接续](ENTRY_REPAIR_RESIDENT_2026-10-07.md)。

## 以下为保留的历史状态

'''
for name in ['docs/STATE.md','docs/PLAN.md','docs/EXPERIMENT_LOG.md','AGENTS.md']:
 p=repo/name;text=lead.replace('(ENTRY_REPAIR_RESIDENT_2026-10-07.md)','(docs/ENTRY_REPAIR_RESIDENT_2026-10-07.md)') if name=='AGENTS.md' else lead;p.write_text(text+p.read_text(encoding='utf8'),encoding='utf8')
for name,text in {'README.md':'# Athena NSS 多WAN／高级QoS受控原型\n\nv54可复用五WAN入口60秒硬件闭环完成，现网完整恢复。常驻90秒候选尚未进入NSS；当前不是永久NSS部署。具体事实与限制见[最新记录](docs/ENTRY_REPAIR_RESIDENT_2026-10-07.md)、[STATE](docs/STATE.md)。\n',
 'docs/BOUNDED_MULTIWAN_ENTRY.md':'# 当前入口与常驻候选\n\n已通过的可复用入口是`work/v54-owned-control/entry.mjs`：显式inspect／status／run／stop，一代60秒／五WAN／完整恢复。最新修正版`work/v58-resident-timeout/entry.mjs`是90秒常驻候选，实际五WAN已齐但第四TCP缺BULK资格，在NSS前拒绝，硬件未验。两者均需新namespace和checkpoint／独立恢复；勿把入口命令列表当作连续重试指令。见[本次记录](ENTRY_REPAIR_RESIDENT_2026-10-07.md)。\n'}.items():
 p=repo/name;p.write_text(text+'\n## 以下为历史状态\n\n'+p.read_text(encoding='utf8'),encoding='utf8')
checker=repo/'tools/check_repository.py';text=checker.read_text(encoding='utf8');needle="print(json.dumps({'passed':True,'filesChecked':count";assert text.count(needle)==1
checks='''if (root/'evidence/v58-entry-repair-resident.json').exists():
 a=json.loads((root/'evidence/v58-entry-repair-resident.json').read_text(encoding='utf8'));s=json.loads((root/'evidence/v58-source-proof.json').read_text(encoding='utf8'))
 assert a['passed'] and a['reusableEntryHardwareCompleted'] and not a['residentNinetySecondHardwareCompleted'] and a['latestState']=='RESTORED'
 assert manifest['lastEntryRepairExport']=='V54_ENTRY_COMPLETE_V58_RESIDENT_PREREQUISITE_REFUSED_RESTORED'
 h=a['runtimeResults']['v54']['hardware'];assert h['passed'] and 60<=h['phase']['seconds']<=61.5 and h['phase']['sampleCount']==121 and h['renewals']==20 and h['allBSamplesEcmFive'] and set(h['selectedWanBySlot'].values())=={1,2,3,4,5}
 for v,r in a['runtimeResults'].items():
  assert r['state']=='RESTORED' and r['restorationPassed'] and r['lockRemoved'];q=r['finalFullAudit'];assert q['passed'] and q['queryAge']<6 and q['ecmClosedAndZero'] and q['allFiveHealthyWanBaseline'] and q['protectedConfigurationUnchanged'] and r['physicalQueues']['defaultQueueOptionsAndHandlesExact']
  if v!='v54':assert not r['hardwareCompleted'] and not r['nssCheckpointOrStageStarted']
  if 'endpointClosure' in r:assert r['endpointClosure']['passed'] and r['endpointClosure']['ownedRulesRemaining']==0 and r['endpointClosure']['baselineRestored'] and r['endpointClosure']['exactOwnedEndpointClosed'] and r['clientClosure']['ownedTestProcessesRemaining']==0
 r=a['runtimeResults']['v58'];assert r['actualBindings']==3424 and r['matchingReads']==34 and r['fixture']['errors']==[] and r['lastMatchingSummary']['tcpBulk']==3 and r['lastMatchingSummary']['udpRt']==1
 assert sorted(x['wan'] for x in r['lastAcquisition']['retained'])==[1,2,4,5]
 assert a['models']['v58-resident-timeout']['checks']==9 and a['routeAcquisitionVerification']['nodeCases']==11 and a['routeAcquisitionVerification']['ramCases']==9
 assert a['originalV55UnconfirmedResultRetained'] and a['v55EndpointRecoveryFollowupPassed'] and a['sourceFreshnessSeconds']==6 and a['nativeMaximumSeconds']==120 and a['ownerSeconds']==180 and a['clientSeconds']==180 and a['naturalAcquisitionSeconds']==30 and a['firstPayloadSeconds']==8 and a['slotMaximumAttempts']==8
 assert not any(a[k] for k in ['mtuRootCauseProved','permanentNssDeployment','cs2OrSteamOperated','newCpuAcceptance'])
 assert s['passed'] and s['historicPrefixSources']==5010 and s['newSources']==len(s['sourceHashes']) and s['oldCodeEvidenceUnmodified']
 groups=[s['sourceHashes'],*a['sourceHashesByRuntime'].values(),*(m['sourceHashes'] for m in a['models'].values())]
 for group in groups:
  for rel,digest in group.items():assert hashlib.sha256((root/'code'/rel).read_bytes()).hexdigest()==digest,rel
'''
checker.write_text(text.replace(needle,checks+needle),encoding='utf8')
for name,h0 in old.items():assert sha((repo/name).read_bytes())==h0,name
fresh(t/'publication-candidate.json',{'passed':True,'baseCommit':base,'newSources':len(new_sources),'totalSources':len(manifest['sources']),'oldCodeEvidenceBlobsPreserved':len(old),'reusableEntryHardwareCompleted':True,'residentNinetySecondHardwareCompleted':False,'restorationPassed':True})
page=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Athena NSS — 入口修复与常驻候选</title><style>body{{font:16px/1.8 system-ui,sans-serif;background:#f4f7f5;color:#183c2e;max-width:920px;margin:40px auto;padding:0 24px}}main{{background:white;padding:34px;border-radius:18px}}h1{{font-size:30px;line-height:1.4}}table{{border-collapse:collapse;width:100%}}th,td{{text-align:left;padding:12px;border-bottom:1px solid #dbe7df}}.ok{{color:#167a4e}}.wait{{color:#956017}}a{{color:#14633e}}</style><main><small>ATHENA NSS · {html.escape(now)}</small><h1>五 WAN 入口闭环已完成<br><span class="wait">常驻候选尚未进入 NSS</span></h1><table><tr><th>范围</th><th>实际结果</th></tr><tr><td>可复用入口 v54</td><td class="ok">4 TCP BULK＋模拟 UDP RT／五WAN／60.01秒／ECM5／20续租／完整恢复</td></tr><tr><td>已修程序错误</td><td>SSH offer和控制启动传输、写前清理指针、实际CT提前自然轮换、整数timeout</td></tr><tr><td>常驻候选 v58</td><td class="wait">五WAN连接已齐；分类仅3BULK＋1RT，在NSS checkpoint／stage前拒绝</td></tr><tr><td>最终现网</td><td class="ok">五WAN健康、ECM关闭全零、原物理队列／FW基线／自有进程0，完整恢复</td></tr></table><p>90秒候选、长期与永久NSS仍未验收。历史CPU与v42高级QoS证据复用；本轮没有CS2／Steam或新增下载。所有原失败保留，没有硬改分类或放宽期限。</p><p><a href="../athena-nss-mainline/docs/ENTRY_REPAIR_RESIDENT_2026-10-07.md">本次完整记录</a> · <a href="../athena-nss-mainline/docs/STATE.md">当前STATE</a></p></main></html>'''
with (w/'outputs/nss58-resident-report.html').open('x',encoding='utf8') as f:f.write(page)
print(dump({'passed':True,'newSources':len(new_sources),'totalSources':len(manifest['sources']),'oldCodeEvidenceBlobsPreserved':len(old),'reusableEntryHardwareCompleted':True,'residentNinetySecondHardwareCompleted':False,'report':'outputs/nss58-resident-report.html'}))
