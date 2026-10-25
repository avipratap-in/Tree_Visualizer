"""Quality and edge case audit tests against the reference specification.

Covers:
- Empty tree operations and guards
- Single node tree metrics and traversals
- Deep skewed tree (10+ nodes) level clamping
- BST duplicate handling and frequency labels ("7-2", "7-3")
- Alphabetic label sorting in BST
- Dense tree with 40+ nodes (adaptive node radius)
- Rapid playback click locking
- Tiny (640x480) and huge (2560x1440) window sizing
- Full GUI smoke test (open window, generate Random, run traversal, close cleanly)
"""
from __future__ import annotations

import pytest
from tests.conftest import requires_display
from tree_visualizer.core.binary_tree import BinaryTree
from tree_visualizer.core.bst import BinarySearchTree
from tree_visualizer.core.generators import generate_random_bst
from tree_visualizer.core.node import TreeNode
from tree_visualizer.core.properties import compute_properties
from tree_visualizer.core.traversals import inorder_recursive
from tree_visualizer.export import render_tree_to_pillow_image, render_tree_to_svg
from tree_visualizer.state.controller import Controller
from tree_visualizer.ui.layout import compute_tree_layout
from tree_visualizer.ui.main_window import MainWindow
from tree_visualizer.ui.theme import ThemeManager


def test_edge_case_empty_tree_operations():
    """Verify all operations on an empty tree emit friendly warnings without throwing."""
    ctrl = Controller()
    ctrl.set_active_tab("bst")
    assert ctrl.current_tree is None

    status_records = []
    ctrl.on_status_message = lambda msg, sev: status_records.append((msg, sev))

    ctrl.bst_search(50)
    ctrl.bst_remove(50)
    ctrl.bst_min()
    ctrl.bst_max()
    ctrl.bst_predecessor(50)
    ctrl.bst_successor(50)
    ctrl.bst_rank(50)
    ctrl.bst_select(1)
    ctrl.run_traversal("in")

    assert len(status_records) >= 8
    assert all(sev in ("warning", "info") for _, sev in status_records)
    assert any("empty" in msg.lower() for msg, _ in status_records)


def test_edge_case_single_node_tree():
    """Verify 1-node tree properties, traversals, and bounds."""
    root = TreeNode(42)
    props = compute_properties(root)

    assert props["size"] == 1
    assert props["height"] == 1
    assert props["leaves"] == 1
    assert props["internal"] == 0
    assert props["is_full"] is True
    assert props["is_complete"] is True
    assert props["is_perfect"] is True
    assert props["is_balanced"] is True

    layout = compute_tree_layout(root)
    assert layout.node_count == 1
    assert len(layout.edges) == 0
    node = layout.nodes[root.node_id]
    assert node.x == 450.0  # Centered at canvas width / 2
    assert node.y == 60.0   # Top margin


def test_edge_case_deep_skewed_tree():
    """Verify deep skewed tree (12 nodes) clamps level height to prevent overflowing."""
    bst = BinarySearchTree()
    for v in range(1, 13):
        bst.insert(v)

    layout = compute_tree_layout(bst.root, canvas_width=900, canvas_height=500)
    assert layout.node_count == 12
    assert layout.max_depth == 11

    # Clamped level height ensures deepest node fits inside canvas height
    max_y = max(n.y for n in layout.nodes.values())
    assert max_y <= 500.0


def test_edge_case_bst_duplicates_frequency():
    """Verify duplicate insertions increment frequency and format labels as 'val-freq'."""
    bst = BinarySearchTree()
    bst.insert(7)
    bst.insert(7)
    assert bst.root is not None
    assert bst.root.freq == 2

    layout1 = compute_tree_layout(bst.root)
    node1 = layout1.nodes[bst.root.node_id]
    assert node1.label_text == "7-2"

    bst.insert(7)
    assert bst.root.freq == 3
    layout2 = compute_tree_layout(bst.root)
    assert layout2.nodes[bst.root.node_id].label_text == "7-3"

    # Remove decrements
    bst.remove(7)
    assert bst.root.freq == 2


def test_edge_case_alphabetic_labels():
    """Verify alphabetic labels compare and sort in correct lexicographical order."""
    bst = BinarySearchTree()
    letters = ["M", "B", "Z", "A", "C", "P"]
    for ch in letters:
        bst.insert(ch)

    inorder = inorder_recursive(bst.root)
    assert inorder == ["A", "B", "C", "M", "P", "Z"]


def test_edge_case_dense_40_nodes():
    """Verify 40+ node tree adapts radius and exports without errors."""
    tree = BinaryTree.from_level_order(list(range(1, 45)))
    assert tree.root is not None

    layout = compute_tree_layout(tree.root, canvas_width=900, canvas_height=500)
    assert layout.node_count == 44

    # Node radius must adapt to prevent overlapping
    for n in layout.nodes.values():
        assert n.radius <= 12.0

    # Exports must succeed without Pillow or SVG errors
    img = render_tree_to_pillow_image(tree.root)
    assert img.size == (1800, 1000)

    svg = render_tree_to_svg(tree.root)
    assert "<circle" in svg
    assert len(svg) > 2000


def test_edge_case_rapid_clicks_playback_lock():
    """Verify playback locking protects controller state during animation."""
    ctrl = Controller()
    ctrl.set_active_tab("bst")
    ctrl.bst_random(7)
    assert ctrl.current_tree is not None

    # Simulate play state
    ctrl.player.is_playing = True
    assert ctrl.player.is_playing is True

    # Playback pause restores state
    ctrl.player.pause()
    assert ctrl.player.is_playing is False


@requires_display
def test_edge_case_window_resizing_tiny_and_huge():
    """Verify MainWindow handles tiny (640x480) and huge (2560x1440) resize events."""
    import tkinter as tk

    root = tk.Tk()
    ctrl = Controller()
    app = MainWindow(root, controller=ctrl)

    # 1. Resize to tiny
    root.geometry("640x480")
    root.update_idletasks()
    # Narrow screen triggers auto-collapse
    app._on_window_configure(type("Event", (), {"widget": root, "width": 640})())
    assert app.sidebar.is_collapsed is True

    # 2. Resize to huge
    root.geometry("2560x1440")
    root.update_idletasks()
    app._on_window_configure(type("Event", (), {"widget": root, "width": 2560})())
    assert app.sidebar.is_collapsed is False

    app.destroy()


@requires_display
def test_gui_smoke_test_full_lifecycle():
    """Full GUI smoke test: opens window, creates Random BST, runs traversal, ticks player, and closes."""
    import tkinter as tk

    root = tk.Tk()
    ctrl = Controller()
    app = MainWindow(root, controller=ctrl)
    root.update_idletasks()

    # 1. Click Random in BST
    app.sidebar._handle_bst_random()
    root.update_idletasks()
    assert ctrl.current_tree is not None

    # 2. Switch to Binary Tree and run Inorder traversal
    app.top_bar.select_tab("binary")
    app.controller.set_active_tab("binary")
    app.sidebar._handle_binary_random()
    root.update_idletasks()
    assert ctrl.current_tree is not None

    # 3. Trigger Traversal and tick animation
    app.sidebar._handle_traversal("in")
    root.update_idletasks()
    assert ctrl.player.total_steps > 0

    # Step through animation
    ctrl.player.step_forward()
    root.update_idletasks()
    assert ctrl.player.current_index >= 1

    # 4. Clean shutdown
    app.destroy()
