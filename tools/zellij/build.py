from __future__ import annotations

import re
from pathlib import Path


HEX = re.compile(r'"#([0-9a-fA-F]{6})"')


def repl(match: re.Match[str]) -> str:
    value = match.group(1)
    r = int(value[0:2], 16)
    g = int(value[2:4], 16)
    b = int(value[4:6], 16)
    return f"{r} {g} {b}"


def build(rendered_theme: Path, output_root: Path) -> tuple[Path, ...]:
    del output_root

    text = rendered_theme.read_text(encoding="utf-8")
    rendered_theme.write_text(HEX.sub(repl, text), encoding="utf-8")

    return ()
