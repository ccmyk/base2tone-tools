# Base2Tone Tools Project Guide

Base2Tone Tools is a compiler for the upstream Base2Tone palette system. It reads Base2Tone scheme files, validates the original 32-coordinate palette, renders native tool templates, runs tool-specific validators and build hooks, and writes one active generated output tree.

This document consolidates the project architecture, palette rules, module contract, generated-output model, installation model, supported tools, and roadmap.

## Core concept

Base2Tone Tools is not a theme collection. It is a theme compiler.

The project transforms this:

```text
vendor/Base2Tone/db/schemes/base2tone-<scheme>.yml
```

into native configuration for terminal tools:

```text
generated/current/
├── bat/theme.conf
├── delta/theme.gitconfig
├── eza/theme.yml
├── fastfetch/theme.jsonc
├── fsh/base2tone.ini
├── fzf/colors.zsh
├── glow/style.json
├── nvim/current-theme.lua
├── starship/palette.toml
├── tmux/theme.conf
├── vivid/theme.yml
├── vivid/ls-colors.zsh
├── yazi/theme.toml
└── zellij/base2tone.kdl
```

The generated output is tool-native. Applications should consume those files directly, with minimal shell glue only where a tool requires it.

## Base2Tone palette model

Each upstream Base2Tone scheme contains four banks of eight coordinates:

```text
A0 A1 A2 A3 A4 A5 A6 A7
B0 B1 B2 B3 B4 B5 B6 B7
C0 C1 C2 C3 C4 C5 C6 C7
D0 D1 D2 D3 D4 D5 D6 D7
```

In upstream YAML, these appear as:

```text
baseA0..baseA7
baseB0..baseB7
baseC0..baseC7
baseD0..baseD7
```

The coordinate is the stable identity. The project does not convert coordinates into a global semantic dictionary such as:

```text
background
foreground
accent
success
warning
danger
```

A coordinate can have a local purpose inside one tool template, but that local purpose does not become a universal meaning across the project.

## General palette tendencies

These are tendencies, not rules.

### A bank

The A bank usually provides structural dark values, raised surfaces, borders, separators, quiet metadata, and dim readable foregrounds.

`A0` is usually the darkest anchor.

### B bank

The B bank is one authored chromatic family. It is often useful for paths, navigation, secondary emphasis, syntax fields, and classifications.

Its hue and lightness vary by scheme.

### C bank

The C bank usually provides the most neutral readable light ramp and often reaches the brightest text values.

It is often useful for primary text or prominent foregrounds when high contrast is required.

### D bank

The D bank is the second authored chromatic family. It is often useful for active states, emphasis, highlights, and alternate classifications.

It must not be assumed to mean success, warning, or accent globally.

## Mapping rule

Templates should choose coordinates according to:

1. the native visual structure of the target tool;
2. foreground/background contrast;
3. hierarchy and visual priority inside that tool;
4. consistency with related modules;
5. behavior across all Base2Tone schemes;
6. upstream Base2Tone precedents where appropriate.

A template should not be tuned only for one favorite scheme.

## Architecture

The project has three layers:

```text
bin/b2t-theme
      ↓
lib/compiler.py
      ↓
tools/<tool>/
```

### CLI launcher

The CLI lives at:

```text
bin/b2t-theme
```

It handles command-line parsing and delegates work to the compiler.

The launcher should not contain tool-specific color mappings or generated config construction.

### Shared compiler

The compiler lives at:

```text
lib/compiler.py
```

It owns shared behavior:

- scheme name normalization;
- scheme discovery;
- palette loading;
- exact 32-coordinate validation;
- module discovery;
- manifest loading;
- placeholder substitution;
- temporary build output;
- atomic generated-output replacement;
- post-processing hooks;
- validation hooks;
- install target handling.

The compiler treats coordinates as identifiers, not semantic roles.

### Tool modules

Each supported tool owns a module directory:

```text
tools/<tool>/
```

A normal module contains:

```text
README.md
template.<native-extension>
tool.toml
validate.py
```

Some modules also contain:

```text
build.py
icons.toml
other appended fragments
```

The template owns color mapping. The manifest owns operational metadata.

## Template model

Templates use direct coordinate placeholders:

```text
{{A0}}
{{B4}}
{{C6}}
{{D5}}
```

The compiler substitutes each placeholder with the selected scheme's bare six-digit hexadecimal value.

The template controls surrounding syntax.

For a format that requires a leading `#`:

```yaml
directory:
  foreground: "#{{B4}}"
```

For a format that requires bare hex:

```yaml
A0: "{{A0}}"
```

For a shell fragment:

```zsh
'--color=fg:#{{A6}}'
```

## Metadata placeholders

Some modules need non-color metadata.

`{{SCHEME}}` expands to the normalized active scheme name.

This is useful for modules that select maintained upstream named themes instead of regenerating equivalent color definitions.

Examples:

- Neovim selects the matching upstream `Base2Tone-nvim` colorscheme.
- Delta can select a matching syntax theme.
- Bat selects the matching upstream `Base2Tone-bat` theme.

`{{SCHEME}}` is not a color and not a second palette system.

## Module manifest contract

Each module declares itself with `tool.toml`.

A typical manifest:

```toml
name = "eza"
template = "template.yml"
output = "eza/theme.yml"
validator = "validate.py"

[install]
target = "eza/theme.yml"
mode = "symlink"
```

Manifest fields describe how to build, validate, and install the module.

Color decisions belong in templates, not manifests.

## Build lifecycle

A normal build produces one active generated tree:

```text
generated/current/
```

The compiler should complete rendering and validation before replacing the active output.

The active scheme is recorded in:

```text
generated/current/scheme
```

The project does not keep a permanent matrix of every generated scheme and every tool during normal operation.

## Testing lifecycle

All-scheme testing renders every upstream scheme into temporary output, runs module validators, reports pass or failure, and removes temporary files.

This catches mappings that only work in one scheme but fail in another because of contrast, hue, syntax, or tool-format issues.

## Installation and dotfiles boundary

Base2Tone Tools is the source of truth for generation.

Dotfiles are consumers of the generated output.

The intended boundary is:

```text
~/development/base2tone-tools
    compiler, modules, templates, validators, generated active output

~/.dotfiles
    installed active files consumed by user applications
```

An apply operation should:

1. render into temporary storage;
2. validate every enabled module;
3. stop without touching installed files if anything fails;
4. install the active output into configured targets;
5. use symlinks or managed files as declared by each module;
6. record the active scheme.

Shell integration should remain minimal and tool-specific.

## Supported modules

### bat

Generates a selector for the matching upstream Base2Tone-bat theme.

Output:

```text
generated/current/bat/theme.conf
```

Bat syntax scope mappings remain owned by upstream Base2Tone-bat themes. This project should not duplicate those syntax definitions locally.

### broot

Generates a native Broot skin.

Output:

```text
generated/current/broot/base2tone.hjson
```

### delta

Generates a Git Delta config fragment.

Output:

```text
generated/current/delta/theme.gitconfig
```

Delta styling must use valid Delta style syntax. Syntax-theme selection should point to an installed matching theme.

### eza

Generates a native eza theme.

Output:

```text
generated/current/eza/theme.yml
```

eza should use its native theme file and should not erase `LS_COLORS` or `EZA_COLORS` in shell aliases unless intentionally disabling color input.

User-facing columns such as headers, users, groups, sizes, and dates should be restrained enough that filenames remain visually primary.

### fastfetch

Generates Fastfetch display color configuration.

Output:

```text
generated/current/fastfetch/theme.jsonc
```

The generated theme can be paired with a separate user-owned Fastfetch module list.

### fast-syntax-highlighting

Generates a native fast-syntax-highlighting INI theme.

Output:

```text
generated/current/fsh/base2tone.ini
```

Each shell syntax field maps directly to Base2Tone coordinates.

### fzf

Generates a Zsh fragment that appends color options to `FZF_DEFAULT_OPTS`.

Output:

```text
generated/current/fzf/colors.zsh
```

This module should only own colors. Search commands, previews, layouts, keybindings, and behavior belong in the user's normal fzf shell config.

### glow

Generates a Glamour JSON style for Glow Markdown rendering.

Output:

```text
generated/current/glow/style.json
```

The template maps Markdown structure and Chroma syntax fields directly to Base2Tone coordinates.

### Neovim

Generates a selector file for the matching upstream Base2Tone-nvim theme.

Output:

```text
generated/current/nvim/current-theme.lua
```

This module should not duplicate Neovim highlight groups or Lualine colors that are already owned by upstream Base2Tone-nvim.

### Starship

Generates a Starship palette fragment.

Output:

```text
generated/current/starship/palette.toml
```

Prompt layout remains user-owned. The generated output should expose the Base2Tone coordinate values in a way Starship can use.

### tmux

Generates native tmux color and status configuration.

Output:

```text
generated/current/tmux/theme.conf
```

The module owns color-bearing tmux options and status styling.

### vivid

Generates both a vivid YAML theme and a compiled `LS_COLORS` shell fragment.

Outputs:

```text
generated/current/vivid/theme.yml
generated/current/vivid/ls-colors.zsh
```

This module requires post-processing because vivid compiles YAML into an `LS_COLORS` expression.

### Yazi

Generates a complete Yazi theme.

Output:

```text
generated/current/yazi/theme.toml
```

The readable interface template and large Nerd Font icon database are maintained as separate source fragments, then rendered into one native output file.

### Zellij

Generates a Zellij KDL theme.

Output:

```text
generated/current/zellij/base2tone.kdl
```

Zellij requires RGB integer values, so this module may use a build hook to transform rendered hex colors.

## Separate projects

Zed and Warp are intentionally outside this repository.

They may use the same Base2Tone principles, but they should not be treated as modules inside `base2tone-tools`.

## Documentation model

The root README should be short and practical:

- what the project is;
- what it supports;
- quick commands;
- generated output example;
- where to read more.

This file is the consolidated technical project document. It replaces overlapping architecture, palette, and tool-roadmap notes.

## Roadmap

Useful future work:

- dry-run apply mode;
- current theme reporting;
- status command;
- install target verification;
- optional reload hooks;
- stale generated file cleanup;
- clearer module enable/disable controls;
- improved all-scheme contrast validation;
- reduced shell startup glue;
- stronger validation for installed theme availability.
