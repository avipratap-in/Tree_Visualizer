"""Unit tests for tree reconstruction builders and error handling."""
from __future__ import annotations

import pytest
from tree_visualizer.core.builders import (
    AmbiguousTreeError,
    DuplicateValueError,
    MixedTypesError,
    TreeBuildError,
    build_bst_from_postorder,
    build_bst_from_preorder,
    build_from_inorder_level_order,
    build_from_inorder_postorder,
    build_from_inorder_preorder,
    build_from_preorder_postorder,
)
from tree_visualizer.core.node import TreeNode
from tree_visualizer.core.traversals import (
    inorder_recursive,
    level_order,
    postorder_recursive,
    preorder_recursive,
)


def test_build_inorder_preorder():
    inorder = ["D", "B", "E", "A", "F", "C"]
    preorder = ["A", "B", "D", "E", "C", "F"]

    root = build_from_inorder_preorder(inorder, preorder)
    assert root is not None
    assert inorder_recursive(root) == inorder
    assert preorder_recursive(root) == preorder


def test_build_inorder_postorder():
    inorder = ["D", "B", "E", "A", "F", "C"]
    postorder = ["D", "E", "B", "F", "C", "A"]

    root = build_from_inorder_postorder(inorder, postorder)
    assert root is not None
    assert inorder_recursive(root) == inorder
    assert postorder_recursive(root) == postorder


def test_build_inorder_level_order():
    inorder = ["D", "B", "E", "A", "C"]
    level = ["A", "B", "C", "D", "E"]

    root = build_from_inorder_level_order(inorder, level)
    assert root is not None
    assert inorder_recursive(root) == inorder
    assert level_order(root) == level


def test_build_preorder_postorder_full():
    # Full binary tree:
    #       1
    #     /   \
    #    2     3
    #   / \
    #  4   5
    preorder = [1, 2, 4, 5, 3]
    postorder = [4, 5, 2, 3, 1]

    root = build_from_preorder_postorder(preorder, postorder)
    assert root is not None
    assert preorder_recursive(root) == preorder
    assert postorder_recursive(root) == postorder


def test_build_preorder_postorder_ambiguity():
    # Tree where node 1 has only left child 2 (not full):
    #       1
    #      /
    #     2
    preorder = [1, 2]
    postorder = [2, 1]

    # Must raise AmbiguousTreeError
    with pytest.raises(AmbiguousTreeError) as exc_info:
        build_from_preorder_postorder(preorder, postorder)
    assert "ambiguous" in str(exc_info.value).lower()


def test_build_bst_from_preorder():
    # Numeric
    preorder_num = [50, 30, 20, 40, 70, 60, 80]
    root_num = build_bst_from_preorder(preorder_num)
    assert root_num is not None
    assert preorder_recursive(root_num) == preorder_num
    assert inorder_recursive(root_num) == sorted(preorder_num)

    # Alphabetic
    preorder_alpha = ["M", "F", "B", "H", "S", "P", "W"]
    root_alpha = build_bst_from_preorder(preorder_alpha)
    assert root_alpha is not None
    assert preorder_recursive(root_alpha) == preorder_alpha
    assert inorder_recursive(root_alpha) == sorted(preorder_alpha)


def test_build_bst_from_postorder():
    # Numeric
    postorder_num = [20, 40, 30, 60, 80, 70, 50]
    root_num = build_bst_from_postorder(postorder_num)
    assert root_num is not None
    assert postorder_recursive(root_num) == postorder_num
    assert inorder_recursive(root_num) == sorted(postorder_num)

    # Alphabetic
    postorder_alpha = ["B", "H", "F", "P", "W", "S", "M"]
    root_alpha = build_bst_from_postorder(postorder_alpha)
    assert root_alpha is not None
    assert postorder_recursive(root_alpha) == postorder_alpha
    assert inorder_recursive(root_alpha) == sorted(postorder_alpha)


def test_builder_exceptions():
    # Length mismatch
    with pytest.raises(TreeBuildError) as exc_info:
        build_from_inorder_preorder([1, 2, 3], [1, 2])
    assert "length mismatch" in str(exc_info.value).lower()

    # Inconsistent elements
    with pytest.raises(TreeBuildError) as exc_info:
        build_from_inorder_preorder([1, 2, 3], [1, 2, 4])
    assert "inconsistent" in str(exc_info.value).lower()

    # Duplicates in general tree reconstruction
    with pytest.raises(DuplicateValueError):
        build_from_inorder_preorder([1, 2, 2], [1, 2, 2])

    # Duplicates in BST preorder
    with pytest.raises(DuplicateValueError):
        build_bst_from_preorder([50, 30, 30])

    # Mixed numbers and letters in BST
    with pytest.raises(MixedTypesError):
        build_bst_from_preorder([50, "A", 30])

    # Invalid BST ordering
    with pytest.raises(TreeBuildError):
        build_bst_from_preorder([50, 60, 40])
