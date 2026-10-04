"""Append NSS64 findings while retaining earlier documents as labeled history."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
def rewrite(path,text):(root/path).write_text(text,encoding='utf-8',newline='\n')
state=(root/'docs/STATE.md').read_text(encoding='utf-8');assert '最新为 NSS63' in state.splitlines()[2]
preface='''更新：2026-10-04，北京时间。最新为 NSS64；以下 NSS63 及更早章节是历史。

**常驻仍 NSS47，ECM 关闭全零。完成完整字段一致的 JSON 发布候选：真实319条快照编码 CPU 179.06→136.22 ms（−23.92%），目标精确32,019字节编译通过，尚未安装。没有新增NSS放行、整机收益或真人闭环。**

见 [本轮](../evidence/nss64-mainline.json)、[完整编码](../evidence/nss64-encoding.json)、[规模测量](../evidence/nss64-scale.json)、[被动链路](../evidence/nss64-pipeline.json) 和 [问题候选](ISSUE_JSON_PUBLICATION_COST.md)。

- 原NSS63失败：query→发布时间标记3.84秒，提示消费完成约5.47秒；交接0.29秒、哈希0.35 / journal0.03 / selector0.51 / 完整解析0.76秒，最终source7.41>6。标记在编码前采样，不是rename；不能将之后全部时间归于JSON。
- 最新目标RAM36投影/29完整编码案例通过，包括共享引用、循环/错误值/键拒绝、slot map和未知字段。不同组不宣称唯一独立案例总数，旧99/13未重跑。三对计时用同一冻结真实内存夹具；不是高网络负载或整机A/B。
- 仅编码规模128/256/512/1024条：旧29.96/64.54/156.96/422.87ms CPU，分块23.77/55.39/108.93/198.18ms，完整解析字段一致；投影CPU不在此组内。是离线形状重复，不是实际CT/准入资格。上游JSON-C线性visited查重与趋势相符，目标二进制精确commit未确认。
- 候选 `work/nss64/candidate-worker.lua` 只改完整快照JSON边界，非快照序列化和其余worker字节不变；全部字段/原完整审核、分类策略/学习、PBR/ct mark/NAT/gate、所有期限不变。目标SHA精确编译，未执行watch、安装或绑定新NSS入口；当前仍NSS63/241项。
- 首次2048组合模拟六秒runner返回124；观察器初版请求不支持时长，在执行Lua前返回2。原失败保留，没有提高六秒上限。随后分拆和四秒自然观察通过；没有生产配置写入、checkpoint或新回滚试验。
- 自然4.03秒：LAN4 0.023Mbps /18.11pps，busy17.04%、softirq3.21%、time_squeeze+0，含观察器成本。两个完整周期query→可见约0.63–0.86秒，stamp→可见约20–80ms观测窗。没有高负载/HUD/体感或同负载转发结论。
- 23:15原完整审核/清理通过、source2.61秒，同worker20682/guardian5412/producer，NSS47/config不变。ECM全零，无事务/暂存/state/实验gate/qdisc模块。未操作游戏GUI/新下载；未刷新客户端Steam/HUD，旧客户端状态不当新验证。
- 20份源码冻结、累计815，旧NSS63及更早runtime原字节保留，完整私有数据不上传。只证明最新native合同和编译，不增加准入/高负载稳定资格。报告源检查通过，浏览器渲染未核验；未提交上游。

**下一步直接做publication边界单项短测：checkpoint、独立超时撤销，保留原完整审核与期限；原47能精确恢复后再测真实高负载发布与可比单WAN A/B/A2。** 不重装整套分类器、重复已完准备、用新游戏维持准备或扩WAN/共享预算。

## NSS63历史

'''
rewrite('docs/STATE.md',state.splitlines()[0]+'\n\n'+preface+'\n'.join(state.splitlines()[4:])+'\n')
plan=(root/'docs/PLAN.md').read_text(encoding='utf-8');assert plan.startswith('# 下一步：')
rewrite('docs/PLAN.md','''# 下一步：单项发布试验，再完成可比A/B/A2

最新NSS64：完整字段一致的JSON发布候选、真实快照编码CPU约23.92%改善、目标精确编译通过；尚未安装。现网仍NSS47、ECM关闭全零、NSS63入口241项。见 [状态](STATE.md) 和 [候选](ISSUE_JSON_PUBLICATION_COST.md)。

1. 直接核验20份冻结源、候选SHA和当前47配置/实例。无需重跑旧99/13或本轮已完成的合同/编译，也不用挂游戏或安装大游戏维持准备。
2. 为publication边界单项准备精确旧worker/config/指针恢复；checkpoint下载/哈希/gzip、独立超时守护写前核验后才短时变更。保持完整字段/原审核/source/owner期限，失败定位后精确撤销。编码收益是否补上高负载缺口仍未证明，不因希望通过而延长期限或扩大改动。
3. 真实高负载publication→完整审核在原门槛内通过后，集中做单WAN同TCP/UDP流、负载可比software→NSS→software A/B/A2及实际HUD/真人体验；通过后才扩第二WAN/共享预算/Wi-Fi/autorate。

## NSS63历史计划

'''+plan.split('\n\n',1)[1])
agents=(root/'AGENTS.md').read_text(encoding='utf-8');at=agents.index('最新 NSS63')
latest='''最新NSS64（下方63及更早“最新”为历史）：只读定位和JSON发布边界候选，常驻47/config不变、ECM关闭全零。真实319条三对编码CPU179.06→136.22ms（−23.92%），规模夹具完整字段相同，不是整机/高負载收益。最新native36投影/29完整编码，32,019字节候选目标SHA精确编译，未执行watch/安装，NSS63入口241项保持。2048组合runner124/观察器时长2失败保留、六秒不放宽。自然4.03秒仅0.023Mbps。23:15原完整审核/清理通过、同worker20682/guardian5412/producer/source2.61，无事务/暂存/state/模块；无游戏GUI/新下载/生产配置写入/新checkpoint或回滚试验。20源码冻结/累计815，旧63runtime原字节保留。下一步只做publication单项checkpoint+独立撤销短测，再测高负载原完整审核与集中可比A/B/A2；不重装整套分类器、重复已完准备、用新游戏维持准备或扩WAN。STATE开头为准。

'''.replace('高負载','高负载')
rewrite('AGENTS.md',agents[:at]+latest+agents[at:])
readme=(root/'README.md').read_text(encoding='utf-8');head,rest=readme.split('\n\n',1)
rewrite('README.md',head+'''\n\n最新 [NSS64](evidence/nss64-mainline.json)：完整JSON发布候选、319条真实快照编码CPU约23.92%改善、目标精确编译；尚未安装，整机/高负载收益未验证。现网仍47、ECM关闭全零，原完整审核/清理通过。下一步直接单项checkpoint/独立撤销发布测试，再补可比单WAN A/B/A2；不重复准备或继续装新游戏。先读 [STATE](docs/STATE.md)、[PLAN](docs/PLAN.md) 和 [候选](docs/ISSUE_JSON_PUBLICATION_COST.md)。下方NSS63为历史。

'''+rest)
log=(root/'docs/EXPERIMENT_LOG.md').read_text(encoding='utf-8')
rewrite('docs/EXPERIMENT_LOG.md',log+'''
## 2026-10-04 NSS64：完整发布编码候选，只读与RAM资格

- 常驻NSS47不变。开场/23:15收尾原完整持锁审核与清理通过，同worker20682/guardian5412/producer，source1.38→2.61秒；ECM关闭全零，无事务/暂存/state/gate或qdisc模块。未操作GUI/下载，客户端历史状态未刷新；无配置写入/checkpoint/新增自动回滚试验。
- 拆解NSS63原source7.41失败：query→stamp3.84秒、提示消费结束5.47秒、交接0.29/哈希0.35/journal0.03/selector0.51/完整解析0.76秒。stamp在编码前，rename未直接计时，提示读耗时未分离，不能把全部后stamp时间当编码。
- 原投影内联scalar候选native36通过、真实82条投影约12%改善，仅作为该轮早期候选。完整分块编码原投影25/29案例分别通过；最新快速投影＋分块完整边界native36/29通过，真实319条冻结同内存夹具三对原179.06/新136.22ms CPU、−23.92%。36/29不是独立唯一案例数，也不重算旧99/13。没有实际高网络负载或整机收益。
- 预投影512/1024真实形状规模的纯编码156.96→108.93 /422.87→198.18ms CPU，全部字段相同；不计投影CPU，不是真实512/1024条CT或NSS准入。C函数身份已确认，上游visited线性扫描与趋势吻合；目标二进制精确commit未证明。仅本地Issue候选，未提交上游。
- 首次2048组合模拟六秒runner返回124自动结束，失败保留；观察器初版请求超过runner支持范围，执行Lua前返回2。改为原六秒内四秒观察，没有扩大限额。自然4.03秒，LAN4约0.023Mbps、18.11pps、busy17.04/softirq3.21%、squeeze0，包含0.226 CPU秒观察器成本；两个完整周期0.63–0.86秒可见，stamp→可见观测窗20–80ms，只是轻载。
- 单项候选worker32,019字节精确目标RAM编译/SHA通过，剥离该边界补丁与原28,919字节worker逐字节相同；非快照序列化保持原式。未执行watch、安装、改原模块或绑定新NSS入口。策略/学习/字段/原完整解析/审核/PBR/ct mark/NAT/gate及全部期限未变，当前仍NSS63/241项。
- 20份源码冻结/累计815，原63 runtime与全部旧证明按字节保持，原始连接/配置/CT与私有输出不上传。输出中originalJsonProjectionRetained旧布尔已注明指合同、不是同一函数，原raw保留。源码/报告源检查通过，浏览器渲染未验证。下一步直接publication边界checkpoint+独立撤销单项试验，再高负载完整审核和集中单WAN可比A/B/A2，不重装/重放旧准备/扩WAN。
''')
index=(root/'docs/ARTIFACT_INDEX.md').read_text(encoding='utf-8')
rewrite('docs/ARTIFACT_INDEX.md',index+'''
## NSS64

- [本轮只读/候选](../evidence/nss64-mainline.json)、[完整编码](../evidence/nss64-encoding.json)、[编码规模](../evidence/nss64-scale.json)、[被动发布链路](../evidence/nss64-pipeline.json)。
- [原NSS63拒绝拆分](../evidence/nss64-latency.json)、[精确编译](../evidence/nss64-compile.json)、[最终原审核](../evidence/nss64-final-audit.json)、[20份冻结源](../evidence/nss64-source-proof.json)。
- [publication候选worker](../code/work/nss64/candidate-worker.lua)，未安装/未授予准入；[潜在Issue](ISSUE_JSON_PUBLICATION_COST.md) 未提交。
- 本地 `outputs/nss64-mainline-report.html` / `work/nss64/` 保存报告与完整私有证据；原始连接、配置和截图不上传。
''')
print('NSS64 current docs updated; NSS63 and earlier history retained.')
