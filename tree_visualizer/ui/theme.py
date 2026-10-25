"""Theme and ttk visual styling system.

Provides Dark and Light themes exactly matching docs/SPEC.md:
- Based on the ttk 'clam' theme engine.
- Configures hover, pressed, active, and disabled states across all widgets.
- Supports dynamic live theme switching without application restarts.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Dict, List
from tree_visualizer.ui.fonts import get_ui_font

DARK_THEME: Dict[str, str] = {
    "name": "dark",
    "bg_app": "#0f172a",          # Slate 900
    "bg_panel": "#1e293b",        # Slate 800
    "bg_panel_alt": "#334155",    # Slate 700
    "border_color": "#334155",    # Slate 700
    "text_main": "#f8fafc",       # Slate 50
    "text_muted": "#94a3b8",      # Slate 400
    "accent": "#38bdf8",          # Sky 400
    "accent_hover": "#0284c7",    # Sky 600
    "accent_text": "#0f172a",     # Dark text on bright accent
    "danger": "#ef4444",          # Red 500
    "danger_hover": "#dc2626",    # Red 600
    "canvas_bg": "#0b0f19",       # Deep Obsidian
    "node_default": "#3b82f6",    # Blue 500
    "node_visited": "#10b981",    # Emerald 500
    "node_highlight": "#ea580c",  # Orange 600
    "node_stroke": "#1e293b",     # Slate 800
    "node_text": "#ffffff",       # Pure White
    "edge_default": "#64748b",    # Slate 500
    "edge_highlight": "#ea580c",  # Orange 600
    "status_bg": "#fef08a",       # Yellow 200
    "status_text": "#854d0e",     # Yellow 800
    "status_border": "#facc15",   # Yellow 400
    "pseudo_bg": "#fce7f3",       # Pink 100
    "pseudo_text": "#831843",     # Pink 900
    "pseudo_border": "#f472b6",   # Pink 400
    "pseudo_act_bg": "#fbcfe8",   # Pink 200
    "pseudo_act_bd": "#db2777",   # Pink 600
}

LIGHT_THEME: Dict[str, str] = {
    "name": "light",
    "bg_app": "#f8fafc",          # Slate 50
    "bg_panel": "#ffffff",        # Pure White
    "bg_panel_alt": "#f1f5f9",    # Slate 100
    "border_color": "#e2e8f0",    # Slate 200
    "text_main": "#0f172a",       # Slate 900
    "text_muted": "#64748b",      # Slate 500
    "accent": "#0284c7",          # Sky 600
    "accent_hover": "#0369a1",    # Sky 700
    "accent_text": "#ffffff",     # White text on dark sky
    "danger": "#dc2626",          # Red 600
    "danger_hover": "#b91c1c",    # Red 700
    "canvas_bg": "#ffffff",       # Pure White
    "node_default": "#2563eb",    # Blue 600
    "node_visited": "#059669",    # Emerald 600
    "node_highlight": "#ea580c",  # Orange 600
    "node_stroke": "#ffffff",     # White outline
    "node_text": "#ffffff",       # Pure White
    "edge_default": "#94a3b8",    # Slate 400
    "edge_highlight": "#ea580c",  # Orange 600
    "status_bg": "#fef9c3",       # Yellow 100
    "status_text": "#713f12",     # Yellow 900
    "status_border": "#fde047",   # Yellow 300
    "pseudo_bg": "#fdf2f8",       # Pink 50
    "pseudo_text": "#701a75",     # Fuchsia 900
    "pseudo_border": "#f9a8d4",   # Pink 300
    "pseudo_act_bg": "#fce7f3",   # Pink 100
    "pseudo_act_bd": "#ec4899",   # Pink 500
}


class ThemeManager:
    """Manages active color palette and ttk style configuration."""

    def __init__(self, root: tk.Tk, initial_theme: str = "dark") -> None:
        self.root: tk.Tk = root
        self.theme_name: str = initial_theme if initial_theme in ("dark", "light") else "dark"
        self.style: ttk.Style = ttk.Style(root)
        self.listeners: List[Callable[[Dict[str, str]], None]] = []

        # Ensure base clam theme is active for consistent cross-platform styling
        available_themes = self.style.theme_names()
        if "clam" in available_themes:
            self.style.theme_use("clam")

        self.apply_theme(self.theme_name)

    @property
    def current(self) -> Dict[str, str]:
        """Return color dictionary for active theme."""
        return DARK_THEME if self.theme_name == "dark" else LIGHT_THEME

    def is_dark(self) -> bool:
        """Return True if active theme is dark."""
        return self.theme_name == "dark"

    def register_listener(self, callback: Callable[[Dict[str, str]], None]) -> None:
        """Register a callback to be invoked when the theme switches."""
        self.listeners.append(callback)

    def toggle_theme(self) -> str:
        """Toggle between dark and light themes."""
        new_theme = "light" if self.theme_name == "dark" else "dark"
        self.apply_theme(new_theme)
        return new_theme

    def apply_theme(self, theme_name: str) -> None:
        """Apply full ttk styles for specified theme ('dark' or 'light')."""
        self.theme_name = theme_name if theme_name in ("dark", "light") else "dark"
        t = self.current

        # Window root background
        self.root.configure(bg=t["bg_app"])

        # Base Frame styles
        self.style.configure("TFrame", background=t["bg_app"])
        self.style.configure("TopBar.TFrame", background=t["bg_panel"])
        self.style.configure("Sidebar.TFrame", background=t["bg_panel"])
        self.style.configure("PlayerBar.TFrame", background=t["bg_panel"])
        self.style.configure("Card.TFrame", background=t["bg_panel_alt"])

        # Label styles
        font_regular = get_ui_font(10)
        font_bold = get_ui_font(10, bold=True)
        font_title = get_ui_font(13, bold=True)
        font_muted = get_ui_font(9)

        self.style.configure(
            "TLabel",
            background=t["bg_app"],
            foreground=t["text_main"],
            font=font_regular,
        )
        self.style.configure(
            "Panel.TLabel",
            background=t["bg_panel"],
            foreground=t["text_main"],
            font=font_regular,
        )
        self.style.configure(
            "Title.TLabel",
            background=t["bg_panel"],
            foreground=t["text_main"],
            font=font_title,
        )
        self.style.configure(
            "Header.TLabel",
            background=t["bg_panel"],
            foreground=t["text_main"],
            font=font_bold,
        )
        self.style.configure(
            "Muted.TLabel",
            background=t["bg_panel"],
            foreground=t["text_muted"],
            font=font_muted,
        )

        # Standard button styling
        self.style.configure(
            "TButton",
            background=t["bg_panel_alt"],
            foreground=t["text_main"],
            bordercolor=t["border_color"],
            darkcolor=t["bg_panel_alt"],
            lightcolor=t["bg_panel_alt"],
            font=font_bold,
            padding=(8, 5),
            relief="flat",
        )
        self.style.map(
            "TButton",
            background=[
                ("pressed", t["accent_hover"]),
                ("active", t["border_color"]),
                ("disabled", t["bg_panel"]),
            ],
            foreground=[
                ("disabled", t["text_muted"]),
                ("pressed", "#ffffff"),
            ],
        )

        # Tab navigation buttons
        self.style.configure(
            "Tab.TButton",
            background=t["bg_panel"],
            foreground=t["text_muted"],
            bordercolor=t["bg_panel"],
            font=font_bold,
            padding=(12, 6),
            relief="flat",
        )
        self.style.map(
            "Tab.TButton",
            background=[("active", t["bg_panel_alt"])],
            foreground=[("active", t["text_main"])],
        )

        self.style.configure(
            "ActiveTab.TButton",
            background=t["accent"],
            foreground=t["accent_text"],
            bordercolor=t["accent"],
            font=font_bold,
            padding=(12, 6),
            relief="flat",
        )
        self.style.map(
            "ActiveTab.TButton",
            background=[("active", t["accent_hover"])],
            foreground=[("active", t["accent_text"])],
        )

        # Primary accent buttons (e.g. Insert, Build)
        self.style.configure(
            "Primary.TButton",
            background=t["accent"],
            foreground=t["accent_text"],
            bordercolor=t["accent"],
            font=font_bold,
            padding=(10, 5),
            relief="flat",
        )
        self.style.map(
            "Primary.TButton",
            background=[
                ("pressed", t["accent_hover"]),
                ("active", t["accent_hover"]),
                ("disabled", t["bg_panel_alt"]),
            ],
            foreground=[
                ("disabled", t["text_muted"]),
            ],
        )

        # Danger buttons (e.g. Remove)
        self.style.configure(
            "Danger.TButton",
            background=t["danger"],
            foreground="#ffffff",
            bordercolor=t["danger"],
            font=font_bold,
            padding=(10, 5),
            relief="flat",
        )
        self.style.map(
            "Danger.TButton",
            background=[
                ("pressed", t["danger_hover"]),
                ("active", t["danger_hover"]),
                ("disabled", t["bg_panel_alt"]),
            ],
            foreground=[
                ("disabled", t["text_muted"]),
            ],
        )

        # Action bar buttons (Top-right Undo, Clear, Share...)
        self.style.configure(
            "Action.TButton",
            background=t["bg_panel_alt"],
            foreground=t["text_main"],
            bordercolor=t["border_color"],
            font=get_ui_font(9, bold=True),
            padding=(8, 4),
            relief="flat",
        )
        self.style.map(
            "Action.TButton",
            background=[
                ("pressed", t["accent_hover"]),
                ("active", t["border_color"]),
                ("disabled", t["bg_panel"]),
            ],
            foreground=[
                ("disabled", t["text_muted"]),
            ],
        )

        # Entry fields
        self.style.configure(
            "TEntry",
            fieldbackground=t["bg_panel_alt"],
            foreground=t["text_main"],
            insertcolor=t["text_main"],
            bordercolor=t["border_color"],
            padding=5,
        )

        # Combobox dropdown
        self.style.configure(
            "TCombobox",
            fieldbackground=t["bg_panel_alt"],
            background=t["bg_panel_alt"],
            foreground=t["text_main"],
            arrowcolor=t["text_main"],
            bordercolor=t["border_color"],
            padding=4,
        )
        self.style.map(
            "TCombobox",
            fieldbackground=[("readonly", t["bg_panel_alt"])],
            foreground=[("readonly", t["text_main"])],
            selectbackground=[("readonly", t["accent"])],
            selectforeground=[("readonly", t["accent_text"])],
        )

        # Scrubber Scale Slider
        self.style.configure(
            "Horizontal.TScale",
            troughcolor=t["bg_panel_alt"],
            background=t["accent"],
            bordercolor=t["border_color"],
            darkcolor=t["accent"],
            lightcolor=t["accent"],
        )
        self.style.map(
            "Horizontal.TScale",
            background=[("active", t["accent_hover"])],
        )

        # Notify all registered components of theme update
        for cb in self.listeners:
            try:
                cb(t)
            except Exception:
                pass
