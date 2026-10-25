"""Random tree and traversal generators.

Generates random binary trees, full binary trees, and BSTs with
either alphabetic labels (A-Z, strictly clamped to max 26) or
numeric labels (1-99, clamped to max 99).
Provides traversal pairs guaranteed to be valid and uniquely reconstructible.
"""
from __future__ import annotations

import random
from typing import Any, List, Optional, Tuple
from tree_visualizer.core.bst import BinarySearchTree
from tree_visualizer.core.node import TreeNode
from tree_visualizer.core.traversals import (
    inorder_recursive,
    level_order,
    postorder_recursive,
    preorder_recursive,
)


def validate_and_clamp_n(n: int, label_type: str = "letters") -> int:
    """Validate and clamp node count based on label type limits.

    Raises:
        ValueError: if n <= 0.
    """
    if n <= 0:
        raise ValueError("Node count n must be positive (got {n}).")

    if label_type == "letters":
        return min(n, 26)
    else:
        return min(n, 99)


def get_random_labels(n: int, label_type: str = "letters") -> List[Any]:
    """Generate n unique labels: letters (A-Z, max 26) or numbers (1-99, max 99)."""
    clamped_n = validate_and_clamp_n(n, label_type)

    if label_type == "numbers":
        pool = list(range(1, 100))
        return random.sample(pool, clamped_n)
    else:
        alphabet = [chr(c) for c in range(ord("A"), ord("Z") + 1)]
        return random.sample(alphabet, clamped_n)


def generate_random_binary_tree(n: int, label_type: str = "letters") -> TreeNode:
    """Generate a random connected binary tree with n unique nodes."""
    clamped_n = validate_and_clamp_n(n, label_type)
    labels = get_random_labels(clamped_n, label_type)
    root = TreeNode(labels[0])
    nodes = [root]

    for label in labels[1:]:
        new_node = TreeNode(label)
        candidates = [node for node in nodes if node.left is None or node.right is None]
        parent = random.choice(candidates)
        if parent.left is None and parent.right is None:
            if random.random() < 0.5:
                parent.left = new_node
            else:
                parent.right = new_node
        elif parent.left is None:
            parent.left = new_node
        else:
            parent.right = new_node
        nodes.append(new_node)

    return root


def generate_random_full_binary_tree(n: int, label_type: str = "letters") -> TreeNode:
    """Generate a random Full Binary Tree (every node has 0 or 2 children).

    A full binary tree must have an odd number of nodes (n = 2k + 1).
    Even counts are adjusted to the nearest smaller odd number (or 1).
    """
    clamped_n = validate_and_clamp_n(n, label_type)
    if clamped_n % 2 == 0:
        clamped_n = max(1, clamped_n - 1)

    labels = get_random_labels(clamped_n, label_type)
    root = TreeNode(labels[0])

    if clamped_n == 1:
        return root

    leaves: List[TreeNode] = [root]
    idx = 1

    while idx < clamped_n and leaves:
        leaf = random.choice(leaves)
        leaves.remove(leaf)

        left_node = TreeNode(labels[idx])
        right_node = TreeNode(labels[idx + 1])
        idx += 2

        leaf.left = left_node
        leaf.right = right_node

        leaves.append(left_node)
        leaves.append(right_node)

    return root


def generate_random_bst(n: int, label_type: str = "numbers") -> BinarySearchTree:
    """Generate a random BST with n unique keys."""
    clamped_n = validate_and_clamp_n(n, label_type)
    labels = get_random_labels(clamped_n, label_type)
    bst = BinarySearchTree()
    for label in labels:
        bst.insert(label)
    return bst


def generate_traversal_pair(
    mode: str,
    n: int = 7,
    labels: str = "letters",
) -> Tuple[List[Any], Optional[List[Any]]]:
    """Generate valid, reconstructible traversal sequences for any given mode.

    For pre+post mode, generates a Full Binary Tree with an odd number of nodes.
    Returns:
        (seq1, seq2) for 2-sequence modes, or (seq1, None) for single-sequence BST modes.
    """
    clamped_n = validate_and_clamp_n(n, labels)

    if mode in {"in+pre", "in+post", "in+level"}:
        root = generate_random_binary_tree(clamped_n, labels)
        in_seq = inorder_recursive(root)
        if mode == "in+pre":
            return in_seq, preorder_recursive(root)
        elif mode == "in+post":
            return in_seq, postorder_recursive(root)
        else:
            return in_seq, level_order(root)

    elif mode == "pre+post":
        # Pre+post requires full binary tree with odd node count
        root = generate_random_full_binary_tree(clamped_n, labels)
        return preorder_recursive(root), postorder_recursive(root)

    elif mode == "bst-pre":
        bst = generate_random_bst(clamped_n, labels)
        assert bst.root is not None
        return preorder_recursive(bst.root), None

    elif mode == "bst-post":
        bst = generate_random_bst(clamped_n, labels)
        assert bst.root is not None
        return postorder_recursive(bst.root), None

    else:
        raise ValueError(f"Unknown reconstruction mode: '{mode}'")
