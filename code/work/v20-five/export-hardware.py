"""Publish actual multi-WAN borrowing while preserving the earlier retirement."""
from pathlib import Path
import copy,hashlib,json,subprocess
w=Path(__file__).resolve().parents[2];root=w/'work/v20-five';repo=w/'athena-nss-mainline';base='e75c95c818de18f44b655f36da127b9be6d52c58'
read=lambda p:json.loads(p.read_text(encoding='utf8'));sha=lambda b:hashlib.sha256(b).hexdigest();dump=lambda d:json.dumps(d,ensure_ascii=False,indent=2)+'\n'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()==base and not subprocess.check_output(['git','status','--porcelain'],cwd=repo)
h=read(root/'hardware-descriptive.json');q=read(root/'entry-qualified.json');n=read(root/'native-qualified.json');assert h['passed'] and h['sharedBudgetBorrowingObserved'] and h['bulkWithinSharedDownBudget'] and q['passed'] and n['passed']
m=read(repo/'source-manifest.json');prefix=copy.deepcopy(m['sources']);assert len(prefix)==3537;hashes={}
for p in sorted(root.iterdir()):
 if not p.is_file() or p.suffix not in ['.mjs','.lua','.py','.ps1'] or any(x in p.name for x in ['private','failure','credential','connect-router']):continue
 f=p.relative_to(w).as_posix();b=p.read_bytes();dst=repo/'code'/f;dst.parent.mkdir(parents=True,exist_ok=True)
 with dst.open('xb') as x:x.write(b)
 hashes[f]=sha(b);m['sources'].append({'path':'code/'+f,'workspaceSource':f,'sha256':sha(b),'bytes':len(b),'role':'v20-fixed-five-wan-queue-mappings'})
for f,d in q['sourceManifest'].items():
 if f in hashes:assert hashes[f]==d
m['lastAppendExport']='V20_FIVE_QUEUE_MAP';(repo/'source-manifest.json').write_text(dump(m),encoding='utf8')
def evidence(name,x):
 with (repo/'evidence'/('v20-five-'+name+'.json')).open('x',encoding='utf8') as f:f.write(dump(x))
evidence('hardware',h);evidence('qualification',q);evidence('native-qualification',n);evidence('source-proof',{'passed':True,'baseCommit':base,'historicPrefixSources':3537,'historicPrefixCanonicalSha256':sha(json.dumps(prefix,sort_keys=True,separators=(',',':')).encode()),'sourceHashes':hashes,'oldEvidenceAndSourcesUnchanged':True,'privateInputsAndBinariesExcluded':True})
head='''# 五 WAN NSS 队列映射与共享借用通过

更新：2026-10-07北京时间03:50。上下行各18个HTB class、11个FQ-CoDel leaf已实际建立和完整读取，涵盖WAN1..5的BULK/RT以及default950。共同DOWN18：每WAN保障3、ceiling18可借用；共同UP60：每WAN12硬上限。原三槽native gate和常驻自动分类器保持，只放行两TCP BULK＋一UDP RT；实际自然WAN4／5，不声称五WAN同时fast path。

60.00秒／121帧、ECM3、20续租，六tag、完整ct mark、NAT和WAN affinity正确。2533绑定，record844813字节在1MiB内；附近异步窗bulk6.72／8.28Mbps、合14.99，超过3Mbps保障并在共享18内，空闲份额借用继续成立。RT双向leaf drop0；保守B内部57.24秒UDP2434发／2434返，RTT中位197.68ms、p95 198.74ms、p99 200.14ms，仅自有echo，不代替CS2或真人体验。未活跃WAN/类别leaf保持零包。

原完整audit、模块、private WAN、两物理原mq＋四fq_codel、端点/FW/客户端恢复通过。没有新CPU因果、长期或永久NSS声明；历史v18真实改类与失败不覆盖。下一步评估五条精确CT的同时准入，保持同一五WAN QoS政策、默认拒绝和独立撤销；实际前必须确认原传输/记录预算可容纳。07:40收尾、07:50不新开生产、08:00前暂停。

证据：[五WAN映射/借用/RT与恢复](../evidence/v20-five-hardware.json)、[入口](../evidence/v20-five-qualification.json)、[新增映射RAM模型](../evidence/v20-five-native-qualification.json)、[源码](../evidence/v20-five-source-proof.json)。入口：[控制器](../code/work/v20-five/pilot-supervisor.mjs)。

## 三流跨WAN借用与更早历史

'''
for f in ['AGENTS.md','docs/STATE.md','docs/PLAN.md','docs/EXPERIMENT_LOG.md']:
 p=repo/f;new=head.replace('../evidence/','evidence/').replace('../code/','code/') if f=='AGENTS.md' else head;p.write_text(new+p.read_text(encoding='utf8'),encoding='utf8')
checker=repo/'tools/check_repository.py';s=checker.read_text(encoding='utf8').replace("'V19_BORROW_PASS']","'V19_BORROW_PASS','V20_FIVE_QUEUE_MAP']").replace("if manifest['lastAppendExport']=='V19_BORROW_PASS':","if manifest['lastAppendExport'] in ['V19_BORROW_PASS','V20_FIVE_QUEUE_MAP']:")
needle="print(json.dumps({'passed':True,'filesChecked':count";assert s.count(needle)==1
extra="""if manifest['lastAppendExport']=='V20_FIVE_QUEUE_MAP':
 h=json.loads((root/'evidence/v20-five-hardware.json').read_text(encoding='utf8'));p=json.loads((root/'evidence/v20-five-source-proof.json').read_text(encoding='utf8'))
 assert h['passed'] and h['actualHardware'] and h['actualBoundInputs']==2533 and h['nativeGateUnchangedFromV16'] and h['onlyQosMapExpandedFromV19'] and h['residentClassifierUnchanged']
 assert 60<=h['phase']['seconds']<61 and h['ecmCountsThroughoutB']==[3] and h['finalEcmCount']==0 and h['renewals']==20 and all(h['originalRecoveryFlags'].values()) and h['nativeRecordBytes']<1048576
 assert h['fiveWanQueueCoverageVerified'] and h['queueWanSet']==[1,2,3,4,5] and h['simultaneouslyAdmittedExactFlowCount']==3 and not h['fiveWanConcurrentFastPathProven']
 assert h['sharedBudgetBorrowingObserved'] and h['bulkWithinSharedDownBudget'] and h['twoSimultaneousBulkFlowsProven'] and not h['longTermRateAccuracyProven'] and not h['newCpuCausalBenefitClaimed'] and not h['humanCs2Acceptance'] and not h['fiveWanOrPermanentNssAcceptance']
 assert h['rtLeafDrop']=={'down':0,'up':0} and h['rtEchoDuringInteriorB']['sent']==2434 and h['rtEchoDuringInteriorB']['returned']==2434 and not h['rtEchoDuringInteriorB']['cs2Metrics']
 assert p['historicPrefixSources']==3537 and p['oldEvidenceAndSourcesUnchanged'] and p['historicPrefixCanonicalSha256']==hashlib.sha256(json.dumps(manifest['sources'][:3537],sort_keys=True,separators=(',',':')).encode()).hexdigest()
 for f,d in p['sourceHashes'].items():assert hashlib.sha256((root/'code'/f).read_bytes()).hexdigest()==d,f
"""
checker.write_text(s.replace(needle,extra+needle),encoding='utf8')
with (repo/'.gitattributes').open('a',encoding='utf8') as f:f.write('\n/code/work/v20-five/fast-path.lua whitespace=cr-at-eol,-blank-at-eol\n/code/work/v20-five/endpoint-firewall-guardian.py whitespace=cr-at-eol,-blank-at-eof\n')
print(dump({'passed':True,'newSources':len(hashes),'sources':len(m['sources'])}))
