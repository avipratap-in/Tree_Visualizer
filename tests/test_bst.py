"""Unit tests for BinarySearchTree and duplicate handling."""
from __future__ import annotations

import pytest
from tree_visualizer.core.bst import BinarySearchTree
from tree_visualizer.core.comparison import compare_bst_keys
from tree_visualizer.core.exceptions import MixedTypesError
from tree_visualizer.core.node import TreeNode


def test_bst_empty():
    bst = BinarySearchTree()
    assert bst.is_empty() is True
    assert bst.size() == 0
    assert bst.height() == 0
    assert bst.min() is None
    assert bst.max() is None
    assert bst.search(10) is None
    assert bst.remove(10) is False
    assert bst.is_valid_bst() is True


def test_bst_single_node():
    bst = BinarySearchTree()
    bst.insert(50)
    assert bst.is_empty() is False
    assert bst.size() == 1
    assert bst.height() == 1
    assert bst.min() == 50
    assert bst.max() == 50
    assert bst.search(50) is not None
    assert bst.search(20) is None
    assert bst.is_valid_bst() is True


def test_bst_duplicates_frequency():
    bst = BinarySearchTree()
    bst.insert(50)
    bst.insert(30)
    bst.insert(50)  # duplicate
    bst.insert(50)  # duplicate

    node50 = bst.search(50)
    assert node50 is not None
    assert node50.freq == 3
    assert bst.size(include_duplicates=True) == 4
    assert bst.size(include_duplicates=False) == 2

    # Remove one duplicate: freq decreases from 3 to 2, node remains
    assert bst.remove(50) is True
    assert node50.freq == 2
    assert bst.search(50) is not None

    # Remove again: freq decreases to 1
    assert bst.remove(50) is True
    assert node50.freq == 1

    # Remove final 50: physically deletes node
    assert bst.remove(50) is True
    assert bst.search(50) is None
    assert bst.root.val == 30


def test_bst_removal_cases():
    # Case 1: Leaf removal
    bst = BinarySearchTree.create_from_array([50, 30, 70, 20])
    assert bst.remove(20) is True
    assert bst.search(20) is None
    assert bst.search(30).left is None

    # Case 2: One child removal (bypass)
    bst = BinarySearchTree.create_from_array([50, 30, 70, 20])
    # 30 has only one child (20)
    assert bst.remove(30) is True
    assert bst.search(30) is None
    assert bst.root.left.val == 20

    # Case 3: Two children removal (successor replacement)
    bst = BinarySearchTree.create_from_array([50, 30, 70, 60, 80])
    # 70 has two children (60 and 80); successor is 80 (or 60 if left?) successor is min(right) = 80
    assert bst.remove(70) is True
    assert bst.search(70) is None
    assert bst.root.right.val == 80
    assert bst.root.right.left.val == 60

    # Root removal with two children
    bst = BinarySearchTree.create_from_array([50, 30, 70, 20, 40, 60, 80])
    assert bst.remove(50) is True
    assert bst.search(50) is None
    assert bst.root.val == 60  # Inorder successor of 50
    assert bst.is_valid_bst() is True


def test_bst_min_max_pred_succ():
    values = [50, 25, 75, 12, 37, 62, 87]
    bst = BinarySearchTree.create_from_array(values)

    assert bst.min() == 12
    assert bst.max() == 87

    # Predecessor
    assert bst.predecessor(50) == 37
    assert bst.predecessor(25) == 12
    assert bst.predecessor(12) is None  # Smallest element
    assert bst.predecessor(60) == 50   # Absent value

    # Successor
    assert bst.successor(50) == 62
    assert bst.successor(75) == 87
    assert bst.successor(87) is None   # Largest element
    assert bst.successor(60) == 62    # Absent value


def test_bst_rank_and_select():
    # Sorted order with duplicates: 20, 30 (x2), 50 (x2), 70, 80
    # Total count = 7
    values = [50, 30, 70, 30, 50, 80, 20]
    bst = BinarySearchTree.create_from_array(values)

    assert bst.size(include_duplicates=True) == 7

    # Rank: number of elements strictly smaller than target
    assert bst.rank(20) == 0
    assert bst.rank(30) == 1  # 20
    assert bst.rank(50) == 3  # 20, 30, 30
    assert bst.rank(70) == 5  # 20, 30, 30, 50, 50
    assert bst.rank(80) == 6
    assert bst.rank(100) == 7

    # Select: 1-indexed k-th smallest element
    assert bst.select(0) is None   # Out of bounds
    assert bst.select(8) is None   # Out of bounds
    assert bst.select(1) == 20
    assert bst.select(2) == 30
    assert bst.select(3) == 30
    assert bst.select(4) == 50
    assert bst.select(5) == 50
    assert bst.select(6) == 70
    assert bst.select(7) == 80


def test_bst_alphabetic_labels():
    letters = ["M", "F", "S", "B", "H", "P", "W"]
    bst = BinarySearchTree.create_from_array(letters)

    assert bst.is_valid_bst() is True
    assert bst.min() == "B"
    assert bst.max() == "W"
    assert bst.predecessor("M") == "H"
    assert bst.successor("M") == "P"
    assert bst.rank("M") == 3
    assert bst.select(1) == "B"
    assert bst.select(4) == "M"
    assert bst.select(7) == "W"


def test_bst_mixed_types_rejection():
    bst = BinarySearchTree()
    bst.insert(50)
    with pytest.raises(MixedTypesError):
        bst.insert("A")

    bst2 = BinarySearchTree()
    bst2.insert("Alpha")
    with pytest.raises(MixedTypesError):
        bst2.insert(42)

    with pytest.raises(MixedTypesError):
        compare_bst_keys(10, "ten")
