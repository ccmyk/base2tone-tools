from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCHEME_DIR = ROOT / "vendor/Base2Tone/db/schemes"
THEMES_DIR = Path.home() / ".config/bat/themes/Base2Tone-bat"

THEME_PATTERN = re.compile(
    r'^--theme="(base2tone-[a-z0-9-]+-dark)"$',
    re.MULTILINE,
)

PALETTE_PATTERN = re.compile(
    r"""base([ABCD])([0-7])\s*:\s*['"]?([0-9a-fA-F]{6})['"]?"""
)

GLOBAL_SETTINGS_PATTERN = re.compile(
    r"<key>settings</key>\s*<array>\s*<dict>\s*<key>settings</key>"
    r"\s*<dict>(.*?)</dict>",
    re.DOTALL,
)

SETTING_PATTERN = re.compile(
    r"<key>(\w+)</key>\s*<string>(#[0-9a-fA-F]{6})</string>"
)

EXPECTED_GLOBAL_COORDINATES = {
    "background": "A0",
    "foreground": "A3",
    "caret": "D2",
    "invisibles": "A1",
    "lineHighlight": "A1",
    "selection": "A1",
    "findHighlight": "D7",
    "findHighlightForeground": "A3",
    "selectionBorder": "A2",
    "bracketsForeground": "B7",
    "bracketContentsForeground": "A0",
    "guide": "A1",
    "activeGuide": "A3",
    "stackGuide": "A2",
}


def load_palette(scheme: str) -> dict[str, str]:
    path = SCHEME_DIR / f"base2tone-{scheme}.yml"

    if not path.is_file():
        raise RuntimeError(f"Base2Tone scheme not found: {path}")

    colors: dict[str, str] = {}

    for bank, index, value in PALETTE_PATTERN.findall(
        path.read_text(encoding="utf-8")
    ):
        colors[f"{bank}{index}"] = f"#{value.lower()}"

    return colors


def validate_theme_palette(theme: str) -> None:
    match = re.fullmatch(
        r"base2tone-([a-z0-9-]+)-dark",
        theme,
    )

    if match is None:
        raise RuntimeError(f"unexpected Bat theme name: {theme}")

    scheme = match.group(1)
    palette = load_palette(scheme)
    theme_path = THEMES_DIR / f"{theme}.tmTheme"

    if not theme_path.is_file():
        raise RuntimeError(
            f"upstream Bat theme file is unavailable: {theme_path}"
        )

    text = theme_path.read_text(encoding="utf-8")
    global_match = GLOBAL_SETTINGS_PATTERN.search(text)

    if global_match is None:
        raise RuntimeError(
            f"upstream Bat theme is missing global settings: {theme_path}"
        )

    globals_ = dict(
        SETTING_PATTERN.findall(global_match.group(1))
    )

    mismatches: list[str] = []

    for setting, coordinate in EXPECTED_GLOBAL_COORDINATES.items():
        expected = palette[coordinate]
        actual = globals_.get(setting)

        if actual is None:
            mismatches.append(
                f"{setting}: missing in upstream theme"
            )
            continue

        if actual.lower() != expected:
            mismatches.append(
                f"{setting}: {actual} expected {expected} "
                f"({coordinate})"
            )

    if mismatches:
        raise RuntimeError(
            "upstream Bat theme palette drift:\n"
            + "\n".join(f"  {line}" for line in mismatches)
        )


def validate(
    rendered_theme: Path,
    output_root: Path,
) -> None:
    del output_root

    if shutil.which("bat") is None:
        raise RuntimeError(
            "bat is not installed or is not available in PATH"
        )

    text = rendered_theme.read_text(encoding="utf-8")
    matches = THEME_PATTERN.findall(text)

    if len(matches) != 1:
        raise RuntimeError(
            "generated Bat config must select exactly one "
            "Base2Tone theme"
        )

    theme = matches[0]

    environment = os.environ.copy()

    for name in (
        "BAT_THEME",
        "BAT_THEME_DARK",
        "BAT_THEME_LIGHT",
        "BAT_CONFIG_PATH",
    ):
        environment.pop(name, None)

    list_process = subprocess.run(
        [
            "bat",
            "--list-themes",
        ],
        env=environment,
        capture_output=True,
        text=True,
    )

    if list_process.returncode != 0:
        message = (
            list_process.stderr.strip()
            or list_process.stdout.strip()
        )

        raise RuntimeError(
            message
            or "bat could not list installed syntax themes"
        )

    available = {
        line.strip()
        for line in list_process.stdout.splitlines()
        if line.strip()
    }

    if theme not in available:
        raise RuntimeError(
            f"upstream Bat theme is unavailable: {theme}"
        )

    validate_theme_palette(theme)

    with tempfile.TemporaryDirectory(
        prefix="base2tone-tools-bat-"
    ) as temporary_directory:
        sample = Path(temporary_directory) / "sample.zsh"

        sample.write_text(
            '# Base2Tone Bat validation\n'
            'typeset -U path\n'
            'if [[ -d "$HOME/.config" ]]; then\n'
            '  print -r -- "$HOME/.config"\n'
            'fi\n',
            encoding="utf-8",
        )

        environment["BAT_CONFIG_PATH"] = str(rendered_theme)

        process = subprocess.run(
            [
                "bat",
                "--paging=never",
                "--color=always",
                "--style=plain",
                str(sample),
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
                or f"bat validation returned {process.returncode}"
            )

        if "\x1b[" not in process.stdout:
            raise RuntimeError(
                "bat validation produced no ANSI color output"
            )
