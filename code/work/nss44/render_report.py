from pathlib import Path
import json,html,re
p=Path('outputs/nss44-mainline-observations.json');d=json.loads(p.read_text(encoding='utf-8'));a=d['actualAttempt'];c=d['readonlySchedulingCandidate'];f=d['passiveFollowup'];h=d['hashCandidate']
body=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NSS44 · 真人准入失败与发布来源</title>
<style>body{{max-width:1000px;margin:32px auto;padding:0 24px;font:16px/1.8 system-ui,"Microsoft YaHei",sans-serif;color:#203341;background:#f6f8fa}}h1{{font-size:30px}}h2{{margin-top:28px}}.box{{padding:18px;background:white;border-left:4px solid #ab5b37}}table{{width:100%;border-collapse:collapse;background:white}}td,th{{padding:10px;border-bottom:1px solid #dbe2e8;text-align:left}}a{{color:#126d86}}.muted{{color:#59707f}}</style>
<h1>NSS44：找到真人连接对，但仍未进入 NSS</h1>
<p class="box">真实 CS2＋Steam WAN1 连接对已识别。原 102 项入口在写前审核等待阶段拒绝：完整发布延迟超过 2 秒。没有 checkpoint、独立实验 owner、WAN/qdisc/tag/gate/ECM 改动，没有 software→NSS→software 或新的 CPU/游戏收益。本轮又捕获常驻分类器自然重启；最终新实例健康、保护配置和清理通过，但高负载稳定性仍未通过。</p>
<h2>本次真实尝试</h2><p>北京时间约 10:38:57 起，用户进入对局并保持 Steam。选中 WAN1，一条 bulk TCP＋一条 RT UDP，完整 mark 均 0x10000，zone 0、同 NAT 地址，应用归属新鲜。尚未执行原生 fast path 出口/NAT 校验，不能把候选相符写成加速 affinity 已通过。</p>
<p>原控制器终态 false 保留，102 份绑定源码冻结。5.06 秒内 {a['alignmentPolls']} 次健康发布观察，只有两个 full 来源序列，query→publish 为 2.91/3.01 秒，来源年龄 {a['sourceAgeRangeSeconds'][0]:.2f}–{a['sourceAgeRangeSeconds'][1]:.2f} 秒，全部不满足原 2 秒提示条件。更早一次原完整审核也因来源年龄 7.61 秒超过 6 秒拒绝。没有放宽任何时限，也没有继续试写。</p>
<h2>自然退出与恢复</h2><p>10:41:17 日志明确指出 software selector 写前快照过期；apply 子进程 rawStatus 256、耗时 3.79 秒。10:41:23 主 worker 记录失败，随后的 exactRecovery=false，恢复子进程 rawStatus 31744、6.18 秒。不能写成第一次恢复成功。没有注入 crash 或人工重启，是否受本轮观察或具体负载影响尚未证明。</p>
<p>procd 自动启动新 worker，guardian 保持。11:01:58 左右复核，新实例健康且与重启后检查相同；原完整 owned/native/配置审核通过，ECM 关闭且零计数，无事务、暂存、实验状态或模块。现网源码配置仍 NSS39；自然重启不能算长期稳定性通过。</p>
<h2>发布依赖的源码证据</h2><p>NSS39 worker 先写 classification.json，再同步软件规则 apply/audit，最后写 snapshot.json。NSS 分类消费者读前者；NSS42 写前等待器却读后者，要求新序列来源年龄小于 2 秒，再运行原完整审核。软件规则处理延迟能让等待器看不到符合条件的 full 发布。</p>
<p>后续 27.15 秒自然轻载被动窗：105 帧，观察 CPU 0.888 秒；classification 延迟 0.32–0.35 秒，snapshot 0.58–1.25 秒，完整跟踪 138–146 flows。LAN4 {f['performance']['lan4DownMbps']:.3f} Mbps、softirq {f['performance']['softirqPercent']:.2f}%、time_squeeze +0，包含观察开销。该窗未重新确认真人应用归属，不能和早先重载比较为 CPU 收益。</p>
<h2>只读候选与边界</h2><p>候选仅将调度提示来源换为既有 before-software-baseline 分类发布；仍要求新序列和小于 2 秒，验证 boot/config/producer/guardian 与 projection 元数据；随后仍执行原完整 snapshot/所有 owned/native 保护审核，原 6/9 秒判据不变。初始 1 秒、学习前 2 秒、调度内 5/外 6 秒、owner 45 秒、20 Mbps、一 TCP＋一 UDP 均保持。</p>
<p>一次目标路由器只读候选提示及原完整审核通过：提示来源年龄 {c['nativeHintSourceAge']:.2f} 秒，完整审核来源年龄 {c['nativeReadonlyFullAuditQueryAge']:.2f} 秒；NSS 准入权限始终 false。30 项离线 checksum/projection guard 与代码不变区检查通过，不是完整生命周期、真实高负载或新的生产入口资格。候选未用于生产，不修复 apply/recover 超时。</p>
<p>另测批量 payload SHA256 的未安装候选：每次仍查全部 12 份，无缓存，三对只读测量平均 {h['individualMeanMs']:.1f}→{h['batchMeanMs']:.1f} ms。只节省约 {h['savedMeanMs']:.1f} ms，测量为自然轻载且不计 hash 子进程 CPU，不能解释或解决几秒的发布延迟；不安装。</p>
<h2>下一步</h2><p>先稳定自动分类器在原时限内的 apply/recovery，并把正确的等待来源纳入新生产入口绑定和完整资格核验，再请求一次集中真人测试。当前不需要继续挂机或反复下载。不扩第二 WAN、共享预算、Wi-Fi、autorate 或五 WAN；不刷机、升级、改分区、全清 conntrack 或重建全部 qdisc；不提交上游 Issue/PR。</p>
<p class="muted">原始连接/日志/备份/模块保留私有，仅源码和脱敏证据进入仓库。HTML 源与链接检查通过；既有本地浏览器策略限制保留，未完成视觉渲染核验。</p>
<p><a href="nss44-mainline-observations.json">结构化证据</a> · <a href="https://github.com/ZyPulse-zy/athena-nss-mainline">私有研究仓库</a></p></html>'''
assert '\ufffd' not in body
for url in re.findall(r'href="([^"]+)"',body):
 if not url.startswith('https://'):assert (Path('outputs')/url).is_file()
Path('outputs/nss44-mainline-report.html').write_text(body,encoding='utf-8');d['reportVerification']['sourceValidated']=True;p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'reportSaved':True,'sourceValidated':True,'browserRendered':False}))
