"""Comprehensive unit tests for lenient sequence and level-order parsing."""
from __future__ import annotations

import pytest
from tree_visualizer.core.parsing import parse_level_order, parse_sequence


def test_parsing_empty_and_whitespace():
    p1 = parse_sequence("")
    assert p1.tokens == []
    assert any("Interpreted as: (empty)" in n for n in p1.notes)

    p2 = parse_sequence("   \n\t  ")
    assert p2.tokens == []
    assert any("Interpreted as: (empty)" in n for n in p2.notes)

    p3 = parse_sequence(None)
    assert p3.tokens == []


def test_parsing_messy_mixed_separators():
    # Mix of commas, spaces, tabs, semicolons, pipes, newlines, repeated and leading/trailing
    raw = ",,,  ;\t| 10 , 20 ; 30 | 40\n\t50 ;;; || \n 60 ,,, "
    p = parse_sequence(raw)
    assert p.tokens == [10, 20, 30, 40, 50, 60]
    assert any("Interpreted as: 10, 20, 30, 40, 50, 60" in n for n in p.notes)


def test_parsing_brackets_and_quotes():
    # Square brackets
    p1 = parse_sequence("[1, 2, 3, 4]")
    assert p1.tokens == [1, 2, 3, 4]

    # Parentheses
    p2 = parse_sequence("(A, B, C)")
    assert p2.tokens == ["A", "B", "C"]

    # Curly braces
    p3 = parse_sequence("{10, 20, 30}")
    assert p3.tokens == [10, 20, 30]

    # Quoted tokens
    p4 = parse_sequence(" 'Apple' , \"Banana\" , 'Cherry' ")
    assert p4.tokens == ["Apple", "Banana", "Cherry"]


def test_parsing_contiguous_letters_split():
    # Pure letter strings without delimiters must be split into characters
    p = parse_sequence("DBEAC")
    assert p.tokens == ["D", "B", "E", "A", "C"]
    assert any("split contiguous letters" in n for n in p.notes)
    assert any("Interpreted as: D, B, E, A, C" in n for n in p.notes)


def test_parsing_contiguous_digits_not_split():
    # Pure digit strings without delimiters must NOT be split
    p = parse_sequence("12345")
    assert p.tokens == [12345]
    assert len(p.tokens) == 1
    assert any("Interpreted as: 12345" in n for n in p.notes)
    assert any("use commas or spaces" in n.lower() for n in p.notes)


def test_parsing_level_order_null_placeholders():
    # Level-order inputs accept '-', 'null', '#', 'none'
    raw = "1, 2, 3, null, 4, -, 5, #, none"
    p = parse_level_order(raw)
    assert p.tokens == [1, 2, 3, None, 4, None, 5, None, None]
    assert any("Interpreted as: 1, 2, 3, null, 4, null, 5, null, null" in n for n in p.notes)

    # Alphabetic level-order
    raw_alpha = "A, B, C, -, D, null, E, #"
    p_alpha = parse_level_order(raw_alpha)
    assert p_alpha.tokens == ["A", "B", "C", None, "D", None, "E", None]


def test_parsing_mixed_numbers_and_letters_warning():
    p = parse_sequence("A, 10, B, 20")
    assert p.tokens == ["A", "10", "B", "20"]
    assert len(p.warnings) > 0
    assert "mixed" in p.warnings[0].lower()
