"""NSS65 is a live trial and undo, not high-load performance acceptance."""
from pathlib import Path
import json
root=Path(__file__).resolve().parents[1];data=json.loads((root/'evidence/nss65-mainline.json').read_text())
assert data['rollback']['automaticExpiryWithoutControllerRollback']and data['finalState']['protectedAudit']['passed']
def rewrite(p,s):(root/p).write_text(s,encoding='utf-8',newline='\n')
state=(root/'docs/STATE.md').read_text(encoding='utf-8');assert any('最新为 '+v in state.splitlines()[2]for v in ['NSS64','NSS65'])
latest='''更新：2026-10-05，北京时间。最新为 NSS65；以下 NSS64 及更早章节是历史。

**完整JSON发布候选已实际短时运行，两次原完整审核通过；独立180秒自然撤销精确恢复原worker/config/版本指针。常驻仍47，ECM关闭全零。高负载发布、整机CPU与真人闭环仍未验收。**

见 [现场试验](../evidence/nss65-mainline.json)、[自然发布窗口](../evidence/nss65-pipeline.json)、[恢复后原审核](../evidence/nss65-final-audit.json) 和 [冻结源](../evidence/nss65-source-proof.json)。

- checkpoint下载/SHA/gzip通过；独立480秒暂存守护与独立180秒生产撤销在写前分别验证，生产守护PPID1、命令/启动身份/boot/checkpoint/deadline均符合原条件。没有控制器主动回滚命令，自然到期恢复通过。
- 只替换32,019字节publication worker及其config.files/事务身份，其余四个模块未写入；分类策略/学习、PBR/ct mark/NAT/gate、完整字段/原审核及全部原期限不变。只发生分类器的试装/恢复restart，未重装整套分类器、重建十个生产根qdisc或开放NSS。
- 候选期间同worker9414/guardian9415/producer，sequence16→37，两次原完整持锁审核source2.69/1.78秒。之后精确旧worker/config SHA、原四模块SHA与版本指针核验，恢复后00:04完整审核/清理通过，worker20030/guardian20031/source2.43；不是旧实例连续。
- 两个四秒候选窗及一个恢复窗只有0.025/0.031/0.018Mbps，pps11.5/17.6/8.2、squeeze均0；busy16.50/15.21/21.11%，softirq4.61/0.13/5.12%，背景负载不匹配且包含观察器成本。完整周期首次可见约0.77/0.73/0.85秒，仅观测界限，不能比较CPU收益或声称高负载发布修复。
- 生产自动恢复已证明后，精确owner/inode取消本轮暂存，无事务/stage/state/gate或qdisc模块；不声称该stage自然480秒到期。候选未留驻，常驻47配置478818…a900不变，ECM全零。
- NSS63入口241项保持，没有为临时候选创建新NSS入口绑定，也没有NSS加速、真实Steam高负载、CS2 HUD/真人体验或可比A/B/A2。本轮不重跑旧36/29及99/13、不操作游戏GUI或新下载。
- 8份公开白名单源码冻结/累计823，另8份实际owner/完整输入原字节仅私有；旧64及更早runtime按字节保留，未提交上游。报告源检查通过，浏览器渲染未核验。

**下一步直接沿用已通过的单项试装/精确恢复路径，做真实高负载publication→原完整审核；在实际候选输入正确绑定后集中单WAN同流同负载A/B/A2。** 不重装/重放已完准备、用新游戏维持准备或扩WAN/共享预算。

## NSS64历史

'''
if '最新为 NSS65'not in state.splitlines()[2]:rewrite('docs/STATE.md',state.splitlines()[0]+'\n\n'+latest+'\n'.join(state.splitlines()[4:])+'\n')
plan=(root/'docs/PLAN.md').read_text(encoding='utf-8')
if '最新NSS65'not in plan.split('\n\n')[1]:rewrite('docs/PLAN.md','''# 下一步：真实高负载发布审核，再完成可比A/B/A2

最新NSS65已完成publication候选现场试装、两次原审核和独立180秒自然精确恢复，常驻47、ECM关闭全零。无需重复轻载试装、分类器安装或旧合同准备。见 [状态](STATE.md)。

1. 每轮先读当前47配置与实际新实例20030/20031并核验原完整审核；不要沿用20682或候选9414的producer。旧64/63所有失败和证据不覆盖。
2. 在真正高负载窗口复用本轮单项publication trial/undo，保持checkpoint下载验证、独立撤销、全部字段/原审核/source期限。记录完整publish和消费者成本，判断原source7.41>6的缺口是否补上；自然0.02–0.03Mbps和编码夹具不能替代。不要用新游戏维持准备。
3. 只在候选实际配置/worker/producer与完整输入正确绑定后使用集中单WAN真实CS2+Steam配对。保留NSS63的241项全部原输入或精确等义重绑定证明，不能把本轮试装当新NSS入口资格。20Mbps、一TCP一UDP、45秒owner、1/2/6/9秒source及200ms child条件不变。
4. 做完整同流同负载software→NSS→software A/B/A2，记录LAN4/单WAN/受控leaf份额、softirq、time_squeeze、实际HUD jitter/loss/Miss/真人体验。负载不可比或A2缺失即未验收，之后才扩第二WAN/共享预算/其它支线。

## NSS64历史计划

'''+plan.split('\n\n',1)[1])
brief='''最新NSS65（下方64及更早为历史）：publication候选32,019字节实际短时运行，两次原完整审核source2.69/1.78通过；checkpoint/独立180秒撤销写前核验，自然到期精确恢复旧worker/config/指针，四模块未变。候选worker9414/guardian9415同producer；00:04恢复后完整审核/清理通过，常驻47配置不变、worker20030/guardian20031/source2.43，ECM关闭全零，无事务/暂存/state/模块。三个自然窗0.025/0.031/0.018Mbps，非同负载，不能算CPU或高负载收益。stage在生产自然恢复后按owner/inode取消，未宣称480秒自然到期。NSS63/241项不动、没有新候选入口绑定/高负载/游戏GUI/下载/真人指标，旧36/29和99/13未重跑。8份白名单源/累计823，8份实际完整输入私有冻结，旧64runtime原字节留存。下一步直接高负载完整发布/原审核与正确绑定后的集中可比单WAN A/B/A2，不重装/重放/扩WAN/新游戏维持准备；STATE为准。

'''
agents=(root/'AGENTS.md').read_text(encoding='utf-8');at=agents.index('最新NSS64')
if brief not in agents:rewrite('AGENTS.md',agents[:at]+brief+agents[at:])
readme=(root/'README.md').read_text(encoding='utf-8');head,rest=readme.split('\n\n',1)
if not rest.startswith('最新 [NSS65]'):rewrite('README.md',head+'\n\n最新 [NSS65](evidence/nss65-mainline.json)：JSON发布候选现场试装/两次原完整审核通过，独立180秒自然撤销精确恢复；常驻47、ECM关闭全零。自然轻载不能验收高负载/整机CPU或真人收益。下一步直接高负载发布审核与正确绑定的集中单WAN A/B/A2。先读 [STATE](docs/STATE.md)、[PLAN](docs/PLAN.md)，下方NSS64为历史。\n\n'+rest)
log=(root/'docs/EXPERIMENT_LOG.md').read_text(encoding='utf-8')
if '## 2026-10-05 NSS65：'not in log:rewrite('docs/EXPERIMENT_LOG.md',log+'''
## 2026-10-05 NSS65：publication现场单项试装与自然精确恢复

- 23:56开场原完整审核通过，旧20682/5412。创建一个checkpoint并下载/SHA/gzip核验，先证明独立480秒暂存守护，再证明PPID1且身份/boot/期限/CP绑定的180秒生产撤销，然后仅替换完整snapshot序列化worker32,019字节与config.files/事务身份。四模块、策略/学习、PBR/NAT/gate、root qdisc及原期限保持。
- 候选期间00:00:59和00:02:01两次原完整持锁审核通过，source2.69/1.78秒，worker9414/guardian9415/producer连续，sequence16→37。NSS始终关闭零计数；不是新的241项入口资格。
- 00:03独立180秒自然到期，不发控制器回滚命令；00:03:19已核验rolled-back日志、旧worker/config SHA/指针、四模块SHA、健康fresh snapshot。随后精确stage owner/inode取消本轮暂存；不是该stage自然480秒到期证明。
- 00:04:20原完整审核/保护配置/清理通过，worker20030/guardian20031/source2.43秒，常驻47/config不变，ECM全零、无事务/stage/state/实验模块。实例变化是本轮试装及恢复restart，不能声称原producer/PID连续。
- 两个候选自然窗和一个恢复自然窗：0.025/0.031/0.018Mbps，busy16.50/15.21/21.11%、softirq4.61/0.13/5.12%、squeeze+0，均含观察器成本，未匹配负载。完整周期query→首次可见0.77/0.73/0.85秒为观测界限，不证明高负载来源过期已解决或CPU/游戏收益。
- 不重跑旧36/29与99/13；无GUI、新下载、真实CS2/Steam高负载/HUD/真人体验、NSS放行或A/B/A2。8份白名单源码/累计823和8份完整实际私有输入冻结，旧64/runtime与历史证据保留，未提交上游。下一步直接高负载原完整发布/审核及候选正确绑定后的集中可比单WAN闭环。
''')
index=(root/'docs/ARTIFACT_INDEX.md').read_text(encoding='utf-8')
if '## NSS65：'not in index:rewrite('docs/ARTIFACT_INDEX.md',index+'''
## NSS65：现场publication试装与独立自然恢复

- [主线结果](../evidence/nss65-mainline.json)、[自然窗口](../evidence/nss65-pipeline.json)、[恢复后审核](../evidence/nss65-final-audit.json)、[8份白名单源](../evidence/nss65-source-proof.json)。
- [单项试装](../code/work/nss65/publication-trial.mjs)、[独立自然恢复核验](../code/work/nss65/verify-rollback.mjs)。候选没有留驻，也没有新NSS入口绑定或高负载/游戏收益。
- 本地 `outputs/nss65-mainline-report.html` / `work/nss65/` 保留报告与完整私有checkpoint/config/owner/实际输入；未上传。
''')
workspace=root.parent;local=workspace/'AGENTS.md';s=local.read_text(encoding='utf-8');at=s.index('- 最新NSS64')
if '- '+brief.strip()not in s:local.write_text(s[:at]+'- '+brief.strip()+'\n'+s[at:],encoding='utf-8',newline='\n')
print('NSS65 current docs updated; prior histories retained.')
