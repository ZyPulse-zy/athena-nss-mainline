"""Curated overnight delivery. Old public evidence and private inputs stay intact."""
from pathlib import Path
import argparse,copy,hashlib,json,subprocess

p=argparse.ArgumentParser();p.add_argument('--pilot',required=True);a=p.parse_args()
w=Path(__file__).resolve().parents[2];repo=w/'athena-nss-mainline';pilot=w/a.pilot
base='04408b25209f1cb3bef5a6470460b4a13c7afbb4'
read=lambda x:json.loads(x.read_text(encoding='utf-8'))
sha=lambda x:hashlib.sha256(x).hexdigest()
dump=lambda x:json.dumps(x,ensure_ascii=False,indent=2)+'\n'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()==base
assert not subprocess.check_output(['git','status','--porcelain'],cwd=repo)
assert (pilot/'automatic-result.json').exists(),'Wait for actual controller result'
actual=read(pilot/'automatic-result.json');bindings=read(pilot/'actual-entry-bindings.json')
for f,d in bindings.items():assert sha((w/f).read_bytes())==d,f
manifest=read(repo/'source-manifest.json');prefix=copy.deepcopy(manifest['sources']);assert len(prefix)==2825
old_paths={x['path'] for x in prefix};sources={}
for f in bindings:
 src=w/f
 if src.suffix not in ['.mjs','.lua','.py','.ps1','.c','.h'] or any(x in src.name for x in ['connect-router','private','credential']):continue
 target='code/'+f
 if target in old_paths:
  assert (repo/target).read_bytes()==src.read_bytes(),f
  continue
 sources[f]=src
for f in ['work/v13-two/export-night.py','work/v13-two/verify-night-archive.py','work/v13-two/read-probe-identity.mjs','work/v13/qualify-pin.py','work/v13/endpoint-gate/build_local.py','work/v13/endpoint-gate/control_harness.py','work/v13/endpoint-gate/ct_harness.py','work/v13/endpoint-gate/predicate_test.c','work/v13/endpoint-gate/two_slot_predicate.h','work/v13/endpoint-gate/ecm_ae_classifier_public.h']:
 assert 'code/'+f not in old_paths;sources[f]=w/f
for src in (w/'work/v13-two').iterdir():
 if src.is_file() and src.suffix in ['.mjs','.lua','.py','.ps1','.c','.h'] and not any(x in src.name for x in ['connect-router','private','credential']):sources[src.relative_to(w).as_posix()]=src
source_hashes={}
for f,src in sorted(sources.items()):
 data=src.read_bytes();target='code/'+f;dest=repo/target;dest.parent.mkdir(parents=True,exist_ok=True)
 with dest.open('xb') as out:out.write(data)
 digest=sha(data);manifest['sources'].append({'path':target,'workspaceSource':f,'sha256':digest,'bytes':len(data),'role':'v13-two-wan-night-candidate-and-preserved-failed-entries'})
 source_hashes[f]=digest
manifest['lastAppendExport']='V13_TWO_WAN_NIGHT';(repo/'source-manifest.json').write_text(dump(manifest),encoding='utf-8')
def evidence(name,data):
 with (repo/'evidence'/('v13-night-'+name+'.json')).open('x',encoding='utf-8') as out:out.write(dump(data))
q=read(w/'work/v13-two/entry-qualified-v6.json');native=read(w/'work/v13-two/native-qualified.json');pin=read(w/'work/v13/pin-qualified.json');elf=read(w/'work/v13/runtime-elf-comparison.json')
assert q['passed'] and pin['passed'] and elf['passed'] and native['passed']
qualification={'passed':True,'actualBoundInputs':len(bindings),'sourceFreshnessSeconds':6,'actualControllerSessionSeconds':27,'nssPhaseSeconds':20,'independentOwnerSeconds':100,'clientHardSeconds':180,'twoExactSlotsOnly':True,'distinctNaturalWansRequired':True,'kernelSessionMaximumSeconds':120,'compiledRuntimeBytes':38512,'compiledRuntimeSha256':elf['runtimeSha256'],'actualExtractedPinConditions':pin['checks'],'wanHelperBackendMockedCases':2,'localTwentySecondTimingCases':1,'wholeFactoryModeled':False,'modelsNotHardwareProof':True,'payloadCapBytes':73728,'guardianExecCapBytes':9000,'recordCapBytes':1048576,'linuxPbrStillSelectsNewFlows':True,'completePerFlowMarkNatAndKernelCtPinsRetained':True,'nativeGateInstalledPermanently':False}
evidence('qualification',qualification)
hardware={'passed':bool(actual['passed']),'actualHardwareNssSessionCompleted':bool(actual['passed']),'humanGameAcceptance':False,'sameLoadCpuBenefitClaim':False,'permanentNssDeployment':False,'allFiveWanSimultaneousAcceptance':False,'controllerResultSha256':sha((pilot/'automatic-result.json').read_bytes())}
load=read(w/'work/v13-two/load-latest-private.json');closure=w/load['dir']/'endpoint-retry-closure.json'
if closure.exists():
 hardware['endpointFinalClosure']=read(closure);hardware['originalEndpointReadTimeoutRetained']=True
case=None
if (pilot/'case-reference-private.json').exists():case=w/read(pilot/'case-reference-private.json')['dir']
elif (pilot/'detached-owner-reference-private.json').exists():case=w/read(pilot/'detached-owner-reference-private.json')['caseDir']
if case:
 result=read(case/'result.json');hardware['actualControllerResultPassed']=result['passed']
 if (case/'baseline-audit.json').exists():hardware['finalScopedBaselineAudit']=read(case/'baseline-audit.json')
 if (case/'last-record-private.json').exists():
  rec=read(case/'last-record-private.json');hardware.update({'phaseSeconds':[x['seconds'] for x in rec.get('phases',[])],'renewals':len(rec.get('renewals',[])),'automaticLifecycleCompleted':rec.get('automaticLifecycleEpochCompleted',False),'actualWanNumbers':[x['wan'] for x in rec.get('wanBefore',[])],'allSuccessfulRestorationFlags':{k:rec.get(k) for k in ['moduleUnloaded','tagsRemoved','dualPhysicalQueuesRestored','wanRestored','mwan3Restored','stateNodeRemoved']}})
 if (case/'actual-accelerated-state-proof.json').exists():hardware['ecmAndTagsProof']=read(case/'actual-accelerated-state-proof.json')
evidence('hardware',hardware)
failures=[
 {'label':'initial endpoint transport','productionNssStarted':False,'reason':'SSH connection timeouts before firewall/client/router admission; exact endpoint closure retained'},
 {'label':'raw TCP and SSH2 upload fixture','productionNssStarted':False,'reason':'Zero confirmed application bytes and reset or keepalive termination; not attributed to NSS'},
 {'label':'native child timestamp','productionNssStarted':False,'reason':'UTC versus local-time comparison; corrected using UTC on both sides'},
 {'label':'historical WAN4 exclusion','productionNssStarted':False,'reason':'Old helper rejected currently healthy WAN4; new current full five-WAN audit required'},
 {'label':'single-WAN natural matching','productionNssStarted':False,'reason':'Eight own TCP candidates did not match fixed UDP WAN; no PBR/mark changes'},
 {'label':'first two-WAN controller','productionNssStarted':False,'reason':'Unspaced import retained old class helper; checkpoint/stage not reached'},
 {'label':'peer discovery','productionNssStarted':False,'reason':'No authenticated probe observed; bounded same-port retry added, old failure retained'},
 {'label':'actual parent link format','productionNssStarted':False,'reason':'Actual ip JSON has link=wan and no link_index; strict parent name/ifindex/MAC check corrected before checkpoint'},
 {'label':'post-checkpoint legacy refinement','productionNssStarted':False,'reason':'Unspaced import retained old same-WAN refinement; checkpoint was created but stage and ECM not reached; actual distinct-WAN input and eight immutable-change refusals checked in corrected helper'},
 {'label':'WAN4 endpoint UDP probe','productionNssStarted':False,'reason':'Actual software conntrack WAN4/proxy-bit clear/original packets30/reply0; endpoint capture empty before NSS, endpoint-specific WAN4 path not attributed to NSS'},
 {'label':'owned data SSH short keepalive','productionNssStarted':False,'reason':'About 11 MB received then 3-second keepalive termination; only data keepalive disabled with all hard deadlines retained'},
 {'label':'successful router pilot endpoint read timeout','productionNssStarted':True,'routerFunctionalResultPassed':True,'reason':'First closure SSH read timed out after router restored; independent expiry and new exact persistent-transport closure verified zero owned rules and original firewall baseline; original timeout retained'},
 {'label':'modeled payload and namespace','productionNssStarted':False,'reason':'73728-byte refusal and namespace typo preserved; corrected candidate separately qualified'}]
for x in failures:x['originalEvidenceRetainedLocally']=True
if not actual['passed']:failures.append({'label':'latest actual pilot','productionNssCompletionClaimed':False,'reason':actual.get('error'),'originalEvidenceRetainedLocally':True})
evidence('failures',failures)
proof={'passed':True,'baseCommit':base,'historicPrefixSources':len(prefix),'historicPrefixCanonicalSha256':sha(json.dumps(prefix,sort_keys=True,separators=(',',':')).encode()),'sourceHashes':source_hashes,'oldV1AndV11CodeEvidenceUnchanged':True,'privateCtNonceCredentialsConfigCheckpointsAndBinariesExcluded':True,'actualBindingInputsVerified':len(bindings)}
evidence('source-proof',proof)
main={'version':'v1.2 overnight multi-WAN candidate','userAuthorizedExpansion':True,'authorizedDeadlineBeijing':'2026-10-07 08:00','actualHardwareTwoWanCompletion':bool(actual['passed']),'v1TechnicalEvidenceReusedAndFrozen':True,'strictHumanV1ExperienceStillUnverified':True,'oneTcpBulkOneUdpRtOnly':True,'linuxPbrAndConnectionAffinityPreserved':True,'sharedPhysicalNssLeaves':{'upMbps':60,'upBulkMbps':59,'upRtMbps':1,'downMbps':30,'downBulkMbps':29,'downRtMbps':1,'unselectedFallbackMbps':950},'advancedQosImplementedBeforeThisNight':['bidirectional bulk and RT tags','HTB subgroup budgets','four FQ-CoDel leaves'],'advancedQosNotYetProven':['independent per-WAN NSS bandwidth budgets','simultaneous multiple bulk flows','five-WAN acceleration','continuous sessions','ECN full validation'],'sleepingUserDesktopNotOperated':True,'heartbeatResumedUntilDeadline':True,'next':'Complete two-WAN hardware proof, extend bounded session, then implement shared or per-WAN QoS mapping with actual runtime support'}
evidence('mainline',main)
title='双 WAN NSS 硬件闭环通过' if actual['passed'] else '多 WAN／高级 QoS 夜间推进中'
status='一条真实受控 TCP BULK 与一条 UDP RT 在两个自然 WAN 完成约20秒 NSS 与恢复。' if actual['passed'] else '双 WAN gate／控制器已实现、编译并局部验证；当前现场失败与未验边界如下，不声称硬件通过。'
text=f'''# {title}

用户最新授权：自主推进到2026-10-07北京时间08:00，目标扩展为多 WAN 与高级 QoS。旧 v1 冻结及停止扩展的计划属于历史；其技术证据继续复用，真人体感未验仍保留。

**{status}** 实际生产范围仍只两条精确连接：一 TCP BULK＋一 UDP RT，自然分属两个健康 WAN；Linux 继续决定新连接 PBR，NSS 不重做负载均衡。完整 ct mark、NAT、WAN affinity 与 kernel CT pin 保留，未知流默认拒绝。

已完成：新 gate 在原 Linux6.18.44 SDK 编译，15个实际 C 准入条件检查通过；独立两 WAN 模式 helper 的正常及第二步失败恢复模型通过。实际 `ip` 只返回 `link:wan`，已按真实格式核验接口 index/MAC/父接口名；历史 WAN4 排除与旧 import 失败保留。原生 OpenSSH 32Mbps 下载已实际收包，负载专用短保活已关闭，180/185/210秒硬截止保留。模型不能代替硬件。

当前会话沿用20秒 B／27秒 kernel／100秒独立回滚／6秒分类来源，源与实际输入共{len(bindings)}项绑定。每次生产写前新 checkpoint 下载 SHA/gzip 与控制连接外独立恢复核验，保护五路认证/PBR/sing-box/Tailscale和十 CAKE fallback。没有桌面/Steam/CS2操作、购买或新游戏下载，没有认证请求、固件/内核/分区修改。

QoS 当前是两物理口上的共享 bulk/RT HTB＋四 FQ-CoDel leaf，UP60（59/1）／DOWN30（29/1），未准入流 fallback950。还不能称为各 WAN 独立预算、五路同时加速或常驻服务。下一步顺序：双 WAN 实测 → 延长有界会话 → 可实现的共享／每 WAN预算和高级分类，不重复旧 CPU 门槛或 NSS159 gap。

07:40最终恢复/审核/报告，07:50不新开生产，08:00前暂停 heartbeat。失败原证据保留；新源码与脱敏证据按白名单发布，完整 CT/nonce/凭据/config/checkpoint/二进制只本地。

证据：[当前主线](../evidence/v13-night-mainline.json)、[硬件结果](../evidence/v13-night-hardware.json)、[资格范围](../evidence/v13-night-qualification.json)、[保留失败](../evidence/v13-night-failures.json)、[源校验](../evidence/v13-night-source-proof.json)。入口：[双 WAN 有界控制器](../code/work/v13-two/pilot-supervisor-v6.mjs)。

## v1.1及更早历史

'''
for f in ['docs/STATE.md','docs/PLAN.md','docs/EXPERIMENT_LOG.md','AGENTS.md']:
 target=repo/f;head=text if f!='AGENTS.md' else text.replace('../evidence/','evidence/').replace('../code/','code/')
 target.write_text(head+target.read_text(encoding='utf-8'),encoding='utf-8')
checker=repo/'tools/check_repository.py';s=checker.read_text(encoding='utf-8')
s=s.replace("'V11_BOUNDED_ENTRY']","'V11_BOUNDED_ENTRY','V13_TWO_WAN_NIGHT']")
s=s.replace("if manifest['lastAppendExport']=='V11_BOUNDED_ENTRY':","if manifest['lastAppendExport'] in ['V11_BOUNDED_ENTRY','V13_TWO_WAN_NIGHT']:")
end="print(json.dumps({'passed':True,'filesChecked':count";assert s.count(end)==1
extra="""if manifest['lastAppendExport']=='V13_TWO_WAN_NIGHT':
 night=json.loads((root/'evidence/v13-night-mainline.json').read_text(encoding='utf-8'))
 np=json.loads((root/'evidence/v13-night-source-proof.json').read_text(encoding='utf-8'))
 nq=json.loads((root/'evidence/v13-night-qualification.json').read_text(encoding='utf-8'))
 nh=json.loads((root/'evidence/v13-night-hardware.json').read_text(encoding='utf-8'))
 assert night['userAuthorizedExpansion'] and night['oneTcpBulkOneUdpRtOnly'] and night['linuxPbrAndConnectionAffinityPreserved']
 assert np['passed'] and np['historicPrefixSources']==2825 and np['oldV1AndV11CodeEvidenceUnchanged']
 assert np['historicPrefixCanonicalSha256']==hashlib.sha256(json.dumps(manifest['sources'][:2825],sort_keys=True,separators=(',',':')).encode()).hexdigest()
 assert nq['passed'] and nq['twoExactSlotsOnly'] and nq['distinctNaturalWansRequired'] and nq['sourceFreshnessSeconds']==6
 assert not nh['humanGameAcceptance'] and not nh['sameLoadCpuBenefitClaim'] and not nh['permanentNssDeployment']
 assert night['actualHardwareTwoWanCompletion']==nh['actualHardwareNssSessionCompleted']
 for src,digest in np['sourceHashes'].items():assert hashlib.sha256((root/'code'/src).read_bytes()).hexdigest()==digest,src
"""
checker.write_text(s.replace(end,extra+end),encoding='utf-8')
(repo/'tools/verify_night_archive.py').write_bytes((w/'work/v13-two/verify-night-archive.py').read_bytes())
print(dump({'passed':True,'newSources':len(source_hashes),'sources':len(manifest['sources']),'hardwareCompleted':actual['passed']}))
