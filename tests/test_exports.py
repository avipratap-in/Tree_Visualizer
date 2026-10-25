"""Tests for Step 10: Top-bar actions, JSON/PNG/SVG exports, and Share dialog."""
from __future__ import annotations

import json
import os
import tempfile
import pytest
from PIL import Image

from tests.conftest import requires_display
from tree_visualizer.core.binary_tree import BinaryTree
from tree_visualizer.core.node import TreeNode
from tree_visualizer.export import (
    export_tree_to_json,
    render_tree_to_pillow_image,
    render_tree_to_svg,
    save_tree_to_json_file,
    save_tree_to_png_file,
    save_tree_to_svg_file,
)
from tree_visualizer.state.controller import Controller
from tree_visualizer.state.share import decode_share_code, encode_share_code
from tree_visualizer.ui.share_dialog import ShareDialog
from tree_visualizer.ui.theme import DARK_THEME, LIGHT_THEME, ThemeManager


@pytest.fixture
def sample_tree() -> TreeNode:
    """Create a sample 5-node binary tree."""
    tree = BinaryTree.from_level_order([50, 25, 75, 10, 30])
    assert tree.root is not None
    return tree.root


def test_json_export_schema(sample_tree):
    """Verify JSON export produces valid JSON matching the reference recursive schema."""
    json_str = export_tree_to_json(sample_tree)
    data = json.loads(json_str)

    # Validate recursive schema fields
    assert "val" in data and data["val"] == 50
    assert "id" in data
    assert "freq" in data and data["freq"] == 1
    assert "left" in data and data["left"]["val"] == 25
    assert "right" in data and data["right"]["val"] == 75
    assert data["left"]["left"]["val"] == 10
    assert data["left"]["right"]["val"] == 30

    # Test file saving
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "tree.json")
        save_tree_to_json_file(sample_tree, filepath)
        assert os.path.exists(filepath)
        assert os.path.getsize(filepath) > 0

        with open(filepath, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        assert loaded["val"] == 50


def test_json_export_empty_tree():
    """Verify empty tree export produces valid empty JSON."""
    json_str = export_tree_to_json(None)
    assert json_str == "{}"


def test_png_export_valid_and_non_empty(sample_tree):
    """Verify Pillow ImageDraw re-draws tree without Ghostscript dependency."""
    # Render in-memory
    img = render_tree_to_pillow_image(sample_tree, theme=DARK_THEME, width=900, height=500, scale_factor=2)
    assert isinstance(img, Image.Image)
    assert img.size == (1800, 1000)

    # Save to file and inspect
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "tree.png")
        save_tree_to_png_file(sample_tree, filepath, theme=LIGHT_THEME)
        assert os.path.exists(filepath)
        assert os.path.getsize(filepath) > 1000  # Non-trivial image file

        # Open and verify Pillow can read it back cleanly
        with Image.open(filepath) as loaded_img:
            assert loaded_img.format == "PNG"
            assert loaded_img.size == (1800, 1000)


def test_png_export_empty_tree():
    """Verify PNG export on empty tree produces a clean background image."""
    img = render_tree_to_pillow_image(None, theme=DARK_THEME, width=900, height=500, scale_factor=2)
    assert isinstance(img, Image.Image)
    assert img.size == (1800, 1000)


def test_svg_export_valid_standard_library(sample_tree):
    """Verify SVG export writes valid XML with rect, lines, circles, and text."""
    svg_str = render_tree_to_svg(sample_tree, theme=DARK_THEME, width=900, height=500)
    assert svg_str.startswith('<svg xmlns="http://www.w3.org/2000/svg"')
    assert svg_str.endswith("</svg>")
    assert '<rect width="100%" height="100%"' in svg_str
    assert "<line " in svg_str
    assert "<circle " in svg_str
    assert "<text " in svg_str
    assert ">50<" in svg_str

    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "tree.svg")
        save_tree_to_svg_file(sample_tree, filepath)
        assert os.path.exists(filepath)
        assert os.path.getsize(filepath) > 0


def test_svg_export_empty_tree():
    """Verify SVG export on empty tree generates valid minimal container."""
    svg_str = render_tree_to_svg(None, theme=DARK_THEME)
    assert svg_str.startswith('<svg')
    assert svg_str.endswith("</svg>")
    assert "<circle" not in svg_str


def test_share_code_roundtrip_all_tabs(sample_tree):
    """Verify share code round-tripping preserves tree values, structure, and active tab."""
    for tab in ["bst", "binary", "build"]:
        code = encode_share_code(sample_tree, tab=tab)
        assert isinstance(code, str) and len(code) > 0

        decoded_dict, decoded_tab = decode_share_code(code)
        assert decoded_tab == tab
        rebuilt_tree = TreeNode.from_dict(decoded_dict)
        assert rebuilt_tree.val == sample_tree.val
        assert rebuilt_tree.size() == sample_tree.size()
        assert rebuilt_tree.left.val == 25
        assert rebuilt_tree.right.val == 75


@requires_display
def test_ui_share_dialog_and_load(sample_tree):
    """Verify ShareDialog displays current share code and allows importing another."""
    import tkinter as tk

    root = tk.Tk()
    tm = ThemeManager(root, initial_theme="dark")
    ctrl = Controller()
    ctrl.set_active_tab("bst")
    ctrl.current_tree = sample_tree

    dialog = ShareDialog(root, ctrl, tm)
    assert dialog.entry_export.get() != ""
    assert "(Canvas is empty" not in dialog.entry_export.get()

    # Generate another tree and share code to import
    tree2 = BinaryTree.from_level_order(["X", "Y", "Z"]).root
    code2 = encode_share_code(tree2, tab="binary")

    # Paste and load code
    dialog.entry_import.insert(0, code2)
    dialog._handle_load_code()

    # Controller should have switched to 'binary' tab and loaded tree2
    assert ctrl.active_tab == "binary"
    assert ctrl.current_tree is not None
    assert ctrl.current_tree.val == "X"
    assert ctrl.current_tree.size() == 3

    root.destroy()
