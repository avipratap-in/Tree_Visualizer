"""Unit tests for suggestions.py: verifying all suggestion types and severities."""
from __future__ import annotations

import pytest
from tree_visualizer.core.suggestions import diagnose_sequences


def test_suggestion_empty_input():
    # Primary sequence missing
    d1 = diagnose_sequences("in+pre", "")
    assert d1.valid is False
    assert d1.severity == "info"
    assert "Enter the primary traversal" in d1.message

    # Secondary sequence missing in two-sequence mode
    d2 = diagnose_sequences("in+pre", "A, B, C", "")
    assert d2.valid is False
    assert d2.severity == "info"
    assert "Enter the secondary traversal" in d2.message


def test_suggestion_length_mismatch():
    d = diagnose_sequences("in+pre", "A, B, C", "A, B")
    assert d.valid is False
    assert d.severity == "error"
    assert "Length mismatch" in d.message


def test_suggestion_element_difference():
    d = diagnose_sequences("in+pre", "A, B, C", "A, B, D")
    assert d.valid is False
    assert d.severity == "error"
    assert "Inconsistent sequences" in d.message
    assert "Missing in Sequence 2" in d.message
    assert "Missing in Sequence 1" in d.message


def test_suggestion_duplicates_rename():
    d = diagnose_sequences("in+pre", "A, B, A", "A, A, B")
    assert d.valid is False
    assert d.severity == "error"
    assert "Duplicate value(s)" in d.message

    # Check deduplication one-click fix
    sug_seq1 = [s for s in d.suggestions if s["type"] == "replace" and s["field"] == "seq1"]
    assert len(sug_seq1) > 0
    assert sug_seq1[0]["value"] == "A, B, A2"


def test_suggestion_swapped_fields():
    # User put Preorder in Seq 1 and Inorder in Seq 2
    inorder = "D, B, E, A, C"
    preorder = "A, B, D, E, C"
    d = diagnose_sequences("in+pre", preorder, inorder)

    assert d.valid is False
    assert d.severity == "error"
    assert any(s["type"] == "swap_fields" for s in d.suggestions)
    assert "swapped" in d.message.lower()


def test_suggestion_wrong_mode_switch():
    # Sequence pair valid for Inorder + Level Order, but evaluated under in+pre
    d = diagnose_sequences("in+pre", "A, B, C, D", "B, D, A, C")

    assert d.valid is False
    assert d.severity == "error"
    # Should suggest switching mode to Inorder + Level Order
    mode_sugs = [s for s in d.suggestions if s["type"] == "switch_mode"]
    assert len(mode_sugs) > 0
    assert mode_sugs[0]["mode"] == "in+level"


def test_suggestion_valid_partner_sequences():
    # Sequences that cannot belong to the same tree under in+pre
    d = diagnose_sequences("in+pre", "A, B, C, D, E", "D, E, A, C, B")

    assert d.valid is False
    assert d.severity == "error"
    # Must offer valid partner sequence replacement suggestions
    partner_sugs = [s for s in d.suggestions if s["type"] == "replace"]
    assert len(partner_sugs) > 0
    fields_suggested = {s["field"] for s in partner_sugs}
    assert "seq1" in fields_suggested or "seq2" in fields_suggested


def test_suggestion_pre_post_ambiguity_warning():
    # Preorder + Postorder with single-child node (ambiguous)
    preorder = "A, B"
    postorder = "B, A"
    d = diagnose_sequences("pre+post", preorder, postorder)

    # Must report severity "warning"
    assert d.valid is False
    assert d.severity == "warning"
    assert "Ambiguity Warning" in d.message


def test_suggestion_bst_mixed_types():
    d = diagnose_sequences("bst-pre", "10, A, 30")
    assert d.valid is False
    assert d.severity == "error"
    assert "Mixed numbers and letters" in d.message


def test_suggestion_success():
    d = diagnose_sequences("in+pre", "D, B, E, A, C", "A, B, D, E, C")
    assert d.valid is True
    assert d.severity == "success"
    assert "Ready to build" in d.message
