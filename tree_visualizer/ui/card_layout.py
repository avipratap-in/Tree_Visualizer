"""Pure algorithmic layout computation for canvas empty-state definition cards.

Zero Tkinter dependencies: purely deterministic mathematical geometry.
Computes collision-free vertical flow for Title, Narrative Body, and Actionable Hint.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Optional, Tuple


@dataclass(frozen=True)
class BlockLayout:
    """Computed geometric rectangle and typographic attributes for a card text block."""

    role: str
    text: str
    center_x: float
    top_y: float
    wrap_width: float
    width: float
    height: float
    font_size: int
    lines: int
    linespace: float

    @property
    def bottom_y(self) -> float:
        return self.top_y + self.height

    @property
    def left_x(self) -> float:
        return self.center_x - self.width / 2.0

    @property
    def right_x(self) -> float:
        return self.center_x + self.width / 2.0


@dataclass(frozen=True)
class CardLayoutResult:
    """Full layout geometry for empty-state definition card."""

    canvas_width: float
    canvas_height: float
    title: BlockLayout
    body: BlockLayout
    hint: BlockLayout
    total_height: float
    gap_title_body: float
    gap_body_hint: float

    def has_overlap(self) -> bool:
        """Verify whether any of title, body, or hint overlap vertically."""
        if self.title.bottom_y > self.body.top_y:
            return True
        if self.body.bottom_y > self.hint.top_y:
            return True
        return False


# Measurer signature: (text, role, font_size, wrap_width) -> (linespace, line_count, max_line_width)
TextMeasurer = Callable[[str, str, int, float], Tuple[float, int, float]]


def compute_card_layout(
    canvas_width: float,
    canvas_height: float,
    title_text: str,
    body_text: str,
    hint_text: str,
    measure_fn: TextMeasurer,
    title_font_size: int = 34,
    body_font_size: int = 20,
    hint_font_size: int = 12,
    pan_x: float = 0.0,
    pan_y: float = 0.0,
    scale: float = 1.0,
    max_card_width: float = 720.0,
) -> CardLayoutResult:
    """Compute exact non-overlapping vertical layout for definition card.

    Args:
        canvas_width: Width of canvas in pixels.
        canvas_height: Height of canvas in pixels.
        title_text: Card heading string.
        body_text: Main narrative text.
        hint_text: Actionable instruction line.
        measure_fn: Callable returning (linespace, line_count, max_line_width).
        title_font_size: Base heading font size (default 34, +20% scaled).
        body_font_size: Base body font size (default 20, +20% scaled).
        hint_font_size: Base hint font size (default 12, +20% scaled).
        pan_x: Viewport horizontal pan offset.
        pan_y: Viewport vertical pan offset.
        scale: Viewport zoom scale.
        max_card_width: Maximum card width constraint (default ~720 px).

    Returns:
        CardLayoutResult with exact positions, widths, heights, and zero overlaps.
    """
    scale = max(0.1, scale)
    cx = canvas_width / 2.0 + pan_x

    # Effective font sizes scaled with viewport zoom
    t_size = max(12, int(round(title_font_size * scale)))
    b_size = max(10, int(round(body_font_size * scale)))
    h_size = max(8, int(round(hint_font_size * scale)))

    # Width constraints
    eff_max_w = min(max_card_width * scale, max(80.0, canvas_width * 0.88))
    body_wrap_w = eff_max_w
    title_wrap_w = min(eff_max_w + 80.0 * scale, max(80.0, canvas_width * 0.94))
    hint_wrap_w = eff_max_w

    # Gaps proportional to font size and scale
    gap_tb = max(10.0, round(24.0 * scale * (b_size / 20.0)))
    gap_bh = max(8.0, round(18.0 * scale * (h_size / 12.0)))

    # Initial measurement
    t_linespace, t_lines, t_w = measure_fn(title_text, "title", t_size, title_wrap_w)
    b_linespace, b_lines, b_w = measure_fn(body_text, "body", b_size, body_wrap_w)
    h_linespace, h_lines, h_w = measure_fn(hint_text, "hint", h_size, hint_wrap_w)

    t_height = max(1.0, t_linespace * max(1, t_lines))
    b_height = max(1.0, b_linespace * max(1, b_lines))
    h_height = max(1.0, h_linespace * max(1, h_lines))

    total_h = t_height + gap_tb + b_height + gap_bh + h_height

    # Adapt if card is taller than canvas: reduce spacing then font size slightly
    avail_h = max(40.0, canvas_height - 20.0)
    if total_h > avail_h:
        # Step 1: Compress gaps
        gap_tb = max(6.0, gap_tb * 0.5)
        gap_bh = max(4.0, gap_bh * 0.5)
        total_h = t_height + gap_tb + b_height + gap_bh + h_height

        # Step 2: If still taller, scale font sizes down gracefully
        if total_h > avail_h:
            ratio = max(0.5, avail_h / total_h)
            t_size = max(10, int(round(t_size * ratio)))
            b_size = max(8, int(round(b_size * ratio)))
            h_size = max(7, int(round(h_size * ratio)))

            t_linespace, t_lines, t_w = measure_fn(title_text, "title", t_size, title_wrap_w)
            b_linespace, b_lines, b_w = measure_fn(body_text, "body", b_size, body_wrap_w)
            h_linespace, h_lines, h_w = measure_fn(hint_text, "hint", h_size, hint_wrap_w)

            t_height = max(1.0, t_linespace * max(1, t_lines))
            b_height = max(1.0, b_linespace * max(1, b_lines))
            h_height = max(1.0, h_linespace * max(1, h_lines))
            total_h = t_height + gap_tb + b_height + gap_bh + h_height

    # Vertically center the entire card group
    target_top = (canvas_height - total_h) / 2.0 + pan_y

    # Calculate strictly stacked, non-overlapping positions
    title_top = target_top
    body_top = title_top + t_height + gap_tb
    hint_top = body_top + b_height + gap_bh

    title_block = BlockLayout(
        role="title",
        text=title_text,
        center_x=cx,
        top_y=title_top,
        wrap_width=title_wrap_w,
        width=min(t_w, title_wrap_w) if t_w > 0 else title_wrap_w,
        height=t_height,
        font_size=t_size,
        lines=t_lines,
        linespace=t_linespace,
    )

    body_block = BlockLayout(
        role="body",
        text=body_text,
        center_x=cx,
        top_y=body_top,
        wrap_width=body_wrap_w,
        width=min(b_w, body_wrap_w) if b_w > 0 else body_wrap_w,
        height=b_height,
        font_size=b_size,
        lines=b_lines,
        linespace=b_linespace,
    )

    hint_block = BlockLayout(
        role="hint",
        text=hint_text,
        center_x=cx,
        top_y=hint_top,
        wrap_width=hint_wrap_w,
        width=min(h_w, hint_wrap_w) if h_w > 0 else hint_wrap_w,
        height=h_height,
        font_size=h_size,
        lines=h_lines,
        linespace=h_linespace,
    )

    return CardLayoutResult(
        canvas_width=canvas_width,
        canvas_height=canvas_height,
        title=title_block,
        body=body_block,
        hint=hint_block,
        total_height=total_h,
        gap_title_body=gap_tb,
        gap_body_hint=gap_bh,
    )
