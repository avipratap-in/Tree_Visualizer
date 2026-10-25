"""Randomized round-trip testing (300+ random trees across all 6 reconstruction modes).

Verifies that for every builder mode (in+pre, in+post, in+level, pre+post, bst-pre, bst-post),
extracting the traversals and rebuilding produces an identical binary tree.
Tested across both numeric (1-99) and alphabetic (letters A-Z) node labels.
"""
from __future__ import annotations

import random
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
)
from tree_visualizer.core.traversals import (
    inorder_recursive,
    level_order,
    postorder_recursive,
    preorder_recursive,
)


@pytest.mark.parametrize("label_type", ["numbers", "letters"])
def test_roundtrip_inorder_preorder(label_type: str):
    """50 round-trips for Inorder + Preorder builder (25 numbers, 25 letters)."""
    random.seed(42)
    for i in range(25):
        n = random.randint(1, 20)
        tree = generate_random_binary_tree(n, label_type=label_type)
        in_seq = inorder_recursive(tree)
        pre_seq = preorder_recursive(tree)

        rebuilt = build_from_inorder_preorder(in_seq, pre_seq)
        assert rebuilt == tree
        assert inorder_recursive(rebuilt) == in_seq
        assert preorder_recursive(rebuilt) == pre_seq


@pytest.mark.parametrize("label_type", ["numbers", "letters"])
def test_roundtrip_inorder_postorder(label_type: str):
    """50 round-trips for Inorder + Postorder builder (25 numbers, 25 letters)."""
    random.seed(43)
    for i in range(25):
        n = random.randint(1, 20)
        tree = generate_random_binary_tree(n, label_type=label_type)
        in_seq = inorder_recursive(tree)
        post_seq = postorder_recursive(tree)

        rebuilt = build_from_inorder_postorder(in_seq, post_seq)
        assert rebuilt == tree
        assert inorder_recursive(rebuilt) == in_seq
        assert postorder_recursive(rebuilt) == post_seq


@pytest.mark.parametrize("label_type", ["numbers", "letters"])
def test_roundtrip_inorder_level_order(label_type: str):
    """50 round-trips for Inorder + Level-Order builder (25 numbers, 25 letters)."""
    random.seed(44)
    for i in range(25):
        n = random.randint(1, 18)
        tree = generate_random_binary_tree(n, label_type=label_type)
        in_seq = inorder_recursive(tree)
        lvl_seq = level_order(tree)

        rebuilt = build_from_inorder_level_order(in_seq, lvl_seq)
        assert rebuilt == tree
        assert inorder_recursive(rebuilt) == in_seq
        assert level_order(rebuilt) == lvl_seq


@pytest.mark.parametrize("label_type", ["numbers", "letters"])
def test_roundtrip_preorder_postorder_full_tree(label_type: str):
    """50 round-trips for Preorder + Postorder on Full Binary Trees (25 numbers, 25 letters)."""
    random.seed(45)
    for i in range(25):
        # Odd node counts for full binary trees
        n = random.choice([1, 3, 5, 7, 9, 11, 15, 19])
        tree = generate_random_full_binary_tree(n, label_type=label_type)
        pre_seq = preorder_recursive(tree)
        post_seq = postorder_recursive(tree)

        rebuilt = build_from_preorder_postorder(pre_seq, post_seq)
        assert rebuilt == tree
        assert preorder_recursive(rebuilt) == pre_seq
        assert postorder_recursive(rebuilt) == post_seq


@pytest.mark.parametrize("label_type", ["numbers", "letters"])
def test_roundtrip_bst_from_preorder(label_type: str):
    """50 round-trips for BST from Preorder (25 numbers, 25 letters)."""
    random.seed(46)
    for i in range(25):
        n = random.randint(1, 20)
        bst = generate_random_bst(n, label_type=label_type)
        pre_seq = preorder_recursive(bst.root)

        rebuilt = build_bst_from_preorder(pre_seq)
        assert rebuilt == bst.root
        assert preorder_recursive(rebuilt) == pre_seq
        assert inorder_recursive(rebuilt) == inorder_recursive(bst.root)


@pytest.mark.parametrize("label_type", ["numbers", "letters"])
def test_roundtrip_bst_from_postorder(label_type: str):
    """50 round-trips for BST from Postorder (25 numbers, 25 letters)."""
    random.seed(47)
    for i in range(25):
        n = random.randint(1, 20)
        bst = generate_random_bst(n, label_type=label_type)
        post_seq = postorder_recursive(bst.root)

        rebuilt = build_bst_from_postorder(post_seq)
        assert rebuilt == bst.root
        assert postorder_recursive(rebuilt) == post_seq
        assert inorder_recursive(rebuilt) == inorder_recursive(bst.root)
