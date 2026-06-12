from __future__ import annotations

import configparser
import re
from pathlib import Path


EXPECTED_SECTIONS = {
    "base",
    "command-point",
    "paths",
    "brackets",
    "arguments",
    "in-string",
    "other",
    "math",
    "for-loop",
    "case",
}

EXPECTED_KEYS = {
    "base": {
        "default",
        "unknown-token",
        "commandseparator",
        "redirection",
        "here-string-tri",
        "here-string-text",
        "here-string-var",
        "exec-descriptor",
        "comment",
        "correct-subtle",
        "incorrect-subtle",
        "subtle-separator",
        "subtle-bg",
        "recursive-base",
    },
    "command-point": {
        "reserved-word",
        "subcommand",
        "alias",
        "suffix-alias",
        "global-alias",
        "builtin",
        "function",
        "command",
        "precommand",
        "hashed-command",
        "single-sq-bracket",
        "double-sq-bracket",
        "double-paren",
    },
    "paths": {
        "path",
        "pathseparator",
        "path-to-dir",
        "globbing",
        "globbing-ext",
    },
    "brackets": {
        "paired-bracket",
        "bracket-level-1",
        "bracket-level-2",
        "bracket-level-3",
    },
    "arguments": {
        "single-hyphen-option",
        "double-hyphen-option",
        "back-quoted-argument",
        "single-quoted-argument",
        "double-quoted-argument",
        "dollar-quoted-argument",
    },
    "in-string": {
        "back-dollar-quoted-argument",
        "back-or-dollar-double-quoted-argument",
    },
    "other": {
        "variable",
        "assign",
        "assign-array-bracket",
        "history-expansion",
    },
    "math": {
        "mathvar",
        "mathnum",
        "matherr",
    },
    "for-loop": {
        "forvar",
        "fornum",
        "foroper",
        "forsep",
    },
    "case": {
        "case-input",
        "case-parentheses",
        "case-condition",
    },
}

HEX_COLOR = re.compile(r"^#[0-9a-fA-F]{6}$")
NUMBER_COLOR = re.compile(r"^[0-9]+$")

NAMED_COLORS = {
    "black",
    "red",
    "green",
    "yellow",
    "blue",
    "magenta",
    "cyan",
    "white",
}

STYLES = {
    "none",
    "bold",
    "no-bold",
    "blink",
    "no-blink",
    "conceal",
    "no-conceal",
    "reverse",
    "no-reverse",
    "standout",
    "no-standout",
    "underline",
    "no-underline",
}


def valid_color(value: str) -> bool:
    return (
        bool(HEX_COLOR.fullmatch(value))
        or bool(NUMBER_COLOR.fullmatch(value))
        or value in NAMED_COLORS
    )


def valid_style_value(value: str) -> bool:
    parts = [part.strip() for part in value.split(",")]

    if not parts or any(not part for part in parts):
        return False

    for part in parts:
        if part in STYLES:
            continue

        if part.startswith("bg:"):
            if valid_color(part.removeprefix("bg:")):
                continue
            return False

        if valid_color(part):
            continue

        return False

    return True


def validate(
    rendered_theme: Path,
    output_root: Path,
) -> None:
    del output_root

    parser = configparser.ConfigParser(
        interpolation=None,
        strict=True,
        delimiters=("=",),
        comment_prefixes=(";",),
        empty_lines_in_values=False,
    )
    parser.optionxform = str

    try:
        with rendered_theme.open("r", encoding="utf-8") as file:
            parser.read_file(file)
    except configparser.Error as error:
        raise RuntimeError(
            f"invalid INI syntax: {error}"
        ) from error

    actual_sections = set(parser.sections())

    missing_sections = sorted(EXPECTED_SECTIONS - actual_sections)
    extra_sections = sorted(actual_sections - EXPECTED_SECTIONS)

    if missing_sections:
        raise RuntimeError(
            "missing sections: " + ", ".join(missing_sections)
        )

    if extra_sections:
        raise RuntimeError(
            "unexpected sections: " + ", ".join(extra_sections)
        )

    for section, expected_keys in EXPECTED_KEYS.items():
        actual_keys = set(parser[section])

        missing_keys = sorted(expected_keys - actual_keys)
        extra_keys = sorted(actual_keys - expected_keys)

        if missing_keys:
            raise RuntimeError(
                f"[{section}] missing keys: "
                + ", ".join(missing_keys)
            )

        if extra_keys:
            raise RuntimeError(
                f"[{section}] unexpected keys: "
                + ", ".join(extra_keys)
            )

        for key in sorted(expected_keys):
            value = parser[section][key].strip()

            if not valid_style_value(value):
                raise RuntimeError(
                    f"[{section}] {key} has invalid style value: "
                    f"{value!r}"
                )
