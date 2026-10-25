"""VisuAlgo-styled status message card and pseudocode animation overlay panels.

- StatusBox: Yellow informational card displaying active step messages and comparisons.
- PseudocodePanel: Pink card displaying numbered algorithm lines with active step highlighting.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional
from tree_visualizer.ui.fonts import get_code_font, get_ui_font
from tree_visualizer.ui.theme import ThemeManager


class StatusBox(tk.Frame):
    """VisuAlgo-style yellow status card displaying execution status."""

    def __init__(self, master: tk.Widget, theme_manager: ThemeManager, **kwargs) -> None:
        super().__init__(master, bd=1, relief="solid", padx=10, pady=8, **kwargs)
        self.theme_manager: ThemeManager = theme_manager

        self.label = tk.Label(
            self,
            text="Ready. Select an operation from the sidebar.",
            wraplength=380,
            justify=tk.LEFT,
            font=get_ui_font(10),
        )
        self.label.pack(fill=tk.BOTH, expand=True)

        self.update_theme(self.theme_manager.current)
        self.theme_manager.register_listener(self.update_theme)

    def set_message(self, message: str, severity: str = "info") -> None:
        """Update displayed status message and adjust colors if needed."""
        self.label.configure(text=message)
        # Subtle styling tweaks for warnings/errors if desired
        t = self.theme_manager.current
        if severity == "error":
            self.configure(bg="#fee2e2", highlightbackground="#f87171")
            self.label.configure(bg="#fee2e2", fg="#991b1b")
        elif severity == "warning":
            self.configure(bg=t["status_bg"], highlightbackground=t["status_border"])
            self.label.configure(bg=t["status_bg"], fg=t["status_text"])
        else:
            self.update_theme(t)

    def update_theme(self, theme: Dict[str, str]) -> None:
        """Apply theme colors for status card."""
        self.configure(
            bg=theme["status_bg"],
            highlightbackground=theme["status_border"],
            highlightcolor=theme["status_border"],
        )
        self.label.configure(
            bg=theme["status_bg"],
            fg=theme["status_text"],
        )


class PseudocodePanel(tk.Frame):
    """VisuAlgo-style pink pseudocode overlay panel with active line highlighting."""

    def __init__(self, master: tk.Widget, theme_manager: ThemeManager, **kwargs) -> None:
        super().__init__(master, bd=1, relief="solid", padx=8, pady=6, **kwargs)
        self.theme_manager: ThemeManager = theme_manager
        self.lines: List[str] = []
        self.active_line_idx: Optional[int] = None
        self.line_widgets: List[tk.Label] = []

        # Header title
        self.header_label = tk.Label(
            self,
            text="Pseudocode",
            font=get_ui_font(9, bold=True),
            anchor="w",
        )
        self.header_label.pack(fill=tk.X, pady=(0, 4))

        self.lines_frame = tk.Frame(self)
        self.lines_frame.pack(fill=tk.BOTH, expand=True)

        self.update_theme(self.theme_manager.current)
        self.theme_manager.register_listener(self.update_theme)

    def set_pseudocode(self, lines: List[str], active_idx: Optional[int] = None) -> None:
        """Populate pseudocode lines and set active highlight index."""
        self.lines = list(lines)
        self.active_line_idx = active_idx

        # Clear existing line labels
        for w in self.line_widgets:
            w.destroy()
        self.line_widgets.clear()

        t = self.theme_manager.current
        for i, text in enumerate(self.lines):
            is_active = (i == self.active_line_idx)
            bg = t["pseudo_act_bg"] if is_active else t["pseudo_bg"]
            fg = t["pseudo_text"]

            lbl = tk.Label(
                self.lines_frame,
                text=f"{i:2d}  {text}",
                font=get_code_font(9, bold=is_active),
                bg=bg,
                fg=fg,
                anchor="w",
                padx=4,
                pady=1,
            )
            lbl.pack(fill=tk.X)
            self.line_widgets.append(lbl)

    def highlight_line(self, line_idx: Optional[int]) -> None:
        """Highlight specified 0-based pseudocode line without rebuilding widgets."""
        self.active_line_idx = line_idx
        t = self.theme_manager.current

        for i, lbl in enumerate(self.line_widgets):
            is_active = (i == self.active_line_idx)
            lbl.configure(
                bg=t["pseudo_act_bg"] if is_active else t["pseudo_bg"],
                font=get_code_font(9, bold=is_active),
            )

    def update_theme(self, theme: Dict[str, str]) -> None:
        """Apply theme colors for pseudocode card and line labels."""
        self.configure(
            bg=theme["pseudo_bg"],
            highlightbackground=theme["pseudo_border"],
            highlightcolor=theme["pseudo_border"],
        )
        self.header_label.configure(
            bg=theme["pseudo_bg"],
            fg=theme["pseudo_text"],
        )
        self.lines_frame.configure(bg=theme["pseudo_bg"])

        for i, lbl in enumerate(self.line_widgets):
            is_active = (i == self.active_line_idx)
            lbl.configure(
                bg=theme["pseudo_act_bg"] if is_active else theme["pseudo_bg"],
                fg=theme["pseudo_text"],
            )
