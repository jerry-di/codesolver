"""Tests for the interactive REPL wrapper (pure helpers only).

Run with:
    python -m pytest tests/test_sweagent_chat.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from sweagent_chat import EXIT_KEYWORDS, build_command, is_exit


def test_is_exit_matches_keywords_case_insensitive():
    for keyword in EXIT_KEYWORDS:
        assert is_exit(keyword)
        assert is_exit(f"  {keyword}  ")
        assert is_exit(keyword.upper())
    assert not is_exit("")
    assert not is_exit("fix the login bug")


def test_build_command_without_patch():
    cmd = build_command(
        config=Path("config/default.yaml"),
        model="deepseek/deepseek-chat",
        repo="/tmp/repo",
        task="fix the bug",
        apply_patch=False,
    )
    assert cmd[0] == sys.executable
    assert "--config" in cmd
    assert cmd[cmd.index("--config") + 1] == "config/default.yaml"
    assert "--agent.model.name" in cmd
    assert "--env.repo.path" in cmd
    assert "--problem_statement.text" in cmd
    assert "--actions.apply_patch_locally=True" not in cmd


def test_build_command_with_patch_appends_flag():
    cmd = build_command(
        config=Path("config/default.yaml"),
        model="deepseek/deepseek-chat",
        repo="/tmp/repo",
        task="fix the bug",
        apply_patch=True,
    )
    assert "--actions.apply_patch_locally=True" in cmd
