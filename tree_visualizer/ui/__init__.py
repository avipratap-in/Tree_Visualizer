"""Tkinter and ttk user interface layer.

Renders windows, tabs, canvas, player bar, pseudocode panel, status box,
and interactive operations panels.
"""
from __future__ import annotations

from tree_visualizer.ui.canvas_view import CanvasView
from tree_visualizer.ui.fonts import (
    get_code_font,
    get_definition_body_font,
    get_definition_title_font,
    get_ui_font,
    load_custom_fonts,
)
from tree_visualizer.ui.icon import generate_tree_icon, save_app_icons
from tree_visualizer.ui.layout import (
    CANVAS_HEIGHT,
    CANVAS_WIDTH,
    EdgeLayout,
    NodeLayout,
    TreeLayoutResult,
    compute_tree_layout,
)
from tree_visualizer.ui.main_window import MainWindow, enable_windows_dpi_awareness
from tree_visualizer.ui.overlays import PseudocodePanel, StatusBox
from tree_visualizer.ui.player_bar import PlayerBar
from tree_visualizer.ui.sidebar import CollapsibleSidebar
from tree_visualizer.ui.theme import DARK_THEME, LIGHT_THEME, ThemeManager
from tree_visualizer.ui.top_bar import TopBar

__all__ = [
    "MainWindow",
    "ThemeManager",
    "DARK_THEME",
    "LIGHT_THEME",
    "TopBar",
    "CollapsibleSidebar",
    "CanvasView",
    "PlayerBar",
    "StatusBox",
    "PseudocodePanel",
    "load_custom_fonts",
    "get_ui_font",
    "get_code_font",
    "get_definition_title_font",
    "get_definition_body_font",
    "save_app_icons",
    "generate_tree_icon",
    "enable_windows_dpi_awareness",
    "compute_tree_layout",
    "NodeLayout",
    "EdgeLayout",
    "TreeLayoutResult",
    "CANVAS_WIDTH",
    "CANVAS_HEIGHT",
]
