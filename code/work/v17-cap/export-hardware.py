"""Publish the bounded budget response and RT measurements, with original evidence retained."""
from pathlib import Path
import copy,hashlib,json,subprocess
w=Path(__file__).resolve().parents[2];root=w/'work/v17-cap';repo=w/'athena-nss-mainline';base='4b81f7bc9481716870a06fc242079b3cfc8ab4ec'
read=lambda p:json.loads(p.read_text(encoding='utf8'));sha=lambda b:hashlib.sha256(b).hexdigest();dump=lambda d:json.dumps(d,ensure_ascii=False,indent=2)+'\n'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()==base and not subprocess.check_output(['git','status','--porcelain'],cwd=repo)
h=read(root/'hardware-descriptive.json');q=read(root/'entry-qualified.json');n=read(root/'native-qualified.json');assert h['passed'] and q['passed'] and n['passed']
m=read(repo/'source-manifest.json');prefix=copy.deepcopy(m['sources']);assert len(prefix)==3432;hashes={}
for p in sorted(root.iterdir()):
 if not p.is_file() or p.suffix not in ['.mjs','.lua','.py','.ps1'] or any(x in p.name for x in ['private','failure','credential','connect-router']):continue
 f=p.relative_to(w).as_posix();b=p.read_bytes();dst=repo/'code'/f;dst.parent.mkdir(parents=True,exist_ok=True)
 with dst.open('xb') as x:x.write(b)
 hashes[f]=sha(b);m['sources'].append({'path':'code/'+f,'workspaceSource':f,'sha256':sha(b),'bytes':len(b),'role':'v17-down18-budget-and-rt-coexistence'})
for f,d in q['sourceManifest'].items():
 if f in hashes:assert hashes[f]==d
m['lastAppendExport']='V17_BUDGET_RT';(repo/'source-manifest.json').write_text(dump(m),encoding='utf8')
def evidence(name,x):
 with (repo/'evidence'/('v17-cap-'+name+'.json')).open('x',encoding='utf8') as f:f.write(dump(x))
evidence('hardware',h);evidence('qualification',q);evidence('native-qualification',n);evidence('source-proof',{'passed':True,'baseCommit':base,'historicPrefixSources':3432,'historicPrefixCanonicalSha256':sha(json.dumps(prefix,sort_keys=True,separators=(',',':')).encode()),'sourceHashes':hashes,'oldEvidenceAndSourcesUnchanged':True,'privateInputsAndBinariesExcluded':True})
head='''# 多 WAN NSS 下行预算响应与 RT 共存通过

更新：2026-10-07北京时间03:20。唯一数据面改动为共享DOWN30→18Mbps，UP60保留；三槽native gate、分类器/标签/精确CT pin及其它Lua均复用v16字节。TCP BULK自然WAN3／WAN2、UDP RT在WAN3；60.00秒/121个B帧、ECM3、20次续租、六tag/完整ct mark/NAT/affinity正确，结束ECM0并完整恢复。2425绑定，实际guardian8831／bundle72637／record747019都在原上限内。

两路bulk约6.54／6.70Mbps、合计13.24Mbps，RT双向leaf drop0、squeeze/drop0。相比先前DOWN30的22.16Mbps，流量描述性比例约0.597，与预算18/30的0.6接近；WAN/CT已不同，不能称同流因果A/B。未跑到各WAN9Mbps的90%，不宣称精确跑满或长期限速精度。bulk AQM有drop，TCP利用率和WAN/远端RTT影响列为后续描述，未自动升级blocker。

直接复用既有PC时间、来源uptime和receipt时间戳，偏移不确定度0.85秒并排除边缘；NSS B内部可确定的57.15秒，UDP2365发／2365返、RTT中位199.62ms、p95 200.59ms、p99 201.71ms。是自有Dallas echo，不是CS2 jitter/loss/Miss或真人验收。没有新增tap/故障注入或CPU门槛。

模块、private WAN、两物理原mq＋四fq_codel、精确端点FW和客户端全部恢复，原完整audit通过，常驻NSS68分类器未修改。下一步验证共享预算借用：保持总DOWN18和RT保障，让繁忙WAN在共同父预算下借用空闲份额；使用明确不对称但总量仍32Mbps的自有bulk负载。07:40收尾、07:50不新开生产、08:00前暂停；睡眠期间不操作桌面/Steam/CS2或新下载。

证据：[真实硬件/队列/RT窗口与恢复](../evidence/v17-cap-hardware.json)、[入口](../evidence/v17-cap-qualification.json)、[新增预算RAM模型](../evidence/v17-cap-native-qualification.json)、[源码](../evidence/v17-cap-source-proof.json)。入口：[控制器](../code/work/v17-cap/pilot-supervisor.mjs)。

## 三流跨WAN及更早历史

'''
for f in ['AGENTS.md','docs/STATE.md','docs/PLAN.md','docs/EXPERIMENT_LOG.md']:
 p=repo/f;new=head.replace('../evidence/','evidence/').replace('../code/','code/') if f=='AGENTS.md' else head;p.write_text(new+p.read_text(encoding='utf8'),encoding='utf8')
checker=repo/'tools/check_repository.py';s=checker.read_text(encoding='utf8').replace("'V16_THREE_FLOW_MULTIWAN']","'V16_THREE_FLOW_MULTIWAN','V17_BUDGET_RT']").replace("if manifest['lastAppendExport']=='V16_THREE_FLOW_MULTIWAN':","if manifest['lastAppendExport'] in ['V16_THREE_FLOW_MULTIWAN','V17_BUDGET_RT']:")
needle="print(json.dumps({'passed':True,'filesChecked':count";assert s.count(needle)==1
extra="""if manifest['lastAppendExport']=='V17_BUDGET_RT':
 h=json.loads((root/'evidence/v17-cap-hardware.json').read_text(encoding='utf8'));p=json.loads((root/'evidence/v17-cap-source-proof.json').read_text(encoding='utf8'))
 assert h['passed'] and h['actualHardware'] and h['actualBoundInputs']==2425 and h['nativeGateUnchangedFromV16'] and h['residentClassifierUnchanged']
 assert 60<=h['phase']['seconds']<61 and h['ecmCountsThroughoutB']==[3] and h['finalEcmCount']==0 and h['renewals']==20 and all(h['originalRecoveryFlags'].values()) and h['nativeRecordBytes']<1048576
 assert h['twoSimultaneousBulkFlowsProven'] and not h['boundedPerWanSaturationObserved'] and not h['longTermRateAccuracyProven'] and not h['newCpuCausalBenefitClaimed'] and not h['humanCs2Acceptance'] and not h['fiveWanOrPermanentNssAcceptance']
 assert h['rtLeafDrop']=={'down':0,'up':0} and h['rtEchoDuringInteriorB']['sent']==2365 and h['rtEchoDuringInteriorB']['returned']==2365 and h['rtEchoDuringInteriorB']['unreturned']==0 and h['rtEchoDuringInteriorB']['cs2Metrics']==False
 assert p['historicPrefixSources']==3432 and p['oldEvidenceAndSourcesUnchanged'] and p['historicPrefixCanonicalSha256']==hashlib.sha256(json.dumps(manifest['sources'][:3432],sort_keys=True,separators=(',',':')).encode()).hexdigest()
 for f,d in p['sourceHashes'].items():assert hashlib.sha256((root/'code'/f).read_bytes()).hexdigest()==d,f
"""
checker.write_text(s.replace(needle,extra+needle),encoding='utf8')
with (repo/'.gitattributes').open('a',encoding='utf8') as f:f.write('\n/code/work/v17-cap/fast-path.lua whitespace=cr-at-eol,-blank-at-eol\n/code/work/v17-cap/endpoint-firewall-guardian.py whitespace=cr-at-eol,-blank-at-eof\n')
print(dump({'passed':True,'newSources':len(hashes),'sources':len(m['sources'])}))
