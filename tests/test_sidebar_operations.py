"""Tests for operations panels, controller connectivity, button states, and settings."""
from __future__ import annotations

import tkinter as tk
import pytest
from tests.conftest import requires_display
from tree_visualizer.ui.main_window import MainWindow


@requires_display
def test_sidebar_bst_operations():
    """Verify BST tab operations trigger controller actions and update canvas."""
    root = tk.Tk()
    app = MainWindow(root=root)
    root.update()

    # 1. Random BST
    app.sidebar.bst_count_entry.delete(0, tk.END)
    app.sidebar.bst_count_entry.insert(0, "5")
    app.sidebar._handle_bst_random()
    root.update()
    assert app.controller.current_tree is not None
    assert app.controller.current_tree.size() == 5

    # 2. Preset Selection
    app.sidebar.bst_preset_cb.current(1)  # Balanced BST
    app.sidebar._handle_preset_selected(None)
    root.update()
    assert app.controller.current_tree.size() == 7

    # 3. Insert value
    app.sidebar.bst_insert_entry.delete(0, tk.END)
    app.sidebar.bst_insert_entry.insert(0, "99")
    app.sidebar._handle_bst_insert()
    root.update()
    assert app.controller.current_tree.size() == 8

    # 4. Search, Min, Max, Predecessor, Successor, Rank, Select
    app.sidebar.bst_search_entry.delete(0, tk.END)
    app.sidebar.bst_search_entry.insert(0, "99")
    app.sidebar._handle_bst_search()
    root.update()
    assert app.controller.player.total_steps > 0

    app.sidebar._handle_bst_min()
    root.update()
    assert app.controller.player.total_steps > 0

    app.sidebar._handle_bst_max()
    root.update()
    assert app.controller.player.total_steps > 0

    app.sidebar.bst_ps_entry.delete(0, tk.END)
    app.sidebar.bst_ps_entry.insert(0, "50")
    app.sidebar._handle_bst_pred()
    root.update()
    assert app.controller.player.total_steps > 0

    app.sidebar._handle_bst_succ()
    root.update()
    assert app.controller.player.total_steps > 0

    app.sidebar.bst_rank_entry.delete(0, tk.END)
    app.sidebar.bst_rank_entry.insert(0, "50")
    app.sidebar._handle_bst_rank()
    root.update()
    assert app.controller.player.total_steps > 0

    app.sidebar.bst_select_entry.delete(0, tk.END)
    app.sidebar.bst_select_entry.insert(0, "2")
    app.sidebar._handle_bst_select()
    root.update()
    assert app.controller.player.total_steps > 0

    # 5. Remove
    app.sidebar.bst_remove_entry.delete(0, tk.END)
    app.sidebar.bst_remove_entry.insert(0, "99")
    app.sidebar._handle_bst_remove()
    root.update()
    assert app.controller.current_tree.size() == 7

    app.destroy()


@requires_display
def test_sidebar_binary_tree_operations_and_settings():
    """Verify Binary Tree generation, label toggle settings persistence, and hint note."""
    root = tk.Tk()
    app = MainWindow(root=root)
    root.update()

    app._on_tab_selected("binary")
    root.update()

    # 1. Label toggle remembered in settings
    app.sidebar.bt_label_type_var.set("letters")
    app.sidebar._on_label_type_toggle()
    assert app.controller.settings.bt_label_type == "letters"

    # Clamp test: count requested > 26 for letters clamped to 26
    app.sidebar.bt_count_entry.delete(0, tk.END)
    app.sidebar.bt_count_entry.insert(0, "30")
    app.sidebar._handle_binary_random()
    root.update()
    assert app.controller.current_tree is not None
    assert app.controller.current_tree.size() <= 26

    # 2. Lenient load with hint note
    app.sidebar.bt_level_entry.delete(0, tk.END)
    app.sidebar.bt_level_entry.insert(0, "[1, 2, 3; null | 4]")
    app.sidebar._handle_binary_load()
    root.update()
    hint_text = app.sidebar.bt_hint_label.cget("text")
    assert "Interpreted as:" in hint_text
    assert "1" in hint_text
    assert app.controller.current_tree is not None

    # 3. Traversals
    for trav in ("pre", "in", "post", "level"):
        app.sidebar._handle_traversal(trav)
        root.update()
        assert app.controller.player.total_steps > 0

    app.destroy()


@requires_display
def test_sidebar_build_panel_and_random():
    """Verify Build from Traversal mode change, random pair generation, and build."""
    root = tk.Tk()
    app = MainWindow(root=root)
    root.update()

    app._on_tab_selected("build")
    root.update()

    # Pre+post ambiguity banner check
    app.sidebar.build_mode_cb.current(3)  # Preorder + Postorder
    app.sidebar._handle_build_mode_changed(None)
    root.update()
    assert app.sidebar.ambiguity_banner.winfo_ismapped()

    # Mode 0: Inorder + Preorder
    app.sidebar.build_mode_cb.current(0)
    app.sidebar._handle_build_mode_changed(None)
    root.update()
    assert not app.sidebar.ambiguity_banner.winfo_ismapped()

    # Random Pair
    app.sidebar._handle_build_random()
    root.update()
    assert len(app.sidebar.build_seq1_entry.get().strip()) > 0
    assert len(app.sidebar.build_seq2_entry.get().strip()) > 0

    # Build & Animate
    app.sidebar._handle_build_animate()
    root.update()
    assert app.controller.current_tree is not None

    app.destroy()


@requires_display
def test_disable_buttons_during_animation():
    """Verify operation buttons are disabled during playback and re-enabled on pause."""
    root = tk.Tk()
    app = MainWindow(root=root)
    root.update()

    assert len(app.sidebar.operation_buttons) > 0

    # Initially not playing -> all buttons normal
    for btn in app.sidebar.operation_buttons:
        assert str(btn.cget("state")) != "disabled"

    # Start playback
    app.controller.player.steps = [app.controller.player.current_step or None, None]  # dummy steps
    app.controller.player.play()
    root.update()

    # While playing -> all operation buttons disabled
    for btn in app.sidebar.operation_buttons:
        assert str(btn.cget("state")) == "disabled"
    assert str(app.top_bar.btn_clear.cget("state")) == "disabled"
    assert str(app.top_bar.btn_undo.cget("state")) == "disabled"

    # Pause playback
    app.controller.player.pause()
    root.update()

    # Operation buttons re-enabled
    for btn in app.sidebar.operation_buttons:
        assert str(btn.cget("state")) == "normal"
    assert str(app.top_bar.btn_clear.cget("state")) == "normal"

    app.destroy()


@requires_display
def test_clear_and_undo_definition_card_behavior():
    """Verify Clear brings back definition card and Undo restores previous tree."""
    root = tk.Tk()
    app = MainWindow(root=root)
    root.update()

    # Initially empty -> card shown
    assert len(app.canvas_view.canvas.find_withtag("definition_card")) > 0

    # Insert node -> card gone
    app.controller.bst_insert("42")
    root.update()
    app.controller.player.skip_to_end()
    root.update()
    assert len(app.canvas_view.canvas.find_withtag("definition_card")) == 0

    # Clear -> card returns
    app.top_bar._handle_clear()
    root.update()
    assert len(app.canvas_view.canvas.find_withtag("definition_card")) > 0
    assert app.controller.current_tree is None

    # Undo -> tree returns, card gone
    app.top_bar._handle_undo()
    root.update()
    app.controller.player.skip_to_end()
    root.update()
    assert len(app.canvas_view.canvas.find_withtag("definition_card")) == 0
    assert app.controller.current_tree is not None
    assert app.controller.current_tree.val == 42

    app.destroy()
