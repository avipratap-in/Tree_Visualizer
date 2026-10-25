"""Lenient sequence parsing module.

Extracts tokens from raw user inputs with support for messy separators,
bracket stripping, delimiterless strings, and number parsing.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, List, Optional
from tree_visualizer.core.comparison import is_numeric_value


@dataclass
class ParsedSequence:
    """Represents the outcome of parsing a raw traversal sequence string."""

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
            "formatted": ", ".join(str(t) for t in self.tokens),
        }


def parse_sequence(raw: Optional[str]) -> ParsedSequence:
    """Parse a raw sequence string into normalized tokens.

    Supports:
    - Common delimiters: commas, spaces, semicolons, tabs, newlines, pipes.
    - Stripping enclosing brackets: [...], (...), {...}.
    - Pure contiguous letters (e.g. "DBEAC" -> ['D', 'B', 'E', 'A', 'C']).
    - Automatic integer conversion if all tokens are integers.
    """
    if raw is None:
        return ParsedSequence(tokens=[], raw="", notes=["Empty input sequence."])

    raw_str = str(raw).strip()
    if not raw_str:
        return ParsedSequence(tokens=[], raw=raw_str, notes=["Empty input sequence."])

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
            tokens: List[Any] = list(cleaned)
            notes.append(f"Parsed continuous letters as {len(tokens)} distinct tokens.")
            return ParsedSequence(tokens=tokens, raw=raw_str, notes=notes)
        elif cleaned.isdigit():
            warnings.append(
                f"Continuous digits '{cleaned}' treated as a single token. Use commas or spaces to separate multiple numbers."
            )
            return ParsedSequence(tokens=[int(cleaned)], raw=raw_str, warnings=warnings)

    # Standard split by delimiters
    raw_tokens = re.split(r"[,;\s\|\n\t]+", cleaned)
    tokens = []
    for token in raw_tokens:
        tok = token.strip()
        if not tok:
            continue
        # Strip surrounding quotes if present
        if (tok.startswith('"') and tok.endswith('"')) or (tok.startswith("'") and tok.endswith("'")):
            tok = tok[1:-1].strip()
        if not tok:
            continue

        if is_numeric_value(tok):
            try:
                # If int representation
                val_float = float(tok)
                if val_float.is_integer() and "." not in tok:
                    tokens.append(int(tok))
                else:
                    tokens.append(val_float)
            except ValueError:
                tokens.append(tok)
        else:
            tokens.append(tok)

    return ParsedSequence(tokens=tokens, raw=raw_str, warnings=warnings, notes=notes)
