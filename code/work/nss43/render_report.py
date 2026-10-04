"""Render source-only HTML. No browser-policy workaround or fabricated game data."""
from pathlib import Path
import json,html,re
p=Path('outputs/nss43-mainline-observations.json');d=json.loads(p.read_text(encoding='utf-8'));s=d['steamProfile'];perf=s['performance'];interfaces=perf['interfaces']
esc=lambda v:html.escape(str(v))
rows=''.join(f"<tr><td>WAN{wan}</td><td>{interfaces['rpwan'+wan]['rxMbps']:.2f}</td><td>{r['observedInstances']}</td><td>{r['wholeWindowInstances']}</td><td>{r['highestWholeWindowCtReplyMbps']:.2f}</td></tr>" if r['highestWholeWindowCtReplyMbps'] is not None else f"<tr><td>WAN{wan}</td><td>{interfaces['rpwan'+wan]['rxMbps']:.2f}</td><td>{r['observedInstances']}</td><td>{r['wholeWindowInstances']}</td><td>未取得</td></tr>" for wan,r in s['byWan'].items())
parts=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">',
'<title>NSS43 · Steam 负载与受控份额</title><style>body{max-width:1040px;margin:32px auto;padding:0 22px;font:16px/1.75 system-ui,"Microsoft YaHei",sans-serif;color:#182b39;background:#f5f8fa}h1{font-size:30px}h2{margin-top:30px}table{border-collapse:collapse;width:100%;background:white}th,td{padding:10px;text-align:left;border-bottom:1px solid #dbe4eb}.box{background:white;border-left:4px solid #247277;padding:14px 20px}.muted{color:#526777}a{color:#136b85}code{font-size:.9em}</style>',
'<h1>NSS43：先量清单连接能接管多少流量</h1>',
'<p class="box">本轮完成 Steam 只读负载测量和离线预算分析。现网仍为 NSS39，NSS 未开启，20 Mbps 预算、一条 TCP＋一条 UDP、45 秒独立 owner 均未改变。下一次集中验证真人闭环；本轮没有新的 CPU 收益或游戏体验结论。</p>',
f"<h2>实际窗口</h2><p>{esc(s['startedAt'])}–{esc(s['finishedAt'])}（UTC；北京时间加 8 小时），路由器计数窗口 {s['seconds']:.2f} 秒，13/13 次成功，每次匹配新鲜 Steam socket 与分类器 CT。没有 CS2 对局候选，没有生成额外负载。</p>",
f"<p>LAN4 平均 {interfaces['lan4']['txMbps']:.2f} Mbps / {interfaces['lan4']['txPps']:,.0f} pps；4 秒窗口 {s['lan4IntervalMbpsRange'][0]:.2f}–{s['lan4IntervalMbpsRange'][1]:.2f} Mbps，变异系数 {s['lan4IntervalCoefficientOfVariation']*100:.2f}%。busy {perf['busyPercent']:.2f}%，softirq {perf['softirqPercent']:.2f}%，time_squeeze +{perf['timeSqueezeDelta']}，softnet dropped +{perf['softnetDroppedDelta']}。这些数据包含观察程序开销。</p>",
'<h2>各 WAN 与连接持续性</h2><table><thead><tr><th>WAN</th><th>接口 RX / Mbps</th><th>观测实例数</th><th>全窗连接数</th><th>最大全窗 CT reply / Mbps</th></tr></thead><tbody>'+rows+'</tbody></table>',
'<p>每帧活跃 bulk 候选 13–16 条，全窗合计 23 个 CT 实例；部分连接退出或重建。WAN5 没有贯穿全部样本的单条连接，短时约 49 Mbps 的连接只出现两个样本，不能拿来设计稳定高负载实验。CT reply 窗与接口窗时钟略有不同，速率不是 Steam 应用载荷，也不是精确 fast path 占比。</p>',
'<h2>是否应提高 20 Mbps 预算</h2><p>以这次软件路径的全窗连接速率固定不变作离线敏感性分析：WAN1 上限 20→30 Mbps 对应约 7.20%→7.85% 的 LAN4 参考流量；WAN3 约 7.20%→8.28%；WAN2/4 的最大全窗连接本来低于 20 Mbps，模型没有增益。40/60 Mbps 也不会增加这个固定需求模型的接管量。</p>',
'<p>因此本轮不扩大预算、流数或 TTL。加速后 TCP 需求可能变化，上述数字只解释当前样本，不能预测实际 NSS 速率、CPU 或延迟。单 WAN 一条 TCP 的试验应先评价自动分类、bulk/RT leaf 和游戏体验；仅占整机少量流量时，global busy 不适合承担主要性能判据。</p>',
'<h2>保留的失败与检查</h2><p>第一轮 13 次均因本地 JavaScript 语法错误在连接路由器前退出，原错误和源码哈希保留；修正后才取得本报告 13 个有效样本。分开的 CAKE JSON/文本速率读取出现跨时刻差异，改用相邻 JSON→文本→JSON：5/5 WAN 单位匹配，70–90 Mbps 是采样后 autorate 状态，不能回填为整个下载窗的固定预算。</p>',
'<p>20 项离线检查覆盖 CPU/softnet、计数重置、CT 实例重建、NAT/mark/zone、缺失样本、去除端点，以及 A/B/A2 可比性。预先声明的观测阈值为三个阶段总吞吐/pps 和选中 WAN 速率相对跨度均不超过 10%；它不授权 NSS，也不能证明 offered load 相同。历史 NSS41 的实际数据不满足这个观测条件，原功能证明与失败结果保持。</p>',
'<h2>终态与下一步</h2><p>原完整保护审核起止均通过，分类器是同一健康实例；结束有 12 个分类器自主管理的 selector，配置与业务保护保持。ECM 全零，无事务、暂存、实验状态节点或模块残留。本轮工具只读，不存在生产变更的回滚试验。</p>',
'<p>下一次只集中请求一次 CS2＋Steam。固定新鲜真实连接对，仍使用原预算和单 WAN；学习前确认 tag，验证 0→2→0、bulk/RT leaf、完整 mark/NAT/WAN affinity 和独立恢复。记录三个阶段相同 TCP 持续性、选中 WAN/总负载、实际 leaf 份额、softirq/time_squeeze，以及客户端 jitter/loss/Miss。负载漂移或无客户端数据时仅报告功能与测量，不宣称体验改善；第二 WAN 等待。</p>',
'<p class="muted">HTML 源与本地链接已检查。既有浏览器本地文件策略限制仍有效，本轮未尝试替代访问方式，未完成视觉渲染核验。</p>',
'<p><a href="nss43-mainline-observations.json">结构化证据</a> · <a href="https://github.com/ZyPulse-zy/athena-nss-mainline">私有研究仓库</a></p></html>']
body='\n'.join(parts);assert '\ufffd' not in body
for link in re.findall(r'href="([^"]+)"',body):
    if not link.startswith('https://'):assert (Path('outputs')/link).is_file()
Path('outputs/nss43-mainline-report.html').write_text(body,encoding='utf-8')
d['reportVerification']['sourceValidated']=True;p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'reportSaved':True,'sourceValidated':True,'browserRendered':False,'characters':len(body)}))
