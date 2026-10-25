"""Validation and diagnostic engine adapter."""
from __future__ import annotations

from typing import Any, Dict, Optional
from tree_visualizer.core.suggestions import diagnose_sequences


def validate_build_input(
    mode: str,
    raw_seq1: Optional[str],
    raw_seq2: Optional[str] = None,
) -> Dict[str, Any]:
    """Validate reconstruction inputs and generate structured diagnostics and suggestions."""
    result = diagnose_sequences(mode, raw_seq1, raw_seq2)
    return result.to_dict()
