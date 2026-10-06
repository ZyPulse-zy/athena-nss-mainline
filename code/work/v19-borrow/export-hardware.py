"""Publish actual multi-WAN borrowing while preserving the earlier retirement."""
from pathlib import Path
import copy,hashlib,json,subprocess
w=Path(__file__).resolve().parents[2];root=w/'work/v19-borrow';repo=w/'athena-nss-mainline';base='b8d8a2b7ae9a54e9815fd768e7b653eecde31bf2'
read=lambda p:json.loads(p.read_text(encoding='utf8'));sha=lambda b:hashlib.sha256(b).hexdigest();dump=lambda d:json.dumps(d,ensure_ascii=False,indent=2)+'\n'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()==base and not subprocess.check_output(['git','status','--porcelain'],cwd=repo)
h=read(root/'hardware-descriptive.json');q=read(root/'entry-qualified.json');n=read(root/'native-qualified.json');assert h['passed'] and h['sharedBudgetBorrowingObserved'] and h['bulkWithinSharedDownBudget'] and q['passed'] and n['passed']
m=read(repo/'source-manifest.json');prefix=copy.deepcopy(m['sources']);assert len(prefix)==3502;hashes={}
for p in sorted(root.iterdir()):
 if not p.is_file() or p.suffix not in ['.mjs','.lua','.py','.ps1'] or any(x in p.name for x in ['private','failure','credential','connect-router']):continue
 f=p.relative_to(w).as_posix();b=p.read_bytes();dst=repo/'code'/f;dst.parent.mkdir(parents=True,exist_ok=True)
 with dst.open('xb') as x:x.write(b)
 hashes[f]=sha(b);m['sources'].append({'path':'code/'+f,'workspaceSource':f,'sha256':sha(b),'bytes':len(b),'role':'v19-actual-multiwan-bandwidth-borrowing'})
for f,d in q['sourceManifest'].items():
 if f in hashes:assert hashes[f]==d
m['lastAppendExport']='V19_BORROW_PASS';(repo/'source-manifest.json').write_text(dump(m),encoding='utf8')
def evidence(name,x):
 with (repo/'evidence'/('v19-borrow-'+name+'.json')).open('x',encoding='utf8') as f:f.write(dump(x))
evidence('hardware',h);evidence('qualification',q);evidence('native-qualification',n);evidence('source-proof',{'passed':True,'baseCommit':base,'historicPrefixSources':3502,'historicPrefixCanonicalSha256':sha(json.dumps(prefix,sort_keys=True,separators=(',',':')).encode()),'sourceHashes':hashes,'oldEvidenceAndSourcesUnchanged':True,'privateInputsAndBinariesExcluded':True})
head='''# 多 WAN NSS 共享预算借用实测通过

更新：2026-10-07北京时间03:45。保持v18的DOWN18借用／UP60硬上限政策与v16三槽gate，唯一负载变化28＋4→24＋8Mbps，总32和64KiB credit不变。实际WAN1／4／5三条TCP BULK、TCP BULK、UDP RT完成60.01秒／121帧，ECM持续3、20次续租；六tag、完整ct mark、NAT和WAN affinity正确。2497实际绑定，record808129字节在原1MiB内。

附近异步队列窗两路bulk约7.05／8.26Mbps、合15.31；各WAN保障6Mbps，两个bulk均超过保障，且合计在共同18Mbps预算内，证明空闲份额借用已生效。RT上下行FQ-CoDel leaf drop0；保守B内部57.15秒的自有UDP2470发／2470返，RTT中位203.89ms、p95 204.93ms、p99 205.92ms。该echo不代表CS2 jitter/loss/Miss或真人体验；本轮不新增CPU因果、长期限速精度或常驻结论。

原完整audit与模块、private WAN、两物理mq＋四fq_codel、端点、精确FW和客户端恢复全部通过。v18低速TCP真实改类失败保留；没有修改分类阈值或伪造BULK。下一步只扩QoS映射为五WAN的bulk/RT leaf，保留三条精确加速连接和未知默认拒绝；这是五WAN队列覆盖，不能称五WAN同时fast path。07:40收尾、07:50不新开生产、08:00前暂停。

证据：[真实借用/RT与恢复](../evidence/v19-borrow-hardware.json)、[入口](../evidence/v19-borrow-qualification.json)、[复用RAM证明](../evidence/v19-borrow-native-qualification.json)、[源码](../evidence/v19-borrow-source-proof.json)。入口：[控制器](../code/work/v19-borrow/pilot-supervisor.mjs)。

## 保留的改类失败与更早历史

'''
for f in ['AGENTS.md','docs/STATE.md','docs/PLAN.md','docs/EXPERIMENT_LOG.md']:
 p=repo/f;new=head.replace('../evidence/','evidence/').replace('../code/','code/') if f=='AGENTS.md' else head;p.write_text(new+p.read_text(encoding='utf8'),encoding='utf8')
checker=repo/'tools/check_repository.py';s=checker.read_text(encoding='utf8').replace("'V18_BORROW_RETIRED']","'V18_BORROW_RETIRED','V19_BORROW_PASS']").replace("if manifest['lastAppendExport']=='V18_BORROW_RETIRED':","if manifest['lastAppendExport'] in ['V18_BORROW_RETIRED','V19_BORROW_PASS']:")
needle="print(json.dumps({'passed':True,'filesChecked':count";assert s.count(needle)==1
extra="""if manifest['lastAppendExport']=='V19_BORROW_PASS':
 h=json.loads((root/'evidence/v19-borrow-hardware.json').read_text(encoding='utf8'));p=json.loads((root/'evidence/v19-borrow-source-proof.json').read_text(encoding='utf8'))
 assert h['passed'] and h['actualHardware'] and h['actualBoundInputs']==2497 and h['nativeGateUnchangedFromV16'] and h['qosUnchangedFromV18'] and h['residentClassifierUnchanged']
 assert 60<=h['phase']['seconds']<61 and h['ecmCountsThroughoutB']==[3] and h['finalEcmCount']==0 and h['renewals']==20 and all(h['originalRecoveryFlags'].values()) and h['nativeRecordBytes']<1048576
 assert h['sharedBudgetBorrowingObserved'] and h['bulkWithinSharedDownBudget'] and h['twoSimultaneousBulkFlowsProven'] and not h['longTermRateAccuracyProven'] and not h['newCpuCausalBenefitClaimed'] and not h['humanCs2Acceptance'] and not h['fiveWanOrPermanentNssAcceptance']
 assert h['rtLeafDrop']=={'down':0,'up':0} and h['rtEchoDuringInteriorB']['sent']==2470 and h['rtEchoDuringInteriorB']['returned']==2470 and not h['rtEchoDuringInteriorB']['cs2Metrics']
 assert p['historicPrefixSources']==3502 and p['oldEvidenceAndSourcesUnchanged'] and p['historicPrefixCanonicalSha256']==hashlib.sha256(json.dumps(manifest['sources'][:3502],sort_keys=True,separators=(',',':')).encode()).hexdigest()
 for f,d in p['sourceHashes'].items():assert hashlib.sha256((root/'code'/f).read_bytes()).hexdigest()==d,f
"""
checker.write_text(s.replace(needle,extra+needle),encoding='utf8')
with (repo/'.gitattributes').open('a',encoding='utf8') as f:f.write('\n/code/work/v19-borrow/fast-path.lua whitespace=cr-at-eol,-blank-at-eol\n/code/work/v19-borrow/endpoint-firewall-guardian.py whitespace=cr-at-eol,-blank-at-eof\n')
print(dump({'passed':True,'newSources':len(hashes),'sources':len(m['sources'])}))
