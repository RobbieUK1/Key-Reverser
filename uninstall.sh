#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="${XDG_DATA_HOME:-$HOME/.local/share}/omarchy-quoteswap"
BIN="$HOME/.local/bin/omarchy-quoteswap"
DESKTOP="${XDG_DATA_HOME:-$HOME/.local/share}/applications/omarchy-quoteswap.desktop"
XKB="${XDG_CONFIG_HOME:-$HOME/.config}/xkb/symbols/omarchy_quoteswap"

if [[ -f "$ROOT/quoteswap.py" ]]; then
  python3 "$ROOT/quoteswap.py" remove-config
fi
rm -f "$BIN" "$DESKTOP" "$XKB"
rm -rf "$ROOT"
printf 'Key Reverser uninstalled; other Hyprland input settings left in place.\n'
printf 'A one-time backup, if made, is preserved in ~/.config/omarchy-quoteswap/.\n'
