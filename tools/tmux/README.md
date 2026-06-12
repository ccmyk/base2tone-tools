# tmux

This module owns the complete Base2Tone visual layer for the customized tmux
configuration.

## Files

- `template.conf` contains all color-bearing native options and status content.
- `tool.toml` declares the template, output, and validator.
- `validate.py` loads the generated theme in an isolated tmux server.

## Output

    generated/current/tmux/theme.conf

## Coordinate model

The tracked template uses direct Base2Tone coordinates:

    #{{A0}}
    #{{B4}}
    #{{D6}}

Generated output contains literal hexadecimal colors.

The module does not create a second runtime palette using tmux variables such
as `@b2t_a0`.

## Module ownership

The generated theme owns:

- status content and colors;
- window-list formats and styles;
- separators;
- pane borders;
- messages;
- copy-mode selection;
- menus;
- popups;
- pane-number overlays;
- clock mode.

The user's `.tmux.conf` owns:

- terminal and clipboard behavior;
- indexing and history;
- key bindings;
- mouse behavior;
- copy commands;
- popup commands;
- status position and dimensions;
- automatic window naming;
- plugins.

## Installation

The user's configuration sources:

    ~/.config/tmux/theme.conf

That path may link to:

    generated/current/tmux/theme.conf

## Validation

Validation rejects unresolved placeholders, runtime `@b2t_*` variables, and
output without literal colors.

It loads the generated file using a separate tmux socket and verifies the
expected options without touching the user's active tmux server.
