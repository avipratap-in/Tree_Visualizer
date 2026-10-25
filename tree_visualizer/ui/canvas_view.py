"""Central interactive canvas viewport with smooth pan, zoom, tweening, and overlays.

Renders:
- Deterministic tree layout computed via ui/layout.py.
- Animated ~150 ms tweening of node positions between algorithm steps.
- Edges drawn first, followed by node circles and frequency labels.
- Adaptive font sizing for longer labels to ensure text fits inside circles.
- Smooth mouse wheel zooming toward cursor with cross-platform delta normalization:
    scale *= exp(-delta * 0.0008), clamped per event.
- Animated smooth reset back to default scale (1.0) and origin (0, 0).
- Empty-state definition cards rendered in Rouge Script that never block pan/zoom.
- Floating overlay panels: stats badge, zoom controls, visited banner, status box, pseudocode panel.
"""
from __future__ import annotations

import math
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from tree_visualizer.core.node import TreeNode
from tree_visualizer.core.properties import height as compute_height, size as compute_size
from tree_visualizer.recorder.steps import Step
from tree_visualizer.ui.fonts import (
    get_definition_body_font,
    get_definition_font_family,
    get_definition_title_font,
    get_ui_font,
)
from tree_visualizer.ui.layout import (
    CANVAS_HEIGHT,
    CANVAS_WIDTH,
    NodeLayout,
    TreeLayoutResult,
    compute_tree_layout,
)
from tree_visualizer.ui.overlays import PseudocodePanel, StatusBox
from tree_visualizer.ui.theme import ThemeManager


class CanvasView(tk.Frame):
    """Interactive tree visualization viewport supporting pan/zoom, tweening, and overlays."""

    BUTTON_STEP: float = 1.08
    WHEEL_ZOOM_COEFF: float = 0.00064
    MIN_SCALE: float = 0.3
    MAX_SCALE: float = 3.0
    TWEEN_DURATION_MS: int = 150
    TWEEN_STEPS: int = 10

    DEFINITION_TEXTS: Dict[str, Dict[str, str]] = {
        "binary": {
            "title": "Binary Tree",
            "body": (
                "A binary tree is a hierarchical data structure in which every node "
                "has at most two children, called the left child and the right child. "
                "Formally, it is either empty or consists of a root node together with "
                "a left subtree and a right subtree, each of which is itself a binary tree."
            ),
            "hint": "Use the panel on the left to create a tree.",
        },
        "bst": {
            "title": "Binary Search Tree (BST)",
            "body": (
                "A binary search tree is a binary tree in which, for every node, all values "
                "in its left subtree are smaller than the node's value and all values in its "
                "right subtree are greater. Because of this ordering, an inorder traversal "
                "visits the values in sorted order, and search, insert and remove take O(h) "
                "time, where h is the height of the tree."
            ),
            "hint": "Use the panel on the left to create a tree.",
        },
        "build": {
            "title": "Build from Traversal",
            "body": (
                "A binary tree can be reconstructed from two of its traversal sequences. "
                "The inorder sequence together with the preorder, postorder or level-order "
                "sequence identifies the tree uniquely, as long as all values are distinct. "
                "Preorder with postorder alone is unique only for full binary trees."
            ),
            "hint": "Use the panel on the left to create a tree.",
        },
    }

    def __init__(
        self,
        master: tk.Widget,
        theme_manager: ThemeManager,
        on_expand_sidebar: Optional[Callable[[], None]] = None,
        **kwargs,
    ) -> None:
        super().__init__(master, **kwargs)
        self.theme_manager: ThemeManager = theme_manager
        self.on_expand_sidebar: Optional[Callable[[], None]] = on_expand_sidebar

        # Pan and Zoom state
        self.scale: float = 1.0
        self.pan_x: float = 0.0
        self.pan_y: float = 0.0
        self._drag_start_x: float = 0.0
        self._drag_start_y: float = 0.0

        # Animation & Tweening state
        self._animating_reset: bool = False
        self._reset_after_id: Optional[str] = None
        self._tween_after_id: Optional[str] = None
        self._tween_progress: float = 1.0
        self._prev_node_coords: Dict[str, Tuple[float, float]] = {}
        self._curr_node_coords: Dict[str, Tuple[float, float]] = {}

        # Active data
        self.active_tab: str = "bst"
        self.current_step: Optional[Step] = None
        self.current_tree: Optional[TreeNode] = None
        self._layout_result: Optional[TreeLayoutResult] = None

        self._build_ui()
        self.theme_manager.register_listener(self.on_theme_updated)

    def _build_ui(self) -> None:
        t = self.theme_manager.current

        # Central Canvas
        self.canvas = tk.Canvas(
            self,
            bg=t["canvas_bg"],
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Mouse & gesture bindings for pan and zoom
        self.canvas.bind("<ButtonPress-1>", self._on_drag_start)
        self.canvas.bind("<B1-Motion>", self._on_drag_motion)
        self.canvas.bind("<MouseWheel>", self._on_mouse_wheel)
        self.canvas.bind("<Button-4>", self._on_mouse_wheel)  # Linux scroll up
        self.canvas.bind("<Button-5>", self._on_mouse_wheel)  # Linux scroll down
        self.canvas.bind("<Configure>", lambda e: self.redraw())

        # -------------------------------------------------------------
        # Floating Overlays
        # -------------------------------------------------------------

        # 1. Left Edge Collapsed Toggle Button (☰ Operations)
        self.btn_open_sidebar = ttk.Button(
            self.canvas,
            text="☰ Operations",
            style="Action.TButton",
            command=self._handle_expand_sidebar,
        )

        # 2. Top-Left Stats Badge [N=0, h=0]
        self.stats_frame = tk.Frame(
            self.canvas,
            bg=t["bg_panel"],
            bd=1,
            relief="solid",
            padx=8,
            pady=4,
        )
        self.lbl_stats = tk.Label(
            self.stats_frame,
            text="N=0, h=0",
            bg=t["bg_panel"],
            fg=t["text_main"],
            font=get_ui_font(9, bold=True),
        )
        self.lbl_stats.pack()

        # 3. Top-Right Zoom Controls [+ | 100% | - | ⟲]
        self.zoom_frame = tk.Frame(
            self.canvas,
            bg=t["bg_panel"],
            bd=1,
            relief="solid",
            padx=4,
            pady=3,
        )
        self.btn_zoom_in = ttk.Button(
            self.zoom_frame,
            text="+",
            width=2,
            style="Action.TButton",
            command=self.zoom_in,
        )
        self.btn_zoom_in.pack(side=tk.LEFT, padx=1)

        self.lbl_zoom = tk.Label(
            self.zoom_frame,
            text="100%",
            bg=t["bg_panel"],
            fg=t["text_main"],
            font=get_ui_font(8, bold=True),
            width=5,
        )
        self.lbl_zoom.pack(side=tk.LEFT, padx=2)

        self.btn_zoom_out = ttk.Button(
            self.zoom_frame,
            text="−",
            width=2,
            style="Action.TButton",
            command=self.zoom_out,
        )
        self.btn_zoom_out.pack(side=tk.LEFT, padx=1)

        self.btn_zoom_reset = ttk.Button(
            self.zoom_frame,
            text="⟲",
            width=2,
            style="Action.TButton",
            command=self.animated_reset_view,
        )
        self.btn_zoom_reset.pack(side=tk.LEFT, padx=1)

        # 4. Top-Center Visited Sequence Banner
        self.visited_banner = tk.Frame(
            self.canvas,
            bg=t["bg_panel"],
            bd=1,
            relief="solid",
            padx=12,
            pady=4,
        )
        self.lbl_visited = tk.Label(
            self.visited_banner,
            text="Visited: []",
            bg=t["bg_panel"],
            fg=t["accent"],
            font=get_ui_font(10, bold=True),
        )
        self.lbl_visited.pack()

        # 5. Bottom-Right VisuAlgo Status Box & Pseudocode Panel
        self.overlay_container = tk.Frame(self.canvas, bg=t["canvas_bg"])
        self.status_box = StatusBox(self.overlay_container, self.theme_manager)
        self.status_box.pack(side=tk.BOTTOM, fill=tk.X, pady=(4, 0))

        self.pseudocode_panel = PseudocodePanel(self.overlay_container, self.theme_manager)
        self.pseudocode_panel.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.redraw()

    # =========================================================================
    # Pan & Zoom Logic
    # =========================================================================

    def _on_drag_start(self, event: tk.Event) -> None:
        self._drag_start_x = event.x
        self._drag_start_y = event.y

    def _on_drag_motion(self, event: tk.Event) -> None:
        dx = event.x - self._drag_start_x
        dy = event.y - self._drag_start_y
        self.pan_x += dx
        self.pan_y += dy
        self._drag_start_x = event.x
        self._drag_start_y = event.y
        self.redraw()

    def _on_mouse_wheel(self, event: tk.Event) -> None:
        """Gentle mouse wheel zoom toward cursor with cross-platform delta normalization."""
        raw_delta = getattr(event, "delta", 0)
        if raw_delta == 0:
            num = getattr(event, "num", None)
            if num == 4:
                delta = 120.0
            elif num == 5:
                delta = -120.0
            else:
                delta = 0.0
        else:
            if abs(raw_delta) < 10:
                delta = raw_delta * 120.0
            else:
                delta = float(raw_delta)

        # Clamp delta per event to [-240, 240]
        delta = max(-240.0, min(240.0, delta))

        # Gentle zoom formula: scale *= exp(-deltaY * coeff)
        # Windows positive delta is zoom in, corresponding to negative deltaY in web
        factor = math.exp(delta * self.WHEEL_ZOOM_COEFF)
        self._apply_zoom(factor, event.x, event.y)

    def zoom_in(self) -> None:
        """Zoom in by 1.08x toward canvas center."""
        cx = self.canvas.winfo_width() / 2.0
        cy = self.canvas.winfo_height() / 2.0
        self._apply_zoom(self.BUTTON_STEP, cx, cy)

    def zoom_out(self) -> None:
        """Zoom out by 1/1.08x toward canvas center."""
        cx = self.canvas.winfo_width() / 2.0
        cy = self.canvas.winfo_height() / 2.0
        self._apply_zoom(1.0 / self.BUTTON_STEP, cx, cy)

    def _apply_zoom(self, factor: float, cx: float, cy: float) -> None:
        """Apply zoom factor centered around target cursor (cx, cy)."""
        new_scale = max(self.MIN_SCALE, min(self.scale * factor, self.MAX_SCALE))
        if new_scale == self.scale:
            return

        ratio = new_scale / self.scale
        self.pan_x = cx - ratio * (cx - self.pan_x)
        self.pan_y = cy - ratio * (cy - self.pan_y)
        self.scale = new_scale
        self.lbl_zoom.configure(text=f"{int(round(self.scale * 100))}%")
        self.redraw()

    def reset_view(self) -> None:
        """Instantly reset pan and zoom to scale 1.0 and origin."""
        if self._reset_after_id:
            try:
                self.after_cancel(self._reset_after_id)
            except Exception:
                pass
            self._reset_after_id = None
        self.scale = 1.0
        self.pan_x = 0.0
        self.pan_y = 0.0
        self.lbl_zoom.configure(text="100%")
        self.redraw()

    def animated_reset_view(self) -> None:
        """Smoothly tween scale to 1.0 and pan to (0, 0) over ~150 ms."""
        if self._reset_after_id:
            try:
                self.after_cancel(self._reset_after_id)
            except Exception:
                pass

        start_scale = self.scale
        start_pan_x = self.pan_x
        start_pan_y = self.pan_y
        total_steps = 10
        interval_ms = 15

        def _step(step_idx: int) -> None:
            if not self.winfo_exists():
                return
            t = step_idx / float(total_steps)
            ease = 1.0 - (1.0 - t) ** 2  # quadratic ease-out

            self.scale = start_scale + ease * (1.0 - start_scale)
            self.pan_x = start_pan_x + ease * (0.0 - start_pan_x)
            self.pan_y = start_pan_y + ease * (0.0 - start_pan_y)
            self.lbl_zoom.configure(text=f"{int(round(self.scale * 100))}%")
            self.redraw()

            if step_idx < total_steps:
                self._reset_after_id = self.after(interval_ms, lambda: _step(step_idx + 1))
            else:
                self._reset_after_id = None
                self.reset_view()

        _step(1)

    def set_sidebar_collapsed(self, is_collapsed: bool) -> None:
        """Display ☰ Operations button when sidebar is collapsed."""
        if is_collapsed:
            self.canvas.create_window(12, 12, window=self.btn_open_sidebar, anchor="nw", tags="overlay")
        else:
            self.btn_open_sidebar.place_forget()
        self.redraw()

    def _handle_expand_sidebar(self) -> None:
        if self.on_expand_sidebar:
            self.on_expand_sidebar()

    # =========================================================================
    # Step Tweening & State Updates
    # =========================================================================

    def set_tab(self, tab: str) -> None:
        """Update active tab and refresh canvas."""
        self.active_tab = tab
        self.redraw()

    def set_tree(self, tree: Optional[TreeNode]) -> None:
        """Set current tree and trigger layout calculation without step tween."""
        self.current_tree = tree
        self.current_step = None
        self._prev_node_coords = {}
        self._tween_progress = 1.0
        self._update_layout()
        self.redraw()

    def set_step(self, step: Optional[Step]) -> None:
        """Render algorithm Step with ~150 ms tweening between node positions."""
        self.current_step = step
        new_tree = step.tree_root if step is not None else None

        # Cancel any active tween
        if self._tween_after_id:
            try:
                self.after_cancel(self._tween_after_id)
            except Exception:
                pass
            self._tween_after_id = None

        # Capture previous coordinates
        if self._layout_result:
            self._prev_node_coords = {
                nid: (n.x, n.y) for nid, n in self._layout_result.nodes.items()
            }
        else:
            self._prev_node_coords = {}

        self.current_tree = new_tree
        self._update_layout()

        # Update overlay messages
        if step is not None:
            if step.message:
                self.status_box.set_message(step.message)
            if step.pseudo_line is not None:
                self.pseudocode_panel.highlight_line(step.pseudo_line)

        # Trigger smooth ~150ms position tween if nodes moved
        if self._prev_node_coords and self._layout_result and self._layout_result.nodes:
            self._start_node_tween()
        else:
            self._tween_progress = 1.0
            self.redraw()

    def _update_layout(self) -> None:
        """Recalculate pure tree layout coordinates using ui.layout."""
        if self.current_tree is None:
            self._layout_result = None
        else:
            self._layout_result = compute_tree_layout(self.current_tree)

    def _start_node_tween(self) -> None:
        """Start ~150 ms tween of node positions."""
        interval_ms = max(10, self.TWEEN_DURATION_MS // self.TWEEN_STEPS)
        step_delta = 1.0 / float(self.TWEEN_STEPS)

        def _step_anim(current_t: float) -> None:
            if not self.winfo_exists():
                return
            self._tween_progress = min(1.0, current_t)
            self.redraw()
            if self._tween_progress < 1.0:
                self._tween_after_id = self.after(
                    interval_ms,
                    lambda: _step_anim(current_t + step_delta),
                )
            else:
                self._tween_after_id = None

        _step_anim(step_delta)

    def destroy(self) -> None:
        """Cancel active animation tweens and cleanly destroy widget."""
        if hasattr(self, "_reset_after_id") and self._reset_after_id:
            try:
                self.after_cancel(self._reset_after_id)
            except Exception:
                pass
            self._reset_after_id = None
        if hasattr(self, "_tween_after_id") and self._tween_after_id:
            try:
                self.after_cancel(self._tween_after_id)
            except Exception:
                pass
            self._tween_after_id = None
        super().destroy()

    def set_pseudocode(self, lines: List[str], active_idx: Optional[int] = None) -> None:
        """Update pseudocode lines on the overlay."""
        self.pseudocode_panel.set_pseudocode(lines, active_idx)
        if not lines:
            self.pseudocode_panel.pack_forget()
        else:
            self.pseudocode_panel.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    # =========================================================================
    # Drawing Pipeline
    # =========================================================================

    def redraw(self) -> None:
        """Redraw all canvas elements, edges, nodes, and floating overlays."""
        self.canvas.delete("all")
        t = self.theme_manager.current

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w <= 1 or h <= 1:
            return

        # Position Floating Overlays
        stats_x = 120 if self.btn_open_sidebar.winfo_ismapped() else 12
        self.canvas.create_window(stats_x, 12, window=self.stats_frame, anchor="nw", tags="overlay")
        self.canvas.create_window(w - 12, 12, window=self.zoom_frame, anchor="ne", tags="overlay")

        # Visited Banner (Top Center)
        visited = self.current_step.visited if (self.current_step and self.current_step.visited) else []
        if visited:
            vis_str = ", ".join(str(v) for v in visited)
            self.lbl_visited.configure(text=f"Visited: [ {vis_str} ]")
            self.canvas.create_window(w / 2, 16, window=self.visited_banner, anchor="n", tags="overlay")
        else:
            self.visited_banner.place_forget()

        # Status & Pseudocode Overlays (Bottom Right)
        self.canvas.create_window(w - 16, h - 16, window=self.overlay_container, anchor="se", tags="overlay")

        # Update stats badge
        tree_root = self.current_tree
        n = compute_size(tree_root)
        tree_h = compute_height(tree_root)
        self.lbl_stats.configure(text=f"N={n}, h={tree_h}")

        # Render Tree or Definition Card
        if tree_root is None or self._layout_result is None or self._layout_result.node_count == 0:
            self._draw_definition_card(w, h)
        else:
            self._draw_tree_layout(self._layout_result, w, h)

    def _draw_definition_card(self, w: float, h: float) -> None:
        """Render empty-state academic definition card in Special Elite.

        Drawn directly onto canvas background with dynamic non-overlapping vertical flow
        so pan/zoom gestures work seamlessly over it.
        """
        t = self.theme_manager.current
        card_info = self.DEFINITION_TEXTS.get(self.active_tab, self.DEFINITION_TEXTS["bst"])

        cx = w / 2.0 + self.pan_x
        cy = h / 2.0 + self.pan_y - 25

        # Font sizes increased by 20%
        title_size = max(12, int(round(34 * self.scale)))
        body_size = max(10, int(round(20 * self.scale)))
        hint_size = max(8, int(round(12 * self.scale)))

        title_font = get_definition_title_font(title_size)
        body_font = get_definition_body_font(body_size)
        hint_font = (get_definition_font_family(), hint_size, "normal")

        # 1. Title item (top-anchored at temporary y=0)
        title_item = self.canvas.create_text(
            cx,
            0,
            text=card_info["title"],
            font=title_font,
            fill=t["accent"],
            justify=tk.CENTER,
            anchor="n",
            tags="definition_card",
        )
        title_bbox = self.canvas.bbox(title_item)
        title_bottom = title_bbox[3] if title_bbox else 0

        # Spacing between title and body
        gap_title_body = max(16.0, 24.0 * self.scale)

        # 2. Narrative body (top-anchored below title)
        max_width = max(100.0, min(760.0 * self.scale, w * 0.88))
        body_item = self.canvas.create_text(
            cx,
            title_bottom + gap_title_body,
            text=card_info["body"],
            font=body_font,
            fill=t["text_muted"],
            width=max_width,
            justify=tk.CENTER,
            anchor="n",
            tags="definition_card",
        )
        body_bbox = self.canvas.bbox(body_item)
        body_bottom = body_bbox[3] if body_bbox else title_bottom + gap_title_body

        # Spacing between body and hint
        gap_body_hint = max(12.0, 18.0 * self.scale)

        # 3. Actionable hint line (top-anchored below body)
        hint_item = self.canvas.create_text(
            cx,
            body_bottom + gap_body_hint,
            text=card_info["hint"],
            font=hint_font,
            fill=t["text_muted"],
            justify=tk.CENTER,
            anchor="n",
            tags="definition_card",
        )
        hint_bbox = self.canvas.bbox(hint_item)

        # Compute bounding box of entire card to center it vertically around cy
        total_top = title_bbox[1] if title_bbox else 0
        total_bottom = hint_bbox[3] if hint_bbox else body_bottom + gap_body_hint
        total_height = total_bottom - total_top

        target_top = cy - (total_height / 2.0)
        dy = target_top - total_top
        self.canvas.move("definition_card", 0, dy)

    def _draw_tree_layout(self, layout: TreeLayoutResult, w: float, h: float) -> None:
        """Render edges and nodes using layout result and active step highlights."""
        t = self.theme_manager.current

        # Compute interpolated positions for tweening
        tween_t = self._tween_progress
        ease = 1.0 - (1.0 - tween_t) ** 2  # smooth ease-out

        interpolated_coords: Dict[str, Tuple[float, float]] = {}
        for nid, nlayout in layout.nodes.items():
            curr_x, curr_y = nlayout.x, nlayout.y
            if nid in self._prev_node_coords and tween_t < 1.0:
                prev_x, prev_y = self._prev_node_coords[nid]
                ix = prev_x + ease * (curr_x - prev_x)
                iy = prev_y + ease * (curr_y - prev_y)
            else:
                ix, iy = curr_x, curr_y
            interpolated_coords[nid] = (ix, iy)

        # Transform logical coords to view coords
        def _to_view(lx: float, ly: float) -> Tuple[float, float]:
            vx = lx * self.scale + self.pan_x
            vy = ly * self.scale + self.pan_y
            return vx, vy

        # Highlight sets from active step
        highlight_nodes: Set[str] = set()
        visited_nodes: Set[str] = set()
        highlight_edges: Set[Tuple[str, str]] = set()

        if self.current_step is not None:
            highlight_nodes = set(self.current_step.highlight_nodes)
            visited_nodes = {str(v) for v in self.current_step.visited}
            highlight_edges = set(self.current_step.highlight_edges)

        # 1. Draw Edges first (underneath nodes)
        for edge in layout.edges:
            p_id = edge.parent_id
            c_id = edge.child_id
            if p_id in interpolated_coords and c_id in interpolated_coords:
                px, py = _to_view(*interpolated_coords[p_id])
                cx, cy = _to_view(*interpolated_coords[c_id])

                is_edge_hl = (p_id, c_id) in highlight_edges or (c_id, p_id) in highlight_edges
                edge_color = t["edge_highlight"] if is_edge_hl else t["edge_default"]
                edge_width = max(1, int(round(3 * self.scale if is_edge_hl else 2 * self.scale)))

                self.canvas.create_line(
                    px, py, cx, cy,
                    fill=edge_color,
                    width=edge_width,
                    tags="edge",
                )

        # 2. Draw Nodes
        base_radius = layout.nodes[list(layout.nodes.keys())[0]].radius if layout.nodes else 20.0
        r = base_radius * self.scale

        for nid, nlayout in layout.nodes.items():
            vx, vy = _to_view(*interpolated_coords[nid])

            is_hl = nid in highlight_nodes or str(nlayout.val) in highlight_nodes
            is_vis = str(nlayout.val) in visited_nodes

            if is_hl:
                fill_col = t["node_highlight"]
            elif is_vis:
                fill_col = t["node_visited"]
            else:
                fill_col = t["node_default"]

            stroke_w = max(1, int(round(2 * self.scale)))
            self.canvas.create_oval(
                vx - r, vy - r, vx + r, vy + r,
                fill=fill_col,
                outline=t["node_stroke"],
                width=stroke_w,
                tags=("node", nid),
            )

            # Adaptive font sizing: long labels shrink the font to fit node circle
            label_text = nlayout.label_text
            label_len = len(label_text)
            if label_len <= 2:
                base_font_size = 11
            elif label_len == 3:
                base_font_size = 9
            elif label_len == 4:
                base_font_size = 8
            else:
                base_font_size = 7

            font_size = max(6, int(round(base_font_size * self.scale)))
            font = get_ui_font(font_size, bold=True)

            self.canvas.create_text(
                vx, vy,
                text=label_text,
                fill=t["node_text"],
                font=font,
                tags=("node_text", nid),
            )

    def on_theme_updated(self, theme: Dict[str, str]) -> None:
        """Update canvas and floating overlay backgrounds on theme change."""
        self.canvas.configure(bg=theme["canvas_bg"])
        self.stats_frame.configure(bg=theme["bg_panel"], highlightbackground=theme["border_color"])
        self.lbl_stats.configure(bg=theme["bg_panel"], fg=theme["text_main"])
        self.zoom_frame.configure(bg=theme["bg_panel"], highlightbackground=theme["border_color"])
        self.lbl_zoom.configure(bg=theme["bg_panel"], fg=theme["text_main"])
        self.visited_banner.configure(bg=theme["bg_panel"], highlightbackground=theme["border_color"])
        self.lbl_visited.configure(bg=theme["bg_panel"], fg=theme["accent"])
        self.overlay_container.configure(bg=theme["canvas_bg"])
        self.redraw()
