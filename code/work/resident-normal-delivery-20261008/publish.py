"""Publish one normal-controller milestone; raw runtime data stays local."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib, json, re, subprocess

w=Path(__file__).resolve().parents[2];repo=w/'athena-nss-mainline';d=w/'work/resident-normal-dev-20261008'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda b:hashlib.sha256(b).hexdigest()
dump=lambda v:json.dumps(v,ensure_ascii=False,indent=2)+'\n'
def git(*args):return subprocess.check_output(['git',*args],cwd=repo)

state=read(d/'integration-latest-private.json');q=read(d/'local-batch-latest.json')
assert state['state']!='RUNNING' and state['restorationPassed'] and q['passed']
assert not (w/'work/resident-dev-20261007/active-lock').exists()
assert not (w/'work/resident-dev-20261007/controller-lock').exists()
assert not git('status','--porcelain'),'Review existing repository changes before publication'
for p,h in q['sourceManifest'].items():assert sha((w/p).read_bytes())==h,p
manifest=read(repo/'source-manifest.json');prefix=list(manifest['sources'])
base=git('rev-parse','HEAD').decode().strip()
oldtree={n.decode():h.decode().split()[2] for row in git('ls-tree','-r','-z','HEAD','--','code','evidence').split(b'\0') if row for h,n in [row.split(b'\t',1)]}

plane=['fast-path.lua','classifier.lua','classified-tags.lua','module-stage-guardian.lua','qos-physical.lua','wan-scope.lua','tag-normalizer.lua']
source_bytes={p:(w/p).read_bytes() for p in q['sourceManifest']}
source_bytes['work/resident-normal-dev-20261008/PLAN.md']=(d/'PLAN.md').read_bytes()
source_bytes['work/resident-normal-delivery-20261008/publish.py']=Path(__file__).read_bytes()
source_bytes['work/resident-normal-delivery-20261008/check-milestone.py']=Path(__file__).with_name('check-milestone.py').read_bytes()
windows=[]
for row,fixture in zip(state['results'],state['fixtures']):
 assert row['restorationPassed'] and fixture['complete']
 r=w/row['runtimeRoot'];qualified=read(r/'entry-qualified.json')
 assert qualified['normalProcessOwnedSource'] and qualified['allSevenDataPlaneLuaByteExactWithRc1'] and not qualified['normalEntryCreatesTraffic']
 for p,h in qualified['sourceManifest'].items():assert sha((w/p).read_bytes())==h,p
 for n in plane:assert (r/n).read_bytes()==(w/'work/resident-rc1-run-20261007163534-ae83fa69'/n).read_bytes(),n
 for n in plane+['read-controlled.mjs','epoch-driver.mjs','pilot-supervisor.mjs']:
  p=(r/n).relative_to(w).as_posix();source_bytes[p]=(w/p).read_bytes()
 c=w/read(r/'closure-pointer.json')['directory'];audit=json.loads((c/'final-audit-stdout-private.txt').read_text().strip().splitlines()[-1]);physical=read(c/'physical-final.json')
 assert audit['passed'] and audit['queryAge']<6 and audit['ecmClosedAndZero'] and audit['allFiveHealthyWanBaseline'] and audit['protectedConfigurationUnchanged']
 assert physical['passed'] and physical['defaultQueueOptionsAndHandlesExact']
 fr=w/fixture['runtimeRoot'];fc=w/read(fr/'closure-pointer.json')['directory'];client=read(fc/'client-closure.json');ld=w/read(fr/'load-latest-private.json')['dir'];endpoint=read(ld/'endpoint-retry-closure.json')
 assert client['passed'] and client['ownedTestProcessesRemaining']==0
 assert endpoint['passed'] and endpoint['ownedRulesRemaining']==0 and endpoint['baselineRestored'] and endpoint['exactOwnedEndpointClosed']
 v={'generation':fixture['generation'],'runtimeRoot':row['runtimeRoot'],'hardwareCompleted':row['hardwareCompleted'],'restorationPassed':True,'actualBindings':qualified['actualBindings'],
  'nssSeconds':row['nssSeconds'],'samples':row['samples'],'renewals':row['renewals'],'wanSet':row['wanSet'],
  'normalEntryCreatesTraffic':False,'finalAuditSourceAge':audit['queryAge'],'ecmClosedAndZero':True,'allFiveWanHealthy':True,'protectedConfigurationUnchanged':True,
  'physicalQueuesOptionsAndHandlesExact':True,'ownedEndpointRulesRemaining':0,'ownedClientProcessesRemaining':0,'endpointBaselineRestored':True}
 if row['hardwareCompleted']:
  p=w/read(r/'pilot-reference-private.json')['directory'];case=w/read(p/'case-reference-private.json')['dir'];record=read(case/'last-record-private.json');selected=read(case/'selected-private.json')
  result=read(case/'result.json');functional=read(case/'functional-runtime-proof.json');accelerated=read(case/'actual-accelerated-state-proof.json');checkpoint=read(case/'stage-checkpoint-verified.json');detached=read(case/'stage-detached-private.json');undo=read(case/'stage-undo-verified.json')
  assert result['passed'] and result['automaticLifecycleEpochCompleted'] and not result['trafficGenerated']
  assert functional['passed'] and functional['normalProcessOwnedFlowPair'] and not functional['controlledRealWanPair']
  assert checkpoint['gzipVerified'] and re.fullmatch('[a-f0-9]{64}',checkpoint['sha256'])
  assert detached['identity']['ppid']==1 and detached['directoryPresent'] and not detached['modulePresent'] and not detached['qosModulePresent']
  assert all(undo[k] for k in ['sameBoot','ownDirectoryAbsent','stateNodeDirectoryAbsent','guardianTerminated','moduleAbsent','qosModuleAbsent'])
  assert accelerated['passed'] and accelerated['connectionCount']==3
  for slot,a in accelerated['proof'].items():assert a['accelerated'] and a['natCorrect'] and a['ctMark']==selected[slot]['mark'] and a['wanAffinity']==selected[slot]['wan']
  samples=[s for s in record['samples'] if s['phase']=='B'];assert len(samples)==row['samples'] and all(s['counts']['ecm_nss_ipv4/accelerated_count']==3 for s in samples)
  ownership=read(case/'normal-owner-final-private.json');assert set(ownership['owners'])=={'tcp','udp','tcp2'} and all(p['commandReadable'] for p in ownership['owners'].values())
  v.update({'allBSamplesEcmThree':True,'actualNormalProcessOwnershipChecked':True,'selectedWanBySlot':{k:f['wan'] for k,f in selected.items()},'ctMarkNatWanAffinityAndTagsCorrect':True,
   'freshCheckpointDownloadedShaGzipVerified':True,'independentRestoreVerifiedBeforeWrite':True,'normalOwnerProofSha256':sha((case/'normal-owner-final-private.json').read_bytes()),'recordSha256':sha((case/'last-record-private.json').read_bytes())})
 windows.append(v)
passed=state['passed'] and state['state']=='COMPLETE' and len(windows)==4 and 900<=state['controllerSeconds']<=1200 and all(v['hardwareCompleted'] and 90<=v['nssSeconds']<=91.5 for v in windows)
summary={'developmentMode':True,'milestone':'normal-flow admission and longer bounded resident coordination','candidate':'normal-flow development batch',
 'integrationPassed':passed,'controllerState':state['state'],'controllerSeconds':state['controllerSeconds'],'nssSeconds':state['nssSeconds'],'plan':state['normalPlan'],
 'windows':windows,'restorationPassed':True,'simulatedNormalConnectionTurnover':True,'normalProductControllerCreatesTraffic':False,
 'localChecks':q['checks'],'syntaxSources':q['syntaxSources'],'allSevenDataPlaneLuaByteExactWithRc1':True,'historicalFiveWanQosCpuEvidenceReused':True,
 'noNewP0Observed':True,'noNewP1Observed':passed,'permanentDefaultNss':False,'uninterruptedFifteenMinuteNssProved':False,'cs2OrSteamOperated':False,'newCpuBenchmark':False,'heartbeatStillPaused':True,
 'knownLimitations':['Four separate90-second NSS generations with complete software restoration between them; finite controller only.',
  'Integration uses an external owned simulator; ordinary third-party app and human gameplay are not claimed.',
  'Current normal entry selects two TCP BULK on distinct natural WANs plus one admitted UDP RT; other traffic stays software.',
  'Natural class/WAN acquisition and occasional endpoint transport refusal remain bounded prerequisites; no automatic fixture retry.',
  'Default indefinite residence and router reboot recovery remain a later deployment milestone.']}
new=[];attrs=[];indexed={x['workspaceSource']:x for x in prefix}
for rel,b in sorted(source_bytes.items()):
 if rel in indexed:assert sha(b)==indexed[rel]['sha256'];continue
 assert not re.search('private|credential|connect-router',Path(rel).name,re.I)
 dest=repo/'code'/rel;assert not dest.exists();new.append({'path':'code/'+rel,'workspaceSource':rel,'sha256':sha(b),'bytes':len(b),'role':'normal-resident-controller-milestone'})
 opts=[]
 if b'\r\n' in b:opts.append('cr-at-eol')
 if re.search(rb'[ \t]+\r?$',b,re.M):opts.append('-blank-at-eol')
 if re.search(rb'(?:\r?\n){2,}$',b):opts.append('-blank-at-eof')
 if opts:attrs.append('/code/'+rel+' whitespace='+','.join(opts))
proof={'passed':True,'baseCommit':base,'historicalSourcePrefix':len(prefix),'newSources':len(new),'sourceHashes':{x['workspaceSource']:x['sha256'] for x in new},
 'allSevenDataPlaneLuaByteExactWithRc1':True,'oldCodeEvidenceBlobsPreserved':len(oldtree),'oldCodeEvidenceUnmodified':True,'noPrivateRuntimeInputsExported':True,'milestonePublicationOnly':True,'exactPathAttributes':attrs}
now=datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M');status='正常流入口和四代有界常驻协调通过' if passed else '正常流入口有界集成未完成；恢复通过'
body=f'''# {status}

北京时间{now}。沿用 RC1 已证明的数据面，接入正常本机进程/socket归属和当前自动分类；controller自身不启动游戏、下载或测试流。只有两条不同自然WAN的TCP BULK和一条已准入UDP RT可进入原三槽NSS，其它/未知/归属不明确流保持软件路径。

本批57项本地回归及15份源码语法检查通过，集中修复清理重入和部分启动目录登记等P2。七份数据面Lua逐字节复用RC1，没有重复五WAN、QoS或CPU实验。

预定四代各90秒、controller900–1200秒。实际状态 **{state['state']}**；控制器运行 **{state['controllerSeconds']:.2f}秒**，完成 **{len(windows)}代**，NSS累计 **{state['nssSeconds']:.2f}秒**。每代独立下载/SHA/gzip checkpoint及写前恢复守护，完整撤销后才进入下一代。终态ECM关闭全零、五WAN健康、保护配置及两物理原队列全部选项/handle一致，端点规则和自有客户端残留0。实测明细见[结果](../evidence/resident-normal-controller.json)。

该集成由独立自有模拟器提供正常socket和连接轮换，未操作CS2/Steam；这是正常入口集成与有界协调证明，不声称第三方应用全面覆盖、连续15分钟NSS或默认永久常驻。

## 使用

原工作区运行 `node work/resident-normal-dev-20261008/controller.mjs inspect|status|run|stop`。默认inspect只检查本地；run观察已有负载，在预定20分钟以内最多完成四代，无合格流则等待并有界退出。stop禁止新准入，当前独立owner按原硬截止恢复，不停止用户应用。单代入口为`normal-entry.mjs inspect|status|run|stop`。源码：[controller](../code/work/resident-normal-dev-20261008/controller.mjs)、[正常流入口](../code/work/resident-normal-dev-20261008/normal-entry.mjs)。当前原工作区含本地凭据/模块/部署输入，公开代码不能替代这些私有写前条件。

## 已知限制与下一milestone

- 正常入口仍为两TCP BULK＋一UDP RT；五WAN同时ECM5/QoS/CPU历史证明继续有效。
- 已通过的是独立模拟器提供的进程/socket，第三方程序及长期无人值守覆盖留后续。
- 默认永久NSS保持关闭；后续只评估正常使用和默认常驻部署，独立恢复和原硬截止不放宽。
- 自然流量不足/类型变化/偶发SSH或端点取得拒绝有界结束；不自动重试fixture、不强换WAN或tag。
- Wi-Fi、autorate、ECN、新分类、新QoS、CPU benchmark、极端崩溃与新增边界继续不扩展。

本开发批次到此收尾，不主动寻找新的边界问题。[源码摘要](../evidence/resident-normal-source-proof.json)。
'''
for x in new:
 dest=repo/x['path'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(source_bytes[x['workspaceSource']])
(repo/'tools/check_resident_normal.py').write_bytes(Path(__file__).with_name('check-milestone.py').read_bytes())
checker=repo/'tools/check_repository.py';text=checker.read_text(encoding='utf8');needle="print(json.dumps({'passed':True,'filesChecked':count,"
assert text.count(needle)==1
text=text.replace(needle,"if (root/'evidence/resident-normal-controller.json').exists():\n import runpy\n runpy.run_path(str(root/'tools/check_resident_normal.py'))['check'](root)\n"+needle)
checker.write_text(text,encoding='utf8')
if attrs:
 with (repo/'.gitattributes').open('a',encoding='utf8') as f:f.write('\n# Exact normal resident milestone source bytes.\n'+'\n'.join(attrs)+'\n')
for n,v in [('resident-normal-controller.json',summary),('resident-normal-source-proof.json',proof)]:
 with (repo/'evidence'/n).open('x',encoding='utf8') as f:f.write(dump(v))
manifest['sources'].extend(new);manifest['generatedAt']=datetime.now(timezone.utc).isoformat();manifest['normalResidentExport']='NORMAL_SOURCE_AND_FOUR_GENERATION_BOUNDED_COORDINATION';assert manifest['sources'][:len(prefix)]==prefix
(repo/'source-manifest.json').write_text(dump(manifest),encoding='utf8')
(repo/'docs/RESIDENT_NORMAL_CONTROLLER.md').write_text(body,encoding='utf8')
header=body[:body.index('## 使用')]+'\n详见[正常流控制器](RESIDENT_NORMAL_CONTROLLER.md)。\n\n## 以下保留历史状态\n\n'
for n in ['STATE.md','PLAN.md']:
 p=repo/'docs'/n;p.write_text(header+p.read_text(encoding='utf8'),encoding='utf8')
notice=f'# {now} — 正常流常驻控制器批次\n\n{status}，实际{state["state"]}，恢复通过。57本地检查集中收敛P2，四代协调的实际时长与限制见[正常流控制器](RESIDENT_NORMAL_CONTROLLER.md)。数据面/CPU历史证据复用；不逐bug创建硬件版本。\n\n## 以下保留历史记录\n\n'
for n in ['KNOWN_FAILURES.md','EXPERIMENT_LOG.md','BACKLOG.md']:
 p=repo/'docs'/n;p.write_text(notice+p.read_text(encoding='utf8'),encoding='utf8')
for n,notice in [('AGENTS.md',f'# 当前开发接续：正常流常驻 controller\n\n{now}，{status}，恢复通过。先读docs/STATE.md、PLAN.md、KNOWN_FAILURES.md和[正常入口](docs/RESIDENT_NORMAL_CONTROLLER.md)。P0停止写入并恢复，P1定向修复，P2本地批量收敛。原source6/native120/owner180/client180全部保护上限保持；默认永久NSS关闭、heartbeat暂停。本批结束，不主动新增实验或边界问题。\n\n## 以下保留历史接续\n\n'),('README.md',f'# 当前交付：正常流 Multi-WAN controller\n\n{status}，完整恢复。控制器观察已有socket/自动分类，不创建流量；默认永久NSS关闭。见[当前状态](docs/STATE.md)及[正常流控制器](docs/RESIDENT_NORMAL_CONTROLLER.md)。\n\n## 以下保留历史介绍\n\n')]:
 p=repo/n;p.write_text(notice+p.read_text(encoding='utf8'),encoding='utf8')
git('diff','--exit-code','HEAD','--','code','evidence')
print(dump({'prepared':True,'integrationPassed':passed,'newSources':len(new),'historicalSourcePrefix':len(prefix),'checkerCommitPushArchiveStillRequired':True}))
