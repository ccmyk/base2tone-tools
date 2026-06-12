from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


def validate(
    rendered_theme: Path,
    output_root: Path,
) -> None:
    del output_root

    if shutil.which("zsh") is None:
        raise RuntimeError(
            "zsh is not installed or is not available in PATH"
        )

    if shutil.which("fzf") is None:
        raise RuntimeError(
            "fzf is not installed or is not available in PATH"
        )

    environment = os.environ.copy()

    # Validate only the generated fragment. Existing user options could conceal
    # a malformed fragment or introduce unrelated failures.
    environment["FZF_DEFAULT_OPTS"] = ""

    syntax_process = subprocess.run(
        [
            "zsh",
            "-n",
            str(rendered_theme),
        ],
        env=environment,
        capture_output=True,
        text=True,
    )

    if syntax_process.returncode != 0:
        message = syntax_process.stderr.strip()

        raise RuntimeError(
            message or "generated fzf fragment has invalid Zsh syntax"
        )

    test_script = r'''
source "$1"

[[ -n "$FZF_DEFAULT_OPTS" ]] || {
  print -u2 "FZF_DEFAULT_OPTS is empty"
  false
}

print -l alpha beta gamma |
  fzf \
    --filter=beta \
    --no-sort \
    >/dev/null
'''

    process = subprocess.run(
        [
            "zsh",
            "-f",
            "-c",
            test_script,
            "_",
            str(rendered_theme),
        ],
        env=environment,
        capture_output=True,
        text=True,
    )

    if process.returncode != 0:
        message = process.stderr.strip()

        raise RuntimeError(
            message
            or f"fzf validation returned status {process.returncode}"
        )
