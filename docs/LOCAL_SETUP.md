# 本地接续

完整私有工作区仍是本聊天原目录。仓库的 `code/work/...` 保存代码原路径；凭据与完整实验目录不会上传。

已验证的本地工具是 Node.js、Python 与 WSL `Athena-Cake-Build` 中的 Lua 5.1。没有把 SDK、固件或内核模块二进制加入仓库。

## 仓库内可独立运行的离线回放

`python tools/replay_admission.py --lua /path/to/lua5.1`

Windows 上已有分离的 Lua 运行目录时可使用 `--wsl-runtime <runtime/usr> --wsl-distro Athena-Cake-Build`。该目录应包含 `bin/lua5.1` 和相应 `lib/x86_64-linux-gnu`，可指向原工作区现有运行时。脚本只使用仓库源码和脱敏时间包络，模拟 IO/时间/身份，不连接路由器，不生成网络负载。临时输出位于忽略的 `.local/`。

预期 87 项检查通过；这些检查证明准入逻辑和诊断边界，不是现场 NSS 性能验收。

另外，`python tools/replay_classifier_recovery.py --wsl-runtime <runtime/usr>` 可独立回放 57 项地址失败恢复与不安全子进程状态检查，使用模拟进程/时间/发布，不访问路由器；输出保存在 `.local/`。

## 先读与只读核验

在完整私有工作区运行现有入口前，先检查源文件哈希和作用范围：

- `work/nss35/operational-audit.mjs <new-label>`：核验现网与分类器；输出保存在当前部署目录，使用新标签避免覆盖历史证明。
- 新一轮真实候选读取器须先绑定 NSS35 当前配置。旧 `work/nss34/read-real-candidates.mjs` 保留为历史入口，不直接用于新部署验收。
- `work/nss35/final-closure.mjs`：核验无实验事务/模块/状态残留。
- `work/nss33/real-session.mjs`：旧现场控制器，资格绑定 NSS33。不能直接拿它运行当前 NSS35 的 `aba`；先在新轮次重新生成当前配置的资格。

连接封装使用本机已保存的认证。不要把密码、密钥、令牌或认证文件内容粘进对话、日志或仓库。

## 同步代码和证据

`tools/sync_from_workspace.py <完整私有工作区路径>` 仅从明确白名单复制源码、校验部署文件哈希、生成脱敏摘要。不枚举并上传整个工作区，不复制原始连接/配置/备份。

同步后运行 `tools/check_repository.py`，检查 Git diff 和新增文件，再提交。新测试应放新轮次目录；不要覆盖冻结的历史证明来匹配当前代码。

仓库内的控制器依赖被刻意排除的私有状态与连接封装，因此代码镜像不是可直接刷入或安装的发布包。
