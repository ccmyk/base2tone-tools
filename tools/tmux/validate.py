from __future__ import annotations

import os
import re
import shutil
import subprocess
import uuid
from pathlib import Path


HEX_COLOR = re.compile(
    r"#[0-9a-fA-F]{6}"
)

UNRESOLVED_PLACEHOLDER = re.compile(
    r"\{\{\s*[A-Za-z_][A-Za-z0-9_]*\s*\}\}"
)

REQUIRED_OPTIONS = {
    "clock-mode-colour",
    "display-panes-active-colour",
    "display-panes-colour",
    "menu-border-style",
    "menu-selected-style",
    "menu-style",
    "message-command-style",
    "message-style",
    "mode-style",
    "pane-active-border-style",
    "pane-border-style",
    "popup-border-style",
    "popup-style",
    "status-left",
    "status-right",
    "status-style",
    "window-status-activity-style",
    "window-status-bell-style",
    "window-status-current-format",
    "window-status-current-style",
    "window-status-format",
    "window-status-last-style",
    "window-status-separator",
    "window-status-style",
}


def run_tmux(
    socket: str,
    environment: dict[str, str],
    *arguments: str,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "tmux",
            "-L",
            socket,
            *arguments,
        ],
        env=environment,
        capture_output=True,
        text=True,
    )


def validate(
    rendered_theme: Path,
    output_root: Path,
) -> None:
    del output_root

    if shutil.which("tmux") is None:
        raise RuntimeError(
            "tmux is not installed or is not available in PATH"
        )

    text = rendered_theme.read_text(
        encoding="utf-8"
    )

    unresolved = sorted(
        set(
            UNRESOLVED_PLACEHOLDER.findall(text)
        )
    )

    if unresolved:
        raise RuntimeError(
            "generated tmux theme contains unresolved placeholders: "
            + ", ".join(unresolved)
        )

    if "@b2t_" in text:
        raise RuntimeError(
            "generated tmux theme contains runtime palette variables"
        )

    colors = HEX_COLOR.findall(text)

    if len(colors) < 20:
        raise RuntimeError(
            "generated tmux theme does not contain enough literal colors"
        )

    environment = os.environ.copy()
    environment.pop("TMUX", None)

    socket = (
        "base2tone-tools-"
        + uuid.uuid4().hex
    )

    try:
        process = run_tmux(
            socket,
            environment,
            "-f",
            str(rendered_theme),
            "new-session",
            "-d",
            "-s",
            "base2tone-validation",
        )

        if process.returncode != 0:
            message = (
                process.stderr.strip()
                or process.stdout.strip()
            )

            raise RuntimeError(
                message
                or "tmux rejected the generated theme"
            )

        global_process = run_tmux(
            socket,
            environment,
            "show-options",
            "-g",
        )

        window_process = run_tmux(
            socket,
            environment,
            "show-window-options",
            "-g",
        )

        if global_process.returncode != 0:
            raise RuntimeError(
                global_process.stderr.strip()
                or "could not inspect tmux global options"
            )

        if window_process.returncode != 0:
            raise RuntimeError(
                window_process.stderr.strip()
                or "could not inspect tmux window options"
            )

        loaded = (
            global_process.stdout
            + "\n"
            + window_process.stdout
        )

        missing = sorted(
            option
            for option in REQUIRED_OPTIONS
            if option not in loaded
        )

        if missing:
            raise RuntimeError(
                "generated tmux theme did not set: "
                + ", ".join(missing)
            )

    finally:
        run_tmux(
            socket,
            environment,
            "kill-server",
        )
