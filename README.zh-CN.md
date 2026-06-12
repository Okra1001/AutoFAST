# AutoFAST v1.0

[![English](https://img.shields.io/badge/Documentation-English-blue)](README.md)
[![OpenFAST](https://img.shields.io/badge/OpenFAST-官方仓库-blue)](https://github.com/OpenFAST/openfast)

AutoFAST 是一个面向 Codex 及其他智能 Agent 的通用 OpenFAST Skill，旨在帮助用户从一个 OpenFAST 可执行文件或已有模型目录出发，获得可运行、可验证、可追溯的仿真结果。

AutoFAST 不绑定任何特定风机、平台或研究课题。它既可以帮助初学者完成第一次可靠仿真，也可以帮助研究人员组织参数扫频、故障诊断、结果比较和可复现性记录。

AutoFAST **不会替代 OpenFAST**。它围绕官方 [OpenFAST](https://github.com/OpenFAST/openfast) 求解器及其输入模型，为 Agent 提供一套可靠的工程工作流。

## 主要功能

- 当用户只有 OpenFAST 可执行文件时，识别当前状态并指导获取版本匹配、来源明确的官方模型。
- 自动发现 `.fst`、Driver 输入、模块文件、引用关系和缺失依赖。
- 按字段名称安全修改标量参数，支持 dry-run、备份和修改前后 diff。
- 运行单个算例，并记录命令、工作目录、日志、返回码和输出证据。
- 使用 CSV 管理参数扫频，逐算例保存状态，并支持中断后继续。
- 根据日志和模型依赖关系对常见报错进行分类，给出证据、可能原因和最小修复方案。
- 直接分析文本 `.out`；安装 OpenFAST Toolbox 或 pyFAST 后可分析二进制 `.outb`。
- 对两个受控算例进行通道级比较，计算均值偏差、RMSE 和相对 RMSE。
- 生成包含输入文件哈希、可执行文件版本、运行命令、环境和分析信息的 provenance 记录。

## 安装

将 `autofast` 文件夹复制到 Agent 的 Skills 目录，或者安装已经打包好的：

```text
dist/autofast.skill
```

推荐使用以下方式显式调用：

```text
$autofast
```

示例：

```text
使用 $autofast 检查这个 OpenFAST release，选择一个版本匹配的官方案例，
运行基准仿真，并生成可追溯的验证结果。
```

## 典型工作流程

1. **检查环境**
   - 定位 OpenFAST 或 Driver 可执行文件。
   - 获取版本信息并扫描当前目录中的模型入口。

2. **建立基准**
   - 优先运行来源明确且未经修改的官方或用户基准模型。
   - 不在没有物理模型时凭空生成一台风机。

3. **定义研究问题**
   - 明确需要改变的独立变量。
   - 明确必须保持一致的控制变量。

4. **安全修改输入**
   - 通过字段身份查找参数，不依赖固定行号。
   - 先预览 diff，再执行原子写入和重新解析。

5. **运行仿真**
   - 大规模扫频前先验证一个代表性算例。
   - 为每个算例保存独立日志和增量状态。

6. **诊断报错**
   - 优先寻找最早出现的致命错误。
   - 根据实际证据执行最小修复，不通过随意关闭物理模块来强行跑通。

7. **验证结果**
   - 检查正常终止、输出完整性、最终时间和有限数值。
   - 进一步检查物理合理性和受控比较是否有效。

8. **保存溯源信息**
   - 记录输入文件、哈希、版本、命令、日志、输出和统计方法。
   - 明确区分成功、失败、跳过和尚未验证的算例。

## 设计原则

- 不硬编码特定风机或平台。
- 只有求解器、没有模型时，不虚构仿真输入。
- 修改模型前先建立未修改基准。
- 每次只改变声明过的研究变量。
- 按字段身份修改参数，不使用记忆中的固定行号。
- 修复报错时依据日志和模型链，优先采用最小修改。
- “程序返回 0”只是必要条件，不代表结果具有物理可信度。
- 仿真结果必须能够追溯到输入、版本、命令和后处理方法。

## 环境要求

- Python 3.10 或更高版本，用于运行附带脚本。
- OpenFAST 可执行文件和完整模型目录，用于执行真实物理仿真。
- 可选安装 OpenFAST Toolbox 或 pyFAST，用于读取二进制 `.outb`。

AutoFAST 的核心脚本只依赖 Python 标准库。

## OpenFAST 相关资源

- 官方仓库：[OpenFAST/openfast](https://github.com/OpenFAST/openfast)
- 官方文档：[openfast.readthedocs.io](https://openfast.readthedocs.io/)
- Release 下载：[OpenFAST releases](https://github.com/OpenFAST/openfast/releases)
- 回归测试与参考输入：[OpenFAST/r-test](https://github.com/OpenFAST/r-test)

## 运行测试

```powershell
python -m unittest discover -s autofast/tests -v
```

## 当前边界

- 通用依赖检查器采用保守解析方法，并不是所有 OpenFAST 版本和模块的完整 schema 解析器。
- 某些未启用模块仍可能包含不存在的文件引用，因此 unresolved reference 需要结合模块开关复核。
- 表格、`OutList`、翼型极曲线和特定版本的数据块需要使用专门的结构化修改方法。
- 功率、载荷和平台运动等物理验收标准必须根据具体模型和研究目标确定。

## 致谢

AutoFAST 围绕 OpenFAST 构建，没有 OpenFAST 项目就不会有 AutoFAST。我们特别感谢 **Jason Jonkman** 对 FAST/OpenFAST 的奠基性领导和长期贡献，同时感谢所有 OpenFAST 维护者、研究人员、软件工程师、机构支持者以及社区贡献者持续开发、测试、记录并共享这一重要的开源工具。

AutoFAST 是独立的社区项目，并非 OpenFAST 或 National Laboratory of the Rockies 的官方产品。

## 许可证

MIT
