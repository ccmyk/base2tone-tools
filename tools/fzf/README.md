# fzf

This module owns the Base2Tone color integration for fzf.

## Files

- `template.zsh` appends generated color options to `FZF_DEFAULT_OPTS`.
- `tool.toml` declares the template, output, and validator.
- `validate.py` checks Zsh syntax, sources the fragment in isolation, and runs
  fzf non-interactively.

## Manifest

    name = "fzf"
    template = "template.zsh"
    output = "fzf/colors.zsh"
    validator = "validate.py"

## Output

    generated/current/fzf/colors.zsh

## Mapping format

Each fzf field occupies its own template line:

    '--color=fg:#{{A6}}'
    '--color=bg:#{{A0}}'
    '--color=prompt:#{{B5}}'

This keeps the fzf field and its original Base2Tone coordinate directly
adjacent and makes individual assignments easy to change.

## Scope

The module controls only colors.

It does not define:

- input commands;
- preview commands;
- layout;
- height;
- key bindings;
- shell widgets;
- history behavior.

Those remain in the user's ordinary fzf configuration.

## Validation

Validation clears inherited `FZF_DEFAULT_OPTS`, sources the generated fragment
with Zsh, and runs fzf using `--filter` so no interactive terminal is required.
