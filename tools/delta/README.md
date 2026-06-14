# Delta

This module generates a Delta theme fragment for Git.

## Output

    generated/current/delta/theme.gitconfig

## Runtime integration

The generated file should be symlinked to:

    ~/.config/delta/theme.gitconfig

and included from `~/.gitconfig`:

    [include]
      path = ~/.config/delta/theme.gitconfig

The user's main Delta behavior, such as side-by-side mode and line numbers,
can remain in `~/.gitconfig`.
