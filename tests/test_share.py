"""Unit tests for share code encoding and decoding."""
from __future__ import annotations

import base64
import json
import pytest
from tree_visualizer.core.bst import BinarySearchTree
from tree_visualizer.core.node import TreeNode
from tree_visualizer.state.share import decode_share_code, encode_share_code


def test_share_code_empty_tree():
    """Verify share encoding and decoding with None tree."""
    code = encode_share_code(None, tab="bst")
    assert isinstance(code, str)
    assert len(code) > 0

    tree_dict, tab = decode_share_code(code)
    assert tree_dict is None
    assert tab == "bst"


def test_share_code_tree_roundtrip():
    """Verify roundtrip encode/decode of a full BST."""
    bst = BinarySearchTree()
    for val in [50, 25, 75, 12, 37, 62, 87]:
        bst.insert(val)

    code = encode_share_code(bst.root, tab="bst")
    tree_dict, tab = decode_share_code(code)

    assert tab == "bst"
    assert tree_dict is not None
    restored_root = TreeNode.from_dict(tree_dict)
    assert restored_root is not None
    assert restored_root.val == 50
    assert restored_root.size() == 7
    assert restored_root.height() == 3


def test_share_code_preserves_tab_names():
    """Verify tabs 'binary', 'bst', and 'build' are preserved."""
    for tab_name in ("binary", "bst", "build"):
        code = encode_share_code(None, tab=tab_name)
        _, decoded_tab = decode_share_code(code)
        assert decoded_tab == tab_name

    # Unknown tab falls back to 'bst'
    code = encode_share_code(None, tab="invalid_tab")
    _, decoded_tab = decode_share_code(code)
    assert decoded_tab == "bst"


def test_share_code_with_dict_tree():
    """Verify encoding accepts dictionary tree representation."""
    sample_dict = {"val": 10, "freq": 1, "left": None, "right": None}
    code = encode_share_code(sample_dict, tab="binary")
    tree_dict, tab = decode_share_code(code)
    assert tab == "binary"
    assert tree_dict == sample_dict


def test_share_code_invalid_empty():
    """Verify empty string raises ValueError."""
    with pytest.raises(ValueError, match="empty"):
        decode_share_code("")
    with pytest.raises(ValueError, match="empty"):
        decode_share_code("   ")


def test_share_code_corrupted_base64():
    """Verify corrupted base64 raises ValueError."""
    with pytest.raises(ValueError, match="Malformed"):
        decode_share_code("This is not valid base64!@#$")


def test_share_code_invalid_json():
    """Verify non-JSON payload raises ValueError."""
    bad_bytes = b"not a json object"
    bad_code = base64.urlsafe_b64encode(bad_bytes).decode("ascii")
    with pytest.raises(ValueError, match="Malformed"):
        decode_share_code(bad_code)


def test_share_code_unsupported_version():
    """Verify version mismatch raises ValueError."""
    payload = {"v": 99, "tab": "bst", "tree": None}
    code = base64.urlsafe_b64encode(json.dumps(payload).encode("utf-8")).decode("ascii")
    with pytest.raises(ValueError, match="Unsupported share code version"):
        decode_share_code(code)


def test_share_code_invalid_payload_type():
    """Verify non-dict payload raises ValueError."""
    payload = ["not", "a", "dict"]
    code = base64.urlsafe_b64encode(json.dumps(payload).encode("utf-8")).decode("ascii")
    with pytest.raises(ValueError, match="expected JSON object"):
        decode_share_code(code)
