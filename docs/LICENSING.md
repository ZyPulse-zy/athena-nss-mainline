# 许可证与来源

## 项目代码

项目原创代码、维护工具及配套文档采用 **GPL-2.0-only**，许可证全文见根目录 [LICENSE](../LICENSE)。本次补齐仓库级许可说明，已有源码和实测记录的内容哈希保持不变。

部分历史 C 文件使用 `SPDX-License-Identifier: GPL-2.0`。索引将这一旧标识记录为 GPL-2.0-only，同时保存原标识；原文件头不改写。

## 第三方接口头文件

各轮 `endpoint-gate/ecm_ae_classifier_public.h` 保留 The Linux Foundation 与 Qualcomm Innovation Center 的版权和 ISC 许可声明。其许可文本见 [LICENSES/ISC.txt](../LICENSES/ISC.txt)，原署名与八个副本路径见 [NOTICE](../NOTICE)。这些文件继续使用自身的 ISC 条款。

## 索引

[LICENSES/inventory.json](../LICENSES/inventory.json) 列出带显式许可声明的源码路径、哈希、原标识和归类依据，并汇总源码清单中的许可分布。未带独立声明的项目原创文件使用上述默认许可。

```sh
make catalog
make check
```

索引工具识别源码开头的声明；遇到新的 SPDX 标识或未识别的版权声明时停止，要求先补充对应许可信息。

## 参考

- [GNU GPL 第 2 版原文](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)
- [SPDX 的 GPL-2.0 标识说明](https://spdx.org/licenses/GPL-2.0.html)
- [SPDX 的 ISC 许可文本](https://spdx.org/licenses/ISC.html)
- [GitHub 的仓库许可证说明](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)
