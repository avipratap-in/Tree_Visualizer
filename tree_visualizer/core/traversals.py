"""Binary tree traversal algorithms.

Provides both recursive and iterative (explicit stack / deque) implementations
for preorder, inorder, postorder, and level-order traversals.

Time Complexity:
- O(n) for all traversals (each node is visited a constant number of times).

Space Complexity:
- O(h) for preorder, inorder, and postorder (stack depth bounded by tree height).
- O(w) for level_order (queue size bounded by tree maximum level width).
"""
from __future__ import annotations

from collections import deque
from typing import Any, List, Optional
from tree_visualizer.core.node import TreeNode


def preorder_recursive(root: Optional[TreeNode]) -> List[Any]:
    """Preorder traversal (Root -> Left -> Right) using recursion.

    Time Complexity: O(n)
    Space Complexity: O(h) recursion stack
    """
    result: List[Any] = []

    def _traverse(node: Optional[TreeNode]) -> None:
        if node is None:
            return
        result.append(node.val)
        _traverse(node.left)
        _traverse(node.right)

    _traverse(root)
    return result


def preorder_iterative(root: Optional[TreeNode]) -> List[Any]:
    """Preorder traversal (Root -> Left -> Right) using an explicit stack.

    Time Complexity: O(n)
    Space Complexity: O(h) explicit stack
    """
    if root is None:
        return []

    result: List[Any] = []
    stack: List[TreeNode] = [root]

    while stack:
        curr = stack.pop()
        result.append(curr.val)
        # Push right child first so left child is popped and processed first
        if curr.right is not None:
            stack.append(curr.right)
        if curr.left is not None:
            stack.append(curr.left)

    return result


def inorder_recursive(root: Optional[TreeNode]) -> List[Any]:
    """Inorder traversal (Left -> Root -> Right) using recursion.

    Time Complexity: O(n)
    Space Complexity: O(h) recursion stack
    """
    result: List[Any] = []

    def _traverse(node: Optional[TreeNode]) -> None:
        if node is None:
            return
        _traverse(node.left)
        result.append(node.val)
        _traverse(node.right)

    _traverse(root)
    return result


def inorder_iterative(root: Optional[TreeNode]) -> List[Any]:
    """Inorder traversal (Left -> Root -> Right) using an explicit stack.

    Time Complexity: O(n)
    Space Complexity: O(h) explicit stack
    """
    result: List[Any] = []
    stack: List[TreeNode] = []
    curr: Optional[TreeNode] = root

    while curr is not None or stack:
        while curr is not None:
            stack.append(curr)
            curr = curr.left

        curr = stack.pop()
        result.append(curr.val)
        curr = curr.right

    return result


def postorder_recursive(root: Optional[TreeNode]) -> List[Any]:
    """Postorder traversal (Left -> Right -> Root) using recursion.

    Time Complexity: O(n)
    Space Complexity: O(h) recursion stack
    """
    result: List[Any] = []

    def _traverse(node: Optional[TreeNode]) -> None:
        if node is None:
            return
        _traverse(node.left)
        _traverse(node.right)
        result.append(node.val)

    _traverse(root)
    return result


def postorder_iterative(root: Optional[TreeNode]) -> List[Any]:
    """Postorder traversal (Left -> Right -> Root) using an explicit stack.

    Time Complexity: O(n)
    Space Complexity: O(h) explicit stack
    """
    if root is None:
        return []

    result: List[Any] = []
    stack: List[TreeNode] = []
    curr: Optional[TreeNode] = root
    last_visited: Optional[TreeNode] = None

    while curr is not None or stack:
        if curr is not None:
            stack.append(curr)
            curr = curr.left
        else:
            peek = stack[-1]
            if peek.right is not None and last_visited != peek.right:
                curr = peek.right
            else:
                result.append(peek.val)
                last_visited = stack.pop()

    return result


def level_order(root: Optional[TreeNode]) -> List[Any]:
    """Level-order (breadth-first) traversal using collections.deque.

    Time Complexity: O(n)
    Space Complexity: O(w) queue where w is maximum width of tree
    """
    if root is None:
        return []

    result: List[Any] = []
    queue: deque[TreeNode] = deque([root])

    while queue:
        curr = queue.popleft()
        result.append(curr.val)
        if curr.left is not None:
            queue.append(curr.left)
        if curr.right is not None:
            queue.append(curr.right)

    return result
