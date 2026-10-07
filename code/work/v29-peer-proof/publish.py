"""Append the bounded peer diagnosis and actual restoration; never rewrite old evidence."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import copy, gzip, hashlib, json, subprocess

w=Path(__file__).resolve().parents[2]; repo=w/'athena-nss-mainline'
base='e29d2e6ff5c2c055ffde7b3dca3cf9c238bf2996'
run=w/'work/v29-peer-proof/run-20261007002118-60e512ecac8637fe'
read=lambda p: json.loads(p.read_text(encoding='utf8'))
dump=lambda x: json.dumps(x,ensure_ascii=False,indent=2)+'\n'
sha=lambda b: hashlib.sha256(b).hexdigest()
def git(*a): return subprocess.check_output(['git',*a],cwd=repo)
assert git('rev-parse','HEAD').decode().strip()==base
assert not git('status','--porcelain')
before={}
for row in git('ls-tree','-r','-z',base,'--','code','evidence').split(b'\0'):
    if row:
        header,name=row.split(b'\t',1); before[name.decode()]=header.decode().split()[2]
old_bytes={p:sha((repo/p).read_bytes()) for p in before}
manifest=read(repo/'source-manifest.json'); prefix=copy.deepcopy(manifest['sources']); assert len(prefix)==3866
v28=read(w/'work/v28-peer-path/run-20261007001049-3be9c7c0/summary.json')
correlation=read(w/'work/v28-peer-path/run-20261007001049-3be9c7c0/peer-correlation-proof.json')
v29=read(run/'summary.json'); final=read(run/'final-audit.json')
assert v28['diagnosticCompleted'] and not v28['configurationWrites'] and not v28['nssStarted']
assert not correlation['tcpSynSourcePortMatchesOwnedClient'] and not correlation['tcpSynSourcePortMatchesExactCtReplyPort']
assert v29['passed'] and v29['tcpAuthenticatedReady'] and v29['tcpPayloadBytes']==22960476
assert 0<v29['firstPayloadSeconds']<8 and 25<=v29['clientSeconds']<26 and not v29['clientErrors']
assert v29['protocolSpecificPublicPeersDiffer'] and v29['exactFirewallRules']==2 and not v29['nssStarted'] and not v29['routerConfigurationWrites']
assert final['passed'] and final['fullAudit']['ecmClosedAndZero'] and final['fullAudit']['queryAge']<6
assert final['physicalQueues']['defaultQueueOptionsAndHandlesExact']
closure=final['endpointAndClientClosure']; assert closure['canonicalFirewallBaselineMatched'] and closure['temporaryFirewallRulesRemaining']==0
assert closure['endpointPortsClosed'] and closure['clientClosure']['ownedDiagnosticClientProcessesRemaining']==0
assert closure['independentGuardianPastNaturalDeadline'] and not closure['sameGuardianStillLive']
checkpoint=read(run/'checkpoint-verified.json'); raw=(run/'endpoint-checkpoint-private.json').read_bytes()
assert checkpoint['sha256']==sha(raw) and checkpoint['gzipSha256']==sha((run/'endpoint-checkpoint-private.json.gz').read_bytes())
assert gzip.decompress((run/'endpoint-checkpoint-private.json.gz').read_bytes())==raw
inputs=read(run/'source-inputs-private.json')
for x in inputs:
    assert (run/'source-input-private'/x['stored']).read_bytes()==(w/x['path']).read_bytes()
    assert sha((w/x['path']).read_bytes())==x['sha256']
failed=read(run/'endpoint-restoration-private.json')
assert failed['code']==1 and 'Wait for independent natural deadline before checking' in failed['stderr']
assert read(run/'recheck-endpoint-restoration-private.json')['code']==0
sources=['work/v28-peer-path/capture.py','work/v28-peer-path/probe-client.mjs','work/v28-peer-path/run.mjs',
         'work/v29-peer-proof/run.mjs','work/v29-peer-proof/client.mjs','work/v29-peer-proof/capture.py',
         'work/v29-peer-proof/read-restoration.mjs','work/v29-peer-proof/read-restoration-v2.mjs',
         'work/v29-peer-proof/read-deadline.mjs','work/v29-peer-proof/finish-audit.mjs',
         final['physicalReaderSource'],'work/v29-peer-proof/publish.py']
hashes={}
for rel in sources:
    data=(w/rel).read_bytes(); dst=repo/'code'/rel; dst.parent.mkdir(parents=True,exist_ok=True)
    with dst.open('xb') as f: f.write(data)
    hashes[rel]=sha(data)
    manifest['sources'].append({'path':'code/'+rel,'workspaceSource':rel,'sha256':sha(data),'bytes':len(data),'role':'bounded-protocol-peer-diagnosis'})
# Keep all existing production qualification branches enabled.
manifest['lastPrerequisiteDiagnosticExport']='V29_PROTOCOL_SPECIFIC_PEER_PROOF'
(repo/'source-manifest.json').write_text(dump(manifest),encoding='utf8')
def evidence(name,value):
    with (repo/'evidence'/name).open('x',encoding='utf8') as f: f.write(dump(value))
v28.pop('output'); v28['correlationLimits']=correlation; v28['tcpPeerWasNotNonceAuthenticated']=True
v28['notUdpLossOrGameQualityMeasurement']=True
evidence('v28-peer-path.json',v28)
v29.pop('output'); v29['checkpointDownloadShaAndGzipVerifiedBeforeWrite']=True
v29['guardianByteIdenticalToV27']=True; v29['serverAndProtocolByteIdenticalToV27']=True
v29['firstPayloadDeadlineSeconds']=8; v29['singleTcpSlotMbps']=8
v29['fourTcpOrFiveWanFixtureQualified']=False; v29['historicalV27ExactFailureCauseProven']=False
v29['udpCountersAreWholeDiagnosticNotLossAcceptance']=True
evidence('v29-peer-proof.json',v29)
evidence('v29-peer-restoration.json',final)
evidence('v29-peer-source-proof.json',{'passed':True,'baseCommit':base,'historicPrefixSources':len(prefix),
    'historicPrefixCanonicalSha256':sha(json.dumps(prefix,sort_keys=True,separators=(',',':')).encode()),
    'sourceHashes':hashes,'actualTrialSourceInputs':[{k:x[k] for k in ['path','sha256','bytes']} for x in inputs],
    'guardianSha256':sha((w/'work/v27-raw/endpoint-firewall-guardian.py').read_bytes()),
    'oldCodeAndEvidenceBlobsChecked':len(before),'oldCodeAndEvidenceUnmodified':True,
    'rawCtPublicPeerAddressesNoncesCredentialsCheckpointsAndBinariesExcluded':True,
    'firstRestorationFailure':{'preserved':True,'code':failed['code'],'message':'Wait for independent natural deadline before checking',
        'refusedBeforeFullRestorationAudit':True,'oneLaterReadonlyRecheckPassed':True},
    'localReadCorrection':{'missingPath':'work/morning-20261007/verify_night_archive.py',
        'correctedPath':'athena-nss-mainline/tools/verify_night_archive.py','originalToolTranscriptPreserved':True},
    'noNewNssCpuGameOrFiveWanHardwareAcceptanceClaim':True})
stamp=datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
report=f'''# TCP / UDP 公网源地址假设修正与短测

更新：北京时间 {stamp}。用户在晨间封存后要求继续；本次只做传输前提定位和一条认证 TCP 短测，未启动 NSS、五槽模块或游戏。夜间 heartbeat 保持暂停。

v27 启动器把 nonce UDP 探测到的源地址同时用于 TCP / UDP 两个规则。不同协议经过 Linux PBR 和上游 NAT 后，公网源地址不保证相同。这项源码假设需要修正；旧 v27 的具体失败连接没有相同的完整公网归属证据，因此历史精确根因仍未追认。

## 实测

| 步骤 | 实际结果 | 结论边界 |
| --- | --- | --- |
| v28 只读探测 | 一条自有 TCP 尝试、30个nonce UDP；精确 CT 为 TCP WAN1/mark65536、UDP WAN5/mark327680；VPS收到4条TCP SYN metadata和5条认证UDP metadata，公网源地址不同 | TCP只有时间关联，上游还改写源端口；不是完整TCP认证或UDP交付率证明 |
| v29 单TCP修正验证 | 分别选择TCP和UDP的实际公网源地址，仍为两个单IPv4规则；原nonce服务认证后1.391秒收到首payload，25.007秒共22960476字节，客户端无错误 | 8Mbps单TCP传输前提通过；没有证明四TCP或五WAN完整fixture |
| UDP | 全短测1025发/995返，包含防火墙启用前和结束边界 | 描述性计数，不作为丢包、CS2或NSS质量验收 |
| 恢复 | 独立180秒FW自然到期；规则0/canonical基线一致/端点关闭/客户端0；原完整router audit来源1.55秒、五WAN健康、保护配置和服务epoch保持、ECM关闭全零；两物理原mq+四fq_codel所有选项和handle一致 | 当前软件fallback保持，无NSS或router配置写入 |

每次使用新目录和nonce。端点checkpoint实际下载、SHA及gzip回读一致；原v27防火墙守护、认证server和协议字节不变，写前核验独立守护，端点250秒/客户端25秒硬截止保持。没有扩源地址范围、端口、认证期限、学校策略或修改PBR。

首次清理读取早于远端守护实际截止，按原断言拒绝。失败输出和源码保持；读取剩余时间确认自然到期后，只做一次只读重查并通过。没有提前删除规则来替代自然到期证据。

## 当前范围与下一步

v20三流跨两个或三个WAN、五WANQoS队列映射、共享DOWN18借用、UP60每WAN12硬上限、RT prio0/FQ-CoDel的硬件结论保持。本次没有新增CPU、游戏体验、五WAN同时fast path或长期常驻声明。

五流fixture必须为每条实际TCP证明其公网归属，不能继续复制UDP地址；如果原精确FW政策容纳不了实际peer，写前拒绝。本次只证明一条TCP，不能直接加载五槽模块或盲重试旧五流。下一次正常Steam/CS2条件出现时，优先用新版本/新绑定承接已冻结v26入口的一次有界正常应用会话；v26旧截止和冻结字节不改。主观真人体验仍未验。

证据：[只读诊断](../evidence/v28-peer-path.json)、[认证短测](../evidence/v29-peer-proof.json)、[完整终态](../evidence/v29-peer-restoration.json)、[源码及失败保存](../evidence/v29-peer-source-proof.json)。
'''
with (repo/'docs/PEER_DIAGNOSIS_2026-10-07.md').open('x',encoding='utf8') as f: f.write(report)
head=f'''# TCP协议源地址假设已修正；单TCP认证短测与恢复通过

更新：北京时间{stamp}。用户在08:00晨间封存后要求继续；本轮没有新NSS或router配置写入。v28只读实际TCP走WAN1、UDP走WAN5，公网源地址不同且上游改写TCP源端口；TCP metadata只作时间关联。v29分别取协议公网地址，原两个单IPv4规则/180秒独立FW撤销与原认证server保持，1.391秒首payload、25.007秒22960476字节、客户端无错误。旧v27具体失败连接的精确根因仍未追认。

08:25完整终态通过：原audit source1.55秒、五WAN健康/保护配置及epoch保持/ECM关闭全零；两物理原mq+四fq_codel全部选项/handle一致；FW自然到期规则0/canonical原基线一致、端点和客户端0。首次过早清理读取拒绝的原输出/源码保留，确认到期后一次只读重查通过。

**这只证明单TCP传输前提，未新增五WAN同时fast path、正常Steam/CS2整合factory、CPU或长期验收。** v20三流多WAN和高级QoS硬件结论保持。五流必须逐TCP取实际公网归属，原精确FW政策容纳不了就写前拒绝，不复制UDP地址或盲重试。下一正常应用窗口用新版本和新绑定接v26有界会话；旧v26截止/源码不改。夜间heartbeat继续暂停。

详情：[传输定位报告](PEER_DIAGNOSIS_2026-10-07.md)、[短测](../evidence/v29-peer-proof.json)、[终态](../evidence/v29-peer-restoration.json)、[源码保存](../evidence/v29-peer-source-proof.json)。

## 以下保留晨间与夜间原记录

'''
for rel in ['AGENTS.md','docs/STATE.md','docs/PLAN.md','docs/EXPERIMENT_LOG.md']:
    p=repo/rel; h=head
    if rel=='AGENTS.md': h=h.replace('(PEER_DIAGNOSIS_2026-10-07.md)','(docs/PEER_DIAGNOSIS_2026-10-07.md)').replace('../evidence/','evidence/')
    p.write_bytes(h.encode()+p.read_bytes())
p=repo/'README.md'; intro='''# Athena NSS 多WAN / QoS 受控原型

三流跨WAN、五WAN队列映射和共享预算已硬件通过。最新TCP/UDP公网源地址假设修正，单TCP认证短测与完整恢复通过；当前NSS关闭，五WAN同时加速和正常应用新factory仍未验。见[STATE](docs/STATE.md)及[传输定位](docs/PEER_DIAGNOSIS_2026-10-07.md)。

## 以下保留晨间交付和历史记录

'''; p.write_bytes(intro.encode()+p.read_bytes())
# Exact new paths only: preserve CRLF source bytes without a global policy change.
with (repo/'.gitattributes').open('a',encoding='utf8') as f:
    f.write('\n# Exact new peer-diagnosis Windows source paths.\n')
    for rel in sources:
        if b'\r\n' in (w/rel).read_bytes(): f.write('/code/'+rel+' whitespace=cr-at-eol\n')
assert not git('diff','--name-only',base,'--','code','evidence')
assert all(sha((repo/p).read_bytes())==d for p,d in old_bytes.items())
print(json.dumps({'passed':True,'newSources':len(sources),'totalSources':len(manifest['sources']),
    'oldCodeAndEvidenceBlobsPreserved':len(before),'singleTcpPrerequisitePassed':True,'nssWrites':False}))
