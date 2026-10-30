#!/usr/bin/env bash
set -Eeuo pipefail

REPO="RobbieUK1/Key-Reverser"
ROOT="${XDG_DATA_HOME:-$HOME/.local/share}/omarchy-quoteswap"
BIN="$HOME/.local/bin"
APPS="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
XKB="${XDG_CONFIG_HOME:-$HOME/.config}/xkb/symbols"
TEMP=""
cleanup() { [[ -z "$TEMP" ]] || rm -rf "$TEMP"; }
trap cleanup EXIT

if [[ "${EUID}" -eq 0 ]]; then
  printf 'Do not run this installer as root; it installs into your user account.\n' >&2
  exit 1
fi

if [[ -f "./quoteswap.py" && -f "./xkb/symbols/omarchy_quoteswap" ]]; then
  SOURCE="$(pwd)"
else
  for tool in curl tar; do
    command -v "$tool" >/dev/null || { printf '%s is required.\n' "$tool" >&2; exit 1; }
  done
  TEMP="$(mktemp -d)"
  printf 'Downloading Key Reverser from GitHub...\n'
  curl -fsSL "https://github.com/$REPO/archive/refs/heads/main.tar.gz" -o "$TEMP/source.tar.gz"
  tar -xzf "$TEMP/source.tar.gz" -C "$TEMP" --no-same-owner
  SOURCE="$TEMP/Key-Reverser-main"
fi

command -v python3 >/dev/null || { printf 'Python 3 is required.\n' >&2; exit 1; }
if ! python3 -c 'import tkinter' 2>/dev/null; then
  if command -v pacman >/dev/null && command -v sudo >/dev/null; then
    printf 'Installing the Tk GUI dependency (sudo may ask for your password)...\n'
    sudo pacman -S --needed tk
  else
    printf 'Install Python Tkinter (Omarchy: sudo pacman -S tk), then retry.\n' >&2
    exit 1
  fi
fi

mkdir -p "$ROOT" "$BIN" "$APPS" "$XKB"
if [[ -e "$XKB/omarchy_quoteswap" ]] && ! cmp -s "$SOURCE/xkb/symbols/omarchy_quoteswap" "$XKB/omarchy_quoteswap"; then
  printf 'A different layout already exists at %s. Nothing was overwritten.\n' "$XKB/omarchy_quoteswap" >&2
  exit 1
fi
install -m 644 "$SOURCE/xkb/symbols/omarchy_quoteswap" "$XKB/omarchy_quoteswap"
install -m 755 "$SOURCE/quoteswap.py" "$ROOT/quoteswap.py"
install -m 755 "$SOURCE/uninstall.sh" "$ROOT/uninstall.sh"

cat > "$BIN/omarchy-quoteswap" <<'SH'
#!/usr/bin/env bash
exec python3 "${XDG_DATA_HOME:-$HOME/.local/share}/omarchy-quoteswap/quoteswap.py" "$@"
SH
chmod 755 "$BIN/omarchy-quoteswap"

cat > "$APPS/omarchy-quoteswap.desktop" <<'DESKTOP'
[Desktop Entry]
Type=Application
Name=Key Reverser
Comment=Swap @ and quotation marks on the UK keyboard
Exec=omarchy-quoteswap
Icon=input-keyboard
Terminal=false
Categories=Settings;Utility;
Keywords=keyboard;quotes;at;keymap;Omarchy;
DESKTOP

python3 "$ROOT/quoteswap.py" enable
printf '\nKey Reverser installed! Find it in the app launcher.\n'
printf 'To open manually: ~/.local/bin/omarchy-quoteswap\n'
printf 'To uninstall: bash "%s/uninstall.sh"\n' "$ROOT"
