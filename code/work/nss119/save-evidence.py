"""Preserve the 32 Mbps upload hypothesis and its actual non-matched result."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib,shutil,subprocess,importlib.util
w=Path(__file__).resolve().parents[2];repo=w/'athena-nss-mainline';r=w/'work/nss119'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
spec=importlib.util.spec_from_file_location('collector',w/'work/nss101/collect-lifecycle.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
cases=[p for p in r.glob('controlled-matched-aba-*')if p.is_dir()and(p/'result.json').exists()];assert len(cases)==1
t=c.stage(cases[0].relative_to(w).as_posix());assert t['passed']and t['completeABA']and all(t['rollback'].values())
m=t['metrics'];up=load(cases[0]/'actual-upstream-proof.json');trans=load(cases[0]/'uplink-transient-analysis.json');qual=load(r/'entry-qualified.json');final=load(r/'v1-final-health.json');physical=load(r/'physical-final.json');closure=c.closure(load(r/'load-reference-private.json')['dir'])
assert m['offeredTcpMbps']==32 and m['bulkDirection']=='upload'and up['passed']and trans['shaperActivityObserved']
assert qual['onlyUploadPacingChanged']and len(qual['checks'])==4 and not qual['routerPayloadChanged']
assert final['passed']and physical['passed']and final['ecmStoppedAndZero']
old=(repo/'evidence/current-runtime.json').read_bytes();assert load(repo/'evidence/current-runtime.json')['round']=='NSS118';assert subprocess.check_output(['git','show','HEAD:evidence/current-runtime.json'],cwd=repo)==old
archive=repo/'evidence/nss118-runtime.json';assert not archive.exists();archive.write_bytes(old)
manifest=load(repo/'source-manifest.json');assert len(manifest['sources'])==1364;prefix=sha(json.dumps(manifest['sources'],sort_keys=True,separators=(',',':')).encode())
allowed=['prepare.py','bounded-pacer.mjs','upload-ack.mjs','upload-server.py','ssh-client.mjs','session-binding.mjs','qualify.mjs','controlled-session.mjs','current-audit-diagnostic.mjs','match-controlled.mjs','read-controlled.mjs','run.mjs','module-stage.mjs','payload.mjs','pack-lua.mjs','pack-guardian.mjs','compact-default-queues.mjs','uplink-tag-plan.mjs','parse-ecm-any-wan.mjs','fast-path.lua','module-stage-guardian.lua','qos-physical.lua','tag-normalizer.lua','failed-wan-owner.lua','declared-baseline.mjs','service-epoch.mjs','prepare-analysis.py','analyze-long.py','calibrate-clock.mjs','prove-upstream.py','analyze-uplink-transient.py','health.mjs','read-final-physical.mjs','build-report.py','save-evidence.py']
hashes={}
for name in allowed:
 src=r/name;rel=src.relative_to(w).as_posix();dst=repo/'code'/rel;assert not dst.exists();dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);digest=sha(src.read_bytes());hashes[rel]=digest;manifest['sources'].append({'path':'code/'+rel,'workspaceSource':rel,'sha256':digest,'bytes':src.stat().st_size,'role':'single-variable-32Mbps-upload-hypothesis'})
manifest['generatedAt']=datetime.now(timezone.utc).isoformat();manifest['lastAppendExport']='NSS119';dump(repo/'source-manifest.json',manifest)
frozen={};freeze=r/'proof-v1/private-inputs';freeze.mkdir(parents=True,exist_ok=False)
for src in sorted(r.rglob('*')):
 if not src.is_file()or any(p in src.parts for p in ['proof-v1','frozen','frozen-qualified-inputs','__pycache__']):continue
 rel=src.relative_to(w);dst=freeze/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);frozen[rel.as_posix()]=sha(src.read_bytes());assert sha(dst.read_bytes())==frozen[rel.as_posix()]
dump(r/'private-input-freeze-index.json',frozen)
summary={'round':'NSS119','observedAt':final['observedAt'],'onlyUploadPacingChanged':True,'offeredUploadMbps':32,'maximumPacerCreditBytes':65536,'instantaneousLoadCatchupStillPossible':False,'sameWanAs118':False,'hardwarePayloadByteExactFrom116':True,'queueRatesUnchanged':True,'oneWan':m['oneWan'],'boundInputs':890,'phaseSeconds':20,'nativeSessionSeconds':27,'independentOwnerSeconds':100,'classifierMaximumLeaseSeconds':6,'completeFunctionalABA':True,'shaperActivityObserved':True,'boundedPacerRestoredNssThroughput':False,'rtRepliesComplete':True,'rtLeafDrop':up['uplinkLeafDelta']['8e06:']['dropped'],'bulkLeafDrop':up['uplinkLeafDelta']['8e05:']['dropped'],'newMatchedCpuComparisonAccepted':False,'strictRateAccuracyAccepted':False,'tcpThroughputRootCauseProved':False,'humanCs2Acceptance':False,'highLoad300MbpsAcceptance':False,'fullCakeReplacementAccepted':False,'residentClassifierChanged':False,'nssPermanentlyEnabled':False,'uiOperated':False,'upstreamSubmitted':False,'temporaryEndpointsClosed':1}
source={'round':'NSS119','historicPrefixSources':1364,'historicPrefixCanonicalSha256':prefix,'sources':len(hashes),'sourceHashes':hashes,'privateOwnedHostBootstrapExcluded':True,'actualBindingTreesRetained':True,'privateArtifactsFrozen':len(frozen)}
for key,value in {'mainline':summary,'trial':t,'metrics':m,'uplink-proof':up,'uplink-transient':trans,'qualification':qual['checks'],'endpoint-closure':closure,'final-audit':final,'physical-final':physical,'source-proof':source}.items():dump(repo/f'evidence/nss119-{key}.json',value)
runtime={'round':'NSS119','checkedAt':physical['observedAt'],'deploymentReference':'work/nss68/deployment-latest.json','classifierConfigSha256':final['configSha256'],'workerPid':final['workerPid'],'guardianPid':final['guardianPid'],'nssPermanentlyEnabled':False,'residentClassifierChangedThisTurn':False,'qualifiedExperimentalEntry':'work/nss119/controlled-session.mjs','qualifiedExperimentalEntryBoundInputs':890,'currentNssAdmissionMustBeRefreshedBeforeWrite':True,'audit':final,'physicalRootRestoreAudit':physical,'realHumanGameAcceptance':False,'newMatchedCpuComparisonAccepted':False,'historical117RuntimePreservedSha256':sha(old),'nightContinuationUntilBeijing':'2026-10-06T10:00:00+08:00'};dump(repo/'evidence/current-runtime.json',runtime)
when=datetime.fromisoformat(final['observedAt'].replace('Z','+00:00')).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M');speeds='/'.join(f"{p['whole']['clientTcpMbps']:.3f}"for p in m['phases']);udp='、'.join(f"{p['whole']['udp']['received']}/{p['whole']['udp']['sent']}"for p in m['phases'])
text=f'''更新：{when}，北京时间。最新NSS119；常驻68/config581b5d46…c791d7、4859/17139保持，实验全撤销。

**32Mbps上传改为最多64KiB信用，避免阻塞期间累积补发债务；原双向30/29/1队列和6/27/100期限不变。WAN{m['oneWan']}完整20秒A/B/A2、ECM0→2→0、四leaf/mark/NAT/affinity及恢复通过。服务器确认{speeds}Mbps，A/A2回到约31Mbps，B仍只有16.33Mbps。**

见 [实际指标](../evidence/nss119-metrics.json)、[完整轮次](../evidence/nss119-trial.json)、[汇总](../evidence/nss119-mainline.json)、[上行](../evidence/nss119-uplink-proof.json)、[关闭](../evidence/nss119-endpoint-closure.json)、[终态](../evidence/nss119-final-audit.json)。

- UDP收/发{udp}，上下RT drop0，上bulk drop{summary['bulkLeafDrop']}、parent overlimits+{trans['uplinkParentAndLeafClassDelta']['8e00:50']['overlimits']}；新CPU/游戏/精确限速均不验收。B吞吐仍降，当前发送器债务不能作为唯一解释。与118的WAN1不同，本轮为WAN5，不把两轮差异直接归因pacer；本轮A/B/A2是同一对flow。
- 4项本地合同验证含真实callback时长模型及10秒阻塞后的64KiB上限，硬件helper与118/116逐字节相同。新的890项入口/独立100秒守护/完整checkpoint、端点180秒FW与210秒客户端均完成；终态source{final['queryAge']:.2f}、ECM关闭全零、无事务/stage/state/模块，两物理mq/fq_codel恢复，WAN4仍down四路PBR不改。旧118 runtime逐字节保存，原始私有证据冻结。
- 下一步只提高受控上行组30→60Mbps，bulk29→59/RT1/ceil60，保留下行30和同一有界32Mbps发送器。自然选择WAN5而非改PBR；未知flow默认拒绝。先验证方向布局/原预算错误拒绝/部分恢复及payload上限，再新checkpoint与独立撤销。若不拥塞时吞吐恢复，再定位30组的拥塞/AQM，不靠同时调整RT/其它参数。
- 不动常驻classifier/upTag0，不重装/操作UI/新下载/扩WAN/共享全局预算/WiFi/autorate；最后一次集中真人CS2验收。夜间到10:00，09:50起收尾和晨间报告、推送后暂停接续。
'''
for name,title in [('STATE.md','# 当前状态'),('PLAN.md','# 当前单WAN上传后续')]:
 p=repo/'docs'/name;p.write_text(title+'\n\n'+text+'\n## NSS118历史\n\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
p=repo/'docs/EXPERIMENT_LOG.md';head,tail=p.read_text(encoding='utf-8').split('\n',1);p.write_text(head+'\n\n## NSS119 · '+when+' · 32Mbps上传仍未稳定\n\n'+text+tail,encoding='utf-8')
p=repo/'AGENTS.md';head,tail=p.read_text(encoding='utf-8').split('\n',1);p.write_text(head+'\n\n最新NSS119：只给32Mbps上传增加64KiB信用上限、890项/4合同；WAN5真实完整20秒A/B/A2、ECM0/2/0、四leaf/mark/NAT/affinity/6续租及恢复通过，确认上传'+speeds+'Mbps，UDP'+udp+'、RTdrop0、上bulk36/parent9804 overlimit。A/A2约31、B约16，未验收CPU；较118 WAN1变化不作因果比较。下一步仅上行组30→60、bulk29→59/RT1/ceil60、下行30，保持有界32发送与全部期限，自然选择WAN5不改PBR。原120候选尚未现场；常驻68不变、终态4859/17139/source2.97、ECM全零、双mq/fq_codel恢复、端点关闭、旧118原字节保留。UI停用、不新下载/重装/扩WAN/WiFi/共享预算/autorate；09:50后收尾、10点前暂停本夜接续；STATE为准。\n\n'+tail,encoding='utf-8')
p=repo/'docs/ARTIFACT_INDEX.md';p.write_text('# 当前NSS119\n\n[上传](../evidence/nss119-metrics.json) · [轮次](../evidence/nss119-trial.json) · [汇总](../evidence/nss119-mainline.json) · [终态](../evidence/nss119-final-audit.json) · [历史117 runtime](../evidence/nss118-runtime.json)。\n\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
dump(r/'export-receipt.json',{'passed':True,'newSources':len(hashes),'totalSources':len(manifest['sources']),'uploadMbps':speeds,'privateArtifacts':len(frozen)});print(json.dumps({'exported':True,'sources':len(hashes),'totalSources':len(manifest['sources']),'uploadMbps':speeds}))
