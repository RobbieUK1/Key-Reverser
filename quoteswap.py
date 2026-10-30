#!/usr/bin/env python3
"""Omarchy Key Reverser: user-level UK @ / " toggle for Lua Hyprland."""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TITLE = "Key Reverser"
BEGIN = "-- BEGIN OMARCHY_QUOTESWAP (managed by Key Reverser)"
END = "-- END OMARCHY_QUOTESWAP"
LAYOUT = "omarchy_quoteswap"


def paths() -> tuple[Path, Path, Path]:
    config = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    return (config / "hypr" / "input.lua",
            config / "xkb" / "symbols" / LAYOUT,
            config / "omarchy-quoteswap" / "input.lua.before-first-change")


def section(enabled: bool) -> str:
    layout = LAYOUT if enabled else "gb"
    return (f"{BEGIN}\n"
            "hl.config({\n"
            f'  input = {{ kb_layout = "{layout}", kb_variant = "" }},\n'
            "})\n"
            f"{END}\n")


def remove_section(contents: str) -> str:
    if contents.count(BEGIN) != contents.count(END) or contents.count(BEGIN) > 1:
        raise ValueError("Config markers incomplete or duplicated. input.lua left unchanged.")
    if BEGIN not in contents:
        return contents
    pattern = r"\n^" + re.escape(BEGIN) + r"\n.*?^" + re.escape(END) + r"\n?"
    return re.sub(pattern, "", contents, count=1, flags=re.MULTILINE | re.DOTALL)


def status() -> str:
    config, _, _ = paths()
    if not config.is_file():
        return "not configured"
    data = config.read_text(encoding="utf-8")
    if BEGIN not in data:
        return "not configured"
    if section(True).strip() in data:
        return "enabled"
    if section(False).strip() in data:
        return "disabled"
    return "modified externally"


def atomic_write(filename: Path, contents: str) -> None:
    filename.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=".key-reverser-", dir=filename.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(contents)
        if filename.exists():
            os.chmod(temp, filename.stat().st_mode & 0o777)
        os.replace(temp, filename)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def update(enabled: bool | None) -> None:
    config, xkb, backup = paths()
    if enabled is True and not xkb.is_file():
        raise RuntimeError(f"Missing installed layout: {xkb}")
    previous = config.read_text(encoding="utf-8") if config.exists() else ""
    clean = remove_section(previous)
    updated = clean if enabled is None else clean + "\n" + section(enabled)
    if updated == previous:
        return
    backup.parent.mkdir(parents=True, exist_ok=True)
    if config.exists() and not backup.exists():
        shutil.copy2(config, backup)
    atomic_write(config, updated)


def reload_session() -> str:
    if not shutil.which("hyprctl") or not os.environ.get("HYPRLAND_INSTANCE_SIGNATURE"):
        return "Saved. The change takes effect next time Hyprland starts."
    process = subprocess.run(["hyprctl", "reload"], text=True, capture_output=True)
    if process.returncode or "error" in process.stdout.lower():
        raise RuntimeError((process.stderr or process.stdout).strip() or "Hyprland reload failed")
    return "Applied to your current Hyprland session."


def change(enabled: bool | None) -> str:
    update(enabled)
    return reload_session()


def gui() -> int:
    try:
        import tkinter as tk
        from tkinter import messagebox
    except ImportError:
        print("Tkinter is required. On Omarchy: sudo pacman -S tk", file=sys.stderr)
        return 2

    bg, panel, mint, white, dim = "#000000", "#151d1a", "#8fffd3", "#f5fffa", "#adc4b8"
    root = tk.Tk()
    root.title(TITLE)
    root.geometry("560x420")
    root.minsize(500, 390)
    root.configure(bg=bg)
    try:
        root.tk.call("tk", "scaling", 1.5)
    except tk.TclError:
        pass
    tk.Label(root, text='@  ↔  "', bg=bg, fg=mint,
             font=("Sans", 32, "bold")).pack(pady=(25, 9))
    tk.Label(root, text="Key Reverser", bg=bg, fg=white,
             font=("Sans", 20, "bold")).pack()
    tk.Label(root, text="Switch only two keys on your UK keyboard",
             bg=bg, fg=dim, font=("Sans", 11)).pack(pady=(6, 20))
    state_text = tk.StringVar()
    status_label = tk.Label(root, textvariable=state_text, bg=panel, fg=white,
                            font=("Sans", 12, "bold"), pady=14)
    status_label.pack(fill="x", padx=30)
    info_text = tk.StringVar()

    def refresh(note: str = "") -> None:
        state_text.set("Status: " + status().capitalize())
        info_text.set(note or 'Shift + 2 → @     Shift + apostrophe → "')

    def apply(value: bool) -> None:
        try:
            message = change(value)
            refresh(message)
        except Exception as error:
            messagebox.showerror(TITLE, str(error), parent=root)
            refresh()

    actions = tk.Frame(root, bg=bg)
    actions.pack(fill="x", padx=30, pady=(23, 10))
    for label, func, button_bg, button_fg in [
        ("Enable swap", lambda: apply(True), mint, bg),
        ("Normal UK keys", lambda: apply(False), panel, white),
    ]:
        tk.Button(actions, text=label, command=func,
                  bg=button_bg, fg=button_fg, activebackground=mint,
                  activeforeground=bg, relief="flat",
                  font=("Sans", 11, "bold"), padx=8, pady=13,
                  cursor="hand2", highlightthickness=0
                  ).pack(side="left", expand=True, fill="x", padx=5)
    tk.Label(root, textvariable=info_text, bg=bg, fg=dim, wraplength=500,
             font=("Sans", 10)).pack(pady=10)
    refresh()
    root.mainloop()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Swap the UK keyboard @ and quote keys")
    parser.add_argument("action", nargs="?", choices=("enable", "disable", "status", "remove-config"),
                        help="Omit to open the graphical utility")
    args = parser.parse_args()
    try:
        if not args.action:
            return gui()
        if args.action == "status":
            print(status())
            return 0
        print(change(None if args.action == "remove-config" else args.action == "enable"))
        return 0
    except Exception as error:
        print(f"Key Reverser: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
