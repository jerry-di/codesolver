# 项目优化记录

> 项目：**CodeSolver** —— 基于 [SWE-agent](https://github.com/SWE-agent/SWE-agent) 的 AI 编程助手。
> 本文档记录 2026-10-30 做的一轮全面优化，说明改了什么、为什么改，以及哪些地方**刻意保留未动**。

---

## 一、改动总览

| 文件 | 改动内容 | 类型 |
|------|----------|------|
| `sweagent_chat.py` | REPL 健壮性 + 重构 + 运行日志 | 增强 / 重构 |
| `tests/test_sweagent_chat.py` | 新增单元测试 | 测试 |
| `README.md` | 新增项目说明 | 文档 |
| `.env.example` | 补充 `DEEPSEEK_API_KEY` | 修正 |
| `sweagent/agent/*.py` 等 6 个文件 | 导入排序修复 | 清理 |
| `TECH_STACK.md` | 删除（提交） | 清理 |

---

## 二、详细说明

### 1. 交互式 REPL（`sweagent_chat.py`）

**功能增强：**
- 新增 `exit` / `quit` / `q` 退出命令（原来只能 Ctrl+C 强退，还会报堆栈）
- Ctrl+C 优雅退出，不再打印报错
- 子进程运行失败时红色报错并显示退出码（原来失败也静默继续）
- 运行前显示一行摘要：仓库 / 模型 / 是否应用补丁
- 依赖没装时给出友好中文提示，而不是一堆 `ModuleNotFoundError` 堆栈
- 新增运行日志 `sweagent_chat.log`：每次运行追加一行 `时间 | 结果 | 模型 | 仓库 | 任务摘要`，方便回看（该文件已被 `.gitignore` 的 `*.log` 规则自动忽略）

**重构（可测试性）：**
- `sweagent` 改为**延迟导入**（只在真正运行时才 import），模块可被单独导入而不依赖完整依赖树
- 抽出纯函数 `build_command()`（拼接命令行）和 `is_exit()`（判断退出词），逻辑清晰且可单测

### 2. 单元测试（`tests/test_sweagent_chat.py`）

为上面两个纯函数补了 3 个测试：退出词大小写/空白匹配、命令行拼接（含/不含补丁参数）。

运行方式：
```bash
python -m pytest tests/test_sweagent_chat.py
```

### 3. README.md

新增了项目介绍、安装、配置（DeepSeek Key）、两种使用方式（REPL / 命令行）的完整说明。

### 4. .env.example

补上了主键 `DEEPSEEK_API_KEY`（默认模型 `deepseek/deepseek-chat` 必需），`GITHUB_TOKEN` 改为可选。原来只写了 `GITHUB_TOKEN`，和实际不符。

### 5. 导入排序修复（6 个文件）

`types.py` 重命名为 `shared_types.py` 时，有 6 个文件的 import 顺序乱了。已用 ruff 自动修复（纯排序，零风险）：
- `sweagent/agent/action_sampler.py`
- `sweagent/agent/agents.py`
- `sweagent/agent/extra/shell_agent.py`
- `sweagent/agent/models.py`
- `sweagent/agent/reviewer.py`
- `tests/test_models.py`

---

## 三、刻意保留未改动的部分（重要）

### `tools/` 目录的 33 个 lint 提示 —— 不动

`tools/` 是运行在**目标仓库沙箱里**的工具，必须兼容旧版 Python。代码里有明确注释（`flake8_utils.py`：`don't use capture_output because it's not compatible with python3.6`）。

ruff 建议的 `List[int] → list[int]`、`Optional[X] → X | None` 等属于**新语法**，在旧 Python 沙箱里会直接崩溃。项目自己的 pre-commit 也正是因此排除了 `tools/**/*.py`。

> 我在优化过程中一度被 ruff 自动修复改到了 `tools/`，发现后**已全部回退**。

### 上游 `sweagent/` 大库代码 —— 不动

这是成熟的 SWE-agent 上游代码，本身已经很干净（ruff 全项目检查除上述外无其他问题）。没有做无意义的改动。

---

## 四、验证方式

```bash
# 单元测试（需在你的 PyCharm 环境里跑，本机依赖齐全）
python -m pytest tests/test_sweagent_chat.py

# 项目代码 lint 检查（应全部通过）
python -m ruff check sweagent tests

# 启动交互式 REPL
python sweagent_chat.py
```

---

## 五、后续建议

1. **撤销 token**：推送用的 Personal Access Token 曾出现在聊天记录里，建议去 GitHub 撤销（Settings → Developer settings → Personal access tokens）。
2. **把 `codesolver` 设为默认 remote**：目前本地 `origin` 仍指向 `SWE-agent`，`git push` 会推到上游而不是你的 `codesolver`。
3. **配置 git 代理**：国内直连 GitHub 不通，建议把 `http.proxy = http://127.0.0.1:7890` 写进 git 配置，以后 push 不用每次手动加参数。
