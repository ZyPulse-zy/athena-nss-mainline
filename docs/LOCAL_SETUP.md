# 本地接续

完整私有工作区仍是本聊天原目录。仓库的 `code/work/...` 保存代码原路径；凭据与完整实验目录不会上传。

已验证的本地工具是 Node.js、Python 与 WSL `Athena-Cake-Build` 中的 Lua 5.1。没有把 SDK、固件或内核模块二进制加入仓库。

## 仓库内可独立运行的离线回放

`python tools/replay_admission.py --lua /path/to/lua5.1`

Windows 上已有分离的 Lua 运行目录时可使用 `--wsl-runtime <runtime/usr> --wsl-distro Athena-Cake-Build`。该目录应包含 `bin/lua5.1` 和相应 `lib/x86_64-linux-gnu`，可指向原工作区现有运行时。脚本只使用仓库源码和脱敏时间包络，模拟 IO/时间/身份，不连接路由器，不生成网络负载。临时输出位于忽略的 `.local/`。

预期 87 项检查通过；这些检查证明准入逻辑和诊断边界，不是现场 NSS 性能验收。

另外，`python tools/replay_classifier_recovery.py --wsl-runtime <runtime/usr>` 可独立回放 57 项地址失败恢复与不安全子进程状态检查，使用模拟进程/时间/发布，不访问路由器；输出保存在 `.local/`。

`python tools/replay_mainline_admission.py --wsl-runtime <runtime/usr>` 可从仓库独立回放 NSS36 的 212 项准入检查（108 新旧差分、66 历史时序包络）。使用现有 WSL `Athena-Cake-Build`，输出保存在 `.local/nss36-replay/`，不读取凭据、不连接路由器、不发流量。

`python tools/replay_normalizer.py --wsl-runtime <runtime/usr>` 可从仓库独立执行 NSS37 新旧解析器的 9,085 项检查，仅合成文本、模拟时间，不读取任何私有捕获。完整工作区加入真实采集文本后为 9,087 项，另有 26 项核心/leaf 生命周期检查。输出保存在忽略的 `.local/`；不要对冻结的工作区资格文件直接重跑覆盖。

`python tools/replay_adapter_candidate.py --wsl-runtime <runtime/usr>` 可独立回放 NSS38 未安装的带诊断候选：1,470 个决策对照、5 个调用次数约束、230 个准入/诊断案例。只使用仓库源码与脱敏时间包络，不访问路由器，输出保存在 `.local/nss38-replay/`。这些不等于完整当前控制器绑定或硬件验收。

## 先读与只读核验

在完整私有工作区运行现有入口前，先检查源文件哈希和作用范围：

- `work/nss37/current-audit.mjs <new-label>`：绑定当前 NSS37；输出在 NSS37 新标签下，避免覆盖已保存证明。审计会严格拒绝过旧快照，保留失败和随后复查两份记录。
- `work/nss37/real-session.mjs inspect`：严格检查 66 项 manifest/current config，然后只读核验真实应用连接，不开启 gate/ECM 或生成流量。已有输出应保留，新轮次先复制入口与输出位置。NSS38 复制入口完成一次失败的真实 `aba`，未使用新候选。
- `work/nss37/final-closure.mjs`：核验无实验事务/模块/状态残留；新轮次先复制为自己的输出位置。
- `work/nss36/rehearse-admission.mjs`：只读检查 NSS36 固定历史连接身份是否仍可准入，不重新证明当前应用 socket 归属；不能当真实 A/B。
- `work/nss36/profile-publication-path.mjs`：一次只读 CT 采集 + RAM 冷回放，验证当前代码哈希后测时间；不修改生产 worker，不等于完整生产计时。
- NSS37 `operational-audit.mjs` 是试装前/恢复后针对 NSS35 的历史入口，最终当前审核使用 `current-audit.mjs`，不要混用。
- NSS38 `current-audit.mjs` 仍绑定 NSS37、输出在 NSS38。本轮源码/证据已冻结；后续新目录重新生成资格。`candidate-*.lua` 仅候选，不能替换当前绑定文件后直接运行。
- NSS33/34/35/36 现场入口保留为历史，不能拿旧配置资格操作 NSS37。NSS36 两个只读诊断也依赖历史身份/哈希，不是当前部署入口。若修改当前配置或绑定源码，NSS37 资格同样必须重新生成，不能复用。

连接封装使用本机已保存的认证。不要把密码、密钥、令牌或认证文件内容粘进对话、日志或仓库。

## 同步代码和证据

`tools/sync_from_workspace.py <完整私有工作区路径>` 仅从明确白名单复制源码、校验部署文件哈希、生成脱敏摘要。不枚举并上传整个工作区，不复制原始连接/配置/备份。

同步后运行 `tools/check_repository.py`，检查 Git diff 和新增文件，再提交。新测试应放新轮次目录；不要覆盖冻结的历史证明来匹配当前代码。

仓库内的控制器依赖被刻意排除的私有状态与连接封装，因此代码镜像不是可直接刷入或安装的发布包。
