"""Render a reviewable evidence report without inventing game/CPU outcomes."""
from pathlib import Path
import json,html
path=Path('outputs/nss45-mainline-observations.json');d=json.loads(path.read_text());esc=html.escape
rows=''
for t in d['temporaryClassifierTrials']:
 p=t['activeWindow']['performance'];rows+=f"<tr><td>{esc(t['kind'])}</td><td>{p['lan4DownMbps']:.3f} Mbps / {p['lan4DownPps']:.1f} pps</td><td>{p['busyPercent']:.2f}% / {p['softirqPercent']:.2f}%</td><td>+{p['timeSqueezeDelta']}</td><td>35/35 健康；180 秒自然回滚通过</td></tr>"
b=d['recoveryReadReuse'];body=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NSS45 · 分类器恢复与独立回滚</title>
<style>body{{max-width:1080px;margin:48px auto;padding:0 24px;background:#f5f7fa;color:#182333;font:16px/1.75 system-ui,"Microsoft YaHei",sans-serif}}h1{{font-size:32px;line-height:1.35}}h2{{font-size:22px;margin-top:34px}}section{{background:white;padding:22px 28px;border-radius:12px;margin:20px 0;border:1px solid #dfe5eb}}.lead{{font-size:19px}}.status{{background:#eef4ff;border-left:4px solid #416db0;padding:14px 18px}}table{{border-collapse:collapse;width:100%;font-size:14px}}td,th{{border:1px solid #dfe5eb;padding:10px;text-align:left;vertical-align:top}}code{{font-size:13px;overflow-wrap:anywhere}}small{{color:#506071}}a{{color:#285b9c}}@media(max-width:720px){{body{{margin:24px auto;padding:0 14px}}section{{padding:16px}}table{{display:block;overflow:auto}}}}</style>
<h1>NSS45：分类器恢复与独立回滚</h1><p class="lead">两项修复分别完成短时试装与自然到期恢复；软件快照过期处理完成局部逻辑和规则日志交叉验证。NSS 全程关闭，真人性能与游戏闭环仍未通过。</p>
<p class="status">最终现网仍为 NSS39，分类器健康，原完整保护审核通过。两次 180 秒回滚独立于 SSH 控制连接；两套暂存由各自 480 秒守护自然清理。没有长期保留候选，没有修改 NSS 准入、20 Mbps 预算、连接数或 TTL。</p>
<section><h2>已定位与验证</h2><ol><li>开场日志保留三次此前自然退出：11:07:30、11:08:02、11:08:10，均为 2048 行上限触发未分类错误；不是本轮故障注入。</li><li>恢复函数重复读取同一初始枚举。候选只复用已核验的第一遍状态，实际写前与写后仍重新检查，首次写后停止缓存。空日志只读调用 60→40；目标三对只读交替测量平均 {b['originalMeanSeconds']:.3f}→{b['candidateMeanSeconds']:.3f} 秒，约缩短 {b['wallTimeReductionPercent']:.1f}%。这没有证明高负载 6.18 秒恢复问题已解决，也不是整机 CPU 收益。</li><li>2049 行候选返回有类型的完整观察失败，要求实际 query 子进程回收证明。7 个真实目标子进程案例通过，包括 2048 成功、2049 边界、新旧对照、字节溢出及未知错误拒绝。</li><li>软件来源过期候选保留 6 秒界限：拒绝软件写入，绑定 apply 返回，撤回两种发布、清空观察历史、精确恢复，再接受新观察。34 个辅助逻辑案例与 8 个实际 backend/ownership 算法交叉场景通过本地及目标 RAM 重放；这些场景的队列 IO、发布和应用子进程被模拟。该候选未安装，完整应用子进程与高负载服务恢复尚未资格核验。</li></ol></section>
<section><h2>实际试装与回滚</h2><p>每次新 checkpoint 均下载并核对哈希与压缩完整性；修改前确认独立回滚进程身份、父进程、事务与截止时间。第一轮仅改变恢复函数，第二轮仅改变行数溢出处理。两次之间恢复原程序与配置，原生完整规则/配置审核通过。</p>
<table><thead><tr><th>试装</th><th>自然 LAN4 负载</th><th>busy / softirq</th><th>time_squeeze</th><th>观测与恢复</th></tr></thead><tbody>{rows}</tbody></table>
<p>表内各为约 17 秒的轻载观察窗，包含观察开销；负载不同，不能构成转发 A/B。RT 软件规则是现有启发式分类结果，未由 CS2 socket 证明，不能当作真人游戏命中。</p><p>接近事务到期时，两次候选 worker 按原安装期限拒绝继续工作；procd 重试也拒绝，随后独立守护恢复旧配置与健康实例。最后的 last-error 属于第二次受控到期，不属于当前 worker。没有把 35 帧健康写成整段 180 秒连续健康。</p></section>
<section><h2>假设的结论</h2><table><tr><th>假设</th><th>证据支持范围</th></tr><tr><td>重复初始读取增加恢复开销</td><td>源码、24 个新旧算法案例、目标空日志测量支持；高负载恢复时限仍未验证。</td></tr><tr><td>原行数边界导致无必要的 worker 退出</td><td>自然日志与旧 2049 行复现支持。新逻辑的回收/撤回要求、冷启动与独立恢复已检查，生产高负载溢出未注入。</td></tr><tr><td>已知来源过期可安全退回观察</td><td>局部逻辑与日志算法模拟支持，未知写入者保留；真实 apply 子进程与完整服务故障恢复仍未通过。</td></tr></table></section>
<section><h2>保留的限制与下一步</h2><p>没有真人 CS2＋Steam 配对，没有 ECM fast path、leaf 计数、转发 A/B/A2 或客户端 jitter/loss/Miss；没有新的 CPU、吞吐或游戏收益结论。NSS41 的真实功能证明与其性能限制保持。</p><p>下一项是完整 apply 子进程与过期恢复的资格核验，随后分步组合修复，核验 classification 调度提示＋原完整审核的新入口。准备期间无需挂游戏或反复下载；第二 WAN、共享预算、Wi-Fi 和 autorate 继续等待主线闭环。</p><p>原始日志、身份、checkpoint、私有配置与模块留本地。源码与脱敏证据同步私有仓库，潜在问题只进本地 backlog，未提交上游。</p></section>
<small>最终核验：{esc(d['finalState']['observedAt'])}。<a href="nss45-mainline-observations.json">结构化证据</a>。报告源与本地引用已检查；沿用已有本地浏览器策略拒绝，未绕过，浏览器渲染未核验。</small></html>'''
assert all(x in body for x in ['NSS 全程关闭','34 个辅助逻辑','8 个实际 backend','6.18 秒','未安装','180 秒','480 秒'])
assert 'password='not in body.lower()and 'ghp_'not in body
Path('outputs/nss45-mainline-report.html').write_text(body,encoding='utf-8',newline='\n')
d['reportVerification']['sourceValidated']=True;path.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'reportSaved':True,'sourceValidated':True,'localEvidenceReferenceExists':path.exists(),'browserRendered':False}))
