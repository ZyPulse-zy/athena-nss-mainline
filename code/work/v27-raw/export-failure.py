"""Publish the retained raw-TCP prerequisite refusal and exact closure evidence."""
from pathlib import Path
import copy,hashlib,json,subprocess
w=Path(__file__).resolve().parents[2];r=w/'work/v27-raw';repo=w/'athena-nss-mainline';base='4975bccfa2763339d2635703f8956cbd70aae3ba'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda b:hashlib.sha256(b).hexdigest();dump=lambda x:json.dumps(x,ensure_ascii=False,indent=2)+'\n'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()==base and not subprocess.check_output(['git','status','--porcelain'],cwd=repo)
pilots=sorted(r.glob('pilot-aba-*'));assert len(pilots)==1;pilot=pilots[0]
loads=sorted(r.glob('load-*'));assert len(loads)==1;load=loads[0]
trial=read(pilot/'automatic-result.json');events=read(pilot/'driver-private.json');client=read(load/'result-private.json');guard=read(load/'guard-result-private.json');closure=read(load/'endpoint-retry-closure.json');audit=read(r/'terminal-after-raw-audit.json');physical=read(r/'terminal-physical-summary.json');q=read(r/'entry-qualified.json');models=read(r/'raw-model-qualified.json')
assert not trial['passed'] and 'wait-four-raw.mjs failed' in trial['error'] and len(events)==4
assert not (pilot/'detached-owner-reference-private.json').exists() and not (pilot/'case-reference-private.json').exists()
assert client['tcpBytes']==0 and client['errors']==['Error: Owned raw first-byte deadline tcp'] and 8<=client['seconds']<9
assert all(guard[k] for k in ['passed','clientExitedBeforeDeadline','exactClientOnly']) and all(closure[k] for k in ['passed','baselineRestored','exactOwnedEndpointClosed']) and closure['ownedRulesRemaining']==0
assert audit['passed'] and audit['ecmClosedAndZero'] and audit['allFiveHealthyWanBaseline'] and physical['passed'] and q['passed'] and models['passed']
diagnostic=read(load/'firstbyte-diagnostic-v2-raw-private.json');assert diagnostic['code']==0
counters=json.loads(diagnostic['stdout'].splitlines()[0])['ownedRuleCounters'];assert [x['counters'][0]['packets'] for x in counters if x['protocol']=='tcp']==[0]
data={'passed':True,'prerequisiteTestPassed':False,'originalControllerFailurePreserved':True,'productionNssWrites':False,'checkpointOrNativeStageStarted':False,'fiveSlotModuleHardwareLoaded':False,'fiveWanConcurrentFastPathProven':False,'sourceBindings':2761,'onlyOwnFixtureTransportChanged':True,'nativeAndQosByteEquivalentToV24':True,'localActualSenderChecks':10,'localProtocolModels':33,'client':{'seconds':client['seconds'],'tcpPayloadBytes':0,'error':client['errors'][0],'udpWholeShortClientWindow':{'sent':client['udpSent'],'returned':client['udpReceived'],'nssQualityMetric':False}},'endpointReadOnly':{'serviceReadySeen':True,'unhandledExceptionSeen':False,'ownedRuleCounters':counters,'tcpSourceOrPathCauseDetermined':False,'firstControlSshTimedOutThenReadOnlyRetrySucceeded':True},'exactClientClosure':guard,'exactEndpointClosure':closure,'terminalCompleteAudit':audit,'terminalPhysicalRoots':physical,'firstDiagnosticSyntaxFailureRetained':True,'firstDiagnosticRanNetworkTools':False,'noFirmwareFaultOrNewCpuOrHumanAcceptanceClaim':True}
m=read(repo/'source-manifest.json');prefix=copy.deepcopy(m['sources']);assert len(prefix)==3801;hashes={}
for p in [w/'work/prepare-v27-raw.py',*sorted(r.iterdir())]:
    if not p.is_file() or p.suffix not in ['.mjs','.lua','.py','.ps1','.md'] or any(x in p.name for x in ['private','credential','connect-router']):continue
    f=p.relative_to(w).as_posix();b=p.read_bytes();dst=repo/'code'/f;dst.parent.mkdir(parents=True,exist_ok=True)
    with dst.open('xb')as out:out.write(b)
    hashes[f]=sha(b);m['sources'].append({'path':'code/'+f,'workspaceSource':f,'sha256':sha(b),'bytes':len(b),'role':'retained-owned-raw-fixture-prerequisite-refusal'})
for f,h in q['sourceManifest'].items():assert hashes[f]==h,f
def evidence(name,v):
    with (repo/'evidence'/('v27-'+name+'.json')).open('x',encoding='utf8')as f:f.write(dump(v))
evidence('raw-prerequisite',data);evidence('entry-qualification',q);evidence('raw-models',models)
evidence('source-proof',{'passed':True,'baseCommit':base,'historicPrefixSources':3801,'historicPrefixCanonicalSha256':sha(json.dumps(prefix,sort_keys=True,separators=(',',':')).encode()),'sourceHashes':hashes,'oldEvidenceAndSourcesUnmodified':True,'rawCtNonceConfigsCheckpointsAndBinariesExcluded':True})
m['lastAppendExport']='V27_OWN_RAW_PREREQUISITE';(repo/'source-manifest.json').write_text(dump(m),encoding='utf8')
head='''# 多 WAN高级QoS受控通过；五流新负载在NSS前拒绝

更新：2026-10-07北京时间05:20。v20三流跨WAN和五WAN队列/共享借用硬件结论保持；v26正常Steam/CS2入口已发布并实际archive校验4975bcc。正常整合factory仍仅只读0流，五WAN同时加速和长期常驻未验。

v27唯一改动为四条自有SSH bulk数据连接改成nonce认证raw TCP，固定小UDP/总32Mbps/合64KiB credit/client180及独立210退出保持；五槽native、数据面Lua、PBR/tag/队列/180秒owner与独立恢复均不变。实际sender本地socket10检查、33协议模型、2761绑定通过。现场首TCP约8.008秒首包超时、payload0，NSS stage/checkpoint/模块/放行均未开始；不能归因NSS/固件。旧SSH失败、首次只读诊断语法错误和实际失败保留。

只读端点核查服务就绪、无未处理异常，精确TCP放行规则packet0、UDP规则packet1；控制SSH也曾超时后恢复。不能区分TCP路径与外部源地址差异，根因未定。独立防火墙到期后原canonical基线一致、规则0、精确端点关闭；客户端原实例独立退出通过。05:19完整终态audit source1.00、五WAN健康/保护配置不变/ECM关闭全零、两物理原mq＋四fq_codel、无实验gate。

不盲重试五流或放宽源过滤/期限/认证。睡眠期间无桌面、游戏下载或认证操作。已成立的多WAN原型是两TCP BULK＋一UDP RT、DOWN18共享借用和UP60每WAN12硬上限、RT优先级0/FQ-CoDel；新的普通程序入口一次正常会话和长期连续代列为未验。剩余夜间整理报告并保持安静，07:40做最后完整健康/恢复/端点/客户端核验，07:50不新开实验，08:00前保存推送并暂停heartbeat。

证据：[原生TCP前提与恢复](../evidence/v27-raw-prerequisite.json)、[资格](../evidence/v27-entry-qualification.json)、[本地实际sender与模型](../evidence/v27-raw-models.json)、[源码](../evidence/v27-source-proof.json)。[负载说明](../code/work/v27-raw/README.md)。

## 保留的正常入口与历史硬件证明

'''
for name in ['AGENTS.md','docs/STATE.md','docs/PLAN.md','docs/EXPERIMENT_LOG.md']:
    p=repo/name;new=head.replace('../evidence/','evidence/').replace('../code/','code/')if name=='AGENTS.md'else head;p.write_text(new+p.read_text(encoding='utf8'),encoding='utf8')
p=repo/'docs/MULTI_WAN_QOS.md';s=p.read_text(encoding='utf8');s=s.replace('先解决四个自有SSH流建连/轮换的独立fixture问题。','先解决自有TCP端点可达性的独立fixture问题；SSH版本和nonce认证raw TCP版本均在NSS前失败。');p.write_text(s,encoding='utf8')
p=repo/'tools/check_repository.py';s=p.read_text(encoding='utf8').replace("'V26_NORMAL_APP_ENTRY']","'V26_NORMAL_APP_ENTRY','V27_OWN_RAW_PREREQUISITE']").replace("if manifest['lastAppendExport']=='V26_NORMAL_APP_ENTRY':","if manifest['lastAppendExport'] in ['V26_NORMAL_APP_ENTRY','V27_OWN_RAW_PREREQUISITE']:")
needle="print(json.dumps({'passed':True,'filesChecked':count";assert s.count(needle)==1
extra="""if manifest['lastAppendExport']=='V27_OWN_RAW_PREREQUISITE':
 h=json.loads((root/'evidence/v27-raw-prerequisite.json').read_text(encoding='utf8'));q=json.loads((root/'evidence/v27-entry-qualification.json').read_text(encoding='utf8'));p=json.loads((root/'evidence/v27-source-proof.json').read_text(encoding='utf8'))
 assert h['passed'] and not h['prerequisiteTestPassed'] and h['originalControllerFailurePreserved'] and not any(h[k] for k in ['productionNssWrites','checkpointOrNativeStageStarted','fiveSlotModuleHardwareLoaded','fiveWanConcurrentFastPathProven'])
 assert h['client']['tcpPayloadBytes']==0 and 8<=h['client']['seconds']<9 and h['sourceBindings']==2761 and q['passed'] and q['nativeAndQosByteEquivalent'] and not q['fiveSlotHardwareExecuted']
 assert h['localActualSenderChecks']==10 and h['localProtocolModels']==33 and all(h['exactClientClosure'][k] for k in ['passed','clientExitedBeforeDeadline','exactClientOnly']) and h['exactEndpointClosure']['passed'] and h['terminalCompleteAudit']['ecmClosedAndZero'] and h['terminalPhysicalRoots']['passed']
 assert p['historicPrefixSources']==3801 and p['oldEvidenceAndSourcesUnmodified'] and p['historicPrefixCanonicalSha256']==hashlib.sha256(json.dumps(manifest['sources'][:3801],sort_keys=True,separators=(',',':')).encode()).hexdigest()
 for f,d in p['sourceHashes'].items():assert hashlib.sha256((root/'code'/f).read_bytes()).hexdigest()==d,f
"""
p.write_text(s.replace(needle,extra+needle),encoding='utf8')
with (repo/'.gitattributes').open('a',encoding='utf8')as f:f.write('\n/code/work/v27-raw/fast-path.lua whitespace=cr-at-eol,-blank-at-eol\n/code/work/v27-raw/endpoint-firewall-guardian.py whitespace=cr-at-eol,-blank-at-eof\n')
print(json.dumps({'passed':True,'newSources':len(hashes),'totalSources':len(m['sources']),'fiveSlotHardwareLoaded':False,'endpointAndClientRestored':True}))
