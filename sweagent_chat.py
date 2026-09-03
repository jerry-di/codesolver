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

from sweagent import CONFIG_DIR, REPO_ROOT

console = Console()

DEFAULT_MODEL = "deepseek/deepseek-chat"
DEFAULT_CONFIG = CONFIG_DIR / "default.yaml"


def read_task() -> str:
    """Read a multi-line task. Finish with an empty line."""
    console.print("[bold cyan]输入任务描述：[/bold cyan]")
    console.print("[dim]（可多行粘贴；结束时空一行再回车）[/dim]")
    lines: list[str] = []
    while True:
        line = input()
        if line.strip() == "":
            if lines:
                break
            continue
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
    console.print(f"[dim]{' '.join(cmd)}[/dim]\n")
    subprocess.run(cmd)


def main() -> None:
    console.print("[bold]🤖 SWE-agent 交互式 REPL[/bold]")
    model = Prompt.ask("模型", default=DEFAULT_MODEL)
    repo = Prompt.ask("仓库路径", default=str(REPO_ROOT))
    apply_patch = Confirm.ask("跑完自动应用补丁到本地仓库？", default=True)

    while True:
        task = read_task()
        if not task:
            console.print("[yellow]任务为空，已跳过[/yellow]")
            continue
        run_one(repo, task, model, apply_patch)

        repo = Prompt.ask("下一个任务的仓库路径（回车保持不变）", default=repo)
        if not Confirm.ask("继续下一个任务？", default=True):
            break

    console.print("再见 👋")


if __name__ == "__main__":
    main()
