# 可复用的有界入口：v45提前取得软件候选

当前本地候选`work/v45-early-acquisition/entry.mjs`，命令仍为默认inspect / status / run / stop。24模型、默认inspect和实际最终恢复通过；唯一run在端点控制SSH连接超时处写前退出，未生成fixture流量，新启动时序尚未现场验证。核心五WAN数据面已由v42验收；完整最新入口整合仍未通过，勿自动盲重试。

```powershell
& 'C:/Users/lishu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe' 'work/v45-early-acquisition/entry.mjs' inspect
& 'C:/Users/lishu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe' 'work/v45-early-acquisition/entry.mjs' status
```

同样四条初始自有TCP并发启动，四个唯一自有PID发布后提前观察实际WAN；最终四首包、CIM/socket/CT完整身份、4BULK＋1RT、五WAN、source6/原30秒取得和checkpoint/独立恢复保持。60秒B、kernel90最大120/owner180/client180/guard210/server250、32Mbps/64KiB和所有字节预算不变。stop只控制同session自有发送与下一准入，恢复未确认不得重开。

已保留v44唯一最终label修复。旧v44 WAN列表是native数组顺序，真实自有槽为4/2/1/1、UDP3；原记录不改，见[本次记录与更正](V45_EARLY_ACQUISITION_2026-10-07.md)。

## 以下保留历史描述，当前状态以上文为准

# 可复用的有界多 WAN 入口：最新软件候选

当前推荐的本地预览与状态候选是`work/v44-unique-label-entry/entry.mjs`，命令仍为默认inspect / status / run / stop。17项模型与默认inspect通过；run和stop的完整现场闭环尚未通过。本轮停止新增流量，勿把以下命令清单理解为自动重试计划。

```powershell
& 'C:/Users/lishu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe' 'work/v44-unique-label-entry/entry.mjs' inspect
& 'C:/Users/lishu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe' 'work/v44-unique-label-entry/entry.mjs' status
```

未来明确一次run仍需要本地已绑定源、部署资料和SSH；在原30秒自然取得期限内必须配齐五WAN，未知默认拒绝。原60秒B、source6/kernel90最大120/owner180/client180/guard210/server250和各字节预算保持，写前仍需新checkpoint下载/SHA/gzip与独立恢复。恢复未确认保留锁，禁止下一代。stop只控制同session自有发送和下一次准入；收到请求不等于硬件恢复已通过。

v43固定命名空间替换漏分隔符和v44固定审核label冲突均有实际本地失败证据；最新候选保留分隔符，并将最终label绑定完整新runtime。没有改分类、QoS、七Lua数据面或共享publication helper。v44唯一实际流量窗4BULK/1RT，但TCP WAN1/1/2/4＋UDP WAN3未配齐，NSS写前退出；一次新目录只读补核验确认完整恢复。见[本次完整记录](BOUNDED_ENTRY_INTEGRATION_2026-10-07.md)、[17模型候选](../evidence/v44-unique-label-candidate.json)。

## 以下保留v43原软件与失败记录，旧权限描述仅对应当时

# 可复用的有界多 WAN 入口

当前已接入四个命令：`inspect`（默认）、`status`、`run`、`stop`。入口沿用 v42 的四条自有 TCP 下载＋一条模拟 UDP 实时流，以及已验收的五 WAN 数据面。默认预览只核对本地源码和既有验收依据，不产生流量，不连接路由器，也不代表新的现网健康审核。

```powershell
& 'C:/Users/lishu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe' 'work/v43-bounded-entry/entry.mjs' inspect
& 'C:/Users/lishu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe' 'work/v43-bounded-entry/entry.mjs' status
& 'C:/Users/lishu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe' 'work/v43-bounded-entry/entry.mjs' run
& 'C:/Users/lishu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe' 'work/v43-bounded-entry/entry.mjs' stop
```

命令从本工作区执行，依赖本地保存的已绑定源码、原部署资料和 SSH 连接；公开仓库包含白名单源码和脱敏证据，凭据、完整运行输入、checkpoint 和模块留在本地。这是一次显式触发、到期恢复的受控入口，不是永久开启 NSS 的服务。

## 运行与停止

`run` 先检查 Windows 的进程身份和 socket 查询能力，再创建独占锁和新的运行目录。每次从 v42 冻结源产生独立副本；模型生成的实际源绑定为3354原绑定＋51新绑定＝3405。七份 Lua 数据面、分类、QoS、tag、guardian 源与 v42 字节相同。新运行只改变本地命名空间、有限启动截止和停止请求检查。

后续仍由原自动分类和 Linux PBR 取得五个不同 WAN 的四 BULK＋一 RT，原 tuple / CT / 完整 mark / NAT / WAN affinity 冻结后不替换。每次生产写前仍需新的 checkpoint 下载/SHA/gzip 与控制连接外独立恢复核验；原 60秒 B / source6 / kernel90最大120 / owner180 / client180 / guard210、32Mbps负载、DOWN18 / UP60每WAN12、各字节上限保持。

`stop` 只向本次命名空间写入停止意图和同 session 的自有客户端控制，不强杀控制器、不直接改现网 tag。它阻止下一次准入，并停止自有发送；NSS 撤销与恢复继续由原控制器和独立 guardian 完成。收到停止请求不等于恢复审核已经通过。`status` 显示本地入口记录，不能代替新网络审核。恢复未确认时独占锁保留，禁止自动开启下一代。

## 本次实际验证

修订后的13项模型检查和默认预览通过，包括命名空间、恢复余量、完整/缺失进程身份、同session停止与已结束客户端不重启。首版9项输出保留；其中“延长截止拒绝”用错了命名空间，不能单独证明截止检查，已改为合法命名空间和明确失败信息的用例。没有覆盖旧输出。

实际启动返回1：当前执行环境无法查询 Windows CIM 进程身份。入口在创建独占锁、运行记录、负载、SSH/router连接、checkpoint或NSS stage前拒绝，原输出仅保存在本地；状态为IDLE。本次没有新的硬件会话，不能标完整新入口现场通过。后续先取得可完成原进程身份核验的执行条件，再只补一次该入口整合会话，保持原安全检查。

封存脚本首次误将模型里的虚拟客户端指针当作真实负载而拒绝，发生在源码复制与提交之前。原源码及失败已保存；修正为验证虚拟样例身份后继续，没有新开网络测试。

v42 的五 WAN 五流60.01秒 / 121个ECM5采样 / 20续租、2373模拟UDP全部返回和完整恢复结论保持。v41分类计数差异继续保留为已知限制，不称已修复。本次没有 CS2 / Steam操作、新CPU、长期或永久部署声明。

源码：[入口](../code/work/v43-bounded-entry/entry.mjs)、[副本和绑定](../code/work/v43-bounded-entry/materialize.mjs)、[进程检查](../code/work/v43-bounded-entry/platform-preflight.mjs)。证据：[本次软件检查与启动拒绝](../evidence/v43-bounded-entry.json)、[源码保存](../evidence/v43-bounded-source-proof.json)、[v42硬件验收](FIVE_WAN_SIMULATED_ACCEPTANCE_2026-10-07.md)。
