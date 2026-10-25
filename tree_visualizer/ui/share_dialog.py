"""Share and Load Tree dialog for Tree_Visualizer."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Optional
from tree_visualizer.state.controller import Controller
from tree_visualizer.ui.fonts import get_ui_font
from tree_visualizer.ui.theme import ThemeManager


class ShareDialog(tk.Toplevel):
    """Modal dialog displaying active share code and allowing users to import one."""

    def __init__(
        self,
        parent: tk.Tk,
        controller: Controller,
        theme_manager: ThemeManager,
    ) -> None:
        super().__init__(parent)
        self.controller: Controller = controller
        self.theme_manager: ThemeManager = theme_manager
        self.parent: tk.Tk = parent

        self.title("Share / Load Tree")
        self.geometry("460x320")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        t = self.theme_manager.current
        self.configure(bg=t["bg_panel"])

        self._build_ui()
        self._center_window()

    def _center_window(self) -> None:
        self.update_idletasks()
        pw = self.parent.winfo_width()
        ph = self.parent.winfo_height()
        px = self.parent.winfo_rootx()
        py = self.parent.winfo_rooty()

        w = self.winfo_width()
        h = self.winfo_height()
        x = px + max(0, (pw - w) // 2)
        y = py + max(0, (ph - h) // 2)
        self.geometry(f"+{x}+{y}")

    def _build_ui(self) -> None:
        t = self.theme_manager.current

        # Header Title
        lbl_title = tk.Label(
            self,
            text="🔗 Share & Load Tree",
            bg=t["bg_panel"],
            fg=t["text_main"],
            font=get_ui_font(12, bold=True),
        )
        lbl_title.pack(anchor="w", padx=16, pady=(16, 12))

        # 1. Export Code Section
        sec_export = ttk.LabelFrame(self, text="Current Tree Share Code", padding=10)
        sec_export.pack(fill=tk.X, padx=16, pady=(0, 10))

        code = self.controller.get_share_code() if not self.controller.is_current_empty else ""
        row_exp = ttk.Frame(sec_export)
        row_exp.pack(fill=tk.X)

        self.entry_export = ttk.Entry(row_exp)
        self.entry_export.insert(0, code if code else "(Canvas is empty; nothing to share)")
        self.entry_export.configure(state="readonly")
        self.entry_export.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        btn_copy = ttk.Button(
            row_exp,
            text="Copy",
            style="Primary.TButton",
            command=self._handle_copy_code,
            state="normal" if code else "disabled",
        )
        btn_copy.pack(side=tk.RIGHT)

        # 2. Import Code Section
        sec_import = ttk.LabelFrame(self, text="Load Tree from Share Code", padding=10)
        sec_import.pack(fill=tk.X, padx=16, pady=(0, 8))

        row_imp = ttk.Frame(sec_import)
        row_imp.pack(fill=tk.X, pady=(0, 4))

        self.entry_import = ttk.Entry(row_imp)
        self.entry_import.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        self.entry_import.focus_set()

        btn_load = ttk.Button(
            row_imp,
            text="Load Tree",
            style="TButton",
            command=self._handle_load_code,
        )
        btn_load.pack(side=tk.RIGHT)

        self.lbl_error = tk.Label(
            sec_import,
            text="",
            bg=t["bg_panel"],
            fg="#ef4444",
            font=get_ui_font(8),
            anchor="w",
        )
        self.lbl_error.pack(fill=tk.X)

        # Footer Buttons
        row_close = ttk.Frame(self)
        row_close.pack(fill=tk.X, padx=16, pady=(8, 12))

        btn_close = ttk.Button(
            row_close,
            text="Close",
            style="TButton",
            command=self.destroy,
        )
        btn_close.pack(side=tk.RIGHT)

    def _handle_copy_code(self) -> None:
        code = self.controller.get_share_code()
        if code:
            self.clipboard_clear()
            self.clipboard_append(code)
            self.controller.set_status("Share code copied to clipboard!", severity="info")

    def _handle_load_code(self) -> None:
        raw_code = self.entry_import.get().strip()
        if not raw_code:
            self.lbl_error.configure(text="Please paste or enter a share code.")
            return

        success = self.controller.load_share_code(raw_code)
        if success:
            self.destroy()
        else:
            self.lbl_error.configure(text="Invalid, corrupted, or unsupported share code.")
