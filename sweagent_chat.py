#!/usr/bin/env python3
"""Interactive REPL wrapper for SWE-agent.

Lets you "chat" with SWE-agent by typing tasks directly instead of
passing files and a long list of CLI flags.

Usage:
    python sweagent_chat.py
"""

from __future__ import annotations

import subprocess
import sys

from rich.console import Console
from rich.prompt import Confirm, Prompt

console = Console()

try:
    from sweagent import CONFIG_DIR, REPO_ROOT
except ImportError as e:
    console.print(f"[bold red]❌ 无法导入 sweagent：{e}[/bold red]")
    console.print("[dim]请先在项目根目录安装依赖：pip install -e .[/dim]")
    raise SystemExit(1)

DEFAULT_MODEL = "deepseek/deepseek-chat"
DEFAULT_CONFIG = CONFIG_DIR / "default.yaml"

EXIT_KEYWORDS = ("exit", "quit", "q")


def read_task() -> str | None:
    """Read a multi-line task. Finish with an empty line.

    Returns None if the user asks to exit the REPL (``exit``/``quit``/``q``).
    """
    console.print("[bold cyan]输入任务描述：[/bold cyan]")
    console.print("[dim]（可多行粘贴；结束时空一行再回车；输入 exit 退出）[/dim]")
    lines: list[str] = []
    while True:
        try:
            line = input()
        except EOFError:
            return None
        if line.strip() == "":
            if lines:
                break
            continue
        if line.strip().lower() in EXIT_KEYWORDS:
            return None
        lines.append(line)
    return "\n".join(lines).strip()


def run_one(repo: str, task: str, model: str, apply_patch: bool) -> None:
    """Run SWE-agent once for the given repo + task."""
    cmd = [
        sys.executable,
        "-m",
        "sweagent",
        "run",
        "--config",
        str(DEFAULT_CONFIG),
        "--agent.model.name",
        model,
        "--env.repo.path",
        repo,
        "--problem_statement.text",
        task,
        "--env.deployment.python_standalone_dir=",
    ]
    if apply_patch:
        cmd.append("--actions.apply_patch_locally=True")

    console.print("\n[bold green]>>> 正在运行[/bold green]")
    console.print(f"[dim]仓库: {repo} | 模型: {model} | 应用补丁: {apply_patch}[/dim]")
    console.print(f"[dim]{' '.join(cmd)}[/dim]\n")

    result = subprocess.run(cmd)
    if result.returncode == 0:
        console.print("[bold green]✅ 运行完成[/bold green]")
    else:
        console.print(f"[bold red]❌ 运行失败（退出码 {result.returncode}）[/bold red]")


def main() -> None:
    console.print("[bold]🤖 SWE-agent 交互式 REPL[/bold]")
    try:
        model = Prompt.ask("模型", default=DEFAULT_MODEL)
        repo = Prompt.ask("仓库路径", default=str(REPO_ROOT))
        apply_patch = Confirm.ask("跑完自动应用补丁到本地仓库？", default=True)

        while True:
            task = read_task()
            if task is None:
                break
            run_one(repo, task, model, apply_patch)

            repo = Prompt.ask("下一个任务的仓库路径（回车保持不变）", default=repo)
            if not Confirm.ask("继续下一个任务？", default=True):
                break
    except KeyboardInterrupt:
        console.print()

    console.print("再见 👋")


if __name__ == "__main__":
    main()
