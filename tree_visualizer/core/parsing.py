"""Lenient sequence parsing module.

Extracts tokens from raw user inputs with support for messy separators,
bracket stripping, contiguous letter splitting, and level-order null placeholders.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, List, Optional
from tree_visualizer.core.comparison import is_numeric_value


@dataclass
class ParsedSequence:
    """Represents the parsed outcome of a raw traversal sequence string.

    Attributes:
        tokens: The cleaned list of tokens (int, str, or None for empty children).
        raw: The original raw string input.
        warnings: List of warning messages.
        notes: List of informational notes (e.g. "Interpreted as: ...").
    """
    tokens: List[Any] = field(default_factory=list)
    raw: str = ""
    warnings: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "tokens": self.tokens,
            "raw": self.raw,
            "warnings": self.warnings,
            "notes": self.notes,
            "formatted": ", ".join("null" if t is None else str(t) for t in self.tokens),
        }


def parse_sequence(raw: Optional[str], is_level_order: bool = False) -> ParsedSequence:
    """Parse a raw sequence string into normalized tokens.

    Supports:
    - Separators: commas, spaces, tabs, semicolons, pipes, newlines, or any combination.
    - Repeated, leading, and trailing separators.
    - Surrounding brackets [..], (..), {..} and quotes are stripped.
    - Pure-letter strings without separators (e.g. "DBEAC") are split into characters.
    - Pure digit strings (e.g. "12345") are NOT split (treated as single number with hint).
    - Level-order lists (or when is_level_order=True) accept "-", "null", "#", or "none" for empty children.
    - Returns tokens plus notes ("Interpreted as: ...").
    """
    if raw is None:
        return ParsedSequence(tokens=[], raw="", notes=["Interpreted as: (empty)"])

    raw_str = str(raw).strip()
    if not raw_str:
        return ParsedSequence(tokens=[], raw=raw_str, notes=["Interpreted as: (empty)"])

    cleaned = raw_str
    notes: List[str] = []
    warnings: List[str] = []

    # Strip surrounding brackets/parentheses
    if (cleaned.startswith("[") and cleaned.endswith("]")) or \
       (cleaned.startswith("(") and cleaned.endswith(")")) or \
       (cleaned.startswith("{") and cleaned.endswith("}")):
        cleaned = cleaned[1:-1].strip()

    # Check for presence of common delimiters
    has_delimiters = bool(re.search(r"[,;\s\|\n\t]", cleaned))

    # Special case: Contiguous string without delimiters
    if not has_delimiters and len(cleaned) > 1:
        if cleaned.isalpha():
            # e.g. "DBEAC" -> ['D', 'B', 'E', 'A', 'C']
            tokens_str = list(cleaned)
            formatted = ", ".join(tokens_str)
            notes.append(f"Interpreted as: {formatted} (automatically split contiguous letters)")
            return ParsedSequence(tokens=tokens_str, raw=raw_str, warnings=warnings, notes=notes)
        elif cleaned.isdigit():
            # e.g. "12345" -> single token, do NOT split
            notes.append(
                f"Interpreted as: {cleaned} (single numeric token; use commas or spaces to separate multiple numbers)"
            )
            return ParsedSequence(tokens=[int(cleaned)], raw=raw_str, warnings=warnings, notes=notes)

    # Split using any mix of delimiters: comma, space, tab, semicolon, pipe, newline
    # Leading, trailing, and repeated separators are automatically consumed
    raw_pieces = re.split(r"[,;\s\|\n\t]+", cleaned)
    tokens_str: List[Optional[str]] = []

    for piece in raw_pieces:
        p = piece.strip()
        if not p:
            continue
        # Strip surrounding quotes from individual token: e.g. 'A' or "A"
        if (p.startswith("'") and p.endswith("'")) or (p.startswith('"') and p.endswith('"')):
            p = p[1:-1].strip()
        if not p:
            continue

        if is_level_order and p.lower() in ("-", "null", "#", "none", "."):
            tokens_str.append(None)
        else:
            tokens_str.append(p)

    if not tokens_str:
        return ParsedSequence(tokens=[], raw=raw_str, notes=["Interpreted as: (no valid tokens found)"])

    # Type normalization: Check if non-null tokens parse cleanly as integers
    all_ints = True
    parsed_tokens: List[Any] = []
    has_any_int = False
    has_any_str = False

    for t in tokens_str:
        if t is None:
            parsed_tokens.append(None)
            continue

        if re.match(r"^-?\d+$", t):
            has_any_int = True
            parsed_tokens.append(int(t))
        elif is_numeric_value(t):
            try:
                val_float = float(t)
                if val_float.is_integer() and "." not in t:
                    parsed_tokens.append(int(t))
                    has_any_int = True
                else:
                    parsed_tokens.append(val_float)
                    has_any_int = True
            except ValueError:
                parsed_tokens.append(t)
                all_ints = False
                has_any_str = True
        else:
            all_ints = False
            has_any_str = True
            parsed_tokens.append(t)

    if has_any_int and has_any_str:
        warnings.append("Mixed numeric and alphabetical tokens detected. Values will be treated as strings.")
        # If mixed, preserve original strings for non-null tokens
        final_tokens: List[Any] = [str(x) if x is not None else None for x in tokens_str]
    else:
        final_tokens = parsed_tokens

    formatted_str = ", ".join("null" if t is None else str(t) for t in final_tokens)
    notes.append(f"Interpreted as: {formatted_str}")

    return ParsedSequence(tokens=final_tokens, raw=raw_str, warnings=warnings, notes=notes)


def parse_level_order(raw: Optional[str]) -> ParsedSequence:
    """Parse a level-order sequence with null placeholders ('-', 'null', '#', 'none')."""
    return parse_sequence(raw, is_level_order=True)
