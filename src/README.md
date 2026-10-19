# 主线源码入口

主线选择由 [current.json](current.json) 记录，绑定原始文件路径、SHA-256 和对应实测记录。当前选择是 **2026-10-08 连续续租控制器**，用于阅读和接续该研究版本。

## 组件

| 组件 | 入口 | 职责 |
| --- | --- | --- |
| 常驻协调 | [daemon.mjs](../code/work/resident-continuous-dev-20261008/daemon.mjs) | 观察合格流、启动与结束控制代 |
| 准入入口 | [normal-entry.mjs](../code/work/resident-continuous-dev-20261008/normal-entry.mjs) | 分类与连接身份核验 |
| 生命周期 | [run-generation.mjs](../code/work/resident-continuous-dev-20261008/run-generation.mjs) | 单代运行与结果收集 |
| 策略 | [policy.mjs](../code/work/resident-continuous-dev-20261008/policy.mjs) | 调度与错误处理 |
| 持久化 | [storage.mjs](../code/work/resident-continuous-dev-20261008/storage.mjs) | 状态文件及观察记录 |
| 连续续租适配 | [adapt.mjs](../code/work/resident-continuous-dev-20261008/adapt.mjs) | 基于已有模板生成控制与守护逻辑 |
| 分类核心 | [classifier-core.lua](../code/work/resident-dev-20261007/classifier-core.lua) | 软件分类器的核心判断 |
| 数据面模板 | [v20-five](../code/work/v20-five/) | 队列、分类与恢复的基础实现 |
| 内核准入模块 | [rp_ecm_gate_lab_ct.c](../code/work/resident-continuous-dev-20261008/endpoint-gate/rp_ecm_gate_lab_ct.c) | 连接及续租令牌核验 |
| 后端接口 | [ecm_ae_classifier_public.h](../code/work/resident-continuous-dev-20261008/endpoint-gate/ecm_ae_classifier_public.h) | 上游 ECM（增强连接管理器）接口声明 |

`current.json` 还标明生成链使用的中间适配器和验证入口。完整历史见[源码快照索引](../docs/history/README.md)。这些源码保留原有相对路径，因为生成脚本、导入和实验哈希均依赖它们。

## 检查

```sh
python3 tools/catalog.py show
make check
make test
```

检查使用仓库内的代码和数据，不启动控制器。设备运行需要与该版本匹配的构建产物及环境配置；源码入口清单本身不是安装入口。

## 接续开发

新修改使用独立工作目录，沿用代码的来源与许可证；更新源码清单后，再调整 `current.json` 并运行 `make catalog`。旧实验使用的源码和记录保持原字节。具体流程见[贡献说明](../CONTRIBUTING.md)。
