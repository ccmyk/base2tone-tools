# Neovim

This module selects the matching colorscheme from the upstream
`atelierbram/Base2Tone-nvim` project.

## Files

- `template.lua` generates the active upstream colorscheme name.
- `tool.toml` declares the output and validator.
- `validate.py` checks the generated selector and upstream integration.

## Output

    generated/current/nvim/current-theme.lua

For Motel:

    return "base2tone_motel_dark"

## Scope

This module does not generate or duplicate Neovim colors.

`Base2Tone-nvim` owns:

- editor highlight groups;
- Treesitter highlighting;
- plugin highlights;
- matching Lualine themes.

Base2Tone Tools owns only selection of the active upstream variant.

## Metadata placeholder

The template uses:

    {{SCHEME}}

This placeholder inserts the normalized Base2Tone scheme name. It is metadata,
not a color or semantic palette alias.

## Validation

Validation confirms:

- the generated file contains one valid dark-theme selector;
- no hexadecimal palette values are duplicated;
- the corresponding upstream colorscheme exists;
- the corresponding upstream Lualine theme exists;
- Neovim can load both in an isolated headless process.
