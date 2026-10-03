import fs from 'node:fs';
const s=JSON.parse(fs.readFileSync('outputs/nss40-mainline-observations.json')),a=s.realReadOnlyAdmission,p=a.performance,f=(v,n=2)=>Number(v).toFixed(n);
const css=fs.readFileSync('outputs/nss39-mainline-report.html','utf8').match(/<style>([\s\S]*?)<\/style>/)[1];
fs.writeFileSync('outputs/nss40-mainline-report.html',`<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NSS40 · 真人高负载准入与写前拒绝</title><style>${css}</style><main>
<p class="muted">Athena AX6600 · 2026-10-03 深夜至 10-04 凌晨 · 时间为北京时间</p><h1>真实高负载下出现准入窗口<br>写入前的快照审核仍未通过</h1>
<p class="note">本轮已经集中使用真实 CS2＋Steam。${f(p.lan4DownMbps,1)} Mbps 下，WAN5 游戏 UDP 与下载 TCP 的只读准入 ${a.ready}/${a.samples} 次通过。随后实际入口被过期快照保护挡住，<strong>NSS、WAN 模式和队列均未改动，没有进入 A/B/A2</strong>。当前继续运行 NSS39。</p>
<h2>真实只读窗口</h2><p>23:52:31–23:52:42，核对本机应用 socket 归属，选择自然同 WAN5 的 CS2 RT UDP 与 Steam bulk TCP。完整 CT 实例、zone、双向元组、mark 和 NAT 条件经过当前 reader/adapter 校验；双方完整 mark 均为 0x50000，未重写出口或连接粘性。</p>
<div class="scroll"><table><thead><tr><th>测量</th><th>实际记录</th></tr></thead><tbody><tr><td>计数窗口</td><td>${f(p.seconds)} 秒</td></tr><tr><td>LAN4 下行 / pps</td><td>${f(p.lan4DownMbps)} Mbps / ${f(p.lan4DownPps,0)}</td></tr><tr><td>CPU busy / softirq</td><td>${f(p.cpuBusyPercent)}% / ${f(p.softirqPercent)}%</td></tr><tr><td>time_squeeze</td><td>+${p.timeSqueezeDelta}</td></tr><tr><td>只读准入</td><td>${a.ready}/${a.samples}，成功来自 2 个新序列</td></tr><tr><td>最小来源年龄</td><td>${f(a.sourceAgeMinSeconds)} 秒</td></tr><tr><td>adapter / phase 最大用时</td><td>${f(a.adapterMaxSeconds)} / ${f(a.phaseMaxSeconds)} 秒</td></tr></tbody></table></div>
<p>59 次因预学习余量不足拒绝，31 次因 tag 设置余量不足拒绝。初始采集年龄 &lt;1 秒、预学习 &lt;2 秒保持。探测程序自身用了 ${f(a.observerCpuSeconds,3)} CPU 秒，密集只读检查对路由器有可观开销；上表包含观察成本，<strong>不是无干扰性能基线，更不是 NSS 的 CPU 收益</strong>。ECM 在整个只读窗口均关闭且计数为零。</p>
<h2>实际尝试为何结束</h2><p>23:52:59 发起单 WAN A/B 入口。其写前审核读取完整 snapshot.json，在“发布年龄 &lt;9 秒且来源年龄 &lt;6 秒”的联合断言失败。此次尚未走到 checkpoint、独立事务、private MacVLAN、NSS qdisc、packet tag 或 ECM gate；没有生产写入，因此本轮回滚<strong>不适用</strong>，不能记作一次回滚成功。</p>
<p>失败发生在保存选中 pair 的阶段之前；当次精确年龄与阶段耗时未被旧审核器记录，原始应用 latest 文件后来被刷新。保留的只读 rehearsal 元组属于此前独立窗口，不能冒充失败瞬间的完整身份记录。已在失败后按未变的绑定哈希冻结 ${s.actualTrial.frozenBoundFiles} 份源码/证明。</p>
<h2>定位结果与补充诊断</h2><p>源码顺序是：先发布精简 classification.json，再同步等待持锁的软件规则维护/审核，最后发布完整 snapshot.json。因此两类发布处于不同阶段，不能把一次 compact 准入通过当作后续完整快照必然新鲜。<strong>这只是代码顺序，尚未证明本次失败由哪段等待造成。</strong></p>
<p>用户结束负载后，23:55 同一审核带分段计时只读通过，锁内 ${f(s.diagnosticFollowup.firstLockedAuditSeconds)} 秒，来源年龄 ${f(s.diagnosticFollowup.firstFreshness.sourceAge)} 秒。随后完整集成诊断入口也通过。保留了所有原断言与固定截止，只新增阶段时间和拒绝时的年龄记录；没有通过延长期限、重用旧身份或吞错取得通过。</p>
<p>新增按次应用证据封存入口已验证，可以避免 socket、候选和原始响应被后续 latest 覆盖。它是本地取证改进，没有改常驻分类器；下一轮需要把这两个入口绑定到新的实际控制器后再尝试。未把带诊断版本反写到本次被冻结的失败脚本。</p>
<h2>结束状态与结论</h2><p>结束轻载窗口 ${s.closingSoftwareWindow.samples}/35 次健康，精简与完整快照同序列的身份、分类、leaf 和有效期相等。保护配置、规则所有权、认证/PBR/服务审核通过，仍是 NSS39 同一实例；ECM 全零，无实验模块、暂存目录或活动事务。旧 last-error 属于此前试装到期，不属于当前实例的新故障。</p>
<ul><li>支持：当前分类器能识别真实游戏与下载，精简 adapter 在约 323 Mbps 时能出现符合原期限的初始准入窗口。</li><li>尚未支持：入口可靠性、真实加速 flow 命中 bulk/RT leaf、同负载 NSS 的 softirq/吞吐收益，以及游戏 jitter/loss/Miss 改善。</li><li>本轮没有客户端 CS2 遥测、NSS leaf 计数或加速后的 mark/NAT/WAN 证明。没有替代或推算这些数据。</li></ul>
<h2>下一步</h2><p>先把新增的完整快照年龄与分段计时接入下一轮写前审核，并按次冻结应用证据。只解决这一主线入口：明确高负载新鲜度失败发生在哪里，维持原拒绝边界，再集中一次单 WAN software→NSS→software。通过前不扩第二 WAN、共享预算、Wi-Fi 或 autorate。现在无需继续挂机或下载。</p>
<p><a href="nss40-mainline-observations.json">结构化证据</a> · <a href="nss39-mainline-report.html">NSS39 部署与资格</a> · <a href="https://github.com/ZyPulse-zy/athena-nss-mainline">私有仓库</a></p></main></html>`);
console.log(JSON.stringify({report:'outputs/nss40-mainline-report.html',highLoadNssCompleted:false}));
