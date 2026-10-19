# 贡献与维护

## 源码入口

从 [src/current.json](src/current.json) 选择组件；[主线说明](src/README.md)介绍生成链与依赖。`code/work/` 中的编号表示研究轮次，文件夹日期或编号不能单独作为选用依据。

新功能在新的工作目录中实现，保留原有来源和许可证声明。修改后的源文件加入 `source-manifest.json`，验证完成后再更新主线选择及对应证据。旧轮次绑定的源文件和实测数据保留原字节。

## 文档与索引

- README 保持项目概览；具体实验过程写入对应文档。
- `docs/STATE.md` 和 `docs/PLAN.md` 按日期说明进展，状态变化才更新实验记录。
- `src/current.json` 是主线选择的手工输入。
- `docs/history/` 和 `LICENSES/inventory.json` 由 `make catalog` 生成；使用 `make check` 检查同步状态。
- 已有 `tools/update_docs_nss*.py` 用于重建特定历史轮次，后续维护不再使用它们累积重写首页。

## 验证

```sh
make catalog
make test
make check
```

索引检查核对全部源文件的哈希、主线选择和许可证声明；仓库检查另行核对原实验数据与文档链接。功能变更还应运行相关离线回放。硬件结果需记录设备、版本、负载、失败及恢复过程，与离线检查分开报告。

提交说明问题、变更和实际执行的检查；使用 `Signed-off-by:` 署名，并注明 AI 协助及人工或工具验证的范围。

## 许可证

项目原创代码及配套文档采用 GPL-2.0-only。第三方代码保留自身许可与署名，详见[许可证说明](docs/LICENSING.md)。新增第三方文件时补充对应许可文本和来源，再生成索引。
