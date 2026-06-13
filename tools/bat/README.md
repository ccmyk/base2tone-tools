# Bat

This module selects the active upstream Base2Tone-bat syntax theme.

## Files

- `template.conf` generates the active Bat configuration.
- `tool.toml` declares the generated output and validator.
- `validate.py` verifies that the selected upstream theme exists and renders
  syntax-highlighted output.

## Manifest

    name = "bat"
    template = "template.conf"
    output = "bat/config"
    validator = "validate.py"

## Output

    generated/current/bat/config

## Theme ownership

Syntax scope mappings are maintained by the upstream Base2Tone-bat project.

The generated configuration selects:

    base2tone-<scheme>-dark

This avoids duplicating or approximating the upstream syntax-color mappings.

## Installation

Apply creates a dotfiles symlink to the generated selector:

    b2t-theme apply <scheme> --module bat

The generated configuration is installed at:

    ~/.config/bat/config

The upstream themes are installed beneath:

    ~/.config/bat/themes/Base2Tone-bat/

Bat compiles those themes into its binary cache with:

    bat cache --build
