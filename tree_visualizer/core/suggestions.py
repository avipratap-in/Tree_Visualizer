"""Diagnostic and suggestion engine for tree reconstruction inputs.

Analyzes sequence pairs, reports errors and warnings with severity levels,
and generates one-click corrective suggestions (swap fields, switch mode,
deduplicate, or valid partner sequence generation).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
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
from tree_visualizer.core.node import TreeNode
from tree_visualizer.core.parsing import ParsedSequence, parse_sequence
from tree_visualizer.core.traversals import (
    inorder_recursive,
    level_order,
    postorder_recursive,
    preorder_recursive,
)


@dataclass
class DiagnosticResult:
    """Structured diagnostic outcome for tree reconstruction input sequences."""

    valid: bool = False
    severity: str = "info"  # info | success | warning | error
    message: str = ""
    mode: str = "in+pre"
    seq1: Dict[str, Any] = field(default_factory=dict)
    seq2: Optional[Dict[str, Any]] = None
    field_errors: Dict[str, str] = field(default_factory=dict)
    suggestions: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "valid": self.valid,
            "status": self.severity,  # For UI compatibility: status matches severity
            "severity": self.severity,
            "message": self.message,
            "mode": self.mode,
            "seq1": self.seq1,
            "seq2": self.seq2,
            "field_errors": self.field_errors,
            "suggestions": self.suggestions,
        }


def _find_duplicates(tokens: List[Any]) -> List[Any]:
    seen = set()
    dups = []
    for t in tokens:
        if t in seen and t not in dups:
            dups.append(t)
        seen.add(t)
    return dups


def _suggest_deduplication(tokens: List[Any]) -> str:
    """Generate a sequence renaming duplicates (e.g. ['A', 'B', 'A'] -> 'A, B, A2')."""
    counts: Dict[Any, int] = {}
    deduped = []
    for t in tokens:
        counts[t] = counts.get(t, 0) + 1
        if counts[t] == 1:
            deduped.append(str(t))
        else:
            deduped.append(f"{t}{counts[t]}")
    return ", ".join(deduped)


def _tree_from_inorder(in_seq: List[Any]) -> Optional[TreeNode]:
    """Construct a balanced reference binary tree from an inorder sequence."""
    if not in_seq:
        return None
    mid = len(in_seq) // 2
    root = TreeNode(in_seq[mid])
    root.left = _tree_from_inorder(in_seq[:mid])
    root.right = _tree_from_inorder(in_seq[mid + 1:])
    return root


def _tree_from_preorder(pre_seq: List[Any]) -> Optional[TreeNode]:
    """Construct a reference binary tree from a preorder sequence."""
    if not pre_seq:
        return None
    root = TreeNode(pre_seq[0])
    rem = pre_seq[1:]
    if rem:
        mid = (len(rem) + 1) // 2
        root.left = _tree_from_preorder(rem[:mid])
        root.right = _tree_from_preorder(rem[mid:])
    return root


def _tree_from_postorder(post_seq: List[Any]) -> Optional[TreeNode]:
    """Construct a reference binary tree from a postorder sequence."""
    if not post_seq:
        return None
    root = TreeNode(post_seq[-1])
    rem = post_seq[:-1]
    if rem:
        mid = len(rem) // 2
        root.left = _tree_from_postorder(rem[:mid])
        root.right = _tree_from_postorder(rem[mid:])
    return root


def _tree_from_level_order(lvl: List[Any]) -> Optional[TreeNode]:
    """Construct a reference binary tree from a level-order sequence."""
    if not lvl:
        return None
    root = TreeNode(lvl[0])
    queue = [root]
    idx = 1
    while queue and idx < len(lvl):
        curr = queue.pop(0)
        if idx < len(lvl):
            curr.left = TreeNode(lvl[idx])
            queue.append(curr.left)
            idx += 1
        if idx < len(lvl):
            curr.right = TreeNode(lvl[idx])
            queue.append(curr.right)
            idx += 1
    return root


def _generate_partner_suggestions(
    mode: str,
    tokens1: List[Any],
    tokens2: List[Any],
) -> List[Dict[str, Any]]:
    """Offer valid partner sequences when existing sequences cannot belong to the same tree."""
    suggestions: List[Dict[str, Any]] = []
    try:
        if mode == "in+pre":
            t1 = _tree_from_inorder(tokens1)
            if t1 is not None:
                valid_pre = ", ".join(str(x) for x in preorder_recursive(t1))
                suggestions.append({
                    "type": "replace",
                    "field": "seq2",
                    "label": f"Valid Preorder for Seq 1: {valid_pre}",
                    "value": valid_pre,
                })
            t2 = _tree_from_preorder(tokens2)
            if t2 is not None:
                valid_in = ", ".join(str(x) for x in inorder_recursive(t2))
                suggestions.append({
                    "type": "replace",
                    "field": "seq1",
                    "label": f"Valid Inorder for Seq 2: {valid_in}",
                    "value": valid_in,
                })

        elif mode == "in+post":
            t1 = _tree_from_inorder(tokens1)
            if t1 is not None:
                valid_post = ", ".join(str(x) for x in postorder_recursive(t1))
                suggestions.append({
                    "type": "replace",
                    "field": "seq2",
                    "label": f"Valid Postorder for Seq 1: {valid_post}",
                    "value": valid_post,
                })
            t2 = _tree_from_postorder(tokens2)
            if t2 is not None:
                valid_in = ", ".join(str(x) for x in inorder_recursive(t2))
                suggestions.append({
                    "type": "replace",
                    "field": "seq1",
                    "label": f"Valid Inorder for Seq 2: {valid_in}",
                    "value": valid_in,
                })

        elif mode == "in+level":
            t1 = _tree_from_inorder(tokens1)
            if t1 is not None:
                valid_lvl = ", ".join(str(x) for x in level_order(t1))
                suggestions.append({
                    "type": "replace",
                    "field": "seq2",
                    "label": f"Valid Level-order for Seq 1: {valid_lvl}",
                    "value": valid_lvl,
                })
            t2 = _tree_from_level_order(tokens2)
            if t2 is not None:
                valid_in = ", ".join(str(x) for x in inorder_recursive(t2))
                suggestions.append({
                    "type": "replace",
                    "field": "seq1",
                    "label": f"Valid Inorder for Seq 2: {valid_in}",
                    "value": valid_in,
                })
    except Exception:
        pass

    return suggestions


def diagnose_sequences(
    mode: str,
    raw_seq1: Optional[str],
    raw_seq2: Optional[str] = None,
) -> DiagnosticResult:
    """Diagnose a pair of sequences for the selected mode and return severity and fixes.

    Severities:
    - info: Missing input or neutral guidance.
    - success: Sequences are valid and ready to reconstruct.
    - warning: Reconstruction succeeds but is structurally ambiguous (e.g. pre+post non-full).
    - error: Duplicates, mismatched elements, length disparity, or invalid tree ordering.
    """
    p1 = parse_sequence(raw_seq1)
    tokens1 = p1.tokens

    two_seq_modes = {"in+pre", "in+post", "in+level", "pre+post"}
    p2 = parse_sequence(raw_seq2) if mode in two_seq_modes else None
    tokens2 = p2.tokens if p2 is not None else None

    result = DiagnosticResult(
        valid=False,
        severity="info",
        mode=mode,
        seq1=p1.to_dict(),
        seq2=p2.to_dict() if p2 is not None else None,
        suggestions=[],
    )

    # 1. Empty sequence checks
    if not tokens1:
        result.severity = "info"
        result.message = "Enter the primary traversal sequence above."
        return result

    if mode in two_seq_modes and not tokens2:
        result.severity = "info"
        result.message = "Enter the secondary traversal sequence."
        return result

    # 1b. Maximum node limit (50 nodes)
    count = max(len(tokens1), len(tokens2) if tokens2 is not None else 0)
    if count > 50:
        result.severity = "error"
        result.message = (
            f"Input sequence exceeds the maximum limit of 50 nodes (got {count}). "
            f"Please limit to 50 nodes for smooth visualization."
        )
        return result

    # 2. Check duplicates for general binary tree modes
    if mode in two_seq_modes:
        dups1 = _find_duplicates(tokens1)
        dups2 = _find_duplicates(tokens2) if tokens2 is not None else []

        if dups1 or dups2:
            result.severity = "error"
            dup_items = list(set(dups1 + dups2))
            result.message = (
                f"Duplicate value(s) {dup_items} detected. Tree reconstruction requires unique node labels."
            )
            if dups1:
                result.suggestions.append({
                    "type": "replace",
                    "field": "seq1",
                    "label": "Rename duplicates in Seq 1",
                    "value": _suggest_deduplication(tokens1),
                })
            if dups2:
                result.suggestions.append({
                    "type": "replace",
                    "field": "seq2",
                    "label": "Rename duplicates in Seq 2",
                    "value": _suggest_deduplication(tokens2),
                })
            return result

    # 3. Check element sets & lengths for 2-sequence modes
    if mode in two_seq_modes and tokens2 is not None:
        if len(tokens1) != len(tokens2):
            result.severity = "error"
            result.message = (
                f"Length mismatch: Sequence 1 has {len(tokens1)} items, while Sequence 2 has {len(tokens2)} items."
            )
            return result

        set1 = set(tokens1)
        set2 = set(tokens2)
        if set1 != set2:
            diff1 = set1 - set2
            diff2 = set2 - set1
            result.severity = "error"
            parts = []
            if diff1:
                parts.append(f"Missing in Sequence 2: {sorted(list(diff1), key=str)}")
            if diff2:
                parts.append(f"Missing in Sequence 1: {sorted(list(diff2), key=str)}")
            result.message = "Inconsistent sequences: " + "; ".join(parts)
            return result

    # 4. BST mode checks: ensure consistent data types and no duplicates
    if mode in {"bst-pre", "bst-post"}:
        has_num = any(is_numeric_value(x) for x in tokens1)
        has_alpha = any(not is_numeric_value(x) for x in tokens1)

        if has_num and has_alpha:
            result.severity = "error"
            result.message = (
                "Mixed numbers and letters detected. BST requires all-numbers (numeric order) "
                "or all-letters (alphabetical order)."
            )
            return result

        dups = _find_duplicates(tokens1)
        if dups:
            result.severity = "error"
            result.message = f"Duplicate value(s) {dups} detected in BST traversal."
            return result

        try:
            if mode == "bst-pre":
                build_bst_from_preorder(tokens1)
            else:
                build_bst_from_postorder(tokens1)
            result.valid = True
            result.severity = "success"
            result.message = f"Valid BST traversal ({len(tokens1)} nodes). Ready to build!"
            return result
        except Exception as e:
            result.severity = "error"
            result.message = str(e)
            return result

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

        result.valid = True
        result.severity = "success"
        result.message = f"Valid traversal pair ({len(tokens1)} nodes). Ready to build!"
        return result

    except AmbiguousTreeError as e:
        result.severity = "warning"
        result.message = f"⚠️ Ambiguity Warning: {e}"
        return result

    except TreeBuildError as e:
        result.severity = "error"
        result.message = str(e)

        # 5a. Check if fields were swapped
        try:
            assert tokens2 is not None
            if mode == "in+pre":
                build_from_inorder_preorder(tokens2, tokens1)
            elif mode == "in+post":
                build_from_inorder_postorder(tokens2, tokens1)
            elif mode == "in+level":
                build_from_inorder_level_order(tokens2, tokens1)
            elif mode == "pre+post":
                build_from_preorder_postorder(tokens2, tokens1)

            result.suggestions.append({
                "type": "swap_fields",
                "label": "⇄ Swap Sequence 1 and Sequence 2",
                "action": "swap",
            })
            result.message += " (The two sequences appear to be swapped)."
            return result
        except Exception:
            pass

        # 5b. Check if the pair matches another mode
        alt_modes = [
            ("in+pre", "Inorder + Preorder", build_from_inorder_preorder),
            ("in+post", "Inorder + Postorder", build_from_inorder_postorder),
            ("in+level", "Inorder + Level Order", build_from_inorder_level_order),
            ("pre+post", "Preorder + Postorder", build_from_preorder_postorder),
        ]
        for alt_key, alt_label, alt_fn in alt_modes:
            if alt_key != mode:
                try:
                    alt_fn(tokens1, tokens2)
                    result.suggestions.append({
                        "type": "switch_mode",
                        "label": f"Switch mode to {alt_label}",
                        "mode": alt_key,
                    })
                    break
                except Exception:
                    pass

        # 5c. Offer valid partner sequences
        partner_suggestions = _generate_partner_suggestions(mode, tokens1, tokens2)
        result.suggestions.extend(partner_suggestions)

        return result
