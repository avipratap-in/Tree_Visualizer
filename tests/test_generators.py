"""Unit tests for generators.py and traversal pair round-trip rebuilding."""
from __future__ import annotations

import pytest
from tree_visualizer.core.builders import (
    build_bst_from_postorder,
    build_bst_from_preorder,
    build_from_inorder_level_order,
    build_from_inorder_postorder,
    build_from_inorder_preorder,
    build_from_preorder_postorder,
)
from tree_visualizer.core.generators import (
    generate_random_binary_tree,
    generate_random_bst,
    generate_random_full_binary_tree,
    generate_traversal_pair,
    get_random_labels,
    validate_and_clamp_n,
)
from tree_visualizer.core.properties import is_full
from tree_visualizer.core.traversals import (
    inorder_recursive,
    level_order,
    postorder_recursive,
    preorder_recursive,
)


def test_validate_and_clamp():
    with pytest.raises(ValueError):
        validate_and_clamp_n(0)

    with pytest.raises(ValueError):
        validate_and_clamp_n(-5)

    # Alphabetic clamped to max 26
    assert validate_and_clamp_n(30, label_type="letters") == 26
    assert validate_and_clamp_n(10, label_type="letters") == 10

    # Numeric clamped to max 99
    assert validate_and_clamp_n(150, label_type="numbers") == 99
    assert validate_and_clamp_n(42, label_type="numbers") == 42


def test_random_labels_uniqueness_and_ranges():
    # Numbers
    num_labels = get_random_labels(50, label_type="numbers")
    assert len(num_labels) == 50
    assert len(set(num_labels)) == 50
    assert all(1 <= x <= 99 for x in num_labels)

    # Letters
    alpha_labels = get_random_labels(30, label_type="letters")
    # Clamped to 26
    assert len(alpha_labels) == 26
    assert len(set(alpha_labels)) == 26
    assert all(len(x) == 1 and "A" <= x <= "Z" for x in alpha_labels)


def test_generate_random_full_binary_tree():
    for req_n in [1, 2, 4, 6, 7, 10, 15]:
        tree = generate_random_full_binary_tree(req_n, label_type="letters")
        assert is_full(tree) is True
        # Full binary trees always have odd node counts
        nodes_count = len(inorder_recursive(tree))
        assert nodes_count % 2 == 1


def test_generate_random_bst():
    bst = generate_random_bst(15, label_type="numbers")
    assert bst.is_valid_bst() is True
    assert bst.size() == 15


@pytest.mark.parametrize("mode", [
    "in+pre",
    "in+post",
    "in+level",
    "pre+post",
    "bst-pre",
    "bst-post",
])
@pytest.mark.parametrize("label_type", ["numbers", "letters"])
def test_generated_pairs_always_rebuild_same_tree(mode: str, label_type: str):
    """Verify that every generated traversal pair cleanly rebuilds the exact tree."""
    for n in [3, 7, 11]:
        seq1, seq2 = generate_traversal_pair(mode, n=n, labels=label_type)

        if mode == "in+pre":
            assert seq2 is not None
            rebuilt = build_from_inorder_preorder(seq1, seq2)
            assert rebuilt is not None
            assert inorder_recursive(rebuilt) == seq1
            assert preorder_recursive(rebuilt) == seq2

        elif mode == "in+post":
            assert seq2 is not None
            rebuilt = build_from_inorder_postorder(seq1, seq2)
            assert rebuilt is not None
            assert inorder_recursive(rebuilt) == seq1
            assert postorder_recursive(rebuilt) == seq2

        elif mode == "in+level":
            assert seq2 is not None
            rebuilt = build_from_inorder_level_order(seq1, seq2)
            assert rebuilt is not None
            assert inorder_recursive(rebuilt) == seq1
            assert level_order(rebuilt) == seq2

        elif mode == "pre+post":
            assert seq2 is not None
            rebuilt = build_from_preorder_postorder(seq1, seq2)
            assert rebuilt is not None
            assert preorder_recursive(rebuilt) == seq1
            assert postorder_recursive(rebuilt) == seq2

        elif mode == "bst-pre":
            assert seq2 is None
            rebuilt = build_bst_from_preorder(seq1)
            assert rebuilt is not None
            assert preorder_recursive(rebuilt) == seq1

        elif mode == "bst-post":
            assert seq2 is None
            rebuilt = build_bst_from_postorder(seq1)
            assert rebuilt is not None
            assert postorder_recursive(rebuilt) == seq1
