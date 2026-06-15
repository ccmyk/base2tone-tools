# Base2Tone Tools

Base2Tone Tools is a compiler for the upstream Base2Tone palette system. It converts Base2Tone schemes into native configuration files for terminal tools, shells, prompts, file managers, and terminal workspace utilities.

It keeps the original Base2Tone coordinate system visible:

```text
A0 A1 A2 A3 A4 A5 A6 A7
B0 B1 B2 B3 B4 B5 B6 B7
C0 C1 C2 C3 C4 C5 C6 C7
D0 D1 D2 D3 D4 D5 D6 D7
```

Tool templates use those coordinates directly. The project does not replace them with a global semantic layer such as `background`, `accent`, `success`, `warning`, or `danger`.

## Supported tools

Current modules generate native config or theme fragments for:

- bat
- broot
- delta
- eza
- fastfetch
- fast-syntax-highlighting
- fzf
- glow
- Neovim
- Starship
- tmux
- vivid / LS_COLORS
- Yazi
- Zellij

Zed and Warp are separate projects, not modules in this repository.

## Quick start

List schemes:

```sh
./bin/b2t-theme list
```

Validate a scheme:

```sh
./bin/b2t-theme validate drawbridge
```

Build generated output:

```sh
./bin/b2t-theme build drawbridge
```

Apply a scheme to configured install targets:

```sh
./bin/b2t-theme apply drawbridge
```

Test every scheme:

```sh
./bin/b2t-theme test
```

## Generated output

Normal builds maintain one active output tree:

```text
generated/current/
├── scheme
├── bat/theme.conf
├── broot/base2tone.hjson
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

`generated/current/scheme` records the active scheme.

## Project layout

```text
base2tone-tools/
├── bin/
│   └── b2t-theme
├── docs/
├── generated/
│   └── current/
├── lib/
│   └── compiler.py
├── tools/
│   └── <tool>/
│       ├── README.md
│       ├── template.<native-extension>
│       ├── tool.toml
│       └── validate.py
└── vendor/
    └── Base2Tone/
```

## Source of truth

Palette data comes from upstream Base2Tone scheme files:

```text
vendor/Base2Tone/db/schemes/base2tone-<scheme>.yml
```

Each scheme must contain exactly 32 coordinates:

```text
baseA0..baseA7
baseB0..baseB7
baseC0..baseC7
baseD0..baseD7
```

## How it works

The build pipeline is:

```text
Base2Tone scheme
        ↓
bin/b2t-theme
        ↓
lib/compiler.py
        ↓
tools/*/tool.toml
        ↓
tool-owned native templates
        ↓
generated/current/
```

Each tool module owns its native mapping. The compiler loads the selected palette, substitutes placeholders such as `{{B4}}`, runs validators or build hooks, and writes the active generated output.

## Tool modules

A typical module contains:

```text
tools/eza/
├── README.md
├── template.yml
├── tool.toml
└── validate.py
```

A template keeps the coordinate assignment visible:

```yaml
directory:
  foreground: "#{{B4}}"
```

The compiler replaces `{{B4}}` with the selected scheme's hex value. The native template owns surrounding syntax such as `#`, quotes, shell escaping, or tool-specific formatting.

## More documentation

See:

```text
PROJECT.md
```

for the full architecture, palette rules, module contract, validation model, installation model, per-tool notes, and roadmap.
