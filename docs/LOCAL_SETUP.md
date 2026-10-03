# 本地接续

完整私有工作区仍是本聊天原目录。仓库的 `code/work/...` 保存代码原路径；凭据与完整实验目录不会上传。

已验证的本地工具是 Node.js、Python 与 WSL `Athena-Cake-Build` 中的 Lua 5.1。没有把 SDK、固件或内核模块二进制加入仓库。

## 先读与只读核验

在完整私有工作区运行现有入口前，先检查源文件哈希和作用范围：

- `work/nss33/operational-audit.mjs <new-label>`：核验现网与分类器；输出保存在当前部署目录，使用新标签避免覆盖历史证明。
- `work/nss34/read-real-candidates.mjs`：只读关联 PC 进程 socket 和当前候选；不生成流量。
- `work/nss34/final-closure.mjs`：核验无实验事务/模块/状态残留。
- `work/nss33/real-session.mjs`：默认 inspect；`aba` 会变更现网，只能在全部约束通过后使用。

连接封装使用本机已保存的认证。不要把密码、密钥、令牌或认证文件内容粘进对话、日志或仓库。

## 同步代码和证据

`tools/sync_from_workspace.py <完整私有工作区路径>` 仅从明确白名单复制源码、校验部署文件哈希、生成脱敏摘要。不枚举并上传整个工作区，不复制原始连接/配置/备份。

同步后运行 `tools/check_repository.py`，检查 Git diff 和新增文件，再提交。新测试应放新轮次目录；不要覆盖冻结的历史证明来匹配当前代码。

仓库内的控制器依赖被刻意排除的私有状态与连接封装，因此代码镜像不是可直接刷入或安装的发布包。
