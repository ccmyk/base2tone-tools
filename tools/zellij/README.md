# Zellij

This module generates a native Zellij theme.

## Output

    generated/current/zellij/base2tone.kdl

## Runtime integration

Symlink the generated theme to:

    ~/.config/zellij/themes/base2tone.kdl

and set this in `~/.config/zellij/config.kdl`:

    theme "base2tone"

Your keybindings, layouts, plugins, and UI behavior remain in `config.kdl`.
