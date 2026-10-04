"""Preserve prior rounds while recording the real high-load publication boundary."""
from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
s=json.loads((root/'evidence/nss67-mainline.json').read_text(encoding='utf-8'));assert s['conclusions']['testedAbove300MbpsPublicationWindowSupported']
assert s['finalState']['protectedAudit']['passed']and s['rollback']['automaticExpiryWithoutControllerRollback']
def write(p,text):(root/p).write_text(text,encoding='utf-8',newline='\n')
intro='''更新：2026-10-05，北京时间。最新为 NSS66–67；以下 NSS65 及更早章节是历史。

**发布候选已在真实 Steam 372 / 367 / 385 Mbps 窗口运行，高负载期间两次原完整审核 source3.62 / 4.41秒通过。两轮独立180秒自然撤销精确恢复。常驻仍47、ECM关闭全零；这不是新的NSS转发或CPU/真人收益验收。**

见 [NSS67实测](../evidence/nss67-mainline.json)、[实际窗口](../evidence/nss67-pipeline.json)、[最终审核](../evidence/nss67-final-audit.json)、[NSS66前一轮](../evidence/nss66-mainline.json) 和 [入口接续位置](PUBLICATION_ENTRY_HANDOFF.md)。

- 两轮各一个checkpoint，下载/SHA/gzip通过；各自独立480秒stage和独立180秒生产守护写前确认，再只改32,019字节publication worker及config.files/事务身份。四模块、分类策略/学习、PBR/NAT、生产根qdisc、原完整字段与1/2/6/9秒来源/6秒runner均未变。
- NSS66实际候选两窗209.06 /147.86Mbps；原完整审核source0.74 /1.74秒通过，不能拿Steam331.7Mbps界面峰值当整窗300Mbps。前两公共负载探针403/429失败保留，429后停止不重试。
- NSS67三个候选四秒窗371.50 /366.78 /385.08Mbps、30.7k/30.3k/31.8k pps；busy84.51 /78.70 /82.36%，softirq60.72 /51.89 /55.77%，squeeze+11 /0 /0。含观察器成本、负载未控制，不构成CPU因果对照。候选完整快照实际145–285条；审核与四秒流量窗相邻，不是同窗。
- 候选worker31721/guardian31722/producer连续，轻载/启动审核source1.63，以及两次高负载期间原完整审核3.62 /4.41秒，全部保留原6秒限期。支持本次高负载publication可运行，不能保证所有峰值、长期恢复或新NSS入口成功。
- NSS66/67各保留一次到期后候选context审核拒绝：生产独立期限已过、原配置已恢复，候选SHA不符，在配置断言即拒绝；不是source超时。失败输出不覆盖，之后恢复后的原审核通过。NSS67失败窗口仅10ms，计数统计不作性能证据。
- 两轮均未发控制器回滚命令，180秒自然撤销精确恢复旧worker/config/指针及四模块；之后精确owner/inode取消stage，不声称该stage自然480秒到期。NSS67恢复后同窗原完整审核314.06Mbps/source5.97秒通过，距原6秒仅0.03秒，不能保证稳定，也不是与候选的同负载比较。
- 01:09最终完整保护审核/清理通过，worker9454/guardian9455/source2.22秒，常驻47/config478818…a900，ECM关闭全零，无事务/stage/state/gate/qdisc模块；不是旧20030/20031连续实例。
- 已授权Steam库内负载：Disco Elysium 8.7GB自然完成；首个360秒客户端守护确实自然执行精确Steam实例-shutdown。随后黎明杀机放D盘（要求61.01GB、可用298.21GB），短测到17%已暂停，网络/磁盘0bps，守护随后取消，317KB旧安排未操作。无购买/卸载/游戏启动/CS2/HUD/真人体验；部分下载保留暂停。
- NSS63入口241项保持，未新绑候选入口或放行ECM；本轮publication试装不是NSS准入资格。两个保留部署与消费者/审核/stage的实际context需统一绑定后，才集中做现有暂停下载＋真实CS2的单WAN可比A/B/A2。
- 22份新增白名单源/累计845，14份实际完整运行输入仅私有冻结；旧65/runtime原字节留存，旧64及更早证明保持。未重跑旧36/29或99/13，未提交上游。报告源验证通过，浏览器渲染未核验。

**下一步只做候选实际保留部署与NSS入口的精确重绑定，再集中一次真人CS2＋现有暂停下载的可比A/B/A2。** 不再重复轻载试装或大游戏准备，不重装分类器、放宽门槛、扩第二WAN/共享预算。

'''
state=(root/'docs/STATE.md').read_text(encoding='utf-8')
if '最新为 NSS66–67'not in state.splitlines()[2]:write('docs/STATE.md',state.splitlines()[0]+'\n\n'+intro+'## NSS65历史\n\n'+state.split('\n\n',2)[2])
plan='''# 下一步：精确绑定候选部署，再集中单WAN闭环

NSS67已在真实372/367/385Mbps窗口运行发布候选，高负载期间两次原完整审核3.62/4.41秒通过；180秒自然回滚精确恢复47，ECM关闭全零。无需重复轻载试装、旧合同准备或新游戏下载。见 [状态](STATE.md) 与 [接续调用位置](PUBLICATION_ENTRY_HANDOFF.md)。

1. 只读核验当前47/config478818…a900和实际9454/9455；每轮重新读实际实例，不沿用旧producer、过期trial或旧别名。已有暂停的黎明杀机负载可复用，不要求用户反复重下。
2. 在checkpoint与独立撤销保护下形成候选的实际保留部署。消费者、原完整审核与NSS stage必须共同绑定正确base/config/worker/producer和已验证部署；不能将committed:false的180秒试装直接冒充已提交部署、覆盖原资格或混淆45秒NSS owner。详见接续文档。
3. 新轮次入口保留原241项所有输入及原证明，对实际变更的context传递单独验证/绑定，全部原断言、来源1/2/6/9秒、200ms child、20Mbps、一TCP一UDP、45秒owner保持。高负载publication成功不是新的NSS入口资格。
4. 集中真实CS2和已有下载，一次完成同流同WAN software→NSS→software、实际bulk/RT leaf与完整ct mark/NAT/affinity、HUD jitter/loss/Miss及真人体验。先判断LAN4/单WAN/受控份额/吞吐可比，再解释softirq/time_squeeze；未通过前不扩其它支线。

'''
old=(root/'docs/PLAN.md').read_text(encoding='utf-8')
if not old.startswith(plan):write('docs/PLAN.md',plan+'## NSS65历史计划\n\n'+old.split('\n\n',1)[1])
brief='''最新NSS66–67（下方65及更早为历史）：publication候选32,019字节在真实372/367/385Mbps、约3万pps运行；高负载期间原完整审核source3.62/4.41<6通过，含观察器且非同窗CPU对照。66实际209/148Mbps，仅较低负载。两轮各checkpoint+独立180秒自然撤销精确恢复原47/config/指针、四模块不变，stage后按owner/inode取消；两次到期context SHA拒绝原失败保留，非source超时。01:09原完整最终审核/清理通过，worker9454/guardian9455/source2.22，ECM关闭全零，无事务/stage/state/模块。恢复后原审核同窗314Mbps/source5.97，仅0.03秒余量非稳定证明。Disco Elysium8.7GB完成；黎明杀机D盘17%已暂停、网络/磁盘0bps，未购买/卸载/启动游戏，独立客户端360秒首轮自然-shutdown实际验证、后续确认完成/暂停才取消。NSS63/241项不变，无新候选入口/ECM放行/CS2/HUD/真人或CPU验收。22新源/累计845、14完整实际输入私有冻结，旧65runtime原字节保持。下一步候选实际保留部署与消费者/原审核/stage共同精确绑定，然后集中现有暂停下载+真实CS2单WAN可比A/B/A2；不重复轻载试装/旧36/29/99/13/新下载准备/重装/扩WAN。STATE为准。'''
agents=(root/'AGENTS.md').read_text(encoding='utf-8')
if brief not in agents:
 at=agents.index('最新NSS65');write('AGENTS.md',agents[:at]+brief+'\n\n'+agents[at:])
local=root.parent/'AGENTS.md';text=local.read_text(encoding='utf-8')
if '- '+brief not in text:
 at=text.index('- 最新NSS65');local.write_text(text[:at]+'- '+brief+'\n'+text[at:],encoding='utf-8',newline='\n')
readme=(root/'README.md').read_text(encoding='utf-8');heading,body=readme.split('\n\n',1)
if not body.startswith('最新 [NSS67]'):write('README.md',heading+'\n\n最新 [NSS67](evidence/nss67-mainline.json)：发布候选在372/367/385Mbps真实Steam负载运行，高负载原完整审核3.62/4.41秒通过；独立180秒自然撤销精确恢复47，ECM关闭全零。下一步精确绑定候选实际部署再集中单WAN真人闭环；不是NSS/CPU/游戏收益验收。先读 [STATE](docs/STATE.md)、[PLAN](docs/PLAN.md)。下方65等为历史。\n\n'+body)
log=(root/'docs/EXPERIMENT_LOG.md').read_text(encoding='utf-8')
if '## 2026-10-05 NSS66–67：'not in log:write('docs/EXPERIMENT_LOG.md',log+'''
## 2026-10-05 NSS66–67：真实300Mbps以上完整发布与独立恢复

- NSS66公共负载探针403/429失败，429后停止不重试、不执行payload；随后已授权Disco Elysium下载。首次客户端360秒自然执行精确实例-shutdown，00:44:57确认原进程退出。publication候选00:46单项试装，经checkpoint下载/SHA/gzip和独立180秒守护；候选实际209/148Mbps，原审核source0.74/1.74通过。到期后继续用候选context的SHA断言拒绝失败保留，00:50自然精确恢复/完整审核/清理通过，12843/12844。下载8.7GB完成，网络/磁盘0，第二客户端守护取消。
- NSS67复用同候选，00:55在新的checkpoint/独立守护核验后试装，D盘已授权黎明杀机负载。候选四秒窗口371.50/366.78/385.08Mbps、约3万pps，busy84.51/78.70/82.36、softirq60.72/51.89/55.77、squeeze+11/0/0，含观察器成本，负载不匹配，不是NSS转发或CPU A/B。
- 原完整审核：启动source1.63，00:56:20和00:57:28高负载期间3.62/4.41秒通过，同31721/31722/producer；原6/9秒与完整字段未改。审核和四秒流量窗是相邻窗口，不冒充同窗观测。只有publication变量，四模块/学习/PBR/NAT/生产根qdisc/gate保持。
- 180秒独立生产恢复已自然执行；00:58:40晚到的候选context审核在配置SHA拒绝，10ms统计不作性能证据。00:59:14原worker/config/指针及四模块恢复通过，之后按精确owner/inode取消stage，非stage自然480秒到期。恢复后原完整审核同窗314.06Mbps/source5.97秒通过，余量0.03秒，不能保证长期稳定或证明候选CPU收益。
- 00:59约17%暂停黎明杀机，随后界面网络/磁盘0、旧317KB安排未操作，01:00:53取消客户端守护。01:09:58原完整最终审核/保护配置/清理通过，9454/9455/source2.22、常驻47/config不变、ECM全零，无事务/stage/state/模块。无游戏启动/购买/卸载/CS2/HUD或真人体验。
- 22份白名单源、累计845与14份实际完整运行输入私有冻结；旧65runtime原字节保持，36/29及99/13不重跑，241项NSS入口不变，本轮publication未当NSS准入。下一步精确绑定候选实际保留部署、消费者/原审核/stage，再集中现有下载和真实CS2可比A/B/A2，不扩大WAN或其它支线。
''')
index=(root/'docs/ARTIFACT_INDEX.md').read_text(encoding='utf-8')
if '## NSS66–67：'not in index:write('docs/ARTIFACT_INDEX.md',index+'''
## NSS66–67：真实下载发布、独立精确恢复和入口接续

- [NSS66实测](../evidence/nss66-mainline.json)、[NSS67实测](../evidence/nss67-mainline.json)、[300Mbps以上窗口](../evidence/nss67-pipeline.json)、[最终审核](../evidence/nss67-final-audit.json)。
- [10份NSS66源码](../evidence/nss66-source-proof.json)、[12份NSS67源码](../evidence/nss67-source-proof.json)、[保留的NSS65 runtime](../evidence/nss65-runtime.json)、[NSS66 runtime](../evidence/nss66-runtime.json)。
- [单项试装](../code/work/nss67/publication-trial.mjs)、[精确独立恢复](../code/work/nss67/verify-rollback.mjs)、[入口接续的三个来源位置](PUBLICATION_ENTRY_HANDOFF.md)。
- 本地 `outputs/nss67-mainline-report.html` 与 `work/nss66/`、`work/nss67/` 保存完整私有资料；配置/checkpoint/owner/CT/socket/截图未上传。本轮没有新NSS入口资格或真人/CPU验收。
''')
issue=(root/'docs/ISSUE_JSON_PUBLICATION_COST.md').read_text(encoding='utf-8')
if '## NSS67 实际高负载补证'not in issue:write('docs/ISSUE_JSON_PUBLICATION_COST.md',issue+'''
## NSS67 实际高负载补证

32,019字节候选在372/367/385Mbps真实Steam窗口运行，高负载期间两次完整原审核3.62/4.41秒通过、原6秒门槛保持；独立180秒自然恢复精确通过。见 [NSS67](../evidence/nss67-mainline.json)。完整snapshot观察145–285条，发布时间标记在编码前，采样可见时间不能直接等于编码成本。窗口包含观察器且负载未控制，不能将整机busy/softirq差异归于JSON或NSS。

候选未留驻，NSS未开放；两次到期context配置SHA拒绝及之后恢复成功分别保留。不改写NSS63原source7.41失败，也不保证所有高峰或长期稳定。上游精确二进制commit仍未确认，本问题继续为潜在Issue/PR backlog，未提交上游。
''')
print('NSS66/67 measured docs updated; histories retained.')
