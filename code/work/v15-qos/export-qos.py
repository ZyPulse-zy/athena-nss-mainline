"""Append the actual two-WAN class/QoS delivery, keeping all prior bytes."""
from pathlib import Path
import copy,hashlib,json,subprocess
w=Path(__file__).resolve().parents[2];root=w/'work/v15-qos';repo=w/'athena-nss-mainline'
base='713419bce572c591aae541066c76019fc9cf87de'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda b:hashlib.sha256(b).hexdigest()
dump=lambda d:json.dumps(d,ensure_ascii=False,indent=2)+'\n'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()==base
assert not subprocess.check_output(['git','status','--porcelain'],cwd=repo)
h=read(root/'hardware-descriptive.json');q=read(root/'entry-qualified.json');n=read(root/'native-qualified.json')
assert h['passed'] and h['actualHardware'] and q['passed'] and n['passed']
m=read(repo/'source-manifest.json');prefix=copy.deepcopy(m['sources']);assert len(prefix)==3346
hashes={}
for src in sorted(root.iterdir()):
 if not src.is_file() or src.suffix not in ['.mjs','.lua','.py','.ps1','.c','.h'] or any(v in src.name for v in ['private','credential','connect-router']):continue
 f=src.relative_to(w).as_posix();data=src.read_bytes();out=repo/'code'/f;out.parent.mkdir(parents=True,exist_ok=True)
 with out.open('xb') as x:x.write(data)
 hashes[f]=sha(data);m['sources'].append({'path':'code/'+f,'workspaceSource':f,'sha256':sha(data),'bytes':len(data),'role':'v15-actual-wan-class-tags-and-budgets'})
for f,d in q['sourceManifest'].items():
 if f in hashes:assert hashes[f]==d
m['lastAppendExport']='V15_WAN_CLASS_QOS';(repo/'source-manifest.json').write_text(dump(m),encoding='utf-8')
def evidence(name,data):
 with (repo/'evidence'/('v15-qos-'+name+'.json')).open('x',encoding='utf-8') as f:f.write(dump(data))
evidence('hardware',h);evidence('qualification',q);evidence('native-qualification',n)
evidence('source-proof',{'passed':True,'baseCommit':base,'historicPrefixSources':3346,'historicPrefixCanonicalSha256':sha(json.dumps(prefix,sort_keys=True,separators=(',',':')).encode()),'sourceHashes':hashes,'oldEvidenceAndSourcesUnchanged':True,'privateInputsAndBinariesExcluded':True})
evidence('failures',[{'kind':'FIRST_HOST_SIZE_MODEL_INVALID','originalPreserved':True,'productionWrites':False,'cause':'Model omitted the same forward-counter removal used by the actual builder; corrected exact model payload72446 within73728.'},{'kind':'ENDPOINT_SSH_CONNECT_TIMEOUT','originalPreserved':True,'productionWrites':False,'cause':'Endpoint control SSH22 timed out before checkpoint or firewall writes; unchanged retry completed.'}])
head='''# 双 WAN 独立类别 tag 与 NSS QoS 预算实测通过

更新：2026-10-07北京时间02:35。受控TCP BULK自然走WAN3、UDP RT走WAN2。60.01秒、121帧全程ECM2，20次续租；四个按WAN/方向/类别派生的tag、完整ct mark、NAT及连接粘性正确。NSS gate与常驻自动分类器未变，实际2335绑定。测试结束ECM0，模块、两private WAN、两物理原mq＋四fq_codel、端点FW和客户端完整恢复；原完整审核通过。

两物理NSS HTB上分别设置共享DOWN30／UP60预算，选中两WAN各15／30Mbps；各WAN有BULK与RT FQ-CoDel leaf，RT保障1Mbps、bulk使用余量。下行WAN3 bulk和WAN2 RT、上行对应leaf实际有包；其它选中WAN类别leaf零包。附近60.46秒异步快照bulk下行约10.78Mbps、drop98，RT双向drop0。配置命令和真实leaf生效已证明；没有跑满15Mbps，不能宣称限速精度或两路bulk竞争已经通过。RT队列drop0不代表端到端零丢包。

现有NSS HTB class dump将parent打印成root，实际层级依据本机源码和成功的parent attach命令判断，不用错误dump做层级证明。FQ-CoDel原参数保持；不新增ECN、Wi-Fi、autorate或完整CAKE语义结论。B-only busy13.71%、softirq0.90%、squeeze/drop0仅描述，不重跑CPU门槛或外推300Mbps/真人/常驻。

source6／kernel90(最大120)／独立owner180／client180保持；record767123字节小于1MiB，payload72446小于73728。初次尺寸模型不等价、端点SSH超时均保留；修正后才继续，所有写前新checkpoint下载SHA/gzip与控制连接外自动恢复照常核验。

下一步：两条受控TCP下载同时跨WAN加速，加一条UDP RT，验证共享与每WAN预算实际竞争。07:40收尾、07:50不新开生产、08:00前暂停；睡眠期间无桌面/Steam/CS2、新游戏下载或认证操作。

证据：[实际硬件与恢复](../evidence/v15-qos-hardware.json)、[新增准入](../evidence/v15-qos-qualification.json)、[目标RAM模型](../evidence/v15-qos-native-qualification.json)、[保留失败](../evidence/v15-qos-failures.json)、[源码](../evidence/v15-qos-source-proof.json)。入口：[控制器](../code/work/v15-qos/pilot-supervisor.mjs)。

## 双WAN60秒及更早历史

'''
for f in ['AGENTS.md','docs/STATE.md','docs/PLAN.md','docs/EXPERIMENT_LOG.md']:
 p=repo/f;new=head.replace('../evidence/','evidence/').replace('../code/','code/') if f=='AGENTS.md' else head;p.write_text(new+p.read_text(encoding='utf-8'),encoding='utf-8')
checker=repo/'tools/check_repository.py';s=checker.read_text(encoding='utf-8')
s=s.replace("'V14_TWO_WAN_DURATION']","'V14_TWO_WAN_DURATION','V15_WAN_CLASS_QOS']")
s=s.replace("if manifest['lastAppendExport']=='V14_TWO_WAN_DURATION':","if manifest['lastAppendExport'] in ['V14_TWO_WAN_DURATION','V15_WAN_CLASS_QOS']:")
needle="print(json.dumps({'passed':True,'filesChecked':count";assert s.count(needle)==1
extra="""if manifest['lastAppendExport']=='V15_WAN_CLASS_QOS':
 h=json.loads((root/'evidence/v15-qos-hardware.json').read_text(encoding='utf-8'))
 p=json.loads((root/'evidence/v15-qos-source-proof.json').read_text(encoding='utf-8'))
 assert h['passed'] and h['actualHardware'] and h['actualBoundInputs']==2335 and h['nativeGateUnchanged'] and h['residentClassifierUnchanged']
 assert 60<=h['phase']['seconds']<61 and h['ecmCountsThroughoutB']==[2] and h['finalEcmCount']==0 and h['renewals']==20 and all(h['originalRecoveryFlags'].values())
 assert h['perWanTagAndBudgetRuntimeConfigured'] and not h['saturatedRateAccuracyProven'] and not h['twoSimultaneousBulkFlowsProven']
 assert not h['newCpuCausalBenefitClaimed'] and not h['humanCs2Acceptance'] and not h['fiveWanOrPermanentNssAcceptance'] and h['nativeRecordBytes']<1048576
 assert p['historicPrefixSources']==3346 and p['oldEvidenceAndSourcesUnchanged']
 assert p['historicPrefixCanonicalSha256']==hashlib.sha256(json.dumps(manifest['sources'][:3346],sort_keys=True,separators=(',',':')).encode()).hexdigest()
 for f,d in p['sourceHashes'].items():assert hashlib.sha256((root/'code'/f).read_bytes()).hexdigest()==d,f
 for slot,wan,cls in [('tcp',3,5),('udp',2,6)]:
  v=h['flowProof'][slot];assert v['ctMark']==wan<<16 and v['wanAffinity']==wan and v['natCorrect'] and v['downTag']==(0x8f00+wan*16+cls)<<16 and v['upTag']==(0x8e00+wan*16+cls)<<16
"""
checker.write_text(s.replace(needle,extra+needle),encoding='utf-8')
attrs=repo/'.gitattributes'
with attrs.open('a',encoding='utf-8') as f:f.write('\n/code/work/v15-qos/fast-path.lua whitespace=cr-at-eol,-blank-at-eol\n/code/work/v15-qos/endpoint-firewall-guardian.py whitespace=cr-at-eol,-blank-at-eof\n')
print(dump({'passed':True,'newSources':len(hashes),'sources':len(m['sources']),'actualHardware':True}))
