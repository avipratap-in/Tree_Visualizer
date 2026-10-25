"""Unit tests for traversal operation recorder."""
from __future__ import annotations

import pytest
from tree_visualizer.core.binary_tree import BinaryTree
from tree_visualizer.core.traversals import (
    inorder_recursive,
    level_order,
    postorder_recursive,
    preorder_recursive,
)
from tree_visualizer.recorder.steps import Step
from tree_visualizer.recorder.traversal_recorder import (
    record_inorder,
    record_level_order,
    record_postorder,
    record_preorder,
)


@pytest.fixture
def sample_tree():
    return BinaryTree.from_level_order([1, 2, 3, 4, 5, 6]).root


def test_record_preorder(sample_tree):
    pseudo, steps = record_preorder(sample_tree)
    assert len(pseudo) == 4
    assert len(steps) > 0
    assert all(isinstance(s, Step) for s in steps)

    core_pre = preorder_recursive(sample_tree)
    # Check that visited sequence grows progressively
    visited_lengths = [len(s.visited) for s in steps]
    assert sorted(visited_lengths) == visited_lengths

    # Final visited sequence matches core preorder
    assert steps[-1].visited == core_pre


def test_record_inorder(sample_tree):
    pseudo, steps = record_inorder(sample_tree)
    assert len(pseudo) == 4
    core_in = inorder_recursive(sample_tree)
    assert steps[-1].visited == core_in


def test_record_postorder(sample_tree):
    pseudo, steps = record_postorder(sample_tree)
    assert len(pseudo) == 4
    core_post = postorder_recursive(sample_tree)
    assert steps[-1].visited == core_post


def test_record_level_order(sample_tree):
    pseudo, steps = record_level_order(sample_tree)
    assert len(pseudo) == 5
    core_lvl = level_order(sample_tree)
    assert steps[-1].visited == core_lvl
