"""Unit tests for tree properties (leaf count, full, complete, perfect, balanced)."""
from __future__ import annotations

import pytest
from tree_visualizer.core.binary_tree import BinaryTree
from tree_visualizer.core.node import TreeNode
from tree_visualizer.core.properties import (
    compute_properties,
    height,
    internal_node_count,
    is_balanced,
    is_complete,
    is_full,
    is_perfect,
    leaf_count,
    size,
)


def test_properties_empty():
    props = compute_properties(None)
    assert props["leaves"] == 0
    assert props["internal"] == 0
    assert props["height"] == 0
    assert props["is_full"] is True
    assert props["is_complete"] is True
    assert props["is_perfect"] is True
    assert props["is_balanced"] is True


def test_properties_single_node():
    node = TreeNode(1)
    props = compute_properties(node)
    assert props["leaves"] == 1
    assert props["internal"] == 0
    assert props["height"] == 1
    assert props["is_full"] is True
    assert props["is_complete"] is True
    assert props["is_perfect"] is True
    assert props["is_balanced"] is True


def test_full_tree():
    # Full tree: 1 has 2 children (2, 3), both are leaves
    full_t = BinaryTree.from_level_order([1, 2, 3]).root
    assert is_full(full_t) is True

    # Non-full tree: 1 has left child 2 (which has no children), but 1 has no right child
    non_full_t = BinaryTree.from_level_order([1, 2]).root
    assert is_full(non_full_t) is False


def test_complete_tree():
    # Complete tree: levels filled left-to-right
    t_complete = BinaryTree.from_level_order([1, 2, 3, 4, 5]).root
    assert is_complete(t_complete) is True

    # Incomplete tree: gap in level-order (left missing but right present)
    t_incomplete = BinaryTree.from_level_order([1, 2, 3, None, 4]).root
    assert is_complete(t_incomplete) is False


def test_perfect_tree():
    # Perfect tree with 3 nodes (h=2, 2^2 - 1 = 3)
    p3 = BinaryTree.from_level_order([1, 2, 3]).root
    assert is_perfect(p3) is True

    # Perfect tree with 7 nodes (h=3, 2^3 - 1 = 7)
    p7 = BinaryTree.from_level_order([1, 2, 3, 4, 5, 6, 7]).root
    assert is_perfect(p7) is True

    # Complete but not perfect (5 nodes)
    c5 = BinaryTree.from_level_order([1, 2, 3, 4, 5]).root
    assert is_perfect(c5) is False


def test_balanced_tree_avl():
    # Balanced tree: |h_left - h_right| <= 1 for all nodes
    b_tree = BinaryTree.from_level_order([1, 2, 3, 4]).root
    assert is_balanced(b_tree) is True

    # Unbalanced tree: Left-skewed 3 -> 2 -> 1
    unbal = TreeNode(3, left=TreeNode(2, left=TreeNode(1)))
    assert is_balanced(unbal) is False


def test_counts():
    t = BinaryTree.from_level_order([1, 2, 3, 4, 5, 6, 7]).root
    assert size(t) == 7
    assert leaf_count(t) == 4
    assert internal_node_count(t) == 3
    assert height(t) == 3
