"""Pure standard library SVG vector image export for binary trees."""
from __future__ import annotations

import html
from typing import Dict, Optional
from tree_visualizer.core.node import TreeNode
from tree_visualizer.ui.layout import compute_tree_layout
from tree_visualizer.ui.theme import DARK_THEME


def render_tree_to_svg(
    tree: Optional[TreeNode],
    theme: Optional[Dict[str, str]] = None,
    width: int = 900,
    height: int = 500,
) -> str:
    """Render binary tree as pure SVG XML string using Python standard library."""
    t = theme if theme is not None else DARK_THEME
    bg_color = t.get("canvas_bg", "#0b0f19")
    edge_color = t.get("edge_default", "#64748b")
    node_color = t.get("node_default", "#3b82f6")
    stroke_color = t.get("node_stroke", "#1e293b")
    text_color = t.get("node_text", "#ffffff")

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">',
        f'  <rect width="100%" height="100%" fill="{bg_color}"/>',
    ]

    if tree is not None:
        layout = compute_tree_layout(tree, canvas_width=width, canvas_height=height)

        # 1. Connecting edges
        lines.append("  <!-- Edges -->")
        for edge in layout.edges:
            lines.append(
                f'  <line x1="{edge.x1:.1f}" y1="{edge.y1:.1f}" x2="{edge.x2:.1f}" y2="{edge.y2:.1f}" '
                f'stroke="{edge_color}" stroke-width="2"/>'
            )

        # 2. Nodes and Labels
        lines.append("  <!-- Nodes -->")
        for node in layout.nodes.values():
            lbl = html.escape(node.label_text)
            fsize = 11 if len(node.label_text) <= 2 else (9 if len(node.label_text) <= 4 else 8)
            lines.append(
                f'  <circle cx="{node.x:.1f}" cy="{node.y:.1f}" r="{node.radius:.1f}" '
                f'fill="{node_color}" stroke="{stroke_color}" stroke-width="2"/>'
            )
            lines.append(
                f'  <text x="{node.x:.1f}" y="{node.y:.1f}" fill="{text_color}" font-family="Segoe UI, Arial, sans-serif" '
                f'font-size="{fsize}" font-weight="bold" text-anchor="middle" dominant-baseline="central">{lbl}</text>'
            )

    lines.append("</svg>")
    return "\n".join(lines)


def save_tree_to_svg_file(
    tree: Optional[TreeNode],
    filepath: str,
    theme: Optional[Dict[str, str]] = None,
    width: int = 900,
    height: int = 500,
) -> None:
    """Save rendered binary tree to SVG file."""
    content = render_tree_to_svg(tree, theme=theme, width=width, height=height)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
