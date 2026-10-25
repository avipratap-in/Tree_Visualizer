"""Unit tests for pure tree layout mathematics and coordinate computation."""
from __future__ import annotations

import pytest
from tree_visualizer.core.bst import BinarySearchTree
from tree_visualizer.core.node import TreeNode
from tree_visualizer.ui.layout import (
    CANVAS_HEIGHT,
    CANVAS_WIDTH,
    MARGIN_X,
    MARGIN_Y,
    MAX_LEVEL_HEIGHT,
    NODE_RADIUS,
    compute_tree_layout,
)


def test_layout_empty_tree():
    """Verify empty tree returns zero nodes and edges."""
    res = compute_tree_layout(None)
    assert res.node_count == 0
    assert res.max_depth == 0
    assert len(res.nodes) == 0
    assert len(res.edges) == 0


def test_layout_single_node():
    """Verify single node is placed precisely in horizontal center at top margin."""
    root = TreeNode(val=42)
    res = compute_tree_layout(root)

    assert res.node_count == 1
    assert res.max_depth == 0
    assert len(res.nodes) == 1
    assert len(res.edges) == 0

    node_layout = res.get_node(root.node_id)
    assert node_layout is not None
    assert node_layout.x == CANVAS_WIDTH / 2.0  # 450.0
    assert node_layout.y == MARGIN_Y            # 60.0
    assert node_layout.label_text == "42"
    assert node_layout.radius == NODE_RADIUS


def test_layout_three_node_balanced_tree():
    """Verify 3-node tree coordinates follow Inorder sequence indices."""
    bst = BinarySearchTree()
    bst.insert(50)
    bst.insert(25)
    bst.insert(75)

    res = compute_tree_layout(bst.root)
    assert res.node_count == 3
    assert res.max_depth == 1
    assert len(res.edges) == 2

    usable_width = CANVAS_WIDTH - 2 * MARGIN_X  # 780.0
    # Inorder: 25 (idx 0), 50 (idx 1), 75 (idx 2)
    n25 = [n for n in res.nodes.values() if n.val == 25][0]
    n50 = [n for n in res.nodes.values() if n.val == 50][0]
    n75 = [n for n in res.nodes.values() if n.val == 75][0]

    assert n25.x == MARGIN_X                                      # 60.0
    assert n50.x == MARGIN_X + 0.5 * usable_width                 # 450.0
    assert n75.x == MARGIN_X + usable_width                       # 840.0

    # Depth & Y positions
    assert n50.y == MARGIN_Y
    assert n25.y == MARGIN_Y + MAX_LEVEL_HEIGHT                   # 60 + 85 = 145.0
    assert n75.y == MARGIN_Y + MAX_LEVEL_HEIGHT

    # Edges
    edge_pairs = {(e.parent_id, e.child_id) for e in res.edges}
    assert (n50.node_id, n25.node_id) in edge_pairs
    assert (n50.node_id, n75.node_id) in edge_pairs


def test_layout_frequency_labels():
    """Verify duplicate node frequency format 'val-freq'."""
    root = TreeNode(val=10, freq=3)
    res = compute_tree_layout(root)
    node_layout = res.get_node(root.node_id)
    assert node_layout is not None
    assert node_layout.label_text == "10-3"


def test_layout_deep_skewed_tree_level_compression():
    """Verify deep tree compresses level height to fit canvas boundaries."""
    # Build right-skewed tree of depth 8
    root = TreeNode(val=1)
    curr = root
    for v in range(2, 9):
        curr.right = TreeNode(val=v)
        curr = curr.right

    res = compute_tree_layout(root)
    assert res.node_count == 8
    assert res.max_depth == 7

    usable_height = CANVAS_HEIGHT - 2 * MARGIN_Y  # 380.0
    expected_level_h = usable_height / 7.0        # ~54.28px < 85px max
    assert expected_level_h < MAX_LEVEL_HEIGHT

    bottom_node = [n for n in res.nodes.values() if n.val == 8][0]
    assert pytest.approx(bottom_node.y, 0.01) == MARGIN_Y + 7 * expected_level_h
