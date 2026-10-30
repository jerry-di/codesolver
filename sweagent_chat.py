#!/usr/bin/env python3
"""Interactive REPL wrapper for SWE-agent.

Lets you "chat" with SWE-agent by typing tasks directly instead of
passing files and a long list of CLI flags.

Usage:
    python sweagent_chat.py

The `sweagent` import is deferred to `main()` so the pure helpers
(`build_command`, `is_exit`) can be unit-tested without the full
SWE-agent dependency tree.
"""

from __future__ import annotations

import subprocess
import sys
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.prompt import Confirm, Prompt

console = Console()

DEFAULT_MODEL = "deepseek/deepseek-chat"
EXIT_KEYWORDS = ("exit", "quit", "q")
LOG_FILE = Path("sweagent_chat.log")


def is_exit(line: str) -> bool:
    """Return True if the trimmed line is an exit keyword (case-insensitive)."""
    return line.strip().lower() in EXIT_KEYWORDS


def import_sweagent() -> tuple[Path, Path]:
    """Import SWE-agent lazily and return ``(CONFIG_DIR, REPO_ROOT)``.

    Deferred so the module can be imported for tests without installing the
    full SWE-agent dependency tree.
    """
    try:
        from sweagent import CONFIG_DIR, REPO_ROOT
    except ImportError as e:
        console.print(f"[bold red]❌ 无法导入 sweagent：{e}[/bold red]")
        console.print("[dim]请先在项目根目录安装依赖：pip install -e .[/dim]")
        raise SystemExit(1) from e
    return CONFIG_DIR, REPO_ROOT


def build_command(config: Path, model: str, repo: str, task: str, apply_patch: bool) -> list[str]:
    """Build the ``sweagent run`` command line for a single task."""
    cmd = [
        sys.executable,
        "-m",
        "sweagent",
        "run",
        "--config",
        str(config),
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
    return cmd


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
        if is_exit(line):
            return None
        lines.append(line)
    return "\n".join(lines).strip()


def log_run(repo: str, model: str, task: str, apply_patch: bool, returncode: int) -> None:
    """Append a one-line summary of a run to ``LOG_FILE`` (best-effort)."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "ok" if returncode == 0 else f"failed({returncode})"
    first_line = task.splitlines()[0] if task else ""
    entry = f"{timestamp} | {status} | model={model} | repo={repo} | patch={apply_patch} | {first_line}\n"
    try:
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(entry)
    except OSError:
        pass  # logging must never break the REPL


def run_one(config: Path, repo: str, task: str, model: str, apply_patch: bool) -> int:
    """Run SWE-agent once for the given repo + task. Returns the exit code."""
    cmd = build_command(config, model, repo, task, apply_patch)

    console.print("\n[bold green]>>> 正在运行[/bold green]")
    console.print(f"[dim]仓库: {repo} | 模型: {model} | 应用补丁: {apply_patch}[/dim]")
    console.print(f"[dim]{' '.join(cmd)}[/dim]\n")

    result = subprocess.run(cmd)
    log_run(repo, model, task, apply_patch, result.returncode)

    if result.returncode == 0:
        console.print("[bold green]✅ 运行完成[/bold green]")
    else:
        console.print(f"[bold red]❌ 运行失败（退出码 {result.returncode}）[/bold red]")
    return result.returncode


def main() -> None:
    console.print("[bold]🤖 SWE-agent 交互式 REPL[/bold]")
    config_dir, repo_root = import_sweagent()
    default_config = config_dir / "default.yaml"

    try:
        model = Prompt.ask("模型", default=DEFAULT_MODEL)
        repo = Prompt.ask("仓库路径", default=str(repo_root))
        apply_patch = Confirm.ask("跑完自动应用补丁到本地仓库？", default=True)

        while True:
            task = read_task()
            if task is None:
                break
            run_one(default_config, repo, task, model, apply_patch)

            repo = Prompt.ask("下一个任务的仓库路径（回车保持不变）", default=repo)
            if not Confirm.ask("继续下一个任务？", default=True):
                break
    except KeyboardInterrupt:
        console.print()

    console.print("再见 👋")


if __name__ == "__main__":
    main()
