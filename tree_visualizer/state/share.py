"""Serialization and sharing codecs.

Encodes and decodes tree structures and active tab state to compact
base64-encoded strings with a schema version field.
"""
from __future__ import annotations

import base64
import json
from typing import Any, Dict, Optional, Tuple, Union
from tree_visualizer.core.node import TreeNode


def encode_share_code(
    tree: Optional[Union[TreeNode, Dict[str, Any]]],
    tab: str = "bst",
) -> str:
    """Encode a tree and active tab to a compact URL-safe base64 string.

    Format: Base64( JSON({"v": 1, "tab": tab, "tree": <tree_dict>}) )
    """
    if isinstance(tree, TreeNode):
        tree_dict = tree.to_dict()
    elif isinstance(tree, dict):
        tree_dict = tree
    else:
        tree_dict = None

    payload = {
        "v": 1,
        "tab": tab if tab in ("binary", "bst", "build") else "bst",
        "tree": tree_dict,
    }

    raw_json = json.dumps(payload, separators=(",", ":"))
    return base64.urlsafe_b64encode(raw_json.encode("utf-8")).decode("ascii")


def decode_share_code(code: str) -> Tuple[Optional[Dict[str, Any]], str]:
    """Decode a share string into (tree_dict, tab_name).

    Raises:
        ValueError: if the code is malformed, not base64, missing required fields,
                    or has an unsupported version.
    """
    clean_code = code.strip()
    if not clean_code:
        raise ValueError("Share code is empty.")

    try:
        raw_bytes = base64.urlsafe_b64decode(clean_code.encode("ascii"))
        payload = json.loads(raw_bytes.decode("utf-8"))
    except Exception as e:
        raise ValueError(f"Malformed share code: {e}") from e

    if not isinstance(payload, dict):
        raise ValueError("Invalid share code payload format (expected JSON object).")

    version = payload.get("v", payload.get("version"))
    if version != 1:
        raise ValueError(f"Unsupported share code version: {version}")

    tab = payload.get("tab", "bst")
    if tab not in ("binary", "bst", "build"):
        tab = "bst"

    tree_dict = payload.get("tree")
    if tree_dict is not None and not isinstance(tree_dict, dict):
        raise ValueError("Tree payload must be a JSON object or null.")

    return tree_dict, tab
