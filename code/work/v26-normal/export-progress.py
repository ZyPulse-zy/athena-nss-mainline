"""Publish curated normal-app entry and honest five-flow prerequisite failures."""
from pathlib import Path
import copy
import hashlib
import json
import subprocess

w=Path(__file__).resolve().parents[2];r=w/'work/v26-normal';repo=w/'athena-nss-mainline'
base='bdae525fbbfedd479ddbefb814238369064d2b33'
read=lambda p:json.loads(p.read_text(encoding='utf8'));sha=lambda b:hashlib.sha256(b).hexdigest()
dump=lambda x:json.dumps(x,ensure_ascii=False,indent=2)+'\n'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()==base
assert not subprocess.check_output(['git','status','--porcelain'],cwd=repo)
progress=read(r/'progress-sanitized.json');appendix=read(r/'restoration-and-limits-appendix.json')
assert progress['passed'] and appendix['passed'] and not progress['fiveExactFlowNativeCandidate']['hardwareLoaded']
assert progress['normalEntry']['actualReadOnlyInspectionPassed'] and progress['normalEntry']['terminalCompleteAudit']['ecmClosedAndZero']
m=read(repo/'source-manifest.json');prefix=copy.deepcopy(m['sources']);assert len(prefix)==3572
hashes={}
def source(p,role):
    f=p.relative_to(w).as_posix();data=p.read_bytes();dst=repo/'code'/f;dst.parent.mkdir(parents=True,exist_ok=True)
    with dst.open('xb') as out:out.write(data)
    hashes[f]=sha(data);m['sources'].append({'path':'code/'+f,'workspaceSource':f,'sha256':sha(data),'bytes':len(data),'role':role})
for name in ['v21-fiveflow','v22-fiveflow','v23-fiveflow','v24-fiveflow','v25-normal','v26-normal']:
    for p in sorted((w/'work'/name).iterdir()):
        if p.is_file() and p.suffix in ['.mjs','.lua','.py','.ps1','.md'] and not any(x in p.name for x in ['private','credential','connect-router']):
            source(p,'normal-application-entry-and-five-flow-prerequisites')
endpoint=w/'work/v21-fiveflow/endpoint-gate'
for name in ['rp_ecm_gate_lab_ct.c','two_slot_predicate.h','ecm_ae_classifier_public.h','Makefile','control_harness.py','ct_harness.py','predicate_test.c','build_local.py']:
    source(endpoint/name,'five-slot-native-source-models-no-hardware-acceptance')
for folder in ['failed-control-v1','failed-control-v2']:
    for name in ['control_harness.py']:
        if (endpoint/folder/name).exists():source(endpoint/folder/name,'retained-failed-five-slot-local-model')
for name in ['prepare-v21-native.py','prepare-v22-five.py','prepare-v23-five.py','prepare-v24-serial.py','prepare-v25-normal.py','prepare-v26-normal.py','prepare-v23-analysis.py']:
    source(w/'work'/name,'preparation-sources-and-retained-copy-failures')
for version in ['v21-fiveflow','v22-fiveflow','v23-fiveflow','v24-fiveflow','v25-normal','v26-normal']:
    q=read(w/'work'/version/'entry-qualified.json')
    assert q['passed'] and not q['hardwareExecuted']
    for f,h in q['sourceManifest'].items():
        if f in hashes:assert hashes[f]==h,f
m['lastAppendExport']='V26_NORMAL_APP_ENTRY';(repo/'source-manifest.json').write_text(dump(m),encoding='utf8')
def evidence(name,value):
    with (repo/'evidence'/('v26-'+name+'.json')).open('x',encoding='utf8') as f:f.write(dump(value))
evidence('progress',progress);evidence('restoration-limits',appendix)
evidence('normal-entry-qualification',read(r/'entry-qualified.json'));evidence('normal-policy-models',read(r/'normal-policy-qualified.json'))
evidence('five-native-source-models',read(w/'work/v21-fiveflow/native-source-qualified.json'))
evidence('five-native-elf',read(w/'work/v21-fiveflow/runtime-elf-comparison.json'))
evidence('five-target-ram',read(w/'work/v21-fiveflow/native-qualified.json'))
evidence('five-native-entry-qualification',read(w/'work/v21-fiveflow/entry-qualified.json'))
evidence('fixture-serial-models',read(w/'work/v24-fiveflow/serial-model-qualified.json'))
localFailures={}
for folder,name in [('v22-fiveflow','failed-qualification-newlines-v1.json'),('v22-fiveflow','failed-qualification-copy-scope-v2.json'),('v25-normal','failed-import-summary.json'),('v26-normal','failed-sanitizer-codec.json')]:
    localFailures[folder+'/'+name]=read(w/'work'/folder/name)
evidence('retained-local-failures',localFailures)
evidence('source-proof',{'passed':True,'baseCommit':base,'historicPrefixSources':3572,
        'historicPrefixCanonicalSha256':sha(json.dumps(prefix,sort_keys=True,separators=(',',':')).encode()),
        'sourceHashes':hashes,'oldCodeAndEvidenceUnmodified':True,'binariesCredentialsRawCtAndCheckpointsExcluded':True})
head='''# 多 WAN 高级 QoS：受控硬件通过，正常流入口只读就绪

更新：2026-10-07北京时间05:10。已通过的范围仍以v20真实硬件为准：两TCP BULK＋一UDP RT跨两个或三个WAN、60秒/121帧/ECM3/20续租；上下行五WAN各18class、11leaf，DOWN18共享借用、UP60每WAN12硬上限，RT优先级0/FQ-CoDel。完整tag、ct mark、NAT、WAN affinity和恢复通过。该范围是受控有界原型，尚未长期常驻或覆盖所有正常连接。

新的正常流入口`v26-normal`直接接已有Steam、CS2 socket归属和自动分类，选择两个不同WAN的Steam BULK TCP＋一个已准入CS2 RT UDP；无造流、无启动游戏或下载。18选择/拒绝模型与46相对依赖检查通过，2586绑定；native/Lua/tag builder/QoS沿用v20确切字节。现场inspect为0游戏/0下载/0准入，无NSS写入。正常程序整合factory尚未硬件执行，不能用历史数据面替它宣布新入口或真人验收。

五槽native候选同内核编译、63控制/68CT模型、20运行节/675重定位逐项比对及14目标RAM检查通过，55872字节runtime SHA574ffbec…ceb7d4；尚未加载硬件。五流尝试共五次均在NSS前结束：首次自然配齐五WAN但客户端恢复余量不足；一次本地旧目录拒绝；三次自有SSH建连/轮换失败。v24最初四次依次握手成功，后续轮换仍超时，原因未定；不得归因NSS/固件、放宽准入或修改SSH/学校策略。所有端点/FW恢复，四个原客户端独立退出证明通过。

复制换行、错误复制qualifier、缺失本地依赖与sanitizer编码错误原始失败保留，分别更正后才继续。五槽初始78220/81331字节bundle超限原失败保持；现模型72868、guard8763、NFT46750，原9000/65536/73728/49152/1MiB、source6/kernel90最大120/owner180/client180均未放宽。压缩仅JSON数据，无损重构及完整guard分发等价已在目标RAM验证。

04:55完整终态audit source0.95：保护配置不变、五WAN健康、ECM关闭全零；无实验gate，两物理原mq＋四fq_codel。常驻分类器NSS68/config581b5d46…c791d7保持。没有新增CPU因果、300Mbps/长期或真人体验声明。历史CPU证据继续复用；五WAN同时加速不算已通过。

本轮剩余：封存/推送/实际Git archive读回，07:40最后只读终态核验和晨间报告，08:00前暂停heartbeat。无新的五流实验，除非有明确的新可执行前提；不重新开Steam/CS2或下载。下一正常使用时只需一次新整合入口会话，检查实际体验；长期连续新代、五流fixture和扩大加速池进入后续。

证据：[进度和失败](../evidence/v26-progress.json)、[独立客户端和尺寸](../evidence/v26-restoration-limits.json)、[正常入口资格](../evidence/v26-normal-entry-qualification.json)、[五槽源码模型](../evidence/v26-five-native-source-models.json)、[目标RAM](../evidence/v26-five-target-ram.json)、[源码](../evidence/v26-source-proof.json)。[入口说明](../code/work/v26-normal/README.md)。

## 保留的五WAN队列硬件证明

'''
for name in ['AGENTS.md','docs/STATE.md','docs/PLAN.md','docs/EXPERIMENT_LOG.md']:
    p=repo/name; text=head.replace('../evidence/','evidence/').replace('../code/','code/') if name=='AGENTS.md' else head
    p.write_text(text+p.read_text(encoding='utf8'),encoding='utf8')
detail='''# 多 WAN NSS 与高级 QoS的实际边界

| 能力 | 当前证据 |
|---|---|
| 同时加速跨WAN的两TCP BULK＋一UDP RT | v16、v19、v20实际60秒；ECM3和恢复通过 |
| 五WAN上下行RT/BULK队列映射 | v20实际完整建立/读取，十个类别leaf加default950 |
| 共享下行预算与空闲份额借用 | DOWN30→18响应、保障/ceil分离；v19/v20实测借用 |
| RT优先级与FQ-CoDel | RT保障1Mbps、prio0，BULK prio1，target5ms/interval100ms/1024流；B内自有echo全返回，RTleaf drop0 |
| PBR/NAT/完整ct mark/WAN粘性 | Linux决定新连接；已选CT/快路径保持原出口，六tag实际命中 |
| 正常Steam和CS2自动进入新的多WAN入口 | v26实现18模型、46导入检查和现场只读0流；新整合NSSfactory尚未硬件运行 |
| 五条不同WAN flow同时NSS | 仅五槽编译/离线模型；所有尝试在NSS前拒绝，未加载硬件 |
| 全网/长期常驻、所有连接主要由NSS QoS处理 | 尚未交付；当前只选三条精确CT，其余软件fallback |

上行总60Mbps、每WAN12Mbps硬上限；下行共享18Mbps、每WAN保障3Mbps可借用至18Mbps。五WAN保障合15Mbps，剩余3Mbps属于共同父预算余量。default950保障未加速物理fallback；其软件路径原IFB/CAKE继续存在。

NSS用分层预算、RT/BULK优先级与每leaf FQ-CoDel替代这部分关键QoS。它没有复刻CAKE的NAT后host公平、diffserv4四tin、COBALT或autorate；用户已明确多人公平性不必要。target5ms是配置值，不是整个互联网连接的RTT保证。自有echo不是CS2的jitter/loss/Miss；新范围未增加CPU因果证明，旧NSS128的同负载softirq收益继续成立。

## 后续明确范围

1. 用户正常玩CS2和下载时，运行一次v26新整合有界入口，保留实际游戏体验与恢复；不用再下载游戏制造负载。
2. 五槽候选的现场前提：先解决四个自有SSH流建连/轮换的独立fixture问题。当前根因未知、不是已确认NSS故障，不能靠改学校或SSH策略解决。
3. 扩大精确加速池、连续新代和长期启停。当前三CT耦合旧代中任一flow改类/退出会结束该代并恢复；禁止直接更改已加速tag。
4. 普通共享预算、Wi-Fi、autorate、ECN全面验证及极端生命周期故障留后续；不影响本轮已成立的受控跨WAN原型。

截至08:00的夜间授权在07:40进入最终恢复核验、07:50禁止新实验，完成报告和推送后暂停自动化。任何未来生产会话仍需新checkpoint和控制连接外独立恢复。
'''
with (repo/'docs/MULTI_WAN_QOS.md').open('x',encoding='utf8') as f:f.write(detail)
checker=repo/'tools/check_repository.py';s=checker.read_text(encoding='utf8')
s=s.replace("'V20_FIVE_QUEUE_MAP']","'V20_FIVE_QUEUE_MAP','V26_NORMAL_APP_ENTRY']")
s=s.replace("if manifest['lastAppendExport']=='V20_FIVE_QUEUE_MAP':","if manifest['lastAppendExport'] in ['V20_FIVE_QUEUE_MAP','V26_NORMAL_APP_ENTRY']:")
needle="print(json.dumps({'passed':True,'filesChecked':count";assert s.count(needle)==1
extra="""if manifest['lastAppendExport']=='V26_NORMAL_APP_ENTRY':
 p=json.loads((root/'evidence/v26-progress.json').read_text(encoding='utf8'));a=json.loads((root/'evidence/v26-restoration-limits.json').read_text(encoding='utf8'));q=json.loads((root/'evidence/v26-normal-entry-qualification.json').read_text(encoding='utf8'));s=json.loads((root/'evidence/v26-source-proof.json').read_text(encoding='utf8'))
 assert p['passed'] and len(p['failedFiveFlowPrerequisites'])==5 and all(not x['passed'] and not x['productionNssWrites'] and x['noCheckpointOrNativeStageStarted'] for x in p['failedFiveFlowPrerequisites'])
 assert p['fiveWanConcurrentAccelerationNotClaimed'] and not p['fiveExactFlowNativeCandidate']['hardwareLoaded'] and not p['fiveExactFlowNativeCandidate']['hardwareAcceptance']
 assert p['normalEntry']['actualReadOnlyInspectionPassed'] and p['normalEntry']['actualCs2RtCandidates']==p['normalEntry']['actualSteamBulkCandidates']==0 and not p['normalEntry']['normalApplicationFactoryHardwareAcceptance'] and not p['normalEntry']['humanGameAcceptance'] and not p['normalEntry']['permanentNssDeployment']
 assert q['passed'] and q['selectorModels']==18 and q['relativeDependenciesExist']==46 and not q['hardwareExecuted'] and not q['wholeFactoryModeled']
 assert p['normalEntry']['terminalCompleteAudit']['ecmClosedAndZero'] and p['normalEntry']['twoPhysicalRoots']['passed'] and a['passed'] and len(a['exactClientClosures'])==4
 assert s['historicPrefixSources']==3572 and s['oldCodeAndEvidenceUnmodified'] and s['binariesCredentialsRawCtAndCheckpointsExcluded'] and s['historicPrefixCanonicalSha256']==hashlib.sha256(json.dumps(manifest['sources'][:3572],sort_keys=True,separators=(',',':')).encode()).hexdigest()
 for f,h in s['sourceHashes'].items():assert hashlib.sha256((root/'code'/f).read_bytes()).hexdigest()==h,f
"""
checker.write_text(s.replace(needle,extra+needle),encoding='utf8')
with (repo/'.gitattributes').open('a',encoding='utf8') as f:
    for version in ['v21-fiveflow','v22-fiveflow','v23-fiveflow','v24-fiveflow','v25-normal','v26-normal']:
        f.write(f'\n/code/work/{version}/fast-path.lua whitespace=cr-at-eol,-blank-at-eol\n')
        if (repo/'code/work'/version/'endpoint-firewall-guardian.py').exists():f.write(f'/code/work/{version}/endpoint-firewall-guardian.py whitespace=cr-at-eol,-blank-at-eof\n')
print(dump({'passed':True,'newSources':len(hashes),'totalSources':len(m['sources']),'fiveFlowHardwareLoaded':False,'normalReadonlyOnly':True}))
