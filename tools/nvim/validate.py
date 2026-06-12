from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path


THEME_PATTERN = re.compile(
    r'\A'
    r'(?:--[^\n]*\n|[ \t]*\n)*'
    r'return "'
    r'(base2tone_([a-z0-9]+(?:-[a-z0-9]+)*)_dark)'
    r'"\n?'
    r'\Z'
)


def find_plugin() -> Path:
    override = os.environ.get(
        "B2T_NVIM_PLUGIN_DIR"
    )

    candidates: list[Path] = []

    if override:
        candidates.append(
            Path(override).expanduser()
        )

    data_home = Path(
        os.environ.get(
            "XDG_DATA_HOME",
            Path.home() / ".local/share",
        )
    )

    candidates.extend(
        [
            data_home / "nvim/lazy/Base2Tone-nvim",
            Path.home()
            / ".local/share/nvim/lazy/Base2Tone-nvim",
            Path.home()
            / ".dotfiles/vendor/Base2Tone-nvim",
        ]
    )

    for candidate in candidates:
        if (
            candidate.is_dir()
            and (candidate / "lua").is_dir()
        ):
            return candidate

    checked = "\n".join(
        f"  {candidate}"
        for candidate in candidates
    )

    raise RuntimeError(
        "Base2Tone-nvim was not found. Checked:\n"
        + checked
    )


def validate(
    rendered_theme: Path,
    output_root: Path,
) -> None:
    del output_root

    if shutil.which("nvim") is None:
        raise RuntimeError(
            "Neovim is not installed or is not available in PATH"
        )

    text = rendered_theme.read_text(
        encoding="utf-8"
    )

    match = THEME_PATTERN.fullmatch(text)

    if match is None:
        raise RuntimeError(
            "generated selector must contain exactly one "
            'Base2Tone-nvim dark theme return value'
        )

    theme = match.group(1)
    scheme = match.group(2)

    if "{{" in text or "}}" in text:
        raise RuntimeError(
            "generated selector contains an unresolved placeholder"
        )

    if re.search(r"#[0-9a-fA-F]{6}", text):
        raise RuntimeError(
            "Neovim selector must not duplicate palette colors"
        )

    expected_theme = (
        f"base2tone_{scheme}_dark"
    )

    if theme != expected_theme:
        raise RuntimeError(
            f"unexpected theme name: {theme}"
        )

    plugin = find_plugin()

    environment = os.environ.copy()
    environment["B2T_NVIM_PLUGIN"] = str(plugin)
    environment["B2T_NVIM_THEME"] = theme

    script = r'''
vim.opt.runtimepath:prepend(vim.env.B2T_NVIM_PLUGIN)

local theme = vim.env.B2T_NVIM_THEME

vim.cmd.colorscheme(theme)

assert(
  vim.g.colors_name == theme,
  "colorscheme did not become active: "
    .. tostring(vim.g.colors_name)
)

local lualine_theme = require(
  "lualine.themes." .. theme
)

assert(
  type(lualine_theme) == "table",
  "matching Lualine theme did not return a table"
)
'''

    process = subprocess.run(
        [
            "nvim",
            "--headless",
            "-u",
            "NONE",
            "-i",
            "NONE",
            "-n",
            "-c",
            "lua " + script,
            "-c",
            "qa!",
        ],
        env=environment,
        capture_output=True,
        text=True,
    )

    if process.returncode != 0:
        message = (
            process.stderr.strip()
            or process.stdout.strip()
        )

        raise RuntimeError(
            message
            or f"Neovim validation returned {process.returncode}"
        )
