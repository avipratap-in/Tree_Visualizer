"""Comparison utilities for BST keys.

Supports numeric comparison when values are numbers (or numeric strings)
and lexicographical comparison when values are alphabetic labels.
Disallows mixing numbers and alphabetic strings in the same BST.
"""
from __future__ import annotations

from typing import Any, Iterable, Tuple
from tree_visualizer.core.exceptions import MixedTypesError


def is_numeric_value(val: Any) -> bool:
    """Check if a value represents a number (int, float, or numeric string).

    Booleans are explicitly excluded.
    """
    if isinstance(val, bool):
        return False
    if isinstance(val, (int, float)):
        return True
    if isinstance(val, str):
        s = val.strip()
        if not s:
            return False
        # Check integer or float representation
        try:
            float(s)
            return True
        except ValueError:
            return False
    return False


def to_numeric_value(val: Any) -> float:
    """Convert a numeric value or numeric string to float for comparison."""
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        return float(val.strip())
    raise ValueError(f"Value '{val}' is not numeric.")


def detect_value_type(val: Any) -> str:
    """Return 'numeric' if value is numeric, else 'alpha'."""
    return "numeric" if is_numeric_value(val) else "alpha"


def validate_consistent_types(values: Iterable[Any]) -> str:
    """Ensure all values in collection share the same type regime.

    Returns 'numeric' or 'alpha'. Raises MixedTypesError if both appear.
    """
    has_numeric = False
    has_alpha = False

    for v in values:
        if is_numeric_value(v):
            has_numeric = True
        else:
            has_alpha = True

        if has_numeric and has_alpha:
            raise MixedTypesError(
                "Mixed numeric and alphabetic values detected. "
                "BST requires all values to be numbers or all values to be letters."
            )

    return "alpha" if has_alpha else "numeric"


def compare_bst_keys(a: Any, b: Any) -> int:
    """Compare two BST keys.

    Returns:
        negative int if a < b
        0 if a == b
        positive int if a > b

    Raises:
        MixedTypesError: if one value is numeric and the other is alphabetic.
    """
    a_is_num = is_numeric_value(a)
    b_is_num = is_numeric_value(b)

    if a_is_num != b_is_num:
        raise MixedTypesError(
            f"Cannot compare mixed types in BST: '{a}' ({'numeric' if a_is_num else 'alphabetic'}) "
            f"and '{b}' ({'numeric' if b_is_num else 'alphabetic'})."
        )

    if a_is_num:
        num_a = to_numeric_value(a)
        num_b = to_numeric_value(b)
        if num_a < num_b:
            return -1
        elif num_a > num_b:
            return 1
        return 0
    else:
        str_a = str(a)
        str_b = str(b)
        if str_a < str_b:
            return -1
        elif str_a > str_b:
            return 1
        return 0


class BSTKey:
    """Comparable wrapper around a BST key using strict type-aware comparison."""

    __slots__ = ("val",)

    def __init__(self, val: Any) -> None:
        self.val = val

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, BSTKey):
            return compare_bst_keys(self.val, other.val) < 0
        return compare_bst_keys(self.val, other) < 0

    def __le__(self, other: Any) -> bool:
        if isinstance(other, BSTKey):
            return compare_bst_keys(self.val, other.val) <= 0
        return compare_bst_keys(self.val, other) <= 0

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, BSTKey):
            return compare_bst_keys(self.val, other.val) == 0
        return compare_bst_keys(self.val, other) == 0

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __gt__(self, other: Any) -> bool:
        if isinstance(other, BSTKey):
            return compare_bst_keys(self.val, other.val) > 0
        return compare_bst_keys(self.val, other) > 0

    def __ge__(self, other: Any) -> bool:
        if isinstance(other, BSTKey):
            return compare_bst_keys(self.val, other.val) >= 0
        return compare_bst_keys(self.val, other) >= 0

    def __repr__(self) -> str:
        return f"BSTKey({self.val!r})"
