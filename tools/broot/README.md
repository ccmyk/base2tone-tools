# Broot

This module generates a Broot skin.

## Output

    generated/current/broot/base2tone.hjson

## Runtime integration

Symlink the generated skin to:

    ~/.config/broot/skins/base2tone.hjson

and import it from `~/.config/broot/conf.hjson`:

    imports: [
      "skins/base2tone.hjson"
    ]

The main Broot config owns verbs, flags, modal behavior, and shell integration.
