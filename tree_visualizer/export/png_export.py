"""Pillow-based high-resolution PNG image rendering for binary trees.

Re-draws tree from computed layout without Ghostscript dependencies.
"""
from __future__ import annotations

from typing import Dict, Optional
from PIL import Image, ImageDraw, ImageFont
from tree_visualizer.core.node import TreeNode
from tree_visualizer.ui.layout import compute_tree_layout
from tree_visualizer.ui.theme import DARK_THEME


def render_tree_to_pillow_image(
    tree: Optional[TreeNode],
    theme: Optional[Dict[str, str]] = None,
    width: int = 900,
    height: int = 500,
    scale_factor: int = 2,
) -> Image.Image:
    """Render binary tree directly to a Pillow Image with antialiased lines and circles.

    scale_factor=2 produces a sharp 1800x1000 retina image.
    """
    t = theme if theme is not None else DARK_THEME
    bg_color = t.get("canvas_bg", "#0b0f19")
    edge_color = t.get("edge_default", "#64748b")
    node_color = t.get("node_default", "#3b82f6")
    stroke_color = t.get("node_stroke", "#1e293b")
    text_color = t.get("node_text", "#ffffff")

    img_w = int(width * scale_factor)
    img_h = int(height * scale_factor)
    image = Image.new("RGBA", (img_w, img_h), color=bg_color)
    draw = ImageDraw.Draw(image)

    if tree is None:
        return image

    layout = compute_tree_layout(tree, canvas_width=width, canvas_height=height)

    # 1. Draw connecting edges
    edge_width = max(2, int(2 * scale_factor))
    for edge in layout.edges:
        x1 = edge.x1 * scale_factor
        y1 = edge.y1 * scale_factor
        x2 = edge.x2 * scale_factor
        y2 = edge.y2 * scale_factor
        draw.line([(x1, y1), (x2, y2)], fill=edge_color, width=edge_width)

    # 2. Draw nodes and labels
    for node in layout.nodes.values():
        cx = node.x * scale_factor
        cy = node.y * scale_factor
        r = node.radius * scale_factor

        # Outer circle outline & fill
        draw.ellipse(
            [cx - r, cy - r, cx + r, cy + r],
            fill=node_color,
            outline=stroke_color,
            width=max(2, int(2 * scale_factor)),
        )

        # Label text
        label = node.label_text
        font_size = 11 if len(label) <= 2 else (9 if len(label) <= 4 else 8)
        scaled_font_size = int(font_size * scale_factor * 1.2)
        try:
            font = ImageFont.truetype("segoeui.ttf", scaled_font_size)
        except Exception:
            try:
                font = ImageFont.truetype("arial.ttf", scaled_font_size)
            except Exception:
                font = ImageFont.load_default()

        # Center text inside node
        bbox = draw.textbbox((0, 0), label, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        tx = cx - text_w / 2
        ty = cy - text_h / 2 - bbox[1]
        draw.text((tx, ty), label, fill=text_color, font=font)

    return image


def save_tree_to_png_file(
    tree: Optional[TreeNode],
    filepath: str,
    theme: Optional[Dict[str, str]] = None,
    width: int = 900,
    height: int = 500,
    scale_factor: int = 2,
) -> None:
    """Save rendered binary tree to PNG file."""
    image = render_tree_to_pillow_image(
        tree,
        theme=theme,
        width=width,
        height=height,
        scale_factor=scale_factor,
    )
    image.save(filepath, format="PNG")
