import html,json,re
from pathlib import Path

root=Path(__file__).resolve().parents[2]
source=root/'outputs/nss49-mainline-observations.json'
data=json.loads(source.read_text(encoding='utf-8'))
metrics=data['actualForwardingABA']['measurements']
rows=''
for p in metrics['phases']:
    rows+=f"<tr><th>{html.escape(p['name'])}</th><td>{p['seconds']:.2f} s</td><td>{p['acceleratedCount']}</td><td>{p['interfaces']['lan4']['txMbps']:.2f}</td><td>{p['interfaces']['rpwan2']['rxMbps']:.2f}</td><td>{p['interfaces']['lan4']['txPps']:,.0f}</td><td>{p['busyPercent']:.2f}%</td><td>{p['softirqPercent']:.2f}%</td><td>+{p['timeSqueeze']}</td><td>+{p['softnetDropped']}</td></tr>"
leafRows=''
for handle,title in [('8f05:','Steam bulk'),('8f06:','CS2 RT'),('8fff:','未加速 fallback')]:
    p=metrics['leafDeltasAroundFastPath']['counters'][handle]
    leafRows+=f"<tr><th>{title}</th><td><code>{handle}</code></td><td>{p['bytes']:,}</td><td>{p['packets']:,}</td><td>{p['drops']}</td></tr>"
times=' / '.join(f"{p['phase']} {p['startCst'][11:23]}–{p['endCst'][11:23]}" for p in data['actualForwardingABA']['phases'])
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NSS49：自动分类进入 NSS 队列，完整单 WAN 对照通过</title>
<style>body{margin:0;background:#f4f6f8;color:#213143;font:16px/1.8 system-ui,"Microsoft YaHei",sans-serif}main{max-width:1180px;margin:36px auto;padding:0 24px 48px}h1{font-size:30px;line-height:1.4}h2{font-size:22px;margin:28px 0 12px}.card{background:white;padding:24px;border:1px solid #dbe3ec;border-radius:12px;margin:18px 0}.success{border-left:5px solid #14786b}.pending{border-left:5px solid #be7b18}.eyebrow{color:#5c6e83;font-size:14px}table{border-collapse:collapse;width:100%;font-size:14px}td,th{padding:10px;text-align:left;border-bottom:1px solid #e2e7ed;white-space:nowrap}thead{background:#ecf2f7}.scroll{overflow-x:auto}code{color:#285482}a{color:#235f9b}.small{color:#5e6b79;font-size:14px}.path{overflow-wrap:anywhere}</style>
<main><div class="eyebrow">Athena AX6600 · NSS47–NSS49 · 2026-10-04</div><h1>自动分类 → NSS bulk / RT leaf：完整单 WAN 对照已跑通</h1>
<div class="card success"><p><strong>本轮取得完整控制器成功记录。</strong>真实 Steam TCP 与在线 CS2 UDP 在 WAN2 配对，软件 → NSS → 软件三段各 5.03 秒；加速数为 0 → 2 → 0。TCP 下行进入 bulk leaf，UDP 下行进入 RT leaf，完整 ct mark、NAT、WAN affinity 正确，分类器续租一次，精确撤销与原完整保护审核均通过。</p>
<p>本轮由助手按用户授权恢复现有下载并进入在线死亡竞赛观战。它证明真实应用连接和原生 QoS 功能；没有真人操控，也没有真人体感结论。</p></div>
<div class="card pending"><strong>CPU / 游戏收益尚未通过验收。</strong>三段总流量约为 168 / 194 / 171 Mbps，LAN4 观测跨度 14.66%、WAN2 24.75%，超过预设 10% 比较条件；受控加速组仍只包含一条 TCP＋一条 UDP，上限 20 Mbps。未取得 NSS B 段有效客户端 HUD。不能据此声称整机 CPU 或 CS2 丢包改善。</div>
<h2>本轮实际变更与失败定位</h2><div class="card"><ol>
<li><strong>原 NSS46 入口在真实流下拒绝初始对齐。</strong>精简发布延迟约 1.03–1.26 秒，39 次观察未满足 &lt;1 秒。已建立独立回滚并暂存 QoS，但没有打开 ECM gate；原失败与完整恢复保留。</li>
<li><strong>NSS47 只保留纯地址解析缓存。</strong>每次新观察重置两个各 1024 项的缓存；连接 ID、zone、mark、NAT、双向元组及计数仍实时解析。4,550 个新旧差分样本一致，目标 527 行、每版本 80 次冷缓存遍历一致，3 次完整快照一致；解析 CPU 4.740→3.489 秒（约 26.4%），这是解析段收益。9,612 项边界断言覆盖 1,200 个地址、两遍及无效输入，并非 9,612 个独立用例。第一轮独立 180 秒自然恢复通过，第二轮另建 checkpoint / 回滚后才长期保留。未保留收益仅约 1.9% 的另一扫描候选。</li>
<li><strong>NSS48 在双向标签取证阶段拒绝。</strong>0.3 秒窗内 TCP 四向 total/expected/unexpected 全为 0，UDP 有包且标签正确；这是 TCP 短暂无包，没有观测到错误标签。未打开 NSS，撤销及原完整审核通过。</li>
<li><strong>NSS49 只修正初始无包等待。</strong>初始最多等待 1.2 秒，仍受原 epoch / 45 秒 owner 剩余期限约束；错误标签立即拒绝，零流量不能授权 NSS。其余 NSS Lua 与 NSS48 相同，内核/驱动/固件未改。13 个目标 RAM 场景覆盖延迟 TCP、持续空闲、改类、NAT 漂移、错误标签与加速退出，使用模拟时钟/IO，不能当硬件证明。本次真实 getter 一次、0.16 秒即通过，不能说延长等待导致本次成功。</li>
</ol></div>
<h2>真实应用 A / B / A2 观测</h2><p class="small">北京时间：TIMES。各 11 帧，计入相同测量开销；总吞吐用 LAN4 TX，WAN2 用接口 RX。接口速率不是应用净载荷。</p>
<div class="card scroll"><table><thead><tr><th>阶段</th><th>时长</th><th>ECM 加速数</th><th>LAN4 Mbps</th><th>WAN2 Mbps</th><th>LAN4 pps</th><th>busy</th><th>softirq</th><th>time_squeeze</th><th>softnet drop</th></tr></thead><tbody>ROWS</tbody></table></div>
<div class="card"><p>实际原生状态共 2 条连接：TCP client-first、UDP server-first；两者完整 mark 均为 <code>0x20000</code>，NAT 正确，WAN affinity=2，LAN4 / br-lan 层级正确。TCP downTag=<code>0x8f050000</code>，UDP downTag=<code>0x8f060000</code>；upTag=0，本轮证明下行 QoS。已建立流的出口没有交由 NSS 重新负载均衡。</p>
<p>ECM 只在 B 段放行固定连接对，11/11 帧加速数为 2，并完成一次分类器新序列续租。A / A2 加速数全为 0。RT 类变化、元组漂移、过期或错误标签继续拒绝/撤销。换端口、旧流退出及改类的通用生命周期证据沿用历史算法和原生模拟，本次不增加真人改端口 / 改类证明。</p></div>
<h2>真正命中的 NSS 队列</h2><div class="card scroll"><table><thead><tr><th>用途</th><th>leaf</th><th>字节增量</th><th>包增量</th><th>队列丢弃</th></tr></thead><tbody>LEAFROWS</tbody></table>
<p class="small">计数窗约 5.43 秒，包含加速建立 / 精确撤销边界，不能当作精确 B 5.03 秒净速率。RT leaf 的 0 丢弃不是客户端端到端 0 丢包。受控 leaf 约占该计数窗所有 leaf 字节的 8.56%，其余为软件 fallback；不能将全机 CPU 小变化全归于这两条流。</p></div>
<h2>客户端证据与第二轮</h2><div class="card"><p>第一轮保存 38 张真实 Sky 界面截图。路由器时钟锚点往返 125 ms，校准后 A/B 没有完整有效截图，A2 有 3 张；不能将后续绿色 HUD 回填到 B，也不能把未显示字段填成 0。第二轮启动时 Steam 已下载完成：游戏候选 1、bulk 0，入口在任何 router/NSS 写入前返回等待，未产生第二轮 A/B。后续部分截图被用户前台窗口遮挡，全部不用于 A/B 验收。</p><p>已退出自动测试服务器；没有为了补负载卸载重装游戏或购买内容。原始界面、连接身份及完整捕获仅留私有工作区，未上传 Git。</p></div>
<h2>当前运行与恢复</h2><div class="card"><p>长期保留 NSS47 地址缓存＋NSS46 三项可靠性修复。现网引用：<code>work/nss47/deployment-latest.json</code>；实验入口：<code>work/nss49/real-session.mjs</code>，绑定 121 项来源，99 项入口本地检查及 13 项目标 RAM 场景。历史 NSS42 / NSS46 入口和失败证明保持。资格 JSON 中继承的 <code>nssRouterPayloadsUnchanged</code> 字段不能描述本轮 helper 差异；本报告明确记录该唯一 Lua 改动。</p>
<p>所有本轮写入前 checkpoint 已下载、校验 SHA256 / gzip，并验证独立守护身份。NSS49 实验使用独立 45 秒 owner，主动精确提前撤销；本次没有触发自然 45 秒到期，不能冒充新的自然到期证明。WAN/mwan3、队列、tag、state node 与模块全部恢复。最终 worker 5411 / 原启动身份连续，sequence 645，原完整持锁审核通过，ECM 关闭全零，无事务、暂存或实验模块。</p>
<p class="small path">当前配置 SHA256：<code>478818d553903aa859c853cab99383e038d4d325f500d68843ffff8b7517a900</code>。不把这约半小时实例连续性写成全部高负载 crash / recovery 或长期稳定验收。</p></div>
<h2>下一步只有一条</h2><div class="card"><p><strong>使用已通过的 NSS49 入口补可解释的同负载单 WAN 验收。</strong>不再重做分类器准备，提前同步 HUD，确认相同在线会话和下载连接持续，分别看 RT leaf、softirq / time_squeeze、pps / 吞吐与客户端 jitter / loss / Miss。当前 20 Mbps 子组份额有限：即使功能稳定，整机 CPU 收益仍可能不足以判断。若需要提高受控份额，必须另建单一变量、重新资格核验，先保持当前已验证入口和原回滚边界。</p>
<p>最合理的现有架构是 Linux 决定新连接 PBR / ct mark，默认关闭的精确 gate 继承原 WAN，学习前写入 bulk / RT leaf tag，NSS 负责已放行数据面的下行 FQ-CoDel / 整形；未放行流走软件 CAKE fallback。host fairness 不要求复刻；NSS 当前 leaf 提供 FQ / AQM 和类分离，不能声称已复刻 CAKE DiffServ tin、NAT host fairness、autorate、ECN 或共享五 WAN 预算。第二 WAN 同时加速、共享预算、Wi-Fi、autorate 继续等待本主线验收；无需转 N100。没有上游提交，解析与无包误判只入本地 backlog。</p></div>
<p class="small"><a href="nss49-mainline-observations.json">结构化脱敏观测</a> · <a href="https://github.com/ZyPulse-zy/athena-nss-mainline">私有研究仓库</a>。HTML 源文件和链接已核验；保留此前本地文件浏览器策略拒绝，未绕过，未声称浏览器视觉验收。</p></main></html>'''
page=page.replace('TIMES',html.escape(times)).replace('LEAFROWS',leafRows).replace('ROWS',rows)
assert 'LEAFROWS' not in page and '<tbody>'+leafRows in page
output=root/'outputs/nss49-mainline-report.html'
output.write_text(page,encoding='utf-8',newline='\n')
assert '<title>' in page and '<table>' in page and page.count('<table>')==2 and '<script' not in page
for link in re.findall(r'href="([^"]+)"',page):
    if not link.startswith(('https://','http://')):assert (output.parent/link).is_file()
data['reportVerification']['sourceValidated']=True
source.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'passed':True,'report':str(output),'browserRendered':False,'phases':3,'tables':2}))
