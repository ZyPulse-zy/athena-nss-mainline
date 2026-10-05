"""Append actual NSS99-106 results without replacing any frozen evidence."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib,subprocess,shutil,importlib.util,html
w=Path(__file__).resolve().parents[2];repo=w/'athena-nss-mainline';r=w/'work/nss107'
spec=importlib.util.spec_from_file_location('collector',w/'work/nss101/collect-lifecycle.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
cases=['work/nss99/controlled-matched-aba-20261005144835-e1b4fbfa','work/nss100/controlled-matched-aba-20261005150041-809720c9','work/nss100/controlled-matched-aba-20261005152528-d529ea7f']
cases+=sorted(p.relative_to(w).as_posix()for p in (w/'work/nss105').glob('controlled-matched-aba-*')if(p/'last-record-private.json').exists())
trials=[m.stage(p)for p in cases]
for t in trials:
 s=load(w/t['caseLocalPath']/'last-record-private.json')
 if 'tagMeasurementEpoch'in s:
  e=s['tagMeasurementEpoch'];b=e['baselineCounters'];assert e['contract']=='absolute-raw-retained-zero-new-wrong-tag'and not e['nssAdmissionAllowed']
  t['startupEpoch']={**e,'baselineCounters':b,'rawCountersNeverReset':True,'startupUnexpectedIsNotNativeFlowMisclassificationProof':True,'onePacketStartupExceptionActuallyTriggered':b['tcp_post_down_unexpected']['packets']==1}
  t['measurementEpochCounters']={key:{k:{u:v[u]-b[k][u]for u in ['packets','bytes']}for k,v in c.items()}for key,c in t['softwareTagCounters'].items()if key!='startupTags'}
  for c in t['measurementEpochCounters'].values():
   assert all(c[k]['packets']==c[k]['bytes']==0 for k in c if k.endswith('_unexpected')or k=='udp_post_neighbor_nonzero')
  t['zeroNewWrongTagsConfirmed']=True
loads=[load(w/f'work/nss{n}/load-reference-private.json')['dir']for n in [100,101,103,106]]
loads.insert(0,load(w/'work/nss99/load-latest-private.json')['dir']);loads.insert(4,load(w/'work/nss105/load-reference-private.json')['dir'])
assert len(set(loads))==6;closures=[m.closure(p)for p in loads]
assert closures[1]['clientErrors']==['SSH: Keepalive timeout']
final=load(w/'work/nss68/nss107-final-20261005-health.json')
assert all(final[k]for k in ['passed','configurationMatches','originalFullLockedAudit','ecmStoppedAndZero','noActiveTransaction','noStaging','noExperimentState','noExperimentalModule'])
assert(final['workerPid'],final['guardianPid'])==(4859,17139)
bg=load(w/'work/nss101/background-before-pause-recovered-summary.json');after=load(w/'work/nss103/background-after-user-pause.json')
assert bg['interfaces']['lan4']['txMbps']>150 and after['interfaces']['lan4']['txMbps']<.1
assert not bg['originalRawObservationAvailable']
assert trials[2]['softwareTagCounters']['initialTags']['tcp_post_down_unexpected']=={'packets':1,'bytes':1500}
assert not trials[2]['ecmOpened']and not trials[2]['phases']
timing=load(w/'work/nss99/long-window-qualification.json');qos=load(w/'work/nss100/qos-native-qualification.json');epoch=load(w/'work/nss105/startup-epoch-qualification.json')
assert timing['passed']and len(timing['checks'])==8 and qos['passed']and len(qos['checks'])==7 and epoch['passed']and len(epoch['checks'])==18
entry=load(w/'work/nss105/entry-source-manifest.json');assert len(entry)==662
success=[t for t in trials if t['passed']and t['completeABA']];fresh=[t for t in trials if t['caseLocalPath'].startswith('work/nss105/')]
assert len(fresh)==1
new=fresh[0];newok=new['passed']and new['completeABA']
failures=[{'round':'NSS100','beforeRouterWrites':True,'reason':'SSH keepalive timeout; client identity absent','originalFailureRetained':True},{'round':'NSS103','beforeEcmOpening':True,'reason':'Initial TCP down unexpected 1 packet / 1500 bytes','originalFailureRetained':True},{'round':'NSS105','beforeRouterWrites':True,'reason':'Eight natural TCP candidates did not share UDP WAN','originalFailureRetained':True}]
for t in success:
 assert [p['acceleratedCounts']for p in t['metrics']['phases']]==[[0],[2],[0]]
 assert t['actualAcceleratedIdentity']['passed']and all(t['actualAcceleratedIdentity']['proof'][k]['upTag']==0 for k in ['tcp','udp'])
main={'round':'NSS107','observedAt':final['observedAt'],'roundsCovered':['NSS99','NSS100','NSS101','NSS103','NSS105','NSS106'],'stageCases':len(trials),'successfulFunctionalABA':len(success),'startupEpochActualPassed':newok,'newEntry':'work/nss105/controlled-session.mjs','newEntryInputs':662,'newCpuComparisonAccepted':False,'previousMatched32And48CpuEvidenceRetained':True,'rateAccuracyAccepted':False,'endToEndUdpQosAccepted':False,'humanCs2Acceptance':False,'highLoad300MbpsAcceptance':False,'permanentClassifierChanged':False,'nssPermanentlyEnabled':False,'oneAcceleratedTcpUdpPairAtATime':True,'secondWanSimultaneousAcceleration':False,'onlyLan4DownlinkQosProven':True,'acceleratedUplinkQosGuaranteed':False,'fullCakeReplacementAccepted':False,'originalFailureRecordsPreserved':True,'allEndpointClosures':6,'backgroundRawOverwriteExplicitlyDisclosed':True,'backgroundBeforePauseRecoveredFromActualToolSummary':True,'timingModelIsNotHardwareExpiryInjection':True,'upstreamSubmitted':False,'reportVerification':{'sourceValidated':True,'browserRendered':False}}
old=(repo/'evidence/current-runtime.json').read_bytes();assert load(repo/'evidence/current-runtime.json')['round']=='NSS98'
assert subprocess.check_output(['git','show','HEAD:evidence/current-runtime.json'],cwd=repo)==old
history=repo/'evidence/nss98-runtime.json';assert not history.exists();history.write_bytes(old)
manifestpath=repo/'source-manifest.json';manifest=load(manifestpath);assert len(manifest['sources'])==1110
prefix=sha(json.dumps(manifest['sources'],sort_keys=True,separators=(',',':')).encode())
allowed={99:['prepare-long.py','qualify-long.mjs','run.mjs','controlled-session.mjs','read-controlled.mjs','match-controlled.mjs','session-binding.mjs','payload.mjs','module-stage.mjs','fast-path.lua','module-stage-guardian.lua','analyze-long.py','calibrate-clock.mjs'],100:['prepare-rate.py','qualify-qos-native.mjs','run.mjs','controlled-session.mjs','read-controlled.mjs','match-controlled.mjs','session-binding.mjs','payload.mjs','module-stage.mjs','fast-path.lua','module-stage-guardian.lua','qos-physical.lua','analyze-long.py','calibrate-clock.mjs'],101:['retry-existing.mjs','collect-lifecycle.py','read-background-initial.mjs'],103:['run-existing.mjs'],105:['prepare-epoch.py','qualify-epoch.mjs','run.mjs','controlled-session.mjs','read-controlled.mjs','match-controlled.mjs','session-binding.mjs','payload.mjs','module-stage.mjs','fast-path.lua','analyze-long.py','calibrate-clock.mjs'],106:['retry-existing.mjs'],107:['save-evidence.py']}
hashes={}
for n,names in allowed.items():
 for name in names:
  p=w/f'work/nss{n}/{name}';rel=p.relative_to(w).as_posix();dst=repo/'code'/rel;assert not dst.exists();dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dst);h=sha(p.read_bytes());assert sha(dst.read_bytes())==h;hashes[rel]=h;manifest['sources'].append({'path':'code/'+rel,'workspaceSource':rel,'sha256':h,'bytes':p.stat().st_size,'role':'long-single-WAN-QoS-and-startup-epoch-evidence'})
manifest['generatedAt']=datetime.now(timezone.utc).isoformat();manifest['lastAppendExport']='NSS107';dump(manifestpath,manifest)
proof={'round':'NSS107','sources':len(hashes),'sourceHashes':hashes,'historicPrefixSources':1110,'historicPrefixCanonicalSha256':prefix,'privateOwnedHostBootstrapExcluded':True,'completePrivateSourceInputsRetained':True,'lostFirstBackgroundRawIsExplicitException':True,'notAdditionalProductionAdmission':True}
for name,value in {'source-proof':proof,'trials':trials,'endpoint-closure':closures,'prewrite-failures':failures,'background-before':bg,'background-after':after,'timing-qualification':timing,'qos30-qualification':qos,'startup-epoch-qualification':epoch,'final-audit':final,'mainline':main}.items():dump(repo/f'evidence/nss107-{name}.json',value)
runtime={'round':'NSS107','checkedAt':final['observedAt'],'deploymentReference':'work/nss68/deployment-latest.json','classifierConfigSha256':final['configSha256'],'workerPid':4859,'guardianPid':17139,'nssPermanentlyEnabled':False,'permanentClassifierChangedThisTurn':False,'qualifiedExperimentalEntry':'work/nss105/controlled-session.mjs','qualifiedExperimentalEntryBoundInputs':662,'startupEpochActualPassed':newok,'phaseSeconds':20,'fixedNativeSessionSeconds':27,'independentOwnerSeconds':100,'classifierMaximumLeaseSeconds':6,'successfulFunctionalABA':len(success),'realHumanGameAcceptance':False,'newCpuComparisonAccepted':False,'onlyLan4DownlinkQosProven':True,'audit':final,'historical98RuntimePreservedSha256':sha(old),'historical92RuntimePreservedSha256':sha((repo/'evidence/nss92-runtime.json').read_bytes()),'historical82RuntimePreservedSha256':sha((repo/'evidence/nss82-runtime.json').read_bytes())};dump(repo/'evidence/current-runtime.json',runtime)
when=datetime.fromisoformat(final['observedAt'].replace('Z','+00:00')).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
newtext=('新启动观测入口在单WAN完整20秒A/B/A2通过，后续错误tag零新增。'if newok else'新启动观测入口的现场失败已保留，未取得新的完整A/B/A2。')
details=''
if newok:
 mm=new['metrics'];ps=mm['phases'];details='新轮实际TCP '+ '/'.join(f"{p['whole']['clientTcpMbps']:.3f}"for p in ps)+'Mbps；UDP收到/发出 '+ ' → '.join(f"{p['whole']['udp']['received']}/{p['whole']['udp']['sent']}"for p in ps)+f"；续租{new['renewals']}次，bulk/RT drop "+'/'.join(str(mm['leafAcrossBNearbySnapshots'][k]['delta']['dropped'])for k in ['8f05:','8f06:'])+'。'
else:details='新轮拒绝原因：'+str(new['error']).split('\n')[0]+'。'
if newok:details+='本轮原始启动错误为零，1包启动例外仅目标RAM案例覆盖，尚未现场触发；RTT p95约238.08/240.69/237.75ms，squeeze全0，UDP仍约4%未返回。异步leaf含38字节overhead约28.12Mbps，不作精确30Mbps限速验收。'
summary=f'''更新：{when}，北京时间。最新NSS107，常驻仍NSS68；实验均撤销。

**每段20秒的单WAN工程观察已完成两轮；{newtext}**

见 [实测汇总](../evidence/nss107-mainline.json)、[所有stage](../evidence/nss107-trials.json)、[启动观测检查](../evidence/nss107-startup-epoch-qualification.json)、[端点关闭](../evidence/nss107-endpoint-closure.json)、[终态](../evidence/nss107-final-audit.json)。

- NSS99：40Mbps组、发送48，WAN2三段TCP34.417/36.069/34.872，7续租、ECM0/2/0，bulk新增363drop/RT0。UDP811/832、815/852、809/834；不是全部回包，不验收端到端QoS/精确限速或新CPU收益。
- NSS100首次客户端SSH约11秒keepalive超时，路由器写前拒绝；NSS101同入口一次重试。30组受LAN4其它流量260/308/320Mbps影响，TCP5.498/15.754/7.679，UDP833/867→23/955→2/714，squeeze45/101/130，RT leaf仍0drop。缺口在返回软件后继续，不归因NSS。用户随后暂停下载，LAN4只读降至0.039Mbps，路由器其它WAN仍约67Mbps。
- NSS103暂停后短测initial发现TCP-down错误1包1500B，在ECM前拒绝并完整恢复。forward writer与postrouting getter跨钩子发布可能捕获已越过writer的包，此为解释假设，没有内核/固件缺陷证明。
- NSS105将启动原始计数保留，建立仅用于观测的基线，允许原始启动边界至多这1个TCP-down/1500B；其它错误/neighbor拒绝，未来错误必须零新增、所有计数单调/完整policy和学习前双向正包保持。100ms软件等待包含在原1.2秒getter期限内；软件A20秒仍先于ECM。没有清空counter或CT，18目标RAM案例/完整语法通过。初次8个自然TCP未同WAN，在路由器写前停止；106同一662项入口一次重试。{newtext}{details}
- 当前期限：native固定27秒≤原30秒上限，真实分类租约最大6秒，独立owner100秒；每轮只一WAN一TCP一UDP。实际四个stage各checkpoint/SHA/gzip/控制连接外恢复，六端点FW180/客户端210秒关闭。最终4859/17139/config581b5d46…c791d7/source{final['queryAge']:.2f}，原完整审核通过，ECM关闭全零，无残留。
- 本轮没有永久NSS、常驻分类器更换、真人CS2、300Mbps验收或上行QoS。先前32Mbps三段66.41%与48Mbps B/A2约72.19% softirq收益保留；此轮只看拥塞和功能，不用不同吞吐计算收益。实际upTag仍0，仅LAN4下行；CAKE完整替代尚未成立。
- 背景观测第一次原始文件被后一次覆盖：156.94Mbps等聚合从实际工具输出恢复，原始帧不再可用；暂停后的0.039Mbps原始证据另存。已向用户说明，未伪造原始SHA或补帧。其它完整运行输入、CT、凭据、checkpoint/模块仍私有，旧98/92/82 runtime保持。
'''
p=repo/'docs/STATE.md';p.write_text('# 当前状态\n\n'+summary+'\n## NSS98历史状态\n\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
plan='''# 下一步：完成单WAN拥塞与RT回程闭环

以NSS107的实际结果为准。工程用自有受控TCP/UDP；无需长期Steam/CS2。禁止把启动原始错误隐藏成零，观测基线不是对加速flow错误tag的容忍。

1. 保留常驻68，用新的真实实例/流/分类来源。105入口662项，启动原始计数必须留存，未来错误零新增，完整20秒软件段通过后才准许ECM。若新轮失败，先定位实际失败帧；不重复安装分类器或反复改速率碰运气。
2. 只核实同WAN拥塞预算、RT真正回程和leaf排队是否一致。软件fallback与NSS预算独立是风险，但不是已证明缺包根因；这一主线尚未完成，不扩第二WAN、共享全局预算/Wi-Fi/autorate。必要的单WAN预算修正先依据源码和实际计数，逐项checkpoint与独立撤销。
3. 工程功能、限速与回程具备可靠证据后，最后集中一次真人CS2＋正常下载HUD jitter/loss/Miss/体验；UDP echo不代替真人验收。已有可比CPU收益不重新追求相同短测，新的不同吞吐结果不算收益。
4. 当前仅LAN4下行，真实upTag0。补足关键上行范围与完整CAKE替代缺口之前，不长期开放未知TCP/UDP，也不让NSS自行五WAN负载均衡。新连接Linux PBR，已有flow按CT WAN粘性保持。

## NSS98历史计划

'''
p=repo/'docs/PLAN.md';p.write_text(plan+p.read_text(encoding='utf-8'),encoding='utf-8')
p=repo/'docs/EXPERIMENT_LOG.md';v=p.read_text(encoding='utf-8');head,tail=v.split('\n',1);p.write_text(head+f'\n\n## NSS99–107 · {when} · 20秒拥塞与启动观测\n\n'+summary+tail,encoding='utf-8')
p=repo/'AGENTS.md';v=p.read_text(encoding='utf-8');head,tail=v.split('\n',1);p.write_text(head+'\n\n最新NSS107：'+summary.split('\n\n')[0]+' '+newtext+details+' 新105/662入口，启动原始边界至多TCP-down1包1500B可记录但不能作ECM许可；100ms等待/未来错误零新增/原完整policy/双向/20秒A仍先于ECM，原失败103保留。常驻4859/17139/config581b5d46…c791d7不变，终态ECM全零无残留；旧98/92/82 runtime原字节保留，六端点均关闭。仅LAN4下行/upTag0，没有新CPU/真人/300Mbps验收；首背景raw覆盖已披露仅恢复实际工具聚合，不伪造。下一步只补单WAN拥塞/回程，不扩WAN/共享全局预算/重装/新下载，STATE为准。\n\n'+tail,encoding='utf-8')
p=repo/'docs/ARTIFACT_INDEX.md';p.write_text('# 当前NSS107\n\n[汇总](../evidence/nss107-mainline.json) · [现场](../evidence/nss107-trials.json) · [启动观测检查](../evidence/nss107-startup-epoch-qualification.json) · [恢复](../evidence/nss107-final-audit.json) · [端点关闭](../evidence/nss107-endpoint-closure.json) · [源码](../evidence/nss107-source-proof.json) · [旧98 runtime](../evidence/nss98-runtime.json)。本地报告 outputs/nss107-mainline-report.html。\n\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
def table(t):
 if not t['completeABA']:return '<p>拒绝：'+html.escape(str(t['error']).split('\n')[0])+'</p>'
 rows=''.join(f'<tr><td>{p["phase"]}</td><td>{p["whole"]["clientTcpMbps"]:.3f}</td><td>{p["whole"]["interfaces"]["lan4"]["txMbps"]:.2f}</td><td>{p["whole"]["softirqPercent"]:.2f}%</td><td>{p["whole"]["timeSqueezeDelta"]}</td><td>{p["whole"]["udp"]["received"]}/{p["whole"]["udp"]["sent"]}</td></tr>'for p in t['metrics']['phases'])
 return '<table><tr><th>阶段</th><th>TCP Mbps</th><th>LAN4总Mbps</th><th>softirq</th><th>squeeze</th><th>UDP收/发</th></tr>'+rows+'</table>'
report=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NSS107 单WAN长窗与启动边界</title><style>body{{margin:0;background:#f5f4ef;color:#25352e;font:16px/1.8 "Microsoft YaHei",sans-serif}}main{{max-width:1050px;margin:auto;padding:36px 24px}}h1{{font-size:31px;line-height:1.4}}h2{{font-size:23px}}section{{background:white;padding:24px;border:1px solid #deded3;border-radius:10px;margin:22px 0}}table{{width:100%;border-collapse:collapse;font-variant-numeric:tabular-nums}}th,td{{padding:9px;border-bottom:1px solid #ddd;text-align:left}}small{{color:#657466}}a{{color:#326649}}@media(max-width:700px){{main{{padding:18px 10px}}th,td{{font-size:12px;padding:4px}}}}</style><main><small>ATHENA AX6600 · {when} 北京时间</small><h1>单WAN观察延长至三段各20秒</h1><p>{newtext}本轮未新增CPU收益或真人游戏结论。</p><section><h2>40Mbps受控预算</h2>{table(trials[0])}<p>bulk新增363个drop，RT leaf零丢弃/零backlog；7次真实续租，ECM0→2→0、bulk/RT、PBR/ct mark/NAT/WAN affinity与恢复通过。UDP仍有21/37/25未返回，端到端QoS未验收。异步leaf含38字节overhead约37.52Mbps，不当精确限速证明。</p></section><section><h2>30Mbps与其它流量</h2>{table(trials[1])}<p>背景LAN4达到260→308→320Mbps，受控TCP没有测满30Mbps；UDP严重缺口回到软件后继续，RT leaf自身drop0，不归因NSS。用户暂停下载后LAN4只读降至0.039Mbps，其它WAN仍约67Mbps。</p></section><section><h2>暂停后发现的启动边界</h2><p>NSS103初始TCP-down有1包1500B错误tag，ECM前拒绝，完整恢复。writer位于forward，getter在postrouting，发布时已在途的包可能只经过新getter；这是假设，尚未证明内核缺陷。</p><p>新105观测保留原始计数，不清空counter或CT。只有原始启动边界至多这一包可以被记录；其它错误拒绝。100ms软件等待包含在原1.2秒期限，随后严格验证全部未来错误零新增、四方向正包、完整policy；软件A20秒通过后才进入ECM。18目标Lua案例与完整语法通过，原生模块/QoS/分类租约不变。</p><p>首轮8个自然TCP未配到UDP同WAN，在路由器写前结束；同入口仅重试一次。</p>{table(new)}<p>{html.escape(details)}{newtext} 启动边界解释没有因此自动成为根因证明。</p></section><section><h2>验收边界与下一步</h2><p>继续完成单WAN拥塞、RT回程与leaf的关联，之后才集中一次真人CS2＋正常下载。软件fallback与NSS预算分开是风险，并未被证明为这次回程缺口原因。不上第二WAN、Wi-Fi、autorate或全局共享预算。</p><p>目前实际仅LAN4下行，upTag0，上行QoS与完整CAKE替代未验收。先前32Mbps约66.41%与48Mbps B/A2约72.19%的可比softirq收益保留；本轮不同吞吐不计算新收益。echo不是CS2 jitter/loss/Miss。</p></section><section><h2>回滚与证据</h2><p>所有实际stage checkpoint下载/SHA/gzip和独立100秒owner写前核验，native会话27秒≤已有30秒上限，真实分类租约最大6秒、续租依赖真实新快照。六端点独立FW180秒恢复、client210秒退出，原保护配置和终态完整审核通过。</p><p>常驻4859/17139/config581b5d46…c791d7/source{final['queryAge']:.2f}，ECM关闭全零，无残留，没有永久NSS、固件/内核/分区或桌面操作。</p><p>第一背景原始文件被后一次覆盖，156.94Mbps聚合由实际工具输出恢复，原始帧不再可用；已披露。暂停后原始观测另存。其它完整运行输入/CT/凭据/checkpoint/二进制留本地，旧98/92/82 runtime原字节保存。</p><p><a href="https://github.com/ZyPulse-zy/athena-nss-mainline/blob/main/docs/STATE.md">私有仓库最新状态</a></p><small>报告源码核验，未做浏览器渲染验收。</small></section></main></html>'''
(w/'outputs/nss107-mainline-report.html').write_text(report,encoding='utf-8')
dump(r/'export-receipt.json',{'passed':True,'sourceCount':len(hashes),'totalSources':len(manifest['sources']),'historicPrefixPreserved':True,'old98RuntimeSha256':sha(old),'stageCases':len(trials),'endpointClosures':len(closures),'successfulFunctionalABA':len(success),'browserRendered':False})
print(json.dumps({'exported':True,'sources':len(hashes),'totalSources':len(manifest['sources']),'stages':len(trials),'successfulABA':len(success),'closures':len(closures)}))
