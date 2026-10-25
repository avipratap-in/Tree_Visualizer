"""GUI tests for Tree_Visualizer main window layout, theme switching, and controls."""
from __future__ import annotations

import os
import tkinter as tk
import pytest
from tests.conftest import requires_display
from tree_visualizer.constants import APP_NAME, MIN_WINDOW_HEIGHT, MIN_WINDOW_WIDTH
from tree_visualizer.ui.fonts import (
    get_definition_body_font,
    get_definition_title_font,
    get_ui_font,
    load_custom_fonts,
)
from tree_visualizer.ui.icon import generate_tree_icon, save_app_icons
from tree_visualizer.ui.main_window import MainWindow


def test_font_loader_and_helpers():
    """Verify font loader and typography helper functions."""
    loaded = load_custom_fonts()
    assert isinstance(loaded, bool)

    title_font = get_definition_title_font(28)
    assert len(title_font) == 3
    assert title_font[1] == 28

    body_font = get_definition_body_font(16)
    assert len(body_font) == 3
    assert body_font[1] == 16

    ui_font = get_ui_font(10, bold=True)
    assert len(ui_font) == 3
    assert "bold" in ui_font[2]


def test_icon_generation_and_saving(tmp_path):
    """Verify programmatic tree icon generation and asset saving."""
    img = generate_tree_icon(size=64)
    assert img.size == (64, 64)
    assert img.mode == "RGBA"

    png_path, ico_path = save_app_icons(assets_dir=str(tmp_path))
    assert os.path.exists(png_path)
    assert os.path.exists(ico_path)
    assert os.path.getsize(png_path) > 0
    assert os.path.getsize(ico_path) > 0


@requires_display
def test_main_window_initialization():
    """Verify window title, minimum bounds, and component hierarchy."""
    root = tk.Tk()
    app = MainWindow(root=root)
    root.update()

    assert root.title() == APP_NAME
    assert root.title() == "Tree_Visualizer"
    assert app.top_bar is not None
    assert app.sidebar is not None
    assert app.canvas_view is not None
    assert app.player_bar is not None

    app.destroy()


@requires_display
def test_main_window_theme_toggle():
    """Verify live theme switching between dark and light themes."""
    root = tk.Tk()
    app = MainWindow(root=root)
    root.update()

    initial_theme = app.theme_manager.theme_name

    # Toggle to opposite theme
    app._handle_theme_toggle()
    root.update()
    new_theme = app.theme_manager.theme_name
    assert new_theme != initial_theme
    assert new_theme in ("dark", "light")

    # Toggle back
    app._handle_theme_toggle()
    root.update()
    assert app.theme_manager.theme_name == initial_theme

    app.destroy()


@requires_display
def test_main_window_sidebar_collapse_and_expand():
    """Verify manual collapsing and expanding of operations sidebar."""
    root = tk.Tk()
    app = MainWindow(root=root)
    root.update()

    assert app.sidebar.is_collapsed is False

    # Collapse
    app.sidebar.collapse()
    root.update()
    assert app.sidebar.is_collapsed is True

    # Expand
    app.sidebar.expand()
    root.update()
    assert app.sidebar.is_collapsed is False

    app.destroy()


@requires_display
def test_main_window_tab_switching():
    """Verify navigation tab selection updates top bar, sidebar, and canvas."""
    root = tk.Tk()
    app = MainWindow(root=root)
    root.update()

    # Switch to Binary Tree tab
    app._on_tab_selected("binary")
    root.update()
    assert app.controller.active_tab == "binary"
    assert app.sidebar.active_tab == "binary"
    assert app.canvas_view.active_tab == "binary"

    # Switch to Build tab
    app._on_tab_selected("build")
    root.update()
    assert app.controller.active_tab == "build"
    assert app.sidebar.active_tab == "build"
    assert app.canvas_view.active_tab == "build"

    # Switch back to BST tab
    app._on_tab_selected("bst")
    root.update()
    assert app.controller.active_tab == "bst"

    app.destroy()


@requires_display
def test_main_window_auto_collapse_on_narrow_resize():
    """Verify auto-collapse behavior when window width is resized below threshold."""
    root = tk.Tk()
    app = MainWindow(root=root)
    root.update()

    # Emulate narrow configure event
    narrow_event = tk.Event()
    narrow_event.widget = root
    narrow_event.width = 850
    narrow_event.height = 700

    app._on_window_configure(narrow_event)
    root.update()
    assert app.sidebar.is_collapsed is True
    assert app._auto_collapsed is True

    # Emulate wide configure event restoring sidebar
    wide_event = tk.Event()
    wide_event.widget = root
    wide_event.width = 1100
    wide_event.height = 700

    app._on_window_configure(wide_event)
    root.update()
    assert app.sidebar.is_collapsed is False
    assert app._auto_collapsed is False

    app.destroy()


@requires_display
def test_canvas_view_empty_and_tree_rendering():
    """Verify canvas view draws empty definition card and node circles when tree exists."""
    root = tk.Tk()
    app = MainWindow(root=root)
    root.update()

    # Initially empty tree -> definition card drawn
    app.canvas_view.redraw()
    root.update()
    all_items = app.canvas_view.canvas.find_all()
    assert len(all_items) > 0

    # Insert a node into BST - loads 2-step animation timeline
    app.controller.bst_insert("42")
    root.update()
    assert app.controller.player.total_steps == 2
    assert app.controller.current_tree is not None

    # Advance animation to final frame
    app.controller.player.skip_to_end()
    root.update()
    assert app.canvas_view.current_tree is not None
    assert app.canvas_view.current_tree.val == 42

    # Canvas should have drawn node circle and text elements
    items = app.canvas_view.canvas.find_all()
    assert len(items) > 0

    app.destroy()
