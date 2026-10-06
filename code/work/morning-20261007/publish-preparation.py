"""Save readonly morning handoff without claiming the future audit occurred."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import copy,hashlib,json,subprocess
w=Path(__file__).resolve().parents[2];repo=w/'athena-nss-mainline';base='e90c4a6a4354729741f846ab0c67697725a46920'
read=lambda p:json.loads(p.read_text(encoding='utf8'));dump=lambda x:json.dumps(x,ensure_ascii=False,indent=2)+'\n';sha=lambda b:hashlib.sha256(b).hexdigest()
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()==base and not subprocess.check_output(['git','status','--porcelain'],cwd=repo)
m=read(repo/'source-manifest.json');prefix=copy.deepcopy(m['sources']);assert len(prefix)==3857;hashes={}
files=[w/'work/v27-raw/read-input-rule-order.mjs',*sorted((w/'work/morning-20261007').iterdir())]
for p in files:
    if not p.is_file() or p.suffix not in ['.mjs','.py','.ps1','.md'] or 'private'in p.name:continue
    f=p.relative_to(w).as_posix();b=p.read_bytes();dst=repo/'code'/f;dst.parent.mkdir(parents=True,exist_ok=True)
    with dst.open('xb')as out:out.write(b)
    hashes[f]=sha(b);m['sources'].append({'path':'code/'+f,'workspaceSource':f,'sha256':sha(b),'bytes':len(b),'role':'readonly-morning-handoff-no-production-permission'})
(repo/'source-manifest.json').write_text(dump(m),encoding='utf8')
def evidence(name,v):
    with(repo/'evidence'/name).open('x',encoding='utf8')as f:f.write(dump(v))
rules=read(w/'work/v27-raw/input-rule-order-summary.json');assert rules['readonly'] and not any(x['unconditionalTerminalDeny']for x in rules['rules'])
evidence('night-input-rule-order.json',rules)
evidence('morning-preparation.json',{'passed':True,'preparationOnly':True,'morningFinalAuditPerformed':False,'syntaxChecksPassed':True,'localKnownEndpointUnitCount':17,'localClientInventoryAt0531':{'passed':True,'ownedProcessesRemaining':0,'namespaceCount':16},'notBeforeUtc':'2026-10-06T23:40:00Z','deadlineUtc':'2026-10-07T00:00:00Z','productionExperimentPermissionGranted':False,'newRunDirectoriesPreserveFailures':True,'automaticPauseStillRequiredAfterPublication':True})
evidence('morning-preparation-source-proof.json',{'passed':True,'baseCommit':base,'historicPrefixSources':3857,'historicPrefixCanonicalSha256':sha(json.dumps(prefix,sort_keys=True,separators=(',',':')).encode()),'sourceHashes':hashes,'oldCodeAndEvidenceUnmodified':True,'privateDataAndBinariesExcluded':True})
stamp=datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
head=f'''# 夜间受控多WAN已封存；晨间最后审核待执行

更新：北京时间{stamp}。v20的三流跨WAN、五WAN队列/下行共享借用/RT优先级已在硬件证明；当前没有五WAN同时加速、正常程序新factory或长期常驻声明。v27首TCP超时发生在NSS前，端点/FW/客户端与05:19原完整路由器审核/两物理默认队列均恢复通过，e90c4a6已推送并实际archive验证。额外只读input规则顺序没有发现无条件末尾drop，不能借此确定TCP超时根因。

07:40晨间只读收尾入口已准备：[run.mjs](../code/work/morning-20261007/run.mjs)。依次原完整路由器审核、原两物理默认qdisc选项/handle对照、自有端点和canonical防火墙/端口、Windows自有客户端/发送器/守护/控制器核查；17个已知端点单元来自本地记录，05:31本地客户端库存为0。源码语法和默认inspect通过；**最后晨间现场审核尚未执行**。每次新目录保留失败，不重开生产实验。完成真实晨间结果、报告、检查/提交/推送/实际archive后暂停heartbeat，08:00前结束本轮授权。

当前无活跃实验或fixture，必要准备已完成；到07:40前若无新可执行条件，保持安静，不制造轮次或重复报告。无桌面/Steam/CS2/新下载；不盲重试五流或放宽源过滤/期限/认证。正常流入口v26仍只读0流、数据面复用v20，留下一次正常使用中验证，不要求挂机。

证据：[晨间准备，未执行](../evidence/morning-preparation.json)、[输入规则只读](../evidence/night-input-rule-order.json)、[追加源码](../evidence/morning-preparation-source-proof.json)。

## 保留的实测与失败

'''
for name in ['AGENTS.md','docs/STATE.md','docs/PLAN.md','docs/EXPERIMENT_LOG.md']:
    p=repo/name;h=head.replace('../code/','code/').replace('../evidence/','evidence/')if name=='AGENTS.md'else head;p.write_text(h+p.read_text(encoding='utf8'),encoding='utf8')
print(json.dumps({'passed':True,'newSources':len(hashes),'totalSources':len(m['sources']),'morningAuditPerformed':False}))
