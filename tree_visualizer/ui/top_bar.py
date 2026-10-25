"""Application top navigation and utility action bar.

Renders:
- Brand title: [Tree Icon] Tree_Visualizer
- Navigation tab buttons: [Binary Tree | BST | Build from Traversal]
- Action buttons: [Undo | Clear | JSON | PNG | Share | Theme Toggle]
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict, Optional
from tree_visualizer.constants import APP_NAME
from tree_visualizer.ui.fonts import get_ui_font
from tree_visualizer.ui.icon import TreeIconCanvas
from tree_visualizer.ui.theme import ThemeManager


class TopBar(ttk.Frame):
    """Top application header bar with branding, tab selection, and utility buttons."""

    def __init__(
        self,
        master: tk.Widget,
        theme_manager: ThemeManager,
        on_tab_selected: Optional[Callable[[str], None]] = None,
        on_undo: Optional[Callable[[], None]] = None,
        on_clear: Optional[Callable[[], None]] = None,
        on_export_json: Optional[Callable[[], None]] = None,
        on_export_png: Optional[Callable[[], None]] = None,
        on_share: Optional[Callable[[], None]] = None,
        on_theme_toggle: Optional[Callable[[], None]] = None,
        **kwargs,
    ) -> None:
        super().__init__(master, style="TopBar.TFrame", padding=(12, 8), **kwargs)
        self.theme_manager: ThemeManager = theme_manager
        self.on_tab_selected: Optional[Callable[[str], None]] = on_tab_selected
        self.on_undo: Optional[Callable[[], None]] = on_undo
        self.on_clear: Optional[Callable[[], None]] = on_clear
        self.on_export_json: Optional[Callable[[], None]] = on_export_json
        self.on_export_png: Optional[Callable[[], None]] = on_export_png
        self.on_share: Optional[Callable[[], None]] = on_share
        self.on_theme_toggle: Optional[Callable[[], None]] = on_theme_toggle

        self.active_tab: str = "bst"
        self.tab_buttons: Dict[str, ttk.Button] = {}

        self._build_ui()
        self.theme_manager.register_listener(self.on_theme_updated)

    def _build_ui(self) -> None:
        t = self.theme_manager.current

        # -------------------------------------------------------------
        # Left Section: Icon & Title
        # -------------------------------------------------------------
        brand_frame = ttk.Frame(self, style="TopBar.TFrame")
        brand_frame.pack(side=tk.LEFT, padx=(0, 20))

        self.brand_icon = TreeIconCanvas(brand_frame, size=24, bg_color=t["bg_panel"])
        self.brand_icon.pack(side=tk.LEFT, padx=(0, 8))

        self.title_label = ttk.Label(
            brand_frame,
            text=APP_NAME,
            style="Title.TLabel",
            font=get_ui_font(12, bold=True),
        )
        self.title_label.pack(side=tk.LEFT)

        # -------------------------------------------------------------
        # Center Section: Navigation Tabs
        # -------------------------------------------------------------
        tabs_frame = ttk.Frame(self, style="TopBar.TFrame")
        tabs_frame.pack(side=tk.LEFT, expand=False)

        tabs_info = [
            ("bst", "BST"),
            ("binary", "Binary Tree"),
            ("build", "Build from Traversal"),
        ]
        for tab_id, label in tabs_info:
            style = "ActiveTab.TButton" if tab_id == self.active_tab else "Tab.TButton"
            btn = ttk.Button(
                tabs_frame,
                text=label,
                style=style,
                command=lambda tid=tab_id: self.select_tab(tid),
            )
            btn.pack(side=tk.LEFT, padx=3)
            self.tab_buttons[tab_id] = btn

        # -------------------------------------------------------------
        # Right Section: Actions & Theme Toggle
        # -------------------------------------------------------------
        actions_frame = ttk.Frame(self, style="TopBar.TFrame")
        actions_frame.pack(side=tk.RIGHT)

        self.btn_undo = ttk.Button(
            actions_frame,
            text="↩ Undo",
            style="Action.TButton",
            command=self._handle_undo,
            state="disabled",
        )
        self.btn_undo.pack(side=tk.LEFT, padx=3)

        self.btn_clear = ttk.Button(
            actions_frame,
            text="✕ Clear",
            style="Action.TButton",
            command=self._handle_clear,
        )
        self.btn_clear.pack(side=tk.LEFT, padx=3)

        self.btn_json = ttk.Button(
            actions_frame,
            text="💾 JSON",
            style="Action.TButton",
            command=self._handle_export_json,
        )
        self.btn_json.pack(side=tk.LEFT, padx=3)

        self.btn_png = ttk.Button(
            actions_frame,
            text="📷 PNG",
            style="Action.TButton",
            command=self._handle_export_png,
        )
        self.btn_png.pack(side=tk.LEFT, padx=3)

        self.btn_share = ttk.Button(
            actions_frame,
            text="🔗 Share",
            style="Action.TButton",
            command=self._handle_share,
        )
        self.btn_share.pack(side=tk.LEFT, padx=3)

        theme_text = "☼ Light" if self.theme_manager.is_dark() else "☾ Dark"
        self.btn_theme = ttk.Button(
            actions_frame,
            text=theme_text,
            style="Action.TButton",
            command=self._handle_theme_toggle,
        )
        self.btn_theme.pack(side=tk.LEFT, padx=(6, 0))

    def select_tab(self, tab_id: str) -> None:
        """Select active tab and update tab button styles."""
        if tab_id not in self.tab_buttons:
            return
        self.active_tab = tab_id
        for tid, btn in self.tab_buttons.items():
            btn.configure(style="ActiveTab.TButton" if tid == tab_id else "Tab.TButton")

        if self.on_tab_selected is not None:
            self.on_tab_selected(tab_id)

    def set_undo_enabled(self, enabled: bool) -> None:
        """Update Undo button enabled state."""
        self.btn_undo.configure(state="normal" if enabled else "disabled")

    def _handle_undo(self) -> None:
        if self.on_undo:
            self.on_undo()

    def _handle_clear(self) -> None:
        if self.on_clear:
            self.on_clear()

    def _handle_export_json(self) -> None:
        if self.on_export_json:
            self.on_export_json()

    def _handle_export_png(self) -> None:
        if self.on_export_png:
            self.on_export_png()

    def _handle_share(self) -> None:
        if self.on_share:
            self.on_share()

    def _handle_theme_toggle(self) -> None:
        if self.on_theme_toggle:
            self.on_theme_toggle()

    def on_theme_updated(self, theme: Dict[str, str]) -> None:
        """Update top bar components on theme change."""
        self.brand_icon.update_theme(theme["bg_panel"])
        theme_text = "☼ Light" if self.theme_manager.is_dark() else "☾ Dark"
        self.btn_theme.configure(text=theme_text)
        # Refresh tab styles
        for tid, btn in self.tab_buttons.items():
            btn.configure(style="ActiveTab.TButton" if tid == self.active_tab else "Tab.TButton")
