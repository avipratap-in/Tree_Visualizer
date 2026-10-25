"""Step recorder for tree reconstruction algorithms.

Visualizes root selection, partition splits, and recursive subtree construction.
Returns (pseudocode lines, list of Step objects).
"""
from __future__ import annotations

from typing import Any, List, Optional, Tuple
from tree_visualizer.core.builders import (
    AmbiguousTreeError,
    TreeBuildError,
    _validate_sequences,
)
from tree_visualizer.core.comparison import compare_bst_keys, validate_consistent_types
from tree_visualizer.core.exceptions import DuplicateValueError
from tree_visualizer.core.node import TreeNode
from tree_visualizer.recorder.steps import Step, StepRecorder


def record_build_inorder_preorder(
    inorder: List[Any],
    preorder: List[Any],
) -> Tuple[List[str], List[Step]]:
    """Record step-by-step reconstruction from Inorder + Preorder."""
    _validate_sequences(inorder, preorder, "inorder", "preorder", require_unique=True)

    pseudocode = [
        "pick root value from preorder sequence",
        "find root position in inorder sequence",
        "split inorder into left & right subtrees",
        "recursively construct left subtree",
        "recursively construct right subtree",
    ]
    recorder = StepRecorder(operation="build_inorder_preorder", pseudocode=pseudocode)

    if not inorder:
        recorder.record_step(
            tree_root=None,
            message="Empty traversal sequences. Tree is empty.",
            pseudo_line=0,
        )
        return recorder.pseudocode, recorder.steps

    in_map = {val: idx for idx, val in enumerate(inorder)}
    pre_iter = iter(preorder)
    tree_root: Optional[TreeNode] = None

    def _build(left_in: int, right_in: int, parent: Optional[TreeNode] = None, is_left: bool = True) -> Optional[TreeNode]:
        nonlocal tree_root
        if left_in > right_in:
            return None

        val = next(pre_iter)
        mid_in = in_map[val]

        if mid_in < left_in or mid_in > right_in:
            raise TreeBuildError(f"Inconsistent traversal order: value '{val}' outside subtree range.")

        node = TreeNode(val)
        if parent is None:
            tree_root = node
        else:
            if is_left:
                parent.left = node
            else:
                parent.right = node

        recorder.record_step(
            tree_root=tree_root,
            highlight_nodes=[node.node_id],
            highlight_edges=[(parent.node_id, node.node_id)] if parent else [],
            message=f"Picked root value '{val}' from preorder sequence.",
            pseudo_line=0,
        )

        left_part = inorder[left_in:mid_in]
        right_part = inorder[mid_in + 1:right_in + 1]

        recorder.record_step(
            tree_root=tree_root,
            highlight_nodes=[node.node_id],
            message=f"Inorder split at '{val}': Left subtree elements = {left_part}, Right = {right_part}.",
            pseudo_line=2,
        )

        node.left = _build(left_in, mid_in - 1, node, is_left=True)
        node.right = _build(mid_in + 1, right_in, node, is_left=False)
        return node

    _build(0, len(inorder) - 1)

    recorder.record_step(
        tree_root=tree_root,
        highlight_nodes=[],
        message="Tree reconstruction from Inorder + Preorder is complete.",
        pseudo_line=0,
    )
    return recorder.pseudocode, recorder.steps


def record_build_inorder_postorder(
    inorder: List[Any],
    postorder: List[Any],
) -> Tuple[List[str], List[Step]]:
    """Record step-by-step reconstruction from Inorder + Postorder."""
    _validate_sequences(inorder, postorder, "inorder", "postorder", require_unique=True)

    pseudocode = [
        "pick root value from end of postorder sequence",
        "find root position in inorder sequence",
        "split inorder into left & right subtrees",
        "recursively construct right subtree",
        "recursively construct left subtree",
    ]
    recorder = StepRecorder(operation="build_inorder_postorder", pseudocode=pseudocode)

    if not inorder:
        recorder.record_step(tree_root=None, message="Empty sequences. Tree is empty.", pseudo_line=0)
        return recorder.pseudocode, recorder.steps

    in_map = {val: idx for idx, val in enumerate(inorder)}
    post_iter = reversed(postorder)
    tree_root: Optional[TreeNode] = None

    def _build(left_in: int, right_in: int, parent: Optional[TreeNode] = None, is_left: bool = True) -> Optional[TreeNode]:
        nonlocal tree_root
        if left_in > right_in:
            return None

        val = next(post_iter)
        mid_in = in_map[val]

        if mid_in < left_in or mid_in > right_in:
            raise TreeBuildError(f"Inconsistent traversal order: value '{val}' outside range.")

        node = TreeNode(val)
        if parent is None:
            tree_root = node
        else:
            if is_left:
                parent.left = node
            else:
                parent.right = node

        recorder.record_step(
            tree_root=tree_root,
            highlight_nodes=[node.node_id],
            highlight_edges=[(parent.node_id, node.node_id)] if parent else [],
            message=f"Picked root value '{val}' from end of postorder.",
            pseudo_line=0,
        )

        left_part = inorder[left_in:mid_in]
        right_part = inorder[mid_in + 1:right_in + 1]

        recorder.record_step(
            tree_root=tree_root,
            highlight_nodes=[node.node_id],
            message=f"Inorder split at '{val}': Left = {left_part}, Right = {right_part}.",
            pseudo_line=2,
        )

        node.right = _build(mid_in + 1, right_in, node, is_left=False)
        node.left = _build(left_in, mid_in - 1, node, is_left=True)
        return node

    _build(0, len(inorder) - 1)

    recorder.record_step(
        tree_root=tree_root,
        highlight_nodes=[],
        message="Tree reconstruction from Inorder + Postorder is complete.",
        pseudo_line=0,
    )
    return recorder.pseudocode, recorder.steps


def record_build_inorder_level_order(
    inorder: List[Any],
    level_order: List[Any],
) -> Tuple[List[str], List[Step]]:
    """Record step-by-step reconstruction from Inorder + Level order."""
    _validate_sequences(inorder, level_order, "inorder", "level_order", require_unique=True)

    pseudocode = [
        "pick root from head of level-order sequence",
        "find root position in inorder sequence",
        "filter remaining level-order into left & right sets",
        "recursively construct left subtree",
        "recursively construct right subtree",
    ]
    recorder = StepRecorder(operation="build_inorder_level_order", pseudocode=pseudocode)

    if not inorder:
        recorder.record_step(tree_root=None, message="Empty sequences. Tree is empty.", pseudo_line=0)
        return recorder.pseudocode, recorder.steps

    tree_root: Optional[TreeNode] = None

    def _build(in_list: List[Any], lvl_list: List[Any], parent: Optional[TreeNode] = None, is_left: bool = True) -> Optional[TreeNode]:
        nonlocal tree_root
        if not in_list:
            return None

        val = lvl_list[0]
        node = TreeNode(val)

        if parent is None:
            tree_root = node
        else:
            if is_left:
                parent.left = node
            else:
                parent.right = node

        recorder.record_step(
            tree_root=tree_root,
            highlight_nodes=[node.node_id],
            highlight_edges=[(parent.node_id, node.node_id)] if parent else [],
            message=f"Picked root value '{val}' from level-order.",
            pseudo_line=0,
        )

        mid_idx = in_list.index(val)
        left_in = in_list[:mid_idx]
        right_in = in_list[mid_idx + 1:]

        left_set = set(left_in)
        left_lvl = [x for x in lvl_list[1:] if x in left_set]
        right_lvl = [x for x in lvl_list[1:] if x not in left_set]

        recorder.record_step(
            tree_root=tree_root,
            highlight_nodes=[node.node_id],
            message=f"Partitioned: Left inorder={left_in}, Right inorder={right_in}.",
            pseudo_line=2,
        )

        node.left = _build(left_in, left_lvl, node, is_left=True)
        node.right = _build(right_in, right_lvl, node, is_left=False)
        return node

    _build(inorder, level_order)

    recorder.record_step(
        tree_root=tree_root,
        highlight_nodes=[],
        message="Tree reconstruction from Inorder + Level Order is complete.",
        pseudo_line=0,
    )
    return recorder.pseudocode, recorder.steps


def record_build_preorder_postorder(
    preorder: List[Any],
    postorder: List[Any],
) -> Tuple[List[str], List[Step]]:
    """Record step-by-step reconstruction from Preorder + Postorder (Full Binary Trees)."""
    _validate_sequences(preorder, postorder, "preorder", "postorder", require_unique=True)

    pseudocode = [
        "pick root value from preorder sequence",
        "if leaf (length == 1): return node",
        "check for ambiguity: preorder[1] == postorder[-2]",
        "split subtrees using left child index in postorder",
        "recursively construct left & right subtrees",
    ]
    recorder = StepRecorder(operation="build_preorder_postorder", pseudocode=pseudocode)

    if not preorder:
        recorder.record_step(tree_root=None, message="Empty sequences. Tree is empty.", pseudo_line=0)
        return recorder.pseudocode, recorder.steps

    post_map = {val: idx for idx, val in enumerate(postorder)}
    tree_root: Optional[TreeNode] = None

    def _build(
        pre_start: int,
        pre_end: int,
        post_start: int,
        post_end: int,
        parent: Optional[TreeNode] = None,
        is_left: bool = True,
    ) -> TreeNode:
        nonlocal tree_root
        val = preorder[pre_start]
        node = TreeNode(val)

        if parent is None:
            tree_root = node
        else:
            if is_left:
                parent.left = node
            else:
                parent.right = node

        recorder.record_step(
            tree_root=tree_root,
            highlight_nodes=[node.node_id],
            highlight_edges=[(parent.node_id, node.node_id)] if parent else [],
            message=f"Root of subtree: '{val}'.",
            pseudo_line=0,
        )

        if pre_start == pre_end:
            return node

        left_val = preorder[pre_start + 1]
        last_post_val = postorder[post_end - 1]

        if left_val == last_post_val:
            raise AmbiguousTreeError(
                f"Reconstruction from preorder and postorder is ambiguous: node '{val}' "
                f"has a single child '{left_val}'. Only full binary trees are uniquely defined."
            )

        left_post_idx = post_map[left_val]
        left_size = left_post_idx - post_start + 1

        recorder.record_step(
            tree_root=tree_root,
            highlight_nodes=[node.node_id],
            message=f"Identified left subtree root '{left_val}' (size: {left_size}).",
            pseudo_line=3,
        )

        node.left = _build(
            pre_start + 1,
            pre_start + left_size,
            post_start,
            left_post_idx,
            node,
            is_left=True,
        )
        node.right = _build(
            pre_start + left_size + 1,
            pre_end,
            left_post_idx + 1,
            post_end - 1,
            node,
            is_left=False,
        )
        return node

    _build(0, len(preorder) - 1, 0, len(postorder) - 1)

    recorder.record_step(
        tree_root=tree_root,
        highlight_nodes=[],
        message="Full binary tree reconstruction from Preorder + Postorder is complete.",
        pseudo_line=0,
    )
    return recorder.pseudocode, recorder.steps


def record_build_bst_from_preorder(preorder: List[Any]) -> Tuple[List[str], List[Step]]:
    """Record step-by-step BST construction from Preorder sequence only."""
    validate_consistent_types(preorder)

    if len(set(preorder)) != len(preorder):
        dups = [x for x in preorder if preorder.count(x) > 1]
        raise DuplicateValueError(f"Duplicate elements in preorder: {list(set(dups))}. BST requires unique keys.")

    pseudocode = [
        "pick root value from preorder",
        "elements within (min, max) bounds become children",
        "recursively construct left subtree with upper bound = root.val",
        "recursively construct right subtree with lower bound = root.val",
    ]
    recorder = StepRecorder(operation="build_bst_from_preorder", pseudocode=pseudocode)

    if not preorder:
        recorder.record_step(tree_root=None, message="Empty preorder. BST is empty.", pseudo_line=0)
        return recorder.pseudocode, recorder.steps

    idx = 0
    n = len(preorder)
    tree_root: Optional[TreeNode] = None

    def _build(min_val: Any, max_val: Any, parent: Optional[TreeNode] = None, is_left: bool = True) -> Optional[TreeNode]:
        nonlocal idx, tree_root
        if idx >= n:
            return None

        val = preorder[idx]
        if min_val is not None and compare_bst_keys(val, min_val) <= 0:
            return None
        if max_val is not None and compare_bst_keys(val, max_val) >= 0:
            return None

        idx += 1
        node = TreeNode(val)

        if parent is None:
            tree_root = node
        else:
            if is_left:
                parent.left = node
            else:
                parent.right = node

        recorder.record_step(
            tree_root=tree_root,
            highlight_nodes=[node.node_id],
            highlight_edges=[(parent.node_id, node.node_id)] if parent else [],
            message=f"Placed '{val}' in BST within valid bounds ({min_val}, {max_val}).",
            pseudo_line=1,
        )

        node.left = _build(min_val, val, node, is_left=True)
        node.right = _build(val, max_val, node, is_left=False)
        return node

    _build(None, None)

    if idx < n:
        raise TreeBuildError(f"Invalid BST preorder sequence at element '{preorder[idx]}'.")

    recorder.record_step(
        tree_root=tree_root,
        highlight_nodes=[],
        message="BST reconstruction from preorder is complete.",
        pseudo_line=0,
    )
    return recorder.pseudocode, recorder.steps


def record_build_bst_from_postorder(postorder: List[Any]) -> Tuple[List[str], List[Step]]:
    """Record step-by-step BST construction from Postorder sequence only."""
    validate_consistent_types(postorder)

    if len(set(postorder)) != len(postorder):
        dups = [x for x in postorder if postorder.count(x) > 1]
        raise DuplicateValueError(f"Duplicate elements in postorder: {list(set(dups))}. BST requires unique keys.")

    pseudocode = [
        "pick root value from end of postorder",
        "elements within (min, max) bounds become children",
        "recursively construct right subtree with lower bound = root.val",
        "recursively construct left subtree with upper bound = root.val",
    ]
    recorder = StepRecorder(operation="build_bst_from_postorder", pseudocode=pseudocode)

    if not postorder:
        recorder.record_step(tree_root=None, message="Empty postorder. BST is empty.", pseudo_line=0)
        return recorder.pseudocode, recorder.steps

    idx = len(postorder) - 1
    tree_root: Optional[TreeNode] = None

    def _build(min_val: Any, max_val: Any, parent: Optional[TreeNode] = None, is_left: bool = True) -> Optional[TreeNode]:
        nonlocal idx, tree_root
        if idx < 0:
            return None

        val = postorder[idx]
        if min_val is not None and compare_bst_keys(val, min_val) <= 0:
            return None
        if max_val is not None and compare_bst_keys(val, max_val) >= 0:
            return None

        idx -= 1
        node = TreeNode(val)

        if parent is None:
            tree_root = node
        else:
            if is_left:
                parent.left = node
            else:
                parent.right = node

        recorder.record_step(
            tree_root=tree_root,
            highlight_nodes=[node.node_id],
            highlight_edges=[(parent.node_id, node.node_id)] if parent else [],
            message=f"Placed '{val}' in BST within valid bounds ({min_val}, {max_val}).",
            pseudo_line=1,
        )

        node.right = _build(val, max_val, node, is_left=False)
        node.left = _build(min_val, val, node, is_left=True)
        return node

    _build(None, None)

    if idx >= 0:
        raise TreeBuildError(f"Invalid BST postorder sequence at element '{postorder[idx]}'.")

    recorder.record_step(
        tree_root=tree_root,
        highlight_nodes=[],
        message="BST reconstruction from postorder is complete.",
        pseudo_line=0,
    )
    return recorder.pseudocode, recorder.steps
