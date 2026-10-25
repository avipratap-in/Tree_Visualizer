"""Custom exceptions for tree data structures and algorithms."""
from __future__ import annotations


class TreeError(Exception):
    """Base exception for all tree-related errors."""
    pass


class TreeBuildError(TreeError, ValueError):
    """Raised when traversal inputs are invalid, mismatched, or inconsistent."""
    pass


class AmbiguousTreeError(TreeBuildError):
    """Raised when traversals cannot uniquely define a tree (e.g. non-full Preorder + Postorder)."""
    pass


class MixedTypesError(TreeError, TypeError):
    """Raised when attempting to mix numeric and alphabetic values in a BST."""
    pass


class DuplicateValueError(TreeBuildError):
    """Raised when duplicate values are present in inputs requiring strictly distinct keys."""
    pass


class InvalidInputError(TreeError, ValueError):
    """Raised when input sequence cannot be parsed or violates structural constraints."""
    pass
