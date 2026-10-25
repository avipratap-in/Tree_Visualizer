"""Validation and diagnostic engine for tree reconstruction inputs."""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from tree_visualizer.core.builders import (
    AmbiguousTreeError,
    TreeBuildError,
    build_bst_from_postorder,
    build_bst_from_preorder,
    build_from_inorder_level_order,
    build_from_inorder_postorder,
    build_from_inorder_preorder,
    build_from_preorder_postorder,
)
from tree_visualizer.core.comparison import is_numeric_value
from tree_visualizer.core.exceptions import MixedTypesError
from tree_visualizer.core.parsing import parse_sequence
from tree_visualizer.core.traversals import (
    inorder_recursive,
    postorder_recursive,
    preorder_recursive,
)


def _find_duplicates(tokens: List[Any]) -> List[Any]:
    seen = set()
    dups = []
    for t in tokens:
        if t in seen and t not in dups:
            dups.append(t)
        seen.add(t)
    return dups


def _suggest_deduplication(tokens: List[Any]) -> str:
    counts: Dict[Any, int] = {}
    deduped = []
    for t in tokens:
        counts[t] = counts.get(t, 0) + 1
        if counts[t] == 1:
            deduped.append(str(t))
        else:
            deduped.append(f"{t}{counts[t]}")
    return ", ".join(deduped)


def validate_build_input(
    mode: str,
    raw_seq1: Optional[str],
    raw_seq2: Optional[str] = None,
) -> Dict[str, Any]:
    """Validate reconstruction inputs and generate structured diagnostics and suggestions."""
    p1 = parse_sequence(raw_seq1)
    tokens1 = p1.tokens

    two_seq_modes = {"in+pre", "in+post", "in+level", "pre+post"}
    p2 = parse_sequence(raw_seq2) if mode in two_seq_modes else None
    tokens2 = p2.tokens if p2 else None

    diagnostics: Dict[str, Any] = {
        "valid": False,
        "status": "neutral",  # neutral | success | warning | error
        "mode": mode,
        "seq1": p1.to_dict(),
        "seq2": p2.to_dict() if p2 else None,
        "message": "",
        "suggestions": [],
    }

    # 1. Empty checks
    if not tokens1:
        diagnostics["status"] = "neutral"
        diagnostics["message"] = "Enter the primary traversal sequence above."
        return diagnostics

    if mode in two_seq_modes and not tokens2:
        diagnostics["status"] = "neutral"
        diagnostics["message"] = "Enter the secondary traversal sequence."
        return diagnostics

    # 1b. Maximum node limit (50 nodes)
    count = max(len(tokens1), len(tokens2) if tokens2 else 0)
    if count > 50:
        diagnostics["status"] = "error"
        diagnostics["message"] = (
            f"Input sequence exceeds the maximum limit of 50 nodes (got {count}). "
            f"Please limit to 50 nodes for smooth visualization."
        )
        return diagnostics

    # 2. Check duplicates for general binary tree modes
    if mode in two_seq_modes:
        dups1 = _find_duplicates(tokens1)
        dups2 = _find_duplicates(tokens2) if tokens2 else []

        if dups1 or dups2:
            diagnostics["status"] = "error"
            dup_items = list(set(dups1 + dups2))
            diagnostics["message"] = (
                f"Duplicate value(s) {dup_items} detected. Tree reconstruction requires unique node labels."
            )
            if dups1:
                diagnostics["suggestions"].append({
                    "type": "replace",
                    "field": "seq1",
                    "label": "Rename duplicates in Seq 1",
                    "value": _suggest_deduplication(tokens1),
                })
            if dups2:
                diagnostics["suggestions"].append({
                    "type": "replace",
                    "field": "seq2",
                    "label": "Rename duplicates in Seq 2",
                    "value": _suggest_deduplication(tokens2),
                })
            return diagnostics

    # 3. Check element sets & lengths for 2-sequence modes
    if mode in two_seq_modes and tokens2 is not None:
        if len(tokens1) != len(tokens2):
            diagnostics["status"] = "error"
            diagnostics["message"] = (
                f"Length mismatch: Sequence 1 has {len(tokens1)} items, while Sequence 2 has {len(tokens2)} items."
            )
            return diagnostics

        set1 = set(tokens1)
        set2 = set(tokens2)
        if set1 != set2:
            diff1 = set1 - set2
            diff2 = set2 - set1
            diagnostics["status"] = "error"
            msg_parts = []
            if diff1:
                msg_parts.append(f"Missing in Sequence 2: {sorted(list(diff1), key=str)}")
            if diff2:
                msg_parts.append(f"Missing in Sequence 1: {sorted(list(diff2), key=str)}")
            diagnostics["message"] = "Inconsistent sequences: " + "; ".join(msg_parts)
            return diagnostics

    # 4. BST mode checks: ensure consistent data types
    if mode in {"bst-pre", "bst-post"}:
        has_num = any(is_numeric_value(x) for x in tokens1)
        has_alpha = any(not is_numeric_value(x) for x in tokens1)

        if has_num and has_alpha:
            diagnostics["status"] = "error"
            diagnostics["message"] = (
                "Mixed numbers and letters detected. BST requires all-numbers (numeric order) "
                "or all-letters (alphabetical order)."
            )
            return diagnostics

        dups = _find_duplicates(tokens1)
        if dups:
            diagnostics["status"] = "error"
            diagnostics["message"] = f"Duplicate value(s) {dups} detected in BST traversal."
            return diagnostics

        try:
            if mode == "bst-pre":
                build_bst_from_preorder(tokens1)
            else:
                build_bst_from_postorder(tokens1)
            diagnostics["valid"] = True
            diagnostics["status"] = "success"
            diagnostics["message"] = f"Valid BST traversal ({len(tokens1)} nodes)."
            return diagnostics
        except Exception as e:
            diagnostics["status"] = "error"
            diagnostics["message"] = str(e)
            return diagnostics

    # 5. Try target mode reconstruction
    try:
        assert tokens2 is not None
        if mode == "in+pre":
            build_from_inorder_preorder(tokens1, tokens2)
        elif mode == "in+post":
            build_from_inorder_postorder(tokens1, tokens2)
        elif mode == "in+level":
            build_from_inorder_level_order(tokens1, tokens2)
        elif mode == "pre+post":
            build_from_preorder_postorder(tokens1, tokens2)

        diagnostics["valid"] = True
        diagnostics["status"] = "success"
        diagnostics["message"] = f"Valid traversal pair ({len(tokens1)} nodes). Ready to build!"
        return diagnostics

    except AmbiguousTreeError as e:
        diagnostics["status"] = "error"
        diagnostics["message"] = str(e)
        return diagnostics

    except TreeBuildError as e:
        diagnostics["status"] = "error"
        diagnostics["message"] = str(e)

        # Check if swapping sequences fixes the issue (e.g. user entered Preorder into Seq1 and Inorder into Seq2)
        if mode in ("in+pre", "in+post"):
            try:
                if mode == "in+pre":
                    swapped_tree = build_from_inorder_preorder(tokens2, tokens1)
                else:
                    swapped_tree = build_from_inorder_postorder(tokens2, tokens1)
                if swapped_tree is not None:
                    diagnostics["suggestions"].append({
                        "type": "swap_fields",
                        "label": "Swap Sequence 1 and Sequence 2",
                    })
                    diagnostics["message"] += " (Hint: Swapping Sequence 1 and Sequence 2 produces a valid tree!)"
            except Exception:
                pass

        return diagnostics
