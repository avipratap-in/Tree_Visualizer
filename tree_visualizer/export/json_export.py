"""JSON serialization and file export for binary trees.

Conforms to reference schema: recursive node dictionary with id, val, freq, left, right.
"""
from __future__ import annotations

import json
from typing import Optional
from tree_visualizer.core.node import TreeNode


def export_tree_to_json(tree: Optional[TreeNode], indent: int = 2) -> str:
    """Serialize binary tree into formatted JSON matching the reference schema."""
    if tree is None:
        return "{}"
    return json.dumps(tree.to_dict(), indent=indent)


def save_tree_to_json_file(
    tree: Optional[TreeNode],
    filepath: str,
    indent: int = 2,
) -> None:
    """Write serialized binary tree JSON to specified file path."""
    content = export_tree_to_json(tree, indent=indent)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
