"""BinaryTree wrapper and level-order construction.

Complexity:
- Initialization: O(1) time, O(1) space.
- Construction from level-order list: O(n) time, O(n) space.
- Level-order serialization: O(n) time, O(n) space.
"""
from __future__ import annotations

from collections import deque
from typing import Any, List, Optional
from tree_visualizer.core.node import TreeNode


class BinaryTree:
    """General Binary Tree wrapper providing structural algorithms and conversions."""

    def __init__(self, root: Optional[TreeNode] = None) -> None:
        self.root: Optional[TreeNode] = root

    @classmethod
    def from_level_order(cls, values: List[Optional[Any]]) -> BinaryTree:
        """Construct a binary tree from a level-order list representation.

        None, 'null', '-', or '.' represent missing/null child positions.

        Time Complexity: O(n) where n is length of values.
        Space Complexity: O(n) for queue and created nodes.
        """
        if not values:
            return cls(None)

        first_val = values[0]
        if first_val is None or str(first_val).lower() in ("null", "none", "-", "."):
            return cls(None)

        root = TreeNode(first_val)
        queue: deque[TreeNode] = deque([root])
        idx = 1
        n = len(values)

        def _is_null_placeholder(v: Any) -> bool:
            if v is None:
                return True
            if isinstance(v, str) and v.strip().lower() in ("null", "none", "-", "."):
                return True
            return False

        while queue and idx < n:
            curr = queue.popleft()

            # Left child
            if idx < n:
                left_val = values[idx]
                idx += 1
                if not _is_null_placeholder(left_val):
                    curr.left = TreeNode(left_val)
                    queue.append(curr.left)

            # Right child
            if idx < n:
                right_val = values[idx]
                idx += 1
                if not _is_null_placeholder(right_val):
                    curr.right = TreeNode(right_val)
                    queue.append(curr.right)

        return cls(root)

    def to_level_order(self) -> List[Optional[Any]]:
        """Return level-order list of values with trailing Nones trimmed.

        Time Complexity: O(n).
        Space Complexity: O(n).
        """
        if self.root is None:
            return []

        res: List[Optional[Any]] = []
        queue: deque[Optional[TreeNode]] = deque([self.root])

        while queue:
            curr = queue.popleft()
            if curr is not None:
                res.append(curr.val)
                queue.append(curr.left)
                queue.append(curr.right)
            else:
                res.append(None)

        # Trim trailing Nones
        while res and res[-1] is None:
            res.pop()
        return res

    def size(self) -> int:
        """Return total number of nodes in the binary tree.

        Time Complexity: O(n).
        Space Complexity: O(h) recursion stack.
        """
        def _size(node: Optional[TreeNode]) -> int:
            if node is None:
                return 0
            return 1 + _size(node.left) + _size(node.right)

        return _size(self.root)

    def height(self) -> int:
        """Return tree height (0 for empty tree, 1 for single root node).

        Time Complexity: O(n).
        Space Complexity: O(h) recursion stack.
        """
        def _height(node: Optional[TreeNode]) -> int:
            if node is None:
                return 0
            return 1 + max(_height(node.left), _height(node.right))

        return _height(self.root)

    def is_empty(self) -> bool:
        """Return True if the tree has no root node."""
        return self.root is None

    def clone(self) -> BinaryTree:
        """Return a deep copy of the tree."""
        return BinaryTree(self.root.clone() if self.root is not None else None)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, BinaryTree):
            return False
        return self.root == other.root

    def __repr__(self) -> str:
        return f"BinaryTree(root={self.root!r})"
