# Key Reverser for Omarchy

A tiny black-and-mint utility for the UK keyboard. It changes **only two shifted characters**:

| Shortcut | Standard UK | Key Reverser ON |
|---|---|---|
| `Shift + 2` | `"` | `@` |
| `Shift + '` | `@` | `"` |

Everything else stays UK, including `£`, `#`, and AltGr symbols.

## One-line installer

```bash
curl -fsSL https://raw.githubusercontent.com/RobbieUK1/Key-Reverser/main/install.sh | bash
```

Run the command on **Omarchy with Hyprland's Lua configuration**. It installs a user-level XKB layout, a menu launcher, and a graphical window with **Enable swap** and **Use normal UK keys** buttons. The installer activates the swap straight away. If Python's Tk GUI is unavailable, the installer offers to install Arch's `tk` package via pacman; this is the only step that can require sudo.

You can inspect `install.sh` before running it.

## Launch and commands

Open **Key Reverser** from the app launcher, or run:

```bash
~/.local/bin/omarchy-quoteswap
~/.local/bin/omarchy-quoteswap enable
~/.local/bin/omarchy-quoteswap disable
~/.local/bin/omarchy-quoteswap status
```

Settings apply to the current Hyprland session and persist after reboot.

## Uninstall

```bash
bash "${XDG_DATA_HOME:-$HOME/.local/share}/omarchy-quoteswap/uninstall.sh"
```

Uninstall removes the app, its custom XKB file, and its own clearly marked override in `~/.config/hypr/input.lua`. Other input settings are left alone. A one-time backup is retained under `~/.config/omarchy-quoteswap/`.

**Previous manual changes:** If you already added a separate `gb_swap` keyboard override by hand, it remains your own configuration and may resume when the app is uninstalled. Remove that earlier override if you no longer want it.

## Technical details

- The XKB file `~/.config/xkb/symbols/omarchy_quoteswap` inherits the standard `gb(basic)` symbols and changes only the shifted level of `<AE02>` and `<AC11>`.
- Configuration is stored in a reversible, marked `hl.config` Lua block in `~/.config/hypr/input.lua` and applied with `hyprctl reload`. The old `hyprctl keyword` command is not used.
- Does not modify system files, the Linux console, the boot screen, or the login manager.
- Designed for Omarchy's modern Lua configuration provider, not legacy Hyprland `.conf` configurations.

## Tests

```bash
python3 -m unittest discover -s tests -v
bash -n install.sh uninstall.sh
```

MIT licensed.
