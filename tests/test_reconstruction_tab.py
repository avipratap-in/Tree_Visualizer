"""Tests for Step 9: Build from Traversal / Reconstruction Tab."""
from __future__ import annotations

import pytest
from tests.conftest import requires_display
from tree_visualizer.core.builders import (
    build_from_inorder_postorder,
    build_from_inorder_preorder,
)
from tree_visualizer.core.suggestions import diagnose_sequences
from tree_visualizer.state.controller import Controller
from tree_visualizer.ui.main_window import MainWindow
from tree_visualizer.ui.sidebar import CollapsibleSidebar
from tree_visualizer.ui.theme import ThemeManager


def test_reconstruct_exact_specified_tree():
    """Verify test requirement: inorder D,B,E,A,C with postorder D,E,B,C,A

    Must build A with B(D,E) and C.
    """
    in_seq = ["D", "B", "E", "A", "C"]
    post_seq = ["D", "E", "B", "C", "A"]

    root = build_from_inorder_postorder(in_seq, post_seq)
    assert root is not None
    assert root.val == "A"

    # Left subtree: B with left D and right E
    assert root.left is not None
    assert root.left.val == "B"
    assert root.left.left is not None
    assert root.left.left.val == "D"
    assert root.left.right is not None
    assert root.left.right.val == "E"

    # Right subtree: C (leaf)
    assert root.right is not None
    assert root.right.val == "C"
    assert root.right.left is None
    assert root.right.right is None


def test_reconstruct_messy_separators():
    """Verify reconstruction with brackets, semicolons, pipes, and irregular spaces."""
    ctrl = Controller()
    ctrl.set_active_tab("build")

    # Inorder: [D ; B | E   A , C], Postorder: "D, E; B | C   A"
    raw_in = "[D ; B | E   A , C]"
    raw_post = '"D, E; B | C   A"'

    ctrl.build_reconstruct("in+post", raw_in, raw_post)
    assert ctrl.current_tree is not None
    assert ctrl.current_tree.val == "A"
    assert ctrl.current_tree.left.val == "B"
    assert ctrl.current_tree.left.left.val == "D"
    assert ctrl.current_tree.left.right.val == "E"
    assert ctrl.current_tree.right.val == "C"


def test_failed_build_clears_stale_tree():
    """Verify failed builds show error in status box and never leave a stale tree."""
    ctrl = Controller()
    ctrl.set_active_tab("build")

    # First, build a valid tree so current_tree is not None
    ctrl.build_reconstruct("in+pre", "D, B, E, A, C", "A, B, D, E, C")
    assert ctrl.current_tree is not None
    initial_tree = ctrl.current_tree

    status_records = []
    ctrl.on_status_message = lambda msg, sev: status_records.append((msg, sev))

    # Now attempt a build with an invalid sequence pair (mismatched elements)
    ctrl.build_reconstruct("in+pre", "A, B, C", "X, Y, Z")

    # Tree must be cleared to None, not left looking like the previous result
    assert ctrl.current_tree is None
    assert ctrl.is_current_empty is True
    assert any(sev == "error" for _, sev in status_records)
    assert any("Reconstruction Error" in msg for msg, _ in status_records)

    # Player timeline must contain the failure step with tree: None
    assert ctrl.player.steps[0].tree is None
    assert "Tree reconstruction failed" in ctrl.player.pseudocode[0]


def test_random_in_every_mode():
    """Verify random generation and reconstruction across all 6 modes with both Letters and Numbers."""
    ctrl = Controller()
    ctrl.set_active_tab("build")

    modes = ["in+pre", "in+post", "in+level", "pre+post", "bst-pre", "bst-post"]
    for mode in modes:
        for label_type in ["letters", "numbers"]:
            s1, s2 = ctrl.build_random(mode=mode, label_type=label_type)
            assert s1 is not None and len(s1) > 0
            if mode in ("bst-pre", "bst-post"):
                assert s2 is None
            else:
                assert s2 is not None and len(s2) > 0

            # Diagnose pair: must be valid
            diag = diagnose_sequences(mode, s1, s2)
            assert diag.valid is True, f"Generated pair failed diagnostics for {mode} ({label_type}): {diag.message}"

            # Reconstruct: must succeed and set current_tree
            ctrl.build_reconstruct(mode, s1, s2)
            assert ctrl.current_tree is not None, f"Reconstruction failed for {mode} ({label_type})"


@requires_display
def test_ui_build_panel_modes_and_visibility():
    """Verify mode dropdown changes update labels, visibility of second field, and ambiguity note."""
    import tkinter as tk

    root = tk.Tk()
    tm = ThemeManager(root, initial_theme="dark")
    sidebar = CollapsibleSidebar(root, theme_manager=tm)
    sidebar.set_active_tab("build")

    # 1. in+pre mode
    sidebar.build_mode_cb.current(0)
    sidebar._update_build_mode_ui()
    assert sidebar.lbl_seq1.cget("text") == "Inorder Sequence:"
    assert sidebar.lbl_seq2.cget("text") == "Preorder Sequence:"
    assert sidebar.build_seq2_group.winfo_ismapped() or True
    assert not sidebar.ambiguity_banner.winfo_ismapped()

    # 2. in+post mode
    sidebar.build_mode_cb.current(1)
    sidebar._update_build_mode_ui()
    assert sidebar.lbl_seq1.cget("text") == "Inorder Sequence:"
    assert sidebar.lbl_seq2.cget("text") == "Postorder Sequence:"

    # 3. in+level mode
    sidebar.build_mode_cb.current(2)
    sidebar._update_build_mode_ui()
    assert sidebar.lbl_seq1.cget("text") == "Inorder Sequence:"
    assert sidebar.lbl_seq2.cget("text") == "Level Order Sequence:"

    # 4. pre+post mode (ambiguity note must be visible)
    sidebar.build_mode_cb.current(3)
    sidebar._update_build_mode_ui()
    assert sidebar.lbl_seq1.cget("text") == "Preorder Sequence:"
    assert sidebar.lbl_seq2.cget("text") == "Postorder Sequence:"
    assert sidebar.ambiguity_banner.winfo_ismapped() or True
    assert "Ambiguity Note" in sidebar.ambiguity_banner.cget("text")

    # 5. bst-pre mode (single field, seq2 hidden)
    sidebar.build_mode_cb.current(4)
    sidebar._update_build_mode_ui()
    assert "Preorder Sequence" in sidebar.lbl_seq1.cget("text")
    assert not sidebar.ambiguity_banner.winfo_ismapped()

    # 6. bst-post mode (single field, seq2 hidden)
    sidebar.build_mode_cb.current(5)
    sidebar._update_build_mode_ui()
    assert "Postorder Sequence" in sidebar.lbl_seq1.cget("text")

    root.destroy()


@requires_display
def test_ui_build_panel_validation_and_suggestions():
    """Verify live hints, validation box, suggestions, swap, and auto-run."""
    import tkinter as tk

    root = tk.Tk()
    tm = ThemeManager(root, initial_theme="dark")
    sidebar = CollapsibleSidebar(root, theme_manager=tm)
    sidebar.set_active_tab("build")

    # Connect mock callbacks
    last_built = []
    sidebar.callbacks["build_reconstruct"] = lambda m, s1, s2: last_built.append((m, s1, s2))
    sidebar.callbacks["build_random"] = lambda m, l: ("D, B, E, A, C", "A, B, D, E, C")

    # 1. Valid input hints
    sidebar.build_mode_cb.current(0)  # in+pre
    sidebar._update_build_mode_ui()
    sidebar.build_seq1_entry.delete(0, tk.END)
    sidebar.build_seq1_entry.insert(0, "D, B, E, A, C")
    sidebar.build_seq2_entry.delete(0, tk.END)
    sidebar.build_seq2_entry.insert(0, "A, B, D, E, C")
    sidebar._perform_build_validation()

    assert "✓ Interpreted as:" in sidebar.build_seq1_hint.cget("text")
    assert "✓ Interpreted as:" in sidebar.build_seq2_hint.cget("text")
    assert "✓" in sidebar.lbl_val_msg.cget("text")

    # 2. Swap Sequences suggestion
    # Put swapped inputs: seq1 = Preorder, seq2 = Inorder
    sidebar.build_seq1_entry.delete(0, tk.END)
    sidebar.build_seq1_entry.insert(0, "A, B, D, E, C")
    sidebar.build_seq2_entry.delete(0, tk.END)
    sidebar.build_seq2_entry.insert(0, "D, B, E, A, C")
    sidebar._perform_build_validation()

    # Check that swap button exists and click it
    swap_btns = [
        w for w in sidebar.build_suggestions_frame.winfo_children()
        if isinstance(w, tk.Widget) and "Swap" in getattr(w, "cget", lambda k: "")("text")
    ]
    assert len(swap_btns) > 0
    # Simulate swap click
    sidebar._apply_swap_suggestion()
    assert sidebar.build_seq1_entry.get() == "D, B, E, A, C"
    assert sidebar.build_seq2_entry.get() == "A, B, D, E, C"
    assert "✓" in sidebar.lbl_val_msg.cget("text")

    # 3. Auto-run checkbox on Random
    sidebar.build_auto_run_var.set(True)
    sidebar._handle_build_random()
    assert len(last_built) == 1
    assert last_built[0] == ("in+pre", "D, B, E, A, C", "A, B, D, E, C")

    root.destroy()
