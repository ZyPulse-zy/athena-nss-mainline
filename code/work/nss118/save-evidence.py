"""Preserve the 32 Mbps upload hypothesis and its actual non-matched result."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib,shutil,subprocess,importlib.util
w=Path(__file__).resolve().parents[2];repo=w/'athena-nss-mainline';r=w/'work/nss118'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
spec=importlib.util.spec_from_file_location('collector',w/'work/nss101/collect-lifecycle.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
cases=[p for p in r.glob('controlled-matched-aba-*')if p.is_dir()and(p/'result.json').exists()];assert len(cases)==1
t=c.stage(cases[0].relative_to(w).as_posix());assert t['passed']and t['completeABA']and all(t['rollback'].values())
m=t['metrics'];up=load(cases[0]/'actual-upstream-proof.json');trans=load(cases[0]/'uplink-transient-analysis.json');qual=load(r/'entry-qualified.json');final=load(r/'v1-final-health.json');physical=load(r/'physical-final.json');closure=c.closure(load(r/'load-reference-private.json')['dir'])
assert m['offeredTcpMbps']==32 and m['bulkDirection']=='upload'and up['passed']and trans['shaperActivityObserved']
assert qual['onlyOfferedUploadChanged']and len(qual['checks'])==9 and not qual['routerPayloadChanged']
assert final['passed']and physical['passed']and final['ecmStoppedAndZero']
old=(repo/'evidence/current-runtime.json').read_bytes();assert load(repo/'evidence/current-runtime.json')['round']=='NSS117';assert subprocess.check_output(['git','show','HEAD:evidence/current-runtime.json'],cwd=repo)==old
archive=repo/'evidence/nss117-runtime.json';assert not archive.exists();archive.write_bytes(old)
manifest=load(repo/'source-manifest.json');assert len(manifest['sources'])==1331;prefix=sha(json.dumps(manifest['sources'],sort_keys=True,separators=(',',':')).encode())
allowed=['prepare.py','upload-ack.mjs','upload-server.py','ssh-client.mjs','session-binding.mjs','qualify.mjs','controlled-session.mjs','current-audit-diagnostic.mjs','match-controlled.mjs','read-controlled.mjs','run.mjs','module-stage.mjs','payload.mjs','pack-lua.mjs','pack-guardian.mjs','compact-default-queues.mjs','uplink-tag-plan.mjs','parse-ecm-any-wan.mjs','fast-path.lua','module-stage-guardian.lua','qos-physical.lua','tag-normalizer.lua','failed-wan-owner.lua','declared-baseline.mjs','service-epoch.mjs','prepare-analysis.py','analyze-long.py','calibrate-clock.mjs','prove-upstream.py','analyze-uplink-transient.py','health.mjs','read-final-physical.mjs','save-evidence.py']
hashes={}
for name in allowed:
 src=r/name;rel=src.relative_to(w).as_posix();dst=repo/'code'/rel;assert not dst.exists();dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);digest=sha(src.read_bytes());hashes[rel]=digest;manifest['sources'].append({'path':'code/'+rel,'workspaceSource':rel,'sha256':digest,'bytes':src.stat().st_size,'role':'single-variable-32Mbps-upload-hypothesis'})
manifest['generatedAt']=datetime.now(timezone.utc).isoformat();manifest['lastAppendExport']='NSS118';dump(repo/'source-manifest.json',manifest)
frozen={};freeze=r/'proof-v1/private-inputs';freeze.mkdir(parents=True,exist_ok=False)
for src in sorted(r.rglob('*')):
 if not src.is_file()or any(p in src.parts for p in ['proof-v1','frozen','frozen-qualified-inputs','__pycache__']):continue
 rel=src.relative_to(w);dst=freeze/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);frozen[rel.as_posix()]=sha(src.read_bytes());assert sha(dst.read_bytes())==frozen[rel.as_posix()]
dump(r/'private-input-freeze-index.json',frozen)
summary={'round':'NSS118','observedAt':final['observedAt'],'onlyOfferedUploadChanged':True,'offeredAveragePerConnectionMbps':32,'instantaneousLoadCatchupStillPossible':True,'hardwarePayloadByteExactFrom116':True,'queueRatesUnchanged':True,'oneWan':m['oneWan'],'boundInputs':857,'phaseSeconds':20,'nativeSessionSeconds':27,'independentOwnerSeconds':100,'classifierMaximumLeaseSeconds':6,'completeFunctionalABA':True,'shaperActivityObserved':True,'smallerRateTransitionRestoredThroughput':False,'rtRepliesComplete':True,'rtLeafDrop':up['uplinkLeafDelta']['8e06:']['dropped'],'bulkLeafDrop':up['uplinkLeafDelta']['8e05:']['dropped'],'newMatchedCpuComparisonAccepted':False,'strictRateAccuracyAccepted':False,'tcpThroughputRootCauseProved':False,'humanCs2Acceptance':False,'highLoad300MbpsAcceptance':False,'fullCakeReplacementAccepted':False,'residentClassifierChanged':False,'nssPermanentlyEnabled':False,'uiOperated':False,'upstreamSubmitted':False,'temporaryEndpointsClosed':1}
source={'round':'NSS118','historicPrefixSources':1331,'historicPrefixCanonicalSha256':prefix,'sources':len(hashes),'sourceHashes':hashes,'privateOwnedHostBootstrapExcluded':True,'actualBindingTreesRetained':True,'privateArtifactsFrozen':len(frozen)}
for key,value in {'mainline':summary,'trial':t,'metrics':m,'uplink-proof':up,'uplink-transient':trans,'qualification':qual['checks'],'endpoint-closure':closure,'final-audit':final,'physical-final':physical,'source-proof':source}.items():dump(repo/f'evidence/nss118-{key}.json',value)
runtime={'round':'NSS118','checkedAt':physical['observedAt'],'deploymentReference':'work/nss68/deployment-latest.json','classifierConfigSha256':final['configSha256'],'workerPid':final['workerPid'],'guardianPid':final['guardianPid'],'nssPermanentlyEnabled':False,'residentClassifierChangedThisTurn':False,'qualifiedExperimentalEntry':'work/nss118/controlled-session.mjs','qualifiedExperimentalEntryBoundInputs':857,'currentNssAdmissionMustBeRefreshedBeforeWrite':True,'audit':final,'physicalRootRestoreAudit':physical,'realHumanGameAcceptance':False,'newMatchedCpuComparisonAccepted':False,'historical117RuntimePreservedSha256':sha(old),'nightContinuationUntilBeijing':'2026-10-06T10:00:00+08:00'};dump(repo/'evidence/current-runtime.json',runtime)
when=datetime.fromisoformat(final['observedAt'].replace('Z','+00:00')).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M');speeds='/'.join(f"{p['whole']['clientTcpMbps']:.3f}"for p in m['phases']);udp='、'.join(f"{p['whole']['udp']['received']}/{p['whole']['udp']['sent']}"for p in m['phases'])
text=f'''更新：{when}，北京时间。最新NSS118，常驻68/config581b5d46…c791d7、4859/17139不变；实验均撤销。

**只把上传目标48→32Mbps，原30/29/1双向队列和6/27/100秒来源/native/owner不变。单WAN{m['oneWan']}完整三段各20秒，ECM0→2→0、四leaf/CT mark/NAT/affinity、7次续租及精确恢复通过；服务器确认上传{speeds}Mbps，较小切换仍未恢复B吞吐。**

见 [实际指标](../evidence/nss118-metrics.json)、[完整轮次](../evidence/nss118-trial.json)、[汇总](../evidence/nss118-mainline.json)、[上行](../evidence/nss118-uplink-proof.json)、[关闭](../evidence/nss118-endpoint-closure.json)、[终态](../evidence/nss118-final-audit.json)。

- UDP收/发{udp}、上下行RT drop0；B端点RTT p95约{m['phases'][1]['whole']['udp']['rttP95Ms']:.2f}ms，平均相邻RTT差约{m['phases'][1]['whole']['udp']['meanAbsoluteConsecutiveRttDeltaMs']:.3f}ms。上bulk drop{summary['bulkLeafDrop']}、parent overlimits+{trans['uplinkParentAndLeafClassDelta']['8e00:50']['overlimits']}，shaper实际工作；B上传四个5秒段仍约15–17Mbps。不能把softirq下降算同负载CPU收益，也不是真人CS2或300Mbps验收。
- 本地发送器按连接开始后的累计目标补发，B阻塞后A2实际超过32Mbps；目标是累计平均，非严格各段瞬时offer。服务端确认字节仍真实，此机制是对照负载问题，未证明它解释NSS B降速。下一步先只给发送器加有限信用上限，避免积累补发债务；原队列、RT负载和全部期限保持。之后若仍降速，再单独提高受控上行预算以区分拥塞/AQM与fast path，不同时修改。
- 新857项入口/9项本地边界检查，硬件六helper与116逐字节相同；不是重新安装分类器。单次checkpoint下载/SHA/gzip、独立100秒守护，端点180秒FW与210秒客户端全退出。最终source{final['queryAge']:.2f}、ECM关闭全零、无事务/stage/state/模块，两物理默认mq/fq_codel恢复。WAN4仍down，自然四路PBR不变。旧117 runtime及全部失败原字节保存，私有输入冻结，未提交凭据/CT/nonce/配置/checkpoint/二进制。
- 只推进受控单WAN主线，不扩第二WAN/共享全局预算/WiFi/autorate、不操作UI或新下载。真人留最后一次集中验收。夜间到10:00；09:50不新实验，完成清理、晨间报告与推送后暂停接续。
'''
for name,title in [('STATE.md','# 当前状态'),('PLAN.md','# 当前单WAN上传后续')]:
 p=repo/'docs'/name;p.write_text(title+'\n\n'+text+'\n## NSS117历史\n\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
p=repo/'docs/EXPERIMENT_LOG.md';head,tail=p.read_text(encoding='utf-8').split('\n',1);p.write_text(head+'\n\n## NSS118 · '+when+' · 32Mbps上传仍未稳定\n\n'+text+tail,encoding='utf-8')
p=repo/'AGENTS.md';head,tail=p.read_text(encoding='utf-8').split('\n',1);p.write_text(head+'\n\n最新NSS118：只改上传48→32，857项/9边界；单WAN1完整20秒A/B/A2、ECM0/2/0、四leaf/mark/NAT/affinity/7续租及恢复通过，确认上传'+speeds+'Mbps，UDP'+udp+'，RTdrop0、upbulk32/parent10573 overlimit；较小步幅未恢复B吞吐，不算CPU或真人收益。发送器会在阻塞后补发累计债务，A2超过目标，下一步只加信用上限，再必要时单独查上行预算，不同时改。原队列30/29/1、6/27/100期限和常驻68不动，终态4859/17139、source1.27、ECM全零、双mq/fq_codel恢复、端点关闭，WAN4仍down，旧117原字节保留。UI停用、不新下载/重装/扩WAN/WiFi/共享预算/autorate；09:50后收尾、10点前暂停本夜接续；STATE为准。\n\n'+tail,encoding='utf-8')
p=repo/'docs/ARTIFACT_INDEX.md';p.write_text('# 当前NSS118\n\n[上传](../evidence/nss118-metrics.json) · [轮次](../evidence/nss118-trial.json) · [汇总](../evidence/nss118-mainline.json) · [终态](../evidence/nss118-final-audit.json) · [历史117 runtime](../evidence/nss117-runtime.json)。\n\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
dump(r/'export-receipt.json',{'passed':True,'newSources':len(hashes),'totalSources':len(manifest['sources']),'uploadMbps':speeds,'privateArtifacts':len(frozen)});print(json.dumps({'exported':True,'sources':len(hashes),'totalSources':len(manifest['sources']),'uploadMbps':speeds}))
