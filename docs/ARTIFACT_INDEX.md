# 证据索引

仓库内可直接核对：

- `evidence/nss33-summary.json`：关键量化结果、试验退出位置、回滚和结论范围。
- `evidence/nss33-admission-timing.json`：66 个已脱敏的时序样本，仅保留相对时间、年龄、原因、候选存在性；不是完整包捕获。
- `evidence/nss34-loop-profile.json`：只读循环的汇总与相对时间分解；不含流元组。
- `evidence/nss34-admission-replay.json`：87 项离线检查，身份/IO 为模拟，真实时间包络 66 条；硬件验收明确为 false。
- `evidence/nss34-classifier-restarts.json`：两次自动重启触发时间、地址查询返回码、随后只读复查；不含原始进程和连接记录。
- `evidence/nss35-address-recovery.json`：136 项分层检查、轻负载指标、独立回滚和常驻部署，明确未证明事项。
- `evidence/current-runtime.json`：最新审核摘要与部署哈希；读取者仍应重新核验现网。
- `source-manifest.json`：每个源码副本的原路径、SHA256、大小；部署源文件必须与当前配置记录的哈希一致。

仅在完整私有工作区：

| 路径 | 用途 |
| --- | --- |
| `outputs/nss32-matched-aba-report.html` | 历史受控低负载完整 A/B/A2 |
| `outputs/nss33-classifier-readiness-report.html` | 上一轮完整报告 |
| `work/nss35/deployment-latest.json` | 当前常驻分类器部署引用 |
| `work/nss35/address-trial-qualified.json` | 试装修复与 180 秒独立到期回滚 |
| `outputs/nss35-address-recovery-report.html` | 本轮现场报告 |
| `work/nss33/compact-trial-qualified.json` | 分类发布语义与独立 180 秒回滚 |
| `work/nss33/real-matched-aba-20261003071100-604d4fe1/` | 实际失败与回滚、冻结源码、完整私有原始证据 |
| `work/nss33/admission-rehearsal-20261003071535-private.json` | 66 个准入检查原始样本 |
| `work/nss34/` | 历史只读定位与 GitHub 建仓记录 |
| `work/nss35/` | 新恢复逻辑、测试与部署完整私有证据 |

旧 NSS33/NSS30/NSS29/NSS28 部署别名仍用于历史证明，不能用来覆盖当前常驻分类器状态。
