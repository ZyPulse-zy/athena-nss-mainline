"""One deployment milestone; operational and credential-bearing records stay local."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json,re,subprocess
w=Path(__file__).resolve().parents[2];repo=w/'athena-nss-mainline';delivery=Path(__file__).parent;service=w/'work/resident-service-dev-20261008'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
dump=lambda v:json.dumps(v,ensure_ascii=False,indent=2)+'\n'
sha=lambda b:hashlib.sha256(b).hexdigest()
node='C:/Users/lishu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
def git(*args):return subprocess.check_output(['git',*args],cwd=repo)
q=read(service/'qualification-latest-private.json');assert q['passed']
for p,h in q['sourceManifest'].items():assert sha((w/p).read_bytes())==h,p
observed=subprocess.run([node,str(service/'daemon.mjs'),'status'],cwd=w,capture_output=True,text=True,encoding='utf-8')
with (delivery/'publication-live-status-raw-private.json').open('x',encoding='utf-8') as f:f.write(dump({'code':observed.returncode,'stdout':observed.stdout,'stderr':observed.stderr}))
assert observed.returncode==0
live=json.loads(observed.stdout);assert live['state']=='WAITING_FLOW' and live['running'] and live['identityVerified'] and live['heartbeatFresh'] and live['reads']>=2 and live['generationsStarted']==0
assert live['lastObservation']['triples']==0 and not live['activeGenerationLockPresent']
first=read(delivery/'first-status.json');progress=read(delivery/'progress-status.json');stop=read(delivery/'stopped-status.json');retained=read(delivery/'retained-status.json')
assert first['reads']<progress['reads'] and first['lastObservation']['sourceSequence']<progress['lastObservation']['sourceSequence']
assert stop['state']=='STOPPED' and stop['restorationPassed'] and not stop['running'] and not stop['controllerLockPresent'] and not stop['activeGenerationLockPresent']
ledgers=[read(delivery/'stopped-ledger-private.json'),read(service/'service-latest-private.json')]
audits=[]
for ledger in ledgers:
 root=w/read(w/ledger['runDirectory']/'startup-health-reference-private.json')['root'];closure=w/read(root/'closure-pointer.json')['directory']
 a=json.loads((closure/'final-audit-stdout-private.txt').read_text(encoding='utf-8').strip().splitlines()[-1]);p=read(closure/'physical-final.json')
 assert a['passed'] and a['queryAge']<6 and a['ecmClosedAndZero'] and a['allFiveHealthyWanBaseline'] and a['protectedConfigurationUnchanged'] and p['passed'] and p['defaultQueueOptionsAndHandlesExact']
 audits.append({k:a[k] for k in ['passed','queryAge','ecmClosedAndZero','allFiveHealthyWanBaseline','protectedConfigurationUnchanged']}|{'physicalQueuesOptionsAndHandlesExact':True})
task=read(delivery/'tasks.json');assert task['passed'] and task['hardTerminationDisabled'] and task['logonTriggerCount']==task['restartCount']==0
manifest=read(repo/'source-manifest.json');prefix=list(manifest['sources']);assert len(prefix)==5939
base=git('rev-parse','HEAD').decode().strip();assert base=='4f2a6287a11cedfb26c88b4f7c56e80635cb6136'
oldtree={n.decode():h.decode().split()[2] for row in git('ls-tree','-r','-z','HEAD','--','code','evidence').split(b'\0') if row for h,n in [row.split(b'\t',1)]}
sources={p:(w/p).read_bytes() for p in q['sourceManifest']}
for name in ['capture.mjs','check-service.py','publish.py']:sources[(delivery/name).relative_to(w).as_posix()]=(delivery/name).read_bytes()
new=[]
for rel,b in sorted(sources.items()):
 assert not re.search('private|credential|connect-router',Path(rel).name,re.I)
 target=repo/'code'/rel;assert not target.exists();target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b)
 new.append({'path':'code/'+rel,'workspaceSource':rel,'sha256':sha(b),'bytes':len(b),'role':'manual-resident-orchestration-deployment'})
proof={'passed':True,'baseCommit':base,'historicalSourcePrefix':len(prefix),'newSources':len(new),'sourceHashes':{x['workspaceSource']:x['sha256'] for x in new},'historicalCodeEvidenceUnmodified':True,'historicalCodeEvidenceBlobs':len(oldtree),'noPrivateRuntimeInputsExported':True,'normalEntryAndDataPlaneUnmodified':True}
short=lambda s:{'observedAt':s['observedAt'],'reads':s['reads'],'sourceSequence':s['lastObservation']['sourceSequence'],'sourceAge':s['lastObservation']['sourceAge']}
summary={'milestone':'manual resident process deployment with existing normal-flow entry','manualResidentPilotStarted':True,'gracefulStopAndRestartPassed':True,
 'originalNormalEntryUnmodified':True,'sevenDataPlaneLuaUnmodified':True,'unchangedHistoricalNormalSoakReused':True,
 'localChecks':q['checks'],'javascriptSyntaxSources':q['syntaxSources'],'powershellSyntaxSources':q['powershellSources'],
 'plan':ledgers[-1]['servicePlan'],'first':short(first),'progress':short(progress),'stopped':stop,'retained':{'observedAt':datetime.now(timezone.utc).isoformat(),**live},'startupHealth':audits,'task':task,
 'newHardwareGenerations':0,'newNssHardwareAcceptanceClaim':False,'automaticStartAtLogon':False,'automaticRestartOnFailure':False,'trafficGenerated':False,'cs2OrSteamOperated':False,'newCpuBenchmark':False,'uninterruptedNssClaim':False,
 'knownLimitations':['Manual on-demand Windows task, no logon trigger; process residence is distinct from uninterrupted NSS.',
  'Current natural traffic has zero eligible triples; no new active NSS hardware or long normal-use soak is claimed.',
  'The unchanged entry selects two TCP BULK on distinct natural WANs and one admitted UDP RT for this PC.',
  'Three consecutive source refusals, source binding changes or restored entry refusal pause admission; failures are not blindly restarted.',
  'Per-generation checkpoint and detached restoration remain required; all original data-plane bounds stay unchanged.']}
failures={'passedEvidence':False,'developmentOnly':True,'routerWrites':False,'hardwareExperimentStartedForTheseFailures':False,'items':[
 {'type':'P2','scope':'local model test','error':'Expected six starts although the fake clock allowed a seventh start before its stop threshold','resolution':'Use an explicit1450second model stop; rolling-window quota assertions and full local batch pass','originalRawSha256':sha((service/'local-batch-1791426345815-9da67f8e'/'policy-raw.json').read_bytes())},
 {'type':'P2','scope':'task metadata capture','error':'Read nonexistent DisallowHardTerminate property; original raw output failed validation and is invalid evidence','resolution':'Read actual AllowHardTerminate=false; task configuration unchanged','originalRawSha256':sha((delivery/'tasks-raw-private.json').read_bytes())}]}
now=datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
body=f'''# 手动常驻试用进程已部署

北京时间{now}，常驻进程已保留运行，当前为WAITING_FLOW。18项本地回归、8份JavaScript和2份PowerShell语法通过；真实启动、分类源推进、正常停止/锁解除、重新启动通过。四个已有相关任务的XML指纹未变，新任务无登录触发、无故障自动重启，使用普通用户权限。

进程每30秒观察已有流量，合格时调用原正常入口，每代90秒；每20分钟最多开始四代，每代新checkpoint下载/SHA/gzip和控制连接外独立恢复，恢复审核通过后才进入下一代。source6/native120/owner180/client180与全部原字节限制保持。原四代900秒控制器/360秒累计NSS、五WAN/QoS/CPU证明复用，不重跑数据面。

当前实际合格组合0、新NSS代0。两次启动前完整只读审核及两物理队列选项/handle通过，ECM关闭全零、五WAN健康、保护配置不变。这次证明的是常驻进程和正常停止/重启；真实普通负载的首次自动准入与更长soak尚待自然出现，不声称连续永久NSS或默认开机常驻。实际[部署结果](../evidence/resident-service-runtime.json)。

## 控制

原工作区执行 `powershell -File work/resident-service-dev-20261008/service.ps1 -Mode Status` 查看实际进程身份、心跳、源序列和代数。`Stop`停止新准入，当前代按原独立期限恢复后退出；`Start`重新启动手动试用，`Uninstall`只在进程停止和恢复确认后移除本任务。任务名`Athena-NSS-Controller-Manual`；[控制脚本](../code/work/resident-service-dev-20261008/service.ps1)、[调度器](../code/work/resident-service-dev-20261008/daemon.mjs)、[调度策略](../code/work/resident-service-dev-20261008/policy.mjs)。私有连接、当前部署输入和模块仍只在原工作区。

## 限制与后续

- 仅本机两TCP BULK＋一UDP RT组合，两个TCP使用已有不同自然WAN；其它/未知流保留软件路径。
- 常驻进程持续等待，数据面仍是有限代。登录自启和长期默认运行尚未验收。
- 连续三次源读取拒绝、绑定改变、入口拒绝后暂停准入；不盲重试。P0保留锁并停止后续写入，先确认恢复。
- 常态只轮转本进程的新操作性观察缓存，保留最近16组；硬件代、失败和冻结历史证据不删除。
- Wi-Fi、autorate、ECN、新类型、新QoS、新CPU与极端故障模型不扩展。

本批两处P2报告/模型错误均在本地修正，原失败留存，未因此开硬件实验。[原错误摘要](../evidence/resident-service-development-failures.json)、[白名单源码](../evidence/resident-service-source-proof.json)。
'''
(repo/'docs/RESIDENT_SERVICE.md').write_text(body,encoding='utf-8')
header=body.split('## 控制')[0]+ '\n详见[使用及限制](RESIDENT_SERVICE.md)。\n\n## 以下保留历史状态\n\n'
for n in ['STATE.md','PLAN.md']:
 p=repo/'docs'/n;p.write_text(header+p.read_text(encoding='utf-8'),encoding='utf-8')
notice=f'# {now} — 手动常驻部署批次\n\n真实进程启动/分类源推进/停止/重启通过，已保留WAITING_FLOW；当前0合格组合/0新NSS代。原入口与数据面不变，18本地检查通过，模型计时和Windows任务属性两处P2原失败留存。只复用历史硬件证据，未新增硬件轮次。见[部署与限制](RESIDENT_SERVICE.md)。\n\n## 以下保留历史记录\n\n'
for n in ['KNOWN_FAILURES.md','EXPERIMENT_LOG.md']:
 p=repo/'docs'/n;p.write_text(notice+p.read_text(encoding='utf-8'),encoding='utf-8')
p=repo/'docs/BACKLOG.md';p.write_text('# 常驻部署后续\n\n当前手动常驻进程已保留，首次自然负载准入和更长正常使用soak待出现；通过后再决定登录自启与默认部署。不新开模拟fixture或重复核心证明。非阻塞限制见[使用文档](RESIDENT_SERVICE.md)。\n\n## 以下保留历史待办\n\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
p=repo/'README.md';p.write_text('# 当前交付：手动常驻 Multi-WAN controller\n\n常驻进程已保留运行，真实启动/停止/重启与源读取推进通过；无登录自启。当前等待合格自然流量，尚无新的NSS代，原硬件证据复用。见[状态](docs/STATE.md)及[控制与限制](docs/RESIDENT_SERVICE.md)。\n\n## 以下保留历史介绍\n\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
p=repo/'AGENTS.md';p.write_text('# 当前接续：手动常驻进程运行中\n\n常驻进程已部署并保留WAITING_FLOW，任务Athena-NSS-Controller-Manual，无登录触发或故障自动重启。先读docs/STATE.md、PLAN.md、KNOWN_FAILURES.md与RESIDENT_SERVICE.md，并核对实际service.ps1 Status；不要重复启动、重做已结束soak或重开fixture。18本地检查和实际启动/源推进/停止/重启通过；当前0新NSS代。源/绑定/入口拒绝会暂停准入，P0禁止后续写入并先确认恢复。原入口/数据面/所有期限不变，heartbeat仍暂停。用户常驻授权持续有效。\n\n## 以下保留历史接续\n\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
for name,obj in [('resident-service-runtime.json',summary),('resident-service-source-proof.json',proof),('resident-service-development-failures.json',failures)]:
 with (repo/'evidence'/name).open('x',encoding='utf-8') as f:f.write(dump(obj))
(repo/'tools/check_resident_service.py').write_bytes((delivery/'check-service.py').read_bytes())
p=repo/'tools/check_repository.py';s=p.read_text(encoding='utf-8');needle="print(json.dumps({'passed':True,'filesChecked':count"
assert s.count(needle)==1;s=s.replace(needle,"if (root/'evidence/resident-service-runtime.json').exists():\n import runpy\n runpy.run_path(str(root/'tools/check_resident_service.py'))['check'](root)\n"+needle);p.write_text(s,encoding='utf-8')
manifest['sources']+=new;manifest['residentServiceExport']='MANUAL_RESIDENT_PROCESS_NORMAL_FLOW_WAITING';manifest['generatedAt']=datetime.now(timezone.utc).isoformat();(repo/'source-manifest.json').write_text(dump(manifest),encoding='utf-8')
assert manifest['sources'][:5939]==prefix
for n,h in oldtree.items():assert git('rev-parse','HEAD:'+n).decode().strip()==h
print(json.dumps({'passed':True,'newSources':len(new),'sourceHashes':len(manifest['sources']),'newHardwareGenerations':0,'retainedState':live['state'],'readProgress':live['reads']}))
