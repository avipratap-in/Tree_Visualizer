"""Tree property calculations and validations.

Calculates:
- leaf_count: Number of nodes with 0 children.
- internal_node_count: Number of nodes with at least 1 child.
- height: Maximum path depth from root to leaf (0 for empty tree, 1 for single node).
- is_full: True if every node has 0 or 2 children.
- is_complete: True if all levels are completely filled except possibly the last,
  which is filled from left to right.
- is_perfect: True if all internal nodes have 2 children and all leaves are at same depth (n = 2^h - 1).
- is_balanced: True if for every node, |height(left) - height(right)| <= 1 (AVL condition).

Time Complexity: O(n) for each calculation.
Space Complexity: O(h) recursion stack / O(w) queue.
"""
from __future__ import annotations

from collections import deque
from typing import Any, Dict, Optional
from tree_visualizer.core.node import TreeNode


def height(root: Optional[TreeNode]) -> int:
    """Calculate height of binary tree (0 for empty tree, 1 for single root).

    Time Complexity: O(n)
    Space Complexity: O(h)
    """
    if root is None:
        return 0
    return 1 + max(height(root.left), height(root.right))


def size(root: Optional[TreeNode]) -> int:
    """Count total number of nodes in binary tree.

    Time Complexity: O(n)
    Space Complexity: O(h)
    """
    if root is None:
        return 0
    return 1 + size(root.left) + size(root.right)


def leaf_count(root: Optional[TreeNode]) -> int:
    """Count number of leaf nodes (nodes with 0 children).

    Time Complexity: O(n)
    Space Complexity: O(h)
    """
    if root is None:
        return 0
    if root.left is None and root.right is None:
        return 1
    return leaf_count(root.left) + leaf_count(root.right)


def internal_node_count(root: Optional[TreeNode]) -> int:
    """Count number of internal nodes (nodes with at least one child).

    Time Complexity: O(n)
    Space Complexity: O(h)
    """
    if root is None or (root.left is None and root.right is None):
        return 0
    return 1 + internal_node_count(root.left) + internal_node_count(root.right)


def is_full(root: Optional[TreeNode]) -> bool:
    """Check if tree is a full binary tree (every node has 0 or 2 children).

    An empty tree or single node tree is full.

    Time Complexity: O(n)
    Space Complexity: O(h)
    """
    if root is None:
        return True
    if root.left is None and root.right is None:
        return True
    if root.left is not None and root.right is not None:
        return is_full(root.left) and is_full(root.right)
    return False


def is_complete(root: Optional[TreeNode]) -> bool:
    """Check if tree is a complete binary tree using level-order traversal.

    All levels are completely filled except possibly the last level,
    which is filled strictly from left to right.

    Time Complexity: O(n)
    Space Complexity: O(w) where w is maximum width of tree
    """
    if root is None:
        return True

    queue: deque[Optional[TreeNode]] = deque([root])
    seen_none = False

    while queue:
        curr = queue.popleft()
        if curr is None:
            seen_none = True
        else:
            if seen_none:
                # Found a non-null node after a null node in level-order traversal
                return False
            queue.append(curr.left)
            queue.append(curr.right)

    return True


def is_perfect(root: Optional[TreeNode]) -> bool:
    """Check if tree is a perfect binary tree.

    A perfect tree has all leaves at the same depth and all internal nodes have 2 children.
    Satisfies size n == 2^h - 1.

    Time Complexity: O(n)
    Space Complexity: O(h)
    """
    if root is None:
        return True

    h = height(root)
    n = size(root)
    return n == (2 ** h) - 1


def is_balanced(root: Optional[TreeNode]) -> bool:
    """Check if tree is height-balanced (AVL condition).

    For every node, the height difference between left and right subtrees is at most 1.

    Time Complexity: O(n)
    Space Complexity: O(h)
    """
    def _check(node: Optional[TreeNode]) -> tuple[bool, int]:
        if node is None:
            return True, 0

        left_bal, left_h = _check(node.left)
        if not left_bal:
            return False, 0

        right_bal, right_h = _check(node.right)
        if not right_bal:
            return False, 0

        bal = abs(left_h - right_h) <= 1
        cur_h = 1 + max(left_h, right_h)
        return bal, cur_h

    balanced, _ = _check(root)
    return balanced


def compute_properties(root: Optional[TreeNode]) -> Dict[str, Any]:
    """Compute and return all tree properties in a dictionary.

    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    return {
        "leaves": leaf_count(root),
        "internal": internal_node_count(root),
        "height": height(root),
        "is_full": is_full(root),
        "is_complete": is_complete(root),
        "is_perfect": is_perfect(root),
        "is_balanced": is_balanced(root),
    }
