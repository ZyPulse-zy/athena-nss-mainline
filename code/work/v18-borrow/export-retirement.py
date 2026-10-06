"""Preserve the failed long-window attempt and its exact class-change retirement."""
from pathlib import Path
import copy,hashlib,json,subprocess
w=Path(__file__).resolve().parents[2];root=w/'work/v18-borrow';repo=w/'athena-nss-mainline';base='b42b826f82fc2049d584eb92a8b2ea3c02286b5d'
read=lambda p:json.loads(p.read_text(encoding='utf8'));sha=lambda b:hashlib.sha256(b).hexdigest();dump=lambda d:json.dumps(d,ensure_ascii=False,indent=2)+'\n'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()==base and not subprocess.check_output(['git','status','--porcelain'],cwd=repo)
h=read(root/'retirement-descriptive.json');q=read(root/'entry-qualified.json');n=read(root/'native-qualified.json');assert h['expectedPreciseRetirementVerified'] and not h['fullSixtySecondAcceptance'] and q['passed'] and n['passed']
m=read(repo/'source-manifest.json');prefix=copy.deepcopy(m['sources']);assert len(prefix)==3467;hashes={}
for p in sorted(root.iterdir()):
 if not p.is_file() or p.suffix not in ['.mjs','.lua','.py','.ps1'] or any(x in p.name for x in ['private','failure','credential','connect-router']):continue
 f=p.relative_to(w).as_posix();b=p.read_bytes();dst=repo/'code'/f;dst.parent.mkdir(parents=True,exist_ok=True)
 with dst.open('xb') as x:x.write(b)
 hashes[f]=sha(b);m['sources'].append({'path':'code/'+f,'workspaceSource':f,'sha256':sha(b),'bytes':len(b),'role':'v18-borrow-attempt-and-real-class-retirement'})
for f,d in q['sourceManifest'].items():
 if f in hashes:assert hashes[f]==d
m['lastAppendExport']='V18_BORROW_RETIRED';(repo/'source-manifest.json').write_text(dump(m),encoding='utf8')
def evidence(name,x):
 with (repo/'evidence'/('v18-borrow-'+name+'.json')).open('x',encoding='utf8') as f:f.write(dump(x))
evidence('retirement',h);evidence('qualification',q);evidence('native-qualification',n);evidence('source-proof',{'passed':True,'baseCommit':base,'historicPrefixSources':3467,'historicPrefixCanonicalSha256':sha(json.dumps(prefix,sort_keys=True,separators=(',',':')).encode()),'sourceHashes':hashes,'oldEvidenceAndSourcesUnchanged':True,'privateInputsAndBinariesExcluded':True})
head='''# 共享预算借用配置已建立；低速 TCP 改类后精确结束旧代

更新：2026-10-07北京时间03:35。三条自然WAN1／4／5流进入ECM3，DOWN18共同父预算下按WAN和leaf可借用空闲份额、UP60按WAN硬上限保持，初始tag/ct mark/NAT/affinity正确。但B仅3.09秒，不能宣称60秒或借用吞吐验收通过；原控制器failed结果保持。

同query完整来源显示仅tcp2由BULK转成BE/cooldown：窗口速率1639.42Kbps，低于常驻2000Kbps的bulk门槛。TCP仍在、CT/完整mark/NAT/WAN均相同；另一TCP仍BULK、UDP仍RT。不是将投影缺失当退出。控制器停止新学习、精确关闭这三条旧代CI、ECM3→0，撤销tag并完整恢复模块、private WAN、两物理原mq＋四fq_codel；原完整audit和端点/FW/客户端关闭通过。没有改分类门槛或给BE流硬贴bulk标签。

负载为自有TCP28＋4Mbps、总32Mbps与64KiB credit，UDP50pps。该失败是测试负载未保持BULK类别，不能据此归咎NSS/固件或取消已成立的v16/v17证明。下一轮只将发送器改成24＋8Mbps，总量仍32，借用政策、三槽gate与所有恢复限制保持；先以实际自动分类决定是否准入。BE流仍走软件fallback，当前有限控制器会结束耦合旧代，这项限制进入后续部署backlog。

2461绑定；源6/native90(最大120)/owner180/client180以及9000/65536/73728/1MiB不放宽。07:40收尾、07:50不新开生产、08:00前暂停；睡眠期间无桌面、Steam/CS2、新下载或认证操作。

证据：[真实改类与恢复](../evidence/v18-borrow-retirement.json)、[入口](../evidence/v18-borrow-qualification.json)、[预算RAM模型](../evidence/v18-borrow-native-qualification.json)、[源码](../evidence/v18-borrow-source-proof.json)。入口：[控制器](../code/work/v18-borrow/pilot-supervisor.mjs)。

## 已完成的预算响应与更早历史

'''
for f in ['AGENTS.md','docs/STATE.md','docs/PLAN.md','docs/EXPERIMENT_LOG.md']:
 p=repo/f;new=head.replace('../evidence/','evidence/').replace('../code/','code/') if f=='AGENTS.md' else head;p.write_text(new+p.read_text(encoding='utf8'),encoding='utf8')
checker=repo/'tools/check_repository.py';s=checker.read_text(encoding='utf8').replace("'V17_BUDGET_RT']","'V17_BUDGET_RT','V18_BORROW_RETIRED']").replace("if manifest['lastAppendExport']=='V17_BUDGET_RT':","if manifest['lastAppendExport'] in ['V17_BUDGET_RT','V18_BORROW_RETIRED']:")
needle="print(json.dumps({'passed':True,'filesChecked':count";assert s.count(needle)==1
extra="""if manifest['lastAppendExport']=='V18_BORROW_RETIRED':
 h=json.loads((root/'evidence/v18-borrow-retirement.json').read_text(encoding='utf8'));p=json.loads((root/'evidence/v18-borrow-source-proof.json').read_text(encoding='utf8'))
 assert h['expectedPreciseRetirementVerified'] and not h['fullSixtySecondAcceptance'] and not h['borrowThroughputProven'] and h['originalControllerReportedFailurePreserved'] and h['sameQueryCompleteClassification'] and h['residentThresholdsUnchanged'] and h['ctExitNotInferred']
 assert 3<=h['phaseSeconds']<4 and h['actualNaturalWanSet']==[1,4,5] and h['ecm3BeforeRetirement'] and h['finalEcmCount']==0 and all(h['originalRecoveryFlags'].values()) and h['completeBaselineAuditPassed'] and h['endpointClosedAndRestored']
 assert h['classification']['tcp2']['class']=='BE' and h['classification']['tcp2']['reason']=='cooldown' and h['classification']['tcp2']['rateKbps']<h['actualFlowMaxKbps']==2000
 assert p['historicPrefixSources']==3467 and p['oldEvidenceAndSourcesUnchanged'] and p['historicPrefixCanonicalSha256']==hashlib.sha256(json.dumps(manifest['sources'][:3467],sort_keys=True,separators=(',',':')).encode()).hexdigest()
 for f,d in p['sourceHashes'].items():assert hashlib.sha256((root/'code'/f).read_bytes()).hexdigest()==d,f
"""
checker.write_text(s.replace(needle,extra+needle),encoding='utf8')
with (repo/'.gitattributes').open('a',encoding='utf8') as f:f.write('\n/code/work/v18-borrow/fast-path.lua whitespace=cr-at-eol,-blank-at-eol\n/code/work/v18-borrow/endpoint-firewall-guardian.py whitespace=cr-at-eol,-blank-at-eof\n')
print(dump({'preservedExpectedRetirement':True,'fullPilotPassed':False,'newSources':len(hashes),'sources':len(m['sources'])}))
