# Generated Base2Tone colors for fzf.
#
# This fragment appends only color options to FZF_DEFAULT_OPTS. Search
# commands, previews, layouts, key bindings, and other behavior remain in the
# user's regular fzf configuration.
#
# Each fzf field is kept on its own line so its Base2Tone coordinate remains
# immediately visible and easy to change.
#
# Every assignment uses an original Base2Tone coordinate directly. The
# comments describe only its local purpose inside fzf.

typeset -a b2t_fzf_color_options=(
  # Main list
  '--color=fg:#{{A6}}'
  '--color=bg:#{{A0}}'

  # Selected row
  '--color=fg+:#{{C6}}'
  '--color=bg+:#{{A1}}'

  # Match highlighting
  '--color=hl:#{{D4}}'
  '--color=hl+:#{{D6}}'

  # Controls
  '--color=prompt:#{{B5}}'
  '--color=pointer:#{{D5}}'
  '--color=marker:#{{D4}}'
  '--color=spinner:#{{B5}}'

  # Supporting text
  '--color=info:#{{A5}}'
  '--color=header:#{{A5}}'
  '--color=query:#{{C6}}'

  # Structure
  '--color=gutter:#{{A0}}'
  '--color=border:#{{A3}}'
  '--color=label:#{{B4}}'
  '--color=separator:#{{A3}}'
  '--color=scrollbar:#{{A4}}'

  # Preview
  '--color=preview-border:#{{A3}}'
  '--color=preview-label:#{{B4}}'

  # Candidate list
  '--color=list-border:#{{A3}}'
  '--color=list-label:#{{B4}}'

  # Input area
  '--color=input-border:#{{A3}}'
  '--color=input-label:#{{B5}}'

  # Header area
  '--color=header-border:#{{A3}}'
  '--color=header-label:#{{B4}}'
)

export FZF_DEFAULT_OPTS="${FZF_DEFAULT_OPTS:+${FZF_DEFAULT_OPTS} }${(j: :)b2t_fzf_color_options}"

unset b2t_fzf_color_options
