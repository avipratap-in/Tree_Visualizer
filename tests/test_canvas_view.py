"""Tests for CanvasView pan, zoom, wheel normalization, tweening, and rendering."""
from __future__ import annotations

import math
import tkinter as tk
import pytest
from tests.conftest import requires_display
from tree_visualizer.core.bst import BinarySearchTree
from tree_visualizer.core.node import TreeNode
from tree_visualizer.recorder.steps import Step
from tree_visualizer.ui.canvas_view import CanvasView
from tree_visualizer.ui.theme import ThemeManager


@requires_display
def test_canvas_zoom_in_out():
    """Verify zoom in and out buttons scale by BUTTON_STEP (1.08)."""
    root = tk.Tk()
    tm = ThemeManager(root)
    cv = CanvasView(root, theme_manager=tm)
    cv.pack(fill=tk.BOTH, expand=True)
    root.update()

    initial_scale = cv.scale
    assert initial_scale == 1.0

    # Zoom in
    cv.zoom_in()
    root.update()
    assert pytest.approx(cv.scale, 0.01) == 1.08

    # Zoom out
    cv.zoom_out()
    root.update()
    assert pytest.approx(cv.scale, 0.01) == 1.00

    root.destroy()


@requires_display
def test_canvas_wheel_zoom_normalization():
    """Verify mouse wheel delta normalization across platforms with 20% decreased sensitivity."""
    try:
        root = tk.Tk()
    except tk.TclError as e:
        pytest.skip(f"Tk initialization failed in runner: {e}")
    tm = ThemeManager(root)
    cv = CanvasView(root, theme_manager=tm)
    cv.pack(fill=tk.BOTH, expand=True)
    root.update()

    # Emulate Windows wheel scroll up (event.delta = +120)
    event_win_up = tk.Event()
    event_win_up.delta = 120
    event_win_up.x = 400
    event_win_up.y = 250
    cv._on_mouse_wheel(event_win_up)
    root.update()
    expected_factor = math.exp(120 * cv.WHEEL_ZOOM_COEFF)
    assert pytest.approx(cv.scale, 0.01) == expected_factor

    # Emulate Linux Button-5 scroll down (num = 5)
    event_lin_down = tk.Event()
    event_lin_down.delta = 0
    event_lin_down.num = 5
    event_lin_down.x = 400
    event_lin_down.y = 250
    scale_before = cv.scale
    cv._on_mouse_wheel(event_lin_down)
    root.update()
    expected_factor_down = math.exp(-120 * cv.WHEEL_ZOOM_COEFF)
    assert pytest.approx(cv.scale, 0.01) == scale_before * expected_factor_down

    root.destroy()


@requires_display
def test_canvas_drag_to_pan():
    """Verify clicking and dragging updates pan offset."""
    root = tk.Tk()
    tm = ThemeManager(root)
    cv = CanvasView(root, theme_manager=tm)
    cv.pack(fill=tk.BOTH, expand=True)
    root.update()

    assert cv.pan_x == 0.0
    assert cv.pan_y == 0.0

    # Start drag at (100, 100)
    start_ev = tk.Event()
    start_ev.x = 100
    start_ev.y = 100
    cv._on_drag_start(start_ev)

    # Move drag to (150, 120)
    move_ev = tk.Event()
    move_ev.x = 150
    move_ev.y = 120
    cv._on_drag_motion(move_ev)
    root.update()

    assert cv.pan_x == 50.0
    assert cv.pan_y == 20.0

    root.destroy()


@requires_display
def test_canvas_reset_view():
    """Verify reset_view resets scale and pan."""
    root = tk.Tk()
    tm = ThemeManager(root)
    cv = CanvasView(root, theme_manager=tm)
    cv.pack(fill=tk.BOTH, expand=True)
    root.update()

    cv.scale = 2.0
    cv.pan_x = 150.0
    cv.pan_y = -80.0

    cv.reset_view()
    root.update()

    assert cv.scale == 1.0
    assert cv.pan_x == 0.0
    assert cv.pan_y == 0.0

    root.destroy()


@requires_display
def test_canvas_definition_card_and_tree_toggle():
    """Verify definition card is shown on empty tree and replaced by tree on load."""
    root = tk.Tk()
    tm = ThemeManager(root)
    cv = CanvasView(root, theme_manager=tm)
    cv.pack(fill=tk.BOTH, expand=True)
    root.update()

    # Empty tree initially -> definition card tags exist
    card_items = cv.canvas.find_withtag("definition_card")
    assert len(card_items) > 0

    # Load tree
    bst = BinarySearchTree()
    bst.insert(50)
    bst.insert(25)
    cv.set_tree(bst.root)
    root.update()

    # Definition card must be removed, nodes and edges rendered
    card_items = cv.canvas.find_withtag("definition_card")
    assert len(card_items) == 0

    node_items = cv.canvas.find_withtag("node")
    edge_items = cv.canvas.find_withtag("edge")
    assert len(node_items) == 2
    assert len(edge_items) == 1

    root.destroy()


@requires_display
def test_canvas_step_tweening():
    """Verify set_step triggers tweening between frames."""
    root = tk.Tk()
    tm = ThemeManager(root)
    cv = CanvasView(root, theme_manager=tm)
    cv.pack(fill=tk.BOTH, expand=True)
    root.update()

    step1 = Step(tree={"val": 50, "freq": 1, "left": None, "right": None}, message="Step 1")
    cv.set_step(step1)
    root.update()

    assert cv.current_tree is not None
    assert cv.current_tree.val == 50

    # Next step adding child
    step2 = Step(
        tree={
            "val": 50,
            "freq": 1,
            "left": {"val": 25, "freq": 1, "left": None, "right": None},
            "right": None,
        },
        message="Step 2",
    )
    cv.set_step(step2)
    root.update()

    assert cv.current_tree.left is not None
    assert cv.current_tree.left.val == 25

    root.destroy()
