"""Pure Data Structures & Algorithms layer.

Provides:
- TreeNode: Core node abstraction with frequency-based duplicate handling.
- BinaryTree: General binary tree with level-order construction.
- BinarySearchTree: Strict BST with duplicate frequencies, search, insert, remove,
  min/max, predecessor/successor, rank/select, validation.
- Traversals: Recursive and iterative preorder, inorder, postorder, level-order.
- Properties: Leaf count, internal nodes, height, full, complete, perfect, balanced.
- Builders: In+Pre, In+Post, In+Level, Pre+Post (full BT / ambiguity check), BST-Pre, BST-Post.
- Comparison: Type-safe BST key comparisons (numbers or letters).
- Parsing: Lenient sequence token extraction.
- Validator: Input diagnostic and suggestion engine.
- Generators: Random test trees.

CRITICAL: Never import tkinter in this package.
"""
from __future__ import annotations

from tree_visualizer.core.binary_tree import BinaryTree
from tree_visualizer.core.bst import BinarySearchTree
from tree_visualizer.core.builders import (
    build_bst_from_postorder,
    build_bst_from_preorder,
    build_from_inorder_level_order,
    build_from_inorder_postorder,
    build_from_inorder_preorder,
    build_from_preorder_postorder,
)
from tree_visualizer.core.comparison import (
    BSTKey,
    compare_bst_keys,
    detect_value_type,
    is_numeric_value,
    validate_consistent_types,
)
from tree_visualizer.core.exceptions import (
    AmbiguousTreeError,
    DuplicateValueError,
    InvalidInputError,
    MixedTypesError,
    TreeBuildError,
    TreeError,
)
from tree_visualizer.core.generators import (
    generate_random_binary_tree,
    generate_random_bst,
    generate_random_full_binary_tree,
    get_random_labels,
)
from tree_visualizer.core.node import TreeNode, generate_node_id, reset_node_id_counter
from tree_visualizer.core.parsing import ParsedSequence, parse_sequence
from tree_visualizer.core.properties import (
    compute_properties,
    height,
    internal_node_count,
    is_balanced,
    is_complete,
    is_full,
    is_perfect,
    leaf_count,
    size,
)
from tree_visualizer.core.traversals import (
    inorder_iterative,
    inorder_recursive,
    level_order,
    postorder_iterative,
    postorder_recursive,
    preorder_iterative,
    preorder_recursive,
)
from tree_visualizer.core.validator import validate_build_input

__all__ = [
    "TreeNode",
    "generate_node_id",
    "reset_node_id_counter",
    "BinaryTree",
    "BinarySearchTree",
    "TreeError",
    "TreeBuildError",
    "AmbiguousTreeError",
    "MixedTypesError",
    "DuplicateValueError",
    "InvalidInputError",
    "is_numeric_value",
    "validate_consistent_types",
    "compare_bst_keys",
    "BSTKey",
    "preorder_recursive",
    "preorder_iterative",
    "inorder_recursive",
    "inorder_iterative",
    "postorder_recursive",
    "postorder_iterative",
    "level_order",
    "height",
    "size",
    "leaf_count",
    "internal_node_count",
    "is_full",
    "is_complete",
    "is_perfect",
    "is_balanced",
    "compute_properties",
    "build_from_inorder_preorder",
    "build_from_inorder_postorder",
    "build_from_inorder_level_order",
    "build_from_preorder_postorder",
    "build_bst_from_preorder",
    "build_bst_from_postorder",
    "get_random_labels",
    "generate_random_binary_tree",
    "generate_random_full_binary_tree",
    "generate_random_bst",
    "ParsedSequence",
    "parse_sequence",
    "validate_build_input",
]
