"""TreeNode model with frequency-based duplicate handling and unique node identifiers.

Complexity:
- TreeNode initialization, property access: O(1) time, O(1) space.
- Serialization and cloning: O(n) time, O(h) space where h is tree height.
"""
from __future__ import annotations

import itertools
from typing import Any, Dict, Optional

_NODE_ID_COUNTER = itertools.count(1)


def generate_node_id() -> str:
    """Generate a unique sequential string identifier for visualizer nodes."""
    return f"node_{next(_NODE_ID_COUNTER)}"


def reset_node_id_counter() -> None:
    """Reset the node ID counter (primarily for deterministic unit testing)."""
    global _NODE_ID_COUNTER
    _NODE_ID_COUNTER = itertools.count(1)


class TreeNode:
    """Represents a node in a binary tree or binary search tree.

    Attributes:
        val: Node value (opaque label: number or letter).
        freq: Frequency or occurrence count for duplicate handling (default 1).
        left: Reference to left child TreeNode.
        right: Reference to right child TreeNode.
        node_id: Unique string identifier for animation frame tracking.
    """

    def __init__(
        self,
        val: Any,
        left: Optional[TreeNode] = None,
        right: Optional[TreeNode] = None,
        node_id: Optional[str] = None,
        freq: int = 1,
    ) -> None:
        self.val: Any = val
        self.freq: int = freq
        self.left: Optional[TreeNode] = left
        self.right: Optional[TreeNode] = right
        self.node_id: str = node_id if node_id is not None else generate_node_id()

    @property
    def value(self) -> Any:
        """Alias for val."""
        return self.val

    @value.setter
    def value(self, new_val: Any) -> None:
        self.val = new_val

    def to_dict(self) -> Dict[str, Any]:
        """Serialize tree node into a dictionary matching visualizer step schema.

        Time Complexity: O(n) where n is size of subtree.
        Space Complexity: O(h) recursion stack.
        """
        return {
            "id": self.node_id,
            "value": self.val,
            "val": self.val,
            "freq": self.freq,
            "left": self.left.to_dict() if self.left is not None else None,
            "right": self.right.to_dict() if self.right is not None else None,
        }

    def clone(self) -> TreeNode:
        """Create a deep copy of the subtree preserving values, frequencies, and IDs.

        Time Complexity: O(n) where n is size of subtree.
        Space Complexity: O(h) call stack.
        """
        cloned = TreeNode(
            val=self.val,
            node_id=self.node_id,
            freq=self.freq,
        )
        if self.left is not None:
            cloned.left = self.left.clone()
        if self.right is not None:
            cloned.right = self.right.clone()
        return cloned

    def is_leaf(self) -> bool:
        """Return True if this node has no children."""
        return self.left is None and self.right is None

    def __eq__(self, other: Any) -> bool:
        """Structural and value equality comparison."""
        if not isinstance(other, TreeNode):
            return False
        return (
            self.val == other.val
            and self.freq == other.freq
            and self.left == other.left
            and self.right == other.right
        )

    def __repr__(self) -> str:
        freq_str = f" x{self.freq}" if self.freq > 1 else ""
        return f"TreeNode({self.val}{freq_str}, id={self.node_id})"
