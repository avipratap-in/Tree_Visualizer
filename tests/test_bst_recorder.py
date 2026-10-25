"""Unit tests for BST operation recorder."""
from __future__ import annotations

import pytest
from tree_visualizer.core.bst import BinarySearchTree
from tree_visualizer.core.node import TreeNode
from tree_visualizer.recorder.bst_recorder import (
    record_create_from_array,
    record_insert,
    record_max,
    record_min,
    record_predecessor,
    record_rank,
    record_remove,
    record_search,
    record_select,
    record_successor,
)
from tree_visualizer.recorder.steps import Step


def test_record_search():
    bst = BinarySearchTree.create_from_array([50, 30, 70, 20])
    pseudo, steps = record_search(bst.root, 20)

    assert len(pseudo) == 4
    assert len(steps) > 0
    assert all(isinstance(s, Step) for s in steps)

    # Final step shows value found
    final_step = steps[-1]
    assert "found" in final_step.message.lower()
    assert final_step.pseudo_line == 1

    # Search non-existent
    _, steps_absent = record_search(bst.root, 99)
    assert "not found" in steps_absent[-1].message.lower()


def test_record_insert_equals_core():
    bst = BinarySearchTree.create_from_array([50, 30, 70])
    pseudo, steps = record_insert(bst.root, 40)

    # Core result
    core_bst = BinarySearchTree.create_from_array([50, 30, 70])
    core_bst.insert(40)

    final_tree = steps[-1].tree_root
    assert final_tree == core_bst.root
    assert "Inserted 40 as right child of 30." in steps[-1].message

    # Duplicate insert test
    _, dup_steps = record_insert(core_bst.root, 40)
    assert "incremented frequency to 2" in dup_steps[-1].message.lower()


def test_record_remove_all_cases():
    # 1. Leaf removal
    bst1 = BinarySearchTree.create_from_array([50, 30, 70, 20])
    _, steps_leaf = record_remove(bst1.root, 20)
    core1 = BinarySearchTree.create_from_array([50, 30, 70, 20])
    core1.remove(20)
    assert steps_leaf[-1].tree_root == core1.root
    assert any("is a leaf node" in s.message for s in steps_leaf)

    # 2. Duplicate frequency decrement
    bst_dup = BinarySearchTree.create_from_array([50, 30, 50])
    _, steps_dup = record_remove(bst_dup.root, 50)
    core_dup = BinarySearchTree.create_from_array([50, 30, 50])
    core_dup.remove(50)
    assert steps_dup[-1].tree_root == core_dup.root
    assert any("decremented frequency" in s.message.lower() for s in steps_dup)

    # 3. One child bypass
    bst2 = BinarySearchTree.create_from_array([50, 30, 70, 20])
    _, steps_child = record_remove(bst2.root, 30)
    core2 = BinarySearchTree.create_from_array([50, 30, 70, 20])
    core2.remove(30)
    assert steps_child[-1].tree_root == core2.root
    assert any("bypassing" in s.message.lower() for s in steps_child)

    # 4. Two children successor replacement
    bst3 = BinarySearchTree.create_from_array([50, 30, 70, 60, 80])
    _, steps_succ = record_remove(bst3.root, 70)
    core3 = BinarySearchTree.create_from_array([50, 30, 70, 60, 80])
    core3.remove(70)
    assert steps_succ[-1].tree_root == core3.root
    assert any("successor" in s.message.lower() for s in steps_succ)


def test_record_min_max():
    bst = BinarySearchTree.create_from_array([50, 25, 75, 12, 87])
    _, steps_min = record_min(bst.root)
    assert "Minimum value is 12" in steps_min[-1].message

    _, steps_max = record_max(bst.root)
    assert "Maximum value is 87" in steps_max[-1].message


def test_record_predecessor_successor():
    bst = BinarySearchTree.create_from_array([50, 25, 75, 12, 37, 62, 87])
    _, steps_pred = record_predecessor(bst.root, 50)
    assert "predecessor of 50 is 37" in steps_pred[-1].message.lower()

    _, steps_succ = record_successor(bst.root, 50)
    assert "successor of 50 is 62" in steps_succ[-1].message.lower()


def test_record_rank_and_select():
    bst = BinarySearchTree.create_from_array([50, 30, 70, 30, 50, 80, 20])
    _, steps_rank = record_rank(bst.root, 50)
    assert "Final rank of 50 is 3" in steps_rank[-1].message

    _, steps_select = record_select(bst.root, 4)
    assert "Found 4-th smallest element: 50" in steps_select[-1].message


def test_record_create_from_array():
    arr = [50, 25, 75, 12, 37]
    pseudo, steps = record_create_from_array(arr)

    core_bst = BinarySearchTree.create_from_array(arr)
    assert steps[-1].tree_root == core_bst.root
    assert "BST creation from array complete" in steps[-1].message
