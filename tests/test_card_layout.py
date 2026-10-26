"""Unit tests for pure definition card layout engine.

Tests layout computation across multiple canvas resolutions and all three definition card texts,
asserting that Title, Body, and Hint never overlap and maintain proportional spacing.
"""
from __future__ import annotations

import math
from typing import Tuple
import pytest

from tree_visualizer.ui.canvas_view import CanvasView
from tree_visualizer.ui.card_layout import (
    BlockLayout,
    CardLayoutResult,
    compute_card_layout,
)


def make_fake_measurer(char_aspect: float = 0.55, line_height_ratio: float = 1.35):
    """Create a deterministic fake text measurer callable."""

    def _measurer(
        text: str, role: str, font_size: int, wrap_width: float
    ) -> Tuple[float, int, float]:
        char_w = font_size * char_aspect
        linespace = font_size * line_height_ratio

        words = text.split(" ")
        lines = 0
        current_len = 0
        max_w = 0.0

        for word in words:
            word_w = len(word) * char_w
            cand_w = (current_len + len(word) + 1) * char_w if current_len > 0 else word_w
            if cand_w <= wrap_width or current_len == 0:
                current_len += len(word) + (1 if current_len > 0 else 0)
                if cand_w > max_w:
                    max_w = cand_w
            else:
                lines += 1
                current_len = len(word)
                if word_w > max_w:
                    max_w = word_w

        if current_len > 0:
            lines += 1

        return linespace, max(1, lines), max_w

    return _measurer


@pytest.fixture
def fake_measurer():
    return make_fake_measurer()


CANVAS_SIZES = [
    (1920.0, 1080.0),  # Full HD
    (1440.0, 900.0),   # WXGA+
    (1200.0, 800.0),   # Default app window
    (1000.0, 700.0),   # Medium window
    (900.0, 600.0),    # Minimum app window
    (640.0, 480.0),    # Small window
    (500.0, 350.0),    # Narrow compact window
    (800.0, 260.0),    # Constrained vertical height
]

TABS = ["bst", "binary", "build"]


@pytest.mark.parametrize("canvas_w,canvas_h", CANVAS_SIZES)
@pytest.mark.parametrize("tab", TABS)
def test_card_layout_never_overlaps(canvas_w: float, canvas_h: float, tab: str, fake_measurer):
    """Assert that heading, body, and hint rectangles never overlap across all tabs and canvas sizes."""
    card_info = CanvasView.DEFINITION_TEXTS[tab]

    layout = compute_card_layout(
        canvas_width=canvas_w,
        canvas_height=canvas_h,
        title_text=card_info["title"],
        body_text=card_info["body"],
        hint_text=card_info["hint"],
        measure_fn=fake_measurer,
        title_font_size=34,
        body_font_size=20,
        hint_font_size=12,
        pan_x=0.0,
        pan_y=0.0,
        scale=1.0,
    )

    # 1. Direct overlap assertion
    assert not layout.has_overlap(), (
        f"Overlap detected in tab '{tab}' at {canvas_w}x{canvas_h}: "
        f"title.bottom={layout.title.bottom_y}, body.top={layout.body.top_y}, "
        f"body.bottom={layout.body.bottom_y}, hint.top={layout.hint.top_y}"
    )

    # 2. Strict vertical hierarchy with positive gaps
    assert layout.title.bottom_y < layout.body.top_y
    assert layout.body.bottom_y < layout.hint.top_y
    assert layout.gap_title_body >= 6.0
    assert layout.gap_body_hint >= 4.0

    # 3. Horizontal centering and boundary bounds
    assert layout.title.center_x == canvas_w / 2.0
    assert layout.body.center_x == canvas_w / 2.0
    assert layout.hint.center_x == canvas_w / 2.0
    assert layout.body.wrap_width <= canvas_w

    # 4. Canvas boundary containment on standard screens
    if canvas_h >= 500:
        assert layout.title.top_y >= 0, f"Title top {layout.title.top_y} < 0"
        assert layout.hint.bottom_y <= canvas_h, f"Hint bottom {layout.hint.bottom_y} > {canvas_h}"


def test_card_layout_handles_scaling(fake_measurer):
    """Assert non-overlapping layout under pan and zoom scaling."""
    card_info = CanvasView.DEFINITION_TEXTS["bst"]

    for scale in [0.5, 0.8, 1.0, 1.2, 1.5, 2.0]:
        layout = compute_card_layout(
            canvas_width=1200.0,
            canvas_height=800.0,
            title_text=card_info["title"],
            body_text=card_info["body"],
            hint_text=card_info["hint"],
            measure_fn=fake_measurer,
            pan_x=50.0,
            pan_y=-30.0,
            scale=scale,
        )
        assert not layout.has_overlap()
        assert layout.title.bottom_y < layout.body.top_y
        assert layout.body.bottom_y < layout.hint.top_y


def test_zoom_sensitivity_reduction_constants():
    """Assert that zoom constants reflect exact 20% sensitivity reduction."""
    assert hasattr(CanvasView, "OLD_BUTTON_STEP")
    assert hasattr(CanvasView, "OLD_WHEEL_ZOOM_COEFF")

    assert CanvasView.OLD_BUTTON_STEP == 1.10
    assert CanvasView.OLD_WHEEL_ZOOM_COEFF == 0.0008

    # Wheel sensitivity: old * 0.8 = 0.00064
    assert CanvasView.WHEEL_ZOOM_COEFF == pytest.approx(0.0008 * 0.8)

    # Button step: exp(0.8 * ln(1.10)) = 1.0792823...
    expected_step = math.exp(0.8 * math.log(1.10))
    assert CanvasView.BUTTON_STEP == pytest.approx(expected_step, rel=1e-5)
