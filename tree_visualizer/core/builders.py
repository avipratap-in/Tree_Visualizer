"""Tree reconstruction algorithms from traversal orders.

Reconstructs Binary Trees from:
- Inorder + Preorder
- Inorder + Postorder
- Inorder + Level order
- Preorder + Postorder (Full Binary Tree only; detects single-child ambiguity)
- BST from Preorder only
- BST from Postorder only

Time Complexity:
- in+pre, in+post, pre+post, bst-pre, bst-post: O(n)
- in+level: O(n^2)

Space Complexity:
- O(n) for recursion stack and index lookup maps.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Set
from tree_visualizer.core.comparison import compare_bst_keys, validate_consistent_types
from tree_visualizer.core.exceptions import (
    AmbiguousTreeError,
    DuplicateValueError,
    MixedTypesError,
    TreeBuildError,
)
from tree_visualizer.core.node import TreeNode


def _validate_sequences(
    seq1: List[Any],
    seq2: List[Any],
    name1: str,
    name2: str,
    require_unique: bool = True,
) -> None:
    """Validate two traversal sequences for equal length, uniqueness, and identical element sets."""
    if len(seq1) != len(seq2):
        raise TreeBuildError(
            f"Length mismatch: {name1} has {len(seq1)} elements, but {name2} has {len(seq2)}."
        )

    if require_unique:
        if len(set(seq1)) != len(seq1):
            dups1 = [x for x in seq1 if seq1.count(x) > 1]
            raise DuplicateValueError(
                f"Duplicate elements detected in {name1}: {list(set(dups1))}. Reconstruction requires unique values."
            )
        if len(set(seq2)) != len(seq2):
            dups2 = [x for x in seq2 if seq2.count(x) > 1]
            raise DuplicateValueError(
                f"Duplicate elements detected in {name2}: {list(set(dups2))}. Reconstruction requires unique values."
            )

    set1 = set(seq1)
    set2 = set(seq2)
    if set1 != set2:
        diff1 = set1 - set2
        diff2 = set2 - set1
        parts = []
        if diff1:
            parts.append(f"Missing in {name2}: {sorted(list(diff1), key=str)}")
        if diff2:
            parts.append(f"Missing in {name1}: {sorted(list(diff2), key=str)}")
        raise TreeBuildError(f"Inconsistent sequences: {name1} and {name2} contain different elements. " + "; ".join(parts))


def build_from_inorder_preorder(
    inorder: List[Any],
    preorder: List[Any],
) -> Optional[TreeNode]:
    """Reconstruct binary tree from inorder and preorder traversals.

    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    _validate_sequences(inorder, preorder, "inorder", "preorder", require_unique=True)
    if not inorder:
        return None

    in_map: Dict[Any, int] = {val: idx for idx, val in enumerate(inorder)}
    pre_iter = iter(preorder)

    def _build(left_idx: int, right_idx: int) -> Optional[TreeNode]:
        if left_idx > right_idx:
            return None

        val = next(pre_iter)
        mid_idx = in_map[val]

        if mid_idx < left_idx or mid_idx > right_idx:
            raise TreeBuildError(
                f"Inconsistent traversal order: value '{val}' is outside current subtree range [{left_idx}, {right_idx}]."
            )

        root = TreeNode(val)
        root.left = _build(left_idx, mid_idx - 1)
        root.right = _build(mid_idx + 1, right_idx)
        return root

    return _build(0, len(inorder) - 1)


def build_from_inorder_postorder(
    inorder: List[Any],
    postorder: List[Any],
) -> Optional[TreeNode]:
    """Reconstruct binary tree from inorder and postorder traversals.

    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    _validate_sequences(inorder, postorder, "inorder", "postorder", require_unique=True)
    if not inorder:
        return None

    in_map: Dict[Any, int] = {val: idx for idx, val in enumerate(inorder)}
    post_iter = reversed(postorder)

    def _build(left_idx: int, right_idx: int) -> Optional[TreeNode]:
        if left_idx > right_idx:
            return None

        val = next(post_iter)
        mid_idx = in_map[val]

        if mid_idx < left_idx or mid_idx > right_idx:
            raise TreeBuildError(
                f"Inconsistent traversal order: value '{val}' is outside current subtree range [{left_idx}, {right_idx}]."
            )

        root = TreeNode(val)
        # In reversed postorder, root is followed by right subtree, then left subtree
        root.right = _build(mid_idx + 1, right_idx)
        root.left = _build(left_idx, mid_idx - 1)
        return root

    return _build(0, len(inorder) - 1)


def build_from_inorder_level_order(
    inorder: List[Any],
    level_order: List[Any],
) -> Optional[TreeNode]:
    """Reconstruct binary tree from inorder and level-order traversals.

    Time Complexity: O(n^2)
    Space Complexity: O(n)
    """
    _validate_sequences(inorder, level_order, "inorder", "level_order", require_unique=True)
    if not inorder:
        return None

    def _build(in_list: List[Any], level_list: List[Any]) -> Optional[TreeNode]:
        if not in_list:
            return None

        root_val = level_list[0]
        root = TreeNode(root_val)
        root_idx = in_list.index(root_val)

        left_in = in_list[:root_idx]
        right_in = in_list[root_idx + 1:]

        left_set: Set[Any] = set(left_in)
        left_level: List[Any] = []
        right_level: List[Any] = []

        for item in level_list[1:]:
            if item in left_set:
                left_level.append(item)
            else:
                right_level.append(item)

        root.left = _build(left_in, left_level)
        root.right = _build(right_in, right_level)
        return root

    return _build(inorder, level_order)


def build_from_preorder_postorder(
    preorder: List[Any],
    postorder: List[Any],
) -> Optional[TreeNode]:
    """Reconstruct binary tree from preorder and postorder traversals.

    Preorder + Postorder uniquely identifies a binary tree ONLY when the tree
    is a Full Binary Tree (every node has either 0 or 2 children).
    Raises AmbiguousTreeError if any single-child node is encountered.

    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    _validate_sequences(preorder, postorder, "preorder", "postorder", require_unique=True)
    if not preorder:
        return None

    post_map: Dict[Any, int] = {val: idx for idx, val in enumerate(postorder)}

    def _build(
        pre_start: int,
        pre_end: int,
        post_start: int,
        post_end: int,
    ) -> TreeNode:
        root_val = preorder[pre_start]
        root = TreeNode(root_val)

        if pre_start == pre_end:
            return root

        # Next value in preorder is the root of the left subtree
        left_val = preorder[pre_start + 1]
        # Preceding value in postorder is the root of the right subtree
        last_post_val = postorder[post_end - 1]

        # If left_val == last_post_val, this node has only ONE child, making it ambiguous!
        if left_val == last_post_val:
            raise AmbiguousTreeError(
                f"Reconstruction from preorder and postorder is ambiguous: node '{root_val}' "
                f"has a single child '{left_val}', which could be either a left or right child. "
                f"Preorder + Postorder requires a full binary tree."
            )

        left_post_idx = post_map[left_val]
        left_size = left_post_idx - post_start + 1

        root.left = _build(
            pre_start + 1,
            pre_start + left_size,
            post_start,
            left_post_idx,
        )
        root.right = _build(
            pre_start + left_size + 1,
            pre_end,
            left_post_idx + 1,
            post_end - 1,
        )
        return root

    return _build(0, len(preorder) - 1, 0, len(postorder) - 1)


def build_bst_from_preorder(preorder: List[Any]) -> Optional[TreeNode]:
    """Reconstruct BST from preorder traversal only.

    Validates that values are consistently numeric or alphabetic and distinct.

    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    if not preorder:
        return None

    validate_consistent_types(preorder)

    if len(set(preorder)) != len(preorder):
        dups = [x for x in preorder if preorder.count(x) > 1]
        raise DuplicateValueError(
            f"Duplicate elements in preorder traversal: {list(set(dups))}. BST construction requires distinct keys."
        )

    idx = 0
    n = len(preorder)

    def _build(min_val: Any, max_val: Any) -> Optional[TreeNode]:
        nonlocal idx
        if idx >= n:
            return None

        val = preorder[idx]
        if min_val is not None and compare_bst_keys(val, min_val) <= 0:
            return None
        if max_val is not None and compare_bst_keys(val, max_val) >= 0:
            return None

        idx += 1
        root = TreeNode(val)
        root.left = _build(min_val, val)
        root.right = _build(val, max_val)
        return root

    root = _build(None, None)
    if idx < n:
        raise TreeBuildError(
            f"Invalid BST preorder sequence: element '{preorder[idx]}' violates BST ordering."
        )
    return root


def build_bst_from_postorder(postorder: List[Any]) -> Optional[TreeNode]:
    """Reconstruct BST from postorder traversal only.

    Validates that values are consistently numeric or alphabetic and distinct.

    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    if not postorder:
        return None

    validate_consistent_types(postorder)

    if len(set(postorder)) != len(postorder):
        dups = [x for x in postorder if postorder.count(x) > 1]
        raise DuplicateValueError(
            f"Duplicate elements in postorder traversal: {list(set(dups))}. BST construction requires distinct keys."
        )

    idx = len(postorder) - 1

    def _build(min_val: Any, max_val: Any) -> Optional[TreeNode]:
        nonlocal idx
        if idx < 0:
            return None

        val = postorder[idx]
        if min_val is not None and compare_bst_keys(val, min_val) <= 0:
            return None
        if max_val is not None and compare_bst_keys(val, max_val) >= 0:
            return None

        idx -= 1
        root = TreeNode(val)
        # In postorder reversed, right subtree precedes left subtree
        root.right = _build(val, max_val)
        root.left = _build(min_val, val)
        return root

    root = _build(None, None)
    if idx >= 0:
        raise TreeBuildError(
            f"Invalid BST postorder sequence: element '{postorder[idx]}' violates BST ordering."
        )
    return root
