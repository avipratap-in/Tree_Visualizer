"""Binary Search Tree (BST) implementation with frequency-based duplicate handling.

Duplicate keys increment the node frequency counter (`freq`), maintaining
the strict BST ordering property:
    left.val < node.val < right.val

Time Complexity:
- Search, Insert, Remove, Min, Max, Predecessor, Successor, Rank, Select:
  - Average: O(log n)
  - Worst (skewed tree): O(n)
- Size, Height, is_valid_bst, create_from_array:
  - O(n) or O(n * h)

Space Complexity:
- O(h) recursion stack (or O(1) iterative).
"""
from __future__ import annotations

from typing import Any, Iterable, List, Optional
from tree_visualizer.core.comparison import compare_bst_keys, is_numeric_value
from tree_visualizer.core.exceptions import MixedTypesError
from tree_visualizer.core.node import TreeNode


class BinarySearchTree:
    """Pure Binary Search Tree with frequency-based duplicate handling and strict comparisons."""

    def __init__(self, root: Optional[TreeNode] = None) -> None:
        self.root: Optional[TreeNode] = root

    def insert(self, val: Any) -> TreeNode:
        """Insert a value into the BST.

        If the value already exists, increments its frequency counter.
        Returns the inserted or updated TreeNode.

        Time Complexity: O(h) where h is tree height.
        Space Complexity: O(h) recursion stack.
        """
        if self.root is None:
            self.root = TreeNode(val)
            return self.root

        # Ensure consistent type regime with existing tree
        if is_numeric_value(val) != is_numeric_value(self.root.val):
            raise MixedTypesError(
                f"Cannot insert {'numeric' if is_numeric_value(val) else 'alphabetic'} value '{val}' "
                f"into a BST containing {'numeric' if is_numeric_value(self.root.val) else 'alphabetic'} keys."
            )

        def _insert(node: TreeNode) -> TreeNode:
            cmp = compare_bst_keys(val, node.val)
            if cmp == 0:
                node.freq += 1
                return node
            elif cmp < 0:
                if node.left is None:
                    node.left = TreeNode(val)
                    return node.left
                return _insert(node.left)
            else:
                if node.right is None:
                    node.right = TreeNode(val)
                    return node.right
                return _insert(node.right)

        return _insert(self.root)

    def search(self, val: Any) -> Optional[TreeNode]:
        """Search for a value in the BST.

        Returns matching TreeNode if found, else None.

        Time Complexity: O(h).
        Space Complexity: O(1) iterative.
        """
        curr = self.root
        while curr is not None:
            cmp = compare_bst_keys(val, curr.val)
            if cmp == 0:
                return curr
            elif cmp < 0:
                curr = curr.left
            else:
                curr = curr.right
        return None

    def remove(self, val: Any) -> bool:
        """Remove a value from the BST.

        If freq > 1: decrements freq and returns True.
        If freq == 1: structurally removes the node (leaf, 1 child, or 2 children via successor).
        Returns True if removed/decremented, False if not found.

        Time Complexity: O(h).
        Space Complexity: O(h) recursion stack.
        """
        target = self.search(val)
        if target is None:
            return False

        if target.freq > 1:
            target.freq -= 1
            return True

        self.root = self._delete_node(self.root, val)
        return True

    def _delete_node(self, node: Optional[TreeNode], val: Any) -> Optional[TreeNode]:
        """Physically delete the node containing val."""
        if node is None:
            return None

        cmp = compare_bst_keys(val, node.val)
        if cmp < 0:
            node.left = self._delete_node(node.left, val)
            return node
        elif cmp > 0:
            node.right = self._delete_node(node.right, val)
            return node
        else:
            # Case 1: Leaf node (no children)
            if node.left is None and node.right is None:
                return None

            # Case 2: Exactly one child
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left

            # Case 3: Two children -> find inorder successor
            succ = self._min_node(node.right)
            assert succ is not None
            node.val = succ.val
            node.freq = succ.freq
            # Completely remove successor from right subtree
            node.right = self._delete_node_completely(node.right, succ.val)
            return node

    def _delete_node_completely(self, node: Optional[TreeNode], val: Any) -> Optional[TreeNode]:
        """Remove a node regardless of frequency (used for successor deletion)."""
        if node is None:
            return None

        cmp = compare_bst_keys(val, node.val)
        if cmp < 0:
            node.left = self._delete_node_completely(node.left, val)
            return node
        elif cmp > 0:
            node.right = self._delete_node_completely(node.right, val)
            return node
        else:
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left
            succ = self._min_node(node.right)
            assert succ is not None
            node.val = succ.val
            node.freq = succ.freq
            node.right = self._delete_node_completely(node.right, succ.val)
            return node

    def min(self) -> Optional[Any]:
        """Return minimum value in BST, or None if tree is empty.

        Time Complexity: O(h).
        Space Complexity: O(1).
        """
        min_n = self._min_node(self.root)
        return min_n.val if min_n is not None else None

    def _min_node(self, node: Optional[TreeNode]) -> Optional[TreeNode]:
        if node is None:
            return None
        curr = node
        while curr.left is not None:
            curr = curr.left
        return curr

    def max(self) -> Optional[Any]:
        """Return maximum value in BST, or None if tree is empty.

        Time Complexity: O(h).
        Space Complexity: O(1).
        """
        max_n = self._max_node(self.root)
        return max_n.val if max_n is not None else None

    def _max_node(self, node: Optional[TreeNode]) -> Optional[TreeNode]:
        if node is None:
            return None
        curr = node
        while curr.right is not None:
            curr = curr.right
        return curr

    def predecessor(self, val: Any) -> Optional[Any]:
        """Find the inorder predecessor (largest value strictly less than val).

        Time Complexity: O(h).
        Space Complexity: O(1).
        """
        curr = self.root
        pred: Optional[TreeNode] = None

        while curr is not None:
            cmp = compare_bst_keys(val, curr.val)
            if cmp <= 0:
                curr = curr.left
            else:
                pred = curr
                curr = curr.right

        return pred.val if pred is not None else None

    def successor(self, val: Any) -> Optional[Any]:
        """Find the inorder successor (smallest value strictly greater than val).

        Time Complexity: O(h).
        Space Complexity: O(1).
        """
        curr = self.root
        succ: Optional[TreeNode] = None

        while curr is not None:
            cmp = compare_bst_keys(val, curr.val)
            if cmp >= 0:
                curr = curr.right
            else:
                succ = curr
                curr = curr.left

        return succ.val if succ is not None else None

    def _total_count(self, node: Optional[TreeNode]) -> int:
        """Count total items in subtree including duplicate frequencies."""
        if node is None:
            return 0
        return node.freq + self._total_count(node.left) + self._total_count(node.right)

    def rank(self, val: Any) -> int:
        """Return the count of elements in the BST strictly less than val.

        Accounts for duplicate node frequencies.

        Time Complexity: O(h).
        Space Complexity: O(h).
        """
        def _rank(node: Optional[TreeNode]) -> int:
            if node is None:
                return 0
            cmp = compare_bst_keys(val, node.val)
            if cmp < 0:
                return _rank(node.left)
            elif cmp > 0:
                left_cnt = self._total_count(node.left)
                return left_cnt + node.freq + _rank(node.right)
            else:
                return self._total_count(node.left)

        return _rank(self.root)

    def select(self, k: int) -> Optional[Any]:
        """Return the k-th smallest element in the BST (1-indexed).

        Accounts for duplicate node frequencies.
        Returns None if k < 1 or k > total elements.

        Time Complexity: O(h).
        Space Complexity: O(h).
        """
        total = self.size(include_duplicates=True)
        if k < 1 or k > total:
            return None

        def _select(node: Optional[TreeNode], target_k: int) -> Optional[Any]:
            if node is None:
                return None
            left_count = self._total_count(node.left)

            if target_k <= left_count:
                return _select(node.left, target_k)
            elif target_k <= left_count + node.freq:
                return node.val
            else:
                return _select(node.right, target_k - left_count - node.freq)

        return _select(self.root, k)

    def size(self, include_duplicates: bool = True) -> int:
        """Return number of elements in the BST.

        If include_duplicates is True, sums frequencies;
        if False, counts distinct nodes.

        Time Complexity: O(n).
        Space Complexity: O(h).
        """
        def _size(node: Optional[TreeNode]) -> int:
            if node is None:
                return 0
            cnt = node.freq if include_duplicates else 1
            return cnt + _size(node.left) + _size(node.right)

        return _size(self.root)

    def height(self) -> int:
        """Return height of BST (0 if empty, 1 for single node).

        Time Complexity: O(n).
        Space Complexity: O(h).
        """
        def _height(node: Optional[TreeNode]) -> int:
            if node is None:
                return 0
            return 1 + max(_height(node.left), _height(node.right))

        return _height(self.root)

    @classmethod
    def create_from_array(cls, arr: Iterable[Any]) -> BinarySearchTree:
        """Build a BST by inserting elements from an iterable in order.

        Time Complexity: O(n * h).
        Space Complexity: O(n).
        """
        tree = cls()
        for item in arr:
            tree.insert(item)
        return tree

    def is_valid_bst(self) -> bool:
        """Verify that the strict BST property holds for all nodes.

        Since duplicates are handled via node.freq, left.val < node.val < right.val.

        Time Complexity: O(n).
        Space Complexity: O(h).
        """
        def _validate(node: Optional[TreeNode], min_val: Any, max_val: Any) -> bool:
            if node is None:
                return True
            if min_val is not None and compare_bst_keys(node.val, min_val) <= 0:
                return False
            if max_val is not None and compare_bst_keys(node.val, max_val) >= 0:
                return False
            return _validate(node.left, min_val, node.val) and _validate(node.right, node.val, max_val)

        return _validate(self.root, None, None)

    def is_empty(self) -> bool:
        """Return True if BST is empty."""
        return self.root is None

    def __repr__(self) -> str:
        return f"BinarySearchTree(root={self.root!r})"
