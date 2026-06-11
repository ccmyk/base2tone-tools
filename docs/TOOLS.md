# Tool Roadmap

## Principles

Each supported tool receives its own readable template.

A tool template must:

- use the application's current native schema;
- expose direct `{{A0}}..{{D7}}` assignments;
- document important mapping decisions;
- avoid a shared semantic alias layer;
- generate a complete valid file for the intended integration method.

## Phase 4: Filesystem tools

### eza

Output:

    generated/<scheme>/eza.yml

Purpose:

- native eza file listing colors;
- file kinds;
- permissions;
- sizes;
- users and groups;
- links;
- Git state;
- repository state;
- file categories;
- dates and metadata.

Why it comes first:

eza exposes many visible fields and provides a strong test of direct coordinate
mapping and visual hierarchy.

### vivid

Output:

    generated/<scheme>/vivid.yml

Purpose:

- define file types and filesystem states;
- compile a scheme-specific `LS_COLORS` value;
- support compatible tools beyond one listing command.

Why it follows eza:

eza and vivid overlap in the filesystem concepts they represent, but use
different schemas and integration models. Comparing both will reveal which
mappings should remain similar and which need tool-specific treatment.

### LS_COLORS integration

Possible output:

    generated/<scheme>/ls-colors.zsh

Purpose:

- export the result produced by vivid;
- provide a reusable shell fragment;
- allow compatible tools to inherit the generated file classification colors.

## Phase 5: Shell interaction tools

### fzf

Output:

    generated/<scheme>/fzf.zsh

Fields include:

- background;
- foreground;
- selected row;
- highlights;
- borders;
- prompt;
- pointer;
- marker;
- spinner;
- headers and labels.

### fast-syntax-highlighting

Output:

    generated/<scheme>/fast-syntax-highlighting.ini

Fields include:

- commands;
- aliases;
- functions;
- paths;
- options;
- quoted strings;
- variables;
- redirections;
- operators;
- brackets;
- comments;
- invalid tokens.

### Yazi

Output:

    generated/<scheme>/yazi-theme.toml

Fields include:

- manager interface;
- selected and hovered rows;
- status modes;
- progress states;
- permissions;
- inputs and selection dialogs;
- tasks;
- help;
- file classification.

## Phase 6: Terminal workspace tools

### tmux

Output:

    generated/<scheme>/tmux.conf

Initial strategy:

Generate palette variables first rather than replacing a user's complete tmux
layout.

Possible values:

    @b2t_a0
    @b2t_a1
    ...
    @b2t_d7

A later optional template may generate a complete reference status-line theme.

### Zellij

Output:

    generated/<scheme>/zellij-theme.kdl

Zellij requires a limited terminal-style theme containing:

- foreground;
- background;
- black;
- red;
- green;
- yellow;
- blue;
- magenta;
- cyan;
- white;
- orange.

Because this schema compresses 32 coordinates into a smaller named set, the
template must clearly document every coordinate choice.

### Starship

Output:

    generated/<scheme>/starship-palette.toml

Initial strategy:

Generate only a named coordinate palette:

    b2t_a0..b2t_a7
    b2t_b0..b2t_b7
    b2t_c0..b2t_c7
    b2t_d0..b2t_d7

The user's prompt layout remains separate and may refer directly to those
coordinate names.

## Phase 7: Git and document tools

### Lazygit

Output:

    generated/<scheme>/lazygit-theme.yml

Integration may use a marked block or a standalone generated configuration,
depending on what Lazygit supports cleanly.

### Delta

Output:

    generated/<scheme>/delta.gitconfig

Fields include:

- line numbers;
- additions;
- deletions;
- emphasized additions and deletions;
- hunk headers;
- file names and decorations.

### Glow

Output:

    generated/<scheme>/glow-style.json

Glow will be rebuilt from its documented style schema rather than copied from
the old project.

Special care is required because code block backgrounds and syntax coloring may
not render like full-width editor panels.

### bat

Initial strategy:

Prefer upstream Base2Tone bat themes when available.

The project may copy or select an upstream `.tmTheme` rather than generate an
incomplete syntax theme.

## Phase 8: Monitoring and information tools

### Bottom

Output:

    generated/<scheme>/bottom.toml

Fields include:

- borders;
- selected borders;
- text and headers;
- CPU series;
- memory series;
- network series;
- battery states;
- tables and widgets.

### Fastfetch

Output:

    generated/<scheme>/fastfetch.jsonc

Fields include:

- keys;
- output;
- title;
- separators;
- logo colors.

The compiler may provide derived RGB channel values for applications that
require terminal escape sequences rather than direct hexadecimal strings.

## Later candidates

Potential future templates include:

- ripgrep color fragments;
- fd integrations through `LS_COLORS`;
- Git UI tools;
- shell completion menus;
- process monitors;
- terminal emulators without maintained upstream Base2Tone themes;
- documentation previews and palette comparison reports.

Zed and Warp are separate projects and are not part of this repository.
