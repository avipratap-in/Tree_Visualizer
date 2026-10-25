"""Unit tests for binary tree traversals (recursive vs iterative equivalence)."""
from __future__ import annotations

import pytest
from tree_visualizer.core.binary_tree import BinaryTree
from tree_visualizer.core.node import TreeNode
from tree_visualizer.core.traversals import (
    inorder_iterative,
    inorder_recursive,
    level_order,
    postorder_iterative,
    postorder_recursive,
    preorder_iterative,
    preorder_recursive,
)


@pytest.fixture
def sample_tree() -> TreeNode:
    # Construct tree:
    #       1
    #     /   \
    #    2     3
    #   / \   /
    #  4   5 6
    bt = BinaryTree.from_level_order([1, 2, 3, 4, 5, 6])
    return bt.root


def test_traversals_empty():
    assert preorder_recursive(None) == []
    assert preorder_iterative(None) == []
    assert inorder_recursive(None) == []
    assert inorder_iterative(None) == []
    assert postorder_recursive(None) == []
    assert postorder_iterative(None) == []
    assert level_order(None) == []


def test_traversals_single_node():
    node = TreeNode(42)
    assert preorder_recursive(node) == [42]
    assert preorder_iterative(node) == [42]
    assert inorder_recursive(node) == [42]
    assert inorder_iterative(node) == [42]
    assert postorder_recursive(node) == [42]
    assert postorder_iterative(node) == [42]
    assert level_order(node) == [42]


def test_traversals_recursive_iterative_equivalence(sample_tree):
    # Preorder: 1, 2, 4, 5, 3, 6
    pre_rec = preorder_recursive(sample_tree)
    pre_iter = preorder_iterative(sample_tree)
    assert pre_rec == [1, 2, 4, 5, 3, 6]
    assert pre_rec == pre_iter

    # Inorder: 4, 2, 5, 1, 6, 3
    in_rec = inorder_recursive(sample_tree)
    in_iter = inorder_iterative(sample_tree)
    assert in_rec == [4, 2, 5, 1, 6, 3]
    assert in_rec == in_iter

    # Postorder: 4, 5, 2, 6, 3, 1
    post_rec = postorder_recursive(sample_tree)
    post_iter = postorder_iterative(sample_tree)
    assert post_rec == [4, 5, 2, 6, 3, 1]
    assert post_rec == post_iter

    # Level order: 1, 2, 3, 4, 5, 6
    level = level_order(sample_tree)
    assert level == [1, 2, 3, 4, 5, 6]


def test_traversals_skewed_trees():
    # Left skewed: 3 -> 2 -> 1
    left_skewed = TreeNode(3, left=TreeNode(2, left=TreeNode(1)))
    assert preorder_recursive(left_skewed) == preorder_iterative(left_skewed) == [3, 2, 1]
    assert inorder_recursive(left_skewed) == inorder_iterative(left_skewed) == [1, 2, 3]
    assert postorder_recursive(left_skewed) == postorder_iterative(left_skewed) == [1, 2, 3]

    # Right skewed: 1 -> 2 -> 3
    right_skewed = TreeNode(1, right=TreeNode(2, right=TreeNode(3)))
    assert preorder_recursive(right_skewed) == preorder_iterative(right_skewed) == [1, 2, 3]
    assert inorder_recursive(right_skewed) == inorder_iterative(right_skewed) == [1, 2, 3]
    assert postorder_recursive(right_skewed) == postorder_iterative(right_skewed) == [3, 2, 1]
