"""Unit tests for reconstruction diagnostic validator."""
from __future__ import annotations

from tree_visualizer.core.validator import validate_build_input


def test_validator_valid():
    diag = validate_build_input("in+pre", "D, B, E, A, C", "A, B, D, E, C")
    assert diag["valid"] is True
    assert diag["status"] == "success"


def test_validator_duplicates():
    diag = validate_build_input("in+pre", "A, B, A", "A, A, B")
    assert diag["valid"] is False
    assert diag["status"] == "error"
    assert "duplicate" in diag["message"].lower()
    assert len(diag["suggestions"]) > 0


def test_validator_mismatch():
    diag = validate_build_input("in+pre", "A, B, C", "A, B, D")
    assert diag["valid"] is False
    assert diag["status"] == "error"
    assert "inconsistent" in diag["message"].lower()


def test_validator_swap_suggestion():
    # User gave Preorder as Seq1 and Inorder as Seq2
    diag = validate_build_input("in+pre", "A, B, D, E, C", "D, B, E, A, C")
    assert diag["valid"] is False
    assert any(s["type"] == "swap_fields" for s in diag["suggestions"])
