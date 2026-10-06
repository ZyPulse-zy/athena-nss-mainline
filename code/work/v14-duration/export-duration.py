"""Curated append-only delivery of the completed two-WAN duration trial."""
from pathlib import Path
import copy,hashlib,json,subprocess
w=Path(__file__).resolve().parents[2];root=w/'work/v14-duration';repo=w/'athena-nss-mainline'
base='676b59b884cf94e64b6442c444438ba87d0d1ee9'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda b:hashlib.sha256(b).hexdigest()
dump=lambda d:json.dumps(d,ensure_ascii=False,indent=2)+'\n'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()==base
assert not subprocess.check_output(['git','status','--porcelain'],cwd=repo)
h=read(root/'hardware-descriptive.json');assert h['passed'] and h['actualHardware']
q=read(root/'entry-qualified.json');assert q['passed']
manifest=read(repo/'source-manifest.json');prefix=copy.deepcopy(manifest['sources']);assert len(prefix)==3316
source_hashes={}
for src in sorted(root.iterdir()):
 if not src.is_file() or src.suffix not in ['.mjs','.lua','.py','.ps1','.c','.h'] or any(v in src.name for v in ['private','credential','connect-router']):continue
 f=src.relative_to(w).as_posix();data=src.read_bytes();target='code/'+f;out=repo/target;out.parent.mkdir(parents=True,exist_ok=True)
 with out.open('xb') as x:x.write(data)
 source_hashes[f]=sha(data);manifest['sources'].append({'path':target,'workspaceSource':f,'sha256':sha(data),'bytes':len(data),'role':'v14-completed-two-wan-sixty-second-duration'})
for f,digest in q['sourceManifest'].items():assert source_hashes[f]==digest,f
manifest['lastAppendExport']='V14_TWO_WAN_DURATION';(repo/'source-manifest.json').write_text(dump(manifest),encoding='utf-8')
def evidence(name,data):
 with (repo/'evidence'/('v14-duration-'+name+'.json')).open('x',encoding='utf-8') as f:f.write(dump(data))
evidence('hardware',h);evidence('qualification',q)
evidence('source-proof',{'passed':True,'baseCommit':base,'historicPrefixSources':3316,'historicPrefixCanonicalSha256':sha(json.dumps(prefix,sort_keys=True,separators=(',',':')).encode()),'sourceHashes':source_hashes,'oldV13AndV1EvidenceUnchanged':True,'privateInputsAndBinariesExcluded':True})
evidence('mainline',{'passed':True,'actualTwoWanSixtySecondSessionCompleted':True,'nssNativeGateUnchanged':True,'tcpWan':4,'udpWan':3,'nativeSeconds':90,'ownerSeconds':180,'sourceSeconds':6,'clientSeconds':180,'nssBSeconds':h['phase']['seconds'],'renewals':20,'fourLeavesCarriedTraffic':True,'allFiveWanHealthyAtCompleteAudit':True,'perWanIndependentBudgetsProven':False,'multipleBulkFlowsProven':False,'humanExperienceAccepted':False,'newCpuCausalBenefitClaim':False,'permanentDeployment':False,'next':'WAN and class leaf budgets on actual physical NSS shapers; then bounded multiple bulk flows'})
head='''# 双 WAN 60 秒 NSS 运行与完整恢复通过

更新：2026-10-07北京时间02:15。真实受控 TCP BULK 自然走WAN4、小UDP RT走WAN3，Linux PBR仍决定出口。NSS B段60.01秒、121帧全程ECM2、20次续租，四tag/完整ct mark/NAT/WAN affinity正确；结束后ECM0、模块/两WAN/两物理原mq＋四fq_codel/端点FW/客户端全部恢复，原完整审核通过。

上下行四个FQ-CoDel leaf均有实际流量。64.19秒附近异步队列快照下行bulk112566包/drop25，RT上下行2754/2621包/drop0；RT队列零drop不代表端到端零丢包。B仅描述性CPU busy14.16%、softirq0.96%、time_squeeze/softnet drop0，没有重新做CPU因果对照，不外推300Mbps、真人或长期部署。

原two-slot gate二进制未变，仍只一TCP＋一UDP、两个自然健康WAN，未知流默认拒绝。source6秒；本次kernel90秒/最大120，独立owner180秒，client180/其它硬截止保留。2300实际绑定，完整紧凑record623180字节小于1MiB；每次生产写前新checkpoint下载SHA/gzip及控制连接外独立恢复已核验。原v13及所有失败证据保留。

下一步只实现按WAN与类别映射可控NSS预算，再扩大受控bulk准入；保留Linux PBR连接粘性与CAKE fallback。07:40收尾、07:50不新开生产、08:00前暂停。睡眠期间无桌面/Steam/CS2操作或新游戏下载。

证据：[硬件与恢复](../evidence/v14-duration-hardware.json)、[准入范围](../evidence/v14-duration-qualification.json)、[源码](../evidence/v14-duration-source-proof.json)。入口：[60秒双WAN控制器](../code/work/v14-duration/pilot-supervisor.mjs)。

## 双WAN20秒及更早历史

'''
for f in ['AGENTS.md','docs/STATE.md','docs/PLAN.md','docs/EXPERIMENT_LOG.md']:
 p=repo/f;new=head.replace('../evidence/','evidence/').replace('../code/','code/') if f=='AGENTS.md' else head;p.write_text(new+p.read_text(encoding='utf-8'),encoding='utf-8')
checker=repo/'tools/check_repository.py';s=checker.read_text(encoding='utf-8')
s=s.replace("'V13_TWO_WAN_NIGHT']","'V13_TWO_WAN_NIGHT','V14_TWO_WAN_DURATION']")
s=s.replace("if manifest['lastAppendExport']=='V13_TWO_WAN_NIGHT':","if manifest['lastAppendExport'] in ['V13_TWO_WAN_NIGHT','V14_TWO_WAN_DURATION']:")
needle="print(json.dumps({'passed':True,'filesChecked':count";assert s.count(needle)==1
extra="""if manifest['lastAppendExport']=='V14_TWO_WAN_DURATION':
 duration=json.loads((root/'evidence/v14-duration-hardware.json').read_text(encoding='utf-8'))
 dp=json.loads((root/'evidence/v14-duration-source-proof.json').read_text(encoding='utf-8'))
 assert duration['passed'] and duration['actualHardware'] and duration['actualBoundInputs']==2300
 assert 60<=duration['phase']['seconds']<61 and duration['phase']['sampleCount']==121 and duration['renewals']==20
 assert duration['ecmCountsThroughoutB']==[2] and duration['finalEcmCount']==0 and all(duration['originalRecoveryFlags'].values())
 assert not duration['newCpuCausalBenefitClaimed'] and not duration['humanCs2Acceptance'] and not duration['fiveWanOrPermanentNssAcceptance']
 assert duration['sourceFreshnessSeconds']==6 and duration['kernelSeconds']==90 and duration['ownerSeconds']==180 and duration['nativeRecordBytes']<1048576
 assert dp['passed'] and dp['historicPrefixSources']==3316 and dp['oldV13AndV1EvidenceUnchanged']
 assert dp['historicPrefixCanonicalSha256']==hashlib.sha256(json.dumps(manifest['sources'][:3316],sort_keys=True,separators=(',',':')).encode()).hexdigest()
 for f,h in dp['sourceHashes'].items():assert hashlib.sha256((root/'code'/f).read_bytes()).hexdigest()==h,f
"""
checker.write_text(s.replace(needle,extra+needle),encoding='utf-8')
print(dump({'passed':True,'newSources':len(source_hashes),'sources':len(manifest['sources']),'actualDurationHardware':True}))
