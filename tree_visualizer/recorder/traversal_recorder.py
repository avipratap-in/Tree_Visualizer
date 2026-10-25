"""Step recorder for binary tree traversals (preorder, inorder, postorder, level-order).

Captures progressive node visits, growing visited sequence, and traversal edges.
Returns (pseudocode lines, list of Step objects).
"""
from __future__ import annotations

from collections import deque
from typing import Any, List, Optional, Tuple
from tree_visualizer.core.node import TreeNode
from tree_visualizer.recorder.steps import Step, StepRecorder


def record_preorder(root: Optional[TreeNode]) -> Tuple[List[str], List[Step]]:
    """Record step-by-step preorder traversal (Root -> Left -> Right)."""
    pseudocode = [
        "if curr is null: return",
        "visit curr node (append to visited)",
        "traverse left subtree",
        "traverse right subtree",
    ]
    recorder = StepRecorder(operation="preorder", pseudocode=pseudocode)

    if root is None:
        recorder.record_step(
            tree_root=None,
            visited=[],
            message="Tree is empty. Preorder traversal is empty.",
            pseudo_line=0,
        )
        return recorder.pseudocode, recorder.steps

    visited: List[Any] = []

    def _traverse(node: Optional[TreeNode], parent: Optional[TreeNode]) -> None:
        if node is None:
            return

        # Visit current node
        visited.append(node.val)
        h_edges = [(parent.node_id, node.node_id)] if parent else []
        recorder.record_step(
            tree_root=root,
            highlight_nodes=[node.node_id],
            highlight_edges=h_edges,
            visited=list(visited),
            message=f"Visiting node {node.val}. Appended to visited sequence.",
            pseudo_line=1,
        )

        # Traverse left
        if node.left is not None:
            recorder.record_step(
                tree_root=root,
                highlight_nodes=[node.node_id],
                highlight_edges=[(node.node_id, node.left.node_id)],
                visited=list(visited),
                message=f"Moving to left child of {node.val}.",
                pseudo_line=2,
            )
        _traverse(node.left, node)

        # Traverse right
        if node.right is not None:
            recorder.record_step(
                tree_root=root,
                highlight_nodes=[node.node_id],
                highlight_edges=[(node.node_id, node.right.node_id)],
                visited=list(visited),
                message=f"Moving to right child of {node.val}.",
                pseudo_line=3,
            )
        _traverse(node.right, node)

    _traverse(root, None)

    recorder.record_step(
        tree_root=root,
        highlight_nodes=[],
        visited=list(visited),
        message=f"Preorder traversal complete: {visited}.",
        pseudo_line=1,
    )
    return recorder.pseudocode, recorder.steps


def record_inorder(root: Optional[TreeNode]) -> Tuple[List[str], List[Step]]:
    """Record step-by-step inorder traversal (Left -> Root -> Right)."""
    pseudocode = [
        "if curr is null: return",
        "traverse left subtree",
        "visit curr node (append to visited)",
        "traverse right subtree",
    ]
    recorder = StepRecorder(operation="inorder", pseudocode=pseudocode)

    if root is None:
        recorder.record_step(
            tree_root=None,
            visited=[],
            message="Tree is empty. Inorder traversal is empty.",
            pseudo_line=0,
        )
        return recorder.pseudocode, recorder.steps

    visited: List[Any] = []

    def _traverse(node: Optional[TreeNode], parent: Optional[TreeNode]) -> None:
        if node is None:
            return

        # Traverse left
        if node.left is not None:
            recorder.record_step(
                tree_root=root,
                highlight_nodes=[node.node_id],
                highlight_edges=[(node.node_id, node.left.node_id)],
                visited=list(visited),
                message=f"Traversing to left child of {node.val}.",
                pseudo_line=1,
            )
        _traverse(node.left, node)

        # Visit current
        visited.append(node.val)
        h_edges = [(parent.node_id, node.node_id)] if parent else []
        recorder.record_step(
            tree_root=root,
            highlight_nodes=[node.node_id],
            highlight_edges=h_edges,
            visited=list(visited),
            message=f"Visiting node {node.val}. Appended to visited sequence.",
            pseudo_line=2,
        )

        # Traverse right
        if node.right is not None:
            recorder.record_step(
                tree_root=root,
                highlight_nodes=[node.node_id],
                highlight_edges=[(node.node_id, node.right.node_id)],
                visited=list(visited),
                message=f"Traversing to right child of {node.val}.",
                pseudo_line=3,
            )
        _traverse(node.right, node)

    _traverse(root, None)

    recorder.record_step(
        tree_root=root,
        highlight_nodes=[],
        visited=list(visited),
        message=f"Inorder traversal complete: {visited}.",
        pseudo_line=2,
    )
    return recorder.pseudocode, recorder.steps


def record_postorder(root: Optional[TreeNode]) -> Tuple[List[str], List[Step]]:
    """Record step-by-step postorder traversal (Left -> Right -> Root)."""
    pseudocode = [
        "if curr is null: return",
        "traverse left subtree",
        "traverse right subtree",
        "visit curr node (append to visited)",
    ]
    recorder = StepRecorder(operation="postorder", pseudocode=pseudocode)

    if root is None:
        recorder.record_step(
            tree_root=None,
            visited=[],
            message="Tree is empty. Postorder traversal is empty.",
            pseudo_line=0,
        )
        return recorder.pseudocode, recorder.steps

    visited: List[Any] = []

    def _traverse(node: Optional[TreeNode], parent: Optional[TreeNode]) -> None:
        if node is None:
            return

        # Traverse left
        if node.left is not None:
            recorder.record_step(
                tree_root=root,
                highlight_nodes=[node.node_id],
                highlight_edges=[(node.node_id, node.left.node_id)],
                visited=list(visited),
                message=f"Traversing to left child of {node.val}.",
                pseudo_line=1,
            )
        _traverse(node.left, node)

        # Traverse right
        if node.right is not None:
            recorder.record_step(
                tree_root=root,
                highlight_nodes=[node.node_id],
                highlight_edges=[(node.node_id, node.right.node_id)],
                visited=list(visited),
                message=f"Traversing to right child of {node.val}.",
                pseudo_line=2,
            )
        _traverse(node.right, node)

        # Visit current
        visited.append(node.val)
        h_edges = [(parent.node_id, node.node_id)] if parent else []
        recorder.record_step(
            tree_root=root,
            highlight_nodes=[node.node_id],
            highlight_edges=h_edges,
            visited=list(visited),
            message=f"Visiting node {node.val}. Appended to visited sequence.",
            pseudo_line=3,
        )

    _traverse(root, None)

    recorder.record_step(
        tree_root=root,
        highlight_nodes=[],
        visited=list(visited),
        message=f"Postorder traversal complete: {visited}.",
        pseudo_line=3,
    )
    return recorder.pseudocode, recorder.steps


def record_level_order(root: Optional[TreeNode]) -> Tuple[List[str], List[Step]]:
    """Record step-by-step level-order (breadth-first) traversal."""
    pseudocode = [
        "if root is null: return",
        "queue = [root]",
        "while queue is not empty:",
        "  curr = queue.popleft(), visit curr",
        "  enqueue curr.left, enqueue curr.right",
    ]
    recorder = StepRecorder(operation="level_order", pseudocode=pseudocode)

    if root is None:
        recorder.record_step(
            tree_root=None,
            visited=[],
            message="Tree is empty. Level order traversal is empty.",
            pseudo_line=0,
        )
        return recorder.pseudocode, recorder.steps

    visited: List[Any] = []
    queue: deque[TreeNode] = deque([root])

    recorder.record_step(
        tree_root=root,
        highlight_nodes=[root.node_id],
        visited=list(visited),
        message=f"Initialized BFS queue with root {root.val}.",
        pseudo_line=1,
    )

    while queue:
        curr = queue.popleft()
        visited.append(curr.val)

        recorder.record_step(
            tree_root=root,
            highlight_nodes=[curr.node_id],
            visited=list(visited),
            message=f"Popped node {curr.val} from queue. Appended to visited sequence.",
            pseudo_line=3,
        )

        if curr.left is not None:
            queue.append(curr.left)
            recorder.record_step(
                tree_root=root,
                highlight_nodes=[curr.node_id, curr.left.node_id],
                highlight_edges=[(curr.node_id, curr.left.node_id)],
                visited=list(visited),
                message=f"Enqueued left child {curr.left.val} of node {curr.val}.",
                pseudo_line=4,
            )

        if curr.right is not None:
            queue.append(curr.right)
            recorder.record_step(
                tree_root=root,
                highlight_nodes=[curr.node_id, curr.right.node_id],
                highlight_edges=[(curr.node_id, curr.right.node_id)],
                visited=list(visited),
                message=f"Enqueued right child {curr.right.val} of node {curr.val}.",
                pseudo_line=4,
            )

    recorder.record_step(
        tree_root=root,
        highlight_nodes=[],
        visited=list(visited),
        message=f"Level-order traversal complete: {visited}.",
        pseudo_line=3,
    )
    return recorder.pseudocode, recorder.steps
