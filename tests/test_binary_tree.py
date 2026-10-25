"""Unit tests for BinaryTree and TreeNode classes."""
from __future__ import annotations

import pytest
from tree_visualizer.core.binary_tree import BinaryTree
from tree_visualizer.core.node import TreeNode, generate_node_id, reset_node_id_counter


def test_treenode_basics():
    reset_node_id_counter()
    n1 = TreeNode(10)
    assert n1.val == 10
    assert n1.value == 10
    assert n1.freq == 1
    assert n1.left is None
    assert n1.right is None
    assert n1.node_id == "node_1"
    assert n1.is_leaf() is True

    # Test value setter
    n1.value = 20
    assert n1.val == 20

    # Test serialization
    d = n1.to_dict()
    assert d["val"] == 20
    assert d["freq"] == 1
    assert d["left"] is None
    assert d["right"] is None

    # Test clone
    n2 = n1.clone()
    assert n2 == n1
    assert n2 is not n1
    assert n2.node_id == n1.node_id


def test_treenode_equality():
    t1 = TreeNode(5, left=TreeNode(3), right=TreeNode(8))
    t2 = TreeNode(5, left=TreeNode(3), right=TreeNode(8))
    t3 = TreeNode(5, left=TreeNode(3), right=TreeNode(9))
    assert t1 == t2
    assert t1 != t3
    assert t1 != "not_a_node"


def test_binary_tree_empty():
    bt = BinaryTree()
    assert bt.is_empty() is True
    assert bt.size() == 0
    assert bt.height() == 0
    assert bt.to_level_order() == []


def test_binary_tree_single_node():
    bt = BinaryTree(TreeNode("A"))
    assert bt.is_empty() is False
    assert bt.size() == 1
    assert bt.height() == 1
    assert bt.to_level_order() == ["A"]


def test_binary_tree_from_level_order():
    # [1, 2, 3, None, 4, 5, None]
    items = [1, 2, 3, None, 4, 5, None]
    bt = BinaryTree.from_level_order(items)
    assert bt.size() == 5
    assert bt.height() == 3
    assert bt.root.val == 1
    assert bt.root.left.val == 2
    assert bt.root.right.val == 3
    assert bt.root.left.left is None
    assert bt.root.left.right.val == 4
    assert bt.root.right.left.val == 5
    assert bt.root.right.right is None

    # Round trip level order
    assert bt.to_level_order() == [1, 2, 3, None, 4, 5]


def test_binary_tree_from_level_order_placeholders():
    items = ["A", "null", "B", "-", "C"]
    bt = BinaryTree.from_level_order(items)
    assert bt.root.val == "A"
    assert bt.root.left is None
    assert bt.root.right.val == "B"
    assert bt.root.right.left is None
    assert bt.root.right.right.val == "C"


def test_binary_tree_cloning():
    bt1 = BinaryTree.from_level_order([10, 20, 30])
    bt2 = bt1.clone()
    assert bt1 == bt2
    assert bt1.root is not bt2.root
