# CodeSolver · 项目说明与开发记录

<div align="center">

**基于 [SWE-agent](https://github.com/SWE-agent/SWE-agent) 的 AI 编程助手** —— 自动阅读代码、定位问题、生成并应用补丁

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Commits](https://img.shields.io/badge/提交数-2194-orange)
![Modules](https://img.shields.io/badge/Python%20模块-102-9cf)
![Tests](https://img.shields.io/badge/测试文件-22-blueviolet)

</div>

---

## 📌 项目简介

CodeSolver 是一个**自动化的 AI 编程助手**，在 SWE-agent 框架基础上定制开发。给定一个代码仓库和一段任务描述，它会自主完成：

1. **阅读代码** —— 浏览仓库结构、定位相关文件
2. **复现问题** —— 编写并运行脚本确认错误
3. **修改代码** —— 对非测试文件做最小化修改
4. **验证结果** —— 重新运行脚本确认修复
5. **生成补丁** —— 输出 patch 并可选自动应用到本地仓库

## 📊 项目规模

| 模块 | 规模 |
|------|------|
| Python 模块 | **102 个文件** |
| 核心包 `sweagent/` | 60 个文件 · **1.1 万+ 行代码** |
| 沙箱工具 `tools/` | **15 个工具** |
| 配置文件 `config/` | **24 个**（含 benchmark 配置） |
| 测试 `tests/` | **22 个测试文件** |
| 提交历史 | **2194 个提交** |

## ✨ 核心特性

- 🤖 **交互式 REPL**（`sweagent_chat.py`）：直接输入任务描述即可，无需记忆命令行参数
- 🔌 **默认 DeepSeek 模型**（`deepseek/deepseek-chat`）：成本低、速度快
- 📝 **自动应用补丁**：跑完可自动把改动落到本地仓库
- 📄 **运行日志**：每次运行自动记录时间、结果、模型、任务摘要
- 🧰 **完整工具链**：bash 执行、文件浏览（filemap）、代码编辑、提交前审阅（review-on-submit）等 15 个沙箱工具
- 🧪 **多 benchmark 支持**：内置 SWE-bench 等 24 个配置

## 🏗️ 项目结构

```
codesolver/
├── sweagent/              # 核心包（60 个模块，1.1 万+ 行）
│   ├── agent/             # 代理逻辑、模型、采样器、审阅器
│   ├── environment/       # 沙箱环境、仓库管理
│   ├── run/               # 运行入口、批量执行、hooks
│   ├── tools/             # 工具解析、命令执行
│   └── utils/             # 日志、工具函数
├── tools/                 # 15 个沙箱工具
├── config/                # 24 个配置文件
├── tests/                 # 22 个测试文件
├── sweagent_chat.py       # 交互式 REPL（本项目定制）
├── README.md              # 快速上手
└── OPTIMIZATION.md        # 本文档
```

## 🚀 快速开始

```bash
git clone https://github.com/jerry-di/codesolver.git
cd codesolver
pip install -e .
cp .env.example .env        # 填入 DEEPSEEK_API_KEY
python sweagent_chat.py     # 启动交互式 REPL
```

## 📝 开发记录

### 2026-10-30 · 功能与质量优化

**交互式 REPL（`sweagent_chat.py`）**

- 新增 `exit` / `quit` / `q` 退出命令，Ctrl+C 优雅退出
- 运行失败红色报错并显示退出码，运行前显示参数摘要
- 依赖缺失时给出友好中文提示
- 新增运行日志 `sweagent_chat.log`（自动被 `.gitignore` 忽略）
- 重构：`sweagent` 延迟导入 + 抽出纯函数 `build_command()` / `is_exit()`，提升可测试性

**工程化**

- 新增单元测试 `tests/test_sweagent_chat.py`（3 个用例）
- 修复 6 个文件的导入排序（`types.py` 重命名遗留）
- 新增 `README.md` 项目文档
- 修正 `.env.example`（补充 `DEEPSEEK_API_KEY`）

## ✅ 质量保障

- **Lint**：全项目通过 `ruff` 检查（`sweagent/`、`tests/` 零告警）
- **测试**：`python -m pytest tests/test_sweagent_chat.py`
- **兼容性说明**：`tools/` 沙箱工具刻意保持 Python 3.6 兼容（详见下方说明）

> ⚠️ `tools/` 目录的 33 个 lint 提示为**有意保留**：这些工具运行在目标仓库的沙箱里，必须兼容旧版 Python。ruff 建议的 `list[int]`、`X | None` 等新语法会在旧 Python 沙箱中崩溃，因此未做改动。

## 🔭 未来规划

- [ ] 把 `codesolver` 设为默认 git remote
- [ ] 配置 git 代理（`http.proxy`），简化国内推送流程
- [ ] REPL 支持从文件读取任务列表、批量执行
- [ ] 增加配置文件，持久化模型 / 仓库等默认选项
