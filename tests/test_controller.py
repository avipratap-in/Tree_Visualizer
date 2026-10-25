"""Unit tests for state Controller and tab coordinator."""
from __future__ import annotations

import pytest
from tree_visualizer.core.node import TreeNode
from tree_visualizer.state.controller import Controller
from tree_visualizer.state.settings import Settings


def test_controller_initial_state():
    """Verify default initial state of controller."""
    ctrl = Controller(settings=Settings())
    assert ctrl.active_tab == "bst"
    assert ctrl.current_tree is None
    assert ctrl.is_current_empty is True
    assert ctrl.is_empty_tab("bst") is True
    assert ctrl.is_empty_tab("binary") is True
    assert ctrl.is_empty_tab("build") is True
    assert ctrl.can_undo is False


def test_controller_tab_switching():
    """Verify switching tabs preserves independent trees and triggers callbacks."""
    ctrl = Controller()
    tab_events = []
    ctrl.on_tab_changed = lambda tab: tab_events.append(tab)

    # Insert into BST tab
    ctrl.bst_insert("50, 25, 75")
    assert ctrl.current_tree is not None
    assert ctrl.is_current_empty is False

    # Switch to binary tab
    ctrl.set_active_tab("binary")
    assert ctrl.active_tab == "binary"
    assert "binary" in tab_events
    assert ctrl.is_current_empty is True  # binary tree is still empty

    # Create binary tree
    ctrl.binary_load_level_order("1, 2, 3")
    assert ctrl.current_tree is not None
    assert ctrl.is_current_empty is False

    # Switch back to BST tab and verify tree was preserved
    ctrl.set_active_tab("bst")
    assert ctrl.active_tab == "bst"
    assert ctrl.current_tree is not None
    assert ctrl.current_tree.val == 50


def test_controller_undo_and_clear():
    """Verify undo history and clear behavior."""
    ctrl = Controller()
    undo_states = []
    ctrl.on_undo_state_changed = lambda state: undo_states.append(state)

    ctrl.bst_insert("10")
    assert ctrl.can_undo is True
    assert True in undo_states

    ctrl.bst_insert("20")
    assert ctrl.current_tree is not None
    assert ctrl.current_tree.right is not None
    assert ctrl.current_tree.right.val == 20

    # Undo second insertion
    assert ctrl.undo() is True
    assert ctrl.current_tree is not None
    assert ctrl.current_tree.right is None

    # Undo first insertion
    assert ctrl.undo() is True
    assert ctrl.current_tree is None
    assert ctrl.is_current_empty is True

    # Undo on empty stack
    assert ctrl.undo() is False

    # Re-insert and test clear()
    ctrl.bst_insert("10, 20")
    assert ctrl.current_tree is not None
    ctrl.clear()
    assert ctrl.current_tree is None
    assert ctrl.is_current_empty is True
    # Can undo clear
    assert ctrl.undo() is True
    assert ctrl.current_tree is not None


def test_controller_max_history():
    """Verify history stack adheres to MAX_HISTORY limit."""
    ctrl = Controller()
    for i in range(ctrl.MAX_HISTORY + 10):
        ctrl.save_history()

    assert len(ctrl.history_stacks[ctrl.active_tab]) == ctrl.MAX_HISTORY


def test_controller_bst_operations():
    """Verify BST search, min, max, predecessor, successor, rank, select, and remove."""
    ctrl = Controller()
    ctrl.bst_insert("50, 25, 75, 12, 37, 62, 87")

    # Min & Max
    status_messages = []
    ctrl.on_status_message = lambda msg, sev: status_messages.append((msg, sev))

    ctrl.bst_min()
    assert any("min" in msg.lower() for msg, _ in status_messages)

    ctrl.bst_max()
    assert any("max" in msg.lower() for msg, _ in status_messages)

    # Search
    ctrl.bst_search(37)
    assert any("found" in msg.lower() for msg, _ in status_messages)

    # Predecessor & Successor
    ctrl.bst_predecessor(50)
    assert any("predecessor" in msg.lower() for msg, _ in status_messages)

    ctrl.bst_successor(50)
    assert any("successor" in msg.lower() for msg, _ in status_messages)

    # Rank & Select
    ctrl.bst_rank(50)
    assert any("rank" in msg.lower() for msg, _ in status_messages)

    ctrl.bst_select(3)
    assert any("element" in msg.lower() or "select" in msg.lower() for msg, _ in status_messages)

    # Remove
    ctrl.bst_remove(25)
    assert ctrl.current_tree is not None
    assert ctrl.current_tree.left.val != 25 or ctrl.current_tree.size() == 6


def test_controller_bst_load_array_and_random():
    """Verify bst_load_array and bst_random."""
    ctrl = Controller()
    ctrl.bst_load_array("40, 20, 60, 10, 30")
    assert ctrl.current_tree is not None
    assert ctrl.current_tree.size() == 5

    ctrl.bst_random(n=6)
    assert ctrl.current_tree is not None
    assert ctrl.current_tree.size() == 6


def test_controller_presets():
    """Verify preset loading across tabs."""
    ctrl = Controller()

    ctrl.load_preset("balanced_bst")
    assert ctrl.active_tab == "bst"
    assert ctrl.current_tree is not None
    assert ctrl.current_tree.size() == 7

    ctrl.load_preset("full_binary_tree")
    assert ctrl.active_tab == "binary"
    assert ctrl.current_tree is not None
    assert ctrl.current_tree.size() == 7

    # Unknown preset handles error gracefully
    status_errs = []
    ctrl.on_status_message = lambda msg, sev: status_errs.append((msg, sev))
    ctrl.load_preset("unknown_fake_preset")
    assert any(sev == "error" for _, sev in status_errs)


def test_controller_binary_tree_and_traversals():
    """Verify random binary tree generation and traversals."""
    ctrl = Controller()
    ctrl.set_active_tab("binary")

    # Empty tree traversal warning
    status_records = []
    ctrl.on_status_message = lambda msg, sev: status_records.append((msg, sev))
    ctrl.run_traversal("in")
    assert any("empty" in msg.lower() for msg, _ in status_records)

    # Random binary tree
    ctrl.binary_random(n=5, label_type="letters")
    assert ctrl.current_tree is not None
    assert ctrl.current_tree.size() == 5

    # Run all 4 traversals
    for order in ("pre", "in", "post", "level"):
        ctrl.run_traversal(order)
        assert ctrl.player.total_steps > 0


def test_controller_build_reconstruction():
    """Verify reconstruction operations and error handling."""
    ctrl = Controller()
    ctrl.set_active_tab("build")

    # Valid reconstruction
    ctrl.build_reconstruct("in+pre", "D, B, E, A, F, C", "A, B, D, E, C, F")
    assert ctrl.current_tree is not None
    assert ctrl.current_tree.val == "A"
    assert ctrl.current_tree.size() == 6

    # Ambiguity detection on non-full pre+post
    status_records = []
    ctrl.on_status_message = lambda msg, sev: status_records.append((msg, sev))
    ctrl.build_reconstruct("pre+post", "A, B", "B, A")
    assert any(sev == "warning" for _, sev in status_records)

    # Invalid sequence input
    ctrl.build_reconstruct("in+pre", "A, B, C", "X, Y, Z")
    assert any(sev == "error" for _, sev in status_records)


def test_controller_share_code_integration():
    """Verify share code generation and loading through controller."""
    ctrl = Controller()
    ctrl.bst_insert("30, 15, 45")
    code = ctrl.get_share_code()

    # Create new controller and load share code
    ctrl2 = Controller()
    assert ctrl2.current_tree is None
    success = ctrl2.load_share_code(code)
    assert success is True
    assert ctrl2.active_tab == "bst"
    assert ctrl2.current_tree is not None
    assert ctrl2.current_tree.val == 30
    assert ctrl2.current_tree.size() == 3

    # Corrupt share code returns False and reports error
    err_msgs = []
    ctrl2.on_status_message = lambda msg, sev: err_msgs.append((msg, sev))
    assert ctrl2.load_share_code("corrupted_share_string") is False
    assert any(sev == "error" for _, sev in err_msgs)


def test_controller_observer_property_updates():
    """Verify compute_properties observer is called when tree updates."""
    ctrl = Controller()
    props_history = []
    ctrl.on_properties_changed = lambda props: props_history.append(props)

    ctrl.bst_insert("50")
    assert len(props_history) > 0
    latest = props_history[-1]
    assert latest["size"] == 1
    assert latest["height"] == 1
    assert latest["is_full"] is True
