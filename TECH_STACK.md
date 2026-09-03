# SWE-agent 项目技术栈总览

> 本文档对 `swe` 仓库（即 **SWE-agent**，版本 `1.1.0`）进行了全量遍历，梳理出项目使用的全部技术栈及其用途。
> 生成日期：2026-08-31

---

## 一、项目概览

| 项目 | 说明 |
| --- | --- |
| **名称** | SWE-agent |
| **版本** | 1.1.0 |
| **一句话定位** | 官方 SWE-agent 包 —— 一个开源的 **Agent Computer Interface (ACI)**，用于让语言模型像软件工程师一样工作 |
| **核心功能** | 让大语言模型（LLM）在**沙箱化的 Docker 容器**中自主解决 GitHub issue / 编程任务 |
| **许可证** | MIT |
| **Python 版本** | `>= 3.11`（3.11、3.12 受 CI 支持） |
| **CLI 入口** | `sweagent` → `sweagent.run.run:main` |
| **主页 / 文档** | https://swe-agent.com |

---

## 二、编程语言

| 语言 | 用途 |
| --- | --- |
| **Python 3.11+** | 项目主体语言，全部核心逻辑（agent、environment、tools、CLI） |
| **Bash / Shell** | 工具（tools）中的命令行脚本、install 脚本、容器内 REPL 命令 |
| **YAML** | 所有配置文件（agent 模板、benchmark、工具 bundle 的 `config.yaml`） |
| **HTML / CSS / JavaScript** | trajectory 网页查看器（`inspector/static.py` 内嵌 HTML）、网页浏览工具的页面交互（JS 通过 Playwright 执行） |

---

## 三、核心 Python 依赖

来源：`pyproject.toml` 的 `dependencies` 段。

### 3.1 LLM / AI

| 库 | 用途 |
| --- | --- |
| **litellm** (`>=1.44.12`) | 统一的大模型接入层，通过同一套接口调用 Anthropic / OpenAI / 各类 API，负责模型推理与成本统计（`agent/models.py` 中的 `LiteLLMModel`） |

### 3.2 运行时 / 沙箱（SWE-ReX 生态）

| 库 | 用途 |
| --- | --- |
| **swe-rex** (`>=1.4.0`) | **关键依赖**。提供沙箱运行时与部署抽象（`swerex.runtime`、`swerex.deployment`），SWE-agent 通过它连接 Docker 容器执行命令、读写文件、上传代码。`sweagent/environment/swe_env.py` 直接基于它构建 |
| **GitPython** | 本地 git 仓库操作（读取提交哈希、判断仓库、解析 diff） |
| **ghapi** (`>=1.0.0,<2`) | GitHub REST API 客户端，用于读取 issue、克隆仓库、开 PR（`utils/github.py`、`run/hooks/open_pr.py`） |

### 3.3 数据 / 科学计算

| 库 | 用途 |
| --- | --- |
| **datasets** | 加载 HuggingFace 数据集（如 SWE-bench、SWE-smith 等 benchmark 实例） |
| **numpy** | 数值计算（统计、reviewer 的分数计算） |
| **pandas** | 表格数据处理 |

### 3.4 配置 / 数据模型

| 库 | 用途 |
| --- | --- |
| **pydantic** | 数据模型 / 配置校验，几乎所有 config 类（`ModelConfig`、`ToolConfig`、`RepoConfig` 等）都是 `BaseModel` |
| **pydantic-settings** | 基于环境变量的设置加载 |
| **python-dotenv** | 加载 `.env`（如 `GITHUB_TOKEN`） |
| **ruamel.yaml** | 保留注释/格式的 YAML 读写（配置文件、trajectory 序列化） |
| **simple-parsing** | 将 dataclass/pydantic 模型一键转成 argparse 命令行参数 |
| **rich-argparse** | 美化 argparse 帮助输出 |

### 3.5 CLI / 终端 UI

| 库 | 用途 |
| --- | --- |
| **rich** | 终端富文本渲染（彩色日志、表格、进度条、面板） |
| **textual** (`>=1.0.0`) | TUI 框架，用于命令行 trajectory 查看器 `sweagent run inspect` |
| **tabulate** | 纯文本表格（`compare_runs.py` 等统计输出） |

### 3.6 Web

| 库 | 用途 |
| --- | --- |
| **flask** | 轻量 Web 服务。① 网页版 trajectory 查看器；② 网页浏览工具（web_browser bundle）的浏览器控制后端 |
| **flask-cors** | Flask 跨域支持 |
| **flask-socketio** | WebSocket 实时通信（trajectory 实时推送） |
| **requests** | HTTP 客户端（下载问题描述、读取 URL、网页浏览工具） |

### 3.7 其他工具库

| 库 | 用途 |
| --- | --- |
| **tenacity** | 重试机制（模型调用、网络请求的指数退避重试） |
| **unidiff** | 解析/生成 unified diff patch（`utils/patch_formatter.py`） |
| **jinja2** | 模板渲染（agent 的 system/instance/next_step 模板 `{{working_dir}}` 等占位符） |
| **tabulate** | （同上） |
| **packaging** | 版本号解析与比较（校验 swe-rex 最低版本） |

---

## 四、开发 / 测试 / 文档依赖

来源：`pyproject.toml` 的 `[project.optional-dependencies].dev`。

| 类别 | 库 | 用途 |
| --- | --- | --- |
| **测试** | pytest | 测试框架 |
| | pytest-cov | 覆盖率（配合 Codecov） |
| | pytest-xdist | 并行测试（`-n auto`） |
| **文档** | mkdocs-material | 文档站点主题（`mkdocs.yml` 配置） |
| | mkdocstrings[python] | 从 docstring 自动生成 API 参考 |
| | griffe-pydantic | 让 mkdocstrings 识别 pydantic 模型 |
| | mike | 文档多版本部署（`latest` / `0.7` / `1.0` 版本选择器） |
| | mkdocs-glightbox | 图片灯箱 |
| | mkdocs-include-markdown-plugin | 文档中嵌入外部 Markdown |
| **工具链** | pre-commit | 提交前钩子（见下） |
| | pipx | 隔离安装 CLI 工具 |

---

## 五、代码质量 / 格式化工具

来源：`pyproject.toml` 的 `[tool.ruff]` 段、`.pre-commit-config.yaml`。

| 工具 | 用途 |
| --- | --- |
| **ruff** (`v0.15.20`) | Python linter + formatter（替代 flake8/black/isort，启用了 `E/PLE/F/UP/SIM/RET/PTH/PT/EM` 等大量规则） |
| **typos** | 拼写检查（`.py/.md/.rst/.yaml/.toml`） |
| **prettier** | JS/CSS 格式化 |
| **pre-commit-hooks** | 通用钩子：大文件检查、冲突标记、私钥检测、行尾处理等 |

---

## 六、CI / CD 与基础设施

来源：`.github/workflows/`。

| 工作流 / 组件 | 用途 |
| --- | --- |
| **pytest.yaml** | 在 Python 3.11 / 3.12 上跑 pytest，使用 `uv` 安装依赖，上传覆盖率到 Codecov |
| **build-docs.yaml** | 用 mkdocs + mike 构建并部署文档到 GitHub Pages |
| **check-links-periodic.yaml / check-links-pr.yaml** | Markdown 链接检查（`tcort/markdown-link-check`） |
| **Codecov** | 覆盖率 + 测试结果上报（`codecov.yml`） |
| **uv** | CI 中的 Python 包管理器（替代 pip） |
| **Docker** | agent 的沙箱执行环境（通过 swe-rex 的 `DockerDeploymentConfig` 管理，也支持 modal 部署） |
| **Dev Container** | `.devcontainer/devcontainer.json` 基于 miniconda 镜像 + docker-in-docker，供 Codespaces / VS Code 使用 |

---

## 七、项目目录结构与职责

### 7.1 `sweagent/` — 核心包（60 个 `.py` 文件）

```
sweagent/
├── run/          # CLI 入口与运行逻辑
├── agent/        # Agent 主体、模型抽象、历史处理、评审器
├── environment/  # 沙箱环境 SWEEnv、仓库 Repo、钩子
├── tools/        # 工具配置、命令解析、bundle 加载
├── utils/        # 日志、GitHub、配置、序列化等工具
├── inspector/    # trajectory 网页查看器
├── types.py      # 全局共享类型
└── exceptions.py # 自定义异常
```

#### `sweagent/run/` — 运行入口

| 模块 | 用途 |
| --- | --- |
| `run.py` | 主 CLI（`sweagent`），聚合所有子命令 |
| `run_single.py` | 对单个 problem statement（如一个 GitHub issue）运行 agent |
| `run_batch.py` | 批量运行（如 SWE-bench 基准测试） |
| `run_replay.py` | 重放 trajectory / demo 文件（回填环境输出、调试工具） |
| `run_shell.py` | 半交互式 shell 模式（实验性 `sweagen-sh`） |
| `run_traj_to_demo.py` | 把 trajectory 转成可编辑的 demo YAML |
| `inspector_cli.py` | 基于 textual 的命令行 trajectory 查看器 |
| `compare_runs.py` | 对比多个 run 的 resolved/submitted 实例（tabulate 表格） |
| `merge_predictions.py` | 合并多个预测文件为 `preds.json` |
| `extract_pred.py` | 从 `.traj` 文件恢复 `.pred` 文件 |
| `quick_stats.py` | 从 `.traj` 文件统计成功率/成本等指标 |
| `remove_unfinished.py` | 清理未完成的 trajectory |
| `batch_instances.py` | 实例数据源：`file` / `huggingface` / `swe_bench` / `expert_file` / `swesmith` |
| `common.py` | run 脚本共享逻辑 |
| `_progress.py` | 批量运行的进度渲染 |
| `hooks/` | `RunHook` 钩子：`apply_patch.py`（应用补丁）、`open_pr.py`（自动开 PR）、`swe_bench_evaluate.py`（SWE-bench 评测） |

#### `sweagent/agent/` — Agent 主体

| 模块 | 用途 |
| --- | --- |
| `agents.py` | 核心 `DefaultAgent` 类、`ShellAgentConfig`，主导 agent 行为 |
| `models.py` | 模型抽象层：`LiteLLMModel`（真实 LLM）、`HumanModel`、`ReplayModel`、`InstantEmptySubmitModel` 等 |
| `action_sampler.py` | 从模型输出采样动作 |
| `history_processors.py` | 历史消息处理器（如 `cache_control`，给 Anthropic 最近 2 条消息加缓存） |
| `problem_statement.py` | 问题描述处理（GitHub issue、多模态图片、base64 编码） |
| `reviewer.py` | 评审器：实现"重试 + 选最优解"的循环 |
| `hooks/` | `AbstractAgentHook`、`status.py`（状态上报钩子） |
| `extra/shell_agent.py` | 半交互式的 `ShellAgent`（人机协作） |

#### `sweagent/environment/` — 沙箱环境

| 模块 | 用途 |
| --- | --- |
| `swe_env.py` | `SWEEnv`：对接 **SWE-ReX**，在 Docker 容器中执行命令、管理会话 |
| `repo.py` | `Repo`：GitHub 仓库 / 本地仓库的克隆、安装、diff 生成 |
| `hooks/` | `EnvHook` 环境钩子、`status.py` 状态钩子 |

#### `sweagent/tools/` — 工具系统

| 模块 | 用途 |
| --- | --- |
| `tools.py` | `ToolConfig`（工具配置）、`ToolHandler`（工具加载/安装/执行） |
| `commands.py` | `Command` / `Argument` 定义，支持 bash 函数和 YAML docstring |
| `parsing.py` | 模型输出解析器：`ThoughtActionParser`（反引号包裹命令）、`FunctionCallingParser`（function calling）等 |
| `bundle.py` | `Bundle` / `BundleConfig`，加载 `tools/` 下的工具 bundle |
| `utils.py` | 多行命令、参数引号处理 |

#### `sweagent/utils/` — 工具函数

| 模块 | 用途 |
| --- | --- |
| `log.py` | 基于 rich 的日志系统（彩色、emoji、TRACE 级别） |
| `github.py` | GitHub URL 解析、issue 抓取、PR 相关 API |
| `config.py` | 配置路径解析、`.env` 加载 |
| `files.py` | 文件读写（JSON/YAML 自动判断） |
| `serialization.py` | ruamel.yaml 序列化（保留换行） |
| `patch_formatter.py` | 基于 unidiff 的 patch 格式化 |
| `jinja_warnings.py` | 检测模板中 `{var}` 误写成 `{{var}}` 的告警 |

#### `sweagent/inspector/` — 网页查看器

| 模块 | 用途 |
| --- | --- |
| `server.py` | 基于 `http.server` + flask 的 trajectory 网页服务 |
| `static.py` | 生成静态 HTML 查看页（内嵌 CSS/JS） |

---

### 7.2 `tools/` — 工具 Bundle（Agent 可用命令）

这些 bundle 会被复制进沙箱容器并加入 `$PATH`，每个目录含 `config.yaml`（工具声明）、`bin/`（可执行文件）、`install.sh`（依赖安装）。

| Bundle | 提供命令 | 说明 / 技术 |
| --- | --- | --- |
| **registry** | `_read_env` / `_write_env` | 跨工具调用持久化状态（写入 `/root/.swe-agent-env` 文件，避免环境变量无法在子进程共享） |
| **edit_anthropic** | `str_replace_editor` | Anthropic 风格的查看/创建/编辑文件工具（view/create/str_replace/insert/undo_edit），依赖 **tree-sitter** |
| **filemap** | `filemap` | 打印 Python 文件结构（跳过冗长函数体），依赖 **tree-sitter + tree-sitter-languages** |
| **forfeit** | `exit_forfeit` | 放弃当前任务 |
| **image_tools** | `view_image` | 查看图片（base64 编码成 Markdown 供多模态模型使用） |
| **multilingual_setup** | `do_nothing` | 多语言环境初始化（bash 环境变量导入、Python 3.11 路径设置） |
| **review_on_submit_m** | `submit` | 提交前触发评审流程（多模态） |
| **search** | `find_file` / `search_dir` / `search_file` | 文件/内容搜索（bash 实现，用环境变量保存结果与索引） |
| **submit** | `submit` | 提交当前修改 |
| **web_browser** | `open_site`、`click_mouse`、`screenshot_site`、`execute_script_on_page` 等 19 个命令 | **完整网页浏览器控制**：后端 **Flask** + **Playwright**（Chromium），支持鼠标键盘、截图、JS 执行、console 抓取 |
| **windowed** | `open` / `goto` / `create` / `scroll_up` / `scroll_down` | 分窗口查看文件（默认 100 行/窗口，环境变量 `WINDOW`/`OVERLAP` 控制） |
| **windowed_edit_linting** | `edit` | 行区间替换 + **flake8** 语法检查 |
| **windowed_edit_replace** | `edit` / `insert` | 搜索替换 / 插入 + **flake8** 检查 |
| **windowed_edit_rewrite** | `edit` | 重写当前显示行 |
| **diff_state** | `_state_diff_state` | 输出当前 git diff 状态 |

> 工具技术要点：Python 脚本（`#!/usr/bin/env python3`）、bash 函数脚本、`tree-sitter`（代码解析）、`flake8`（lint）、`flask + playwright + chromium`（浏览器）、JSON 文件（状态持久化）。

---

### 7.3 `config/` — 配置模板

| 路径 | 说明 |
| --- | --- |
| `default.yaml` | **默认配置**（原 `anthropic_filemap.yaml`），Anthropic computer use 风格模板 + `edit_anthropic`/`review_on_submit_m` bundle + `function_calling` 解析 |
| `bash_only.yaml` | 极简 bash-only 配置，兼容任意指令跟随模型（THOUGHT + bash 代码块） |
| `coding_challenge.yaml` | 编程挑战（如 LeetCode）配置，展示如何改造 agent 做非 SWE 任务 |
| `default_backticks.yaml` | 反引号解析版本的默认配置 |
| `default_mm_no_images.yaml` | 多模态（不含图片）配置 |
| `default_mm_with_images.yaml` | 多模态（含图片）配置 |
| `benchmarks/` | SWE-bench 基准测试复现配置（`swe_bench lite/test` 等） |
| `demo/` | 演示配置（`default` / `no_instructions` / `only_bash`） |
| `exotic/` | 特殊配置（`default_shell`、`windowed_replace` 等） |
| `human/` | 人机协作配置（`human.yaml` / `human_demo.yaml`） |
| `sweagent_0_7/` | 0.7 版本向后兼容配置（`07.yaml`、`07_fcalling.yaml`、`07_thought_action.yaml` 等） |

---

### 7.4 `tests/` — 测试

| 内容 | 说明 |
| --- | --- |
| `test_agent.py`、`test_models.py`、`test_env.py` 等 | 核心单元测试（agent、模型、环境、解析、hooks、batch） |
| `test_commands/` | 命令解析测试（含交互式 dummy 脚本） |
| `test_data/` | 测试数据 |
| `tools/` | 工具 bundle 的测试（edit_replace、字符串分割等） |
| `conftest.py` | pytest fixture |

---

### 7.5 `trajectories/` — 轨迹与演示

| 内容 | 说明 |
| --- | --- |
| `demonstrations/` | 演示/示例 trajectory（function calling、xml、ctf、human thought 等样例）、`.demo.yaml` 演示文件 |

---

### 7.6 其他配置

| 文件 | 用途 |
| --- | --- |
| `mkdocs.yml` | MkDocs Material 文档站配置（导航、插件、Google Analytics） |
| `.env.example` | 环境变量示例（`GITHUB_TOKEN`） |
| `.pre-commit-config.yaml` | pre-commit 钩子（ruff/typos/prettier） |
| `codecov.yml` | Codecov 覆盖率配置 |
| `mlc_config.json` | Markdown link check 忽略规则 |
| `.devcontainer/` | VS Code / Codespaces 开发容器配置 |
| `.cursor/rules/` | Cursor 编辑器项目规则（含项目架构概述） |
| `.git-blame-ignore-revs` | git blame 忽略的格式化提交 |

---

## 八、架构要点总结

1. **ACI 模式**：SWE-agent 通过 "Agent Computer Interface" 让 LLM 以"思考 → 动作 → 观察"的循环自主编程。
2. **三层结构**：
   - **Agent 层**（`sweagent/agent/`）：LLM 调用、模板渲染、历史处理、动作解析。
   - **环境层**（`sweagent/environment/` + **SWE-ReX**）：在 Docker 沙箱中执行动作、管理 git 仓库。
   - **工具层**（`tools/` bundles）：以文件/命令形式提供给 agent 的编辑、搜索、浏览等能力。
3. **模型无关**：通过 **litellm** 支持 Anthropic / OpenAI / 自建 API 等任意 provider。
4. **部署无关**：通过 **SWE-ReX** 抽象，支持 Docker / Modal 等运行时。
5. **可扩展钩子**：三处钩子系统（`RunHook` / `AgentHook` / `EnvHook`）用于接入评测、开 PR、状态上报等自定义逻辑。

---

## 九、技术栈速查表（一图流）

| 类别 | 技术 |
| --- | --- |
| 语言 | Python 3.11+、Bash、YAML、HTML/CSS/JS |
| LLM 接入 | litellm |
| 沙箱运行时 | swe-rex、Docker、Modal |
| Git/GitHub | GitPython、ghapi、GitHub Actions |
| 配置/模型 | pydantic、pydantic-settings、python-dotenv、simple-parsing、ruamel.yaml |
| CLI/TUI | rich、rich-argparse、textual、tabulate |
| Web | flask、flask-cors、flask-socketio、requests、Playwright(Chromium) |
| 数据 | datasets、numpy、pandas |
| 补丁/模板 | unidiff、jinja2 |
| 工具辅助 | tree-sitter、flake8、tenacity |
| 测试 | pytest、pytest-cov、pytest-xdist |
| 文档 | mkdocs-material、mkdocstrings、griffe-pydantic、mike、glightbox |
| 质量 | ruff、typos、prettier、pre-commit |
| 基础设施 | GitHub Actions、Codecov、uv、Dev Container(miniconda + docker-in-docker) |
