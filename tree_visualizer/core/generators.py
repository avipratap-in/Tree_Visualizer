"""Random tree generators for testing and visualization presets.

Generates random binary trees (general, full binary trees, and BSTs)
with either alphabetical labels (A-Z) or numeric labels (1-99).
"""
from __future__ import annotations

import random
from typing import Any, List, Optional
from tree_visualizer.core.bst import BinarySearchTree
from tree_visualizer.core.node import TreeNode


def get_random_labels(n: int, label_type: str = "letters") -> List[Any]:
    """Generate n unique labels: either letters (A-Z) or numbers (1-99)."""
    if label_type == "numbers":
        pool = list(range(1, 100))
        if n > len(pool):
            pool = list(range(1, n + 50))
        return random.sample(pool, n)
    else:
        # Letters A-Z (or extended e.g. AA, AB if n > 26)
        alphabet = [chr(c) for c in range(ord("A"), ord("Z") + 1)]
        if n <= 26:
            return random.sample(alphabet, n)
        else:
            extended = list(alphabet)
            for c1 in alphabet:
                for c2 in alphabet:
                    extended.append(f"{c1}{c2}")
                    if len(extended) >= n:
                        break
                if len(extended) >= n:
                    break
            return random.sample(extended, n)


def generate_random_binary_tree(n: int, label_type: str = "letters") -> TreeNode:
    """Generate a random connected binary tree with n nodes."""
    if n <= 0:
        raise ValueError("Node count n must be positive.")

    labels = get_random_labels(n, label_type)
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

    A full binary tree must have an odd number of nodes.
    If an even n is provided, n is adjusted to n - 1 (or 1 if n <= 2).
    """
    if n <= 0:
        raise ValueError("Node count n must be positive.")

    # Full binary trees always have odd node counts
    if n % 2 == 0:
        n = max(1, n - 1)

    labels = get_random_labels(n, label_type)
    root = TreeNode(labels[0])

    if n == 1:
        return root

    leaves: List[TreeNode] = [root]
    idx = 1

    while idx < n:
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
    if n <= 0:
        return BinarySearchTree(None)

    labels = get_random_labels(n, label_type)
    bst = BinarySearchTree()
    for lab in labels:
        bst.insert(lab)
    return bst
