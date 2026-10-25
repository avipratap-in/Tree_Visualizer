"""Unit tests for lenient sequence parsing."""
from __future__ import annotations

from tree_visualizer.core.parsing import parse_sequence


def test_parsing_empty():
    p = parse_sequence("")
    assert p.tokens == []
    p_none = parse_sequence(None)
    assert p_none.tokens == []


def test_parsing_delimiters():
    p1 = parse_sequence("10, 20, 30; 40 | 50\t60\n70")
    assert p1.tokens == [10, 20, 30, 40, 50, 60, 70]


def test_parsing_brackets():
    p = parse_sequence("[1, 2, 3, 4]")
    assert p.tokens == [1, 2, 3, 4]
    p_paren = parse_sequence("(A, B, C)")
    assert p_paren.tokens == ["A", "B", "C"]


def test_parsing_contiguous_letters():
    p = parse_sequence("DBEAC")
    assert p.tokens == ["D", "B", "E", "A", "C"]
