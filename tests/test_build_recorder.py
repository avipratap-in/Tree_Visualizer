"""Unit tests for tree reconstruction recorder."""
from __future__ import annotations

import pytest
from tree_visualizer.core.builders import (
    AmbiguousTreeError,
    build_bst_from_postorder,
    build_bst_from_preorder,
    build_from_inorder_level_order,
    build_from_inorder_postorder,
    build_from_inorder_preorder,
    build_from_preorder_postorder,
)
from tree_visualizer.recorder.build_recorder import (
    record_build_bst_from_postorder,
    record_build_bst_from_preorder,
    record_build_inorder_level_order,
    record_build_inorder_postorder,
    record_build_inorder_preorder,
    record_build_preorder_postorder,
)
from tree_visualizer.recorder.steps import Step


def test_record_build_inorder_preorder():
    inorder = ["D", "B", "E", "A", "C"]
    preorder = ["A", "B", "D", "E", "C"]

    pseudo, steps = record_build_inorder_preorder(inorder, preorder)
    assert len(pseudo) == 5
    assert len(steps) > 0
    assert all(isinstance(s, Step) for s in steps)

    core_tree = build_from_inorder_preorder(inorder, preorder)
    assert steps[-1].tree_root == core_tree

    # Check root selection and split messages
    assert any("Picked root value 'A'" in s.message for s in steps)
    assert any("Inorder split at 'A': Left subtree elements = ['D', 'B', 'E'], Right = ['C']" in s.message for s in steps)


def test_record_build_inorder_postorder():
    inorder = ["D", "B", "E", "A", "C"]
    postorder = ["D", "E", "B", "C", "A"]

    pseudo, steps = record_build_inorder_postorder(inorder, postorder)
    core_tree = build_from_inorder_postorder(inorder, postorder)
    assert steps[-1].tree_root == core_tree
    assert any("Picked root value 'A' from end of postorder" in s.message for s in steps)


def test_record_build_inorder_level_order():
    inorder = ["D", "B", "E", "A", "C"]
    level = ["A", "B", "C", "D", "E"]

    pseudo, steps = record_build_inorder_level_order(inorder, level)
    core_tree = build_from_inorder_level_order(inorder, level)
    assert steps[-1].tree_root == core_tree
    assert any("Picked root value 'A' from level-order" in s.message for s in steps)


def test_record_build_preorder_postorder():
    # Full binary tree: 1 -> left 2, right 3
    preorder = [1, 2, 3]
    postorder = [2, 3, 1]

    pseudo, steps = record_build_preorder_postorder(preorder, postorder)
    core_tree = build_from_preorder_postorder(preorder, postorder)
    assert steps[-1].tree_root == core_tree

    # Ambiguity check
    with pytest.raises(AmbiguousTreeError):
        record_build_preorder_postorder([1, 2], [2, 1])


def test_record_build_bst_from_preorder():
    preorder = [50, 30, 20, 40, 70]
    pseudo, steps = record_build_bst_from_preorder(preorder)
    core_tree = build_bst_from_preorder(preorder)
    assert steps[-1].tree_root == core_tree
    assert any("Placed '50' in BST within valid bounds" in s.message for s in steps)


def test_record_build_bst_from_postorder():
    postorder = [20, 40, 30, 70, 50]
    pseudo, steps = record_build_bst_from_postorder(postorder)
    core_tree = build_bst_from_postorder(postorder)
    assert steps[-1].tree_root == core_tree
    assert any("Placed '50' in BST within valid bounds" in s.message for s in steps)
