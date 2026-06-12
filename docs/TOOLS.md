# Tool Roadmap

## Module contract

Each supported tool owns:

    tools/<name>/
    ├── README.md
    ├── template.<native-extension>
    └── tool.toml

Optional hooks are added only when required by the tool.

The native template maps application fields directly to Base2Tone coordinates.

## Active output layout

Normal builds write only beneath:

    generated/current/

Examples:

    generated/current/eza/theme.yml
    generated/current/vivid/theme.yml
    generated/current/vivid/ls-colors.zsh
    generated/current/fzf/colors.zsh
    generated/current/yazi/theme.toml

## Phase 1: Core

### Shared compiler

Implement:

- scheme discovery;
- palette parsing;
- exact 32-coordinate validation;
- module discovery;
- placeholder substitution;
- atomic active-output replacement.

### Launcher

Implemented:

    list
    validate
    build
    test

## Phase 2: Filesystem tools

### eza

Module:

    tools/eza/

Output:

    generated/current/eza/theme.yml

Validation:

- isolate `EZA_CONFIG_DIR`;
- unset `LS_COLORS`;
- unset `EZA_COLORS`;
- run eza against the rendered theme.

### vivid

Module:

    tools/vivid/

Outputs:

    generated/current/vivid/theme.yml
    generated/current/vivid/ls-colors.zsh

Vivid requires post-processing because it compiles its YAML theme into an
LS_COLORS expression.

## Phase 3: Shell interaction

### fzf

Module:

    tools/fzf/

Output:

    generated/current/fzf/colors.zsh

The module appends only direct Base2Tone color mappings to
`FZF_DEFAULT_OPTS`. Each fzf field occupies its own template line so the
assigned coordinate remains visible and easy to edit.

Existing search commands, previews, layouts, and key bindings remain separate.

Validation sources the generated Zsh fragment and invokes fzf non-interactively
with `--filter`.

### fast-syntax-highlighting

Module:

    tools/fsh/

Output:

    generated/current/fsh/base2tone.ini

The module produces a complete native INI theme. Each syntax field occupies its
own line beside the original Base2Tone coordinate.

Validation checks the complete section and field structure along with supported
foreground, background, and text-style syntax without changing the user's
active shell theme.

### Yazi

Module:

    tools/yazi/

Maintained sources:

    tools/yazi/template.toml
    tools/yazi/icons.toml

Output:

    generated/current/yazi/theme.toml

The readable interface and filetype mappings are maintained in
`template.toml`. The complete shipped icon database is maintained separately in
`icons.toml` so hundreds of icon rules do not obscure the interface design.

The module manifest appends the icon fragment after the interface template.
Both parts compile into one native Yazi theme file.

Validation checks TOML syntax, required interface sections, filetype rules,
icon-group completeness, individual icon rules, color syntax, and isolated
loading through `yazi --debug`.

## Phase 4: Terminal workspace

Planned modules:

- tmux
- Zellij
- Starship

Starship should expose the original coordinate names:

    b2t_a0..b2t_a7
    b2t_b0..b2t_b7
    b2t_c0..b2t_c7
    b2t_d0..b2t_d7

The user's prompt layout remains separate.

## Phase 5: Git and documents

Planned modules:

- Lazygit
- Delta
- bat

Glow will be recreated from its current native schema.

bat should use maintained upstream Base2Tone tmTheme files where appropriate
instead of generating an incomplete syntax theme.

### Glow

Module:

    tools/glow/

Output:

    generated/current/glow/style.json

The module produces a complete native Glamour JSON style for Glow. Markdown
structure and Chroma syntax fields map directly to original Base2Tone
coordinates. Supporting text and punctuation remain restrained while headings,
links, keywords, names, and other important content receive stronger emphasis.

Validation checks JSON structure, maintained Chroma fields, color syntax,
unresolved placeholders, and an isolated Markdown render through Glow.

## Phase 6: Monitoring and information

Planned modules:

- Bottom
- Fastfetch

## Later lifecycle work

After generation and validation are stable:

- all-scheme temporary testing;
- dotfiles installation;
- current-theme reporting;
- reload hooks;
- dry-run support;
- uninstall or restore support.

## Separate projects

Zed and Warp remain outside this repository.

### Neovim

Module:

    tools/nvim/

Output:

    generated/current/nvim/current-theme.lua

The module selects the matching upstream `Base2Tone-nvim` dark colorscheme. It
does not generate Neovim highlight groups or Lualine colors.

Validation confirms that both the upstream colorscheme and its matching
Lualine theme exist and load successfully in headless Neovim.
