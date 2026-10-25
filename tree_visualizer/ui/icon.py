"""Application icon generator and top-bar branding icon.

Uses Pillow to render a high-quality stylized binary tree icon with anti-aliasing
and saves multi-resolution .ico and .png assets for the window and PyInstaller bundle.
Also provides a programmatic code-drawn canvas icon widget for the top bar.
"""
from __future__ import annotations

import os
import tkinter as tk
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageTk


def generate_tree_icon(size: int = 256) -> Image.Image:
    """Generate a stylized high-resolution binary tree icon with transparent background."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Scale factor relative to 256
    scale = size / 256.0

    # Node positions (x, y, radius, fill_color, stroke_color)
    root_x, root_y, root_r = 128 * scale, 48 * scale, 24 * scale
    l_x, l_y, l_r = 72 * scale, 128 * scale, 19 * scale
    r_x, r_y, r_r = 184 * scale, 128 * scale, 19 * scale
    ll_x, ll_y, ll_r = 44 * scale, 204 * scale, 15 * scale
    lr_x, lr_y, lr_r = 100 * scale, 204 * scale, 15 * scale
    rl_x, rl_y, rl_r = 156 * scale, 204 * scale, 15 * scale
    rr_x, rr_y, rr_r = 212 * scale, 204 * scale, 15 * scale

    edge_color = (148, 163, 184, 220)  # Slate 400
    edge_width = max(2, int(4 * scale))

    # Edges (draw first so they sit under nodes)
    edges = [
        ((root_x, root_y), (l_x, l_y)),
        ((root_x, root_y), (r_x, r_y)),
        ((l_x, l_y), (ll_x, ll_y)),
        ((l_x, l_y), (lr_x, lr_y)),
        ((r_x, r_y), (rl_x, rl_y)),
        ((r_x, r_y), (rr_x, rr_y)),
    ]
    for p1, p2 in edges:
        draw.line([p1, p2], fill=edge_color, width=edge_width)

    # Nodes
    nodes = [
        # (x, y, r, fill, stroke)
        (root_x, root_y, root_r, (56, 189, 248, 255), (15, 23, 42, 255)),   # Sky 400
        (l_x, l_y, l_r, (16, 185, 129, 255), (15, 23, 42, 255)),           # Emerald 500
        (r_x, r_y, r_r, (16, 185, 129, 255), (15, 23, 42, 255)),           # Emerald 500
        (ll_x, ll_y, ll_r, (59, 130, 246, 255), (15, 23, 42, 255)),        # Blue 500
        (lr_x, lr_y, lr_r, (59, 130, 246, 255), (15, 23, 42, 255)),        # Blue 500
        (rl_x, rl_y, rl_r, (59, 130, 246, 255), (15, 23, 42, 255)),        # Blue 500
        (rr_x, rr_y, rr_r, (59, 130, 246, 255), (15, 23, 42, 255)),        # Blue 500
    ]

    stroke_width = max(1, int(3 * scale))
    for x, y, r, fill, stroke in nodes:
        # Outer stroke
        draw.ellipse([x - r, y - r, x + r, y + r], fill=fill, outline=stroke, width=stroke_width)
        # Inner specular highlight
        inner_r = r * 0.4
        draw.ellipse(
            [x - inner_r, y - inner_r, x + inner_r, y + inner_r],
            fill=(255, 255, 255, 90),
        )

    return img


def save_app_icons(assets_dir: Optional[str] = None) -> Tuple[str, str]:
    """Generate and save icon.png and icon.ico in the assets folder."""
    if assets_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        assets_dir = os.path.join(base_dir, "assets")

    os.makedirs(assets_dir, exist_ok=True)
    png_path = os.path.join(assets_dir, "icon.png")
    ico_path = os.path.join(assets_dir, "icon.ico")

    # Generate master 256x256 image
    master_img = generate_tree_icon(size=256)
    master_img.save(png_path, format="PNG")

    # Multi-resolution ICO
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    master_img.save(ico_path, format="ICO", sizes=icon_sizes)

    return png_path, ico_path


class TreeIconCanvas(tk.Canvas):
    """Small vector canvas widget rendering the application brand tree icon."""

    def __init__(
        self,
        master: tk.Widget,
        size: int = 28,
        bg_color: str = "#1e293b",
        **kwargs,
    ) -> None:
        super().__init__(
            master,
            width=size,
            height=size,
            bg=bg_color,
            highlightthickness=0,
            **kwargs,
        )
        self.icon_size: int = size
        self.bg_color: str = bg_color
        self.draw_icon()

    def update_theme(self, bg_color: str) -> None:
        """Update canvas background on theme switch."""
        self.bg_color = bg_color
        self.configure(bg=bg_color)
        self.draw_icon()

    def draw_icon(self) -> None:
        """Draw clean vector binary tree icon."""
        self.delete("all")
        s = self.icon_size
        scale = s / 32.0

        # Coords
        rx, ry = 16 * scale, 6 * scale
        lx, ly = 9 * scale, 16 * scale
        rrx, rry = 23 * scale, 16 * scale
        llx, lly = 5 * scale, 26 * scale
        lrx, lry = 13 * scale, 26 * scale
        rlx, rly = 19 * scale, 26 * scale
        rr_x, rr_y = 27 * scale, 26 * scale

        edge_col = "#64748b"
        line_w = max(1, int(1.5 * scale))

        # Edges
        self.create_line(rx, ry, lx, ly, fill=edge_col, width=line_w)
        self.create_line(rx, ry, rrx, rry, fill=edge_col, width=line_w)
        self.create_line(lx, ly, llx, lly, fill=edge_col, width=line_w)
        self.create_line(lx, ly, lrx, lry, fill=edge_col, width=line_w)
        self.create_line(rrx, rry, rlx, rly, fill=edge_col, width=line_w)
        self.create_line(rrx, rry, rr_x, rr_y, fill=edge_col, width=line_w)

        # Draw node circles
        def _node(x: float, y: float, r: float, fill: str):
            self.create_oval(x - r, y - r, x + r, y + r, fill=fill, outline="#0f172a", width=1)

        r_root = 3.5 * scale
        r_child = 3.0 * scale
        r_leaf = 2.5 * scale

        _node(rx, ry, r_root, "#38bdf8")     # Sky
        _node(lx, ly, r_child, "#10b981")    # Emerald
        _node(rrx, rry, r_child, "#10b981")  # Emerald
        _node(llx, lly, r_leaf, "#3b82f6")   # Blue
        _node(lrx, lry, r_leaf, "#3b82f6")   # Blue
        _node(rlx, rly, r_leaf, "#3b82f6")   # Blue
        _node(rr_x, rr_y, r_leaf, "#3b82f6") # Blue
