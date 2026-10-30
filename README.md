# CodeSolver

基于 [SWE-agent](https://github.com/SWE-agent/SWE-agent) 的 AI 编程助手：给定一个代码仓库和任务描述，AI 会自动阅读代码、定位问题、修改代码，并生成 / 应用补丁（patch）。

## ✨ 特点

- 🤖 **交互式 REPL**：直接输入任务描述即可，无需记忆一堆命令行参数（见 `sweagent_chat.py`）
- 🔌 **默认使用 DeepSeek**：模型 `deepseek/deepseek-chat`，成本低、速度快
- 📝 **自动应用补丁**：跑完后可自动把改动应用到本地仓库

## 环境要求

- Python 3.11+
- 一个 DeepSeek API Key（前往 DeepSeek 开放平台申请）

## 安装

```bash
git clone https://github.com/jerry-di/codesolver.git
cd codesolver
pip install -e .
```

## 配置

复制 `.env.example` 为 `.env`，并填入你的 API Key：

```bash
cp .env.example .env
```

编辑 `.env`：

```dotenv
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxx
# 可选：需要 GitHub 相关功能（开 PR、拉取私有仓库）时再填写
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxx
```

> ⚠️ `.env` 已被 `.gitignore` 忽略，**不要**把真实的 Key 提交到仓库。

## 使用

### 方式一：交互式 REPL（推荐）

```bash
python sweagent_chat.py
```

按提示依次输入：

1. **模型** —— 回车使用默认 `deepseek/deepseek-chat`
2. **仓库路径** —— 回车使用当前项目路径
3. **是否自动应用补丁** —— 默认 `y`

然后循环输入任务描述（支持多行粘贴，输入空行结束），例如：

```text
修复登录接口在空用户名时抛出的 500 错误，并补充输入校验。
```

### 方式二：命令行

```bash
sweagent run \
  --config config/default.yaml \
  --agent.model.name deepseek/deepseek-chat \
  --env.repo.path /path/to/your/repo \
  --problem_statement.text "要解决的问题描述"
```

## 许可

[MIT License](LICENSE)，基于 SWE-agent 二次开发。
