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

当前入口在完整私有工作区 `work/nss39/`，新轮次先复制为新目录并重新绑定，不能覆盖这轮证明。

- `current-audit.mjs <new-label>`：核验当前 NSS39/受保护配置/自有规则/ECM，拒绝过期发布。
- `real-session.mjs inspect`：核验 68 项 manifest 与当前配置，再只读核对真实应用流。未通过真人高负载 A/B，不能把资格当性能结论。
- `final-closure.mjs`：实验事务/模块/暂存/状态清理检查。
- `native-qualification.mjs`：完整候选原生 RAM 模拟。会创建已 checkpoint、独立清理的临时文件，不是纯只读入口；不能无审查重跑现场脚本。
- NSS37/38 和更旧入口只保留为历史。NSS39 没有改 NSS32–38 冻结源码与证明。修改当前配置或任何绑定文件必须在新轮次重新资格核验。

`python tools/replay_tc_supervision.py --wsl-runtime <runtime/usr>` 可独立执行 NSS39 的 16 项子进程/管道/截止模型，输出到忽略的 `.local/nss39-replay/`；不访问路由器，不生成流量。NSS38 带诊断 adapter 与 NSS39 的源码一致，原离线差分入口仍适用于这组源码；不同的部署绑定与目标检查另见 NSS39 证据。

连接封装使用本机已保存的认证。不要把密码、密钥、令牌或认证文件内容粘进对话、日志或仓库。

## 同步代码和证据

`tools/sync_from_workspace.py <完整私有工作区路径>` 仅从明确白名单复制源码、校验部署文件哈希、生成脱敏摘要。不枚举并上传整个工作区，不复制原始连接/配置/备份。

同步后运行 `tools/check_repository.py`，检查 Git diff 和新增文件，再提交。新测试应放新轮次目录；不要覆盖冻结的历史证明来匹配当前代码。

仓库内的控制器依赖被刻意排除的私有状态与连接封装，因此代码镜像不是可直接刷入或安装的发布包。
