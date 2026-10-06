"""Append the actual three-flow multi-WAN result; preserve historical evidence."""
from pathlib import Path
import copy,hashlib,json,subprocess
w=Path(__file__).resolve().parents[2];root=w/'work/v16-three';repo=w/'athena-nss-mainline'
base='27e225202c3e1ae1b6890a338d25cfa1c50acce3'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda b:hashlib.sha256(b).hexdigest()
dump=lambda d:json.dumps(d,ensure_ascii=False,indent=2)+'\n'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()==base
assert not subprocess.check_output(['git','status','--porcelain'],cwd=repo)
h=read(root/'hardware-descriptive.json');q=read(root/'entry-qualified-v3.json');n=read(root/'native-qualified.json');udp=read(root/'fixture-udp-descriptive.json')
assert h['passed'] and h['actualHardware'] and q['passed'] and n['passed']
m=read(repo/'source-manifest.json');prefix=copy.deepcopy(m['sources']);assert len(prefix)==3382
paths=set()
for d in [root,root/'endpoint-gate']:
 for p in d.iterdir():
  if p.is_file() and p.suffix in ['.mjs','.lua','.py','.ps1','.c','.h'] and not any(s in p.name for s in ['private','failure','credential','connect-router','.generated.']):paths.add(p)
hashes={}
for src in sorted(paths):
 f=src.relative_to(w).as_posix();data=src.read_bytes();out=repo/'code'/f;out.parent.mkdir(parents=True,exist_ok=True)
 with out.open('xb') as x:x.write(data)
 hashes[f]=sha(data);m['sources'].append({'path':'code/'+f,'workspaceSource':f,'sha256':sha(data),'bytes':len(data),'role':'v16-three-exact-flows-multiwan-qos'})
for f,d in q['sourceManifest'].items():
 if f in hashes:assert hashes[f]==d
m['lastAppendExport']='V16_THREE_FLOW_MULTIWAN';(repo/'source-manifest.json').write_text(dump(m),encoding='utf-8')
def evidence(name,data):
 with (repo/'evidence'/('v16-three-'+name+'.json')).open('x',encoding='utf-8') as f:f.write(dump(data))
evidence('hardware',h);evidence('qualification',q);evidence('native-qualification',n);evidence('udp-descriptive',udp)
evidence('gate-build',{k:read(root/'endpoint-gate'/f) for k,f in [('build','build-manifest.json'),('control','control-host-result.json'),('ct','ct_harness.result.json')]})
evidence('source-proof',{'passed':True,'baseCommit':base,'historicPrefixSources':3382,'historicPrefixCanonicalSha256':sha(json.dumps(prefix,sort_keys=True,separators=(',',':')).encode()),'sourceHashes':hashes,'oldEvidenceAndSourcesUnchanged':True,'privateInputsAndBinariesExcluded':True})
evidence('failures',[{'kind':'GUARDIAN_TRANSPORT_SIZE_REFUSED','productionWrites':False,'originalPreserved':True,'cause':'Representative three-flow rollback exec9143 exceeded9000. Exact selection moved once into the existing SHA-pinned bundle; actual guardian8831 and bundle72637 fit original caps.'},{'kind':'REDUNDANT_FULL_CLASSIFIER_SYNTAX_SIZE_REFUSED','productionWrites':False,'originalPreserved':True,'cause':'Standalone full syntax copy9871 exceeded9000. Two balanced syntax parts checked in RAM; the exact full staged bundle compiled and ran on hardware.'},{'kind':'MODEL_JSON_NUL_ARGV','productionWrites':False,'originalPreserved':True,'cause':'JSON model NUL argv did not preserve the process command string. Model reconstructs it in Lua; production raw argv validation unchanged.'},{'kind':'MODEL_LUA_NEWLINE_ESCAPES','productionWrites':False,'originalPreserved':True,'cause':'Two model-only quoting mistakes rejected by Lua parser, then corrected. No production writes in those attempts.'}])
head='''# 三流跨 WAN NSS 与独立 QoS leaf 实测通过

更新：2026-10-07北京时间03:05。两条自有 TCP BULK 自然走WAN1／WAN2，小UDP RT走WAN2。新三槽gate实际运行60.01秒、121个B帧，ECM全程3、20次续租，结束后0。六个上下行按WAN/类别派生的tag、完整ct mark、NAT、LAN/bridge入口和WAN affinity全部正确。实际2389绑定，常驻自动分类器未修改。

真实两路bulk分别进入8f15／8f25下行和8e15／8e25上行FQ-CoDel；RT进入WAN2的8f26／8e26。附近异步队列快照下行bulk约10.54／11.62Mbps，RT双向队列drop0，错误WAN类别leaf零包。DOWN共享30、UP共享60，每WAN15／30Mbps，RT保障1Mbps。已证明跨WAN两路bulk＋RT实际共存；总负载未跑满预算，尚不宣称饱和限速精度。

新gate使用同内核/ECM，不升级固件；CT/predicate/control模型、实际二进制关联和三CI硬件运行成立。三个精确CT对象及zone0/fullmark/NAT约束、未知默认拒绝、全代租约保留。独立守护的连接身份放到原有SHA-pinned bundle中，owner/模块/恢复信息与硬截止仍独立。实际guardian8831、bundle72637、record925671字节都在原9000／73728／1MiB内；source6、kernel90(最大120)、owner180、client180未放宽。三流改类时结束旧代，不直接换tag；没有声称新增选择性改类分支通过。

路由器模块、两个private WAN、两物理原mq＋四fq_codel完整恢复，原完整audit通过；自有端点、精确FW和客户端全部关闭。全fixture UDP5469发／5458返，11未返中9在停止前1秒内；RTT中位200.71ms、p95 201.26ms，仅自有Dallas echo描述，不能归为NSS特定丢包或CS2指标。B-only softirq4.37%、busy16.71%、squeeze/drop0是描述，不新增CPU因果或300Mbps/真人/长期部署结论。

下一步只改变DOWN共享预算到16Mbps，让现有两路受控bulk压住各WAN8Mbps上限，观察限速与RT共存；UP60及其它主要变量保留。07:40晨间收尾、07:50不新开生产、08:00前暂停。睡眠期间不操作桌面/Steam/CS2、不新下载或主动认证。

证据：[硬件与恢复](../evidence/v16-three-hardware.json)、[入口绑定](../evidence/v16-three-qualification.json)、[RAM模型](../evidence/v16-three-native-qualification.json)、[gate构建](../evidence/v16-three-gate-build.json)、[UDP描述](../evidence/v16-three-udp-descriptive.json)、[失败](../evidence/v16-three-failures.json)、[源码](../evidence/v16-three-source-proof.json)。入口：[控制器](../code/work/v16-three/pilot-supervisor.mjs)。

## 双WAN两槽及更早历史

'''
for f in ['AGENTS.md','docs/STATE.md','docs/PLAN.md','docs/EXPERIMENT_LOG.md']:
 p=repo/f;new=head.replace('../evidence/','evidence/').replace('../code/','code/') if f=='AGENTS.md' else head;p.write_text(new+p.read_text(encoding='utf-8'),encoding='utf-8')
checker=repo/'tools/check_repository.py';s=checker.read_text(encoding='utf-8');s=s.replace("'V15_WAN_CLASS_QOS']","'V15_WAN_CLASS_QOS','V16_THREE_FLOW_MULTIWAN']");s=s.replace("if manifest['lastAppendExport']=='V15_WAN_CLASS_QOS':","if manifest['lastAppendExport'] in ['V15_WAN_CLASS_QOS','V16_THREE_FLOW_MULTIWAN']:")
needle="print(json.dumps({'passed':True,'filesChecked':count";assert s.count(needle)==1
extra="""if manifest['lastAppendExport']=='V16_THREE_FLOW_MULTIWAN':
 h=json.loads((root/'evidence/v16-three-hardware.json').read_text(encoding='utf-8'));p=json.loads((root/'evidence/v16-three-source-proof.json').read_text(encoding='utf-8'))
 assert h['passed'] and h['actualHardware'] and h['actualBoundInputs']==2389 and h['newThreeSlotNativeGateHardwareQualified'] and h['residentClassifierUnchanged']
 assert 60<=h['phase']['seconds']<61 and h['ecmCountsThroughoutB']==[3] and h['finalEcmCount']==0 and h['renewals']==20 and all(h['originalRecoveryFlags'].values())
 assert h['twoSimultaneousBulkFlowsProven'] and not h['saturatedRateAccuracyProven'] and not h['newCpuCausalBenefitClaimed'] and not h['humanCs2Acceptance'] and not h['fiveWanOrPermanentNssAcceptance'] and h['nativeRecordBytes']<1048576
 assert p['historicPrefixSources']==3382 and p['oldEvidenceAndSourcesUnchanged'] and p['historicPrefixCanonicalSha256']==hashlib.sha256(json.dumps(manifest['sources'][:3382],sort_keys=True,separators=(',',':')).encode()).hexdigest()
 for f,d in p['sourceHashes'].items():assert hashlib.sha256((root/'code'/f).read_bytes()).hexdigest()==d,f
 for slot,wan,cls in [('tcp',1,5),('udp',2,6),('tcp2',2,5)]:
  x=h['flowProof'][slot];assert x['ctMark']==wan<<16 and x['wanAffinity']==wan and x['natCorrect'] and x['downTag']==(0x8f00+wan*16+cls)<<16 and x['upTag']==(0x8e00+wan*16+cls)<<16
"""
checker.write_text(s.replace(needle,extra+needle),encoding='utf-8')
with (repo/'.gitattributes').open('a',encoding='utf-8') as f:f.write('\n/code/work/v16-three/fast-path.lua whitespace=cr-at-eol,-blank-at-eol\n/code/work/v16-three/endpoint-firewall-guardian.py whitespace=cr-at-eol,-blank-at-eof\n')
print(dump({'passed':True,'newSources':len(hashes),'sources':len(m['sources']),'actualHardware':True}))
